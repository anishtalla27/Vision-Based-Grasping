# DRAFT v2, working notes before the paper starts

**What this file is.** A complete draft of the NextGen Scholars submission, written through the ARS `academic-paper` skill against `paper_writing_framework.md`, then revised against the 5-reviewer panel report in `paper_review_v2.md`, then rescaled to the expanded word budget. Everything below the horizontal rule is paper content. Everything above it is scaffolding and should not be submitted.

**Nothing sealed was touched.** This read `source_of_truth.md`, the three `system_*_results.md` files, `comparison_results.md`, `center_containment_analysis.md`, and `research_findings.md`, and modified none of them. No system was re-run and no number recomputed. `paper_draft.md` is untouched.

**Plugin deviation, recorded once.** The ARS skill requires a Data Availability Statement, Ethics Declaration, CRediT, COI, and Funding Acknowledgment in every paper. All five are omitted per your decision, since the competition specifies six sections and none of these are among them.

## Revision panel fixes applied

| Roadmap item | What changed |
|---|---|
| 1. "Channel not model" overclaimed | Softened in Abstract, Discussion, and Conclusion. The VLAD-Grasp contrast now states that the two systems differ in more than elicitation. |
| 2. Motive attributed to four papers | Removed. The five systems are described by what they do, and the paper explicitly declines to infer why. |
| 3. System A framing | Detector coverage and the segmentation fallback are disclosed in the Introduction and System A method, not left to surface in Results. |
| 4. Engineering-effort asymmetry | Added to Limitations. It was the panel's strongest counter-argument. |
| 5. Interpretation in Results | Moved to Methods/Discussion. |
| 6. Uncited 84.9% | Citation added at point of use. |
| 7. Orphaned "ten images" line | Connected to the difficulty-floor point. |
| 8. Multiple labeled grasps | Stated in the Introduction where the metric is defined. |
| 9. Center-containment not like-for-like | Qualifying clause added. |
| 10. Table 4 confidence intervals | Added. |

## Citation verification results

All 11 sources were checked against the actual paper before being cited.

| Item | Result |
|---|---|
| COGNITION passage | **Confirmed, with three corrections.** It is in §5.3.2, "Spatial Grounding Failures," not appendix A.3.2/A.3.3. The phrase "solves the puzzle in words" is verbatim but `research_findings.md` merged it with a second sentence. The 700-pixel example is exact but the model is **GPT-5 on path tracing**, which the draft states. The "(400, 690) versus (305, 520)" example in the notes does not exist and is not used. |
| ViewSpatial-Bench | **Not verifiable. Dropped.** |
| VLAD-Grasp motivation | **Refuted.** Motivated by dataset curation cost, not VLM numeric weakness. Method cited, motivation never. |
| GraspMAS / ThinkGrasp / SegGrasp / Lan-grasp | **Two of four confirmed.** ThinkGrasp (Qian et al.) and Lan-grasp (Mirjalili et al.) verified with full author lists. GraspMAS and SegGrasp **dropped**. |
| Page ranges | **All confirmed.** Jiang 3304-11, Lenz 705-24, Redmon 1316-22, Kumra 9626-33. Morrison is RSS 2018 and has no page numbers. |

## Second verification pass, numbers rather than citations

Checked directly against source after the panel round, because the first pass verified that sources exist and say what is attributed to them, not that their reported figures were being compared on equal terms.

| Item | Result |
|---|---|
| Redmon and Angelova, 84.9% | **Confirmed and correctly labeled.** Table "Rectangle Metric Detection Accuracy" gives Direct Regression 84.4% image-wise, **84.9% object-wise**. The object-wise figure is the one used here, which is the right one for comparison against this paper's object-wise split. |
| Redmon metric | **Confirmed identical to this paper's.** Sec. 5.1 defines the rectangle metric as angle within 30 degrees AND Jaccard above 25%. Five-fold cross-validation, RGB-D. |
| Redmon, ~3,000 augmented examples | **Confirmed verbatim.** Sec. 5.5: "We generate 3000 training examples per original image." |
| GR-ConvNet, 97.7% | **Confirmed but was mislabeled here.** 97.7% is the **image-wise** figure; object-wise is 96.6% (sec. 7.1, RGB-D). Both now stated, since this paper is framed object-wise throughout. |
| **VLAD-Grasp, metric and number** | **Real problem, now fixed.** Its Cornell figure is 91.43%, and its table caption defines success as IoU above 25% against at least one annotation, **with no angle criterion at all**. That is strictly looser than the 30-degree-plus-25% metric used throughout this paper, and the omitted criterion is orientation, which is this paper's central axis. Its evaluation also covers 70 unseen Cornell objects and reports per-object rates with very large standard deviations. Decisive evidence the protocols differ: **the same table scores GR-ConvNet at 72.14%, against the 97.7% GR-ConvNet reports for itself.** The draft previously implied a like-for-like contrast with System C's 12.4%. All three mentions (Abstract, Discussion, Conclusion) now state that the comparison is directional only. |
| Seven single-image object groups | **Confirmed against `final_split.csv`.** Test split group-size histogram: seven groups of 1, six of 2, three of 3, thirteen of 4, two of 5, three of 8, one of 9. Totals 35 groups and 123 images. Added to Limitations. |
| "Roughly eight times" (Abstract) | **Fair rounding, left alone.** 53.4/7.0 = 7.6 and 53.4/6.5 = 8.2; "roughly eight times" covers both, and the body already qualifies the comparison as not like-for-like. |
| Interpretation in Results | **Already clean.** The System A Results paragraph reports coverage, detector-only accuracy, and per-category counts with no interpretive clause; the "why" sits in the System A method subsection. No change needed. |
| Keywords line | **Removed.** MLA has no keywords block, and `paper_writing_framework.md` never asks for one. It was an artifact of the plugin's journal defaults. |

## Third pass, claim discipline

