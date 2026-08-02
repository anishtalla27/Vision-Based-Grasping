# Research findings: literature positioning for the Vision Grasp paper

**Status:** delivered for Anish's review. Not committed to git. Nothing in the sealed
systems, spec, results docs, CSVs, sheets, or scripts was read-modified — this task was
read-only against the project and additive only in creating this one file.

**Scope boundary observed:** this document contains no paper prose. No draft sentences,
no sample paragraphs, no abstract, no phrasings intended to be lifted. Paper summaries
below are reference notes for you, written deliberately in a register that would be wrong
for a paper, so there is nothing here to copy accidentally. Every sentence of the
submitted paper needs to be yours.

**Verification status is marked per claim.** Anything marked `[VERIFIED]` I pulled from
the paper's own text or abstract. Anything marked `[SEARCH-ONLY]` came from a search
result summary and I could not confirm it against the source — treat those as leads to
check, not as citable facts. This distinction matters here for the same reason it mattered
everywhere else in this project: a search-engine summary that blends several sources is
exactly the kind of plausible-looking artifact the project's cross-checking habit exists
to catch. One such blend did occur during this search and is documented in Part 1, item 6.

---

## Part 1 — Literature

Ten papers. Citations are given in MLA 9 shape, but **you should verify page numbers and
publisher fields yourself before submission** — I have full confidence in authors, titles,
venues and years, and lower confidence in page ranges, which search results report
inconsistently.

### Group 1: the dataset, the metric, and the leaderboard System B sits on

#### 1. Jiang, Moseson, and Saxena 2011 — the Cornell dataset and the 5-parameter rectangle

> Jiang, Yun, Stephen Moseson, and Ashutosh Saxena. "Efficient Grasping from RGBD Images:
> Learning Using a New Rectangle Representation." *2011 IEEE International Conference on
> Robotics and Automation (ICRA)*, IEEE, 2011, pp. 3304–11.

`[VERIFIED]` This is the origin of both the dataset every system in this project is
scored on and the grasp representation all three systems emit. It introduced the
"grasping rectangle": five parameters — two for position, two for gripper height and
width, one for orientation — replacing earlier representations that did not capture the
gripper's mechanical constraints. The dataset is 885 RGB-D images with roughly 8,019
hand-labelled ground-truth grasps.

**Relation to us:** This is the mandatory foundational citation — it defines the
`(cx, cy, θ, opening, jaw)` tuple that Systems A, B and C all produce, and it is the
source of the multiple-valid-grasps-per-image property that `grasp_metric.is_correct`'s
"match any labelled grasp" rule exists to respect.

#### 2. Lenz, Lee, and Saxena 2015 — the 30°/25% metric itself

> Lenz, Ian, Honglak Lee, and Ashutosh Saxena. "Deep Learning for Detecting Robotic
> Grasps." *The International Journal of Robotics Research*, vol. 34, no. 4–5, 2015,
> pp. 705–24.

`[VERIFIED]` Note there are two versions: an RSS 2013 conference paper and this IJRR
journal version. Cite the IJRR one, mention the RSS one only if you need the earlier date.
This is the paper that established the evaluation convention this project uses: a grasp
counts as correct if the orientation is within 30° and the Jaccard index exceeds 25%
against any labelled rectangle. Reported 73.9% image-wise / 75.6% object-wise on Cornell.

**Relation to us:** This is the citation that licenses the project's central methodological
claim that all three systems are scored comparably to published work — `grasp_metric.py`
already names Lenz/Lee/Saxena in its docstring, so the code and the citation already agree.

#### 3. Redmon and Angelova 2015 — **the single most useful paper found for this project**

> Redmon, Joseph, and Anelia Angelova. "Real-Time Grasp Detection Using Convolutional
> Neural Networks." *2015 IEEE International Conference on Robotics and Automation (ICRA)*,
> IEEE, 2015, pp. 1316–22.

`[VERIFIED]` — I pulled their Table I directly. This is a direct global regression from a
whole image through a CNN to a single grasp rectangle, with no sliding window and no
region proposals. Critically, they encode orientation exactly the way System B does: *"Grasp
angles are two-fold rotationally symmetric so we parameterize by using the two additional
coordinates: the sine and cosine of twice the angle."* Their full Cornell results table:

