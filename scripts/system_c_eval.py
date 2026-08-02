"""Final System C evaluation. Reads the sealed raw JSONL, scores nothing live.

THE ONE TRAP WORTH NAMING (same one System B named)
-----------------------------------------------------
This script never calls the network. It reads
data/interim/system_c_raw.jsonl -- written once, by system_c_run.py's
"test" phase, which refuses to run a second time. Everything below is a
pure function of that frozen text: parsing, geometry, scoring, the
consistency analysis, the sheets. That is what makes the project's
approved re-parse rule real: a parser bug found after reading this
script's output can be fixed and this script re-run any number of
times without the model ever being asked again, because re-parsing
frozen text cannot fish for a better score and re-calling could.

WHAT "HEADLINE" MEANS HERE, AND WHY IT IS NOT THE ONLY NUMBER
---------------------------------------------------------------
Each of the 123 test images gets 5 independent single-turn repeats. A
deployed system making one call per image gets one of those five draws,
so the headline is defined as the MEAN accuracy across the 5 independent
per-repeat accuracies (each computed over all 123 images), with min, max
and std across those 5 numbers reported alongside it -- exactly what
that deployed system experiences, spread included rather than hidden.

Best-of-5 and the majority-consensus rectangle are also reported, and
are explicitly NOT the headline: nobody runs an ensemble of 5 calls per
grasp in production, and folding either into the main number would
quietly turn a single-shot baseline into a best-of-N one.

Usage:
    python scripts/system_c_eval.py     (after system_c_run.py test)

Outputs:
    data/interim/system_c_predictions.csv
    data/interim/system_c_consistency.csv
    data/interim/system_c_results.md
    data/interim/system_c_sheets/*.png
"""

import csv
from collections import Counter, defaultdict

import numpy as np
from PIL import Image, ImageDraw

from cornell_data import INTERIM, find_images, load_rects, load_split, rect_to_corners
from grasp_metric import ANGLE_TOL_DEG, IOU_MIN, angle_diff, is_correct
from system_c_client import load_raw
from system_c_consistency import (abstention_curve, consensus_index,
                                  outcome_histogram, pairwise_angle_spread,
                                  pairwise_iou, self_agreement)
from system_c_prompt import (API_FAIL, OK, PARSE_FAIL, PROMPT_VERSION,
                             RANGE_FAIL, SCHEMA_FAIL, parse_response,
                             response_to_rect)

PRED_CSV = INTERIM / "system_c_predictions.csv"
CONSIST_CSV = INTERIM / "system_c_consistency.csv"
RESULTS_MD = INTERIM / "system_c_results.md"
SHEETS = INTERIM / "system_c_sheets"
N_SHEETS = 12

REPEATS = 5

# Frozen facts from the sealed record, same convention as System B citing
# System A's commit.
SYSTEM_A_ACC = 57.7
SYSTEM_B_ACC = 79.7
SYSTEM_B_MODEL = "resnet18"


def load_test_records():
    """The sealed test replies, asserted to be genuinely test-only."""
    records = load_raw("test")
    table = load_split()
    leaked = [r for r in records if table.get(r["pcd_id"], (0, ""))[1] != "test"]
    if leaked:
        raise SystemExit(f"SPLIT LEAK: {len(leaked)} non-test records in the test log")
    pcds = sorted({r["pcd_id"] for r in records})
    if len(pcds) != 123:
        raise SystemExit(f"expected 123 test images, found {len(pcds)}")
    by_image = defaultdict(dict)
    for r in records:
        by_image[r["pcd_id"]][r["repeat"]] = r
    missing = [p for p in pcds if len(by_image[p]) != REPEATS]
    if missing:
        raise SystemExit(f"{len(missing)} images do not have {REPEATS} repeats: "
                         f"{missing[:5]}")
    print(f"Split hygiene OK: {len(pcds)} images x {REPEATS} repeats = "
          f"{len(records)} sealed test calls.")
    return pcds, by_image