| Item | Result |
|---|---|
| "Harder to produce by chance" | **Real problem, removed.** No test of the joint three-way pattern against a null was ever run, so the sentence made a probability claim with no null behind it. Replaced with an explicit statement that no such test exists, plus the one defense that does hold: System A's drop was predicted from its representation before the stratum was scored, so that cell is a confirmed prediction while the other two are exploratory. |
| "Not one anyone builds on" | **Overreach, narrowed.** Proving nobody does something is not possible from a literature search. Now reads as a search-bounded claim, matching the safer phrasing already used later in the same sentence. |
| "Four bugs" | **Real inconsistency, corrected to three.** `comparison_results.md` names exactly three self-caught bugs, then describes a fourth item and explicitly declines to count it: "a reuse hazard in a shared function's return signature rather than a caught bug, and it is recorded as such rather than inflated." The draft had inflated precisely what the sealed record refused to inflate. All three are now named. |
| Object-grouping validation | **Was too vague, now specific.** Counts pulled from `boundary_decisions.csv` (884 boundaries) and `review_tracking.csv` (251 in the ambiguous band, of which 139 decided by hand and 112 auto-accepted). Blind stratified validation sample was 30 boundaries (`validation_sample.csv`), oversampled toward uncertain calls. Methods now states the review policy and who decided what; Results carries the counts. |
| Resource/cost claims | **Unverifiable specifics removed.** "Months to annotate" and "takes an afternoon" were estimates I cannot source. Replaced with what is actually known: hand-specified rules, versus a task-specific annotated dataset plus compute, versus an API key. |
| Abstract ending | **Made explicit.** "The useful lesson sits in that contrast" asked the reader to infer the contribution. Now states it, scoped to what the paper establishes. |
| "Reasoning" | **Softened at the load-bearing points.** The model's text is observable output and may not reflect any internal process. Abstract, the binding paragraph, and the Conclusion now say "written explanation" and "emitted numbers," with one sentence making the distinction explicit. |
| Conclusion echoing the Abstract | **Restructured.** It now opens on the implication and treats the three accuracies as stage-setting, instead of repeating the Abstract's order. |
| "Worst-case lower bound" | **Fixed in both places.** A confidence-interval bound is not a worst case; now "lower 95% confidence bound." |
| Center containment | **Now explained.** Labeled a supplementary diagnostic outside the Cornell metric, with the point that the hull is the loosest spatial test a prediction can fail. |
| 59.3% vs 59.4% | **Not an issue.** `comparison_results.md` reports 59.3% and the paper matches. The 59.4% appears only in the handoff note, which is not a sealed source. |
| Title | **Kept.** Reviewer rated the current title acceptable, and it names the finding rather than the project. |

## Fourth pass, System A coverage and MLA

| Item | Result |
|---|---|
| **Does the orientation prediction cover all of System A?** | **Checked in code and data. It does, and the paper now says so.** `system_a_run.py` sends the fallback through `mask_bbox()`, an axis-aligned box of the segmentation mask, into the same `predict_rect()` the detector path uses, and `system_a_lookup.py` line 222 sets `theta = 90.0 if horizontal else 0.0`. Confirmed empirically against `system_a_predictions.csv`: all 115 predictions are exactly 0 or 90, split 49 detector (25/24) and 66 fallback (33/33). So the pre-registered prediction was never resting on a minority path, but the draft had not stated it. One sentence added. |
| System A freeze claim vs Amendment 1 | **Valid sequencing problem, fixed.** The strong freeze claim appeared in Methods and the qualifying amendment roughly 1,500 words later in Results. The amendment is now disclosed in the System A method immediately after the freeze claim, matching how detector coverage was handled. |
| **MLA 9 author rule** | **Real error, four entries fixed.** MLA 9 uses "et al." for **three or more** authors, not four. `paper_writing_framework.md` §3.8a stated the MLA 7 rule ("two or three authors: name all of them"), which is why the draft listed three-author sources in full. Corrected in Works Cited (Jiang, Kumra, Lenz, Morrison) and at all six in-text sites. The framework has been corrected too, with a note that older online guidance shows the pre-MLA-8 form. |
| Abstract carrying two findings | **Agreed, orientation demoted.** It is the weaker result: n = 20, and System B's diagonal interval [69.9, 97.2] overlaps its axis-aligned interval [68.7, 84.6] almost entirely. Compressed to a clause that now states the n, so the abstract builds toward the binding finding, which is what the Discussion and Conclusion actually rest on. The body keeps both in full. |
| Interpretive clauses in Results | **Two cut.** "The set where the learned model's contribution is visible" and "the closest thing this test set has to a difficulty floor" were interpretation; the A-only/B-only counts (11 and 38) replace them with numbers. "This axis supports no claim in this paper" also cut, since the sentence before it already reports the contradiction. |
| Repeated constructions | **Varied.** Two "I want to be careful" openings, one rewritten. Of six "worth X-ing" instances, three changed. |
| Framework length contradictions | **Fixed.** §3.2, §3.3, and §3.7 carried the old pre-rescale targets (150-250, 400-600, 150-250) that contradicted §5. All three now match §5 and point to it as authoritative. |
| Title hedging on "Rule-Based" | **Left as is.** System A is a hybrid, but the Introduction and the System A method both correct this within the first page, and the honest alternatives are clumsy. |

## Fifth pass, small corrections

All five verified against code or sealed data. All five were real.

| Item | Result |
|---|---|
| System B's "about four degrees" | **Was conditioned and unstated, now qualified.** `system_b_results.md` reports mean angle error 3.9 degrees on **correct predictions only**, which the Results section already says. The Conclusion dropped that condition. Now reads "to within about four degrees when it succeeds." |
| Guard wording mismatch | **Methods was the imprecise one, corrected.** `system_a_lookup.py:154` defines `detection_on_object` as rejecting "a box that does not contain the segmented object's **centroid**." Results already said centroid; Methods said "the segmented object." Methods now matches the code. |
| Note buried inside Figure 2's caption | **Moved out.** The pcd0676/0348/0824/0316 sheet-availability note sat after "Caption below:" and would have been typeset as part of the caption. It is now a separately labeled source note, with the caption text on its own line. Figures 1 and 3 were checked and carry no embedded notes. |
| "Worth X-ing" clustering | **Two more changed.** "Worth knowing too" and "a prediction worth testing" are gone. One instance remains in the Conclusion and one in Methods, far apart. |
| Orphaned five-attempts clause | **Dropped.** The sentence already opens with "Counting System C as correct if any of its five repeats passed," so the trailing clause repeated the condition without the difficulty-floor framing that once justified it. |