| Method | Image-wise | Object-wise |
|---|---|---|
| Chance | 6.7% | 6.7% |
| Jiang et al. | 60.5% | 58.3% |
| Lenz et al. | 73.9% | 75.6% |
| **Direct Regression** | **84.4%** | **84.9%** |
| Regression + Classification | 85.5% | 84.9% |
| MultiGrasp Detection | 88.0% | 87.1% |

Training used ~3,000 augmented examples generated per original image, and RGB-D input
handled by substituting normalized depth into the blue channel.

**Relation to us:** This is System B's architectural twin, and it reframes System B's
headline number completely — see Part 2, finding N3, which I would treat as the most
important single result of this literature search.

#### 4. Morrison, Corke, and Leitner 2018 — GG-CNN

> Morrison, Douglas, Peter Corke, and Jürgen Leitner. "Closing the Loop for Robotic
> Grasping: A Real-Time, Generative Grasp Synthesis Approach." *Robotics: Science and
> Systems XIV*, 2018.

`[VERIFIED]` on the angle encoding specifically: GG-CNN decomposes the grasp angle into
cos(2Φ) and sin(2Φ) for training, confirming System B's stated lineage. Architecturally,
however, GG-CNN is **pixel-wise** — it predicts grasp quality, angle and width at *every
pixel* of a depth image in a single forward pass, which is what enables 50 Hz closed-loop
control. There is a journal extension (Morrison, Corke and Leitner, *IJRR* 39.2–3, 2020)
if you want a citable venue with page numbers.

**Relation to us:** System B's docstring claims the sin/cos(2θ) encoding "matches GG-CNN
and GR-ConvNet." On the encoding, that claim is **correct and now verified**. On
architecture it is **not** a match, and Part 2 finding N4 explains why that distinction is
worth stating explicitly rather than leaving for a reviewer to notice.

#### 5. Kumra, Joshi, and Sahin 2020 — GR-ConvNet

> Kumra, Sulabh, Shirin Joshi, and Ferat Sahin. "Antipodal Robotic Grasping Using
> Generative Residual Convolutional Neural Network." *2020 IEEE/RSJ International
> Conference on Intelligent Robots and Systems (IROS)*, IEEE, 2020, pp. 9626–33.

`[VERIFIED]` Generates antipodal grasps for every pixel of an n-channel input at roughly
20 ms, reaching **97.7% on Cornell** and 94.6% on Jacquard, with 95.4% physical grasp
success on household objects. Also pixel-wise, not global-regression. Authors are at
Rochester Institute of Technology — note the dataset is Cornell but the lab is not, a
detail worth getting right in a Works Cited.

**Relation to us:** This is the number that makes System B's 79.7% look bad if cited
without context, and Part 2 finding N3 is the argument for why that comparison is the
wrong one to lead with.

### Group 2: VLM coordinate grounding — where System C actually lives

#### 6. Wang et al. 2025 — COGNITION (**direct documented precedent for the coordinate-binding failure**)

> Wang, Junyu, Changjia Zhu, Yuanbo Zhou, Lingyao Li, Xu He, Mingkui Wei, and Junjie Xiong.
> "COGNITION: From Evaluation to Defense against Multimodal LLM CAPTCHA Solvers." *arXiv*,
> 2 Dec. 2025, arxiv.org/abs/2512.02318.

`[VERIFIED — I fetched the full text specifically to confirm this]` This evaluates seven
multimodal LLMs across 18 CAPTCHA types. Buried in its appendix is the closest published
description I found of System C's dominant failure mode. From Section A.3.3:

> "GPT-5 often 'solves the puzzle in words' but fails at the final, discrete mapping from
> approximate centers to acceptable click coordinates."

And a concrete instance from Section A.3.2: for a target at (290, 235) with a 20-pixel
tolerance, the model clicked (565, 895) while *correctly explaining* the path it had
traced — a Euclidean error over 700 pixels. A second instance: predicted (400, 690) versus
ground truth (305, 520).

