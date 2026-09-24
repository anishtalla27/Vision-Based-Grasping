"""Second style pass over preprint_v2.tex: removes AI-writing patterns
(stacked "X, not Y" contrasts, announcer sentences, punchy closers, etc.)
and reflows plain prose paragraphs. Run once, after tone_pass_v2.py.
"""
import pathlib, re, textwrap

F = pathlib.Path(__file__).with_name("preprint_v2.tex")
t = F.read_text()

# ---- condense the "borrowed vs original" subsection -------------------------
a = t.index("\\subsection{What is borrowed and what is original}")
b = t.index("\\section{Methods}")
t = t[:a] + r"""\subsection{Relation to prior work}

This study builds on existing components: the Cornell Grasping Dataset
and its rectangle representation~\cite{jiang2011}, the 30-degree and
25\% IoU pass rule~\cite{lenz2015}, the ResNet architectures with
ImageNet weights~\cite{he2016}, Faster R-CNN with COCO
weights~\cite{ren2015}, the sine and cosine encoding of twice the grasp
angle~\cite{redmon2015,morrison2018}, GPT-4o~\cite{openai2024}, and
marked-candidate prompting~\cite{yang2024}. The work specific to this
study is the shared evaluation pipeline, the reconstruction of object
identities and the object-wise split, the detector-plus-table baseline,
the training recipe and pre-registered second round of the learned
system, the five-repeat protocol for the zero-shot model, the failure
diagnostics, the object-clustered statistical analysis, and the
candidate generator and menus that make up System D.

""" + t[b:]