**Still to do before submission:** confirm object groups 26, 56, 230, 231 visually if you name any object; US-English spelling pass; MLA formatting in a word processor; read aloud once.

**Word count:** 5,875 words of body text, inside the 4,500-6,000 target. Four of the five top-level sections are in band; Methods and discussion runs 39 words over its 3,200 cap, about 1.2%. I stopped trimming there rather than cut material the reviewer panel flagged as load-bearing. Placeholders, tables, and this note excluded.

---

# Three Ways to Miss a Grasp: A Controlled Comparison of Rule-Based, Learned, and Zero-Shot Vision-Language Prediction

> **[MLA-FORMAT]** Before export: MLA header block at top left of page 1 (name, mentor, competition, date), title centered in plain 12pt Times New Roman with no bold or italic, page numbers upper right as "Talla N", double spacing throughout including Works Cited, 1-inch margins, hanging indents on Works Cited entries. Delete this note and all scaffolding above it.

## Abstract

A robot cannot pick anything up until something decides where on the object to place the fingers and at what angle. That decision can come from a hand-written rule, from a model trained to predict grasps from images, or from a general-purpose vision-language model never trained on grasping at all. I built one system of each kind and scored all three against the same external answer key, the Cornell Grasping Dataset's hand-labeled grasp rectangles, on one held-out split of 123 images covering 35 objects that appear nowhere in training. The rule-based system reached 57.7%, the fine-tuned ResNet18 reached 79.7%, and zero-shot GPT-4o reached 12.4% averaged over five runs per image. The first gap is significant under McNemar's exact test, and the vision-language model trails so far that even its best-of-five ceiling of 35.0% sits below the rule-based system's lower 95% confidence bound of 48.9%. The ranking is not the interesting part. Stratifying by whether an image's labeled grasps run diagonally moves the three systems in three different directions rather than by different amounts, though on only 20 images, and the vision-language model is the one that barely responds. Its failures say why. Its written explanation frequently named the correct part of the object while the coordinates in the same reply landed nowhere near it, and on 53.4% of calls the predicted center fell outside the region holding every labeled grasp, roughly eight times either other system's rate. A published system using the same model class, zero-shot, on this same dataset does far better while never asking for a coordinate, though under a looser success test than mine. Together these point at free-text coordinate emission, rather than visual recognition, as the binding constraint when a general-purpose model is asked to predict grasps.

## Introduction

Before a gripper closes on anything, something has to choose a contact point, an approach angle, and how wide to open the fingers. Every piece of motion that follows depends on that choice being roughly right. A robot arm can be mechanically excellent and still fail constantly if the thing telling it where to grip is wrong, which makes grasp prediction one of the places where a small accuracy difference turns into a large behavioral difference. It is also a problem that has to be solved from thin information. In most real settings a robot gets a camera image and little else: no model of the object, no label saying what it is, no annotation marking the handle.

There are three broadly different ways to make that decision, and they are not variations on a single method. A programmer can write the rule directly, saying that mugs get grasped by the handle and bottles around the neck. A model can be trained on thousands of hand-labeled examples until it learns to map pixels to grasp rectangles. Or a general-purpose vision-language model, trained on web text and images and never shown a grasping dataset, can simply be asked in plain language where to grip. Each is a bet about where the useful intelligence in a robot's perception stack should live: in a person's explicit rules, in weights fitted to task-specific data, or in a large model's general knowledge of the world.

That third option is new enough that the field has not settled how to use it. Foundation models arrived in robotics quickly, and the literature is still working out which parts of a manipulation pipeline they should own. The question matters practically, because the three approaches demand very different resources. A lookup table needs only hand-specified rules. A learned predictor needs a task-specific annotated dataset and the compute to train on it. Prompting a hosted vision-language model needs an API key and almost no setup, which is exactly why it is tempting, and exactly why it deserves to be measured rather than assumed.

Comparisons across those three families are rarer than you might expect. Most published grasp-detection work benchmarks within a family, comparing one trained architecture against another on the same dataset. That produces useful leaderboards but does not tell you what you gain or give up by changing approach entirely. Rule-based baselines, when they appear, are often described rather than scored. Vision-language models usually appear embedded inside a larger system, where their individual contribution cannot be isolated. I wanted a comparison where all three sat on the same test images, produced the same kind of output, and were scored by the same code.

This project is that comparison, and the question is plain: which approach actually works, and where does each one break down? I care about the second half at least as much as the first. An accuracy number tells you a system is wrong. The shape of its errors tells you why, and that is the part that transfers to whatever somebody builds next.

The measuring apparatus is borrowed rather than invented, which matters more than it might seem. A grasp here is a rectangle with a center point, an orientation, and a width matched to how far the gripper opens, the representation Jiang et al. introduced with the Cornell Grasping Dataset (3304). Each image carries several labeled grasps rather than one, since most objects can be picked up in more than one valid way, and a prediction counts as correct if it matches any of them. The matching rule is that the predicted angle falls within 30 degrees of a labeled grasp and the intersection over union between the two rectangles exceeds 25%, the convention established by Lenz et al. (712). I chose an external answer key deliberately. An earlier design would have had me write the ground truth myself and then grade my own rule-based system against it, which is close to circular. The dataset's existing annotations remove that problem and make my numbers comparable to published ones.

