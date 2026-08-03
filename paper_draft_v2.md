# DRAFT v2, working notes before the paper starts

**Nothing sealed was touched.** This task read `source_of_truth.md`, the three `system_*_results.md` files, `comparison_results.md`, `center_containment_analysis.md`, and `research_findings.md`. It modified none of them. No system was re-run, no API call was made, no number was recomputed. `paper_draft.md` (the earlier hand-written draft) is also untouched; this is a separate, independent draft.

**Plugin deviation, recorded once as required.** The ARS `academic-paper` skill carries an IRON RULE that every paper must include a Data Availability Statement, Ethics Declaration, CRediT author contributions, Conflict of Interest statement, and Funding Acknowledgment. All five are omitted here, per your decision, because the competition specifies six sections and none of these are among them. This is a deliberate override, not an oversight.

## Citation verification results

Every source below was checked against the actual paper before being cited. Framework §6 listed five open items. Here is what each one turned out to be.

| Item | Result |
|---|---|
| COGNITION passage | **Confirmed, with three corrections.** It lives in §5.3.2, "Spatial Grounding Failures," not appendix A.3.2/A.3.3. The phrase "solves the puzzle in words" is verbatim, but `research_findings.md` presented it merged with a second sentence; the real sentence is quoted correctly in this draft. The 700-pixel example is exact (target at (290, 235), model clicked (565, 895)) but the model is **GPT-5 on a path-tracing task**, not GPT-4o on grasping. That is stated plainly in the draft. The second example the notes quoted, "(400, 690) versus (305, 520)," does not appear in the paper at all and is not used. |
| ViewSpatial-Bench figures | **Not verifiable.** The 34.98% / 26.33% figures are not in the abstract and §5.2 is a table with no extractable text. **The source is dropped entirely.** It was never load-bearing. |
| VLAD-Grasp motivation | **Refuted.** The abstract motivates the method by dataset curation cost and retraining burden, not by VLM numeric weakness. Only the method is cited, never the motivation. |
| GraspMAS / ThinkGrasp / SegGrasp / Lan-grasp | **Two of four confirmed.** ThinkGrasp (Qian et al.) and Lan-grasp (Mirjalili et al.) both verified as instances of the pattern, with full author lists. GraspMAS and SegGrasp could not be verified and are **dropped**. |
| Page ranges | **All confirmed.** Jiang 3304-11, Lenz 705-24, Redmon 1316-22, Kumra 9626-33. Morrison is an RSS 2018 proceedings paper and genuinely has no page numbers, so MLA correctly omits them. |

**One verification finding improved the argument.** VLAD-Grasp reports performance competitive with state of the art **on Cornell itself** while being training-free, because it has the VLM draw a picture rather than emit numbers. That is the same benchmark where System C scores 12.4%. The contrast is now direct rather than analogical, and the Discussion is built on it.

**Still to do before submission** (framework §8): confirm object groups 26, 56, 230, 231 visually if you use any object name; run the US-English spelling pass; apply MLA formatting in a word processor; read the whole thing aloud once.

**Word count:** roughly 3,500 words of body text, inside the 2,800-4,200 target. Placeholders and this note are excluded.

---

# Three Ways to Miss a Grasp: A Controlled Comparison of Rule-Based, Learned, and Zero-Shot Vision-Language Prediction

> **[MLA-FORMAT]** Before export: MLA header block at top left of page 1 (name, mentor, competition, date), title centered in plain 12pt Times New Roman with no bold or italic, page numbers upper right as "Talla N", double spacing throughout including Works Cited, 1-inch margins, hanging indents on Works Cited entries. Delete this note and the entire scaffolding section above it.

## Abstract

A robot cannot pick anything up until something decides where on the object to place the fingers and at what angle. That decision can come from a hand-written rule, from a model trained to predict grasps from images, or from a general-purpose vision-language model never trained on grasping at all. I built one system of each kind and scored all three against the same external answer key, the Cornell Grasping Dataset's hand-labeled grasp rectangles, on one held-out split of 123 images covering 35 objects that appear nowhere in training. The rule-based system reached 57.7%, the fine-tuned ResNet18 reached 79.7%, and zero-shot GPT-4o reached 12.4% averaged over five runs per image. The first gap is statistically significant, and the vision-language model trails so far that even its best-of-five ceiling of 35.0% sits below the rule-based system's worst-case lower bound of 48.9%. The ranking is not the interesting part. Splitting the test set by whether an image's labeled grasps run diagonally shows three systems moving three different ways: the rule-based system loses 21.2 points, the learned model gains 12.3, and the vision-language model barely moves. Its failures explain why. Its written reasoning frequently named the correct part of the object while the coordinates in the same reply landed nowhere near it, and on 53.4% of calls the predicted center fell outside the region holding every labeled grasp, about eight times either other system's rate. The problem is the channel, not the model.

