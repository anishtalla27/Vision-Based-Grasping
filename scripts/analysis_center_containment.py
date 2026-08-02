"""P5 (research_findings.md, approved 2026-08-02, geometric-only form).

READ-ONLY against every sealed artifact. Writes exactly one new file,
data/interim/center_containment_analysis.md, which is not part of the
sealed Section 6 bundle and is not referenced by any frozen script.

WHAT THIS MEASURES
-------------------
For each prediction (System A: 1/image, System B: 1/image, System C:
1/repeat), whether the predicted grasp CENTER (cx, cy) falls inside the
convex hull of the four corners of every ground-truth grasp rectangle
for that image. This is a purely geometric test -- no judgment about
whether a model's stated reasoning was "plausible" enters anywhere, per
the constraint research_findings.md Part 3 / P5 states explicitly:
only the geometric version is in scope, because a plausibility judgment
would be self-authored ground truth (spec section 8).

A center outside the hull of every labelled grasp is a purely spatial
fact: the prediction is not merely mis-angled or under-sized, it is
not object-adjacent by the loosest possible spatial test. This gives a
quantitative comparator across A/B/C for the "365/615 System C calls
fail both criteria simultaneously" observation already in
comparison_results.md, using only geometry already implied by the
sealed cpos files and the sealed prediction CSVs.

This script re-parses only already-frozen data:
  - data/raw/cornell_grasp/*/pcd*cpos.txt (ground truth, via cornell_data.load_rects)
  - data/interim/system_{a,b,c}_predictions.csv (frozen predictions)
No API call is made. No model is run. No file under data/interim that
existed before this script runs is modified.
"""

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from cornell_data import load_rects, rect_to_corners, split_ids
from grasp_dataset import CROP_X0, CROP_Y0, SCALE

INTERIM = Path("data/interim")
OUT_PATH = INTERIM / "center_containment_analysis.md"


def convex_hull(points):
    """Andrew's monotone chain. points: (N,2) array. Returns hull vertices, CCW."""
    pts = sorted(set(map(tuple, points)))
    if len(pts) <= 2:
        return np.array(pts)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return np.array(lower[:-1] + upper[:-1])


def point_in_hull(point, hull, tol=1e-7):
    """True if `point` is inside or on the boundary of convex polygon `hull` (CCW)."""
    if len(hull) < 3:
        return False
    x, y = point
    n = len(hull)
    for i in range(n):
        ax, ay = hull[i]
        bx, by = hull[(i + 1) % n]
        cross = (bx - ax) * (y - ay) - (by - ay) * (x - ax)
        if cross < -tol:
            return False
    return True


def gt_hull_for_image(pcd_id):
    rects = load_rects(pcd_id, "cpos")
    if not rects:
        return None
    all_corners = np.concatenate([rect_to_corners(*r) for r in rects], axis=0)
    return convex_hull(all_corners)


def load_predictions_a():
    out = {}
    with open(INTERIM / "system_a_predictions.csv", newline="") as f:
        for row in csv.DictReader(f):
            pcd_id = int(row["pcd_id"])
            if row["cx"] == "":
                out[pcd_id] = [None]  # no prediction possible
            else:
                out[pcd_id] = [(float(row["cx"]), float(row["cy"]))]
    return out


def load_predictions_b():
    """System B's predictions are frozen in the 224x224 crop frame (see
    grasp_dataset.py), not the 640x480 frame the ground-truth cpos files and
    Systems A/C use. Pulled back into the common 640x480 frame with the
    exact inverse affine already used for this purpose in
    system_all_compare.py (imported constants, not re-derived) -- the
    val/test crop is deterministic with no augmentation, so the inverse is
    exact, not approximate.
    """
    out = {}
    with open(INTERIM / "system_b_predictions.csv", newline="") as f:
        for row in csv.DictReader(f):
            pcd_id = int(row["pcd_id"])
            cx, cy = float(row["cx"]), float(row["cy"])
            out[pcd_id] = [(cx / SCALE + CROP_X0, cy / SCALE + CROP_Y0)]
    return out


def load_predictions_c():
    out = {}
    with open(INTERIM / "system_c_predictions.csv", newline="") as f:
        for row in csv.DictReader(f):
            pcd_id = int(row["pcd_id"])
            out.setdefault(pcd_id, [])
            if row["outcome"] != "ok" or row["cx"] == "":
                out[pcd_id].append(None)  # parse_fail etc: not a spatial prediction
            else:
                out[pcd_id].append((float(row["cx"]), float(row["cy"])))
    return out


def score_system(name, predictions, test_ids, hulls):
    total = 0
    contained = 0
    outside = 0
    no_pred = 0
    per_image_rows = []
    for pcd_id in test_ids:
        hull = hulls[pcd_id]
        preds = predictions.get(pcd_id, [])
        n_out_this_image = 0
        n_pred_this_image = 0
        for p in preds:
            total += 1
            if p is None:
                no_pred += 1
                continue
            n_pred_this_image += 1
            if hull is not None and point_in_hull(p, hull):
                contained += 1
            else:
                outside += 1
                n_out_this_image += 1
        if n_pred_this_image > 0:
            per_image_rows.append((pcd_id, n_out_this_image, n_pred_this_image))
    scored = contained + outside
    return {
        "name": name,
        "total": total,
        "contained": contained,
        "outside": outside,
        "no_pred": no_pred,
        "scored": scored,
        "outside_rate": outside / scored if scored else float("nan"),
        "per_image_rows": per_image_rows,
    }