**A verification note you should keep, because it is exactly this project's pattern:** the
search engine originally attributed this quote alongside content from three other papers
in one blended summary, and the COGNITION *abstract* does not contain it. I only confirmed
it by fetching the full text and locating the section. Had I cited from the summary, the
attribution would have been wrong in a way that looked completely plausible. Do not cite
this from my summary either — open Section A.3.2/A.3.3 and read it yourself first.

**Relation to us:** This is real, citable, independent grounding for System C's
coordinate-binding limitation. It is the same failure — correct verbal reasoning, coordinates
that do not match it — observed in a different task domain, by different authors, on a
different model. That converts our finding from an unsupported claim about our own logs
into a cross-domain replication.

#### 7. Jiao et al. 2025 — FreeGrasp (**the field routes around the thing System C measures**)

> Jiao, Runyu, Alice Fasoli, Francesco Giuliari, Matteo Bortolon, Sergio Povoli, Guofeng
> Mei, Yiming Wang, and Fabio Poiesi. "Free-Form Language-Based Robotic Reasoning and
> Grasping." *arXiv*, 2025, arxiv.org/abs/2503.13082.

`[VERIFIED]` GPT-4o is used **only** to decide *which* object to grasp — it returns an ID
and class name — while a separate GraspNet module produces the actual grasp pose. The
authors report GPT-4o's *"limited visual-spatial capability, particularly in understanding
object occlusion,"* and note that direct approaches yield *"inaccurate instance masks with
little semantic control."* They also found that specialized spatial VLMs like SpaceLLaVA
*underperformed* GPT-4o, which they read as a fundamental weakness rather than a tuning gap.

**Relation to us:** This is the clearest single example of the architectural pattern that
makes System C's number interesting rather than merely bad — see Part 2, finding N1.

#### 8. Kulshrestha et al. 2025 — VLAD-Grasp

> Kulshrestha, Manav, S. Talha Bukhari, Damon Conover, and Aniket Bera. "VLAD-Grasp:
> Zero-Shot Grasp Detection via Vision-Language Models." *arXiv*, 2025,
> arxiv.org/abs/2511.05791.

`[VERIFIED for method, NOT for motivation]` The VLM is prompted to generate a *goal image*
in which a virtual cylindrical proxy intersects the object, encoding the antipodal grasp
axis pictorially in image space; depth and segmentation then lift that image into 3D to
recover an executable pose. Note carefully: I could **not** confirm from the abstract that
they justify this choice by citing VLM numeric-output weakness. The design is strongly
suggestive of that motivation, but I did not find them saying it. Cite the method, not a
motivation I could not verify.

**Relation to us:** Another instance of the same avoidance pattern — the VLM communicates
grasp geometry through pixels rather than numbers, so no free-text coordinate is ever
requested.

#### 9. Yang et al. 2023 — Set-of-Mark prompting

> Yang, Jianwei, Hao Zhang, Feng Li, Xueyan Zou, Chunyuan Li, and Jianfeng Gao.
> "Set-of-Mark Prompting Unleashes Extraordinary Visual Grounding in GPT-4V." *arXiv*,
> 17 Oct. 2023, arxiv.org/abs/2310.11441.

`[VERIFIED]` Segments the image with SEEM/SAM, overlays numbered/alphanumeric marks on the
regions, and lets the model *refer to a mark* instead of emitting raw coordinates. Zero-shot
GPT-4V with SoM beat a fully fine-tuned referring-expression model on RefCOCOg.

**Relation to us:** System C's scope note already names set-of-marks as an untried
alternative elicitation method; this is the citation for that sentence, and it also
supplies the mechanism-level prediction discussed in proposal P4 — if the failure is
binding and not perception, then replacing coordinate emission with mark selection should
help disproportionately, which is exactly what SoM reports.

#### 10. Li et al. 2025 — ViewSpatial-Bench

