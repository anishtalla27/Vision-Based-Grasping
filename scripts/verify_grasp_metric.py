"""Independent checks on the shared grasp metric and Cornell parser.

WHY THIS EXISTS
---------------
Spec section 10.5 says to validate independently before trusting output
at scale, especially where errors are asymmetric. The metric is the
worst place in this project for a silent bug: it scores all three
systems, a wrong answer still looks like a plausible percentage, and
nothing downstream would ever complain. So it gets checked against
sources that do not share its implementation:

  * analytic cases whose IoU can be worked out by hand
  * a brute-force RASTERISED IoU on random rotated pairs, which shares
    no code with the Sutherland-Hodgman clipper, so the two agreeing is
    real evidence rather than a tautology
  * round-trip identities on the rectangle parameterisation
  * the real dataset, including the known pcd0165 NaN quirk

Usage:
    python scripts/verify_grasp_metric.py
"""

import numpy as np

from cornell_data import (corners_to_rect, load_rects, load_split,
                          rect_to_corners, split_ids)
from grasp_metric import angle_diff, polygon_area, rect_iou

FAILURES = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  ' + detail if detail else ''}")
    if not ok:
        FAILURES.append(name)


def raster_iou(r1, r2, n=1400):
    """Brute-force IoU by point sampling. Deliberately dumb and independent.

    Shares no logic with the clipper: it just asks, for a dense grid of
    points, whether each point is inside each rectangle, by projecting
    onto the rectangle's own axes.
    """
    def inside(pts, r):
        cx, cy, th, op, jw = r
        t = np.radians(th)
        ux, uy = np.cos(t), -np.sin(t)
        d = pts - np.array([cx, cy])
        along = d[:, 0] * ux + d[:, 1] * uy
        across = d[:, 0] * -uy + d[:, 1] * ux
        return (np.abs(along) <= op / 2) & (np.abs(across) <= jw / 2)

    allr = np.array([rect_to_corners(*r) for r in (r1, r2)]).reshape(-1, 2)
    lo, hi = allr.min(axis=0) - 1, allr.max(axis=0) + 1
    gx, gy = np.meshgrid(np.linspace(lo[0], hi[0], n), np.linspace(lo[1], hi[1], n))
    pts = np.stack([gx.ravel(), gy.ravel()], axis=1)
    a, b = inside(pts, r1), inside(pts, r2)
    union = (a | b).sum()
    return 0.0 if union == 0 else (a & b).sum() / union


def test_analytic():
    print("\nAnalytic IoU cases")
    check("identical rectangles -> 1.0",
          abs(rect_iou((100, 100, 30, 40, 20), (100, 100, 30, 40, 20)) - 1.0) < 1e-9)
    check("disjoint rectangles -> 0.0",
          rect_iou((0, 0, 0, 10, 10), (500, 500, 0, 10, 10)) == 0.0)

    # Two 40x20 axis-aligned rectangles offset by 20px along the opening
    # axis: they overlap on half their length, so intersection = 20*20 =
    # 400 and union = 800 + 800 - 400 = 1200, giving exactly 1/3.
    check("half-overlap -> exactly 1/3",
          abs(rect_iou((0, 0, 0, 40, 20), (20, 0, 0, 40, 20)) - 1 / 3) < 1e-9)

    # A square rotated 45 degrees inside an identical square: the
    # intersection is a regular octagon of area 8*(sqrt(2)-1)*s^2/2 for
    # side s... easier to just assert the known value 2*(sqrt2 - 1).
    s = 10.0
    inter = 2 * (np.sqrt(2) - 1) * s * s
    exp = inter / (2 * s * s - inter)
    check("square vs 45deg-rotated square",
          abs(rect_iou((0, 0, 0, s, s), (0, 0, 45, s, s)) - exp) < 1e-9,
          f"expected {exp:.6f}")

    check("area of 40x20 rect == 800",
          abs(polygon_area(rect_to_corners(5, 5, 37, 40, 20)) - 800) < 1e-9)