**Keywords:** robotic grasping, grasp detection, vision-language models, Cornell Grasping Dataset, spatial grounding, benchmark evaluation

## Introduction

Before a gripper closes on anything, something has to choose a contact point, an approach angle, and how wide to open. That choice can be made three quite different ways. A programmer can write the rule directly, saying that mugs get grasped by the handle and bottles around the neck. A model can be trained on thousands of labeled examples until it learns to predict grasps from pixels. Or a general-purpose vision-language model, trained on web text and images and never shown a grasping dataset, can simply be asked where to grip. These are not variations on one method. They are three different bets about where the useful intelligence in a robot's perception stack should live.

This project compares all three under conditions strict enough that the comparison means something. Each system predicts a grasp for the same 123 test images, and each is scored against the same hand-labeled ground truth using the same rule. The question I set out to answer is plain: which approach actually works, and where does each one break?

The measuring apparatus is borrowed rather than invented, which matters. A grasp here is a rectangle with a center point, an orientation, and a width matched to how far the gripper opens, the representation Jiang, Moseson, and Saxena introduced with the Cornell Grasping Dataset (3304). A prediction counts as correct if its angle falls within 30 degrees of a labeled grasp and its intersection over union with that grasp exceeds 25%, the convention established by Lenz, Lee, and Saxena (712). I chose an external answer key deliberately. An earlier version of this project would have had me write the ground truth myself and then grade my own rule-based system against it, which would have been close to circular. Using the dataset's existing annotations removes that problem and also makes the numbers comparable to published work.

The three systems are as follows. System A runs a COCO-pretrained object detector and looks the detected category up in a fixed table that maps it to a grasp region. System B is a learned predictor, a small convolutional network built from scratch alongside fine-tuned ResNet18 and ResNet34 models, trained on the Cornell training split. System C is GPT-4o, prompted directly with the raw image and given no task-specific training whatsoever.

I want to be clear about what this paper is not. It does not beat state-of-the-art grasp detection, and it does not try to. What it does is measure, under identical conditions, how three families of technique fail, and then argue that the shape of each failure tells you something the accuracy number alone does not. That argument turns out to matter most for the system that scored worst.

## Methods and discussion

### Dataset and evaluation

Every system was evaluated on the Cornell Grasping Dataset, about a thousand photographs of ordinary household objects with hand-labeled grasp rectangles. I looked into Jacquard as a second source, but its full distribution requires a signed institutional agreement and the mentor who would normally sign one was unavailable over the summer. Cornell alone it was, and I would rather say so directly than leave a reader wondering.

Cornell ships no object identity metadata, and that turned into the hardest methodological problem in the project. The split I needed was object-wise, meaning no physical object may appear in both training and test, because an image-wise split lets a model memorize what a particular stapler looks like and inflates every number afterward. With no labels to group by, identity had to be reconstructed from the image sequence.

My first attempt compared consecutive frames by raw pixel difference. It failed for an interesting reason: the dataset deliberately rotates each object between shots, so same-object and different-object comparisons produced score distributions that overlapped almost completely. I threw it out. The approach that worked segmented each frame using the geometry of the photography platform, since the object appears as a gap in an otherwise uniform surface, then compared those regions using descriptors that ignore rotation, specifically color histogram and pixel area.

The acceptance thresholds were set asymmetrically, for a reason worth stating because it is not obvious. The two possible mistakes are not equally bad. Merging two different objects into one group is nearly harmless, since the merged group still lands entirely on one side of the split. Splitting one real object into two is dangerous, because the halves can end up on opposite sides and every accuracy number in the paper quietly inflates. So I set the automatic "different object" threshold conservatively and the "same object" threshold loosely. About 28.4% of boundaries landed in the ambiguous band between them and were reviewed by hand. An AI assistant made a first pass logging a confidence level per decision, and I then classified a blind sample myself without seeing its answers. We agreed on 86.7% of its confident calls and 40.0% of its uncertain ones. That gap is what made its confidence usable as a signal, and it exposed a specific reasoning bias I could then correct for.

