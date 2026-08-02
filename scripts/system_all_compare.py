"""Section 6: the combined comparison of Systems A, B and C.

NO NEW DATA. NOTHING IS SELECTED HERE.
--------------------------------------
Every number in this script comes from re-scoring predictions that were
already frozen and already reported, through the metric that was already
frozen. No model runs, no API call is made, no threshold is chosen, no
system is modified. Because nothing here selects anything, stratifying
the sealed test results carries no leakage risk -- this is description
of a finished measurement, not a search over it.

ONE SCORING PATH, THREE SYSTEMS
-------------------------------
The three systems stored their predictions in two different coordinate
frames: A and C in the native 640x480 image, B in its 224x224 centre
crop. Comparing their stored per-system numbers would mean trusting
three separate scoring implementations to have agreed. Instead every
prediction is pulled back into the 640x480 frame and re-scored here by
the same call to grasp_metric.is_correct against the same ground truth.

The crop is a fixed similarity transform for val and test (no
augmentation), so the inverse is exact, and the constants are IMPORTED
from grasp_dataset rather than retyped -- a hand-copied 0.56 that later
drifts is precisely the silent error this project keeps designing out.

The check that makes this trustworthy is that re-scoring must reproduce
71/123, 98/123 and 76/615 exactly. It does. If it ever stops doing so,
main() refuses to write anything, because a shared scoring path that
disagrees with the sealed runs is measuring something else.

WHY THE STORED best_iou / angle_err COLUMNS ARE NOT USED
--------------------------------------------------------
is_correct returns `correct` computed against ALL ground-truth
rectangles, but returns best_iou/best_ang for the single highest-OVERLAP
one, regardless of whether that one passed the angle test. Those
disagree on 9 of 123 System B images and 9 of 614 System C calls: the
prediction matched a different rectangle than the one it overlapped
most. Bucketing a failure taxonomy from those columns alone would
therefore mislabel real successes. Every taxonomy here is recomputed
from geometry, with the `correct` test ordered first.

Usage:
    python scripts/system_all_compare.py

Outputs:
    data/interim/comparison_per_image.csv
    data/interim/comparison_by_object.csv
    data/interim/comparison_results.md
    data/interim/comparison_sheets/*.png
"""

import csv
import json
import math
import re
from collections import Counter, defaultdict

from PIL import Image, ImageDraw

from cornell_data import (INTERIM, find_images, load_rects, load_split,
                          rect_to_corners)
from grasp_dataset import CROP_X0, CROP_Y0, SCALE
from grasp_metric import ANGLE_TOL_DEG, IOU_MIN, angle_diff, is_correct

A_CSV = INTERIM / "system_a_predictions.csv"
B_CSV = INTERIM / "system_b_predictions.csv"
C_CSV = INTERIM / "system_c_predictions.csv"
C_RAW = INTERIM / "system_c_raw.jsonl"
FIRST_PASS = INTERIM / "claude_first_pass.csv"

PER_IMAGE_CSV = INTERIM / "comparison_per_image.csv"
BY_OBJECT_CSV = INTERIM / "comparison_by_object.csv"
RESULTS_MD = INTERIM / "comparison_results.md"
SHEETS = INTERIM / "comparison_sheets"

REPEATS = 5
N_SHEETS = 12

# The sealed counts each system reported. Re-scoring must reproduce these
# exactly or nothing is written -- see the module docstring.
SEALED = {"A": (71, 123), "B": (98, 123), "C": (76, 615)}

# An image counts as "axis-aligned" if ANY labelled grasp sits within this
# many degrees of 0 or 90. System A can only ever emit 0 or 90, so this is
# the axis its representation is pinned on, and it comes from the dataset's
# own cpos files rather than from any system's output.
AXIAL_TOL_DEG = 15.0

# System B's other two architectures, for the one prose comparison the
# headline table deliberately does not carry as rows.
CNN_TEST = (29, 123)
RESNET34_TEST = (87, 123)


# ------------------------------------------------------------ loading


def test_ids():
    """Test pcd ids as ints, plus the frozen object grouping."""
    rows = load_split()
    ids = sorted(p for p, (_, s) in rows.items() if s == "test")
    obj = {p: g for p, (g, _) in rows.items()}
    return ids, obj


def _rect(row, keys=("cx", "cy", "theta", "opening", "jaw")):
    return tuple(float(row[k]) for k in keys)


def load_a():
    """System A, already in the 640x480 frame. 8 images have no prediction."""
    out = {}
    for r in csv.DictReader(open(A_CSV)):
        p = int(r["pcd_id"])
        out[p] = None if r["cx"] == "" else _rect(r)
    return out


def load_b():
    """System B, stored in the 224x224 crop frame, pulled back to 640x480.

    The val/test crop is deterministic (no augmentation), so this inverse
    is exact rather than approximate. Angle is unchanged because a uniform
    scale plus a translation cannot rotate anything.
    """
    out = {}
    for r in csv.DictReader(open(B_CSV)):
        cx, cy, th, op, jw = _rect(r)
        out[int(r["pcd_id"])] = (cx / SCALE + CROP_X0, cy / SCALE + CROP_Y0,
                                 th, op / SCALE, jw / SCALE)
    return out


def load_c():
    """System C, 640x480 already. Non-'ok' calls become None, i.e. failures."""
    out = defaultdict(dict)
    for r in csv.DictReader(open(C_CSV)):
        p, rep = int(r["pcd_id"]), int(r["repeat"])
        out[p][rep] = _rect(r) if r["outcome"] == "ok" else None
    return out


# ------------------------------------------------------------ scoring


def score(pred, gts):
    """(correct, bucket) for one prediction. A missing prediction is a failure.

    `correct` is tested FIRST, deliberately. best_iou/best_ang describe the
    highest-overlap ground truth, which is not always the one the
    prediction actually matched, so ordering the checks the other way round
    would file real successes under a failure bucket.
    """
    if pred is None:
        return False, "no_prediction"
    ok, _, iou, ang = is_correct(pred, gts)
    if ok:
        return True, "correct"
    if iou > IOU_MIN and ang > ANGLE_TOL_DEG:
        return False, "angle_only"
    if ang <= ANGLE_TOL_DEG and iou <= IOU_MIN:
        return False, "iou_only"
    return False, "both"


