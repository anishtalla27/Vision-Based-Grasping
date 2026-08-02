# Vision-Informed Grasp Decision Prediction — Source of Truth

## Sub-project of: Adaptive Robotic Grasping Through Vision-Informed Grip Decisions, Multi-Signal Slip Detection, and Real-Time Recovery

Researcher: Anish Talla (high school senior research, ISEF/RSEF level)
Status: Summer work phase, no physical hardware available yet (gripper build happens in fall). Object-wise dataset split is finalized as of this update. See Section 10 for full status and workflow context.
Purpose of this file: this is the current, authoritative plan for the summer sub-project. It replaces the earlier single-model version of this document. Anyone (human or AI) picking up this work should treat this file as the plan to follow, not the earlier draft. Section 10 is an addendum documenting what actually happened during dataset preparation, since real decisions were made that future work (and the eventual paper) needs to reflect accurately.

---

## 1. Where this fits in the larger project

The full senior research project has three pillars:

1. **Vision-informed grip decisions** (this sub-project)
2. Multi-signal slip detection (FSR + piezoelectric sensors, requires physical gripper, done in fall)
3. Real-time recovery (requires physical gripper, done in fall)

This document covers pillar 1. The output is meant to eventually feed into pillars 2 and 3 once the physical gripper exists in the fall. Right now the work only needs to take an image in and output a predicted grasp location, orientation, and grip force recommendation. No physical hardware is required.

---

## 2. What changed from the original plan, and why

An earlier draft ("Version 2") proposed a broader pipeline: detect object category, predict material/fragility/shape attributes, and use those attributes to pick a grip strategy, comparing three systems (category rules, predicted attributes, direct vision-language model recommendation) against a self-authored human-reviewed answer key.

That version had a real flaw worth stating explicitly so it doesn't get reintroduced later: the planned ground truth for evaluation would have been written by the same person building the rule-based baseline, using roughly the same reasoning. That makes the rule-based system's evaluation circular, since it's partly being graded against its own logic. It also leaned heavily on predicting material and fragility from a 2D image, attributes that are genuinely hard to verify from a photo and would have needed the same kind of self-authored judgment calls to "grade."

This document keeps the part of Version 2 that was actually good: comparing multiple decision-making approaches against each other. It fixes the ground truth problem by evaluating everything against the Cornell Grasping Dataset's existing hand-labeled grasp rectangles, which is an objective, external answer key nobody on this project invented. Material and fragility classification are dropped as primary outputs for this reason. Grip force is kept, but only as a secondary, more loosely evaluated output, not a primary metric the whole project rests on.

---

## 3. Research question

**Primary question:** Given an image of an object, which grasp-prediction approach most accurately identifies a viable grasp point (location, orientation, opening width), when evaluated against the Cornell Grasping Dataset's hand-labeled ground truth rectangles?

Three systems are compared:

- **System A — Rule-based baseline.** A pretrained object detector identifies the object category (mug, bottle, box, etc.). A small fixed lookup table maps category to a generic grasp region and force level (e.g. mug → handle, low force). This baseline requires no training and represents "the simple, non-learned approach."
- **System B — Learned grasp predictor.** A CNN (custom baseline) and a fine-tuned pretrained backbone (ResNet18/34) trained directly on the Cornell Grasping Dataset to predict grasp rectangles from image input. This is the core modeling work of the sub-project.
- **System C — Vision-language model baseline.** A pretrained multimodal model (e.g. a VLM with vision input) is prompted directly with the object image and asked to describe a grasp point and orientation, without any task-specific training. This represents "what you get for free from a general-purpose model with no custom training."

All three are scored against the same ground truth, using the same metric, on the same held-out test images. Nobody on the project is authoring the ground truth by hand. It comes directly from the dataset's existing annotations.

**Secondary question:** How does each system's accuracy change across object categories, and where does each one fail? This replaces the earlier material/fragility prediction goal with a lower-risk, still-interesting axis: category-level and condition-level (occlusion, lighting) breakdown of accuracy, using only what the dataset and evaluation already provide.

---

## 4. Dataset

**Primary: Cornell Grasping Dataset**
- Roughly 1035 images of about 280 real objects, each with hand-labeled ground-truth grasp rectangles (positive and negative grasp candidates)
- Each grasp rectangle is defined by center point (x, y), orientation angle (theta), width, and height
- This is the standard benchmark in the grasp-prediction literature, so results are comparable to published numbers
- Check current download/hosting availability before starting, since it has moved between mirrors over time