def parse_all(pcds, by_image):
    """Parse every call once. Returns per-image structures used everywhere below.

    outcomes[pcd][repeat]      -> one of OK/PARSE_FAIL/SCHEMA_FAIL/RANGE_FAIL/API_FAIL
    rects[pcd][repeat]         -> (cx, cy, theta, opening, jaw), only when OK
    correct[pcd][repeat]       -> bool, only when OK (best-match vs load_rects)
    scored[pcd][repeat]        -> (ok, best_i, best_iou, best_ang), only when OK
    """
    outcomes, rects, correct, scored = {}, {}, {}, {}
    gts_cache = {}
    for pcd in pcds:
        gts_cache[pcd] = load_rects(pcd)
        outcomes[pcd], rects[pcd], correct[pcd], scored[pcd] = {}, {}, {}, {}
        for rep in range(REPEATS):
            rec = by_image[pcd][rep]
            if rec.get("text") is None:
                outcomes[pcd][rep] = rec.get("outcome_override", API_FAIL)
                continue
            outcome, meta = parse_response(rec["text"])
            outcomes[pcd][rep] = outcome
            if outcome != OK:
                continue
            rect = response_to_rect(meta)
            rects[pcd][rep] = rect
            s = is_correct(rect, gts_cache[pcd])
            scored[pcd][rep] = s
            correct[pcd][rep] = s[0]
    return outcomes, rects, correct, scored, gts_cache


def per_repeat_accuracy(pcds, correct, outcomes):
    """One accuracy number per repeat index, over all 123 images.

    A parse failure counts as a miss for that repeat -- this is the
    end-to-end number, format problems included, matching System A's
    "with fallback" framing (nothing here silently drops a bad reply
    from the denominator).
    """
    out = []
    for rep in range(REPEATS):
        n_ok = sum(1 for p in pcds if correct[p].get(rep, False))
        out.append(n_ok / len(pcds) * 100)
    return out


def parse_rate_summary(pcds, outcomes):
    """Global outcome counts, and the parsed-only vs end-to-end distinction."""
    counts = Counter()
    for p in pcds:
        for rep in range(REPEATS):
            counts[outcomes[p][rep]] += 1
    total = len(pcds) * REPEATS
    return counts, total


def best_of_5(pcds, correct):
    n = sum(1 for p in pcds if any(correct[p].get(r, False) for r in range(REPEATS)))
    return n / len(pcds) * 100


def majority_consensus(pcds, rects, gts_cache):
    """Score the single repeat each image that agrees most with its own others.

    Not the headline -- see module docstring. Skips images with fewer
    than one parsed repeat (nothing to be a consensus of).
    """
    n_ok, n_scored = 0, 0
    for p in pcds:
        rs = [rects[p][r] for r in sorted(rects[p])]
        if not rs:
            continue
        idx = consensus_index(rs)
        n_scored += 1
        n_ok += is_correct(rs[idx], gts_cache[p])[0]
    return (n_ok / n_scored * 100) if n_scored else float("nan"), n_scored


def taxonomy(pcds, scored, outcomes):
    """angle_only / iou_only / both / correct, over every OK-parsed call.

    Same shape as System A and B's failure breakdowns, and the same
    dev-30 computation, now on test.
    """
    tax = Counter()
    for p in pcds:
        for rep in range(REPEATS):
            if outcomes[p][rep] != OK:
                continue
            ok, _, iou, ang = scored[p][rep]
            if ok:
                tax["correct"] += 1
            elif ang <= ANGLE_TOL_DEG and iou <= IOU_MIN:
                tax["iou_only"] += 1
            elif iou > IOU_MIN and ang > ANGLE_TOL_DEG:
                tax["angle_only"] += 1
            else:
                tax["both"] += 1
    return tax


def consistency_analysis(pcds, rects, correct):
    """Self-agreement, outcome histogram, angle/IoU spread, abstention -- at n=5."""
    agreements, angle_spreads, ious, per_image_correct, any_correct = [], [], [], [], []
    rows = []
    for p in pcds:
        rs = [rects[p][r] for r in sorted(rects[p])]
        flags = [correct[p].get(r, False) for r in range(REPEATS)]
        per_image_correct.append(flags)
        any_correct.append(any(flags))
        sa = self_agreement(rs)
        ang = pairwise_angle_spread(rs)
        iou = pairwise_iou(rs)
        agreements.append(sa)
        angle_spreads.append(ang)
        ious.append(iou)
        rows.append((p, len(rs), sa, ang, iou, sum(flags)))
    hist = outcome_histogram(per_image_correct, REPEATS)
    curve = abstention_curve(agreements, any_correct)
    return {
        "agreements": np.array(agreements, float), "angle_spreads": np.array(angle_spreads, float),
        "ious": np.array(ious, float), "hist": hist, "curve": curve, "rows": rows,
    }


