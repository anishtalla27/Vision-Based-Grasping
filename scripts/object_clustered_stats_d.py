"""Object-clustered statistics for System D (Set-of-Mark selection).

Re-uses object_clustered_stats.py unchanged and adds, per test image:

  D_pooled   fraction of the five repeats whose chosen candidate passed
             (one-call expected accuracy, same rule as C_pooled)
  D_best5    1 if any repeat's choice passed
  D_random   expected accuracy of a uniformly random choice among the
             same candidates (the floor System D must beat)
  D_oracle   1 if any candidate passes (the ceiling)
  D_geom     the deterministic geometric rule, candidate 0

The pairs tested are the ones that answer the paper's open question:
does choosing among marks beat emitting coordinates (D - C), and does
the model's choice beat a random choice among the same marks
(D - D_random)? Both are paired within object and resampled by object.

Usage:
    python scripts/object_clustered_stats_d.py
"""

import csv
from collections import defaultdict

import object_clustered_stats as base
from cornell_data import INTERIM

D_CSV = INTERIM / "system_d_test_per_image.csv"


def main():
    d = {r["pcd_id"]: r for r in csv.DictReader(open(D_CSV))}
    by_object = defaultdict(list)
    with open(base.PER_IMAGE_CSV, newline="") as fh:
        for row in csv.DictReader(fh):
            row.update(d[row["pcd_id"]])
            by_object[row["object_id"]].append(row)

    base.SYSTEMS.update({
        "D_pooled": lambda r: int(r["d_repeats_correct"]) / 5.0,
        "D_best5": lambda r: 1.0 if int(r["d_repeats_correct"]) >= 1 else 0.0,
        "D_random": lambda r: float(r["random"]),
        "D_oracle": lambda r: float(r["oracle"]),
        "D_geom": lambda r: float(r["geometric"]),
    })
    base.PAIRS[:] = [("D_pooled", "C_pooled"), ("D_pooled", "D_random"),
                     ("D_geom", "A"), ("D_geom", "D_pooled"), ("B", "D_geom")]

    objects = list(by_object)
    reps, reps_balanced, diffs = base.bootstrap(by_object)
    print(f"objects: {len(objects)}  bootstrap {base.N_BOOT}, permutation {base.N_PERM}, seed {base.SEED}\n")
    print("Object-clustered 95% CIs (image-level accuracy)")
    for name, score in base.SYSTEMS.items():
        lo, hi = base.percentile_ci(reps[name])
        print(f"  {name:9s} {base.image_mean(objects, by_object, score):5.1f}%   [{lo:5.1f}, {hi:5.1f}]")
    print("\nPaired differences (object-clustered bootstrap CI, permutation p)")
    for hi_n, lo_n in base.PAIRS:
        lo_ci, hi_ci = base.percentile_ci(diffs[(hi_n, lo_n)])
        obs, p = base.permutation_test(by_object, hi_n, lo_n)
        tag = "excludes 0" if lo_ci > 0 or hi_ci < 0 else "INCLUDES 0"
        print(f"  {hi_n:9s} - {lo_n:9s} {obs:+6.1f}   [{lo_ci:+6.1f}, {hi_ci:+6.1f}]  {tag}   p = {p:.4g}")


if __name__ == "__main__":
    main()