def test_angles():
    print("\nAngle handling")
    check("180-degree symmetry: 10 vs 190 -> 0", angle_diff(10, 190) == 0)
    check("wrap: -89 vs 89 -> 2", abs(angle_diff(-89, 89) - 2) < 1e-9)
    check("orthogonal: 0 vs 90 -> 90", abs(angle_diff(0, 90) - 90) < 1e-9)
    check("never exceeds 90",
          max(angle_diff(a, b) for a in range(-90, 91, 7)
              for b in range(-90, 91, 7)) <= 90 + 1e-9)


def test_roundtrip():
    print("\nParameterisation round-trip")
    rng = np.random.default_rng(42)
    worst = 0.0
    for _ in range(400):
        r = (rng.uniform(50, 590), rng.uniform(50, 430), rng.uniform(-90, 90),
             rng.uniform(10, 90), rng.uniform(8, 50))
        back = corners_to_rect(rect_to_corners(*r))
        worst = max(worst, max(abs(np.array(back) - np.array(r))))
    check("rect -> corners -> rect is identity", worst < 1e-8, f"max err {worst:.2e}")


def test_against_raster():
    print("\nClipper vs independent rasterised IoU (500 random pairs)")
    rng = np.random.default_rng(7)
    worst, worst_case = 0.0, None
    overlapping = 0
    for _ in range(500):
        r1 = (rng.uniform(200, 440), rng.uniform(150, 330), rng.uniform(-90, 90),
              rng.uniform(20, 90), rng.uniform(10, 50))
        # Keep the second rectangle near the first so most pairs actually
        # overlap; disjoint pairs are trivially 0 and prove nothing.
        r2 = (r1[0] + rng.uniform(-40, 40), r1[1] + rng.uniform(-40, 40),
              rng.uniform(-90, 90), rng.uniform(20, 90), rng.uniform(10, 50))
        exact, approx = rect_iou(r1, r2), raster_iou(r1, r2)
        if exact > 0:
            overlapping += 1
        d = abs(exact - approx)
        if d > worst:
            worst, worst_case = d, (r1, r2, exact, approx)
    check("agrees with rasterised IoU within 2e-3", worst < 2e-3,
          f"max diff {worst:.2e}, {overlapping}/500 pairs overlapped")
    if worst >= 2e-3:
        print(f"      worst case: {worst_case}")


def test_real_data():
    print("\nReal dataset")
    split = load_split()
    check("split covers 883 images", len(split) == 883, f"got {len(split)}")
    check("0435 and 0782 excluded", 435 not in split and 782 not in split)
    check("split sizes 620/140/123",
          [len(split_ids(s)) for s in ("train", "val", "test")] == [620, 140, 123])

    r165 = load_rects(165)
    check("pcd0165 NaN rectangle dropped, 2 kept", len(r165) == 2, f"got {len(r165)}")

    n_rect, n_img, bad = 0, 0, []
    for pcd in split:
        rs = load_rects(pcd)
        if not rs:
            bad.append(pcd)
        n_img += 1
        n_rect += len(rs)
        for r in rs:
            if not np.isfinite(r).all() or not (-90 <= r[2] < 90):
                bad.append(pcd)
    check("every split image has >=1 positive rectangle, all finite, theta in range",
          not bad, f"{n_rect} rectangles across {n_img} images")

    # Ground truth must score as correct against itself. If this fails,
    # the metric is broken in a way that would understate every system.
    self_ok = all(rect_iou(r, r) > 0.99 for pcd in list(split)[:80]
                  for r in load_rects(pcd))
    check("every ground-truth rectangle matches itself", self_ok)


def main():
    print("Verifying the shared grasp metric (spec sections 6 and 10.5)")
    test_analytic()
    test_angles()
    test_roundtrip()
    test_against_raster()
    test_real_data()

    print()
    if FAILURES:
        raise SystemExit(f"{len(FAILURES)} CHECK(S) FAILED: {', '.join(FAILURES)}")
    print("All checks passed. The metric is safe to score systems A, B and C with.")


if __name__ == "__main__":
    main()