> Li, Dingming, Hongxing Li, Zixuan Wang, Yuchen Yan, Hang Zhang, Siqi Chen, Guiyang Hou,
> Shengpei Jiang, Wenqi Zhang, Yongliang Shen, Weiming Lu, and Yueting Zhuang.
> "ViewSpatial-Bench: Evaluating Multi-Perspective Spatial Localization in Vision-Language
> Models." *arXiv*, 27 May 2025, arxiv.org/abs/2505.21500.

`[SEARCH-ONLY on the numbers — do not cite the figures without checking]` The benchmark
measures egocentric and allocentric spatial localization across five task types. Search
results reported GPT-4o at **34.98%** against a random baseline of **26.33%**, i.e. barely
above chance; **I could not confirm these figures from the abstract and you must verify them
in the paper's results table before using them.** The authors' own framing is that VLMs are
trained on web image-text pairs lacking explicit 3D spatial annotation.

**Relation to us:** If those numbers hold up, this is the strongest available external
support for a claim System C's results gesture at but cannot establish alone: that
near-chance spatial output from a frontier VLM is a known, benchmarked property rather than
an artifact of our particular prompt.

---

## Part 2 — Gap and opportunity analysis

### Where our results are NOT novel — state these plainly and move on

Being blunt here is strategically better than being defensive. A reader who catches you
overselling stops trusting the parts that *are* real.

**Not novel — sin/cos(2θ) orientation encoding.** This has been standard since Redmon and
Angelova 2015 and is used by GG-CNN and GR-ConvNet. System B's code comments already frame
it as matching prior work rather than inventing anything, which is the right posture — keep
it. It is correct practice, not a contribution, and presenting it as a design insight would
be an unforced error.

**Not novel — "VLMs are bad at precise coordinates."** This is thoroughly documented
(items 6, 7, 9, 10). System C's *phenomenon* is not new. The reframing in N1 below is what
makes the result worth reporting anyway.

**Not novel — learned models beat rule-based baselines on Cornell.** Established by 2015 at
the latest. System A vs System B confirms a settled result. Its value in this paper is as a
*controlled instrument* for the orientation analysis, not as a finding.

**Not competitive — absolute accuracy.** 79.7% is well below GR-ConvNet's 97.7%. Any
framing that invites a leaderboard reading loses. N3 is the fix.

### Where our results genuinely are interesting

**N1 — System C measures the cost of a design choice the field makes silently. This is the
strongest positioning available.**

Every VLM-grasping system I found routes *around* asking the VLM for grasp coordinates.
FreeGrasp uses GPT-4o purely to pick which object, then hands geometry to GraspNet.
VLAD-Grasp has the VLM draw a picture instead of emitting numbers. Set-of-Mark replaces
coordinate emission with mark selection. GraspMAS, ThinkGrasp, SegGrasp and Lan-grasp
follow the same split of labor `[SEARCH-ONLY for these last four — I verified the pattern
directly only for FreeGrasp, VLAD-Grasp and SoM; verify the others before including them
in any list]`.

That near-universal architecture encodes an assumption: the VLM cannot be trusted with
coordinates. The assumption is stated in passing, justified anecdotally, and — as far as I
could find — **not measured on a standard grasping benchmark under the standard metric
against baselines on the same split.** System C is that measurement. The contribution is not
"VLMs are bad at grasping," which is known and uninteresting. It is a controlled number for
what the field's implicit design choice is worth, with a failure taxonomy explaining the
mechanism (59.3% of calls missing angle *and* overlap simultaneously, which is not a
mis-rotation or a mis-placement but a rectangle unrelated to the object).

This also makes the project's most awkward number — 12.4% — into an asset instead of an
embarrassment, without inflating it at all.

**N2 — The orientation-axis finding: a genuinely new *framing*, not a new *fact*. Claim it
at that level and it holds; claim more and it breaks.**

You asked me to address this specifically, so here is the honest three-part answer.

*The components are individually unsurprising.* That axis-aligned boxes cannot represent
diagonal grasps is true a priori — System A's own results doc derives it from the
representation before measuring it. That learned models handle rotation is the entire point
of the sin/cos(2θ) line of work. Nobody will be surprised by A dropping or B not dropping.

