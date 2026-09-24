# System B, round 2 (multi-seed, cosine + EMA recipe)

Second opening of the sealed 123-image test split, recorded as such. Round-1 numbers (single seed 42, constant LR, best-of-epochs checkpoint) are unchanged in `system_b_results.md`. All four selection rules in `scripts/system_b_eval_v2.py` were fixed before this file was produced.

## Rule 1: architecture chosen on mean final-EMA val accuracy

| Architecture | Seeds | Mean final-EMA val acc | Per seed |
|---|---|---|---|
| resnet18 | 3 | 81.2% | 83.6, 79.3, 80.7 |
| resnet34 (picked) | 3 | 81.4% | 81.4, 81.4, 81.4 |

## Rule 2: TTA decided on val

resnet34 final-EMA val accuracy per seed: plain [81.42857142857143, 81.42857142857143, 81.42857142857143], TTA (8 dihedral views, medoid) [82.85714285714286, 82.85714285714286, 84.28571428571429]. Headline uses **TTA**.

## Rule 3: headline = resnet34 v2 final, TTA, mean over seeds

**84.0% (sd 0.5, seeds 84.6, 83.7, 83.7)** against round 1's 70.7% for the same architecture.

## Rule 4: everything that was run on test in round 2

| Configuration | Seed | Test acc | Angle only | Overlap only | Both | Angle err (correct, matched) | Angle err (any grasp, all images) |
|---|---|---|---|---|---|---|---|
| resnet18 orig final, plain | 0 | 80.5% (99/123) | 6 | 16 | 2 | 5.6 deg | 4.4 deg |
| resnet18 orig val-best ckpt, plain | 0 | 82.9% (102/123) | 1 | 8 | 12 | 6.0 deg | 4.3 deg |
| resnet18 orig final, plain | 1 | 62.6% (77/123) | 5 | 25 | 16 | 6.2 deg | 5.5 deg |
| resnet18 orig val-best ckpt, plain | 1 | 80.5% (99/123) | 8 | 12 | 4 | 5.6 deg | 4.7 deg |
| resnet18 v2 final, plain | 0 | 79.7% (98/123) | 3 | 16 | 6 | 4.7 deg | 3.3 deg |
| resnet18 v2 final, TTA | 0 | 83.7% (103/123) | 3 | 10 | 7 | 4.5 deg | 3.4 deg |
| resnet18 v2 val-best ckpt, plain | 0 | 78.9% (97/123) | 2 | 15 | 9 | 4.9 deg | 3.4 deg |
| resnet18 v2 final, plain | 1 | 80.5% (99/123) | 1 | 12 | 11 | 5.7 deg | 4.7 deg |
| resnet18 v2 final, TTA | 1 | 80.5% (99/123) | 2 | 12 | 10 | 3.7 deg | 3.1 deg |
| resnet18 v2 val-best ckpt, plain | 1 | 77.2% (95/123) | 1 | 19 | 8 | 5.7 deg | 4.9 deg |
| resnet18 v2 final, plain | 2 | 81.3% (100/123) | 2 | 18 | 3 | 5.1 deg | 3.5 deg |
| resnet18 v2 final, TTA | 2 | 83.7% (103/123) | 1 | 13 | 6 | 4.8 deg | 3.3 deg |
| resnet18 v2 val-best ckpt, plain | 2 | 80.5% (99/123) | 4 | 14 | 6 | 5.1 deg | 4.0 deg |
| resnet34 v2 final, plain | 0 | 80.5% (99/123) | 5 | 15 | 4 | 5.0 deg | 4.2 deg |
| resnet34 v2 final, TTA | 0 | 84.6% (104/123) | 4 | 10 | 5 | 4.6 deg | 3.0 deg |
| resnet34 v2 val-best ckpt, plain | 0 | 82.9% (102/123) | 4 | 12 | 5 | 5.3 deg | 4.4 deg |
| resnet34 v2 final, plain | 1 | 82.1% (101/123) | 2 | 15 | 5 | 4.6 deg | 3.3 deg |
| resnet34 v2 final, TTA | 1 | 83.7% (103/123) | 1 | 13 | 6 | 3.5 deg | 3.0 deg |
| resnet34 v2 val-best ckpt, plain | 1 | 78.0% (96/123) | 3 | 18 | 6 | 4.8 deg | 4.1 deg |
| resnet34 v2 final, plain | 2 | 78.0% (96/123) | 3 | 19 | 5 | 4.3 deg | 3.5 deg |
| resnet34 v2 final, TTA | 2 | 83.7% (103/123) | 1 | 11 | 8 | 3.8 deg | 3.0 deg |
| resnet34 v2 val-best ckpt, plain | 2 | 80.5% (99/123) | 1 | 14 | 9 | 4.5 deg | 3.8 deg |

