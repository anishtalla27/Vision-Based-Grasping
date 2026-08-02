"""Checks on the Section 6 comparison, before it is allowed to write anything.

WHY THIS EXISTS
---------------
The comparison's whole claim to being fair is that all three systems go
through one scoring path. That claim has exactly one way of being
silently false: System B's predictions live in a 224x224 crop frame and
have to be pulled back to 640x480 first. Get that inverse slightly wrong
and nothing raises -- System B just scores a bit lower, which reads as a
model result rather than as arithmetic.

So the inverse is pinned twice, independently. Once against the frozen
forward transform in grasp_dataset (round trip, check 2), and once
against the sealed accuracy System B already reported (check 1). Either
alone could be satisfied by a wrong-but-consistent transform; both at
once is much harder to fake, because check 2 never looks at an accuracy
and check 1 never looks at the transform.

The statistics are checked against hand-computed answers rather than
against another library, and the taxonomy is checked against the one
ordering trap that is known to exist in is_correct's return signature.

Usage:
    python scripts/verify_comparison.py
"""

import subprocess

import numpy as np

from cornell_data import load_rects, load_split, split_ids
from grasp_dataset import CROP_X0, CROP_Y0, SCALE, crop_matrix, transform_rect
from grasp_metric import ANGLE_TOL_DEG, IOU_MIN, is_correct, rect_iou
from system_all_compare import (SEALED, load_a, load_b, load_c, mcnemar,
                                reproduction_check, score, score_everything,
                                test_ids, wilson)

FROZEN_AT = "026032d"        # the commit that froze cornell_data + grasp_metric

FAILURES = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  ' + detail if detail else ''}")
    if not ok:
        FAILURES.append(name)


# --------------------------------------------- 1. the sealed numbers come back


def test_reproduction(ids, correct):
    """Re-scoring all three systems must land exactly on the sealed counts.

    This is the check that says the shared scoring path measures the same
    thing the three sealed runs measured. It is deliberately an equality,
    not a tolerance: an off-by-one would mean one image changed verdict,
    and there is no benign reason for that to happen.
    """
    print("\n1. Sealed counts reproduced through the shared scoring path")
    got, bad = reproduction_check(ids, correct)
    for sysname, (k, n) in SEALED.items():
        check(f"system {sysname} re-scores to its sealed {k}/{n}",
              got[sysname] == k, f"got {got[sysname]}")
    check("no system disagrees with its sealed run", not bad,
          "; ".join(bad) if bad else "")


# --------------------------------------------- 2. the crop inverse, on its own


def test_crop_roundtrip():
    """640 -> 224 -> 640 must return the original rectangle exactly.

    The forward direction is grasp_dataset's own frozen crop_matrix, the
    one System B actually trained and evaluated through. The backward
    direction is the arithmetic system_all_compare.load_b uses. Neither
    number here is an accuracy, so this check cannot be satisfied by a
    transform that merely happens to produce a nice-looking score.
    """
    print("\n2. System B's crop inverse, checked against the frozen forward transform")
    m = crop_matrix()
    rects = []
    for pcd in split_ids("test")[:60]:
        rects.extend(load_rects(pcd))
    check("test rectangles available", len(rects) > 200, f"n={len(rects)}")

    worst_param, worst_iou = 0.0, 1.0
    for r in rects:
        fwd = transform_rect(r, m)
        back = (fwd[0] / SCALE + CROP_X0, fwd[1] / SCALE + CROP_Y0,
                fwd[2], fwd[3] / SCALE, fwd[4] / SCALE)
        worst_param = max(worst_param, max(abs(x - y) for x, y in zip(r, back)))
        worst_iou = min(worst_iou, rect_iou(r, back))
    check("all five parameters survive the round trip", worst_param < 1e-6,
          f"worst error {worst_param:.2e}")
    check("round-tripped rectangle is its own IoU 1.0", worst_iou > 0.9999,
          f"worst IoU {worst_iou:.6f}")

    # The constants are imported, never retyped. Assert they are what the
    # docstring in grasp_dataset says, so a future edit there is loud here.
    check("crop constants unchanged", (SCALE, CROP_X0, CROP_Y0) == (0.56, 120.0, 40.0),
          f"SCALE={SCALE} X0={CROP_X0} Y0={CROP_Y0}")


# --------------------------------------------- 3. the taxonomy ordering trap


def test_taxonomy_ordering(ids, gts, correct, bucket):
    """`correct` must be tested before the criterion buckets, on real data.

    is_correct returns `correct` over ALL ground truths but returns
    best_iou/best_angle for the highest-OVERLAP one, which is not always
    the one that matched. Bucketing on those columns first would file a
    real success as a failure. This asserts the hazard is real (there are
    such images in the test set) and that the code survives it.
    """
    print("\n3. Failure taxonomy: the is_correct ordering trap")
    trap = 0
    for p in ids:
        for pred in [load_a().get(p), load_b().get(p)]:
            if pred is None:
                continue
            ok, _, iou, ang = is_correct(pred, gts[p])
            if ok and not (ang <= ANGLE_TOL_DEG and iou > IOU_MIN):
                trap += 1
    check("the hazard is real: correct predictions whose max-IoU truth fails",
          trap > 0, f"n={trap}")

    for sysname in ("A", "B"):
        n_correct = sum(1 for p in ids if bucket[sysname][p] == "correct")
        check(f"system {sysname} taxonomy 'correct' equals its accuracy count",
              n_correct == sum(correct[sysname][p] for p in ids),
              f"{n_correct}")
    n_c = sum(1 for p in ids for r in range(5) if bucket["C"][p][r] == "correct")
    check("system C taxonomy 'correct' equals its accuracy count",
          n_c == sum(correct["C"][p][r] for p in ids for r in range(5)), f"{n_c}")

    total_a = len([p for p in ids])
    check("system A buckets account for every image",
          sum(1 for p in ids if bucket["A"][p] in
              ("correct", "angle_only", "iou_only", "both", "no_prediction")) == total_a)

    # A prediction that cannot exist scores as a failure, never as absent.
    ok, b = score(None, gts[ids[0]])
    check("a missing prediction is a failure, not a skipped row",
          ok is False and b == "no_prediction")


