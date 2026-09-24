"""How much of System A's gap is fixed by its two-orientation design?

WHY THIS EXISTS
---------------
System A can only emit 0 or 90 degrees, because COCO boxes are
axis-aligned. An ICDM reviewer asked what fraction of the test images
even have a labeled grasp near one of those two angles, so that the
reader can tell how much of the heuristic's score is capped by design
before any placement rule runs.

WHAT IT COMPUTES
----------------
For every test image, the smallest angular distance from any positive
labeled grasp to the nearest of 0 or 90 degrees (theta is folded into
[-90, 90) by cornell_data, and a parallel-jaw grasp is symmetric under
180 degrees, so the distance to 90 and to -90 are the same). Then:

  within 30 deg   the metric's own angle tolerance, so this is System A's
                  hard ceiling: an image outside it cannot pass at any
                  placement.
  within 15 deg   a stricter reading, as the reviewer phrased it.

Reads only labels on the sealed test split. No prediction is made.

USAGE
-----
    python scripts/analysis_orientation_ceiling.py

Output:
    data/interim/orientation_ceiling.md
"""

from pathlib import Path

from cornell_data import INTERIM, load_rects, load_split

OUT_MD = INTERIM / "orientation_ceiling.md"
TOLERANCES = (15.0, 30.0)


def axis_distance(theta):
    """Angular distance from theta (degrees, folded to [-90, 90)) to 0 or 90."""
    t = abs(theta) % 180.0
    return min(t, abs(90.0 - t), 180.0 - t)


def main():
    split = load_split()
    for name in ("test", "val", "train"):
        ids = sorted(p for p, (_, s) in split.items() if s == name)
        best = {}
        for pcd in ids:
            rects = load_rects(pcd)
            best[pcd] = min(axis_distance(r[2]) for r in rects) if rects else float("inf")
        counts = {tol: sum(1 for d in best.values() if d <= tol) for tol in TOLERANCES}
        line = ", ".join(f"within {tol:g} deg: {counts[tol]}/{len(ids)} "
                         f"({100 * counts[tol] / len(ids):.1f}%)" for tol in TOLERANCES)
        print(f"{name:5s} {line}")
        if name == "test":
            test_ids, test_best, test_counts = ids, best, counts

    n = len(test_ids)
    L = ["# Orientation ceiling for System A\n",
         "System A can only output 0 or 90 degrees. For each test image this "
         "takes the labeled positive grasp whose angle is closest to one of those "
         "two orientations and reports how many images fall within each tolerance. "
         "The 30 degree row is the metric's own angle tolerance, so it is the hard "
         "ceiling: an image outside it cannot pass however well the rectangle is "
         "placed. Labels only, no predictions.\n",
         "| Tolerance | Test images with a label within it | Share |",
         "|---|---|---|"]
    for tol in TOLERANCES:
        L.append(f"| {tol:g} deg | {test_counts[tol]}/{n} | {100 * test_counts[tol] / n:.1f}% |")
    unreachable = [p for p, d in test_best.items() if d > 30.0]
    L.append(f"\nImages System A cannot pass at any placement ({len(unreachable)}): "
             + ", ".join(f"pcd{p:04d}" for p in unreachable) + "\n")
    L.append("| Image | Nearest label angle to 0/90 (deg) |")
    L.append("|---|---|")
    for p in unreachable:
        L.append(f"| pcd{p:04d} | {test_best[p]:.1f} |")
    OUT_MD.write_text("\n".join(L) + "\n")
    print(f"\nWrote {OUT_MD}")


if __name__ == "__main__":
    main()
