"""Object-clustered statistics including System B round 2.

Re-uses every function in object_clustered_stats.py unchanged and adds
one system, "B_v2": the round-2 multi-seed System B, scored per image as
the FRACTION of seeds whose final-EMA prediction passed (the same
pooling rule System C's five repeats use). The sealed round-1 columns
are read from comparison_per_image.csv exactly as before, and the new
column is joined on pcd_id from system_b_v2_per_image.csv.

Usage:
    python scripts/object_clustered_stats_v2.py
"""

import csv
from collections import defaultdict

import object_clustered_stats as base
from cornell_data import INTERIM

V2_CSV = INTERIM / "system_b_v2_per_image.csv"


def main():
    v2 = {}
    with open(V2_CSV, newline="") as fh:
        for row in csv.DictReader(fh):
            flags = [int(v) for k, v in row.items() if k.endswith("_correct")]
            v2[row["pcd_id"]] = sum(flags) / len(flags)

    by_object = defaultdict(list)
    with open(base.PER_IMAGE_CSV, newline="") as fh:
        for row in csv.DictReader(fh):
            row["b_v2"] = v2[row["pcd_id"]]
            by_object[row["object_id"]].append(row)

    base.SYSTEMS["B_v2"] = lambda r: float(r["b_v2"])
    base.PAIRS[:] = [("B_v2", "A"), ("B_v2", "B"), ("B_v2", "C_pooled")]

    objects = list(by_object)
    reps, reps_balanced, diffs = base.bootstrap(by_object)
    print(f"objects: {len(objects)}  bootstrap {base.N_BOOT}, permutation {base.N_PERM}, seed {base.SEED}\n")
    print("Object-clustered 95% CIs (image-level accuracy)")
    for name, score in base.SYSTEMS.items():
        lo, hi = base.percentile_ci(reps[name])
        print(f"  {name:9s} {base.image_mean(objects, by_object, score):5.1f}%   [{lo:5.1f}, {hi:5.1f}]")
    print("\nObject-balanced accuracy")
    for name, score in base.SYSTEMS.items():
        lo, hi = base.percentile_ci(reps_balanced[name])
        print(f"  {name:9s} {base.object_mean(objects, by_object, score):5.1f}%   [{lo:5.1f}, {hi:5.1f}]")
    print("\nPaired differences (object-clustered bootstrap CI, permutation p)")
    for hi_n, lo_n in base.PAIRS:
        lo_ci, hi_ci = base.percentile_ci(diffs[(hi_n, lo_n)])
        obs, p = base.permutation_test(by_object, hi_n, lo_n)
        tag = "excludes 0" if lo_ci > 0 or hi_ci < 0 else "INCLUDES 0"
        print(f"  {hi_n:9s} - {lo_n:9s} {obs:+6.1f}   [{lo_ci:+6.1f}, {hi_ci:+6.1f}]  {tag}   p = {p:.4g}")


if __name__ == "__main__":
    main()
