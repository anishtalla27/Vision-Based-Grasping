Three Ways to Miss a Grasp: A Same-Metric Comparison of Rule-Based, Learned, and Zero-Shot Vision-Language Prediction

Abstract

A robot cannot pick anything up until something decides where on the object to place the fingers and at what angle. Such a decision can be made by a set of hand-written rules, by a model that has been trained to recognize grasps from images of objects, or by a general-purpose vision-language model that was never trained on grasping tasks. Each of these systems was built and scored on the same external answer key (the Cornell Grasping Dataset’s hand-labeled grasp rectangles) on the same split of images (123 images, 35 different objects, none of which appear in the training split of the dataset). Success was scored by the standard Cornell rectangle metric, meaning a predicted angle within 30 degrees of a labeled grasp and a rectangle intersection over union above 25%. The learned system (fine-tuned ResNet18) passed on 79.7% of test images, the rule-based system on 57.7%, and the zero-shot system (GPT-4o, one frozen prompt, averaged over five runs per image) on 12.4%. The rule-based figure is post-hoc rather than held-out. A defect found after the test set was opened prompted a fix that raised it from 40.7%, and both numbers are reported throughout. The difference between the rule-based and learned models was significant (McNemar’s exact test), and the vision-language model trailed far enough that even its best-of-five accuracy of 35.0% fell below the rule-based system’s 48.9% lower confidence bound. A secondary analysis divided test images into axis-aligned and diagonal grasp groups. System A performed worse on diagonal grasps, System B performed better, and System C barely changed. Because only 20 test images were in the diagonal group, these results are exploratory. The model often correctly named the part of the object that was to be grasped, but provided coordinates for a point that did not land in any of the grasp rectangles, on 53.4% of calls (compared to approximately 5% in the other two systems). These errors suggest that, in this setup, GPT-4o may have more difficulty converting a visually identified grasp location into usable coordinates than identifying a plausible grasp region. The study does not isolate that mechanism from other explanations, so it is offered as a hypothesis rather than a result.

Introduction

Before a gripper on a robot can pick up an object, something has to decide where to place the fingers and at what angle to grasp it. That decision can come from a set of hand-written rules, from a model trained to recognize grasps in images, or from a vision-language model that has never been trained on grasping at all. This paper builds one system of each kind (a rule-based baseline, a fine-tuned ResNet18, and zero-shot GPT-4o) and scores all three on the same split of the Cornell Grasping Dataset, using the same answer key and the same evaluation code. The headline accuracies are reported above. The analysis also compares the types of errors made by each system.

Methods and discussion

Dataset and evaluation

The dataset used for evaluation is the Cornell Grasping Dataset, roughly a thousand images of household objects, each with hand-labeled grasp rectangles (Jiang et al.). A prediction counts as correct when its angle falls within 30 degrees of some labeled grasp and its rectangle intersection over union with that grasp exceeds 25%, the convention established by Lenz et al. Cornell’s annotations are not exhaustive, so passing this metric means matching a labeled grasp, not that the grasp would physically succeed. The Jacquard dataset was considered as an alternative, but its full distribution requires a signed agreement and an approved non-free-email request. Object identity was the hardest problem in building the split. No object may appear in both training and test, or a model can memorize its grasp rectangles from one split and be credited for recognizing the same object in the other. Cornell provides no object-identity labels, so identity had to be reconstructed from the image sequence. Comparing raw pixel differences between consecutive frames failed, because the dataset deliberately rotates each object between shots and same-object and different-object scores overlapped. Instead, each frame was segmented against the photography platform, and the resulting object regions were compared to decide whether two frames showed the same object or different ones.

Acceptance thresholds were set asymmetrically, since merging two different objects into one group is less harmful than splitting one real object into two. The “different-object” threshold was set below the lowest score seen for any confirmed same-object pair, while the “same-object” threshold stayed loose. A 30-boundary stratified sample was classified by both an AI assistant and a human, blind to each other’s calls. The AI’s classifications matched the human’s on 86.7% of its confident calls but only 40.0% of the calls it flagged as uncertain, so every uncertain call and every confident “different” call was reviewed by hand. Confident “same” calls were accepted unreviewed, since an error in that direction is harmless. The result is 234 objects across 883 images, with 620 for training, 140 for validation, and 123 for test. Published descriptions of Cornell normally report around 240 objects, and the shortfall here is expected rather than surprising, since the thresholds were deliberately biased toward merging. Every merge that should have been a split lowers the object count while keeping the merged group on one side of the division, which is the error direction this design accepts on purpose. Each object has at least one grasp rectangle, and most have several, since most objects can be picked up more than one way. Most published grasp-detection work benchmarks architectures within one system rather than comparing families of technique directly, which is the gap this paper’s three systems are built to fill.