The result is 234 objects across 883 images, split 620 for training, 140 for validation, and 123 for test. One protocol difference from the literature needs stating rather than hiding: most published Cornell results use five-fold cross-validation over all 885 images, while I used a single frozen split opened exactly once. Those are not the same experiment even when the metric matches.

### System A, rule-based baseline

System A detects an object with a COCO-pretrained detector, looks the category up in a small fixed table, and converts the result into a rectangle centered on the detected box. The table was written and committed before any evaluation code existed in the repository, so no entry in it could ever be tuned toward a score. That was enforced structurally rather than by good intentions.

The design has a limitation built into it that I could state before running anything. A detector's bounding box is axis-aligned, so the orientation rule can only ever emit 0 or 90 degrees. Any object lying diagonally is unreachable no matter how perfectly the box is placed. I want to flag that this is a prediction made in advance, not an explanation invented after seeing the results.

### System B, learned grasp predictor

System B regresses a grasp rectangle directly from an image. Orientation is encoded not as a raw angle but as the sine and cosine of twice the angle. The reason is that a parallel-jaw gripper rotated 180 degrees is mechanically identical, so raw angle regression would see two grasps that are two degrees apart as 178 degrees apart, and the model would be punished for being right. Redmon and Angelova introduced this encoding for grasp regression (1316), and Morrison, Corke, and Leitner later used it in GG-CNN.

I trained three architectures: a small network built from scratch, a fine-tuned ResNet18, and a fine-tuned ResNet34. I expected ResNet34's extra capacity to be hard to use with only 620 training images, which is the classic setup for a larger model overfitting rather than generalizing. Architecture selection happened entirely on the validation split before the test split was opened, so the reported model is the one validation chose, not whichever one got lucky on sealed data. The loss was computed against every labeled grasp on an image with only the best match backpropagated, because regressing toward the average of a handle grasp and a rim grasp produces a point between them where neither is valid.

Which published result System B should be measured against is a question worth getting right. GR-ConvNet reports 97.7% on Cornell (Kumra, Joshi, and Sahin 9626), and next to that number System B looks poor. But GR-ConvNet and GG-CNN are pixel-wise: they predict a grasp at every pixel of the image in one pass, which is what lets GG-CNN close a control loop at 50 Hz (Morrison, Corke, and Leitner). System B is nothing like that. It pools a backbone's features and regresses one rectangle for the whole image, which is architecturally the same thing Redmon and Angelova built in 2015. Against that comparison the gap is small, and every remaining difference between the two setups points the same way: they used RGB-D input where I used RGB only, and roughly 3,000 augmented examples per original image where I used 620 real images total. Table 2 lays this out.

### System C, zero-shot vision-language model

System C prompts GPT-4o with each test image and asks where the two gripper fingertips should touch. It receives no training, no examples, and no fine-tuning. One design decision closed off a whole category of false conclusions: I never asked for an angle. The model reports two contact points, and orientation is derived from them by the same function that produced every ground-truth angle in the dataset. Had I asked for an angle directly, a silent convention mismatch over degrees versus radians would have been indistinguishable from the model simply being bad at grasping. Each image was run five times, because a language model's output varies between calls, and that variation is reported rather than averaged away.

The temptation is to read System C's 12.4% as confirming that vision-language models are bad at spatial tasks. That would be both unsurprising and, I think, the wrong lesson. What is more telling is what published vision-language grasping systems actually do, which is take considerable trouble to never ask the model for raw coordinates. FreeGrasp uses GPT-4o to reason about which object to grasp and in what order, annotating detected keypoints as marks on the image rather than requesting numbers, while grasp geometry comes from elsewhere (Jiao et al.). Lan-grasp pairs a language model and a vision-language model to decide which part of an object to grasp, then hands the actual pose to a conventional grasp planner (Mirjalili et al.). ThinkGrasp uses GPT-4o for clutter strategy, deciding what to move and in what sequence (Qian et al.). Set-of-Mark prompting replaces coordinate output entirely with a choice among labeled pre-segmented regions, and reports that doing so lets zero-shot GPT-4V beat a fully fine-tuned referring-expression model on RefCOCOg (Yang et al.). VLAD-Grasp goes furthest, prompting the model to generate a goal image with a virtual cylindrical gripper drawn intersecting the object, so the grasp axis is communicated pictorially and no number is ever requested (Kulshrestha et al.).