The two angle-error columns are the two definitions the paper previously conflated: round 1's 3.9 degrees was the second column (nearest labelled orientation on every image, pass or fail), while the text described the first (correct predictions only, against the grasp the metric matched).

Per-seed, per-image correctness for the headline configuration is in `system_b_v2_per_image.csv`; the object-clustered statistics script reads it.

## Object-clustered statistics (scripts/object_clustered_stats_v2.py)

B_v2 is scored per image as the fraction of the three seeds that passed,
the same pooling rule System C's repeats use. 20,000 object resamples,
20,000 object-level permutations, seed 0.

| System | Accuracy | Object-clustered 95% CI | Object-balanced |
|---|---|---|---|
| A | 57.7% | [46.2, 68.2] | 51.3% |
| B, round 1 (one seed) | 79.7% | [70.8, 87.1] | 75.4% |
| **B, round 2 (3 seeds)** | **84.0%** | [73.9, 92.1] | 79.8% |
| C, one call | 12.4% | [8.0, 17.4] | 10.5% |

| Difference | Points | 95% CI | Permutation p |
|---|---|---|---|
| B round 2 minus A | +26.3 | [+14.8, +38.3] | 0.0002 |
| B round 2 minus B round 1 | +4.3 | [-5.8, +13.7] | 0.43 |
| B round 2 minus C | +71.7 | [+61.3, +80.9] | 5e-5 |

By orientation stratum: axis-aligned (103 images) round 1 77.7%, round 2
83.8%; diagonal (20 images) round 1 90.0%, round 2 85.0%.

## What round 2 changes, and what it does not

- **The round-1 headline was a single draw, and a low-side one.** The
  original recipe re-run at seeds 0 and 1 gave val-best checkpoints
  scoring 82.9% and 80.5% on test, so the three original-recipe seeds
  (with round 1's 79.7%) average 81.0% with a spread of 1.6 points.
  Round 1's number stays on record; it is not wrong, it is one sample.
- **The round-1 "ResNet18 beats ResNet34 by 9 points" claim does not
  survive.** Under the stable recipe, final-weight val accuracy is 81.2%
  (ResNet18) against 81.4% (ResNet34), and test accuracy with TTA is
  82.6% against 84.0%. The round-1 gap was run-to-run noise.
- **The checkpoint lottery is gone.** Round 2's headline uses the
  final-epoch averaged weights with no selection, and those beat the
  val-best checkpoint of the same run on 5 of 6 runs. The original
  recipe's FINAL weights (no checkpoint rescue) scored 80.5% and 62.6%
  on test for its two re-seeds, which is what a constant learning rate
  with no averaging looks like at the end of training.
- **Test-time augmentation is worth about 3 points** (six paired runs:
  +4.0, 0.0, +2.4, +4.1, +1.6, +5.7), decided on val before test.
- **The ordering of the three families does not move.** B leads A by 26
  points and C by 72; both exclude zero after object clustering.

Test was opened a second time for this round. The four rules in
`scripts/system_b_eval_v2.py` were fixed before any round-2 test number
existed, the 60-epoch budget was rejected on val evidence alone
(`system_b_v2/budget60/`), and every configuration that touched test is
listed in the Rule 4 table above, so nothing was selected on test.