The three systems are as follows. System A is the rule-based baseline: a COCO-pretrained detector identifies the object, and a small fixed table maps the detected category to a grasp region. In practice the detector recognizes fewer than half the images, since Cornell photographs many objects COCO has no category for, so a geometric fallback that segments the object against the photography platform covers the rest. System B is the learned predictor, a small convolutional network built from scratch alongside fine-tuned ResNet18 and ResNet34 models, trained on the Cornell training split. System C is GPT-4o, prompted directly with the raw image and given no task-specific training whatsoever.

I want to be clear about what this paper is not. It does not beat state-of-the-art grasp detection and does not try to. Published pixel-wise systems reach accuracies I am not competing with, and pretending otherwise would be an easy way to lose a reader early. What this paper does is measure, under identical conditions, how three families of technique fail, and argue that the shape of each failure carries information the accuracy number does not. That argument turns out to matter most for the system that scored worst, which is not where I expected to end up.

## Methods and discussion

### Dataset and evaluation

Every system was evaluated on the Cornell Grasping Dataset, roughly a thousand photographs of household objects with hand-labeled grasp rectangles. I looked into Jacquard as a second source, since training on one dataset and testing on another is the cleanest generalization check available, but its full distribution requires a signed institutional agreement I could not obtain over the summer.

Cornell ships no object identity metadata, and that became the hardest methodological problem in the project. The split I needed was object-wise, meaning no physical object may appear in both training and test. An image-wise split lets a model memorize one stapler from six angles and then rewards it for recognizing that same stapler at test time, inflating every number afterward. With no object labels to group by, identity had to be reconstructed from the image sequence.

My first attempt compared consecutive frames by raw pixel difference. It failed because the dataset deliberately rotates each object between shots, so same-object and different-object scores overlapped almost completely and no threshold separated them. The approach that worked segmented each frame using the geometry of the photography platform, since the object appears as a gap in an otherwise uniform surface, then compared those regions with descriptors that ignore rotation, color histogram and pixel area.

Acceptance thresholds were set asymmetrically, because the two mistakes are not equally costly. Merging two different objects into one group is nearly harmless, since the merged group still lands entirely on one side of the split. Splitting one real object into two is dangerous, because the halves can land on opposite sides and every accuracy number quietly inflates. So the automatic "different object" threshold went below the lowest score seen for any confirmed same-object pair, while the "same object" threshold stayed loose.

The ambiguous band was reviewed in two layers. An AI assistant made a first pass over each boundary, logging a confidence level per decision. I then classified a 30-boundary stratified sample myself, blind to its calls and oversampled toward the ones it marked uncertain. We agreed on 86.7% of its confident calls and 40.0% of its uncertain ones. That gap set the review policy, since it showed the stated confidence carried real information. I personally decided every uncertain call, every confident "different" call, and every call whose stated basis matched an error the sample had exposed. Confident "same" calls not caught by those rules were accepted unreviewed, since an error in that direction is harmless by construction.

The result is 234 objects across 883 images, split 620 for training, 140 for validation, and 123 for test. One protocol difference needs stating: most published Cornell results use five-fold cross-validation over all 885 images, while I used a single frozen split opened once. Those are not the same experiment even under the same metric.

### System A, rule-based baseline

System A detects an object with a COCO-pretrained detector, looks the category up in a fixed table, and converts the result into a rectangle centered on the object, oriented from the box. The table was committed before any evaluation code existed, so no entry could be tuned toward a score. That was enforced structurally, not by good intentions. One qualification belongs here rather than in Results. After the first evaluation returned 40.7%, I found the detector was frequently boxing background clutter, added a guard requiring the box to contain the segmented object's centroid, and recalibrated one width constant on training only. No lookup entry changed, and both numbers stay on record.

Something else changes how the headline should be read. COCO's 80 categories do not cover most of what Cornell photographs, so the detector produces nothing on more than half the test images. Those fall through to a geometric fallback, the platform-segmentation routine written for the split, which locates the object without knowing what it is. System A is a hybrid: a category rule where the detector fires, a category-free geometric estimate where it does not. Calling it rule-based is fair since nothing is learned from grasp labels, but the lookup table is not doing most of the work.

One limitation follows from the design before any measurement. Both paths hand an axis-aligned box to the same orientation rule, which can only emit 0 or 90 degrees, so a diagonal object is unreachable however well the box is placed. That covers the whole system rather than the detector's share of it: every one of System A's 115 predictions is 0 or 90 degrees. It is a prediction from the representation, not an explanation invented afterward.

### System B, learned grasp predictor

System B regresses a grasp rectangle directly from an image: a backbone produces features, those features are pooled, and regression heads emit the rectangle's parameters. Orientation is encoded not as a raw angle but as the sine and cosine of twice the angle. The reason is that a parallel-jaw gripper rotated 180 degrees is mechanically identical, so the metric treats orientation as symmetric across half a turn. Regressing a raw angle would make two grasps two degrees apart look 178 degrees apart whenever they straddle the wraparound point, punishing the model for being right. Redmon and Angelova introduced this encoding for grasp regression (1316), and Morrison et al. later used it in GG-CNN.

I trained three architectures: a small network built from scratch, a fine-tuned ResNet18, and a fine-tuned ResNet34. I expected ResNet34's extra capacity to be hard to use with only 620 training images, the classic setup for a larger model overfitting rather than generalizing. Architecture selection happened entirely on the validation split, before test was opened, so the model I report is the one validation chose rather than whichever got lucky on sealed data. That ordering is easy to get wrong and hard to detect afterward, which is why I fixed it in advance.

Two training details changed what the model learns. The loss was computed against every labeled grasp on an image, with only the best match backpropagated. Regressing toward the average of an image's grasps sounds reasonable and is actually harmful, since the average of a handle grasp and a rim grasp lands between them where neither is valid. Augmentation handled labels by pushing the rectangle's four corners through the same affine transform as the pixels and re-deriving the parameters, rather than writing a rule for how the angle behaves under a flip. Hand-written rules for that are easy to get backward, and the error stays invisible until accuracy is mysteriously bad.

