"""Object-clustered intervals and between-system tests for the three systems.

WHY THIS EXISTS
---------------
Every interval reported by the per-system scripts treats its unit of
analysis as independent, and none of them are:

  * System C's Wilson interval is computed over 615 calls, but those are
    five repeats of 123 images, not 615 independent trials.
  * The image-level intervals and McNemar tests for Systems A and B have
    the same problem one level up: the 123 test images are grouped
    within 35 objects, and images of the same object are not independent
    (Cornell photographs one object repeatedly from rotated poses).

The population the paper generalises to is *unseen objects*, so the
correct sampling unit is the object, not the image and not the call.
This script rebuilds the intervals on that unit.

WHAT IT COMPUTES
----------------
1. Object-clustered bootstrap CIs: resample the 35 test objects with
   replacement, carrying ALL of an object's images (and, for System C,
   all of its calls) together each time an object is drawn.

2. Paired difference CIs on the same bootstrap replicates. This is the
   comparison that should be reported. Checking whether two separate
   CIs overlap is a conservative, underpowered stand-in for testing the
   difference directly, and it can fail to detect a difference that a
   direct test finds comfortably.

3. An object-clustered permutation test for each pairwise difference.
   Objects (not images) are the exchangeable unit, so the system labels
   are swapped for whole objects at a time.

4. Object-balanced accuracy: each object weighted equally rather than in
   proportion to how many images it contributes. Test object groups
   range from one image to nine, so the image-level mean over-weights
   the objects that happen to be photographed more.

DETERMINISM
-----------
SEED is fixed, so re-running reproduces the reported numbers exactly.
The input CSV is sealed test output; this script only re-reads it.

USAGE
-----
    python scripts/object_clustered_stats.py
"""

import csv
import random
from collections import defaultdict
from pathlib import Path

PER_IMAGE_CSV = Path("data/interim/comparison_per_image.csv")

SEED = 0
N_BOOT = 20000
N_PERM = 20000
ALPHA = 0.05


# --------------------------------------------------------------------
# per-image scoring functions
#
# Each maps one row of comparison_per_image.csv to that image's score in
# [0, 1]. System C gets two readings because the paper reports two:
#   pooled  -- the deployment number, one call per image, so the mean of
#              the five repeats is the expected accuracy of a single call
#   best5   -- the ceiling, correct if ANY of the five repeats passed
# --------------------------------------------------------------------
SYSTEMS = {
    "A": lambda r: float(r["a_correct"]),
    "B": lambda r: float(r["b_correct"]),
    "C_pooled": lambda r: int(r["c_repeats_correct"]) / 5.0,
    "C_best5": lambda r: 1.0 if int(r["c_repeats_correct"]) >= 1 else 0.0,
}

# the comparisons the paper actually makes
PAIRS = [("B", "A"), ("A", "C_best5"), ("A", "C_pooled"), ("B", "C_pooled")]


def load_by_object(path=PER_IMAGE_CSV):
    """Group the sealed per-image results by object id."""
    by_object = defaultdict(list)
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            by_object[row["object_id"]].append(row)
    return by_object


def image_mean(objects, by_object, score):
    """Image-level accuracy over a list of object ids (repeats allowed)."""
    total = count = 0.0
    for obj in objects:
        for row in by_object[obj]:
            total += score(row)
            count += 1
    return 100.0 * total / count


def object_mean(objects, by_object, score):
    """Object-balanced accuracy: each object contributes equally."""
    per_object = []
    for obj in objects:
        rows = by_object[obj]
        per_object.append(sum(score(r) for r in rows) / len(rows))
    return 100.0 * sum(per_object) / len(per_object)


def percentile_ci(values, alpha=ALPHA):
    ordered = sorted(values)
    lo = ordered[int((alpha / 2) * len(ordered))]
    hi = ordered[int((1 - alpha / 2) * len(ordered))]
    return lo, hi


