**NOTE TO ANISH — read before using this file.** This is a full first draft, written directly rather than as an outline. It follows `paper_writing_framework.md`'s structure, word budgets, and tone rules, and pulls only from the sealed results docs and `research_findings.md`. A few things still need your pass before this goes anywhere near a PDF:

1. **Page numbers in citations are placeholders where I was not able to verify the exact page.** I used the start of the cited page range for journal/conference sources (Jiang, Lenz, Redmon, Kumra, Morrison) since `research_findings.md` itself flags page ranges as lower-confidence and unverified. Check these against the actual PDFs before submitting — this is already item 4 on the framework's verification checklist.
2. **I left out the ViewSpatial-Bench citation (Li et al.) entirely.** Its numbers (34.98% / 26.33%) are marked `[SEARCH-ONLY]` in `research_findings.md` and unconfirmed against the paper's actual results table. The paper doesn't need it to make its argument, so I dropped it rather than cite an unverified figure.
3. **Object groups 26, 56, 230, 231** are referred to only by neutral ID anywhere I needed to reference them, per the framework's instruction not to adopt either unconfirmed guess.
4. This is written in your first person ("I built," "I found") per the framework's tone guidance, since you're the sole author of record. Read it out loud once you've edited it, per the framework's final proofread step.
5. Word counts per section are noted in brackets so you can see how this maps to the 2,800–4,200 word target.

---

# Title

**Where Grasp Prediction Breaks: A Controlled Comparison of Rule-Based, Learned, and Zero-Shot Vision-Language Approaches**

---

# Abstract

*[~230 words]*

Robotic grasping requires deciding where and how to grip an object before any motion happens, and there are fundamentally different ways to make that decision: hand-written rules, models trained specifically for the task, and general-purpose AI systems with no task-specific training at all. This project compares three such approaches, a rule-based baseline, a fine-tuned convolutional network, and a zero-shot vision-language model (VLM), against the same externally-sourced ground truth: the Cornell Grasping Dataset's hand-labeled grasp rectangles, scored on the same held-out, object-wise test split of 123 images. The rule-based baseline reached 57.7% accuracy, the fine-tuned ResNet18 reached 79.7%, and the zero-shot VLM (GPT-4o, five repeats per image) reached a mean of 12.4% per repeat. The gap between the rule-based and learned systems is statistically significant (McNemar's test, p = 1.4e-4), and the VLM trails both so badly that its best-of-five ceiling (35.0%) still sits below the rule-based system's worst-case lower bound (48.9%), a comparison that does not depend on exact point estimates. Stratifying the test set by whether an image's labeled grasps are diagonal or axis-aligned shows the three systems failing in three different directions: the rule-based system loses 21.2 points on diagonal objects, the learned model gains 12.3, and the VLM barely moves. A closer look at the VLM's failures shows the problem is not that it cannot describe where to grasp; its written reasoning is frequently accurate. The problem is that the coordinates it outputs often do not match that reasoning. That distinction matters for how vision-language models get built into robotics pipelines going forward.

---

# Introduction

*[~520 words]*

Before a robotic gripper can pick anything up, something has to decide where on the object to place the fingers, at what angle, and with how much force. That decision can come from a hand-written rule ("mugs get grasped by the handle"), from a model trained specifically to predict grasp points from images, or, increasingly, from a general-purpose AI system that was never trained on grasping at all but can be asked to look at a picture and answer a question about it. These are not small implementation differences. They represent three different bets about where the intelligence in a robotic pipeline should live: in a programmer's rules, in a model's learned weights, or in a foundation model's general reasoning.

This project compares those three approaches directly. It builds a rule-based baseline, a learned grasp predictor, and a zero-shot vision-language model, and scores all three against the same ground truth, on the same held-out images, using the same metric. The research question is simple to state: which approach most accurately predicts a viable grasp point, and where does each one break down?

The dataset and the scoring convention are not new. This project uses the Cornell Grasping Dataset, which represents a grasp as a rectangle defined by a center point, an orientation angle, and a width and height matched to the gripper's mechanical opening (Jiang, Moseson, and Saxena 3304). It also uses the evaluation rule established for that representation: a predicted grasp counts as correct if its orientation is within 30 degrees of a labeled grasp and its intersection-over-union with that grasp exceeds 25% (Lenz, Lee, and Saxena 712). Using the same dataset, representation, and scoring convention as the published literature is what makes these results comparable to prior work rather than a closed system that only makes sense on its own terms.