**Alternative/supplement: Jacquard Dataset**
- Larger (around 54,000 images, roughly 11,000 objects), simulation-generated with rendered depth and RGB images and grasp annotations
- Useful as a backup if Cornell access is unreliable, or as a second dataset to test generalization (train on one, test on the other)

**Object category labels**, used for System A's lookup table and for the category-level accuracy breakdown, should come from whatever category metadata ships with the dataset, or from a pretrained general-purpose object detector run on the images (not from ad hoc labeling by the researcher, to avoid reintroducing the ground-truth problem described in section 2).

**Action item for whoever continues this:** verify current download links for both datasets before starting.

---

## 5. Methodology

### 5.1 Preprocessing
- Resize all images to a consistent input size (e.g. 224x224 for ResNet compatibility)
- Normalize grasp rectangle labels to match resized image coordinates
- Split into train/validation/test. Use an **object-wise split**, where the same physical object never appears in both train and test, rather than a plain image-wise split. Image-wise splits can inflate accuracy by letting the model memorize object appearance. This should be explicitly justified in the methods section.

### 5.2 System A — Rule-based baseline
- Run a pretrained object detector (e.g. a standard COCO-pretrained model) to get object category per image
- Map category to a fixed grasp region and force level using a small lookup table defined once, before any evaluation is run, and not adjusted afterward to improve scores
- Convert the qualitative grasp region into a rough rectangle estimate (e.g. centered on the detected bounding box, generic orientation) so it can be scored with the same metric as the other systems

### 5.3 System B — Learned grasp predictor
Two architectures trained and compared against each other, in addition to being compared against Systems A and C:
1. **Baseline custom CNN**: a handful of conv layers built from scratch, regression or classification head outputting grasp rectangle parameters
2. **Fine-tuned pretrained backbone**: ResNet18 or ResNet34 pretrained on ImageNet, final layer(s) replaced with a grasp-prediction head, fine-tuned on the training split

Frame grasp prediction as either direct regression of (x, y, theta, w, h), or as rectangle proposal and classification (closer to how the original Cornell dataset papers approached it, and easier to compare against published benchmark numbers). Pick one framing and stay consistent.

### 5.4 System C — Vision-language model baseline
- Prompt a pretrained multimodal model with the raw image, asking it to identify a grasp location and orientation
- No task-specific training or fine-tuning; this system should represent out-of-the-box capability
- Parse the model's described grasp location into the same rectangle format used for scoring
- Also test **consistency across repeated prompts** on the same image (run the same image through multiple times), since VLM outputs can vary run to run. This becomes a data point in the results, not something to average away or discard.

### 5.5 Training details (System B only)
- Framework: PyTorch
- Environment: Google Colab (free tier) if MacBook compute is insufficient
- Loss function depends on framing chosen in 5.3 (MSE-based for regression, cross-entropy for classification/proposal)
- Track training/validation loss curves to check for overfitting, given the relatively small size of the Cornell dataset

---

## 6. Evaluation

All three systems are scored against the same ground truth, using the same metric, on the same held-out test set. This is the core methodological fix from section 2: one shared, externally-sourced answer key, not a separate hand-graded rubric per system.

**Primary metric (standard in the literature):** a predicted grasp rectangle counts as correct if
1. the angle difference between predicted and ground-truth grasp is within 30 degrees, AND
2. the Jaccard index (intersection over union) between predicted and ground-truth rectangles exceeds 25%

Report for each of the three systems:
- Overall accuracy on the test set
- Accuracy broken down by object category
- Accuracy broken down by condition where possible (occlusion, lighting, unseen vs seen category), to the extent the dataset supports this
- For System C specifically: consistency rate across repeated prompts on the same image
- Qualitative failure case analysis: a handful of images per system where the prediction was wrong, with a brief discussion of why

**Secondary, lower-confidence output:** grip force recommendation. This is not scored against a hand-authored answer key. If reported at all, present it descriptively (e.g. "System A recommended low force for X% of objects, System C for Y%") rather than as an accuracy number, since there is no objective ground truth for force level in the dataset. This is a deliberate scope reduction from the original Version 2 plan, which tried to score force and fragility predictions against self-authored labels.

---

## 7. Deliverables for this phase

1. Working data pipeline (dataset loaded, preprocessed, object-wise split)
2. System A implemented (pretrained detector plus fixed lookup table)
3. System B trained (both custom CNN and fine-tuned ResNet)
4. System C implemented (VLM prompting plus output parsing, including repeated-prompt consistency check)
5. Evaluation results comparing all three systems on the shared metric, with category and condition breakdowns
6. Written methodology section documenting all of the above, ready to drop into the eventual research paper
7. Short discussion of how System B's output (the strongest-performing predictor, most likely) will interface with the physical gripper's control logic once it exists in the fall