Five independent systems, five different ways of routing around the same thing. Each encodes an assumption that a vision-language model should not be handed the coordinate channel. As far as I could find, that assumption is acted on constantly and measured nowhere, at least not on a standard grasping benchmark against non-VLM baselines on a shared split. System C is that measurement.

The failure pattern supports a specific explanation. Of 615 calls, 365 missed on angle and overlap at once, far more than either single-axis failure. A purely geometric check on the same frozen predictions found that on 53.4% of calls the predicted grasp center fell outside the convex hull of every labeled grasp on that image, against 7.0% for System A and 6.5% for System B. Reading the model's reasoning text alongside its coordinates on sampled failures showed why: the reasoning would name a real, sensible part of the object while the coordinates in the same reply landed somewhere unrelated. That is a binding failure between two channels of one response, not a failure to see. Wang et al. document the same disconnect in an unrelated domain, reporting that models solving visual puzzles can describe a correct procedure and then click hundreds of pixels away, in one case over 700 pixels from a target the model had just described tracing a path toward. They put it directly: the model "solves the puzzle in words" but fails to ground those words into acceptable pixel coordinates (Wang et al., sec. 5.3.2). Their examples use a different model on a CAPTCHA task, so this corroborates a mechanism across contexts rather than repeating my experiment.

### The orientation axis

Each system's design predicts something different about how grasp orientation should affect it. System A should suffer badly on diagonal objects, since its representation cannot express them. System B should be largely unaffected, since its encoding handles rotation smoothly. System C has no structural position on orientation at all, so its behavior was genuinely open.

Splitting the test set by whether an image's labeled grasps sit more than 15 degrees off axis produced exactly that pattern. On the 20 diagonal images System A drops 21.2 points, System B gains 12.3 points, and System C moves 2.0 points. Three systems, three directions, one split.

I want to be careful about what to claim here. That axis-aligned boxes cannot represent diagonal grasps is true before any measurement, and that rotation-aware encodings handle rotation is the entire reason those encodings exist. Neither component is a discovery. What I could not find precedent for is using the stratification as a diagnostic instrument, taking a shared axis that comes from the dataset's own annotations rather than from any system's output, and reading off which direction each technique family moves on it. Published Cornell work reports image-wise and object-wise splits, which measure generalization, not orientation-conditioned breakdowns. So I offer this as a method other people could reuse cheaply, not as a fact about grasping. The diagonal stratum holds 20 images, which is enough to see a direction and not enough to trust a magnitude. What holds up is that three systems moved three ways at once, which is harder to get by accident than any single cell.

System C's near-flat response is doing quiet work in that table. A system with no orientation signal at all should look flat on an orientation-stratified split, and it does. That agrees with the compound-failure finding by a completely separate route, and two unrelated measurements landing on one explanation is worth more than either alone.

I also tested a second axis, the number of grasps labeled per image, expecting a difficulty proxy. It did not behave like one. All three systems did worst on the images carrying the most labeled grasps, even though more labeled grasps means more rectangles a prediction may match. My guess is that annotators labeled many grasps on objects that afford many, meaning long, thin, multi-part things, so the count tracks complexity instead. I report it because I measured it, and I use it to argue nothing.

### What this means

The coordinate-binding explanation makes a prediction that could be tested. If the problem is binding reasoning to emitted numbers rather than seeing the object, then changes that remove the numeric channel should help a lot, while changes that only sharpen perception should not. The literature is consistent with that without ever having framed it as a test. Set-of-Mark improves grounding substantially by replacing coordinates with region selection (Yang et al.). VLAD-Grasp reaches performance competitive with the state of the art on Cornell itself, training-free, by having the model draw the grasp instead of state it (Kulshrestha et al.).