Three systems are compared. System A is a rule-based baseline: a pretrained object detector identifies the object category, and a fixed lookup table maps that category to a generic grasp region. System B is a learned predictor: a custom convolutional network and a fine-tuned ResNet, trained directly on the Cornell dataset to regress grasp parameters from an image. System C is a zero-shot vision-language model, prompted directly with the raw image and no task-specific training at all, representing what a general-purpose model gets you for free.

This project is not an attempt to beat state-of-the-art grasp detection accuracy, and claiming that would be a mistake this paper does not make. Its aim is narrower and, I think, more useful: to measure, under identical conditions, how three different families of technique fail, and to show that the shape of a system's failure, not just its accuracy number, tells you something real about where that technique belongs in a robotics pipeline.

---

# Methods and discussion

## Data and evaluation

*[~330 words]*

All three systems were evaluated on the Cornell Grasping Dataset, roughly a thousand RGB images of everyday objects with hand-labeled grasp rectangles. The Jacquard Dataset was considered as an alternative or supplement, but its full distribution requires a signed institutional agreement that could not be obtained during this summer research period, so Cornell was used alone. That is a real limitation, not a silent one, and it is worth stating plainly here rather than letting a reader wonder why only one dataset appears.

Cornell ships with no object-identity metadata, which is a problem for an object-wise train/test split, the kind of split where the same physical object never appears in both sets. A naive pixel-difference heuristic between consecutive frames was tried first and rejected: the dataset deliberately rotates the same object across several photos, and rotation and true object changes produced overlapping score distributions that could not be told apart automatically. The working approach segmented each frame using the photography platform's geometry, then scored the segmented regions with rotation-invariant descriptors (color histogram and pixel area) to decide whether two consecutive frames showed the same object or a different one. Thresholds for automatic accept/reject were set asymmetrically rather than at the midpoint between the two score distributions, because the two kinds of mistake are not equally costly: wrongly merging two different objects into one group is low-risk for a downstream split, since the merged group still lands entirely on one side, while wrongly splitting one true object into two groups is high-risk, since the pieces can land in different splits and silently inflate reported accuracy. About 28.4% of frame boundaries fell into an ambiguous band and were reviewed by hand. A first pass came from an AI assistant with a logged confidence per call, checked against an independent, blind sample I classified myself with no visibility into the model's calls. Agreement was 86.7% on the model's confident calls and 40.0% on its uncertain ones, which confirmed the stated confidence was informative and also surfaced a specific reasoning bias worth fixing by hand.

The resulting split has 234 objects and 883 images, divided 620/140/123 across train, validation, and test by object count (Table 1). Published Cornell results typically use five-fold cross-validation across all 885 images; this project used a single frozen split, opened once. That is a real protocol difference from the literature and it is stated here directly rather than left for a reader to catch.

## System A: rule-based baseline

*[~150 words]*

System A runs a COCO-pretrained object detector on each image to get a category label, then maps that category to a fixed grasp region and force level using a small lookup table. The table was written once, before any evaluation was run, and frozen by commit before the first score was ever computed, so nothing in it could be adjusted in response to a result. The qualitative grasp region is converted into a rectangle centered on the detected object, with an orientation drawn from the detector's axis-aligned bounding box.

That design has a specific, predictable weakness built into it: a bounding box only has two possible orientations, 0 and 90 degrees, so any object whose true grasp is diagonal is unreachable by construction, no matter how well the detector localizes it. That is a prediction about where this system should fail, made before looking at the results in the next section, not an explanation invented afterward.

## System B: learned grasp predictor

*[~370 words]*

System B frames grasp prediction as direct regression from an image to five grasp parameters: center position, width, height, and orientation. Orientation is encoded as the sine and cosine of twice the angle, following the convention Redmon and Angelova used for their global regression model and that GG-CNN later adopted for its pixel-wise predictions (Redmon and Angelova 1316; Morrison, Corke, and Leitner). This encoding avoids the seam a raw angle would create at the metric's 180-degree symmetry point, since a grasp and its 180-degree rotation are mechanically identical for a parallel-jaw gripper.

Three architectures were trained and compared: a custom convolutional network built from scratch, a fine-tuned ResNet18, and a fine-tuned ResNet34. ResNet34 has roughly twice the parameters of ResNet18, and I expected going in that its extra capacity would be hard to use well with only 620 training images, the kind of situation where a bigger model tends to overfit rather than generalize better. Architecture selection happened entirely on the validation set, before the test set was opened, specifically to avoid picking whichever model happened to get lucky on the sealed data.

