"""Camera-ready statistics that use System A's clean, pre-correction result.

WHY THIS EXISTS
---------------
ICDM reviewer 3 pointed out that the paper's paired comparisons used
System A's 57.7%, which exists only because a rendered test image
prompted amendment 1 (spec 10.6). The clean number is the 40.7% the
frozen table scored before that amendment. This script puts the clean
result on the same object-clustered footing as everything else, so the
camera-ready can make its inferential claims on 40.7% and report 57.7%
as post-hoc only.

INPUT
-----
data/interim/system_a_v1_predictions.csv is the frozen table exactly as
committed in afcd99a, re-run with that commit's own scripts and the
committed system_a_detections.csv. It reproduces 50/123 = 40.7%, the
figure in the afcd99a commit message. The current scripts on the same
data reproduce data/interim/system_a_predictions.csv (71/123) exactly,
so the two files differ only by amendment 1.

WHAT IT REPORTS
---------------
1. Clean System A's failure taxonomy and center-hull rate, scored with
   the same functions as the sealed comparison.
2. System A's orientation ceiling from the labels alone: how many test
   images have any labelled grasp within 15 degrees (reviewer 4's
   question) and within 30 degrees (the metric's tolerance) of 0 or 90.
3. Object-clustered CIs and paired differences with "A_clean" added.

Usage:
    python scripts/object_clustered_stats_clean_a.py
"""

import csv
from collections import Counter, defaultdict

import object_clustered_stats as base
from analysis_center_containment import gt_hull_for_image, point_in_hull
from cornell_data import INTERIM, load_rects
from grasp_metric import ANGLE_TOL_DEG, angle_diff
from system_all_compare import score

V1_CSV = INTERIM / "system_a_v1_predictions.csv"
V2_CSV = INTERIM / "system_b_v2_per_image.csv"
D_CSV = INTERIM / "system_d_test_per_image.csv"


def load_v1():
    out = {}
    for r in csv.DictReader(open(V1_CSV)):
        rect = None if r["cx"] == "" else tuple(
            float(r[k]) for k in ("cx", "cy", "theta", "opening", "jaw"))
        out[int(r["pcd_id"])] = (rect, int(r["correct"]))
    return out


def near_axis(gts, tol):
    return any(min(angle_diff(g[2], 0.0), angle_diff(g[2], 90.0)) <= tol
               for g in gts)


def main():
    v1 = load_v1()
    ids = sorted(v1)
    gts = {p: load_rects(p, "cpos") for p in ids}

    # 1. taxonomy and center-hull, re-scored from geometry
    buckets, outside, n_pred = Counter(), 0, 0
    for p in ids:
        rect, flag = v1[p]
        ok, bucket = score(rect, gts[p])
        assert int(ok) == flag, f"pcd{p:04d}: re-score disagrees with saved flag"
        buckets[bucket] += 1
        if rect is not None:
            n_pred += 1
            outside += not point_in_hull(rect[:2], gt_hull_for_image(p))
    n = len(ids)
    print(f"Clean System A (frozen table, afcd99a): {buckets['correct']}/{n} "
          f"= {100 * buckets['correct'] / n:.1f}%")
    for k in ("correct", "angle_only", "iou_only", "both", "no_prediction"):
        print(f"  {k:14s} {buckets[k]:3d} ({100 * buckets[k] / n:4.1f})")
    print(f"  center outside labelled-grasp hull: {outside}/{n_pred} "
          f"({100 * outside / n_pred:.1f}%)\n")

    # 2. orientation ceiling from the labels alone
    for tol in (15.0, ANGLE_TOL_DEG):
        k = sum(near_axis(gts[p], tol) for p in ids)
        print(f"Test images with a labelled grasp within {tol:.0f} deg of 0/90: "
              f"{k}/{n} ({100 * k / n:.1f}%)")
    print()

    # 3. object-clustered statistics with the clean result added
    b2 = {}
    for r in csv.DictReader(open(V2_CSV)):
        flags = [int(v) for k, v in r.items() if k.endswith("_correct")]
        b2[r["pcd_id"]] = sum(flags) / len(flags)
    d = {r["pcd_id"]: r for r in csv.DictReader(open(D_CSV))}

    by_object = defaultdict(list)
    with open(base.PER_IMAGE_CSV, newline="") as fh:
        for row in csv.DictReader(fh):
            row["a_clean"] = v1[int(row["pcd_id"])][1]
            row["b_v2"] = b2[row["pcd_id"]]
            row["geometric"] = d[row["pcd_id"]]["geometric"]
            by_object[row["object_id"]].append(row)

    base.SYSTEMS.update({
        "A_clean": lambda r: float(r["a_clean"]),
        "B_v2": lambda r: float(r["b_v2"]),
        "D_geom": lambda r: float(r["geometric"]),
    })
    base.PAIRS[:] = [("B", "A_clean"), ("B_v2", "A_clean"),
                     ("A_clean", "C_best5"), ("A_clean", "C_pooled"),
                     ("D_geom", "A_clean"), ("A", "A_clean")]

    objects = list(by_object)
    reps, reps_balanced, diffs = base.bootstrap(by_object)
    print(f"objects: {len(objects)}  bootstrap {base.N_BOOT}, "
          f"permutation {base.N_PERM}, seed {base.SEED}\n")
    print("Object-clustered 95% CIs (image-level accuracy)")
    for name, sc in base.SYSTEMS.items():
        lo, hi = base.percentile_ci(reps[name])
        print(f"  {name:9s} {base.image_mean(objects, by_object, sc):5.1f}%   [{lo:5.1f}, {hi:5.1f}]")
    print("\nObject-balanced accuracy")
    for name, sc in base.SYSTEMS.items():
        lo, hi = base.percentile_ci(reps_balanced[name])
        print(f"  {name:9s} {base.object_mean(objects, by_object, sc):5.1f}%   [{lo:5.1f}, {hi:5.1f}]")
    print("\nPaired differences (object-clustered bootstrap CI, permutation p)")
    for hi_n, lo_n in base.PAIRS:
        lo_ci, hi_ci = base.percentile_ci(diffs[(hi_n, lo_n)])
        obs, p = base.permutation_test(by_object, hi_n, lo_n)
        tag = "excludes 0" if lo_ci > 0 or hi_ci < 0 else "INCLUDES 0"
        print(f"  {hi_n:9s} - {lo_n:9s} {obs:+6.1f}   [{lo_ci:+6.1f}, {hi_ci:+6.1f}]  {tag}   p = {p:.4g}")


if __name__ == "__main__":
    main()
