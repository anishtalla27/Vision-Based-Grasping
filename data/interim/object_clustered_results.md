objects: 35   images: 123
bootstrap: 20000 resamples, permutation: 20000, seed 0

Object-clustered 95% CIs (image-level accuracy)
  A          57.7%   [ 46.2,  68.2]
  B          79.7%   [ 70.8,  87.1]
  C_pooled   12.4%   [  8.0,  17.4]
  C_best5    35.0%   [ 24.6,  45.5]

Object-balanced accuracy (each object weighted equally)
  A          51.3%   [ 40.0,  62.4]
  B          75.4%   [ 64.5,  85.1]
  C_pooled   10.5%   [  7.0,  14.3]
  C_best5    29.8%   [ 21.1,  38.5]

Paired differences (object-clustered bootstrap CI, permutation p)
  B         - A          +22.0   [  +9.7,  +35.1]  excludes 0   p = 0.0031
  A         - C_best5    +22.8   [  +9.2,  +35.6]  excludes 0   p = 0.00595
  A         - C_pooled   +45.4   [ +33.8,  +55.6]  excludes 0   p = 5e-05
  B         - C_pooled   +67.3   [ +58.1,  +75.8]  excludes 0   p = 5e-05

Overlap check on the paper's original claim
  System A lower bound      : 46.2
  System C best-of-5 upper  : 45.5
  gap                       : +0.7

## Addendum: clean (pre-correction) System A, added for the ICDM 2026 camera-ready

Reviewer 3 asked that the paired comparisons rest on the pre-correction 40.7%
rather than the post-hoc 57.7%. `system_a_run_precorrection.py` reproduces the
afcd99a run per image (50/123, 69 detector boxes trusted, asserted in the
script) and adds `a_pre_correct` to `comparison_per_image.csv`;
`object_clustered_stats.py` now includes it as `A_pre`. The original rows above
reproduce unchanged (same seed, same bootstrap draws).

```
Object-clustered 95% CIs (image-level accuracy)
  A_pre      40.7%   [ 28.0,  53.2]

Object-balanced accuracy (each object weighted equally)
  A_pre      38.5%   [ 27.2,  50.3]

Paired differences (object-clustered bootstrap CI, permutation p)
  B         - A_pre      +39.0   [ +25.2,  +52.9]  excludes 0   p = 5e-05
  A_pre     - C_best5     +5.7   [  -6.1,  +18.0]  INCLUDES 0   p = 0.4544
  A_pre     - C_pooled   +28.3   [ +16.9,  +40.0]  excludes 0   p = 0.0001
```

The one change of substance: against the clean heuristic, GPT-4o's best-of-five
ceiling is no longer separated from System A. Its expected one-call score
still is.
