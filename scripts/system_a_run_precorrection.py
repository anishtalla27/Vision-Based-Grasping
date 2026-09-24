"""Reproduce System A's pre-correction (40.7%) run, per image.

WHY THIS EXISTS
---------------
Commit afcd99a evaluated the frozen lookup table once, before amendment
1 (the background-clutter guard), and printed 50/123 = 40.7%. Only the
headline was recorded; the per-image predictions from that run were
never committed, so the object-clustered statistics were only ever
computed for the corrected 57.7% configuration. An ICDM reviewer asked
that the paired comparisons be based on the clean pre-correction number,
because 57.7% was reached after test output had been inspected.

This script re-creates that run exactly:

  * the same cached detections (data/interim/system_a_detections.csv,
    produced by system_a_detect.py and unchanged since),
  * the same frozen table and the same JAW_PX / END_OFFSET_FRAC,
  * OPENING_FRAC = 0.537, the value frozen in 853de49 and used in
    afcd99a (it moved to 0.696 only when the guard changed which train
    boxes fed calibration),
  * no detection_on_object guard: every detection is trusted, as in
    afcd99a.

Everything else (segmentation fallback, rectangle rule, metric) is the
current code, which is unchanged in those parts since afcd99a. The
script asserts that it lands on exactly 50 correct, so a silent drift in
any of the shared modules would fail loudly rather than quietly produce
a different "pre-correction" number.

USAGE
-----
    python scripts/system_a_run_precorrection.py

Outputs:
    data/interim/system_a_predictions_precorrection.csv
    data/interim/comparison_per_image.csv   gains an a_pre_correct column
"""

import csv

from cornell_data import INTERIM, find_images, load_rects, load_split
from grasp_metric import is_correct
from system_a_calibrate import load_detections
import system_a_lookup
import system_a_run

PRE_OPENING_FRAC = 0.537      # frozen in 853de49, used by afcd99a
EXPECTED_CORRECT = 50         # 50/123 = 40.7% per the afcd99a commit message

PRED_CSV = INTERIM / "system_a_predictions_precorrection.csv"
COMPARISON_CSV = INTERIM / "comparison_per_image.csv"


def main():
    # Put the two amended pieces back the way afcd99a had them.
    system_a_lookup.OPENING_FRAC = PRE_OPENING_FRAC
    system_a_run.detection_on_object = lambda bbox, mask: True

    split = load_split()
    test = sorted(p for p, (_, s) in split.items() if s == "test")
    paths = find_images()
    dets = {k: v for k, v in load_detections().items() if k in set(test)}

    preds = system_a_run.predict_all(test, paths, dets)

    rows, n_ok, n_det = [], 0, 0
    correct_by_id = {}
    for pcd in test:
        rect, category, score, region, force, source = preds[pcd]
        n_det += source == "detector"
        if rect is None:
            ok = False
            rows.append([f"{pcd:04d}", "", "", "", "", "", "", "", "none", "0"])
        else:
            ok = bool(is_correct(rect, load_rects(pcd))[0])
            rows.append([f"{pcd:04d}", f"{rect[0]:.1f}", f"{rect[1]:.1f}",
                         f"{rect[2]:.1f}", f"{rect[3]:.1f}", f"{rect[4]:.1f}",
                         region, force, source, "1" if ok else "0"])
        n_ok += ok
        correct_by_id[f"{pcd:04d}"] = "1" if ok else "0"

    n = len(test)
    print(f"pre-correction System A: {n_ok}/{n} = {100 * n_ok / n:.1f}%  "
          f"(detector boxes trusted: {n_det})")
    if n_ok != EXPECTED_CORRECT:
        raise SystemExit(f"Expected {EXPECTED_CORRECT} correct as in afcd99a, got {n_ok}. "
                         "A shared module has drifted; do not use this output.")

    with open(PRED_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pcd_id", "cx", "cy", "theta", "opening", "jaw",
                    "region", "force", "source", "correct"])
        w.writerows(rows)
    print(f"Wrote {PRED_CSV}")

    # Add the clean column beside the corrected one in the sealed
    # comparison sheet, so the clustered stats can read both.
    with open(COMPARISON_CSV, newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames)
        comp = list(reader)
    if "a_pre_correct" not in fields:
        fields.insert(fields.index("a_correct"), "a_pre_correct")
    for row in comp:
        row["a_pre_correct"] = correct_by_id[row["pcd_id"]]
    with open(COMPARISON_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(comp)
    print(f"Added a_pre_correct to {COMPARISON_CSV}")


if __name__ == "__main__":
    main()