Which published result System B should be measured against is worth getting right, because getting it wrong makes the paper tell the wrong story. GR-ConvNet reports 97.7% image-wise and 96.6% object-wise on Cornell (Kumra et al. 9626), and next to those numbers System B looks poor. But GR-ConvNet and GG-CNN are pixel-wise: they predict a grasp at every pixel of the input in a single pass, which is what lets GG-CNN close a control loop at 50 Hz (Morrison et al.). System B does nothing of the kind. It pools a backbone's features and regresses one rectangle for the whole image, architecturally the same design Redmon and Angelova published in 2015, reporting 84.9% object-wise (1316). Against that comparison the gap is small, and every remaining difference points the same direction: they used RGB-D where I used RGB only, and roughly 3,000 augmented examples per original image where I used 620 real images total. None of that requires appealing to anything I did not measure.

### System C, zero-shot vision-language model

System C prompts GPT-4o with each test image and asks where the two gripper fingertips should touch. It receives no training, no examples, and no fine-tuning. The prompt was frozen after development on a 30-image training batch and never revised after test was opened.

One design decision closed off a whole category of false conclusions. I never asked for an angle. The model reports two contact points, and orientation is derived from them by the same function that produced every ground-truth angle in the dataset. Had I asked for an angle directly, a silent mismatch over degrees versus radians would have produced wrong scores indistinguishable from the model being bad at grasping. Each image was run five times, since output varies between calls, and that variation is reported rather than averaged away.

The temptation is to read 12.4% as confirming that vision-language models are bad at spatial tasks. That would be unsurprising and, I think, the wrong lesson. More telling is what published grasping systems do with the model. FreeGrasp has GPT-4o choose which object to grasp and in what order, using marks overlaid on the image rather than raw numbers (Jiao et al.). Lan-grasp picks which part to grasp, then hands the pose to a conventional planner (Mirjalili et al.). ThinkGrasp uses GPT-4o for clutter strategy, deciding what to move to uncover a target (Qian et al.). Set-of-Mark replaces coordinate output with a choice among labeled regions, letting zero-shot GPT-4V beat a fine-tuned referring-expression model on RefCOCOg (Yang et al.). VLAD-Grasp goes furthest, having the model draw a goal image with a virtual gripper intersecting the object (Kulshrestha et al.).

In all five, the model's output is a choice, a label, an ordering, or a picture, and the numeric pose comes from something else. I want to be careful about what I infer, since these systems solve different problems, several involving clutter my task does not have, so handing geometry to a planner may be the natural architecture rather than a judgment about coordinates. What I can say is narrower: I did not find a published grasping system that treats free-text coordinate emission as its primary geometric output, nor any benchmark of that path against non-VLM baselines on a shared split. System C is that measurement.

The failure pattern points at a mechanism. Of 615 calls, 365 missed on angle and overlap simultaneously, far more than either single-axis failure. A supplementary geometric check on the frozen predictions, outside the Cornell metric and used only as a diagnostic, asked whether each predicted center fell inside the convex hull of all labeled grasp rectangles. That is the loosest spatial test a prediction can fail, since the hull is larger than any single rectangle. System C failed it on 53.4% of calls, against 7.0% for System A and 6.5% for System B. That gap is real but not like-for-like: System B was trained on this distribution, and System A's center is built from a detected box or a segmentation, so both are close to guaranteed to land on the object. System C is the only one free to place a center anywhere, so the comparison shows its errors are a different kind, not simply more of the same.

Reading the model's written explanation alongside its coordinates on sampled failures showed the pattern behind that number. The explanation would name a real part of the object, the handle or the narrow end, while the coordinates in the same reply landed somewhere unrelated. That is a binding failure between two channels of one response rather than a failure to perceive. I treat that text as observable output, not as a transcript of how the model arrived at anything. Wang et al. document the same disconnect in an unrelated domain, finding models that describe a correct procedure on a visual puzzle and then click hundreds of pixels away: the model "solves the puzzle in words" but fails to ground those words into acceptable pixel coordinates (Wang et al., sec. 5.3.2). Their examples use a different model on a CAPTCHA task, so this corroborates the mechanism across contexts rather than repeating my experiment.

### The orientation axis

Each system's design predicts something different about how orientation should affect it, and those predictions can be checked against an axis sourced from the dataset rather than from any system's output. System A should suffer badly on diagonal objects, since its representation cannot express them. System B should be largely unaffected, since its encoding handles rotation by construction. System C has no structural position either way, so its behavior was open before I looked.

Splitting the test set by whether an image's labeled grasps sit more than 15 degrees off axis produced exactly that pattern. On the 20 diagonal images System A drops 21.2 points relative to the axis-aligned images, System B gains 12.3 points, and System C moves 2.0 points. Three systems, three directions, one split.

Two parts of this deserve no credit. That axis-aligned boxes cannot represent diagonal grasps is derivable from the representation alone, and that rotation-aware encodings handle rotation is the entire reason those encodings exist. Neither is a discovery. What I could not find precedent for is using the stratification as a diagnostic instrument, taking an axis sourced from the dataset's own annotations and reading off which direction each technique family moves. Published Cornell work reports image-wise and object-wise splits, which measure generalization, not orientation-conditioned breakdowns of where a representation gives out. So I offer this as a method others could reuse cheaply, not as a fact about grasping.

The honest caveat is sample size. The diagonal stratum holds 20 images, its intervals are wide, and I ran no test of the joint three-way pattern against a null, so I cannot say how unlikely it is by chance. One cell is firmer: System A's drop was predicted from its representation before the stratum was scored, which makes it a confirmed prediction rather than a pattern found afterward. The rest is exploratory. The divergence earns its place as the diagnostic that pointed at the mechanism, not as a general result, and the effect sizes need a larger diagonal sample before anyone leans on them.

System C's near-flat response is doing quiet work there. A system with no working orientation signal should look flat on an orientation-stratified split, and it does, which agrees with the compound-failure taxonomy by a separate route.

