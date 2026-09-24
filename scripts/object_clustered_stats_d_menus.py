"""Object-clustered statistics for the System D sparse-menu follow-up.

Reads the three System D per-image files (full menu, sparse menu, equal-
size menu) and reports, on the same 35 test objects:

  each menu's one-call accuracy against its own random floor, and
  sparse versus equal (same candidates, same geometry, only the drawn
  mark size differs), which is the salience test.

Usage:
    python scripts/object_clustered_stats_d_menus.py
"""

import csv
from collections import defaultdict

import object_clustered_stats as base
from cornell_data import INTERIM

FILES = {"full": "system_d_test_per_image.csv",
         "sparse": "system_d_test_sparse_per_image.csv",
         "equal": "system_d_test_equal_per_image.csv"}


def main():
    per = {m: {r["pcd_id"]: r for r in csv.DictReader(open(INTERIM / f))}
           for m, f in FILES.items()}
    by_object = defaultdict(list)
    with open(base.PER_IMAGE_CSV, newline="") as fh:
        for row in csv.DictReader(fh):
            for m in FILES:
                x = per[m][row["pcd_id"]]
                row[f"{m}_d"] = int(x["d_repeats_correct"]) / 5.0
                row[f"{m}_rand"] = float(x["random"])
                row[f"{m}_oracle"] = float(x["oracle"])
            by_object[row["object_id"]].append(row)

    base.SYSTEMS.clear()
    for m in FILES:
        base.SYSTEMS[f"{m}_D"] = (lambda k: (lambda r: float(r[k])))(f"{m}_d")
        base.SYSTEMS[f"{m}_rand"] = (lambda k: (lambda r: float(r[k])))(f"{m}_rand")
        base.SYSTEMS[f"{m}_orac"] = (lambda k: (lambda r: float(r[k])))(f"{m}_oracle")
    base.PAIRS[:] = [("full_D", "full_rand"), ("sparse_D", "sparse_rand"),
                     ("equal_D", "equal_rand"), ("sparse_D", "equal_D"),
                     ("sparse_D", "full_D")]

    objects = list(by_object)
    reps, _, diffs = base.bootstrap(by_object)
    print(f"objects: {len(objects)}  bootstrap {base.N_BOOT}, permutation {base.N_PERM}, seed {base.SEED}\n")
    print("Object-clustered 95% CIs (image-level accuracy)")
    for name, score in base.SYSTEMS.items():
        lo, hi = base.percentile_ci(reps[name])
        print(f"  {name:12s} {base.image_mean(objects, by_object, score):5.1f}%   [{lo:5.1f}, {hi:5.1f}]")
    print("\nPaired differences (object-clustered bootstrap CI, permutation p)")
    for hi_n, lo_n in base.PAIRS:
        lo_ci, hi_ci = base.percentile_ci(diffs[(hi_n, lo_n)])
        obs, p = base.permutation_test(by_object, hi_n, lo_n)
        tag = "excludes 0" if lo_ci > 0 or hi_ci < 0 else "INCLUDES 0"
        print(f"  {hi_n:10s} - {lo_n:11s} {obs:+6.1f}   [{lo_ci:+6.1f}, {hi_ci:+6.1f}]  {tag}   p = {p:.4g}")


if __name__ == "__main__":
    main()