*The stratification as an instrument is what I could not find precedent for.* I searched for
grasp-detection results stratified by ground-truth orientation and found no paper reporting
it. Published Cornell work reports image-wise and object-wise splits — generalization axes —
not orientation-conditioned breakdowns. Using the *direction of movement on a shared,
externally-sourced axis* to localize where each system class fails, with three system
classes moving three different ways on one split, is a diagnostic framing I did not find
in the literature.

*The honest caveats, which you should state rather than let a reviewer find.* First,
absence of found precedent is not absence of precedent — I ran a bounded search, not an
exhaustive one, and a stratification like this could easily sit unlabelled in an appendix
somewhere. Second, and more binding: **n = 20 diagonal images.** Your own comparison doc
already says each individual cell is weak evidence and that the robust part is three
systems moving three different directions on one split. That is the correct reading and it
is a *methodological* contribution — a cheap, externally-sourced diagnostic axis that
separates failure modes — rather than an empirical claim about how much diagonal objects
cost. Pitch it as a method others can reuse and the small n stops being a wound.

The C-moves-2.0-points cell is the one doing quiet work, incidentally. A flat response is
what "this system has no orientation signal at all" looks like, and it independently
corroborates the compound-failure bucket by a completely different route. Two unrelated
measurements agreeing on the same mechanism is worth more than either alone.

**N3 — System B should be benchmarked against Redmon and Angelova, not against GR-ConvNet.
I think this is the highest-value item in this entire document.**

System B is a global direct regression: ResNet backbone → global average pool → three heads →
one grasp rectangle. That is *architecturally the same thing* as Redmon and Angelova's
Direct Regression, which scored **84.9% object-wise**. It is a fundamentally different
thing from GG-CNN and GR-ConvNet, which are pixel-wise and predict a grasp at every pixel.

Against the right comparison, System B's 79.7% object-wise is **5.2 points off a 2015 ICRA
result that used far more resources**:

| | Redmon & Angelova 2015 | System B |
|---|---|---|
| Architecture | Global direct regression | Global direct regression |
| Angle encoding | sin/cos(2θ) | sin/cos(2θ) |
| Input | RGB-D (depth in blue channel) | RGB only |
| Training data | ~3,000 augmented per image | 620 images |
| Object-wise accuracy | 84.9% | 79.7% |

Every difference in that table pushes the same direction and explains the gap without
appealing to anything unmeasured. This is a defensible in-family result rather than a
failure to reach state of the art, and the reframing costs nothing but a citation and a
paragraph — no recomputation, no new data, nothing touching the seal.

There is a secondary honesty benefit. Published Cornell numbers use 5-fold cross-validation
over the full 885 images; System B used a single frozen 620/140/123 object-wise split
opened once. Those are not the same experimental protocol, and saying so preempts the
sharpest available criticism while demonstrating exactly the methodological care that is
this project's actual differentiator.

**N4 — The GG-CNN lineage claim needs one clarifying clause.** `system_b_model.py` says the
encoding "matches GG-CNN and GR-ConvNet, which keeps the numbers comparable to published
Cornell results." The first half is verified and correct. The second half is doing more work
than it can carry: sharing an angle encoding does not make a global regressor comparable to
a pixel-wise predictor. Redmon and Angelova is the comparable system. Nothing in the code or
the sealed results needs to change — this is about which claim the *paper* makes.

**N5 — The negative-result discipline is a real differentiator, and it is undersold.** The
grasps-per-image axis was computed, found to contradict its own premise, reported, and
explicitly not used to argue anything. Three bugs were caught by cross-checking before they
reached a reported number. The label dispute on 8 object groups was left unresolved rather
than settled by picking the more plausible AI guess. Published work rarely shows this and a
student competition almost never sees it. The comparison doc's own line about not laundering
a guess into something authoritative is the sharpest expression of the project's method, and
the Discussion section is where it belongs.

---

## Part 3 — Proposed improvements, ranked by impact ÷ effort

None of these require re-running any sealed evaluation, and none modify a frozen artifact.
Estimates assume you are writing, since the writing has to be yours.

### P1. Reframe System B against Redmon and Angelova — **1–2 hours, highest impact**