It is worth being precise about which published system System B should actually be compared against. System B's architecture, a backbone feeding pooled features into regression heads that output one grasp rectangle per image, is the same global-regression design Redmon and Angelova used in 2015, not the pixel-wise design used by GG-CNN or GR-ConvNet, which predict a grasp at every pixel of the image in a single pass and are a genuinely different kind of model. Comparing System B's accuracy against GR-ConvNet's reported 97.7% on Cornell (Kumra, Joshi, and Sahin 9626) invites a reading this project cannot support, because the two systems are not doing the same kind of computation. Compared against Redmon and Angelova's Direct Regression result instead, the comparison is architecturally fair: same global-regression design, same sin/cos(2θ) orientation encoding, and every remaining difference between the two setups (their RGB-D input against this project's RGB-only input, their roughly 3,000 augmented training examples per original image against this project's 620 real images total) points in the same direction and explains a gap without appealing to anything unmeasured. Table 2 lays this comparison out directly.

## System C: zero-shot vision-language model

*[~430 words]*

System C prompts GPT-4o directly with each test image, asking it to identify the two points on the object where a gripper's fingertips should make contact, with no task-specific training or fine-tuning of any kind. The model was never asked for an angle directly; the orientation was derived from its two reported contact points using the same corner-to-rectangle conversion function that produced every ground-truth angle in the dataset, which closes off an entire category of silent convention errors (degrees versus radians, clockwise versus counter-clockwise) that would otherwise be indistinguishable from the model simply grasping badly. Each test image was run five independent times, since a language model's output can vary from call to call, and that variation is reported as a result rather than averaged away.

It would be easy to read System C's 12.4% headline number as simply confirming that vision-language models are bad at spatial tasks. That is already well established and would not be an interesting finding on its own. What is more interesting is what almost every published VLM-based grasping system actually does about it: none of them ask the model for raw coordinates. FreeGrasp uses GPT-4o only to decide which object to grasp, a separate specialized module then produces the actual grasp geometry (Jiao et al.). VLAD-Grasp has the model generate a goal image with a virtual gripper drawn into it, encoding the grasp pictorially instead of numerically (Kulshrestha et al.). Set-of-Mark prompting replaces raw coordinate output with a choice among a small set of labeled, pre-segmented regions, and reports that doing so lets zero-shot GPT-4V outperform a fine-tuned referring-expression model (Yang et al.). Each of these designs quietly encodes the same assumption: that a vision-language model cannot be trusted with raw numeric coordinates. As far as I could find, that assumption is stated and worked around, but not actually measured on a standard grasping benchmark against non-VLM baselines. System C is that measurement.

Looking at what actually went wrong helps explain why. Of System C's 615 calls, 365 (59.3%) failed both the angle and overlap criteria at once, a much larger share than either single-axis failure type. A closer, purely geometric check on the same frozen predictions found that on 53.4% of calls, the predicted grasp center fell entirely outside the convex hull of every labeled grasp on that image, a rate roughly eight times higher than either System A's or System B's (7.0% and 6.5%). Reading the model's own reasoning text next to its coordinates on a sample of these failures showed a specific pattern: the reasoning often named a real, correct part of the object, while the coordinates in the same reply landed somewhere else entirely. That is not a perception failure so much as a binding failure between two output channels in the same response, and it has independent support outside this project. A recent evaluation of multimodal models solving CAPTCHAs found the identical pattern in a completely different task: a model correctly described the path it traced to a target, then clicked more than 700 pixels away from it (Wang et al.). Seeing the same disconnect between stated reasoning and emitted coordinates, in a different task, on a different model, is not proof that this is a general property of vision-language models, but it is real, independent corroboration that the failure mode this project measured is not unique to this prompt or this dataset.

## Cross-system interpretation: the orientation axis

*[~340 words]*

Each system's design makes a different, specific prediction about how it should respond to grasp orientation. System A should fail on diagonal objects, because its bounding-box orientation can only ever be 0 or 90 degrees. System B should handle rotation cleanly, because its sin/cos(2θ) encoding has no seam at any angle. System C has no structural handling of orientation either way, so its response is genuinely open.