I also tested a second axis, the number of grasps labeled per image, expecting a difficulty proxy. It did not behave like one. All three systems did worst on images carrying the most labeled grasps, even though more labeled grasps means more rectangles a prediction may match. My guess is that annotators labeled many grasps on objects that afford many, so the count tracks complexity rather than how generous the metric is. I report it because I measured it, and I use it to argue nothing.

### What this means

The coordinate-binding explanation makes a prediction that can be tested rather than asserted. If the problem is binding reasoning to emitted numbers rather than perceiving the object, then removing the numeric channel should help substantially, while sharpening perception alone should not. The literature is consistent with that without anyone framing it as a test. Set-of-Mark lets zero-shot GPT-4V beat a fine-tuned specialist purely by replacing coordinate emission with region selection (Yang et al.). VLAD-Grasp scores far above System C on Cornell, training-free, by having the model draw the grasp rather than state it (Kulshrestha et al.).

That second comparison is the one I find striking, and it reframes my own worst result, but two things stop it from being a number I can set against my 12.4%. VLAD-Grasp does not merely ask for a picture instead of a number. It then predicts depth and segmentation to lift that image into three dimensions and aligns point clouds to recover a pose, a geometric pipeline System C has no equivalent to. It also counts a grasp correct on overlap alone, without the 30-degree angle requirement I apply throughout, and reports 91.4% under that looser test. That the same evaluation scores GR-ConvNet at 72.1%, against the 97.7% it reports for itself, shows the two protocols are not on one scale. The dropped angle criterion matters most, since orientation is the axis this paper spends its Results on.

What survives the caveat still holds. Two zero-shot uses of one pretrained model on the same benchmark produce very different outcomes, and the one that works never asks for a coordinate. Put that beside the failure taxonomy and beside Wang et al.'s independent observation, and the useful reading is that requesting raw coordinates carries a large cost unrelated to whether the model can see the object.

I should be plain about what is new here and what is not. The sine and cosine encoding has been standard since 2015. That vision-language models produce imprecise coordinates is established, not discovered. That learned models beat rule-based baselines on Cornell was settled a decade ago, so System A against System B confirms a known result, and its value here is as a controlled instrument for the orientation analysis. What this project adds is a measurement of the coordinate weakness on a standard benchmark, against two baselines on the identical split, with a mechanism-level account corroborated from an unrelated domain.

One result genuinely surprised me. The from-scratch network failed to learn the task by any reasonable standard, reaching 23.6% after a learning-rate sweep confirmed the failure was not a tuning artifact, and it still beat GPT-4o by 11 points. A one-million-parameter network that never learned the task reliably outperformed a frontier multimodal model on the same images, which is uncomfortable for anyone's intuitions about where capability lives, mine included.

One process note belongs here, because it is part of why these numbers can be trusted. Three bugs in my own code were caught before any reached a reported result: a corrupted grouping output during split construction, an early-stopping rule that would have named an undertrained checkpoint the best one, and a smart-quote mismatch that silently broke the contamination probe's scoring. Two of the three would have produced perfectly reasonable-looking numbers. Each surfaced the same way, by checking an automated result against an independent method and not trusting either until the disagreement was explained.

### Limitations

The split is a single frozen object-wise split, opened once, rather than the five-fold cross-validation most published Cornell results use, so the protocols are not directly equivalent even under the same metric. Seven of its 35 object groups hold a single image, so per-object accuracy is coarse for those. Jacquard was unavailable, so generalization across datasets is untested. An early formatting check on roughly 550 grasp rectangles likely touched a small number of images that later landed in the test split; no threshold, constant, or lookup entry was derived from that check, but it should be disclosed.

The three systems did not receive comparable engineering effort, and that asymmetry cuts against my own conclusion, so it belongs here rather than buried. System B got three architectures, a five-point learning-rate sweep, a tuned loss weight, and validation-based model selection. System C got one prompt, frozen after development on 30 training images and never revised. Freezing it was right for test-set integrity and I would do it again, but prompt design is the vision-language equivalent of architecture search, and I ran architecture search for one system and not the other. A fair reading is that this study measures what a single un-iterated prompt achieves, not the ceiling of careful prompting.

Contamination deserves its own note. Cornell is public and widely mirrored, so GPT-4o could plausibly have seen it in training. A ten-image probe asking the model to name the source dataset, without revealing the task was grasping, returned zero recognitions. That is a weak indicator rather than a clearance, since a model can have memorized material it cannot name. What makes the risk survivable is its direction: contamination could only raise System C's score, never lower it, so the conclusion that System C trails holds under the least favorable assumption, and I make no claim in the opposite direction.

The orientation finding rests on 20 diagonal images. The coordinate-binding result covers one model, one frozen prompt, and one method of asking, so it describes free-text coordinate emission rather than vision-language models generally. All input was RGB, with no depth channel.

## Results

### The data split

> **[TABLE 1]** Caption above the table in MLA style: "Table 1. Object-wise split of the Cornell Grasping Dataset. No object appears in more than one split."

| Split | Objects | Images |
|---|---|---|
| Train | 164 | 620 |
| Validation | 35 | 140 |
| Test | 35 | 123 |
| Total | 234 | 883 |

The split covers 234 objects across 883 images, divided 70/15/15 by object count with a fixed random seed. No object appears in more than one split, verified twice: once during construction and once by an independent re-read of the final assignment file.

Of the 884 frame boundaries examined during grouping, 251 (28.4%) fell into the ambiguous band. I decided 139 of those by hand; the remaining 112 were confident same-object calls accepted in the low-risk direction. Six remained genuinely ambiguous after full review. Four carried a directional lean and were resolved toward "same object." The remaining two had no lean and were not forced to a decision; one image on the smaller side of each was excluded instead, which accounts for the 883 images retained out of the original 885.

### System A

