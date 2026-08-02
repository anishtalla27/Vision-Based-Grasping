# Section 6: Systems A, B and C compared

Spec section 6 and Deliverable 5. All three systems, one metric (angle within 30 degrees AND IoU above 25% against any labelled grasp), one sealed 123-image test split, one scoring code path.

Nothing here is a new measurement. Every number is a re-score of predictions that were already frozen, through `grasp_metric.is_correct`, which has not changed since commit `026032d`. No model was run and no API call was made. Because nothing is being selected, stratifying the sealed results carries no leakage risk -- this describes a finished measurement rather than searching over it.

The re-score reproduces all three sealed counts exactly (71/123, 98/123, 76/615), which is what licenses putting them in the same table: the comparison is not three separate scoring implementations being trusted to have agreed.


## Headline

| System | Test accuracy | 95% interval |
|---|---|---|
| A (rule-based) | 57.7% (71/123) | [48.9, 66.1] |
| **B (ResNet18, val-selected)** | **79.7%** (98/123) | [71.7, 85.8] |
| C (GPT-4o, mean of 5 repeats) | 12.4% (76/615 calls) | [10.0, 15.2] |

Intervals are Wilson score intervals. At n=123 they are wide enough to matter: System A's point estimate of 57.7% is consistent with anything from 48.9% to 66.1%, so small gaps between systems should not be read as settled.

System C's interval is computed over 615 calls and is therefore **anticonservative**: those are 5 correlated repeats of 123 images, not 615 independent trials. The honest spread is the one across its 5 individual runs: 13.0%, 14.6%, 13.8%, 10.6%, 9.8% (min 9.8%, max 14.6%). That per-repeat spread is a within-system sampling range, and it is never used as an inter-system error bar -- the two look alike in a table and mean completely different things.

One comparison worth making once, in prose rather than as a table row. System B trained three architectures and selected ResNet18 on **val**, before test was opened; the other two test numbers exist but are not leaderboard entries, because selecting on test is the thing that rule was written to prevent. With that stated: the from-scratch custom CNN, which System B's own results doc concludes failed to learn the task, still scored 23.6% [16.9, 31.8] against System C's 12.4% [10.0, 15.2]. The intervals do not overlap. A 1M-parameter network that could not learn grasp orientation from 620 images still outperformed a frontier VLM prompted zero-shot for coordinates.


## The organising claim: failure moves down the pipeline

All three systems solve the same task and fail at three different stages of it. System A can find the object but cannot rotate the gripper. System B can rotate the gripper but still mis-places it. System C fails before either question is reached, because the coordinates it emits are not bound to the object its own reasoning names.

That is one sentence with three clauses, and the rest of this document is evidence for them. It is also why the systems are ordered A, B, C rather than by score (which would be B, A, C): the ordering is how far into the problem each system gets before it fails.


## Failure taxonomy, recomputed identically for all three

Which criterion did a prediction miss on? Recomputed here from geometry for every system, so the bucketing rule is literally the same code in all three columns.

| Bucket | A (of 123 images) | B (of 123 images) | C (of 615 calls) |
|---|---|---|---|
| correct | 71 (57.7%) | 98 (79.7%) | 76 (12.4%) |
| angle_only | 13 (10.6%) | 4 (3.3%) | 85 (13.8%) |
| iou_only | 18 (14.6%) | 15 (12.2%) | 88 (14.3%) |
| both | 13 (10.6%) | 6 (4.9%) | 365 (59.3%) |
| no_prediction | 8 (6.5%) | 0 (0.0%) | 1 (0.2%) |

The signatures invert between A and B, which is the point. Of System A's 52 failures, 13 are angle-only (25%) -- the prediction is in the right place and pointing the wrong way. Of System B's 25 failures, only 4 are, while 15 are overlap-only: right rotation, wrong place. System B's mean angle error is 3.9 degrees, a number System A structurally cannot produce because COCO boxes are axis-aligned and its orientation rule can only emit 0 or 90 degrees.

System C's dominant bucket is neither: 365 of 615 calls (59.3%) miss on angle and overlap simultaneously. A prediction that fails both criteria at once is not a mis-rotation or a mis-placement, it is a rectangle that has little to do with the object.


