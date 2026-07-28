# Vision-Informed Grasp Decision Prediction — Source of Truth

## Sub-project of: Adaptive Robotic Grasping Through Vision-Informed Grip Decisions, Multi-Signal Slip Detection, and Real-Time Recovery

Researcher: Pranav Nair (high school senior research, ISEF/RSEF level)
Status: Summer work phase, no physical hardware available yet (gripper build happens in fall)
Purpose of this file: this is the current, authoritative plan for the summer sub-project. It replaces the earlier single-model version of this document. Anyone (human or AI) picking up this work should treat this file as the plan to follow, not the earlier draft.

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