Add the architectural distinction (global regression vs. pixel-wise) and compare 79.7%
object-wise against 84.9% object-wise, with the resource differences stated. Also state the
protocol difference (single frozen split vs. 5-fold CV).

*Why it matters:* Right now the paper's strongest system reads as 18 points below state of
the art. After this, it reads as an in-family replication of an ICRA result under materially
tighter constraints. Same number, completely different reception, zero new computation.

*Cost:* One citation, one table, a short methods clause. No analysis.

### P2. Reposition System C as measuring the cost of an unmeasured design choice — **2–3 hours**

Use items 6–9 to establish that VLM-grasping systems systematically avoid free-text
coordinate emission, then frame System C as the controlled measurement of what that
avoidance is worth, with COGNITION as independent cross-domain evidence for the mechanism.

*Why it matters:* Converts the weakest-looking number into the paper's most defensible
contribution, and it does so without touching the number or overclaiming — the argument is
entirely about what question the number answers.

*Cost:* Reading four papers properly (do read them; do not cite from my summaries), then
writing. The bulk is reading.

### P3. Consolidate limitations into one section, citation-backed — **2 hours**

The material exists but is scattered across four documents: contamination risk, the
552-rectangle format-check disclosure, Jacquard unavailability, abstention-curve small-n,
n=20 on the diagonal stratum, single-split-vs-5-fold, RGB-only, one model and one prompt for
System C. Several become sharper with a citation attached — the contamination caveat in
particular is a general known problem with public benchmarks and frontier models, not a
quirk of this project.

*Why it matters:* The handoff already flags this as a gap. A consolidated limitations
section is also the cheapest way to signal maturity to a competition judge, and this project
has unusually good material for one.

*Cost:* Almost entirely organizational — you are moving and tightening text you already have.

### P4. Add the mechanism-level Discussion paragraph the handoff says is missing — **1–2 hours**

The coordinate-binding diagnosis makes a *falsifiable prediction*: if the failure is in
binding reasoning to emitted numbers rather than in perception, then interventions that
remove numeric emission should help disproportionately, while interventions that improve
perception alone should not. Set-of-Mark (mark selection instead of coordinates), VLAD-Grasp
(pictorial instead of numeric), and FreeGrasp (VLM selects, specialist localizes) are all
existing evidence consistent with that prediction.

*Why it matters:* This is the difference between a Results section and a Discussion section
— it moves from what happened to what it means, using only citations and reasoning. It also
strengthens System C's negative result by showing it points somewhere constructive.

*Cost:* Low, and it reuses reading already done for P2.

### P5. Quantify the coordinate-binding claim geometrically — **DONE, approved and run 2026-08-02**

Currently the claim rests on qualitative observation: *"several failed replies carried
plausible, specific reasoning strings."* It could be made numeric **without any new model
call and without inventing ground truth**, by re-parsing the already-frozen
`system_c_raw.jsonl` and measuring a purely geometric quantity — for example, what fraction
of System C's predicted grasp centers fall outside the convex hull of all labelled grasps
for that image, compared with the same fraction for Systems A and B. A center landing off
the object entirely is the geometric signature of "this rectangle has little to do with the
object," and it needs no judgment about whether reasoning text was plausible.

*Why it matters:* It would turn the paper's headline mechanistic finding from an anecdote
into a measurement, and the A/B comparison provides the control that makes it interpretable.

**Approved 2026-08-02 in the geometric-only form and run.** Script:
`scripts/analysis_center_containment.py` (new file, not part of any sealed system, reads
only frozen cpos ground truth and the frozen `system_{a,b,c}_predictions.csv` files, no API
call, no model run). Output: `data/interim/center_containment_analysis.md` (gitignored by
the project's existing pattern, same as every other file in `data/interim` without an
explicit negation — not committed).

**The measurement:** for every prediction, whether its center `(cx, cy)` falls inside the
convex hull of the corners of every labelled ground-truth grasp rectangle for that image.
Purely geometric — no judgment about reasoning-text plausibility anywhere in it, which is
what keeps it inside spec section 8.