Splitting the test set by whether an image's labeled grasps are diagonal (more than 15 degrees from axis-aligned) or not shows exactly this pattern. On the 20 diagonal images, System A drops 21.2 points relative to the axis-aligned images, System B gains 12.3 points, and System C moves only 2.0 points. Three systems, three different directions, on the same 20 images.

Stratifying results by ground-truth orientation is not itself a new fact about grasping; that axis-aligned representations cannot capture diagonal grasps, and that rotation-aware encodings can, are both already established in the literature this project draws on. What I could not find precedent for is using that stratification as a diagnostic instrument, a shared, externally-sourced axis that separates three technique families by which direction they move on it, rather than reporting the usual image-wise or object-wise generalization splits. I am presenting this as a method other researchers could reuse cheaply on their own results, not as a discovered fact about grasping, and the sample size here, 20 diagonal images, means each system's individual number is weak evidence on its own. What is not weak is that all three moved in three distinguishable directions on one split; that pattern is harder to produce by chance than any single cell in the table is.

System C's flat 2.0-point move on this axis is not an isolated number. It agrees with the compound-failure result from the previous section by an entirely different route: a system with no working orientation signal at all should look flat on an orientation-stratified split, and that is what System C looks like here. Two unrelated measurements landing on the same explanation is stronger evidence for that explanation than either one is by itself.

A second condition axis, the number of grasps labeled per image, was also tested as a rough difficulty proxy. It did not behave as expected: all three systems scored worse on images with the most labeled grasps rather than the fewest, even though more labeled grasps should make a prediction easier to match. The likely reason is that annotators labeled more grasps on objects that genuinely afford more of them (long, thin, multi-part objects), so the count tracks object complexity more than it tracks how forgiving the metric is. This is reported because it was measured, not because it supports the paper's argument, and it is not used to claim anything further.

## Discussion

*[~380 words]*

The coordinate-binding explanation for System C's failure makes a prediction that can, in principle, be tested directly: if the problem is binding a model's reasoning to the numbers it emits, rather than a failure of visual perception itself, then interventions that remove the need to emit raw numbers should help disproportionately, while interventions aimed only at sharpening perception should not. The existing literature is consistent with that prediction without ever framing it that way. Set-of-Mark prompting, which replaces coordinate emission with selecting a labeled region, substantially improves zero-shot grounding (Yang et al.). VLAD-Grasp sidesteps the problem by having the model draw a picture instead of state numbers (Kulshrestha et al.). FreeGrasp avoids it entirely by never asking the model for geometry in the first place (Jiao et al.). None of these were built to test this exact prediction, so this project does not claim to have tested it either, but the pattern across all three is worth naming directly.

It is worth being plain about what in this project is and is not new. The sin/cos(2θ) orientation encoding is standard practice going back to 2015 and is not a contribution of this work. That vision-language models struggle to produce precise coordinates is an established phenomenon, not a discovery made here. What this project adds is a controlled measurement of that phenomenon, on a standard benchmark, under a standard metric, against two non-VLM baselines scored on the identical images, together with independent cross-domain evidence for the specific mechanism behind it. A paper that oversold either of these points would lose more credibility on the parts that are genuinely earned, so I would rather state this plainly than gesture at more than the results support.

One more thing is worth naming, because it is part of how these numbers were produced and not just a footnote. Three separate implementation bugs were caught and fixed before they reached a reported result: an early object-grouping heuristic that was rejected after direct inspection showed it could not actually separate same-object from different-object frames, an early-stopping rule in System B's training that would have let a lucky, undertrained checkpoint get reported as the best one, and a text-encoding bug in a contamination check for System C that silently broke a negation test. None of the three was caught by an outside reviewer, and none looked obviously wrong before it was checked. A fourth check, on whether System C's predicted grasp centers actually land near any labeled grasp, caught a coordinate-frame mismatch in its own first run before that number was trusted either. The most direct future step this project's findings point to is testing Set-of-Mark prompting on System C specifically, since it is the intervention the coordinate-binding diagnosis predicts should help. I did not run it. Given the timeline for this project, identifying the right next experiment and scoping it clearly is a more honest place to stop than a rushed version of it would have been.

## Limitations

*[~250 words]*

This project has several limitations worth stating together rather than scattered across sections. The train/validation/test split is a single frozen object-wise split, opened once, rather than the five-fold cross-validation most published Cornell results use; the two protocols are not directly equivalent, even though they are scored with the same metric. The Jacquard Dataset, which would have let System B's generalization be tested on a second dataset, was unavailable during this project because its full distribution requires a signed institutional agreement that could not be obtained over the summer. An early verification step, checking roughly 550 grasp rectangles for correct formatting, likely touched a small number of images that later ended up in the test split; no lookup table, threshold, or frozen constant was ever derived from that check, but it is disclosed here for completeness.