---

## 8. Constraints and notes for whoever continues this

- No physical hardware access during this phase. Everything runs on a laptop or free cloud compute.
- MacBook GPU support for PyTorch (the MPS backend) is less mature than CUDA. If training is slow, move to Google Colab rather than fighting local hardware.
- Do not introduce a self-authored ground truth for any primary metric. If a question can't be answered against the dataset's existing annotations or an established benchmark, either drop it or report it descriptively instead of as an accuracy score. This is the main lesson carried over from the flawed Version 2 draft.
- Keep the object-wise train/test split. This is easy to accidentally get wrong (e.g. by shuffling images randomly without checking which object each came from), and getting it wrong silently inflates every accuracy number in the paper.
- Keep code and written methodology clean enough to drop directly into a research paper draft. Comment code clearly.
- Do not overstate this as "the finished grasp decision system." Frame results as validated against the benchmark dataset and existing pretrained models, with real-hardware integration explicitly noted as future work for the fall.
- Writing style for anything drafted from this work should stay in plain, student-authored language: no AI-sounding phrasing, no em dashes, conversational but accurate tone, consistent with the rest of this project's documentation.

---

## 9. Key references to build the annotated bibliography / lit review around

- Lenz, Lee, and Saxena — the original Cornell Grasping Dataset paper, establishes the rectangle-based grasp representation and the accuracy metric used in section 6
- Redmon and Angelova — real-time grasp detection using convolutional neural networks, relevant for framing grasp detection as an object-detection-style problem
- Depierre, Dellandrea, and Chen — the Jacquard Dataset paper, relevant if Jacquard is used as a supplement or alternative dataset

These should be read directly by whoever continues the work, since exact findings and framing need to be verified against the actual papers rather than assumed from this summary.

---

## 10. Addendum — Dataset Preparation Outcome (added after Section 5.1 was completed)

This section documents what actually happened during dataset sourcing and the object-wise split, since the process deviated from a simple download-and-split and produced real methodological decisions that need to carry into the paper. Sections 1-9 above remain the authoritative plan; this section is a record of how Section 4/5.1 was actually executed, and should be treated as settled fact for anyone continuing the work, not re-litigated.

### 10.1 Jacquard Dataset ruled out for this phase

Jacquard was investigated as the primary dataset's fallback per Section 4, but its full distribution is gated behind a EULA requiring a signature and an institutional (non-free) email, submitted to the dataset maintainers for manual admin approval. Because this is summer and the research mentor/supervisor who would normally sign such a request is unavailable, this path is not accessible right now. **Cornell remains primary, as originally planned, but this reason for not using Jacquard should be noted honestly in the methods section if asked why only one dataset was used.**

### 10.2 Cornell Grasping Dataset ships with no object-identity metadata

The Cornell Grasping Dataset does not include an object ID per image, and the object list has no supervisor. This is a real obstacle to the object-wise split required in Section 5.1, since the split's core requirement is that all images of the same physical object end up in the same split, and there was no direct label to group by. Object identity had to be reconstructed from the image sequence itself.

### 10.3 Grouping methodology (summary; full detail lives in `data/interim/` and the git history)

1. **First attempt (rejected):** raw pixel-difference between consecutive frames. Failed because the dataset deliberately varies object rotation within each object's photo set, so same-object rotation and true object changes produced overlapping score distributions. Not usable, discarded.

2. **Working approach:** each frame was segmented using the scene's platform geometry (the object appears as a gap in an otherwise-uniform photography platform), avoiding background-plate misalignment problems. Segmented regions were scored using rotation-invariant descriptors (color histogram, pixel area). This produced a clean, validated separation between same-object and different-object consecutive pairs.

3. **Asymmetric confidence thresholds:** thresholds for automatic accept/reject were set asymmetrically rather than at the empirical midpoint between score distributions. Wrongly merging two different objects into one group is low-risk for a downstream object-wise split (the merged group still lands entirely in one split). Wrongly splitting one true object into two groups is high-risk (the pieces can land in different splits, silently inflating reported accuracy). The automatic "different" threshold was therefore set conservatively, below the lowest score seen for any manually-confirmed same-object pair; the automatic "same" threshold was set more permissively.