That last comparison is the one I find genuinely striking, and it reframes my own worst result. VLAD-Grasp and System C both use a pretrained vision-language model, zero-shot, on the same benchmark. VLAD-Grasp is competitive. System C scores 12.4%. The difference between them is not the model's ability to understand the object. It is how the answer was asked for. That is a much more specific and more useful finding than "vision-language models are bad at grasping," and it is the single thing I would want a reader to take from this project.

It is worth being plain about what here is new and what is not. The sin and cosine orientation encoding has been standard since 2015 and I claim no credit for it. That vision-language models produce imprecise coordinates is established, not discovered. What this project adds is a controlled measurement of that weakness on a standard benchmark under a standard metric against two baselines on the identical split, plus a mechanism-level account supported by corroboration from an unrelated task domain. Overselling either point would cost me credibility on the parts that are real.

One process note belongs here, because it is part of why these numbers can be trusted. Four bugs in my own code were caught and fixed before any of them reached a reported result: the pixel-difference grouping heuristic that could not separate objects, an early-stopping rule that would have reported an undertrained checkpoint as the best model, a text-encoding mismatch that silently broke a contamination check, and a coordinate-frame error in the center-containment measurement. None were found by a reviewer, and none announced themselves through an implausible number. Each surfaced by checking an automated result against an independent method and refusing to trust either side until the disagreement was explained. I also left eight disputed object labels unresolved rather than adopting whichever AI-generated guess looked better, since choosing between two guesses would only produce something that reads as authoritative without being any more true.

The most direct next experiment is to rerun System C with Set-of-Mark prompting, the intervention my diagnosis predicts should help. I did not run it. With the time available, scoping the right experiment honestly seemed more useful than rushing it.

### Limitations

The split is a single frozen object-wise split opened once, not the five-fold cross-validation most published Cornell results use, so the protocols are not directly equivalent. Jacquard was unavailable, so generalization across datasets is untested. An early formatting check on roughly 550 grasp rectangles likely touched a small number of images that later landed in the test split; no threshold, constant, or table was derived from that check, but it should be disclosed.

Contamination deserves its own note. Cornell is public and widely mirrored, so GPT-4o could have seen it in training. A ten-image probe asking the model to name the source dataset without revealing the task returned zero recognitions, which is a weak indicator and not a clearance, since a model can have memorized something it cannot name. The direction of the risk is what makes this survivable: contamination could only raise System C's score, never lower it, so the conclusion that System C trails badly holds under the least favorable assumption. A conclusion in the opposite direction would not have survived, and I make none.

The orientation finding rests on 20 diagonal images. The coordinate-binding result covers one model, one frozen prompt, and one way of asking, so it describes free-text coordinate emission specifically and not vision-language models generally. All input was RGB, with no depth channel. Object-level accuracy is reported for interest only, since seven of the 35 object groups contain a single image where accuracy can only be 0% or 100%.

## Results

### The data split

> **[TABLE 1]** Object-wise split summary. Caption above the table in MLA style: "Table 1. Object-wise split of the Cornell Grasping Dataset. No object appears in more than one split."

| Split | Objects | Images |
|---|---|---|
| Train | 164 | 620 |
| Validation | 35 | 140 |
| Test | 35 | 123 |
| Total | 234 | 883 |

The split covers 234 objects across 883 images. No object appears in more than one split, verified once during construction and once by an independent re-read of the final assignment file.

### System A

System A scored 57.7% on the test split (71 of 123), with a 95% Wilson confidence interval of [48.9, 66.1]. Of its 52 failures, 13 missed on orientation alone, meaning the rectangle overlapped the right region but pointed more than 30 degrees off. This matches the limitation predicted in Methods from the representation itself.

A second number is worth reporting alongside it. Counting every image where the detector fired on nothing as a failure, accuracy falls to 22.8%, because the detector produced any detection at all on only 49 of 123 images. COCO's 80 categories do not cover most of what Cornell photographs, so the detector-only figure largely measures the detector's vocabulary rather than whether the grasp rule works. A platform-segmentation fallback carried the remaining images.

### System B

> **[TABLE 2]** System B against a matched published architecture. Caption above: "Table 2. System B compared with Redmon and Angelova's Direct Regression, the closest published architecture."