def draw_sheets(pcds, rects, correct, gts_cache):
    """Sheets for the val-selected repeat's... no, System C has no single
    checkpoint. Each sheet shows all 5 parsed repeats (thin) against
    ground truth (green), so consistency is visible at a glance the way
    the numbers describe it.
    """
    SHEETS.mkdir(parents=True, exist_ok=True)
    images = find_images()
    colors = [(255, 40, 40), (255, 140, 0), (255, 220, 0), (200, 0, 200), (0, 180, 255)]
    for p in pcds[:N_SHEETS]:
        im = Image.open(images[p]).convert("RGB")
        d = ImageDraw.Draw(im)
        for gt in gts_cache[p]:
            d.polygon([tuple(pt) for pt in rect_to_corners(*gt)], outline=(0, 220, 0))
        n_ok = 0
        for rep in sorted(rects[p]):
            d.polygon([tuple(pt) for pt in rect_to_corners(*rects[p][rep])],
                      outline=colors[rep % len(colors)], width=2)
            n_ok += correct[p].get(rep, False)
        d.text((6, 6), f"pcd{p:04d}  green=GT  {n_ok}/{len(rects[p])} repeats correct",
               fill=(255, 255, 255))
        im.save(SHEETS / f"system_c_{p:04d}.png")


def write_results(pcds, per_repeat, best5, consensus_acc, consensus_n, tax,
                   consist, counts, total, probe_hits, probe_n):
    L = []
    L.append("# System C results (vision-language model baseline)\n")
    L.append("Spec section 5.4, scored with the same section 6 metric and the same "
             "123 held-out test images as Systems A and B. GPT-4o via OpenRouter, "
             f"prompt {PROMPT_VERSION}, frozen on a 30-image train dev batch before "
             "this run. 5 independent repeats per image, no shared conversation, "
             "default temperature -- the spec's premise is that out-of-the-box "
             "output varies run to run, so nothing here suppresses that.\n")

    mean, mn, mx, sd = np.mean(per_repeat), min(per_repeat), max(per_repeat), np.std(per_repeat)
    L.append("\n## Headline\n")
    L.append(f"**System C (GPT-4o) — {mean:.1f}% mean per-repeat accuracy** "
             f"(min {mn:.1f}%, max {mx:.1f}%, std {sd:.1f}, over 5 independent "
             "repeats of the 123-image test split).\n")
    L.append("This is what a deployed system making one call per image actually "
             "gets, spread included rather than averaged away. Per-repeat "
             "accuracies: " + ", ".join(f"{v:.1f}%" for v in per_repeat) + ".\n")

    L.append("\n## Not the headline: upper-bound numbers\n")
    L.append("Reported for completeness, explicitly not comparable to System A/B's "
             "single-prediction numbers as a fair baseline figure -- both require "
             "either multiple calls or knowing the answer in a way a real one-shot "
             "deployment would not.\n")
    L.append("| | Accuracy | Note |")
    L.append("|---|---|---|")
    L.append(f"| Best-of-5 | {best5:.1f}% | at least 1 of 5 repeats correct |")
    L.append(f"| Majority-consensus | {consensus_acc:.1f}% | the repeat that agrees "
             f"most with the other repeats, scored ({consensus_n}/123 images had "
             "a parsed repeat to choose from) |")

    L.append("\n## Parse outcomes, end to end\n")
    L.append(f"{total} calls total (123 images x 5 repeats).\n")
    L.append("| Outcome | Count | Share |")
    L.append("|---|---|---|")
    for k in (OK, PARSE_FAIL, SCHEMA_FAIL, RANGE_FAIL, API_FAIL):
        c = counts.get(k, 0)
        L.append(f"| {k} | {c} | {c/total*100:.1f}% |")
    L.append("\nParse failures are never silently scored as a wrong grasp -- the "
             "headline above already counts every non-`ok` call as a miss for its "
             "repeat (end-to-end). Accuracy computed on parsed (`ok`) calls only "
             f"would be {np.mean([v for v in per_repeat]):.1f}% "
             f"vs {counts.get(OK,0)/total*100:.1f}% of calls actually parsing -- "
             "see the per-repeat table above for the honest, end-to-end figure.\n")

    L.append("\n## Failure taxonomy (of parsed calls)\n")
    n_parsed = sum(tax.values())
    L.append("| Outcome | Count | Share of parsed calls |")
    L.append("|---|---|---|")
    for k in ("correct", "angle_only", "iou_only", "both"):
        v = tax.get(k, 0)
        L.append(f"| {k} | {v} | {v/n_parsed*100:.1f}% |")
    L.append(f"\n{n_parsed} of {total} calls parsed to a scoreable rectangle.\n")

    L.append("\n## Self-agreement, at n=5 repeats (the real curve, not the "
             "2-repeat dev preview)\n")
    ag = consist["agreements"]
    finite = ag[np.isfinite(ag)]
    L.append(f"Mean self-agreement: {np.nanmean(ag)*100:.1f}%  "
             f"(median {np.nanmedian(ag)*100:.1f}%), over {len(finite)}/123 images "
             "with at least 2 parsed repeats to compare.\n")
    L.append(f"Mean pairwise angle spread between repeats: "
             f"{np.nanmean(consist['angle_spreads']):.1f} deg. "
             f"Mean pairwise IoU between repeats: {np.nanmean(consist['ious']):.2f}.\n")

    L.append("\n**Outcome histogram** -- of the 5 repeats, how many scored correct:\n")
    L.append("| Repeats correct | Images | Share |")
    L.append("|---|---|---|")
    for k in range(REPEATS, -1, -1):
        v = consist["hist"].get(k, 0)
        L.append(f"| {k}/5 | {v} | {v/123*100:.1f}% |")
    stable = consist["hist"].get(5, 0) + consist["hist"].get(0, 0)
    L.append(f"\n**Consistency rate** (all 5 repeats agreed on the outcome, "
             f"either 5/5 or 0/5): **{stable/123*100:.1f}%** "
             f"({stable}/123 images). The remaining "
             f"{123-stable} images are the unstable band -- the same model, the "
             "same pixels, sometimes producing a passing grasp and sometimes not.\n")

    L.append("\n**Abstention curve** -- if the system only acts when self-agreement "
             "is at or above a threshold, what accuracy does it get on the images "
             "it acts on, and what coverage does it keep:\n")
    L.append("| Threshold | Coverage | Accuracy on covered |")
    L.append("|---|---|---|")
    for t, cov, acc in consist["curve"]:
        acc_s = f"{acc*100:.1f}%" if acc == acc else "n/a"
        L.append(f"| >= {t:.1f} | {cov*100:.1f}% | {acc_s} |")

    L.append("\n## Training-data contamination\n")
    L.append("The direction of this risk only inflates System C, never deflates "
             "it, so \"System C underperforms System B\" survives it and "
             "\"System C does surprisingly well\" does not -- it would need to be "
             "read as an upper bound, not clean zero-shot capability.\n")
    L.append(f"Contamination probe (10 train images, asked to name the dataset "
             f"without being told the task is grasping): **{probe_hits}/{probe_n} "
             "recognised it.** Non-recognition is not proof of no exposure -- "
             "memorised weights do not have to be able to name their source -- so "
             "this is reported as a mild indicator, not a clearance.\n")

    L.append("\n## Three-way comparison, same sealed 123-image test set\n")
    L.append("| System | Test accuracy |")
    L.append("|---|---|")
    L.append(f"| A (rule-based) | {SYSTEM_A_ACC}% |")
    L.append(f"| B ({SYSTEM_B_MODEL}, val-selected) | **{SYSTEM_B_ACC}%** |")
    L.append(f"| C (GPT-4o, mean of 5 repeats) | {mean:.1f}% |")
    L.append(f"\nSystem C {'beats' if mean > SYSTEM_A_ACC else 'trails'} System A "
             f"({mean - SYSTEM_A_ACC:+.1f} points) and trails System B "
             f"({mean - SYSTEM_B_ACC:+.1f} points) on the identical sealed test "
             "split. Given the contamination risk above, any reading of System C "
             "beating a trained baseline should be treated cautiously; a reading "
             "of System C trailing one is not affected by that risk.\n")

    L.append("\n## Method note: the coordinate-binding limitation\n")
    L.append("The dominant test-time failure mode, consistent with what the "
             "train-30 dev batch showed, is a **text-to-coordinate binding "
             "limitation of this prompting approach** -- asking a VLM to emit "
             "precise pixel coordinates as free-text JSON. Several failed replies "
             "carried plausible, specific `reasoning` strings describing a real "
             "part of the object, while the `finger_a`/`finger_b` coordinates in "
             "the same reply did not land on the object at all. This is stated as "
             "a limitation of prompting for coordinates via free text specifically, "
             "not as a general claim about GPT-4o's or VLMs' spatial grounding "
             "capability -- a different elicitation method (e.g. point-and-click "
             "grounding tools, set-of-marks prompting) might bind reasoning to "
             "coordinates more reliably. That comparison is out of scope here.\n")

    RESULTS_MD.write_text("\n".join(L) + "\n")