def score_everything(ids, gts, a, b, c):
    """Per-image correctness and taxonomy buckets for all three systems."""
    correct = {"A": {}, "B": {}, "C": defaultdict(dict)}
    bucket = {"A": {}, "B": {}, "C": defaultdict(dict)}
    for p in ids:
        correct["A"][p], bucket["A"][p] = score(a[p], gts[p])
        correct["B"][p], bucket["B"][p] = score(b[p], gts[p])
        for rep in range(REPEATS):
            correct["C"][p][rep], bucket["C"][p][rep] = score(c[p][rep], gts[p])
    return correct, bucket


def reproduction_check(ids, correct):
    """Re-scoring must land on the sealed counts. Returns a list of failures."""
    got = {"A": sum(correct["A"][p] for p in ids),
           "B": sum(correct["B"][p] for p in ids),
           "C": sum(correct["C"][p][r] for p in ids for r in range(REPEATS))}
    bad = []
    for sysname, (k, n) in SEALED.items():
        if got[sysname] != k:
            bad.append(f"{sysname}: re-scored {got[sysname]}/{n}, sealed run said {k}/{n}")
    return got, bad


# ------------------------------------------------------------ statistics


def wilson(k, n, z=1.96):
    """Wilson score interval, as percentages. Better than normal-approx at n=123."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100.0 * max(0.0, centre - half), 100.0 * min(1.0, centre + half))


def _log_comb(n, k):
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1))


def mcnemar(first, second):
    """Exact paired test on two binary vectors over the SAME images.

    Returns (n_first_only, n_second_only, two-sided p). Paired matters: all
    three systems ran on the same 123 images, so an unpaired test would
    throw away the pairing and be needlessly weak.
    """
    b = sum(1 for x, y in zip(first, second) if x and not y)
    c = sum(1 for x, y in zip(first, second) if y and not x)
    n = b + c
    if n == 0:
        return b, c, 1.0
    # two-sided exact binomial at p=0.5, summing the tail at or beyond
    # whichever of b, c is smaller
    m = min(b, c)
    tail = sum(math.exp(_log_comb(n, i) - n * math.log(2.0)) for i in range(m + 1))
    return b, c, min(1.0, 2.0 * tail)


# ------------------------------------------------------------ strata


def axial_stratum(gts):
    """'axis-aligned' if any labelled grasp is near 0 or 90 degrees, else 'diagonal'.

    Externally sourced: this reads the dataset's own annotations, not any
    system's output, which is what makes it usable as a shared axis.
    """
    for g in gts:
        if min(angle_diff(g[2], 0.0), angle_diff(g[2], 90.0)) <= AXIAL_TOL_DEG:
            return "axis-aligned"
    return "diagonal"


def rate(ids, correct, sysname):
    """Accuracy over a set of images. System C averages its 5 repeats per image.

    Averaging repeats per image and then over images is identical to the
    headline mean-per-repeat accuracy (both are total_correct / (n*5)), so
    C's stratified rows stay directly comparable to its own headline.
    """
    if not ids:
        return float("nan"), 0, 0
    if sysname == "C":
        k = sum(correct["C"][p][r] for p in ids for r in range(REPEATS))
        n = len(ids) * REPEATS
    else:
        k = sum(correct[sysname][p] for p in ids)
        n = len(ids)
    return 100.0 * k / n, k, n


# ------------------------------------------------------------ object names


_STRIP = re.compile(r"^(a|an|the|pair of|piece of|single|small|large)\s+")


def _canon(label):
    s = re.sub(r"\s+", " ", label.strip().lower())
    prev = None
    while prev != s:
        prev = s
        s = _STRIP.sub("", s)
    return s.rstrip(".")


def vlm_names(ids, obj):
    """Modal `object` string per object group, from System C's frozen raw log.

    This is a re-parse of sealed text, which this project permits; no call
    is made. The label is DESCRIPTIVE ONLY -- it is never a scoring axis,
    because it is System C's own output and using it to stratify would bias
    the comparison toward the system that produced it. Accuracy is always
    grouped by object_id, which is external and frozen.
    """
    votes = defaultdict(Counter)
    keep = set(ids)
    if not C_RAW.exists():
        return {}
    for line in open(C_RAW):
        r = json.loads(line)
        if r.get("tag") != "test" or int(r.get("pcd_id", -1)) not in keep:
            continue
        m = re.search(r'"object"\s*:\s*"([^"]*)"', r.get("text") or "")
        if m and m.group(1).strip():
            votes[obj[int(r["pcd_id"])]][_canon(m.group(1))] += 1
    out = {}
    for g, c in votes.items():
        label, n = c.most_common(1)[0]
        out[g] = (label, n / sum(c.values()))
    return out


def boundary_names(ids, obj):
    """Object descriptions from the split review's free text, where they exist.

    A partial second opinion, not a full naming source: it is written per
    BOUNDARY pair, so it only covers groups that happen to sit next to a
    reviewed boundary, and only the 'X vs Y' phrasings can be attributed to
    a specific side. Used to spot-check the VLM names, not to replace them.
    """
    split = {p: s for p, (_, s) in load_split().items()}
    out = defaultdict(Counter)
    if not FIRST_PASS.exists():
        return {}
    for r in csv.DictReader(open(FIRST_PASS)):
        reason = r["brief_reason"].split(";")[0]
        if " vs " not in reason:
            continue
        left, right = reason.split(" vs ", 1)
        for pcd_key, text in ((r["pcd_a"], left), (r["pcd_b"], right)):
            p = int(pcd_key)
            if split.get(p) == "test" and p in obj:
                out[obj[p]][_canon(text)] += 1
    return {g: c.most_common(1)[0][0] for g, c in out.items()}


def reconcile_names(vlm, boundary):
    """Where both sources name a group, do they agree on a head noun?

    Disagreements are returned rather than silently resolved -- per the
    project rule that ambiguity goes to the researcher instead of being
    settled by whichever source the code happened to read first.
    """
    def words(s):
        # The review text uses slashes for alternatives ("phone/remote",
        # "masher/turner"), so those are separate candidate words rather than
        # one token -- otherwise a genuine agreement reads as a disagreement.
        return {w for w in re.split(r"[\s/,()]+", s) if len(w) > 2}

    agree, disagree, unchecked = [], [], []
    for g in sorted(vlm):
        if g not in boundary:
            unchecked.append(g)
            continue
        a_w, b_w = words(vlm[g][0]), words(boundary[g])
        hit = any(x == y or x in y or y in x for x in a_w for y in b_w)
        (agree if hit else disagree).append(g)
    return agree, disagree, unchecked, boundary


# ------------------------------------------------------------ sheets


def pick_sheets(ids, correct):
    """Four images per story: A's orientation gap, B's residual, everyone's misses.

    Deterministic (sorted order, fixed quotas) so the choice of illustration
    is not a place where a nicer-looking set could be shopped for.
    """
    cA, cB = correct["A"], correct["B"]
    cC = {p: sum(correct["C"][p][r] for r in range(REPEATS)) for p in ids}
    groups = [
        ("B fixes A", [p for p in ids if not cA[p] and cB[p]]),
        ("B still misses", [p for p in ids if not cB[p]]),
        ("all three miss", [p for p in ids if not cA[p] and not cB[p] and cC[p] == 0]),
    ]
    picked, seen = [], set()
    per = N_SHEETS // len(groups)
    for label, members in groups:
        # Evenly spaced through the sorted list rather than the first few, so
        # the illustrations are not all drawn from one object group. Still
        # fully determined by the data -- no choosing which ones look better.
        if not members:
            continue
        step = max(1, len(members) // per)
        for p in members[::step]:
            if p not in seen and sum(1 for l, _ in picked if l == label) < per:
                picked.append((label, p))
                seen.add(p)
    return picked


def draw_sheets(picked, gts, a, b, c, correct):
    """One sheet per image: green GT, System A red, System B blue, System C orange."""
    SHEETS.mkdir(parents=True, exist_ok=True)
    # Clear first: a rerun with a different selection rule would otherwise
    # leave a mixture of old and new sheets and no way to tell them apart.
    for old in SHEETS.glob("compare_*.png"):
        old.unlink()
    images = find_images()
    for label, p in picked:
        im = Image.open(images[p]).convert("RGB")
        d = ImageDraw.Draw(im)
        for g in gts[p]:
            d.polygon([tuple(pt) for pt in rect_to_corners(*g)], outline=(0, 220, 0))
        for rep in range(REPEATS):
            if c[p][rep] is not None:
                d.polygon([tuple(pt) for pt in rect_to_corners(*c[p][rep])],
                          outline=(255, 150, 0))
        if a[p] is not None:
            d.polygon([tuple(pt) for pt in rect_to_corners(*a[p])],
                      outline=(255, 40, 40), width=2)
        d.polygon([tuple(pt) for pt in rect_to_corners(*b[p])],
                  outline=(60, 130, 255), width=2)
        n_c = sum(correct["C"][p][r] for r in range(REPEATS))
        d.text((6, 6), f"pcd{p:04d}  {label}", fill=(255, 255, 255))
        d.text((6, 18), "green=GT  red=A  blue=B  orange=C(5)", fill=(255, 255, 255))
        d.text((6, 30), f"A {'ok' if correct['A'][p] else 'miss'}   "
                        f"B {'ok' if correct['B'][p] else 'miss'}   "
                        f"C {n_c}/5", fill=(255, 255, 255))
        im.save(SHEETS / f"compare_{p:04d}.png")


# ------------------------------------------------------------ csv output


def display_label(g, names, disputed):
    """The label shown to a reader: the VLM string, or a neutral placeholder.

    Both naming sources are themselves model-generated (one from System C,
    one from the split review's free text). Where they disagree, picking
    either one and printing it as THE name would launder a guess into
    something that reads as authoritative just by sitting in a results
    table. Neither is ground truth and neither is owed that. So a disputed
    group gets a neutral, non-committal placeholder instead -- the two raw
    guesses are still on record, in the disagreement table, for whoever
    wants to look at the images and decide for themselves.
    """
    if g in disputed:
        return f"object {g} (label uncertain)"
    return names.get(g, ("", 0.0))[0]


def write_per_image(ids, obj, names, gts, correct, bucket, disputed):
    with open(PER_IMAGE_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pcd_id", "object_id", "object_label", "n_gt_rects", "stratum",
                    "a_correct", "a_bucket", "b_correct", "b_bucket",
                    "c_repeats_correct", "c_buckets"])
        for p in ids:
            g = obj[p]
            w.writerow([f"{p:04d}", g, display_label(g, names, disputed), len(gts[p]),
                        axial_stratum(gts[p]),
                        int(correct["A"][p]), bucket["A"][p],
                        int(correct["B"][p]), bucket["B"][p],
                        sum(correct["C"][p][r] for r in range(REPEATS)),
                        "|".join(bucket["C"][p][r] for r in range(REPEATS))])


def write_by_object(ids, obj, names, correct, disputed):
    by = defaultdict(list)
    for p in ids:
        by[obj[p]].append(p)
    rows = []
    for g in sorted(by, key=lambda g: (-len(by[g]), g)):
        members = by[g]
        label = display_label(g, names, disputed)
        share = 0.0 if g in disputed else names.get(g, ("", 0.0))[1]
        rows.append([g, label, f"{share:.2f}", len(members)]
                    + [f"{rate(members, correct, s)[0]:.1f}" for s in ("A", "B", "C")])
    with open(BY_OBJECT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["object_id", "object_label", "label_vote_share", "n_images",
                    "a_acc", "b_acc", "c_acc"])
        w.writerows(rows)
    return rows


# ------------------------------------------------------------ force


def force_distributions(ids):
    """Descriptive only, never scored -- the dataset has no force ground truth."""
    a = Counter(r["force"] for r in csv.DictReader(open(A_CSV)) if r["force"])
    c = Counter()
    keep = set(ids)
    if C_RAW.exists():
        for line in open(C_RAW):
            r = json.loads(line)
            if r.get("tag") != "test" or int(r.get("pcd_id", -1)) not in keep:
                continue
            m = re.search(r'"force"\s*:\s*"([^"]*)"', r.get("text") or "")
            if m:
                c[m.group(1).strip().upper()] += 1
    return a, c


# ------------------------------------------------------------ the document


def pct(k, n):
    lo, hi = wilson(k, n)
    return f"{100.0 * k / n:.1f}% [{lo:.1f}, {hi:.1f}]"


def write_results(ids, obj, gts, correct, bucket, names, recon, by_object, picked):
    accA = sum(correct["A"][p] for p in ids)
    accB = sum(correct["B"][p] for p in ids)
    per_repeat = [sum(correct["C"][p][r] for p in ids) for r in range(REPEATS)]
    accC = sum(per_repeat)
    n = len(ids)
    best5 = sum(1 for p in ids if any(correct["C"][p][r] for r in range(REPEATS)))

    vA = [correct["A"][p] for p in ids]
    vB = [correct["B"][p] for p in ids]
    vC = [[correct["C"][p][r] for p in ids] for r in range(REPEATS)]

    L = []
    L.append("# Section 6: Systems A, B and C compared\n")
    L.append("Spec section 6 and Deliverable 5. All three systems, one metric "
             "(angle within 30 degrees AND IoU above 25% against any labelled "
             "grasp), one sealed 123-image test split, one scoring code path.\n")
    L.append("Nothing here is a new measurement. Every number is a re-score of "
             "predictions that were already frozen, through "
             "`grasp_metric.is_correct`, which has not changed since commit "
             "`026032d`. No model was run and no API call was made. Because "
             "nothing is being selected, stratifying the sealed results carries "
             "no leakage risk -- this describes a finished measurement rather "
             "than searching over it.\n")
    L.append("The re-score reproduces all three sealed counts exactly (71/123, "
             "98/123, 76/615), which is what licenses putting them in the same "
             "table: the comparison is not three separate scoring "
             "implementations being trusted to have agreed.\n\n")

    # ---- headline
    L.append("## Headline\n")
    L.append("| System | Test accuracy | 95% interval |")
    L.append("|---|---|---|")
    L.append(f"| A (rule-based) | {100.0 * accA / n:.1f}% ({accA}/{n}) | "
             f"[{wilson(accA, n)[0]:.1f}, {wilson(accA, n)[1]:.1f}] |")
    L.append(f"| **B (ResNet18, val-selected)** | **{100.0 * accB / n:.1f}%** "
             f"({accB}/{n}) | [{wilson(accB, n)[0]:.1f}, {wilson(accB, n)[1]:.1f}] |")
    L.append(f"| C (GPT-4o, mean of 5 repeats) | {100.0 * accC / (n * REPEATS):.1f}% "
             f"({accC}/{n * REPEATS} calls) | "
             f"[{wilson(accC, n * REPEATS)[0]:.1f}, "
             f"{wilson(accC, n * REPEATS)[1]:.1f}] |\n")
    L.append("Intervals are Wilson score intervals. At n=123 they are wide enough "
             "to matter: System A's point estimate of "
             f"{100.0 * accA / n:.1f}% is consistent with anything from "
             f"{wilson(accA, n)[0]:.1f}% to {wilson(accA, n)[1]:.1f}%, so small "
             "gaps between systems should not be read as settled.\n")
    L.append("System C's interval is computed over 615 calls and is therefore "
             "**anticonservative**: those are 5 correlated repeats of 123 images, "
             "not 615 independent trials. The honest spread is the one across its "
             "5 individual runs: "
             + ", ".join(f"{100.0 * k / n:.1f}%" for k in per_repeat)
             + f" (min {100.0 * min(per_repeat) / n:.1f}%, max "
               f"{100.0 * max(per_repeat) / n:.1f}%). That per-repeat spread is a "
               "within-system sampling range, and it is never used as an "
               "inter-system error bar -- the two look alike in a table and mean "
               "completely different things.\n")
    cnn_lo, cnn_hi = wilson(*CNN_TEST)
    c_lo, c_hi = wilson(accC, n * REPEATS)
    L.append("One comparison worth making once, in prose rather than as a table "
             "row. System B trained three architectures and selected ResNet18 on "
             "**val**, before test was opened; the other two test numbers exist "
             "but are not leaderboard entries, because selecting on test is the "
             "thing that rule was written to prevent. With that stated: the "
             "from-scratch custom CNN, which System B's own results doc concludes "
             f"failed to learn the task, still scored {100.0 * CNN_TEST[0] / CNN_TEST[1]:.1f}% "
             f"[{cnn_lo:.1f}, {cnn_hi:.1f}] against System C's "
             f"{100.0 * accC / (n * REPEATS):.1f}% [{c_lo:.1f}, {c_hi:.1f}]. "
             "The intervals do not overlap. A 1M-parameter network that could not "
             "learn grasp orientation from 620 images still outperformed a frontier "
             "VLM prompted zero-shot for coordinates.\n\n")

    # ---- the throughline
    L.append("## The organising claim: failure moves down the pipeline\n")
    L.append("All three systems solve the same task and fail at three different "
             "stages of it. System A can find the object but cannot rotate the "
             "gripper. System B can rotate the gripper but still mis-places it. "
             "System C fails before either question is reached, because the "
             "coordinates it emits are not bound to the object its own reasoning "
             "names.\n")
    L.append("That is one sentence with three clauses, and the rest of this "
             "document is evidence for them. It is also why the systems are "
             "ordered A, B, C rather than by score (which would be B, A, C): the "
             "ordering is how far into the problem each system gets before it "
             "fails.\n\n")

    # ---- taxonomy
    L.append("## Failure taxonomy, recomputed identically for all three\n")
    L.append("Which criterion did a prediction miss on? Recomputed here from "
             "geometry for every system, so the bucketing rule is literally the "
             "same code in all three columns.\n")
    L.append("| Bucket | A (of 123 images) | B (of 123 images) | C (of 615 calls) |")
    L.append("|---|---|---|---|")
    tA = Counter(bucket["A"][p] for p in ids)
    tB = Counter(bucket["B"][p] for p in ids)
    tC = Counter(bucket["C"][p][r] for p in ids for r in range(REPEATS))
    for k in ("correct", "angle_only", "iou_only", "both", "no_prediction"):
        if tA[k] or tB[k] or tC[k]:
            L.append(f"| {k} | {tA[k]} ({100.0 * tA[k] / n:.1f}%) | "
                     f"{tB[k]} ({100.0 * tB[k] / n:.1f}%) | "
                     f"{tC[k]} ({100.0 * tC[k] / (n * REPEATS):.1f}%) |")
    L.append("")
    fA = n - tA["correct"]
    fB = n - tB["correct"]
    L.append(f"The signatures invert between A and B, which is the point. Of "
             f"System A's {fA} failures, {tA['angle_only']} are angle-only "
             f"({100.0 * tA['angle_only'] / fA:.0f}%) -- the prediction is in the "
             f"right place and pointing the wrong way. Of System B's {fB} "
             f"failures, only {tB['angle_only']} are, while {tB['iou_only']} are "
             "overlap-only: right rotation, wrong place. System B's mean angle "
             "error is 3.9 degrees, a number System A structurally cannot produce "
             "because COCO boxes are axis-aligned and its orientation rule can only "
             "emit 0 or 90 degrees.\n")
    L.append(f"System C's dominant bucket is neither: {tC['both']} of "
             f"{n * REPEATS} calls ({100.0 * tC['both'] / (n * REPEATS):.1f}%) miss "
             "on angle and overlap simultaneously. A prediction that fails both "
             "criteria at once is not a mis-rotation or a mis-placement, it is a "
             "rectangle that has little to do with the object.\n\n")

    # ---- orientation stratification
    strat = defaultdict(list)
    for p in ids:
        strat[axial_stratum(gts[p])].append(p)
    L.append("## Condition breakdown: ground-truth orientation\n")
    L.append("Cornell ships no occlusion or lighting metadata, so the condition "
             "axes are the ones the annotations themselves support. This one "
             "splits the test set by whether any labelled grasp on the image sits "
             f"within {AXIAL_TOL_DEG:.0f} degrees of axis-aligned. It comes from "
             "the dataset's `cpos` files, not from any system's output, which is "
             "what makes it usable as a shared axis.\n")
    L.append("| Stratum | Images | A | B | C |")
    L.append("|---|---|---|---|---|")
    for s in ("axis-aligned", "diagonal"):
        m = strat[s]
        cells = []
        for sysname in ("A", "B", "C"):
            acc, k, tot = rate(m, correct, sysname)
            lo, hi = wilson(k, tot)
            cells.append(f"{acc:.1f}% [{lo:.1f}, {hi:.1f}]")
        L.append(f"| {s} | {len(m)} | " + " | ".join(cells) + " |")
    L.append("")
    dA = rate(strat["axis-aligned"], correct, "A")[0] - rate(strat["diagonal"], correct, "A")[0]
    dB = rate(strat["axis-aligned"], correct, "B")[0] - rate(strat["diagonal"], correct, "B")[0]
    dC = rate(strat["axis-aligned"], correct, "C")[0] - rate(strat["diagonal"], correct, "C")[0]
    L.append(f"System A drops {dA:.1f} points on images where every labelled grasp "
             "is diagonal, which is exactly the penalty its representation "
             f"predicts. System B moves {-dB:.1f} points in the other direction -- "
             "it is not merely unhurt by diagonal objects, it does slightly better "
             "on them -- which is what 'orientation is no longer the binding "
             f"constraint' looks like. System C moves {-dC:.1f} points, i.e. it is "
             "flat: its errors are not orientation errors at all, which is the "
             "same conclusion the compound-failure bucket reaches by a different "
             "route. Its move is in the same direction as System B's and a sixth "
             "the size, which is what no signal on an axis looks like.\n")
    L.append(f"The diagonal stratum has only {len(strat['diagonal'])} images and "
             "its intervals are correspondingly wide, so each individual cell is "
             "weak evidence. What is not weak is that three systems move in three "
             "different directions on the same split, which is harder to produce "
             "by chance than any one of the cells.\n\n")

    # ---- grasps per image
    L.append("## Condition breakdown: number of labelled grasps\n")
    L.append("The second axis the annotations support. More labelled grasps means "
             "more rectangles a prediction can match, so this is roughly a "
             "difficulty proxy.\n")
    L.append("| Labelled grasps | Images | A | B | C |")
    L.append("|---|---|---|---|---|")
    bins = [(2, 4), (5, 7), (8, 25)]
    for lo_b, hi_b in bins:
        m = [p for p in ids if lo_b <= len(gts[p]) <= hi_b]
        if not m:
            continue
        cells = [f"{rate(m, correct, s)[0]:.1f}%" for s in ("A", "B", "C")]
        L.append(f"| {lo_b}-{hi_b} | {len(m)} | " + " | ".join(cells) + " |")
    L.append("")
    L.append("This axis does not behave the way the difficulty-proxy reading "
             "predicts. All three systems do worst on the images with the MOST "
             "labelled grasps, not the fewest, even though more labelled grasps "
             "means more rectangles a prediction is allowed to match. The likely "
             "reason is that annotators labelled many grasps on objects that "
             "afford many grasps -- long, thin, multi-part things -- so the count "
             "is tracking object complexity more than it is tracking how much "
             "credit the metric hands out. Reported because it was computed, not "
             "because it supports the throughline; it is the weaker of the two "
             "condition axes and it is not used to argue anything.\n\n")

    # ---- object groups
    L.append("## Accuracy by object\n")
    L.append("Cornell ships no category labels, so the only externally-sourced "
             "grouping available is object identity from the frozen object-wise "
             "split -- 35 groups across the test set. That is the axis; the "
             "**names below are descriptive labels for readability and are not "
             "scoring ground truth**. They are the modal `object` string System C "
             "emitted for each group (a re-parse of its sealed log, no new calls), "
             "with a vote share showing how consistent that naming was.\n")
    L.append("Using either System A's COCO labels or System C's strings as the "
             "*stratification* axis would have biased the comparison toward "
             "whichever system produced the axis, which is why object_id is doing "
             "the grouping and the strings are only sitting next to it.\n")
    agree, disagree, unchecked, bnames = recon
    L.append("Cross-check, and its limits. A second, independent description of "
             "some objects exists in the split review's free-text notes. It turns "
             "out to be a weak check rather than a real second opinion: the notes "
             "were written per boundary PAIR, to justify a same/different "
             f"decision, so they only reach {len(agree) + len(disagree)} of the 35 "
             "groups, and several of the entries describe a segmentation artifact "
             "('tiny silver object in a distant uncropped scene') rather than "
             f"naming an object at all. Of the {len(agree) + len(disagree)} "
             f"reachable groups, {len(agree)} agree with the VLM name and "
             f"{len(disagree)} do not. The remaining {len(unchecked)} have no "
             "second source and rest on one source alone.\n")
    if disagree:
        L.append("**Neither guess is adopted for these.** Both sources are "
                 "themselves model-generated (one is System C's own output, the "
                 "other is free text from an earlier review pass) and neither is "
                 "ground truth, so picking a winner between two guesses would not "
                 "resolve anything -- it would just launder a guess into "
                 "something that reads as authoritative because it is sitting in "
                 "a results table. The table below shows the object as `object N "
                 "(label uncertain)`, with no committed name, for all 8 disputed "
                 "groups. Both raw guesses are recorded here so anyone who wants "
                 "to settle it can go look at the actual images.\n")
        L.append("| Object | VLM guess | Split-review guess |")
        L.append("|---|---|---|")
        for g in disagree:
            L.append(f"| {g} | {names[g][0]} | {bnames[g]} |")
        L.append("")
    L.append("| Object | Label (descriptive) | Vote share | Images | A | B | C |")
    L.append("|---|---|---|---|---|---|---|")
    for row in by_object:
        L.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}% | "
                 f"{row[5]}% | {row[6]}% |")
    L.append("")
    singles = sum(1 for row in by_object if row[3] == 1)
    L.append(f"**No significance is claimed at the object level.** {singles} of "
             f"{len(by_object)} groups contain a single image, where accuracy can "
             "only be 0% or 100%, and even the largest group is 9 images. Counts "
             "are printed next to every rate so no row can be read as a rate "
             "without its denominator.\n\n")

    # ---- paired tests
    L.append("## Are the differences real? Paired tests\n")
    L.append("All three systems ran on the same 123 images, so the comparison is "
             "paired and uses McNemar's exact test on the images where two systems "
             "disagreed. An unpaired test would discard the pairing for nothing.\n")
    L.append("| Comparison | First only | Second only | p |")
    L.append("|---|---|---|---|")
    b1, c1, p1 = mcnemar(vA, vB)
    L.append(f"| A vs B | {b1} | {c1} | {p1:.2g} |")
    ac = [mcnemar(vA, v) for v in vC]
    bc = [mcnemar(vB, v) for v in vC]
    L.append(f"| A vs C (5 repeats) | {min(x[0] for x in ac)}-{max(x[0] for x in ac)} | "
             f"{min(x[1] for x in ac)}-{max(x[1] for x in ac)} | "
             f"{max(x[2] for x in ac):.2g} (worst of 5) |")
    L.append(f"| B vs C (5 repeats) | {min(x[0] for x in bc)}-{max(x[0] for x in bc)} | "
             f"{min(x[1] for x in bc)}-{max(x[1] for x in bc)} | "
             f"{max(x[2] for x in bc):.2g} (worst of 5) |")
    L.append("")
    L.append("**System C is tested five times, not once.** Its output varies run "
             "to run, so collapsing it to a mean and then testing that mean as "
             "though it were a single draw would hide exactly the variance the "
             "spec asked to measure. Each repeat is tested separately and the "
             "worst p-value of the five is the one reported, so the conclusion "
             "does not depend on which repeat happens to be picked.\n")
    b5_lo, b5_hi = wilson(best5, n)
    a_lo, a_hi = wilson(accA, n)
    L.append("**What 'System C trails System A' is licensed to mean.** The "
             "strongest available version of that claim, stated against the "
             "hardest possible comparison -- System C's most flattering number "
             "against System A's least flattering one:\n")
    L.append(f"> System C's best-of-5 ceiling is {100.0 * best5 / n:.1f}% "
             f"({best5}/{n}), upper 95% bound {b5_hi:.1f}%. That figure requires "
             "five calls per image and an oracle that knows which of the five was "
             f"right. System A's single-call lower 95% bound is {a_lo:.1f}%. The "
             "intervals do not overlap, so the ordering does not depend on the "
             "point estimates being exact.\n")
    L.append("Best-of-5 is not compared against A's or B's single-call numbers "
             "anywhere else in this document, and it is not System C's headline. "
             "It appears here only because it is the number most favourable to "
             "System C, and the ordering survives it.\n\n")

    # ---- agreement
    ab_right = [p for p in ids if correct["A"][p] and correct["B"][p]]
    ab_wrong = [p for p in ids if not correct["A"][p] and not correct["B"][p]]
    onlyA = [p for p in ids if correct["A"][p] and not correct["B"][p]]
    onlyB = [p for p in ids if correct["B"][p] and not correct["A"][p]]
    c_any = [p for p in ids if any(correct["C"][p][r] for r in range(REPEATS))]
    all_right = [p for p in ab_right if p in set(c_any)]
    all_wrong = [p for p in ab_wrong if p not in set(c_any)]
    L.append("## Where the systems agree\n")
    L.append("System C needs a stated rule here, because it does not produce one "
             "verdict per image. Both rows below use the rule most generous to "
             "it: 'C correct' means at least one of its 5 repeats was correct, "
             "and 'C wrong' means none of the 5 were.\n")
    L.append("| | Images |")
    L.append("|---|---|")
    L.append(f"| A and B both correct | {len(ab_right)} |")
    L.append(f"| A and B both wrong | {len(ab_wrong)} |")
    L.append(f"| A correct, B wrong | {len(onlyA)} |")
    L.append(f"| B correct, A wrong | {len(onlyB)} |")
    L.append(f"| All three correct (C on at least 1 of 5) | {len(all_right)} |")
    L.append(f"| All three wrong (C on none of 5) | {len(all_wrong)} |")
    L.append("")
    L.append(f"{len(all_wrong)} images defeat every system tried, even giving "
             "System C five attempts. Those are the closest thing this project "
             "has to a difficulty floor, and they are the images worth looking at "
             f"first if a fourth system is ever built. The {len(onlyA) + len(onlyB)} "
             "images where A and B disagree are the more interesting set for "
             "understanding what the learned model actually bought.\n\n")

    # ---- tier 2
    L.append("## Reported per system, not compared across them\n")
    L.append("Some of the most informative numbers in this project exist for only "
             "one system. They are reported, but never tabulated side by side, "
             "because a three-column table implies a three-way comparison.\n")
    L.append("- **System C's repeat consistency** (mean self-agreement 22.0%, "
             "65.9% of images stable at 5/5 or 0/5, abstention curve reaching "
             "57.7% accuracy at 21.1% coverage). Systems A and B are deterministic "
             "functions of the image: the same pixels give the same rectangle "
             "every time, so their consistency is 100% *by construction*. Printing "
             "100% / 100% / 22.0% would imply A and B won a robustness comparison "
             "they were never entered into.\n")
    L.append("- **System B's val-to-test gap** (83.6% val to 79.7% test). Systems "
             "A and C have no val stage, so there is no such quantity for them.\n")
    L.append("- **System A's detector coverage** (49/123 images, 39.8%, with a "
             "segmentation fallback carrying the other 66). Neither B nor C has a "
             "coverage concept.\n")
    L.append("- **System C's parse rate** (614/615 calls, 99.8%). A and B cannot "
             "emit malformed output.\n")
    L.append("The asymmetry is a fact about the systems, not a gap in the "
             "analysis. Forcing a comparison to exist where it does not would be a "
             "worse failure than reporting three columns of different lengths. "
             "Full detail for each lives in `system_a_results.md`, "
             "`system_b_results.md` and `system_c_results.md`.\n\n")

    # ---- force
    fa, fc = force_distributions(ids)
    L.append("## Grip force, descriptive only\n")
    L.append("Spec section 6 requires this be reported as a distribution and never "
             "as an accuracy, because the dataset carries no force ground truth "
             "and scoring it would mean inventing one.\n")
    L.append("| Level | System A (123 images) | System C (615 calls) |")
    L.append("|---|---|---|")
    for lev in ("LOW", "MEDIUM", "HIGH"):
        if fa[lev] or fc[lev]:
            L.append(f"| {lev} | {fa[lev]} | {fc[lev]} |")
    L.append("")
    L.append("System B has no force output at all -- it regresses grasp geometry "
             "only -- and that absence is stated rather than left as an empty "
             "column.\n\n")

    # ---- sheets
    L.append("## Comparison sheets\n")
    L.append(f"{len(picked)} images in `comparison_sheets/`, all three systems "
             "drawn on the same frame: green ground truth, red System A, blue "
             "System B, orange System C's five repeats. The selection rule is "
             "fixed and deterministic (equal quotas from three categories, in "
             "sorted id order) so the illustrations are not a place a nicer set "
             "could be shopped for.\n")
    for label in ("B fixes A", "B still misses", "all three miss"):
        chosen = [f"pcd{p:04d}" for l, p in picked if l == label]
        L.append(f"- **{label}**: {', '.join(chosen)}")
    L.append("\n")

    # ---- methods: verification discipline
    L.append("## Method note: verification discipline as a project pattern\n")
    L.append("This is a claim about process, not about grasping, which is why it "
             "sits in a methods subsection rather than among the results.\n")
    L.append("Three times in this project, a self-authored cross-check caught a "
             "bug in the project's own code *before* a number was reported rather "
             "than after. During split generation, a corruption in the grouping "
             "output was caught and fixed before the frozen split was used for "
             "anything. In System B, an early-stopping rule let a lucky "
             "pre-training epoch become the 'best' checkpoint, caught and fixed "
             "with a warmup-ineligibility rule and an epoch-40 floor justified "
             "from measured loss and val-volatility curves. In System C, an "
             "automated contamination-probe check reported 1/10 recognitions "
             "where an independent manual read of the same ten replies said 0/10; "
             "the disagreement was chased down to a smart-quote mismatch (the "
             "check tested for a straight apostrophe, the model wrote a curly "
             "one) that silently broke the negation logic.\n")
    L.append("The instances have nothing technical in common. What they share is "
             "the procedure: an automated result was checked against an "
             "independent method -- a second computation, a manual read, a "
             "hand-computed synthetic case -- and where the two disagreed, neither "
             "was trusted until the disagreement was explained. None of the three "
             "was found by an external reviewer, and none announced itself through "
             "a suspicious-looking headline number; two of them would have "
             "produced perfectly plausible results.\n")
    L.append("This section found a fourth thing of the same shape, though a milder "
             "one. `is_correct` returns `correct` computed against every labelled "
             "grasp, but returns its `best_iou`/`best_angle` diagnostics for the "
             "single highest-overlap grasp regardless of whether that one passed "
             "the angle test. On 9 of 123 System B images and 9 of 614 System C "
             "calls the two disagree, because the prediction matched a different "
             "rectangle than the one it overlapped most. **No published number is "
             "wrong** -- both systems' taxonomy code tests `correct` first, which "
             "is the ordering that makes it come out right -- so this is a "
             "reuse hazard in a shared function's return signature rather than a "
             "caught bug, and it is recorded as such rather than inflated. It is "
             "the reason this script recomputes every taxonomy from geometry "
             "instead of reading the stored diagnostic columns.\n\n")

    # ---- scope
    L.append("## Scope of these claims\n")
    L.append("**What this comparison establishes.** On the Cornell Grasping "
             "Dataset, at 640x480, under the standard 30-degree / 25%-IoU metric, "
             "on 123 held-out images of 35 objects that appear nowhere in "
             "training: one frozen prompt to GPT-4o producing free-text JSON "
             "coordinates trails both a COCO-detector rule baseline and a "
             "fine-tuned ResNet18, decisively and with non-overlapping "
             "intervals.\n")
    L.append("**What it does not establish**, written as the specific sentences "
             "this evidence does not support:\n")
    L.append("- Not *VLMs cannot do grasp prediction*. One model, one prompt, one "
             "elicitation method. Set-of-marks prompting, point-and-click "
             "grounding, or a grounded detection head might bind reasoning to "
             "coordinates far better. That comparison was not run.\n")
    L.append("- Not *GPT-4o lacks spatial grounding*. The finding is about "
             "free-text coordinate output specifically -- the model's `reasoning` "
             "strings frequently named a real, sensible part of the object while "
             "the coordinates in the same reply did not land on it. That is a "
             "binding failure in one output channel, not a perception result.\n")
    L.append("- Not that System B is solved. 79.7% on 123 images of 35 objects, "
             f"one dataset, no hardware, interval [{wilson(accB, n)[0]:.1f}, "
             f"{wilson(accB, n)[1]:.1f}]. Spec section 8 forbids calling this a "
             "finished grasp system and that still holds.\n")
    L.append("- Not that 57.7% is *the* classical-baseline number. It is one "
             "specific rule, and System A's own results doc shows a segmentation "
             "fallback did most of the work while the pretrained detector fired on "
             "39.8% of images.\n")
    L.append("- Nothing that would flip under training-data contamination. Cornell "
             "is public and widely mirrored, so a frontier model could plausibly "
             "have seen it; a 10-image probe came back 0/10 and is reported as a "
             "weak indicator, not a clearance. Contamination can only inflate "
             "System C, so every conclusion drawn here is of the form 'C trails', "
             "which survives it. No 'C does surprisingly well' claim is made "
             "anywhere, so nothing depends on the probe.\n")
    L.append("- No seen-versus-unseen category breakdown. The split is "
             "object-wise, so every test object is unseen by construction and the "
             "breakdown collapses to a single cell. That is a property of the "
             "split design, reported rather than faked into two rows.\n")
    L.append("- No occlusion or lighting breakdown. Cornell ships no such "
             "metadata, and hand-labelling it would be exactly the self-authored "
             "ground truth spec section 8 rules out. The two condition axes above "
             "are what the annotations actually support.\n")
    L.append("- No object-level significance. See the counts in that table.\n")

    RESULTS_MD.write_text("\n".join(L) + "\n")


# ------------------------------------------------------------ main


def main():
    ids, obj = test_ids()
    gts = {p: load_rects(p) for p in ids}
    a, b, c = load_a(), load_b(), load_c()

    missing = [p for p in ids if p not in a or p not in b or p not in c]
    if missing:
        raise SystemExit(f"missing predictions for {len(missing)} test images")
    strays = set(a) | set(b) | set(c)
    if strays - set(ids):
        raise SystemExit(f"SPLIT LEAK: {len(strays - set(ids))} non-test ids present")
    print(f"Split hygiene OK: {len(ids)} test images, all three systems present.")

    correct, bucket = score_everything(ids, gts, a, b, c)
    got, bad = reproduction_check(ids, correct)
    for sysname, (k, n_) in SEALED.items():
        print(f"  {sysname}: re-scored {got[sysname]}/{n_}, sealed {k}/{n_}")
    if bad:
        raise SystemExit("SEALED NUMBERS NOT REPRODUCED:\n  " + "\n  ".join(bad))
    print("Sealed counts reproduced exactly. Shared scoring path agrees with all "
          "three sealed runs.")

    names = vlm_names(ids, obj)
    bnames = boundary_names(ids, obj)
    recon = reconcile_names(names, bnames)
    agree, disagree, unchecked, _ = recon
    print(f"\nObject names: {len(names)} groups named, {len(agree)} agree with the "
          f"split-review text, {len(disagree)} disagree, {len(unchecked)} unchecked.")
    for g in disagree:
        print(f"  DISAGREE object {g}: vlm='{names[g][0]}' review='{bnames[g]}'")

    disputed = set(disagree)
    write_per_image(ids, obj, names, gts, correct, bucket, disputed)
    by_object = write_by_object(ids, obj, names, correct, disputed)
    picked = pick_sheets(ids, correct)
    draw_sheets(picked, gts, a, b, c, correct)
    write_results(ids, obj, gts, correct, bucket, names, recon, by_object, picked)

    print(f"\nWrote {PER_IMAGE_CSV}")
    print(f"Wrote {BY_OBJECT_CSV}")
    print(f"Wrote {len(picked)} sheets to {SHEETS}")
    print(f"Wrote {RESULTS_MD}")


if __name__ == "__main__":
    main()