System A, rule-based baseline

System A is better described as a detector-assisted heuristic baseline than a purely rule-based one. It detects the object with a COCO-pretrained detector, which is itself a learned component, then looks up the detected category in a fixed table of grasps. Nothing in it is learned from grasp labels, which is the sense in which it is rule-based. The table was committed before any evaluation code existed, so no entry could be tuned toward a score. Since COCO’s categories miss more than half of what Cornell photographs, a geometric fallback that does not rely on object recognition covers the objects the detector misses, and that fallback handles the majority of test images.

One qualification belongs here rather than in Results. System A was scored once at 40.7% before the detector was found to be boxing background clutter. The guard that fixed it was added after those test predictions had been inspected, so although the recalibrated constant used training data only, the decision to add the guard was prompted by test behavior. That makes 57.7% a post-hoc corrected figure rather than a clean held-out one, and it weakens the comparisons that rest on it, including the McNemar test against System B and the interval comparison against System C. Both numbers are reported everywhere the result appears.

A second limitation follows from the table’s design. COCO’s 80 categories do not cover most of what Cornell photographs, so many objects have no table entry to begin with. And regardless of path, System A’s rectangle orientation is limited to 0 or 90 degrees, the only two orientations the table and the box-based rule can express, so any grasp that requires an angle in between is one System A cannot produce.

System B, learned grasp predictor

System B regresses a grasp rectangle directly from an image. A backbone network extracts features, pools them, and a regression head predicts the rectangle’s parameters. Orientation is encoded as the sine and cosine of twice the angle rather than a raw angle between 0 and 180 degrees. This accounts for the fact that a grasp rectangle rotated 180 degrees describes the same physical grasp. A raw-angle representation would score that rotation as an entirely different grasp, while the sine/cosine encoding treats it as identical. Redmon and Angelova (2015) and Morrison et al. (2018) both used this same encoding.

System B trained three architectures on the same training split, a small network built from scratch, a fine-tuned ResNet18, and a fine-tuned ResNet34. The loss was computed against every labeled grasp on an image, with only the best match backpropagated. Averaging toward all of an image’s grasps would pull a handle grasp and a rim grasp toward a point on the object where neither is valid. Augmentation applied the same affine transform to the grasp rectangle’s corners as to the image’s pixels, rather than hand-writing a rule for how the angle behaves under a flip.

System B’s accuracy can look low next to two published Cornell results, but neither is an even comparison. GR-ConvNet reports 97.7% image-wise and 96.6% object-wise on an extended 1,035-image version of Cornell (Kumra et al. 9626-33), and only the object-wise figure is on the same footing as anything here. Redmon and Angelova report 84.9% object-wise (1316-22). GR-ConvNet is pixel-wise. It predicts a grasp at every pixel in a single pass. System B does nothing of the kind. It pools a backbone’s features and regresses one rectangle for the whole image, the same design Redmon and Angelova published, whose 84.9% object-wise score is the fairer target. Every remaining gap points the same direction. Redmon and Angelova used RGB-D and roughly 3,000 augmented examples per image, while System B used RGB only and 620 real training images.

System C, zero-shot vision-language model

System C prompts GPT-4o with each test image and asks where the two gripper fingertips should touch, with no training or fine-tuning on grasping. The prompt was developed on a batch of 30 training images and frozen before test was opened.

The configuration was as follows. The model was called as `openai/gpt-4o` through the OpenRouter API, at a 400-token cap, with temperature left unset so the provider default applied and no seed pinned, since run-to-run variation was one of the things being measured. Images were sent at the dataset’s native 640 by 480 resolution with no resizing, and the prompt told the model that coordinates were in pixels of that image. Each repeat was an independent single-turn completion with no prior messages, so the five repeats of an image are five genuine draws rather than one conversation. Transport failures were retried up to three times, but a reply that arrived and then failed to parse was never retried, since re-rolling malformed content would quietly convert a single-shot baseline into a best-of-N one.

