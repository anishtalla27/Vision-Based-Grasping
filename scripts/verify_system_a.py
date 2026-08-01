"""Checks on System A's conversion rules, before its numbers are believed.

WHY THIS EXISTS
---------------
The orientation rule is the one piece of System A that can be exactly
backwards while everything still runs, every file still writes, and the
only symptom is a disappointing accuracy that looks like an honest
result. A baseline that is quietly broken is worse than no baseline,
because Systems B and C would then be compared against a floor that is
wrong for a reason nobody investigated.

So the rule is checked two ways: synthetically (a wide box must grasp
across its height), and empirically against TRAIN ground truth, by
asking whether the rule beats its own inverse. If the inverse fit the
real labels better, the rule is backwards, and this script says so
instead of letting it through.

Train data only. Test and val are never opened.

Usage:
    python scripts/verify_system_a.py     (after calibrate + freeze)
"""

import numpy as np

from cornell_data import load_rects, load_split
from grasp_metric import angle_diff
from system_a_calibrate import load_detections
from system_a_lookup import (END_OFFSET_FRAC, JAW_PX, MAX_OPEN_PX,
                             MIN_OPEN_PX, OPENING_FRAC, lookup, predict_rect)

FAILURES = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  ' + detail if detail else ''}")
    if not ok:
        FAILURES.append(name)


def test_constants():
    print("\nFrozen constants are set")
    for name, v in (("OPENING_FRAC", OPENING_FRAC), ("JAW_PX", JAW_PX),
                    ("END_OFFSET_FRAC", END_OFFSET_FRAC)):
        check(f"{name} is calibrated", v is not None and np.isfinite(v), f"= {v}")
    check("END_OFFSET_FRAC is off-centre",
          END_OFFSET_FRAC is not None and END_OFFSET_FRAC < 0.45,
          "otherwise END/UPPER would collapse into CENTER")


def test_orientation_synthetic():
    print("\nOrientation rule, synthetic")
    wide = predict_rect((100, 200, 300, 260), "CENTER")     # 200 x 60
    tall = predict_rect((200, 100, 260, 300), "CENTER")     # 60 x 200
    check("wide box -> theta 90 (jaws close vertically)", wide[2] == 90.0,
          f"got {wide[2]}")
    check("tall box -> theta 0 (jaws close horizontally)", tall[2] == 0.0,
          f"got {tall[2]}")
    check("opening clamped into physical range",
          MIN_OPEN_PX <= wide[3] <= MAX_OPEN_PX and MIN_OPEN_PX <= tall[3] <= MAX_OPEN_PX)
    check("centre of a CENTER grasp is the box centre",
          (wide[0], wide[1]) == (200.0, 230.0), f"got {wide[:2]}")

    # An END grasp with no mask must fall back to CENTER rather than
    # picking an end at random.
    end_nomask = predict_rect((100, 200, 300, 260), "END", None)
    check("END with no mask falls back to the centre",
          (end_nomask[0], end_nomask[1]) == (200.0, 230.0))

    upper = predict_rect((200, 100, 260, 300), "UPPER")
    check("UPPER sits above the box centre", upper[1] < 200.0, f"cy={upper[1]:.1f}")


def test_orientation_vs_train_labels():
    """The rule must fit real labels better than its own inverse does."""
    print("\nOrientation rule vs TRAIN ground truth")
    split = load_split()
    train = {p for p, (_, s) in split.items() if s == "train"}
    dets = load_detections()

    ours, inverted, n = [], [], 0
    for pcd in sorted(train):
        if pcd not in dets:
            continue
        category, _, bbox = dets[pcd]
        region, _f = lookup(category)
        rect = predict_rect(bbox, region)
        gts = load_rects(pcd)
        if not gts:
            continue
        n += 1
        # Best (smallest) angle error against any labelled grasp, for the
        # rule as written and for the rule rotated 90 degrees.
        ours.append(min(angle_diff(rect[2], g[2]) for g in gts))
        inverted.append(min(angle_diff(rect[2] + 90, g[2]) for g in gts))

    m_ours, m_inv = float(np.mean(ours)), float(np.mean(inverted))
    within_ours = float(np.mean(np.array(ours) <= 30)) * 100
    within_inv = float(np.mean(np.array(inverted) <= 30)) * 100
    check("rule beats its own inverse on train labels", m_ours < m_inv,
          f"mean err {m_ours:.1f} deg vs inverted {m_inv:.1f} deg, n={n}")
    print(f"        within 30 deg: rule {within_ours:.0f}%, inverted {within_inv:.0f}%")


def main():
    print("Verifying System A's fixed rules (train data only)")
    test_constants()
    test_orientation_synthetic()
    test_orientation_vs_train_labels()

    print()
    if FAILURES:
        raise SystemExit(f"{len(FAILURES)} CHECK(S) FAILED: {', '.join(FAILURES)}")
    print("All checks passed.")


if __name__ == "__main__":
    main()