# --------------------------------------------- 4. statistics on known answers


def test_statistics():
    """Wilson and McNemar against hand-computed values, not against a library."""
    print("\n4. Statistics, against hand-computed answers")
    lo, hi = wilson(5, 10)
    check("wilson 5/10 is [23.66, 76.34]", abs(lo - 23.66) < 0.01 and abs(hi - 76.34) < 0.01,
          f"[{lo:.2f}, {hi:.2f}]")
    lo, hi = wilson(0, 10)
    check("wilson 0/10 is [0.00, 27.75]", abs(lo) < 0.01 and abs(hi - 27.75) < 0.01,
          f"[{lo:.2f}, {hi:.2f}]")
    lo, hi = wilson(10, 10)
    check("wilson 10/10 upper bound is exactly 100", abs(hi - 100.0) < 1e-9,
          f"[{lo:.2f}, {hi:.2f}]")

    b, c, p = mcnemar([1] * 10 + [0] * 10, [0] * 10 + [1] * 10)
    check("mcnemar 10 vs 10 discordant is p=1.0", b == 10 and c == 10 and abs(p - 1.0) < 1e-9,
          f"b={b} c={c} p={p:.4f}")
    b, c, p = mcnemar([0] * 10, [1] * 10)
    check("mcnemar 0 vs 10 discordant is p=2/1024",
          b == 0 and c == 10 and abs(p - 2.0 / 1024) < 1e-12, f"p={p:.6g}")
    b, c, p = mcnemar([1] + [0] * 9, [0] + [1] * 9)
    check("mcnemar 1 vs 9 discordant is p=22/1024",
          b == 1 and c == 9 and abs(p - 22.0 / 1024) < 1e-12, f"p={p:.6g}")
    b, c, p = mcnemar([1, 1, 0], [1, 1, 0])
    check("mcnemar with no disagreement is p=1.0", b == 0 and c == 0 and p == 1.0)


# --------------------------------------------- 5. split hygiene


def test_split_hygiene(ids):
    """Nothing outside the test split may be scored, in any of the three loaders."""
    print("\n5. Split hygiene")
    rows = load_split()
    split = {p: s for p, (_, s) in rows.items()}
    check("123 test images", len(ids) == 123, f"n={len(ids)}")
    check("every scored id is in the test split",
          all(split.get(p) == "test" for p in ids))
    for name, loader in (("A", load_a), ("B", load_b), ("C", load_c)):
        stray = [p for p in loader() if split.get(p) != "test"]
        check(f"system {name} loads no train or val image", not stray,
              f"{len(stray)} strays" if stray else "")
    n_obj = len({g for _, (g, s) in rows.items() if s == "test"})
    check("35 distinct test objects", n_obj == 35, f"n={n_obj}")


# --------------------------------------------- 6. nothing frozen has moved


def _git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True,
                          text=True).stdout.strip()


def test_frozen_shared_code():
    """The shared modules must be untouched since they were frozen."""
    print("\n6. Frozen shared code")
    for f in ("scripts/cornell_data.py", "scripts/grasp_metric.py"):
        log = _git("log", "--oneline", f"{FROZEN_AT}..HEAD", "--", f)
        check(f"no commits to {f} since {FROZEN_AT}", log == "",
              log.replace("\n", " | ") if log else "")
    dirty = _git("status", "--porcelain", "--",
                 "scripts/cornell_data.py", "scripts/grasp_metric.py",
                 "scripts/grasp_dataset.py")
    check("no uncommitted changes to the shared modules", dirty == "", dirty)

    for v in ("verify_grasp_metric.py", "verify_system_a.py", "verify_system_c.py"):
        r = subprocess.run(["python", f"scripts/{v}"], capture_output=True, text=True)
        tail = (r.stdout + r.stderr).strip().splitlines()
        check(f"{v} still passes", r.returncode == 0,
              "" if r.returncode == 0 else " / ".join(tail[-3:]))


# ---------------------------------------------------------------- runner


def main():
    print("Verifying the Section 6 comparison. No network, no model, no writes.")
    ids, obj = test_ids()
    gts = {p: load_rects(p) for p in ids}
    correct, bucket = score_everything(ids, gts, load_a(), load_b(), load_c())

    test_reproduction(ids, correct)
    test_crop_roundtrip()
    test_taxonomy_ordering(ids, gts, correct, bucket)
    test_statistics()
    test_split_hygiene(ids)
    test_frozen_shared_code()

    print()
    if FAILURES:
        print(f"{len(FAILURES)} CHECK(S) FAILED:")
        for f in FAILURES:
            print(f"  - {f}")
        raise SystemExit(1)
    print("All checks passed. The comparison is safe to generate.")


if __name__ == "__main__":
    main()