System C was not asked to output an angle. It returned two fingertip points and a jaw width as JSON, and those three values determine all four rectangle corners, which were then passed through the same frozen function that produced every ground-truth angle in the dataset. No rectangle parameter was supplied by me, and no radians-versus-degrees convention had to be matched by hand. Each image was prompted five times, and all five results are reported.

System C’s 12.4% does not mean vision-language models are bad at spatial tasks. In several published grasping systems built on the same kind of model, the model’s output is a choice, a label, an order of operations, or an image, and the pose of the gripper comes from something else. FreeGrasp asks the model to decide which object to grasp and in what order, using marks placed on the image (Jiao et al.). Lan-grasp asks the model which part to grasp, then hands the pose to a conventional planner (Mirjalili et al.). ThinkGrasp uses the model to plan clutter removal (Qian et al.). Set-of-Mark asks the model to select one of several labeled regions (Yang et al.). VLAD-Grasp asks the model to draw the grasp using a virtual gripper (Kulshrestha et al.).

In none of them does the model emit the pose coordinates itself, which is exactly what System C is built to test. Does the gap come from the coordinate-emission step, or from the model’s inability to see the object?

Of 615 calls, 365 failed on both angle and overlap simultaneously, far more than either failure alone. A supplementary check asked whether each predicted center fell inside the convex hull of an image’s labeled grasp rectangles, the loosest spatial test a prediction can fail. System C failed it on 53.4% of calls, against 7.0% for System A and 6.5% for System B. That gap is real, though the comparison isn’t quite even, since System B was trained on this distribution and System A’s center comes from a detected box or a segmentation, so both are close to guaranteed to land on the object. System C is the only one free to place a center anywhere. Reading the model’s written explanations alongside its coordinates on a sample of failures, the explanation frequently named a real part of the object while the coordinates in the same reply landed somewhere unrelated. That reading was informal rather than a blinded coding study with a fixed rubric, so it should be treated as the observation that motivated the hypothesis, not as a measurement of how often the pattern holds.

Wang et al. document the same disconnect in an unrelated domain. Models describing a correct solution to a visual puzzle in text, then clicking hundreds of pixels away from it (Wang et al., sec. 5.3.2). The tasks differ, but the failure, text and coordinates disagreeing within one response, is the same.

The orientation axis

Each system’s design predicts something different about how orientation should affect it. System A’s representation cannot express a diagonal grasp, System B’s encoding handles rotation by construction, and System C has no structural position on the question at all.

An image counts as axis-aligned when any one of its labeled grasps sits within 15 degrees of 0 or 90 degrees, and as diagonal only when none does. The rule is deliberately conservative, since a system that can emit only axis-aligned rectangles still has a valid target whenever a single labeled grasp is axis-aligned. It is also looser than the 30 degree scoring tolerance, so a diagonal image whose labeled grasps sit 20 degrees off axis is still reachable by an axis-aligned prediction. That is why System A scores 40.0% on the diagonal stratum rather than near zero. Splitting the test set that way produced exactly the predicted pattern. System A dropped 21.2 points on the 20 diagonal images relative to axis-aligned ones, System B gained 12.3 points, and System C moved 2.0 points.

An axis-aligned box being unable to represent a diagonal grasp follows from the representation alone, and a rotation-invariant encoding handling rotation is the entire reason that encoding exists, so neither point here is a discovery on its own. What I could not find precedent for was using this split as a diagnostic. It checks whether each system’s accuracy rises or falls along an axis defined by the dataset’s own grasp-angle annotations, rather than reporting a single train/test generalization number.

The diagonal stratum holds only 20 images, and the 95% intervals around System B’s and System C’s per-stratum accuracies are wide enough that their point changes there are not reliably distinguishable from noise. Only System A’s drop was predicted from its representation before the stratum was scored, which makes it pre-registered rather than found afterward. Pre-registering a direction is not the same as confirming an effect, and no interaction test between system and stratum was run, so this remains exploratory too. System C’s near-flat response is at least consistent with the coordinate-binding hypothesis explored later, since a system with no working orientation signal should look flat on this split, and it does.

A second split, by the number of grasps labeled per image, was tested as a difficulty proxy. More labeled grasps should mean more chances for a prediction to match. It did not behave that way. All three systems did worst on the images with the most labeled grasps. The likely explanation is that annotators labeled more grasps on objects that afford more of them, so the count tracks object complexity rather than how generous the metric is.