4. **Two-layer manual review for the ambiguous band (28.4% of boundaries):**
   - Full first pass by the assisting model over every ambiguous boundary, with a logged confidence level and reasoning per call
   - Independent blind validation: the researcher classified a stratified random sample (oversampled toward the model's uncertain calls) with no visibility into the model's calls
   - Result: 86.7% agreement on the model's confident calls, 40.0% on its uncertain calls. This confirmed the model's stated confidence was actually informative, and revealed a specific reasoning bias (inferring object continuity from a failed segmentation / thin visual sliver) that accounted for most of the disagreement
   - Full manual review was then done by the researcher on: all uncertain calls, all confident "different" calls (the higher-risk direction), and any call (regardless of confidence) whose reasoning relied on the flagged segfail-inference pattern
   - Confident "same" calls not flagged by the above were auto-accepted without individual review, since errors in that direction are low-risk by construction

5. **Six boundaries remained genuinely ambiguous after full manual review.** Four with a stated directional lean were resolved toward "same" (consistent with the asymmetric risk argument: a wrong "same" is low-cost, a wrong "different" is not). Two with no lean at all were not forced to a decision; instead, one image on the smaller side of each ambiguous boundary was excluded from the dataset rather than guessed at.

This entire process, including the rejected first approach and the reasoning bias caught during validation, is legitimate material for the paper's methods section. It should be written up honestly, including the dead end, since documenting what was tried and rejected (and why) is normal and expected in a methods section, not something to omit for looking cleaner.

### 10.4 Final split

| Split | Objects | Images |
|---|---|---|
| train | 164 | 620 |
| val | 35 | 140 |
| test | 35 | 123 |
| **Total** | **234** | **883** |

- 70/15/15 split by object count, random seed 42 for reproducibility
- Verified twice that no object appears in more than one split: once during construction, once independently by re-reading the final output file
- 883 of the original 885 images retained; 2 excluded per the unresolved-ambiguity handling described in 10.3, item 5
- Source of truth files: `data/interim/review_tracking.csv` (all 251 manually-reviewed boundary decisions) and `data/interim/final_split.csv` (every image with object ID and split assignment)

This split is finalized. Do not rebuild or re-derive it without a clear reason; if a reason arises, treat it as a deviation from this document and flag it explicitly rather than silently redoing the work.

### 10.5 Workflow conventions established during this phase (apply going forward)

These aren't part of the technical spec but are operating rules for how work gets done on this project, established during the split process and expected to continue for Systems A, B, and C:

- **Canary phrase:** every Claude Code message in this project must begin with "Anish," including short/repetitive status updates. If this stops happening, treat it as a signal to check in on context state, though note that in practice this has been more often a sign of instruction drift during long repetitive tool-use loops than actual context loss, worth a direct reminder before assuming a full context clear is needed.
- **No self-authored ground truth, no silent judgment calls by the assisting model.** This is the throughline of the whole split process and should continue into System A/B/C: any evaluation must trace back to an external, objective source (the dataset's own annotations), and any place where the model is inclined to resolve ambiguity on its own should instead be surfaced to the researcher explicitly, as happened with the six leftover ambiguous boundaries.
- **Model/effort/plan-mode should be specified per prompt**, not left to default: Opus 4.8 at high effort for judgment-heavy design work (thresholds, evaluation logic, anything touching ground truth), Sonnet 5 at medium/low for well-specified, mechanical execution. Plan mode on when real design decisions remain open; off when the approach is already fully specified.
- **Independent validation before trusting model output at scale**, especially anywhere errors could be asymmetric in cost. The blind-validation-sample pattern used for the boundary review (sample a subset, check independently, only then decide how much to trust the rest) is a reusable pattern and should be applied again wherever System A, B, or C output needs to be trusted before being used downstream.

### 10.6 System A outcome (Section 5.2, completed)

System A is built and evaluated. Test split only, 123 images, 35 objects; train and val were left untouched for System B.

| Measure | Result |
|---|---|
| Accuracy, with segmentation fallback (headline) | **57.7%** (71/123) |
| Accuracy, detector-only (misses count as failures) | 22.8% (28/123) |
| Accuracy among images the detector fired on | 57.1% (28/49) |
| Detector coverage | 49/123 (39.8%) |

Things worth carrying into the paper:

- **Two accuracy numbers are reported on purpose.** COCO's 80 classes do not cover most of what Cornell photographs, so a single detector-only figure would mostly measure the detector's vocabulary rather than whether the grasp rule works. Reporting both separates "COCO does not know what a stapler is" from "the grasp rule is wrong."
- **The detector was worse than the non-learned geometry it was meant to anchor.** Only 46.3% of all 883 images produced any detection, and COCO confidently mislabelled much of what it did find (94 "laptop", 36 "kite", 18 "snowboard", one "refrigerator"). The platform-segmentation fallback, written originally for the object-wise split, located the object more reliably than the pretrained detector did.
- **Amendment 1, recorded rather than hidden.** The table was frozen and evaluated once at 40.7% before a defect was spotted on a rendered test image: the detector often boxes background clutter, since Cornell shoots objects in an ordinary room. Measured on train, this affected 33.8% of detections. A geometric guard (the box must contain the segmented object's centroid) was added, `OPENING_FRAC` recalibrated on train from 0.537 to 0.696, and the result rose to 57.7%. Both numbers stay on the record, in `data/interim/system_a_results.md` and in commits `afcd99a` and `f3124c6`. No mapping or constant was ever moved in response to an accuracy figure.
- **The remaining ceiling is orientation.** 13 of the 52 failures clear the IoU bar and fail on angle alone. COCO boxes are axis-aligned, so the orientation rule can only ever emit 0 or 90 degrees and any diagonally-placed object is unreachable. This is the specific weakness System B exists to beat, and it makes a clean point of comparison.

The "defined once, not adjusted afterward" rule was enforced structurally, not on trust: the table was committed in `853de49`, and `git ls-tree` confirms no scoring code was tracked in the repository at that commit.

### 10.7 System B outcome (Section 5.3, completed)

Three architectures trained on train (620), selected on val (140), evaluated once on the same sealed 123-image test split System A used. Test was opened exactly once, by `scripts/system_b_eval.py`, after model selection was finished.

| Model | Params | Test accuracy | Mean angle error | Mean IoU (matched) |
|---|---|---|---|---|
| **ResNet18 (selected on val)** | 11.3M | **79.7%** (98/123) | 3.9 deg | 0.447 |
| ResNet34 | 21.4M | 70.7% (87/123) | 3.9 deg | 0.424 |
| Custom CNN (from scratch) | 1.0M | 23.6% (29/123) | 24.2 deg | 0.391 |

**System B vs System A, now valid since both are the same sealed test set:**

| | System A | System B |
|---|---|---|
| Test accuracy | 57.7% | **79.7%** (+22.0 points) |
| Orientations representable | 2 (0 and 90 deg) | continuous |
| Failures on angle alone | 13/52 | 4/25 |

Things worth carrying into the paper:

- **Architecture selection happened on val, before test was ever opened**, specifically to avoid picking whichever model got lucky on the sealed set. ResNet18 beat ResNet34 on both val (83.6% vs 77.1%) and test (79.7% vs 70.7%), consistent with the plan's prediction that 620 training images cannot use ResNet34's extra capacity. All three test numbers are reported regardless, not just the selected model's.
- **Orientation was the specific axis System B was built to fix, and it worked.** System A could only ever emit 0 or 90 degrees; System B regresses (cos 2θ, sin 2θ) on the unit circle, which has no seam at the metric's 180-degree symmetry point. ResNet18's angle-only failure count dropped in proportion (13/52 for System A vs 4/25 for System B) and its mean angle error is 3.9 degrees, a number System A could not even produce since its orientation was quantised.
- **The val-to-test gap was small and in the expected direction** (83.6% val to 79.7% test for ResNet18, a 3.9-point drop), well inside the epoch-to-epoch val noise measured during training (6.7-11.9 points), which is a reassuring sign rather than evidence of overfitting to val.
- **The custom CNN failed to learn the task**, even after its own learning-rate sweep. Five rates were tried on val (3e-5 through 3e-3); the winner, 1e-4, also had the lowest final training loss of all five, so the failure is not an artifact of an untuned rate. Training loss plateaued around 0.5-0.6 rather than continuing to fall the way the ResNets' losses did, which points to the from-scratch architecture lacking the capacity or the inductive bias (no ImageNet features) to solve grasp orientation from 620 images, not to a tuning oversight.
- **Two real bugs were caught by review before being reported as results**, both recorded in commit history: an early-stopping rule that let a lucky pre-training epoch become the "best" checkpoint (fixed with a warmup-ineligibility rule and an epoch-40 floor, justified from measured loss-plateau and val-volatility curves rather than from where any model's best epoch happened to land), and a size-loss term so underweighted relative to position that predicted rectangles collapsed toward small near-squares (diagnosed via an 8-image overfit sanity check, then correctly resolved on val rather than on that 8-image result, which pointed the wrong way).

### 10.8 Current status / next step

Sections 4, 5.1, 5.2 and 5.3 are complete. Shared infrastructure (`scripts/cornell_data.py`, `scripts/grasp_metric.py`) has now been reused unchanged across two independently-built systems.

Next is **Section 5.4, System C (vision-language model baseline)**: prompt a pretrained multimodal model directly with the image, parse its output into the same rectangle format, and test consistency across repeated prompts on the same image. Section 6's full three-way comparison (with category and condition breakdowns) follows once System C is done.