| | Redmon and Angelova (2015) | System B (ResNet18) |
|---|---|---|
| Architecture | Global regression | Global regression |
| Orientation encoding | sin/cos of twice the angle | sin/cos of twice the angle |
| Input | RGB-D | RGB only |
| Training data | ~3,000 augmented examples per image | 620 real images |
| Object-wise accuracy | 84.9% | 79.7% |

ResNet18, selected on validation before the test split was opened, reached 79.7% (98 of 123), interval [71.7, 85.8], with a mean angle error of 3.9 degrees on correct predictions. ResNet34 reached 70.7% (87 of 123) and the from-scratch network reached 23.6% (29 of 123). This confirms the expectation stated in Methods that 620 images cannot support ResNet34's extra capacity.

The from-scratch network's failure is not a tuning artifact. Five learning rates were swept on validation, and the winner also carried the lowest final training loss of the five, so the model was not merely undertrained. Its loss plateaued where the ResNets' kept falling. I will say plainly that a 1.0M-parameter network that failed to learn the task still outscored a frontier vision-language model by 11 points, and that is the most surprising single result in this project.

> **[FIGURE 1]** Insert `data/interim/system_b_sheets/resnet18_0133.png`. Caption below the image: "Fig. 1. System B (ResNet18) prediction in blue against labeled ground-truth grasps in green."

> **[FIGURE 2]** Insert `data/interim/comparison_sheets/compare_0348.png`. Caption below: "Fig. 2. An orientation-only failure. The predicted rectangle overlaps the object well (IoU 0.38) but is rotated 47 degrees away from any labeled grasp." Note: of ResNet18's four angle-only failures (pcd0676, pcd0348, pcd0824, pcd0316) only pcd0348 has a rendered sheet, which is why this one is used.

### System C

System C averaged 12.4% per repeat across five independent runs (76 of 615 calls), interval [10.0, 15.2], with individual repeats ranging from 9.8% to 14.6%. Best-of-five, meaning an oracle picks the correct attempt whenever one exists, reached 35.0%. Majority consensus reached 12.2%. Neither is the headline; both require either multiple calls or knowing the answer. The model returned a parseable reply on 614 of 615 calls.

> **[TABLE 3]** Failure taxonomy. Caption above: "Table 3. Which criterion each prediction missed, computed through one shared scoring path for all three systems."

| Outcome | System A (of 123) | System B (of 123) | System C (of 615) |
|---|---|---|---|
| Correct | 71 (57.7%) | 98 (79.7%) | 76 (12.4%) |
| Angle only | 13 (10.6%) | 4 (3.3%) | 85 (13.8%) |
| Overlap only | 18 (14.6%) | 15 (12.2%) | 88 (14.3%) |
| Both | 13 (10.6%) | 6 (4.9%) | 365 (59.3%) |
| No prediction | 8 (6.5%) | 0 (0.0%) | 1 (0.2%) |

The signatures invert between A and B. A quarter of System A's failures are orientation-only, against 16% of System B's, while System B's failures are mostly overlap. System C's dominant mode is neither, with 59.3% of calls missing both criteria at once.

The geometric check reported in Methods found System C's predicted center outside the convex hull of every labeled grasp on 53.4% of calls (328 of 614), against 7.0% for System A (8 of 115 scored) and 6.5% for System B (8 of 123).

> **[FIGURE 3]** Insert `data/interim/comparison_sheets/compare_0285.png`. Caption below: "Fig. 3. All three systems on one image: ground truth in green, System A in red, System B in blue, System C's five repeats in orange."

### Cross-system comparison

System A against System B is significant under McNemar's exact test (p = 1.4e-4, from 11 versus 38 discordant pairs). System C was tested separately against each of its five repeats rather than collapsed to a mean, and the least significant of the five is reported in each case: p = 5e-12 against System A and p = 1.6e-20 against System B. Stated most conservatively, System C's best-of-five ceiling of 35.0% has an upper bound of 43.7%, which sits below System A's single-call lower bound of 48.9%. Those intervals do not overlap, so the ordering does not depend on any point estimate being exact.

> **[TABLE 4]** Orientation-stratified accuracy. Caption above: "Table 4. Accuracy split by whether an image's labeled grasps are diagonal."

| Stratum | Images | System A | System B | System C |
|---|---|---|---|---|
| Axis-aligned | 103 | 61.2% | 77.7% | 12.0% |
| Diagonal | 20 | 40.0% | 90.0% | 14.0% |