What this means

This explanation makes a testable prediction. Removing System C’s ability to output coordinates directly should help if the problem is binding reasoning to those coordinates rather than perceiving the object, and should make no difference if the problem is perception. Two published results are consistent with the first case, though neither was designed as a test of it. Set-of-Mark lets zero-shot GPT-4V beat a fine-tuned specialist on RefCOCOg purely by replacing coordinate output with region selection (Yang et al.). VLAD-Grasp scores far above System C on this same dataset, training-free, by having the model draw the grasp instead of stating it (Kulshrestha et al.).

VLAD-Grasp is the comparison that most complicates System C’s result, but two things keep it from being a number that can be set directly against 12.4%. It does not simply ask for a picture instead of a coordinate. It then predicts depth, segments the object, and aligns 3D point clouds to recover a pose, a pipeline System C has no equivalent to. It also counts a grasp correct on overlap alone, with no angle requirement, and reports 91.4% under that looser test on a set of 70 unseen Cornell objects. That the same evaluation scores GR-ConvNet at 72.1%, against the 97.7% GR-ConvNet reports for itself, shows the two protocols are not directly comparable. The dropped angle criterion is what matters here, since orientation is the variable this paper’s results depend on most. It is also a different model rather than the same one, since the current revision of that paper names GPT-5 as its primary model, so it evidences what a vision-language model can do without emitting coordinates, not what GPT-4o specifically can do.

Even with that caveat, two zero-shot uses of the same pretrained model on the same benchmark produce very different outcomes, and the one that works never asks for a coordinate. Requesting raw coordinates appears to carry a cost unrelated to whether the model can see the object.

The sine/cosine encoding dates to 2015, learned models have beaten rule-based baselines on Cornell for a decade, and imprecise VLM coordinates are already documented elsewhere, so none of this is new by itself. Putting a number on that last weakness, on a standard benchmark against two baselines, with an account of the mechanism behind it, is what this experiment adds.

A one-million-parameter network built from scratch never learned the task by any reasonable standard, reaching 23.6% after a learning-rate sweep confirmed that wasn’t a tuning artifact. It still beat GPT-4o (System C) by 11 points, which I did not expect.

Three bugs in my own code were caught before any result was reported, each of which would have produced a plausible but wrong number. All three turned up the same way. An automated result didn’t match an independent calculation, and neither was trusted until the disagreement was explained.

Limitations

This test was limited to using a single split of the dataset relative to the five-fold cross-validation that is used by most published results using the Cornell dataset. Seven of the 35 object groups in the test split contain only a single image of the object, so the results for those objects are not as precise as they could be. Jacquard, considered as a second dataset source, was unavailable during this study, so no results were performed to test the generalization of these techniques across datasets. An early formatting check on roughly 550 grasp rectangles likely touched a small number of images that later landed in the test split. No threshold, constant, or lookup entry was derived from that check, but it should be disclosed.

The three systems did not receive comparable engineering effort, which cuts against the word "controlled" in the title. System B got three architectures, a five-point learning-rate sweep, a tuned loss weight, and validation-based model selection. System C got one prompt, frozen after development on 30 training images and never revised. Freezing it protected test-set integrity and I would do it again, but prompt design is the vision-language equivalent of architecture search, and I ran architecture search for one system and not the other. So 12.4% measures what one un-iterated prompt achieves, not a ceiling for zero-shot GPT-4o. The gap to System B is wide enough that prompt iteration is unlikely to reverse the ordering, but the specific number should not be quoted as the model's best.

System C’s potential contamination by the dataset was examined. While the dataset is a publicly available dataset that is mirrored by many organizations, a test of ten images of objects of various categories asked the language model to identify the source of the images returned no recognitions. This is a weak indicator of contamination of the model by the dataset, but contamination of the language model would only have led to an increase in System C’s score, which is already the lowest of the three systems. So the failure of System C in comparison to the other models holds even in the worst-case scenario of contamination of the model by the dataset.