System A scored 57.7% on the test split (71 of 123), 95% Wilson interval [48.9, 66.1]. Of its 52 failures, 13 missed on orientation alone, meaning the rectangle overlapped the correct region but pointed more than 30 degrees from any labeled grasp.

The two paths performed differently, and separating them matters for reading the headline. The detector fired on 49 of 123 test images (39.8%). Counting every image where it fired on nothing as a failure gives 22.8% (28 of 123), while among the images where it did fire accuracy was 57.1% (28 of 49). The geometric fallback carried 66 images, and 8 yielded no prediction. Accuracy by category varied widely on small counts: apples were 6 of 6 and cell phones 8 of 11, while cups, bowls, and laptops never succeeded.

One amendment is on record. The table was evaluated once at 40.7% before a defect was found: the detector frequently boxed background clutter. A geometric guard requiring the box to contain the segmented object's centroid was added, one constant was recalibrated on training, and the result rose to 57.7%. Both figures stay on the record, and the detector-only number barely moved, from 22.0% to 22.8%.

### System B

> **[TABLE 2]** Caption above: "Table 2. System B compared with Redmon and Angelova's Direct Regression, the closest published architecture."

| | Redmon and Angelova (2015) | System B (ResNet18) |
|---|---|---|
| Architecture | Global regression | Global regression |
| Orientation encoding | sin/cos of twice the angle | sin/cos of twice the angle |
| Input | RGB-D | RGB only |
| Training data | ~3,000 augmented examples per image | 620 real images |
| Object-wise accuracy | 84.9% | 79.7% |

ResNet18, selected on validation before test was opened, reached 79.7% (98 of 123), interval [71.7, 85.8], with a mean angle error of 3.9 degrees and a mean intersection over union of 0.447 on its correct predictions. ResNet34 reached 70.7% (87 of 123) with a mean intersection over union of 0.424, and the from-scratch network reached 23.6% (29 of 123) with a mean angle error of 24.2 degrees. Parameter counts were 11.3M, 21.4M, and 1.0M respectively.

ResNet18 led ResNet34 on validation as well as test, 83.6% against 77.1%, so the selection was consistent across both splits. Its validation-to-test gap was 3.9 points. Epoch-to-epoch validation swings measured during training ranged from 6.7 to 11.9 points, so that gap sits well inside the noise of the quantity it is compared against.

The from-scratch network was given its own learning-rate sweep on validation across five values: 21.4% at 3e-5, 27.1% at 1e-4, 26.4% at 3e-4, 20.0% at 1e-3, and 22.9% at 3e-3. The selected rate of 1e-4 also produced the lowest final training loss of the five, at 0.60 against 1.32 for the worst.

Counted by failure type, ResNet18 missed 25 of 123 images, of which 4 failed on angle alone and 15 on overlap alone. ResNet34 missed 36 and the from-scratch network missed 94.

> **[FIGURE 1]** Insert `data/interim/system_b_sheets/resnet18_0133.png`. Caption below: "Fig. 1. System B (ResNet18) prediction in blue against labeled ground-truth grasps in green."

> **[FIGURE 2]** Insert `data/interim/comparison_sheets/compare_0348.png`.
> **Source note, not part of the caption:** of ResNet18's four angle-only failures (pcd0676, pcd0348, pcd0824, pcd0316) only pcd0348 has a rendered sheet, which is why this one was chosen.
> **Caption to typeset below the figure:** "Fig. 2. An orientation-only failure. The predicted rectangle overlaps the object well (IoU 0.38) but is rotated 47 degrees from any labeled grasp."

### System C

System C averaged 12.4% per repeat across five independent runs (76 of 615 calls), interval [10.0, 15.2]. The five repeats scored 13.0%, 14.6%, 13.8%, 10.6%, and 9.8%. Best-of-five, meaning an oracle picks the correct attempt whenever one exists, reached 35.0% (43 of 123). Majority consensus reached 12.2%. Neither upper-bound figure is the headline, since both require either multiple calls or knowing the answer in advance.

The model returned a parseable reply on 614 of 615 calls (99.8%), with one parse failure and no schema, range, or API failures. Every non-parsing call counts as a miss in the headline figure rather than being dropped.

> **[TABLE 3]** Caption above: "Table 3. Which criterion each prediction missed, computed through one shared scoring path for all three systems."

| Outcome | System A (of 123) | System B (of 123) | System C (of 615) |
|---|---|---|---|
| Correct | 71 (57.7%) | 98 (79.7%) | 76 (12.4%) |
| Angle only | 13 (10.6%) | 4 (3.3%) | 85 (13.8%) |
| Overlap only | 18 (14.6%) | 15 (12.2%) | 88 (14.3%) |
| Both | 13 (10.6%) | 6 (4.9%) | 365 (59.3%) |
| No prediction | 8 (6.5%) | 0 (0.0%) | 1 (0.2%) |

The geometric check reported in Methods found System C's predicted center outside the convex hull of every labeled grasp on 53.4% of calls (328 of 614), against 7.0% for System A (8 of 115 scored) and 6.5% for System B (8 of 123).

Agreement across repeats was low. Mean self-agreement was 22.0%, with a mean pairwise angle spread of 5.8 degrees and a mean pairwise intersection over union of 0.13 between repeats. Counting how many of five repeats scored correct per image: 1 image at five, 3 at four, 6 at three, 8 at two, 25 at one, and 80 at zero. That puts 81 of 123 images (65.9%) at a fully consistent outcome, leaving 42 where the same model on the same pixels sometimes passed and sometimes did not.

Self-agreement carries usable signal. Restricting action to images where at least 40% of repeat pairs agreed leaves 21.1% coverage at 57.7% accuracy on the covered images, against 35.0% at full coverage. This describes which of several repeated calls to trust and is not comparable to the single-call figures for Systems A and B.

> **[FIGURE 3]** Insert `data/interim/comparison_sheets/compare_0285.png`. Caption below: "Fig. 3. All three systems on one image: ground truth in green, System A in red, System B in blue, System C's five repeats in orange."