def main():
    test_ids = split_ids("test")
    assert len(test_ids) == 123, f"expected 123 test images, got {len(test_ids)}"

    hulls = {pcd_id: gt_hull_for_image(pcd_id) for pcd_id in test_ids}
    n_no_gt = sum(1 for h in hulls.values() if h is None)

    preds_a = load_predictions_a()
    preds_b = load_predictions_b()
    preds_c = load_predictions_c()

    result_a = score_system("A", preds_a, test_ids, hulls)
    result_b = score_system("B", preds_b, test_ids, hulls)
    result_c = score_system("C", preds_c, test_ids, hulls)

    for r in (result_a, result_b, result_c):
        assert r["total"] in (123, 615), f"unexpected total for {r['name']}: {r['total']}"

    lines = []
    lines.append("# Center-containment analysis (P5, geometric-only, per research_findings.md)")
    lines.append("")
    lines.append(
        "Generated by `scripts/analysis_center_containment.py`, approved 2026-08-02 in "
        "the geometric-only form specified in `research_findings.md` Part 3 / P5. "
        "Re-parses only frozen `data/raw/cornell_grasp` cpos files and frozen "
        "`data/interim/system_{a,b,c}_predictions.csv`. No API call, no model run, "
        "no sealed file modified. This file is exploratory analysis, not part of the "
        "Section 6 sealed bundle, and is not referenced by any frozen script."
    )
    lines.append("")
    lines.append(
        "**What is measured:** for each prediction, whether the predicted grasp "
        "center (cx, cy) falls inside the convex hull of the corners of every "
        "labelled ground-truth grasp rectangle for that image. This is a strictly "
        "geometric test on already-frozen numbers -- it involves no judgment about "
        "whether any model's stated reasoning was plausible, which spec section 8 "
        "rules out as self-authored ground truth."
    )
    lines.append("")
    if n_no_gt:
        lines.append(f"**Note:** {n_no_gt} test image(s) had no ground-truth rectangles "
                      "and were excluded from hull scoring.")
        lines.append("")

    lines.append("## Headline")
    lines.append("")
    lines.append("| System | Predictions scored | Center outside every GT hull | Rate |")
    lines.append("|---|---|---|---|")
    for r in (result_a, result_b, result_c):
        lines.append(
            f"| {r['name']} | {r['scored']} | {r['outside']} | {r['outside_rate']*100:.1f}% |"
        )
    lines.append("")
    lines.append(
        f"System A: {result_a['no_pred']} image(s) had no prediction at all "
        "(excluded from the rate above, reported separately since 'no prediction' "
        "is not a spatial miss)."
    )
    if result_c["no_pred"]:
        lines.append(
            f"System C: {result_c['no_pred']} call(s) were non-`ok` parses (excluded "
            "from the rate above for the same reason)."
        )
    lines.append("")

    lines.append("## Reading")
    lines.append("")
    lines.append(
        "A center outside the convex hull of every labelled grasp is the loosest "
        "possible spatial test a prediction can fail -- looser than the section 6 "
        "IoU>0.25 threshold, since the hull of all grasps is typically larger than "
        "any single grasp rectangle. A high rate here is not merely 'wrong angle' or "
        "'wrong size'; it means the predicted grasp point is not spatially associated "
        "with the object's labelled grasp region at all."
    )
    lines.append("")
    lines.append(
        "This is offered as a purely geometric corroboration of the qualitative "
        "coordinate-binding observation in `system_c_results.md` and the compound-"
        "failure bucket in `comparison_results.md` (365/615 System C calls fail both "
        "angle and IoU criteria simultaneously) -- not a replacement for either, and "
        "not a new scored metric. It answers a different, narrower question: not "
        "'did this pass the grasp-correctness bar' but 'is the predicted center "
        "anywhere near the object's labelled grasp region at all.'"
    )
    lines.append("")

    lines.append("## Per-image detail, System C (worst rates first)")
    lines.append("")
    lines.append("Fraction of each image's parsed repeats whose center fell outside every GT hull.")
    lines.append("")
    lines.append("| pcd_id | repeats scored | outside hull | rate |")
    lines.append("|---|---|---|---|")
    rows = sorted(result_c["per_image_rows"], key=lambda t: (-t[1] / t[2], -t[0]))
    for pcd_id, n_out, n_scored in rows[:20]:
        lines.append(f"| {pcd_id:04d} | {n_scored} | {n_out} | {n_out/n_scored*100:.0f}% |")
    lines.append("")

    OUT_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT_PATH}")
    print()
    for r in (result_a, result_b, result_c):
        print(f"System {r['name']}: {r['outside']}/{r['scored']} outside hull "
              f"({r['outside_rate']*100:.1f}%), no_pred={r['no_pred']}")


if __name__ == "__main__":
    main()