Every interval and significance test reported here treats its unit of analysis as independent, and none of them are. System C’s interval is computed over 615 calls, but those are five repeats of 123 images, not 615 independent trials, so it is narrower than the data support. The image-level intervals and McNemar tests for Systems A and B have the same problem one level up, since the 123 test images are grouped within 35 objects and images of one object are not independent of each other. The stated population is unseen objects, so the correct sampling unit is the object. Intervals should be rebuilt by bootstrapping the 35 test objects with all of an object’s images and calls resampled together, and between-system comparisons should use an object-clustered permutation test. Doing so would likely leave the point estimates near where they are and widen every interval. That analysis has not been run, so the intervals in this paper should be read as optimistic. An object-balanced accuracy, weighting each object equally regardless of how many images it contributes, would also be a more faithful summary than the image-level mean, since test object groups range from one image to nine.

The findings of the results relative to the orientation of the objects was based on a sample size of only 20 objects. Additionally, the other findings of this test were made of one model, one method of posing the question to that model, and the one aspect of the task of grasping that is examined (the coordinates of the grasp), so these results describe that one setup rather than vision-language models generally.

All of the inputs to the models used in this test were images in RGB format only. No depth information from the objects was used as an input to any of the tested models.

Results

The data split

Table 1. Object-wise split of the Cornell Grasping Dataset. No object appears in more than one split.

SplitObjectsImagesTrain164620Validation35140Test35123Total234883

The split covers 234 objects across 883 images, divided roughly 70/15/15 by object count. No object appears in more than one split.

Of the 884 frame boundaries examined, 251 (28.4%) fell into the ambiguous band. 139 of those were decided by hand, and the remaining 112 were confident same-object calls accepted without review. Six stayed genuinely uncertain after full review. Four carried a lean toward “same object” and were resolved that way, and the other two had no lean. One image from the smaller side of each was dropped instead, accounting for the 883 images retained out of 885.

Three Grasp Prediction Systems

System A

System A achieved 57.7% on the test split (71 of 123), with a 95% Wilson interval of [48.9, 66.1]. Of the 52 failed predictions, 13 missed the orientation step alone.

The two paths performed differently. The detector fired on 39.8% of test images (49 of 123). Counting every image where it fired on nothing as a failure gives 22.8% (28 of 123), while accuracy on the images where it did fire was 57.1% (28 of 49). The fallback geometric system attempted 66 images and found no grasp on 8. Accuracy by object category was uneven, with all apples correct (6 of 6) but only 8 of 11 cell phones, none of the cups or bowls, and none of the laptops.

The table was evaluated once at 40.7% before the detector was found to be boxing background clutter. A geometric guard requiring the box to contain the object’s centroid, plus one constant recalibrated on training, raised the result to 57.7%. Both figures stay on record. The detector-only number moved only from 22.0% to 22.8%.

System B

System B is compared with Redmon and Angelova in Table 2.

Redmon and Angelova (2015)System B (ResNet18)ArchitectureGlobal regressionGlobal regressionOrientation encodingsin/cos of twice the anglesin/cos of twice the angleInputRGB-DRGB onlyTraining data~3,000 augmented examples per image620 real imagesObject-wise accuracy84.9%79.7%

System B achieved a 79.7% accuracy on the test split (98 of 123), with a 95% Wilson interval of [71.7, 85.8]. Its mean angle error of 3.9 degrees is measured only on the predictions it got right, against whichever labeled grasp the metric matched, so it describes how precisely System B orients a grasp when it succeeds and says nothing about the 25 it missed. System B’s ResNet34 model achieved 70.7% (87 of 123) with an average intersection over union of 0.424 of its grasps with the labeled grasps. The from-scratch model achieved 23.6% (29 of 123) with an average angle error of 24.2 degrees. Parameter counts were 11.3M, 21.4M, and 1.0M respectively.

System B’s ResNet18 outperformed ResNet34 on validation as well as test (83.6% vs. 77.1%), so the selection held across both splits. The validation-to-test gap (3.9 points) sits well inside the 6.7–11.9 point swings seen between epochs during training, so it isn’t evidence of overfitting. The from-scratch network got its own five-point learning-rate sweep on validation, scoring 21.4% at 3e-5, 27.1% at 1e-4, 26.4% at 3e-4, 20.0% at 1e-3, and 22.9% at 3e-3. The rate of 1e-4 was selected.

System B’s ResNet18 model missed 25 of 123 test images. Of those missed images, 4 failed on determining the angle of the object to grasp, while 15 failed on the overlap of the bounding box around the object with any labeled grasp in the image. ResNet34 failed to detect grasps in 36 images, while the from-scratch model missed 94 images.