def bootstrap(by_object, n_boot=N_BOOT, seed=SEED):
    """Resample objects with replacement, carrying all their images."""
    objects = list(by_object)
    rng = random.Random(seed)

    reps = {name: [] for name in SYSTEMS}
    reps_balanced = {name: [] for name in SYSTEMS}
    diffs = {pair: [] for pair in PAIRS}

    for _ in range(n_boot):
        sample = [rng.choice(objects) for _ in objects]
        accs = {}
        for name, score in SYSTEMS.items():
            acc = image_mean(sample, by_object, score)
            accs[name] = acc
            reps[name].append(acc)
            reps_balanced[name].append(object_mean(sample, by_object, score))
        for hi, lo in PAIRS:
            diffs[(hi, lo)].append(accs[hi] - accs[lo])

    return reps, reps_balanced, diffs


def permutation_test(by_object, hi, lo, n_perm=N_PERM, seed=SEED):
    """Object-clustered permutation test on the paired difference.

    Under the null the two systems are exchangeable, so for each OBJECT
    (all of its images together) we either keep or swap the two systems'
    scores. Two-sided p, with the observed statistic included in both
    numerator and denominator so p is never reported as exactly zero.
    """
    rng = random.Random(seed)
    objects = list(by_object)
    score_hi, score_lo = SYSTEMS[hi], SYSTEMS[lo]

    # per-object (sum_hi, sum_lo, n_images)
    per_object = []
    for obj in objects:
        rows = by_object[obj]
        per_object.append(
            (sum(score_hi(r) for r in rows), sum(score_lo(r) for r in rows), len(rows))
        )

    n_images = sum(n for _, _, n in per_object)
    observed = 100.0 * sum(h - l for h, l, _ in per_object) / n_images

    at_least_as_extreme = 0
    for _ in range(n_perm):
        total = 0.0
        for h, l, _ in per_object:
            total += (l - h) if rng.random() < 0.5 else (h - l)
        if abs(100.0 * total / n_images) >= abs(observed) - 1e-12:
            at_least_as_extreme += 1

    return observed, (at_least_as_extreme + 1) / (n_perm + 1)


def main():
    by_object = load_by_object()
    objects = list(by_object)
    n_images = sum(len(v) for v in by_object.values())

    print(f"objects: {len(objects)}   images: {n_images}")
    print(f"bootstrap: {N_BOOT} resamples, permutation: {N_PERM}, seed {SEED}\n")

    reps, reps_balanced, diffs = bootstrap(by_object)

    print("Object-clustered 95% CIs (image-level accuracy)")
    for name, score in SYSTEMS.items():
        point = image_mean(objects, by_object, score)
        lo, hi = percentile_ci(reps[name])
        print(f"  {name:9s} {point:5.1f}%   [{lo:5.1f}, {hi:5.1f}]")

    print("\nObject-balanced accuracy (each object weighted equally)")
    for name, score in SYSTEMS.items():
        point = object_mean(objects, by_object, score)
        lo, hi = percentile_ci(reps_balanced[name])
        print(f"  {name:9s} {point:5.1f}%   [{lo:5.1f}, {hi:5.1f}]")

    print("\nPaired differences (object-clustered bootstrap CI, permutation p)")
    for hi_name, lo_name in PAIRS:
        lo_ci, hi_ci = percentile_ci(diffs[(hi_name, lo_name)])
        observed, p = permutation_test(by_object, hi_name, lo_name)
        excludes = "excludes 0" if lo_ci > 0 or hi_ci < 0 else "INCLUDES 0"
        print(
            f"  {hi_name:9s} - {lo_name:9s} {observed:+6.1f}   "
            f"[{lo_ci:+6.1f}, {hi_ci:+6.1f}]  {excludes}   p = {p:.4g}"
        )

    print("\nOverlap check on the paper's original claim")
    a_lo, _ = percentile_ci(reps["A"])
    _, c_hi = percentile_ci(reps["C_best5"])
    print(f"  System A lower bound      : {a_lo:.1f}")
    print(f"  System C best-of-5 upper  : {c_hi:.1f}")
    print(f"  gap                       : {a_lo - c_hi:+.1f}")


if __name__ == "__main__":
    main()