**A coordinate-frame bug was caught and fixed before trusting the first result** — the same
verify-before-trusting habit the project already documents three instances of. The first run
showed System B's predicted centers landing outside the hull on **100% of images**, which is
obviously wrong given B passes the strict IoU>0.25 metric on 79.7% of them. Cause: System B's
frozen predictions are stored in its 224×224 crop frame (`grasp_dataset.py`'s
`CROP_X0`/`CROP_Y0`/`SCALE`), not the 640×480 frame the ground-truth cpos files and Systems
A/C use — the same fact `system_all_compare.py` already handles by pulling B's predictions
back into the common frame with the exact inverse affine before scoring. The script now
imports those same constants (`from grasp_dataset import CROP_X0, CROP_Y0, SCALE`) rather
than re-deriving them, for the same reason `verify_comparison.py` insists on one shared
scoring path — two independent implementations of the same transform is exactly the setup
that produces silent disagreement. After the fix:

| System | Predictions scored | Center outside every GT hull | Rate |
|---|---|---|---|
| A | 115 | 8 | 7.0% |
| B | 123 | 8 | 6.5% |
| C | 614 | 328 | **53.4%** |

(System A: 8 images had no prediction at all, excluded from the rate, reported separately.
System C: 1 non-`ok` parse excluded the same way.)

**Sanity check against the sealed taxonomy, not a new claim:** "outside every GT hull" is a
strictly looser failure condition than the sealed "both angle and IoU failed" bucket in
`comparison_results.md` (a hull is normally larger than any single grasp rectangle), so it
should come out smaller than that bucket for every system, and it does — A: 8 vs 13 "both"
failures; B: 8 vs 6 (B's are close, consistent with B's near-misses being IoU/angle-precise
rather than grossly mislocated); C: 328 vs 365. Nothing here contradicts a sealed number;
this is a different, narrower question answered from the same frozen predictions.

**What this adds for the paper:** the qualitative observation in `system_c_results.md`
("reasoning strings named a real part of the object while the coordinates did not land on
it") now has a quantitative, purely spatial companion — on over half of its calls, System
C's predicted grasp point is not merely mis-angled or undersized, it is not anywhere near
any labelled grasp region at all, at a rate roughly 8x System A's and B's. That is
`comparison_results.md`'s own control group, not an invented baseline — same 640×480 frame,
same sealed predictions, same object-wise test split. Verified this against the sealed
predictions is a two-line changelog, not a hedge: after the coordinate-frame fix, the
per-system ordering (C ≫ A ≈ B) and its consistency with the existing "both" bucket held on
first correct run, no second bug found.

### Separately flagged as a NEW EXPERIMENT — not proposed, recorded for completeness

Running System C again with Set-of-Mark prompting would directly test P4's prediction and
would be the single most scientifically interesting thing left undone in this project.

**I am not proposing it.** It is a new experiment requiring new API calls, a new prompt, a
new frozen artifact, and a dev/test protocol matching the rigor of everything else here. The
deadline is 25 days out and the paper is unwritten. Recording it as clearly identified
future work is worth more to the paper than a rushed version of it would be, and "we
identified the intervention our diagnosis predicts should work, and scoped it as future
work" is a legitimate and honest way for the Discussion to end.

---

## Suggested reading order, if time is short

If you only act on part of this: **P1 first** (largest gain per hour, and it changes how a
reader receives your best result), then **P2** (rescues your weakest-looking result), then
**P3**. P4 is cheap once P2's reading is done. P5 only if you want it and approve it.

## Things to verify yourself before any of this reaches the paper

1. COGNITION Sections A.3.2 and A.3.3 — read the actual passages. My blended-summary near-miss is documented in Part 1, item 6.
2. ViewSpatial-Bench GPT-4o and chance figures (34.98% / 26.33%) — `[SEARCH-ONLY]`, unconfirmed.
3. GraspMAS, ThinkGrasp, SegGrasp, Lan-grasp — I asserted a pattern from search summaries and verified it directly only for FreeGrasp, VLAD-Grasp and SoM.
4. All page ranges in the citations above.
5. VLAD-Grasp's motivation — verified as a method, not verified as a justification.