Fig. 1. System B (ResNet18) prediction in blue against labeled ground-truth grasps in green.

Source note. Of the four failures of ResNet18 due to angle errors (pcd0676, pcd0348, pcd0824, pcd0316), only pcd0348 has a rendered sheet of its object, which is why it was chosen as the depicted example.

Fig. 2. An orientation-only failure. The predicted grasping rectangle correctly overlaps the object (intersection over union of 0.38) but rotates 47 degrees from any labeled grasp.

System C

System C achieved 12.4% accuracy on test images (76 of 615 calls), with a 95% Wilson interval of [10.0, 15.2]. Each of the five independent runs of System C achieved 13.0%, 14.6%, 13.8%, 10.6%, and 9.8% accuracy. The best-of-five attempts at grasping each of the test images achieved a 35.0% accuracy (43 of 123). A consensus rule that scores whichever single repeat agrees most closely with the other four, since continuous rectangles cannot be majority-voted directly, reached 12.2%. Neither of these is the headline figure. Both require either multiple calls per image or knowing the answer in advance.

System C returned a parseable reply on 614 of 615 calls (99.8%). Every non-parsing call counts as a miss in the headline figure.

\begin{table}[h]
\centering
\begin{tabular}{|c|c|c|c|}
\hline
Outcome & System A (of 123) & System B (of 123) & System C (of 615) \
\hline
Correct & 71 (57.7%) & 98 (79.7%) & 76 (12.4%) \
\hline
Angle only & 13 (10.6%) & 4 (3.3%) & 85 (13.8%) \
\hline
Overlap only & 18 (14.6%) & 15 (12.2%) & 88 (14.3%) \
\hline
Both & 13 (10.6%) & 6 (4.9%) & 365 (59.3%) \
\hline
No prediction & 8 (6.5%) & 0 (0.0%) & 1 (0.2%) \
\hline
\end{tabular}
\caption{For each grasp prediction system, the number of test images that were failed due to each type of failure.}
\end{table}

For the geometric grasp system described in Methods, System C’s predicted center of the graspable object was outside of the convex hull that contained every labeled graspable area in 53.4% of calls (328 of 614). System A reported failures of this type in 7.0% of the calls in which it attempted to find grasps (8 of 115 scored calls), while System B’s system had 6.5% failures (8 of 123).

Agreement across System C’s five runs was low. Mean self-agreement was 22.0%, with a mean pairwise angle spread of 5.8 degrees and mean pairwise intersection over union of 0.13. Counting how many of five repeats scored correct per image gives 1 at five, 3 at four, 6 at three, 8 at two, 25 at one, and 80 at zero. That puts 81 of 123 images (65.9%) at a fully consistent outcome, leaving 42 where the same model on the same pixels sometimes passed and sometimes didn’t.

Self-agreement carries usable signal. Restricting to the 21.1% of images where at least 40% of repeat pairs agreed lifts best-of-five accuracy to 57.7% on those images, against 35.0% at full coverage. The match with System A’s single-prediction 57.7% is a coincidence. This describes which of several repeated calls to trust, not a fourth accuracy figure to set against Systems A and B.

Fig. 3. All three systems attempted to grasp the same objects in the same image. Labels for the grasps are in green, while System A’s grasps are red, System B’s grasps are in blue, and System C’s five attempts are orange.

Cross-system comparison

System A against System B is significant under McNemar’s exact test (p = 1.4e-4), the 38-vs-11 split described below. System C was tested separately against each of its five runs rather than pooled. The least significant of the five is reported. p = 5e-12 against System A and p = 1.6e-20 against System B.

Stated conservatively, System C’s best-of-five ceiling of 35.0% carries an upper 95% bound of 43.7%, which sits below System A’s single-call lower 95% bound of 48.9%. Those intervals don’t overlap, so the ordering doesn’t depend on either point estimate being exact.

\begin{table}[h]
\centering
\begin{tabular}{|c|c|c|c|}
\hline
Stratum & Images & System A & System B & System C \
\hline
Axis-aligned & 103 & 61.2% [51.5, 70.0] & 77.7% [68.7, 84.6] & 12.0% [9.5, 15.1] \
\hline
Diagonal & 20 & 40.0% [21.9, 61.3] & 90.0% [69.9, 97.2] & 14.0% [8.5, 22.1] \
\hline
\end{tabular}
\caption{Accuracy by system for each type of grasps within test images, with 95% Wilson intervals.}
\end{table}