Ten images defeated all three systems even when System C was given five attempts.

The grasps-per-image axis is reported here as a negative result. All three systems scored worst on images carrying the most labeled grasps (8 to 25 of them) rather than the fewest, contradicting the premise that more labeled grasps should make a match easier. This axis is not used to support any claim in this paper.

## Conclusion

I set out to find which of three approaches to grasp prediction works best under a shared, external standard, and where each one breaks. The rule-based system reached 57.7%, the fine-tuned ResNet18 reached 79.7%, and zero-shot GPT-4o reached 12.4%, trailing far enough that its most generous reading still does not overlap the rule-based system's worst case.

The ranking is the least interesting result. Each system failed at a different stage of the same problem, and the failures are separable. System A locates objects but cannot rotate the gripper. System B rotates well and sometimes puts the rectangle in the wrong place. System C fails before either question comes up, because the coordinates it emits are not bound to the object its own sentences correctly describe.

That last failure is the one worth carrying forward, because another system does not have it. VLAD-Grasp uses a pretrained vision-language model zero-shot on this same dataset and stays competitive with the state of the art, by asking for a picture instead of a number. Set against my 12.4%, the difference between those two results is not what the model can see. It is which channel the answer was demanded through. If that reading is right, then rerunning System C with Set-of-Mark prompting, where the model selects a labeled region rather than emitting coordinates, should recover a large part of the gap. That experiment is the obvious next step, it is cheap, and I have not run it.

## Works Cited

> **[MLA-FORMAT]** Apply hanging indents through the word processor's paragraph settings, not with tabs or spaces. Double-space with no extra blank lines between entries. Verify no straight quotes were auto-converted to curly ones in the exported PDF.

Jiang, Yun, Stephen Moseson, and Ashutosh Saxena. "Efficient Grasping from RGBD Images: Learning Using a New Rectangle Representation." *2011 IEEE International Conference on Robotics and Automation (ICRA)*, IEEE, 2011, pp. 3304-11.

Jiao, Runyu, et al. "Free-Form Language-Based Robotic Reasoning and Grasping." *arXiv*, 17 Mar. 2025, arxiv.org/abs/2503.13082.

Kulshrestha, Manav, et al. "VLAD-Grasp: Zero-Shot Grasp Detection via Vision-Language Models." *arXiv*, 8 Nov. 2025, arxiv.org/abs/2511.05791.

Kumra, Sulabh, Shirin Joshi, and Ferat Sahin. "Antipodal Robotic Grasping Using Generative Residual Convolutional Neural Network." *2020 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)*, IEEE, 2020, pp. 9626-33.

Lenz, Ian, Honglak Lee, and Ashutosh Saxena. "Deep Learning for Detecting Robotic Grasps." *The International Journal of Robotics Research*, vol. 34, no. 4-5, 2015, pp. 705-24.

Mirjalili, Reihaneh, et al. "Lan-grasp: Using Large Language Models for Semantic Object Grasping and Placement." *arXiv*, 8 Oct. 2023, arxiv.org/abs/2310.05239.

Morrison, Douglas, Peter Corke, and Jurgen Leitner. "Closing the Loop for Robotic Grasping: A Real-Time, Generative Grasp Synthesis Approach." *Robotics: Science and Systems XIV*, 2018.

Qian, Yaoyao, et al. "ThinkGrasp: A Vision-Language System for Strategic Part Grasping in Clutter." *arXiv*, 16 July 2024, arxiv.org/abs/2407.11298.

Redmon, Joseph, and Anelia Angelova. "Real-Time Grasp Detection Using Convolutional Neural Networks." *2015 IEEE International Conference on Robotics and Automation (ICRA)*, IEEE, 2015, pp. 1316-22.

Wang, Junyu, et al. "COGNITION: From Evaluation to Defense against Multimodal LLM CAPTCHA Solvers." *arXiv*, 2 Dec. 2025, arxiv.org/abs/2512.02318.

Yang, Jianwei, et al. "Set-of-Mark Prompting Unleashes Extraordinary Visual Grounding in GPT-4V." *arXiv*, 17 Oct. 2023, arxiv.org/abs/2310.11441.