## Condition breakdown: ground-truth orientation

Cornell ships no occlusion or lighting metadata, so the condition axes are the ones the annotations themselves support. This one splits the test set by whether any labelled grasp on the image sits within 15 degrees of axis-aligned. It comes from the dataset's `cpos` files, not from any system's output, which is what makes it usable as a shared axis.

| Stratum | Images | A | B | C |
|---|---|---|---|---|
| axis-aligned | 103 | 61.2% [51.5, 70.0] | 77.7% [68.7, 84.6] | 12.0% [9.5, 15.1] |
| diagonal | 20 | 40.0% [21.9, 61.3] | 90.0% [69.9, 97.2] | 14.0% [8.5, 22.1] |

System A drops 21.2 points on images where every labelled grasp is diagonal, which is exactly the penalty its representation predicts. System B moves 12.3 points in the other direction -- it is not merely unhurt by diagonal objects, it does slightly better on them -- which is what 'orientation is no longer the binding constraint' looks like. System C moves 2.0 points, i.e. it is flat: its errors are not orientation errors at all, which is the same conclusion the compound-failure bucket reaches by a different route. Its move is in the same direction as System B's and a sixth the size, which is what no signal on an axis looks like.

The diagonal stratum has only 20 images and its intervals are correspondingly wide, so each individual cell is weak evidence. What is not weak is that three systems move in three different directions on the same split, which is harder to produce by chance than any one of the cells.


## Condition breakdown: number of labelled grasps

The second axis the annotations support. More labelled grasps means more rectangles a prediction can match, so this is roughly a difficulty proxy.

| Labelled grasps | Images | A | B | C |
|---|---|---|---|---|
| 2-4 | 53 | 50.9% | 83.0% | 10.2% |
| 5-7 | 45 | 71.1% | 84.4% | 15.6% |
| 8-25 | 25 | 48.0% | 64.0% | 11.2% |

This axis does not behave the way the difficulty-proxy reading predicts. All three systems do worst on the images with the MOST labelled grasps, not the fewest, even though more labelled grasps means more rectangles a prediction is allowed to match. The likely reason is that annotators labelled many grasps on objects that afford many grasps -- long, thin, multi-part things -- so the count is tracking object complexity more than it is tracking how much credit the metric hands out. Reported because it was computed, not because it supports the throughline; it is the weaker of the two condition axes and it is not used to argue anything.


## Accuracy by object

Cornell ships no category labels, so the only externally-sourced grouping available is object identity from the frozen object-wise split -- 35 groups across the test set. That is the axis; the **names below are descriptive labels for readability and are not scoring ground truth**. They are the modal `object` string System C emitted for each group (a re-parse of its sealed log, no new calls), with a vote share showing how consistent that naming was.

Using either System A's COCO labels or System C's strings as the *stratification* axis would have biased the comparison toward whichever system produced the axis, which is why object_id is doing the grouping and the strings are only sitting next to it.

Cross-check, and its limits. A second, independent description of some objects exists in the split review's free-text notes. It turns out to be a weak check rather than a real second opinion: the notes were written per boundary PAIR, to justify a same/different decision, so they only reach 19 of the 35 groups, and several of the entries describe a segmentation artifact ('tiny silver object in a distant uncropped scene') rather than naming an object at all. Of the 19 reachable groups, 11 agree with the VLM name and 8 do not. The remaining 16 have no second source and rest on one source alone.

