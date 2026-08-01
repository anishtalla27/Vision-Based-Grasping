# System A results (rule-based baseline)

Spec section 5.2, scored with the section 6 metric on the test split only (123 images, 35 objects). Train and val were not touched.

The lookup table was frozen in commit 853de49, before any evaluation code existed in the repository. It has been changed exactly once since, by amendment 1 below, which is recorded rather than folded in silently. No category mapping and no constant has ever been moved in response to an accuracy figure.


## Headline

| Measure | Value |
|---|---|
| Accuracy, with segmentation fallback | **57.7%** (71/123) |
| Accuracy, detector-only (misses count as failures) | 22.8% (28/123) |
| Accuracy among images the detector fired on | 57.1% (28/49) |
| Detector coverage | 49/123 (39.8%) |
| Fallback used | 66 images |
| No prediction possible | 8 images |

The gap between the first two rows is the point of reporting both. COCO's 80 classes do not cover most of what Cornell photographs, so the detector-only number is largely a statement about the detector's vocabulary rather than about whether the grasp rule works.


## Amendment 1, before and after

The table was frozen and evaluated once before the background-clutter guard existed. Both results are kept, so the change is visible rather than buried. Nothing else about the table changed; the only constant affected was OPENING_FRAC, which moved from 0.537 to 0.696 once boxes sitting on the room instead of the object stopped feeding calibration.

| | Before (commit afcd99a) | After |
|---|---|---|
| Accuracy, with fallback | 40.7% | **57.7%** |
| Accuracy, detector-only | 22.0% | 22.8% |
| Detector boxes trusted | 69 | 49 |

The detector-only number barely moves, which is the honest reading: the guard does not make the detector better, it just stops the system acting on boxes that were never on the object. The gain lands almost entirely in the fallback path.


## Accuracy by detected category

| Category | Images | Correct | Accuracy |
|---|---|---|---|
| (no detection) | 74 | 43 | 58% |
| cell phone | 11 | 8 | 73% |
| toothbrush | 6 | 2 | 33% |
| apple | 6 | 6 | 100% |
| scissors | 5 | 3 | 60% |
| kite | 5 | 2 | 40% |
| cup | 3 | 0 | 0% |
| frisbee | 2 | 2 | 100% |
| book | 2 | 1 | 50% |
| laptop | 2 | 0 | 0% |
| remote | 2 | 2 | 100% |
| bowl | 2 | 0 | 0% |
| snowboard | 2 | 1 | 50% |
| skis | 1 | 1 | 100% |

## Grip force recommendations (descriptive only)

Not scored. The dataset has no ground truth for grip force, so per spec section 6 this is reported as a distribution and nothing more.

| Force level | Images | Share |
|---|---|---|
| MEDIUM | 98 | 85% |
| LOW | 17 | 15% |

## Failure cases

Closest miss first, so these are the informative failures rather than the hopeless ones. `best IoU` and `angle err` are measured against whichever ground-truth rectangle the prediction overlapped most.

| Image | Category | Source | Best IoU | Angle err |
|---|---|---|---|---|
| pcd0305 | cell phone | detector | 0.62 | 38 deg |
| pcd1030 | kite | detector | 0.55 | 32 deg |
| pcd0299 | cell phone | detector | 0.50 | 35 deg |
| pcd0618 | (no detection) | fallback | 0.47 | 43 deg |
| pcd0732 | (no detection) | fallback | 0.45 | 38 deg |
| pcd0316 | cup | detector | 0.36 | 79 deg |
| pcd0199 | (no detection) | fallback | 0.35 | 79 deg |
| pcd0352 | cell phone | detector | 0.35 | 42 deg |

13 of the 52 failures had good enough overlap (IoU > 0.25) but failed on angle alone. That is the expected signature of this baseline: because COCO boxes are axis-aligned, the orientation rule can only ever output 0 or 90 degrees, so any object sitting diagonally is unreachable no matter how well the box is placed. Fixing that would require a rotated box or a learned orientation, which is exactly what System B is for.