System C's contamination risk deserves its own sentence: Cornell is a public, widely mirrored dataset, and GPT-4o could plausibly have seen it during training. A ten-image probe that asked the model to name the source dataset, without revealing the actual task, came back with zero recognitions, which is a mild, non-decisive signal rather than a clearance. Any contamination could only inflate System C's reported accuracy, never deflate it, so this project's conclusion that System C trails badly holds up even under the least favorable assumption. The orientation-stratified finding rests on only 20 diagonal images, which is enough to see a direction but not enough to claim a precise magnitude. Finally, System C's coordinate-binding finding describes one model, one frozen prompt, and one elicitation method; it is not a general claim about all vision-language models or every way of prompting one.

---

# Results

*[~640 words]*

## Data split

The final object-wise split contains 234 objects across 883 images (Table 1). No object appears in more than one split; this was verified twice, once during construction and once by an independent re-read of the final assignment file.

**Table 1. Object-wise train/validation/test split.**

| Split | Objects | Images |
|---|---|---|
| Train | 164 | 620 |
| Validation | 35 | 140 |
| Test | 35 | 123 |
| Total | 234 | 883 |

## System A

System A reached 57.7% accuracy on the test set (71 of 123 images), with a 95% Wilson confidence interval of [48.9%, 66.1%]. Of its 52 failures, 13 (25.0%) failed on orientation alone, meaning the predicted rectangle overlapped the correct region well enough but was rotated more than 30 degrees away from any labeled grasp. That matches the prediction made in Methods: a system whose orientation can only take two values should fail specifically on objects that need a diagonal grasp.

## System B

Table 2 compares all three trained architectures. ResNet18, the architecture selected on the validation set before the test set was opened, reached 79.7% accuracy (98 of 123 images), 95% confidence interval [71.7%, 85.8%], with a mean angle error of 3.9 degrees on its correct predictions. ResNet34 reached 70.7% (87 of 123), and the from-scratch custom CNN reached 23.6% (29 of 123). The custom CNN's training loss plateaued well above the ResNets' and never resumed falling, consistent with the expectation stated in Methods that 620 images is not enough data for a from-scratch network without ImageNet features to solve this task well.

**Table 2. System B compared with a matched published architecture.**

| | Redmon and Angelova (2015) | System B (ResNet18) |
|---|---|---|
| Architecture | Global regression | Global regression |
| Orientation encoding | sin/cos(2θ) | sin/cos(2θ) |
| Input | RGB-D | RGB only |
| Training data | ~3,000 augmented examples per image | 620 real images |
| Object-wise accuracy | 84.9% | 79.7% |

## System C

System C's mean per-repeat accuracy across five independent runs was 12.4% (76 of 615 calls), 95% confidence interval [10.0%, 15.2%], with individual repeat accuracies ranging from 9.8% to 14.6%. Its best-of-five ceiling, the accuracy if an oracle always picked the correct repeat when at least one existed, was 35.0% (43 of 123); its majority-consensus accuracy, scoring only cases where at least three of five repeats agreed and that agreed answer was correct, was 12.2%. Neither of these is the headline number. The model successfully returned a parseable coordinate pair on 614 of 615 calls (99.8%).

Table 3 gives the failure taxonomy computed identically for all three systems, using the same scoring code path for every column.

**Table 3. Failure taxonomy by criterion missed (angle only, overlap only, or both).**

| Outcome | System A (of 123) | System B (of 123) | System C (of 615) |
|---|---|---|---|
| Correct | 71 (57.7%) | 98 (79.7%) | 76 (12.4%) |
| Angle only | 13 (10.6%) | 4 (3.3%) | 85 (13.8%) |
| Overlap only | 18 (14.6%) | 15 (12.2%) | 88 (14.3%) |
| Both | 13 (10.6%) | 6 (4.9%) | 365 (59.3%) |
| No prediction | 8 (6.5%) | 0 (0.0%) | 1 (0.2%) |

System A's and System B's failure signatures invert (mostly angle-only for A, mostly overlap-only for B), while System C's dominant failure mode is the compound bucket, more than half of all its calls, which neither of the other systems shows.