### Cross-system comparison

System A against System B is significant under McNemar's exact test (p = 1.4e-4), from 11 images System A alone got right against 38 System B alone got right. System C was tested separately against each of its five repeats rather than collapsed to a mean, and the least significant of the five is reported: p = 5e-12 against System A and p = 1.6e-20 against System B.

Stated most conservatively, System C's best-of-five ceiling of 35.0% carries an upper 95% bound of 43.7%, which sits below System A's single-call lower 95% bound of 48.9%. Those intervals do not overlap, so the ordering does not depend on any point estimate being exact.

> **[TABLE 4]** Caption above: "Table 4. Accuracy split by whether an image's labeled grasps are diagonal, with 95% Wilson intervals."

| Stratum | Images | System A | System B | System C |
|---|---|---|---|---|
| Axis-aligned | 103 | 61.2% [51.5, 70.0] | 77.7% [68.7, 84.6] | 12.0% [9.5, 15.1] |
| Diagonal | 20 | 40.0% [21.9, 61.3] | 90.0% [69.9, 97.2] | 14.0% [8.5, 22.1] |

Systems A and B agreed on 74 of 123 images, both correct on 60 and both wrong on 14. They disagreed on 49, with System B alone correct on 38 and System A alone correct on 11. Counting System C as correct if any of its five repeats passed, all three systems succeeded on 22 images and all three failed on 10.

The grasps-per-image axis is reported as a negative result. Grouped into images with 2 to 4 labeled grasps, 5 to 7, and 8 to 25, all three systems scored worst on the last group (48.0%, 64.0%, and 11.2% for A, B, and C) rather than the first, contradicting the premise that more labeled grasps should make a match easier.

## Conclusion

Scoring three approaches through one pipeline showed that their errors are not interchangeable, and that is the finding I would keep if I could keep only one. The accuracies set the stage rather than settling anything: 57.7% for the rule-based system, 79.7% for the fine-tuned ResNet18, and 12.4% for zero-shot GPT-4o, whose best-of-five ceiling still falls below the rule-based system's lower 95% confidence bound.

What the comparison bought was the ability to see three failure modes side by side on the same images, scored by the same code. System A locates objects but cannot rotate the gripper, because an axis-aligned box has no way to express a diagonal grasp. System B rotates well, to within about four degrees when it succeeds, and its remaining errors are mostly about placing the rectangle rather than turning it. System C fails before either question is reached, because the coordinates it emits are frequently not bound to the object its own sentences have just described correctly. Those are three distinguishable problems, and knowing which one you have tells you what to fix.

The third failure is the one worth carrying forward, because another system does not have it. VLAD-Grasp uses a pretrained vision-language model zero-shot on this same dataset and scores far higher, and it never asks for a coordinate. It also does considerably more downstream and grades itself without the angle criterion I use, so its number and my 12.4% cannot simply be subtracted. What I can say is that asking a vision-language model for raw pixel coordinates carries a large, measurable cost, that the cost appears as the written explanation and the emitted numbers diverging rather than as the model failing to see, and that the same divergence has been observed independently in a completely different task.

If that reading is right, it points to one experiment that would settle it. Rerunning System C with Set-of-Mark prompting, where the model selects among labeled regions instead of emitting coordinates, should recover a substantial part of the gap. If it does not, my diagnosis is wrong and the problem lies in perception after all, which I would rather find out than assume. That experiment is cheap, it is the obvious next step, and I have not run it.

## Works Cited

> **[MLA-FORMAT]** Apply hanging indents through the word processor's paragraph settings, not with tabs or spaces. Double-space with no extra blank lines between entries. Verify no straight quotes were auto-converted to curly ones in the exported PDF.

Jiang, Yun, et al. "Efficient Grasping from RGBD Images: Learning Using a New Rectangle Representation." *2011 IEEE International Conference on Robotics and Automation (ICRA)*, IEEE, 2011, pp. 3304-11.

Jiao, Runyu, et al. "Free-Form Language-Based Robotic Reasoning and Grasping." *arXiv*, 17 Mar. 2025, arxiv.org/abs/2503.13082.

Kulshrestha, Manav, et al. "VLAD-Grasp: Zero-Shot Grasp Detection via Vision-Language Models." *arXiv*, 8 Nov. 2025, arxiv.org/abs/2511.05791.

Kumra, Sulabh, et al. "Antipodal Robotic Grasping Using Generative Residual Convolutional Neural Network." *2020 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)*, IEEE, 2020, pp. 9626-33.

Lenz, Ian, et al. "Deep Learning for Detecting Robotic Grasps." *The International Journal of Robotics Research*, vol. 34, no. 4-5, 2015, pp. 705-24.

Mirjalili, Reihaneh, et al. "Lan-grasp: Using Large Language Models for Semantic Object Grasping and Placement." *arXiv*, 8 Oct. 2023, arxiv.org/abs/2310.05239.

Morrison, Douglas, et al. "Closing the Loop for Robotic Grasping: A Real-Time, Generative Grasp Synthesis Approach." *Robotics: Science and Systems XIV*, 2018.

Qian, Yaoyao, et al. "ThinkGrasp: A Vision-Language System for Strategic Part Grasping in Clutter." *arXiv*, 16 July 2024, arxiv.org/abs/2407.11298.

Redmon, Joseph, and Anelia Angelova. "Real-Time Grasp Detection Using Convolutional Neural Networks." *2015 IEEE International Conference on Robotics and Automation (ICRA)*, IEEE, 2015, pp. 1316-22.

Wang, Junyu, et al. "COGNITION: From Evaluation to Defense against Multimodal LLM CAPTCHA Solvers." *arXiv*, 2 Dec. 2025, arxiv.org/abs/2512.02318.

Yang, Jianwei, et al. "Set-of-Mark Prompting Unleashes Extraordinary Visual Grounding in GPT-4V." *arXiv*, 17 Oct. 2023, arxiv.org/abs/2310.11441.