Systems A and B agreed on 74 of 123 images. Both correct on 60, both wrong on 14. Of the 49 they disagreed on, System B alone was correct on 38 and System A alone on 11. Counting System C as correct whenever any of its five repeats passed, all three systems succeeded together on 22 images and failed together on 10.

All three systems did worst on the images with the most labeled grasps (8 to 25), rather than the fewest, the opposite of what a more-labels-means-easier-match hypothesis would predict. In that group, System A scored 48.0%, System B 64.0%, and System C 11.2%.

Conclusion

System A’s accuracy of 57.7% is lower than System B’s 79.7% accuracy, and higher than System C’s 12.4% accuracy for zero-shot GPT-4o.

System A places a rectangle on the object often enough to score, though its detector fires on only 49 of 123 images and a geometric fallback carries the rest, and it cannot rotate the gripper at all, since an axis-aligned box has no way to express a diagonal grasp. System B rotates well, to within about four degrees on the predictions it gets right, with most of its remaining error coming from placement rather than orientation. System C produced the most distinctive error pattern in this comparison. Its coordinates are frequently not bound to the object its own text has just described correctly, so it fails before either of the other two questions is even reached.

The third failure matters most because another system does not have it. VLAD-Grasp runs a vision-language model zero-shot on this same dataset and scores far higher, though it uses a different model, adds a geometry pipeline System C has no equivalent to, and grades itself without the angle criterion used here, so the two numbers cannot be compared directly. The same text-coordinate divergence has turned up independently in a different task with the same kind of model, which is at least some evidence it is a property of the model rather than an artifact of this one prompt.

Rerunning System C with Set-of-Mark prompting, having it select among labeled regions instead of emitting coordinates, would test this directly. If the error persists anyway, the problem is perception, not coordinate binding, and that would be worth knowing too. This experiment has not yet been run.

References

Jiang, Yun, et al. "Efficient Grasping from RGBD Images: Learning Using a New Rectangle Representation." 2011 IEEE International Conference on Robotics and Automation (ICRA), IEEE, 2011, pp. 3304-11.

Jiao, Runyu, et al. "Free-Form Language-Based Robotic Reasoning and Grasping." arXiv, 17 Mar. 2025, arxiv.org/abs/2503.13082.

Kulshrestha, Manav, et al. "VLAD-Grasp: Zero-Shot Grasp Detection via Vision-Language Models." arXiv, 8 Nov. 2025, arxiv.org/abs/2511.05791.

Kumra, Sulabh, et al. "Antipodal Robotic Grasping Using Generative Residual Convolutional Neural Network." 2020 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), IEEE, 2020, pp. 9626-33.

Lenz, Ian, et al. "Deep Learning for Detecting Robotic Grasps." The International Journal of Robotics Research, vol. 34, no. 4-5, 2015, pp. 705-24.

Mirjalili, Reihaneh, et al. "Lan-grasp: Using Large Language Models for Semantic Object Grasping and Placement." arXiv, 8 Oct. 2023, arxiv.org/abs/2310.05239.

Morrison, Douglas, et al. "Closing the Loop for Robotic Grasping: A Real-Time, Generative Grasp Synthesis Approach." Robotics: Science and Systems XIV, 2018.

Qian, Yaoyao, et al. "ThinkGrasp: A Vision-Language System for Strategic Part Grasping in Clutter." arXiv, 16 July 2024, arxiv.org/abs/2407.11298.

Redmon, Joseph, and Anelia Angelova. "Real-Time Grasp Detection Using Convolutional Neural Networks." 2015 IEEE International Conference on Robotics and Automation (ICRA), IEEE, 2015, pp. 1316-22.

Wang, Junyu, et al. "COGNITION: From Evaluation to Defense against Multimodal LLM CAPTCHA Solvers." arXiv, 2 Dec. 2025, arxiv.org/abs/2512.02318.

Yang, Jianwei, et al. "Set-of-Mark Prompting Unleashes Extraordinary Visual Grounding in GPT-4V." arXiv, 17 Oct. 2023, arxiv.org/abs/2310.11441.