## Cross-system comparison and orientation stratification

System A versus System B is a statistically significant difference (McNemar's exact test, p = 1.4e-4, 11 versus 38 discordant pairs). System C was compared against both A and B separately for each of its five repeats, and the largest (least significant) of those five p-values is reported: A versus C, p = 5e-12; B versus C, p = 1.6e-20. Stated at its most conservative, System C's best-of-five ceiling (35.0%, upper 95% bound 43.7%) sits below System A's single-call lower 95% bound (48.9%); these intervals do not overlap.

Table 4 gives the orientation-stratified breakdown described in the Discussion section. On the 20 diagonal-grasp images, System A drops 21.2 points relative to axis-aligned images, System B gains 12.3 points, and System C moves 2.0 points.

**Table 4. Accuracy stratified by whether an image's labeled grasps are diagonal.**

| Stratum | Images | System A | System B | System C |
|---|---|---|---|---|
| Axis-aligned | 103 | 61.2% | 77.7% | 12.0% |
| Diagonal | 20 | 40.0% | 90.0% | 14.0% |

The grasps-per-image axis, reported without further interpretation, showed all three systems scoring worst on images with the most labeled grasps (8 to 25 grasps) rather than the fewest, contradicting the premise that more labeled grasps should make a prediction easier to match.

---

# Conclusion

*[~190 words]*

This project set out to answer a specific question: given the same dataset, the same ground truth, and the same scoring rule, which of three fundamentally different approaches to grasp prediction actually works, and where does each one break down. The rule-based baseline reached 57.7%, the fine-tuned ResNet18 reached 79.7%, a statistically significant improvement, and the zero-shot vision-language model reached 12.4%, trailing both so badly that even its most favorable possible reading does not overlap with the rule-based system's worst case. But the accuracy numbers alone understate what these results show. Stratifying by grasp orientation reveals three systems failing in three distinguishable, mechanistically different ways: an axis-aligned rule that cannot represent diagonal grasps, a learned model that handles rotation but still occasionally mislocates the object, and a language model whose stated reasoning and emitted coordinates come apart entirely on more than half of its attempts. That last finding, that a vision-language model's failure here looks like a binding problem rather than a perception problem, points to a specific, testable next step: prompting the same model with Set-of-Mark grounding instead of raw coordinates, replacing the exact channel this project identified as the point of failure, is the most direct way to find out whether that diagnosis is right.

---

# Works Cited

Jiang, Yun, Stephen Moseson, and Ashutosh Saxena. "Efficient Grasping from RGBD Images: Learning Using a New Rectangle Representation." *2011 IEEE International Conference on Robotics and Automation (ICRA)*, IEEE, 2011, pp. 3304-11.

Jiao, Runyu, et al. "Free-Form Language-Based Robotic Reasoning and Grasping." *arXiv*, 2025, arxiv.org/abs/2503.13082.

Kulshrestha, Manav, et al. "VLAD-Grasp: Zero-Shot Grasp Detection via Vision-Language Models." *arXiv*, 2025, arxiv.org/abs/2511.05791.

Kumra, Sulabh, Shirin Joshi, and Ferat Sahin. "Antipodal Robotic Grasping Using Generative Residual Convolutional Neural Network." *2020 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)*, IEEE, 2020, pp. 9626-33.

Lenz, Ian, Honglak Lee, and Ashutosh Saxena. "Deep Learning for Detecting Robotic Grasps." *The International Journal of Robotics Research*, vol. 34, no. 4-5, 2015, pp. 705-24.

Morrison, Douglas, Peter Corke, and Jurgen Leitner. "Closing the Loop for Robotic Grasping: A Real-Time, Generative Grasp Synthesis Approach." *Robotics: Science and Systems XIV*, 2018.

Redmon, Joseph, and Anelia Angelova. "Real-Time Grasp Detection Using Convolutional Neural Networks." *2015 IEEE International Conference on Robotics and Automation (ICRA)*, IEEE, 2015, pp. 1316-22.

Wang, Junyu, et al. "COGNITION: From Evaluation to Defense against Multimodal LLM CAPTCHA Solvers." *arXiv*, 2 Dec. 2025, arxiv.org/abs/2512.02318.

Yang, Jianwei, et al. "Set-of-Mark Prompting Unleashes Extraordinary Visual Grounding in GPT-4V." *arXiv*, 17 Oct. 2023, arxiv.org/abs/2310.11441.