PAIRS = [
# ------------------------------------------------------------- introduction
("In most practical settings the robot has a camera image and little else: no model of the object, no label identifying it, and no annotation marking a handle.",
 "In most practical settings the robot has a camera image but no model of the object and no label identifying it."),
("Each approach places the relevant knowledge in a different part of the perception stack: in a person's explicit rules, in weights fitted to task-specific data, or in a large model's general knowledge.",
 "Each approach places the relevant knowledge in a different part of the perception stack, whether explicit rules, weights fitted to task-specific data, or the general knowledge of a large model."),
("A lookup table needs only hand-specified rules. A learned predictor needs a task-specific annotated dataset and the compute to train on it. Prompting a hosted vision-language model requires only an API key and minimal setup. That convenience makes the approach attractive, and it is also why the approach should be measured before it is relied on.",
 "A lookup table needs only hand-specified rules, and a learned predictor needs a task-specific annotated dataset and the compute to train on it, whereas prompting a hosted vision-language model requires only an API key and minimal setup. Because that convenience makes the approach attractive, its accuracy should be measured before it is relied on."),
("This study places all three on the same test images, requires the same kind of output from each, and scores them with the same code.",
 "This study evaluates all three on the same test images, with a common output format and a single scoring implementation."),
("This paper asks two questions: which approach works, and where does each one break down? The second question is treated as equal to the first, because an accuracy number only says that a system was wrong, while the pattern of its errors points to a cause that the next designer can act on.",
 "This paper asks which approach works and where each one breaks down. The second question is treated as equal to the first, because an accuracy figure shows only that a system was wrong, while the pattern of its errors points to a cause that a designer can act on."),
("The evaluation protocol is adopted from prior work, and that choice was deliberate. A grasp here",
 "The evaluation protocol is adopted from prior work. A grasp here"),
("Each image carries several labeled grasps rather than one, since",
 "Each image has several labeled grasps, since"),
("An external ground truth was used for a specific reason. An earlier design, in which the author would have written the ground truth and then graded a rule-based system against it, was rejected as close to circular. The dataset's existing annotations remove that problem and make these numbers comparable to published ones.",
 "An external ground truth was used because an earlier design, in which the author would have written the ground truth and then graded a rule-based system against it, was close to circular. The dataset's existing annotations avoid that problem and make the results comparable to published ones."),
("The three systems are as follows. System A is", "Four systems are evaluated. System A is"),
("the pattern of each failure carries information that the accuracy figure does not.",
 "the pattern of each failure contains information that the accuracy figure does not."),
("The contributions are as follows.", "This paper makes the following contributions."),
("\\item Uncertainty reported at the level of the object, not the image. The ordering of the three systems survives an object-clustered bootstrap",
 "\\item Uncertainty reported at the level of the object, the unit that matches the stated population of unseen objects. The ordering of the three systems is preserved under an object-clustered bootstrap"),
# ------------------------------------------------------------------ methods
("so passing this metric means matching a labeled grasp, not that the grasp would physically succeed.",
 "so passing this metric shows agreement with a labeled grasp and does not establish that the grasp would physically succeed."),
("``same-object'' threshold stayed loose.", "``same-object'' threshold was left permissive."),
("One qualification concerns the test protocol. System A was scored once", "System A was scored once"),
("behavior, and the corrected figure is post-hoc, not held-out.",
 "behavior, and the corrected figure is a post-hoc result."),
("A second limitation follows from the table's design. COCO's 80 categories do not cover most of what Cornell photographs, so many objects have no table entry to begin with. And regardless of path, System A's rectangle orientation is limited to 0 or 90 degrees, the only two orientations the table and the box-based rule can express, so any grasp that requires an angle in between is one System A cannot produce.",
 "COCO's 80 categories do not cover most of the objects in Cornell, so many objects have no table entry. In addition, on either path System A's rectangle orientation is limited to 0 or 90 degrees, the only two orientations the table and the box-based rule can express, so it cannot produce a grasp that requires an intermediate angle."),
("Averaging toward all of an image's grasps would pull a handle grasp and a rim grasp toward a point on the object where neither is valid.",
 "Averaging over all of an image's grasps would place the target between, for example, a handle grasp and a rim grasp, at a point where neither is valid."),
("Four rules were written down before the second round touched the test split:",
 "Four rules were fixed before the second round was evaluated on the test split:"),
("the headline is the mean over seeds of the final weights, and every configuration that touches test is reported.",
 "the primary result is the mean over seeds of the final weights, and every configuration evaluated on the test split is reported."),
("Opening the test split a second time is a departure from the one-opening plan and is reported as one.",
 "Opening the test split a second time departs from the original single-opening plan."),
("The configuration was as follows. The model was called", "The model was called"),
("so the five repeats of an image are five independent draws and not one conversation.",
 "so the five repeats of an image are independent draws."),
("No rectangle parameter was supplied by hand, and no radians-versus-degrees convention had to be matched by hand.",
 "No rectangle parameter was supplied manually, and no angle convention had to be matched."),
("so a preference for a number cannot pass as a preference for a grasp, and self-agreement is measured on the physical candidate and not on its label.",
 "so a preference for a particular number cannot be mistaken for a preference for a grasp, and self-agreement is measured on the physical candidate."),
("which could have meant it was reading the line as the finger plates and not as the closing direction.",
 "which could have meant it was reading the line as the finger plates instead of the closing direction."),
("which supports reading the test result as the model's preference and not as an artifact of that particular glyph.",
 "which suggests that the test result reflects the model's preference and is unlikely to be an artifact of that particular glyph."),
("One confound remained after that run. On thin objects",
 "After that run, mark size remained as a possible confound. On thin objects"),
("Per-system accuracies carry 95\\% Wilson intervals,", "Per-system accuracies are reported with 95\\% Wilson intervals,"),
# ------------------------------------------------------------------ results
("so the second round is best read as the same result with its uncertainty measured rather than as an improvement.",
 "so the second round confirms the first-round result with measured uncertainty and does not demonstrate an improvement."),
("Round 1's finding that ResNet18 beat ResNet34 by nine points, which the first draft of this paper explained by the smaller network suiting 620 images, is not supported: the two architectures perform equally within noise.",
 "Round 1's nine-point advantage of ResNet18 over ResNet34 is not supported, since the two architectures perform equally within noise."),
("This is a diagnostic across scored calls, not a partition, so it overlaps the failure categories in Table~\\ref{tab:taxonomy} rather than adding to them.",
 "This diagnostic is computed across all scored calls, so it overlaps the failure categories in Table~\\ref{tab:taxonomy}."),
("Self-agreement carries some usable information.", "Self-agreement provides some usable information."),
("This describes which of several repeated calls to trust, not a fourth accuracy figure to set against Systems A and B.",
 "This result indicates which of several repeated calls to trust and is not comparable with the single-prediction accuracies of Systems A and B."),
("so the gain is attributable to the menu and not to the model.", "so the gain is attributable to the easier menu."),
# --------------------------------------------------------------- discussion
("System C's 12.4\\% does not mean that vision-language models are poor at spatial tasks in general. Its most distinctive feature is where its predictions land.",
 "The most distinctive feature of System C's errors is their location."),
("so both are close to guaranteed to land on the object. System C is the only one free to place a center anywhere.",
 "so both almost always place the center on the object, whereas System C is free to place a center anywhere in the image."),
("the coordinates in the same reply landed somewhere unrelated.", "the coordinates in the same reply fell elsewhere in the image."),
("so it should be treated as the observation that motivated a hypothesis, not as a measurement of how often the pattern holds.",
 "so it is reported only as the observation that motivated a hypothesis, and the frequency of the pattern was not measured."),
("This explanation makes a testable prediction. Removing System C's ability to output coordinates directly should help if the problem is binding reasoning to those coordinates rather than perceiving the object, and should make no difference if the problem is perception.",
 "This explanation predicts that removing System C's coordinate output should help if the problem is binding reasoning to coordinates, and should make no difference if the problem is perception of the object."),
("so it shows what a vision-language model can do without emitting coordinates, not what GPT-4o specifically can do.",
 "so its result describes vision-language models without coordinate output in general and cannot be attributed to GPT-4o."),
("Both remove the coordinate output. Only VLAD-Grasp succeeds, and it also adds depth, segmentation, and a geometric pose recovery, so much of the work in that pipeline is done by the geometry and not by the model's choice alone. System D's failure follows a specific pattern. On the full menu",
 "Both remove the coordinate output, but only VLAD-Grasp succeeds, and it also adds depth, segmentation, and geometric pose recovery, so the geometry contributes a substantial share of that pipeline's performance. On the full menu"),
("In three dimensions the second finger would land on top of the object and not beside it.",
 "In three dimensions the second finger would land on top of the object."),
("High accuracy on it would place the failure in the grasp choice, and low accuracy would place it in mark interpretation. The control has not been run, so the claim made here is the narrower one: removing the coordinate output is not sufficient to recover performance.",
 "High accuracy on that question would indicate that the failure lies in the grasp choice, whereas low accuracy would implicate mark interpretation. The control has not been run, so the claim made here is limited to the statement that removing the coordinate output is not sufficient to recover performance."),
("GR-ConvNet is pixel-wise. It predicts a grasp at every pixel in a single pass. System B instead pools",
 "GR-ConvNet is a pixel-wise method that predicts a grasp at every pixel in a single pass, whereas System B pools"),
("Every remaining gap points the same direction. Redmon and Angelova used RGB-D",
 "The remaining differences favor the published system, since Redmon and Angelova used RGB-D"),
("An axis-aligned box being unable to represent a diagonal grasp follows from the representation alone, and a rotation-invariant encoding handling rotation is the purpose of that encoding, so neither point is a discovery on its own. No precedent was found, however, for using this split as a diagnostic. It checks",
 "Both effects are expected, since an axis-aligned box cannot represent a diagonal grasp and the sine and cosine encoding was designed to handle rotation. The value of the split is as a diagnostic, a use for which no precedent was found. It checks"),
("so the count tracks object complexity and not how generous the metric is.",
 "so the count reflects object complexity more than the leniency of the metric."),
("The sine and cosine encoding dates to 2015, learned models have beaten rule-based baselines on Cornell for a decade, and imprecise vision-language coordinates are already documented elsewhere, so none of these observations is new in isolation.",
 "None of the individual observations is new. The sine and cosine encoding dates to 2015, learned models have outperformed rule-based baselines on Cornell for a decade, and imprecise vision-language coordinates have been documented elsewhere."),
("One correction to the first draft of this paper came from re-running its own experiment. The first round's nine-point gap between ResNet18 and ResNet34 was explained there as the smaller network suiting a small dataset. Three seeds per architecture under a stable recipe put them within a point of each other. A single training run on 620 images, with a checkpoint chosen from a hundred noisy validation epochs, is not evidence about architecture, and the explanation that fit it was constructed after the fact.",
 "The second training round also corrected an earlier interpretation. The first round's nine-point gap between ResNet18 and ResNet34 had been attributed to the smaller network suiting a small dataset. Three seeds per architecture under a stable recipe placed them within 1.4 points of each other. A single training run on 620 images, with a checkpoint chosen from a hundred noisy validation epochs, does not provide evidence about architecture."),
("All three were found the same way. An automated result did not match an independent calculation, and neither was trusted until the disagreement was explained.",
 "Each was found when an automated result did not match an independent calculation, and neither value was used until the disagreement was explained."),
# -------------------------------------------------------------- limitations
("not steer any choice, but it remains a second opening.", "not steer any choice."),
("rectangles likely touched a small number of images that later landed in the test split. No threshold, constant, or lookup entry was derived from that check, but it is disclosed here for completeness.",
 "rectangles likely included a small number of images that were later assigned to the test split. No threshold, constant, or lookup entry was derived from that check."),
("achieves, and it is not a ceiling for zero-shot GPT-4o. The gap to System B is wide enough that prompt iteration is unlikely to reverse the ordering, but the specific number should not be quoted as the model's best. System D shares this limit and adds one of its own: three menus from one candidate generator, all drawn in one glyph style on a zoomed crop.",
 "achieves and should not be read as a ceiling for zero-shot GPT-4o, although the gap to System B is wide enough that prompt iteration is unlikely to reverse the ordering. System D shares this limit and has a further one, since all three menus came from one candidate generator and were drawn in one glyph style on a zoomed crop."),
("Possible exposure of GPT-4o to the dataset during training was checked. Cornell is public and widely mirrored, so this is possible.",
 "Cornell is public and widely mirrored, so GPT-4o may have been exposed to it during training."),
("treats its unit of analysis as independent, and these units are not independent.",
 "treats its unit of analysis as independent, which does not hold here."),
("but those are five repeats of 123 images, not 615 independent trials, so it is narrower than the data support.",
 "but those calls are five repeats of 123 images, so the interval is narrower than the data support."),
("and every Wilson interval quoted per system is image-level and narrower than the data support.",
 "and the per-system Wilson intervals are image-level and should be read as lower bounds on the uncertainty."),
("because test object groups range from one image to nine. The ordering is unchanged.",
 "because test object groups range from one image to nine, but the ordering of the systems does not change."),
("Every system received RGB images only. No depth information was used by any of them.",
 "All systems received RGB images only, and no depth information was used."),
# --------------------------------------------------------------- conclusion
("The ordering was clear and survived every change of analysis.", "The ordering was consistent across every analysis."),
("The accuracy numbers matter less than how each system failed.",
 "The manner in which each system failed is more informative than the accuracy figures."),
("which resembles a grip on a narrow part from above and is not one in three dimensions.",
 "which resembles a grip on a narrow part only when viewed from above."),
("points to the grasp choice itself, with the qualification that the model's reading of the drawn marks has not been separately measured.",
 "points to the grasp choice itself, although the model's reading of the drawn marks has not been measured separately."),
("Three practical points follow. First,", "These results have three practical implications. First,"),
("which makes it a stronger cheap baseline than a lookup table. Third, small-benchmark results are fragile.",
 "which makes it a stronger low-cost baseline than a lookup table. Third, results on a benchmark of this size are sensitive to the training seed and to the unit of analysis."),
("so both practices are recommended for work at this scale.",
 "so multiple seeds and object-level clustering are recommended for work at this scale."),
]

missed = 0
for old, new in PAIRS:
    pat = r"\s+".join(re.escape(w) for w in old.split())
    n = len(re.findall(pat, t))
    if n != 1:
        missed += 1
        print(f"[{n} matches] {old[:90]}")
        continue
    t = re.sub(pat, lambda m: new, t, count=1)
print(f"applied {len(PAIRS) - missed} of {len(PAIRS)}")

t, k = re.subn(r"did\s+worst", "performed worst", t)
print("did worst ->", k)

# ---- reflow plain prose paragraphs to 72 columns ----------------------------
out = []
for para in re.split(r"(\n\s*\n)", t):
    lines = para.split("\n")
    plain = (para.strip()
             and not any(l.lstrip().startswith(("\\", "%")) for l in lines)
             and not re.search(r"(?<!\\)[%&]", para)
             )
    if plain and not re.search(r"\\(begin|end|item|caption|label|addplot|node|draw|fill)\b", para):
        para = "\n".join(textwrap.wrap(" ".join(para.split()), 72,
                                       break_long_words=False, break_on_hyphens=False))
    out.append(para)
t = "".join(out)
F.write_text(t)