**Neither guess is adopted for these.** Both sources are themselves model-generated (one is System C's own output, the other is free text from an earlier review pass) and neither is ground truth, so picking a winner between two guesses would not resolve anything -- it would just launder a guess into something that reads as authoritative because it is sitting in a results table. The table below shows the object as `object N (label uncertain)`, with no committed name, for all 8 disputed groups. Both raw guesses are recorded here so anyone who wants to settle it can go look at the actual images.

| Object | VLM guess | Split-review guess |
|---|---|---|
| 26 | plastic clip | black bent wire shape |
| 50 | rectangular device | tiny silver object in a distant uncropped scene |
| 56 | remote control | dark phone side view |
| 151 | compact disc | tiny blue/silver object in a distant uncropped scene |
| 183 | light bulb | tiny white blob in a distant uncropped scene |
| 221 | metal carabiner | tiny gray paperclip-like sliver (segfail) |
| 230 | spool of thread | similarly shaped red/maroon bead |
| 231 | cylinder | dark green/black bead |

| Object | Label (descriptive) | Vote share | Images | A | B | C |
|---|---|---|---|---|---|---|
| 56 | object 56 (label uncertain) | 0.00 | 9 | 77.8% | 100.0% | 6.7% |
| 23 | toothbrush | 0.40 | 8 | 50.0% | 100.0% | 0.0% |
| 139 | flip-flop sandal | 0.20 | 8 | 50.0% | 75.0% | 15.0% |
| 189 | green apple | 0.50 | 8 | 100.0% | 87.5% | 40.0% |
| 107 | computer mouse | 0.60 | 5 | 60.0% | 100.0% | 16.0% |
| 183 | object 183 (label uncertain) | 0.00 | 5 | 0.0% | 100.0% | 24.0% |
| 6 | green pen | 0.60 | 4 | 100.0% | 100.0% | 0.0% |
| 7 | sunglasses | 1.00 | 4 | 25.0% | 75.0% | 5.0% |
| 8 | rectangular box | 0.45 | 4 | 75.0% | 75.0% | 5.0% |
| 26 | object 26 (label uncertain) | 0.00 | 4 | 75.0% | 50.0% | 0.0% |
| 35 | toothbrush | 1.00 | 4 | 75.0% | 50.0% | 0.0% |
| 50 | object 50 (label uncertain) | 0.00 | 4 | 25.0% | 75.0% | 0.0% |
| 70 | mug | 0.26 | 4 | 25.0% | 25.0% | 15.0% |
| 114 | scissors | 1.00 | 4 | 75.0% | 50.0% | 10.0% |
| 163 | remote control | 0.20 | 4 | 100.0% | 100.0% | 25.0% |
| 166 | folded umbrella | 1.00 | 4 | 75.0% | 75.0% | 15.0% |
| 173 | potato masher | 0.30 | 4 | 50.0% | 75.0% | 25.0% |
| 179 | cleaning brush | 0.50 | 4 | 25.0% | 75.0% | 10.0% |
| 188 | red grape | 0.40 | 4 | 100.0% | 100.0% | 15.0% |
| 57 | metal bolt | 0.27 | 3 | 66.7% | 33.3% | 6.7% |
| 150 | purple cup | 0.40 | 3 | 66.7% | 66.7% | 13.3% |
| 151 | object 151 (label uncertain) | 0.00 | 3 | 0.0% | 100.0% | 20.0% |
| 71 | calculator | 0.40 | 2 | 50.0% | 100.0% | 40.0% |
| 108 | wristwatch | 0.30 | 2 | 50.0% | 100.0% | 10.0% |
| 129 | blue sunglasses | 0.30 | 2 | 50.0% | 50.0% | 10.0% |
| 143 | plastic dispenser | 0.20 | 2 | 50.0% | 100.0% | 20.0% |
| 230 | object 230 (label uncertain) | 0.00 | 2 | 50.0% | 100.0% | 0.0% |
| 231 | object 231 (label uncertain) | 0.00 | 2 | 50.0% | 100.0% | 20.0% |
| 22 | toothbrush | 1.00 | 1 | 100.0% | 0.0% | 0.0% |
| 28 | digital camera | 0.40 | 1 | 0.0% | 100.0% | 0.0% |
| 55 | rectangular device | 0.80 | 1 | 0.0% | 100.0% | 0.0% |
| 59 | plastic cup | 1.00 | 1 | 0.0% | 0.0% | 0.0% |
| 62 | black bowl | 0.80 | 1 | 0.0% | 0.0% | 0.0% |
| 154 | red spool | 0.20 | 1 | 100.0% | 100.0% | 0.0% |
| 221 | object 221 (label uncertain) | 0.00 | 1 | 0.0% | 100.0% | 0.0% |

**No significance is claimed at the object level.** 7 of 35 groups contain a single image, where accuracy can only be 0% or 100%, and even the largest group is 9 images. Counts are printed next to every rate so no row can be read as a rate without its denominator.


## Are the differences real? Paired tests

All three systems ran on the same 123 images, so the comparison is paired and uses McNemar's exact test on the images where two systems disagreed. An unpaired test would discard the pairing for nothing.

| Comparison | First only | Second only | p |
|---|---|---|---|
| A vs B | 11 | 38 | 0.00014 |
| A vs C (5 repeats) | 59-64 | 4-6 | 5e-12 (worst of 5) |
| B vs C (5 repeats) | 84-88 | 1-4 | 1.6e-20 (worst of 5) |

**System C is tested five times, not once.** Its output varies run to run, so collapsing it to a mean and then testing that mean as though it were a single draw would hide exactly the variance the spec asked to measure. Each repeat is tested separately and the worst p-value of the five is the one reported, so the conclusion does not depend on which repeat happens to be picked.

**What 'System C trails System A' is licensed to mean.** The strongest available version of that claim, stated against the hardest possible comparison -- System C's most flattering number against System A's least flattering one:

> System C's best-of-5 ceiling is 35.0% (43/123), upper 95% bound 43.7%. That figure requires five calls per image and an oracle that knows which of the five was right. System A's single-call lower 95% bound is 48.9%. The intervals do not overlap, so the ordering does not depend on the point estimates being exact.

Best-of-5 is not compared against A's or B's single-call numbers anywhere else in this document, and it is not System C's headline. It appears here only because it is the number most favourable to System C, and the ordering survives it.


## Where the systems agree

System C needs a stated rule here, because it does not produce one verdict per image. Both rows below use the rule most generous to it: 'C correct' means at least one of its 5 repeats was correct, and 'C wrong' means none of the 5 were.

| | Images |
|---|---|
| A and B both correct | 60 |
| A and B both wrong | 14 |
| A correct, B wrong | 11 |
| B correct, A wrong | 38 |
| All three correct (C on at least 1 of 5) | 22 |
| All three wrong (C on none of 5) | 10 |

10 images defeat every system tried, even giving System C five attempts. Those are the closest thing this project has to a difficulty floor, and they are the images worth looking at first if a fourth system is ever built. The 49 images where A and B disagree are the more interesting set for understanding what the learned model actually bought.


## Reported per system, not compared across them

Some of the most informative numbers in this project exist for only one system. They are reported, but never tabulated side by side, because a three-column table implies a three-way comparison.

- **System C's repeat consistency** (mean self-agreement 22.0%, 65.9% of images stable at 5/5 or 0/5, abstention curve reaching 57.7% accuracy at 21.1% coverage). Systems A and B are deterministic functions of the image: the same pixels give the same rectangle every time, so their consistency is 100% *by construction*. Printing 100% / 100% / 22.0% would imply A and B won a robustness comparison they were never entered into.

- **System B's val-to-test gap** (83.6% val to 79.7% test). Systems A and C have no val stage, so there is no such quantity for them.

- **System A's detector coverage** (49/123 images, 39.8%, with a segmentation fallback carrying the other 66). Neither B nor C has a coverage concept.

- **System C's parse rate** (614/615 calls, 99.8%). A and B cannot emit malformed output.

The asymmetry is a fact about the systems, not a gap in the analysis. Forcing a comparison to exist where it does not would be a worse failure than reporting three columns of different lengths. Full detail for each lives in `system_a_results.md`, `system_b_results.md` and `system_c_results.md`.


## Grip force, descriptive only

Spec section 6 requires this be reported as a distribution and never as an accuracy, because the dataset carries no force ground truth and scoring it would mean inventing one.

| Level | System A (123 images) | System C (615 calls) |
|---|---|---|
| LOW | 17 | 2 |
| MEDIUM | 98 | 612 |

System B has no force output at all -- it regresses grasp geometry only -- and that absence is stated rather than left as an empty column.


## Comparison sheets

12 images in `comparison_sheets/`, all three systems drawn on the same frame: green ground truth, red System A, blue System B, orange System C's five repeats. The selection rule is fixed and deterministic (equal quotas from three categories, in sorted id order) so the illustrations are not a place a nicer set could be shopped for.

- **B fixes A**: pcd0133, pcd0285, pcd0637, pcd0762
- **B still misses**: pcd0134, pcd0216, pcd0347, pcd0636
- **all three miss**: pcd0139, pcd0310, pcd0324, pcd0348


## Method note: verification discipline as a project pattern

This is a claim about process, not about grasping, which is why it sits in a methods subsection rather than among the results.

Three times in this project, a self-authored cross-check caught a bug in the project's own code *before* a number was reported rather than after. During split generation, a corruption in the grouping output was caught and fixed before the frozen split was used for anything. In System B, an early-stopping rule let a lucky pre-training epoch become the 'best' checkpoint, caught and fixed with a warmup-ineligibility rule and an epoch-40 floor justified from measured loss and val-volatility curves. In System C, an automated contamination-probe check reported 1/10 recognitions where an independent manual read of the same ten replies said 0/10; the disagreement was chased down to a smart-quote mismatch (the check tested for a straight apostrophe, the model wrote a curly one) that silently broke the negation logic.

The instances have nothing technical in common. What they share is the procedure: an automated result was checked against an independent method -- a second computation, a manual read, a hand-computed synthetic case -- and where the two disagreed, neither was trusted until the disagreement was explained. None of the three was found by an external reviewer, and none announced itself through a suspicious-looking headline number; two of them would have produced perfectly plausible results.

This section found a fourth thing of the same shape, though a milder one. `is_correct` returns `correct` computed against every labelled grasp, but returns its `best_iou`/`best_angle` diagnostics for the single highest-overlap grasp regardless of whether that one passed the angle test. On 9 of 123 System B images and 9 of 614 System C calls the two disagree, because the prediction matched a different rectangle than the one it overlapped most. **No published number is wrong** -- both systems' taxonomy code tests `correct` first, which is the ordering that makes it come out right -- so this is a reuse hazard in a shared function's return signature rather than a caught bug, and it is recorded as such rather than inflated. It is the reason this script recomputes every taxonomy from geometry instead of reading the stored diagnostic columns.


## Scope of these claims

**What this comparison establishes.** On the Cornell Grasping Dataset, at 640x480, under the standard 30-degree / 25%-IoU metric, on 123 held-out images of 35 objects that appear nowhere in training: one frozen prompt to GPT-4o producing free-text JSON coordinates trails both a COCO-detector rule baseline and a fine-tuned ResNet18, decisively and with non-overlapping intervals.

**What it does not establish**, written as the specific sentences this evidence does not support:

- Not *VLMs cannot do grasp prediction*. One model, one prompt, one elicitation method. Set-of-marks prompting, point-and-click grounding, or a grounded detection head might bind reasoning to coordinates far better. That comparison was not run.

- Not *GPT-4o lacks spatial grounding*. The finding is about free-text coordinate output specifically -- the model's `reasoning` strings frequently named a real, sensible part of the object while the coordinates in the same reply did not land on it. That is a binding failure in one output channel, not a perception result.

- Not that System B is solved. 79.7% on 123 images of 35 objects, one dataset, no hardware, interval [71.7, 85.8]. Spec section 8 forbids calling this a finished grasp system and that still holds.

- Not that 57.7% is *the* classical-baseline number. It is one specific rule, and System A's own results doc shows a segmentation fallback did most of the work while the pretrained detector fired on 39.8% of images.

- Nothing that would flip under training-data contamination. Cornell is public and widely mirrored, so a frontier model could plausibly have seen it; a 10-image probe came back 0/10 and is reported as a weak indicator, not a clearance. Contamination can only inflate System C, so every conclusion drawn here is of the form 'C trails', which survives it. No 'C does surprisingly well' claim is made anywhere, so nothing depends on the probe.

- No seen-versus-unseen category breakdown. The split is object-wise, so every test object is unseen by construction and the breakdown collapses to a single cell. That is a property of the split design, reported rather than faked into two rows.

- No occlusion or lighting breakdown. Cornell ships no such metadata, and hand-labelling it would be exactly the self-authored ground truth spec section 8 rules out. The two condition axes above are what the annotations actually support.

- No object-level significance. See the counts in that table.

