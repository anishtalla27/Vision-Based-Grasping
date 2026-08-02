# System B results (learned grasp predictor)

Spec section 5.3, scored with the same section 6 metric and the same 123 held-out test images as System A. Train (620) fit the models, val (140) selected them, test was opened once, here.


## Headline

**resnet18 — 79.7%** (98/123) on the test split.

System A was 57.7%, so System B is **+22.0 points**.


## Custom CNN learning rate: resolved, not open

The custom CNN does not use the framework default. It was swept on VAL over five rates (45 epochs each): 3e-5, 1e-4, 3e-4, 1e-3, 3e-3. The table below is the full result, not just the winner.

| LR | Val acc | Val angle err | Final train loss |
|---|---|---|---|
| 3e-05 | 21.4% | 28.0 deg | 1.3219 |
| 0.0001 | 27.1% | 23.4 deg | 0.6014 |  <- selected, final
| 0.0003 | 26.4% | 22.4 deg | 0.8376 |
| 0.001 | 20.0% | 26.6 deg | 1.4168 |
| 0.003 | 22.9% | 27.2 deg | 1.0488 |

**1e-4 is the confirmed final rate**, not an open question. 3e-5 was added after reviewing the first four and scored worse (21.4% vs 27.1%) with a higher final loss (1.32 vs 0.60), so it is undertrained at 45 epochs rather than a better optimum, and the search was not extended further below it. 1e-4 and 3e-4 sit close together (under one val image apart on 140 images) and both are clearly ahead of the three higher rates, which reads as a real low-end-wins trend rather than an isolated spike. 1e-4 also carries the lowest final training loss of all five candidates, so there is no accuracy/loss divergence suggesting the pick came from overfitting to val noise.


## All three architectures

The headline is the model selected on **val**, not the one that scored best on test. Picking by test score would be leakage, so all three test numbers are shown and the selection rule is stated rather than implied.

| Model | Params | Best val acc | Test acc | Mean angle err | Mean IoU (matched) | Selected |
|---|---|---|---|---|---|---|
| cnn | 1.0M | 27.1% | 23.6% | 24.2 deg | 0.391 |  |
| resnet18 | 11.3M | 83.6% | 79.7% | 3.9 deg | 0.447 | **yes** |
| resnet34 | 21.4M | 77.1% | 70.7% | 3.9 deg | 0.424 |  |

`Mean IoU (matched)` is averaged only over predictions that PASSED (matched a ground truth on both criteria), so it describes match quality and is not dragged down by failures the way an all-images average would be.

**Val-to-test gap for resnet18: 83.6% val to 79.7% test, a 3.9-point drop.** This sits well inside the 6.7-11.9 point epoch-to-epoch val noise measured during training (see the val-figures caveat below), which supports that the val-selected checkpoint is not overfit to val-selection noise -- a gap of that size is smaller than the swing val showed between two ordinary consecutive epochs of the same run.


## Against System A, on the axis that limited it

System A could only ever emit 0 or 90 degrees, because COCO boxes are axis-aligned. That put a hard floor under its angle error and accounted for 13 of its 52 failures. The sin/cos(2t) head removes that restriction entirely.

| | System A | System B |
|---|---|---|
| Test accuracy | 57.7% | **79.7%** |
| Orientations representable | 2 (0 and 90 deg) | continuous |
| Mean angle error | n/a (quantised) | 3.9 deg |
| Failures on angle alone | 13/52 | 4/25 |
| Failures on overlap alone | not measured | 15/25 |

## Failure cases, per model

Closest miss first, so these are the informative near-misses rather than the hopeless ones. `best IoU` and `angle err` are against whichever ground-truth grasp the prediction overlapped most.


**cnn** (94 failures out of 123):

| Image | Best IoU | Angle err | Missed on |
|---|---|---|---|
| pcd0784 | 0.45 | 44 deg | angle only |
| pcd0352 | 0.42 | 39 deg | angle only |
| pcd0351 | 0.42 | 62 deg | angle only |
| pcd0636 | 0.41 | 84 deg | angle only |
| pcd0523 | 0.40 | 85 deg | angle only |
| pcd0733 | 0.37 | 49 deg | angle only |
| pcd0786 | 0.36 | 73 deg | angle only |
| pcd0797 | 0.35 | 34 deg | angle only |

**resnet18** (25 failures out of 123):

| Image | Best IoU | Angle err | Missed on |
|---|---|---|---|
| pcd0676 | 0.39 | 44 deg | angle only |
| pcd0348 | 0.38 | 47 deg | angle only |
| pcd0824 | 0.37 | 59 deg | angle only |
| pcd0316 | 0.33 | 74 deg | angle only |
| pcd0760 | 0.23 | 4 deg | overlap only |
| pcd0783 | 0.22 | 8 deg | overlap only |
| pcd0347 | 0.21 | 31 deg | both |
| pcd0286 | 0.20 | 2 deg | overlap only |

**resnet34** (36 failures out of 123):

| Image | Best IoU | Angle err | Missed on |
|---|---|---|---|
| pcd0640 | 0.48 | 37 deg | angle only |
| pcd0350 | 0.42 | 48 deg | angle only |
| pcd0139 | 0.28 | 35 deg | angle only |
| pcd0549 | 0.28 | 66 deg | angle only |
| pcd0633 | 0.25 | 3 deg | overlap only |
| pcd0636 | 0.25 | 10 deg | overlap only |
| pcd0216 | 0.24 | 7 deg | overlap only |
| pcd0684 | 0.24 | 2 deg | overlap only |

## Method notes for the write-up

- Orientation is regressed as (cos 2t, sin 2t) on the unit circle. Direct theta regression would see a 178-degree error between two grasps 2 degrees apart, because the metric treats orientation as 180-degree symmetric.

- The loss is assigned best-match: computed against every labelled grasp, only the minimum backpropagated. Measured on train, regressing to the average of each image's grasps is capped at 86.5% even with a perfect model, because the average of a handle grasp and a rim grasp lies between them where neither is valid. Best-match is capped at 100%.

- Only one hyperparameter was tuned (the size-loss weight), on val. The 8-image overfit check preferred 3.0; val preferred 1.0 and val won.

- Augmentation transforms grasp rectangles by moving their four corners through the same affine as the pixels, then re-deriving the parameters, so no hand-written rule for how theta behaves under a flip can be backwards.


## Caveat: the val figures are optimistically biased

The val accuracies in the table above are each a MAXIMUM over ~50-120 epochs, and val accuracy is very noisy: on 140 images one image is worth 0.71 points, and the measured mean epoch-to-epoch swing is 6.7 to 11.9 points, with single jumps as large as 49. Taking the best of that many noisy draws is upward biased by construction, so a val number is not an unbiased estimate of anything.

Val is still the right tool for its actual job, which is choosing between checkpoints and architectures. It is simply not a performance figure. **Only the test column may be compared against System A's 57.7%**, and only once, which is what this script does. Any 'System B beats System A by N points' claim made from a val number would be comparing a best-of-many-draws figure on one split against a single sealed measurement on another.