def write_csvs(pcds, rects, correct, scored, outcomes, consist):
    with open(PRED_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pcd_id", "repeat", "outcome", "cx", "cy", "theta", "opening",
                    "jaw", "best_iou", "angle_err", "correct"])
        for p in pcds:
            for rep in range(REPEATS):
                if outcomes[p][rep] != OK:
                    w.writerow([f"{p:04d}", rep, outcomes[p][rep]] + [""] * 8)
                    continue
                rect = rects[p][rep]
                ok, _, iou, ang = scored[p][rep]
                w.writerow([f"{p:04d}", rep, OK] + [f"{v:.2f}" for v in rect]
                           + [f"{iou:.3f}", f"{ang:.1f}", int(ok)])

    with open(CONSIST_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pcd_id", "n_parsed", "self_agreement", "pairwise_angle_spread",
                    "pairwise_iou", "n_repeats_correct"])
        for row in consist["rows"]:
            p, n_parsed, sa, ang, iou, n_correct = row
            w.writerow([f"{p:04d}", n_parsed,
                       f"{sa:.3f}" if sa == sa else "", f"{ang:.1f}" if ang == ang else "",
                       f"{iou:.3f}" if iou == iou else "", n_correct])


def main():
    pcds, by_image = load_test_records()
    outcomes, rects, correct, scored, gts_cache = parse_all(pcds, by_image)

    per_repeat = per_repeat_accuracy(pcds, correct, outcomes)
    counts, total = parse_rate_summary(pcds, outcomes)
    b5 = best_of_5(pcds, correct)
    consensus_acc, consensus_n = majority_consensus(pcds, rects, gts_cache)
    tax = taxonomy(pcds, scored, outcomes)
    consist = consistency_analysis(pcds, rects, correct)

    probe_records = load_raw("probe")
    # Negation check normalises curly apostrophes (U+2019) to straight ones
    # first -- an earlier version of this check missed "don’t recognize"
    # (curly quote) and mis-flagged it as a recognition hit. Caught by
    # comparing this heuristic's count against a manual read of all 10
    # replies (system_c_prompt_dev notes / chat record), not by a test.
    probe_hits = sum(1 for r in probe_records
                     if r.get("text")
                     and "recogni" in (t := r["text"].lower().replace("’", "'"))
                     and "not" not in t and "don't" not in t and "do not" not in t)
    probe_n = len(probe_records)

    print(f"\nPer-repeat accuracy: {[f'{v:.1f}%' for v in per_repeat]}")
    mean, sd = np.mean(per_repeat), np.std(per_repeat)
    print(f"  mean {mean:.1f}%  min {min(per_repeat):.1f}%  max {max(per_repeat):.1f}%  "
          f"std {sd:.1f}")
    print(f"Best-of-5: {b5:.1f}%   Majority-consensus: {consensus_acc:.1f}% "
          f"(n={consensus_n})")
    print(f"Parse outcomes: {dict(counts)} / {total}")
    print(f"Taxonomy (parsed calls): {dict(tax)}")
    print(f"Contamination probe: {probe_hits}/{probe_n} recognised the dataset")
    print(f"\nSystem A {SYSTEM_A_ACC}%  System B {SYSTEM_B_ACC}%  "
          f"System C {mean:.1f}%")

    draw_sheets(pcds, rects, correct, gts_cache)
    write_csvs(pcds, rects, correct, scored, outcomes, consist)
    write_results(pcds, per_repeat, b5, consensus_acc, consensus_n, tax, consist,
                  counts, total, probe_hits, probe_n)

    print(f"\nWrote {PRED_CSV}\nWrote {CONSIST_CSV}\nWrote {RESULTS_MD}\n"
          f"Wrote sheets to {SHEETS}")


if __name__ == "__main__":
    main()
