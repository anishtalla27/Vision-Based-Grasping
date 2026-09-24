# ICDM 2026 Teen Track: Camera-Ready Plan (S30345)

> **Status (24 Sept 2026): implemented.** Every item in sections 1 to 4 is in
> `icdm2026_teen.tex`, the PDF is built at `final_submission/icdm2026_teen.pdf`
> (5 pages), and the point-by-point response is in
> `reviewer_feedback_2026-09-24.md`. The numbers in section 3 came out as:
> orientation ceiling 118/123 (95.9%) within 30 deg and 103/123 (83.7%) within
> 15 deg; clean System A CI [28.0, 53.2]; B minus clean A +39.0 [25.2, 52.9],
> p < 0.0001; clean A minus one-call C +28.3 [16.9, 40.0], p = 0.0001; clean A
> minus best-of-five C +5.7 [-6.1, 18.0], p = 0.45. `review_tracking.csv` was
> not in the Drive backup, so the 251 manually reviewed boundaries are reported
> instead of the assistant's uncertain-call count. Remaining: registration, the
> camera-ready form when the instructions email arrives, and the poster.

Accepted 24 Sept 2026. Camera-ready due **4 Oct 2026, 11:59 p.m.** (10 days).
Hard limits: IEEE Computer Society proceedings template, **5 pages including
figures, tables, and references**. Working file: `icdm2026_teen.tex`. Build
output goes to `final_submission/icdm2026_teen.pdf`.

Reviewers read **v1** (`icdm2026_teen_v1_submitted_2026-08-30.tex`), which had
no System D and no round-2 training results. The current tex (v2, 13 Sept)
already contains both. So some review points are already answered and only
need to be made visible; others need new text, new numbers, or a rerun.

---

## 1. Triage: what each reviewer point needs

| # | Reviewer point | Raised by | Status in v2 | Action |
|---|---|---|---|---|
| 1 | Coordinate-binding hypothesis is speculative / underspecified | R1, R4 | **Already tested by System D**, which rejected it | Make this the spine of the paper: intro, abstract, discussion all say "hypothesis proposed, tested, rejected" |
| 2 | Title over-generalizes "vision-language" | R4 | Not done | Put GPT-4o in the title and abstract sentence 1 |
| 3 | 57.7% is post-hoc but still used in the stats comparisons | R3 | Not done | Rerun the paired stats against the clean 40.7%; report 57.7% comparisons only as post-hoc, or drop them |
| 4 | Systems get unequal supervision and unequal tuning; "unified" means I/O + metric only | R1, R3 | Partly (limitations paragraph) | State it once, up front, in the intro; keep the limitations sentence |
| 5 | Motivation unclear, no explicit comparison to prior studies | R2 | Weak | Rewrite intro paragraph 1 and 4; add one sentence per related-work item saying what this paper does differently |
| 6 | Too many variables; pick one or two focal factors and name them in the intro | R2 | Not done | Name two: (a) the output interface (coordinates vs. menu) and (b) orientation handling. Everything else is context |
| 7 | Discuss practical application of the conclusions | R2 | Not done | One short paragraph at the end of Discussion |
| 8 | Two-orientation constraint is a design limit; report the fraction of test images with a label within ±15° of 0°/90° | R4 | Not done | Compute from Cornell labels (needs raw data, see section 3) and add one sentence |
| 9 | Say why the 2 dropped images were unresolvable | R1, R4 | Not done | Answer is in `source_of_truth.md` 10.3 item 5: two boundaries had no directional lean after full manual review, so one image on the smaller side of each was excluded rather than guessed. Neither was an annotation error |
| 10 | Give the number of uncertain boundary calls | R4 | Not done | 251 boundaries were manually decided (`boundary_decisions.csv`: 478 auto-same, 155 auto-different, 251 manual; the ambiguous band was 28.4% of boundaries). The exact count of the model's "uncertain" calls is in `review_tracking.csv`, which is not in the repo. Recover it from the Drive backup; if not recoverable, report the 251 manual figure and the 28.4% band |
| 11 | Acknowledgment duplicated, badly typeset, and vague on student vs. AI division | R3, R4 | Duplicate is gone in v2, but the wording is still vague | Rewrite as a clear two-part statement (section 4) |
| 12 | 79.7% is competitive with RGB-only literature | R4 | Not done | One clause in Results, with a citation |
| 13 | Small sample, wide CIs | R4 | Acknowledged | Keep the existing sentence; no new work |
| 14 | Narrow evaluation (one dataset, one split, one VLM, one prompt, RGB, no robot) | R3 | Acknowledged | Keep; already listed in Limitations |
| 15 | Contribution is a benchmark, not a new method | R1, R3, R4 | n/a | Do not fight this. Frame the contribution honestly as "controlled comparison plus a hypothesis test that reversed my own explanation." That is what R4 valued |

Score pattern to keep in mind: presentation was rated good by all four, so do
not restructure heavily. Novelty was rated marginal by all four; the System D
hypothesis test is the only genuinely new material and should be the thing a
skimming reader sees first.

---

## 2. Text changes, by section

### Title
Change to:
> Benchmarking Rule-Based, Learned, and Zero-Shot GPT-4o Grasp Prediction Under a Unified Evaluation Protocol

(Alternative if the chairs want the original kept close: keep the title and
add "(GPT-4o)" after "Vision-Language".)

### Abstract
- Sentence 1 names GPT-4o explicitly.
- Add "under the same input, output format, and metric, but not the same supervision or tuning budget" so the "unified" scope is clear from the first paragraph.
- Keep the System D sentences; they are the strongest part.
- Make sure the abstract gives 40.7% first and 57.7% second, labeled post-hoc.

### Introduction
- Paragraph 1: motivation. Say why anyone would compare these three: they are the three cheapest starting points a practitioner actually has, and published numbers for them are not comparable because each paper changes the input, output, or metric.
- New paragraph 2: name the two focal factors (R2 #2). (a) The output interface: does a VLM fail because it cannot emit pixel coordinates, or because it chooses the wrong grasp? (b) Orientation: a two-angle rule vs. a continuous regressor. Say that all other differences (supervision, tuning, detector assistance) are held as context and listed as limitations, not as controlled variables.
- Add one sentence defining "unified" narrowly: same 123 RGB images, same rectangle output, same scoring code. Not equal supervision, not equal development effort (R1, R3).
- Contribution list, three bullets: (1) the controlled comparison and object-wise split, (2) the shared failure taxonomy and center-hull check, (3) a hypothesis test (System D) whose result overturned the paper's own first explanation.

### Related Work
- After each cited method add one clause saying what this paper does differently (R2 #1). Redmon and Angelova: RGB-D, this is RGB only. GR-ConvNet: dense output, this is one rectangle. Set-of-Mark and VLAD-Grasp: scaffold the VLM, System C does not and System D scaffolds it in the simplest possible way.

### Experimental Design
- Dataset paragraph: add the reason for the two dropped images (item 9) and the boundary counts (item 10).
- System A: add the orientation ceiling number (item 8): "X% of test images have at least one labeled grasp within 15° of 0° or 90°, so the two-orientation rule can pass at most X% in principle."
- System B: add "compared with one frozen prompt for C and D" here as well as in Limitations, so the budget asymmetry is stated where the tuning is described.

### Results
- Table 2 (accuracy): add a row "A: heuristic, pre-correction, 40.7%" with its CI, above the corrected row. Mark the corrected row "post-hoc".
- Paired comparisons paragraph: lead with the clean comparisons (B vs. A at 40.7%, A at 40.7% vs. C). Give the 57.7% comparisons in one sentence explicitly labeled post-hoc, or cut them if space is tight.
- Table 3 (taxonomy): decide whether column A shows 40.7% or 57.7% outcomes. Recommendation: keep 57.7% in the table (it is the failure pattern the paper discusses) and say in the caption that it is the post-hoc configuration. If the pre-correction per-image outputs can be regenerated, add a second A column.
- Add the RGB-only literature clause (item 12) after the 79.7% figure.

### Discussion and Limitations
- Restate the coordinate-binding hypothesis as "the explanation I proposed first" and System D as the test that rejected it. Add one sentence listing the alternative R4 raised (the model may not understand the coordinate frame or image scale) and note that System D removes coordinates entirely, so that alternative is also ruled out as the sole cause.
- New paragraph, practical implications (R2 #3), about 80 words: a label-free short-axis rule from segmentation matches the detector heuristic at near-zero cost and is the right first baseline; a fine-tuned ResNet is the right choice when a few hundred labels exist; a raw-coordinate VLM query should not be used as a grasp planner, and menu-style scaffolding does not fix it on its own with this model.
- Keep the budget-asymmetry and two-openings sentences.

### Conclusion
- Tighten to fit. Move the "cheapest system to build" claim to the implications paragraph so it is not said twice.

### Acknowledgment
See section 4.

---

## 3. Numbers to compute or recover

| Item | Where it comes from | Blocker |
|---|---|---|
| ±15° orientation ceiling for System A | New script `scripts/analysis_orientation_ceiling.py`: for each test image in `final_split.csv`, load positive rectangles via `cornell_data.py`, check if any label angle is within 15° of 0° or 90° (mod 180). Report count / 123 and also the ±30° version, since 30° is the metric's own tolerance | Raw Cornell data is not on this machine (`data/raw/` is absent). Pull from the Drive backup or the Hugging Face fallback first |
| Clean paired stats at 40.7% | `object_clustered_stats.py` reads `comparison_per_image.csv`, whose `a_correct` column is the corrected run. Commit `afcd99a` only added the script, not the predictions, so the pre-correction per-image results were never committed | Rerun `system_a_run.py` as of commit `afcd99a` (checkout that script version, same frozen table) on the test split, save to `system_a_predictions_precorrection.csv`, then add an `a_pre_correct` column to the comparison CSV and run the stats script once more. Needs raw data and the detector weights. Fallback if this cannot be done in time: report the 40.7% point estimate with a clustered CI computed from the 50-correct count if the per-image correctness list can be reconstructed from the `system_a_sheets` images; otherwise state plainly that clustered CIs exist only for the post-hoc run |
| Uncertain boundary call count | `data/interim/review_tracking.csv` (referenced in `source_of_truth.md` 10.4, not in the repo) | Look in the Drive backup. Fallback: report 251 manual decisions and the 28.4% ambiguous band |
| Dropped image IDs and reason | Already known: 0435 and 0782, `source_of_truth.md` 10.3 item 5 | None |
| RGB-only literature comparison | Find one citable RGB-only Cornell object-wise number (Kumra and Kanan 2017 report RGB-only ResNet results; Redmon and Angelova 2015 report RGB-only variants) | Verify the exact figure before citing. Do not quote from memory |

---

## 4. Acknowledgment rewrite

Reviewers 3 and 4 both flagged this. The track requires the student to be the
primary contributor, so the split has to be concrete. Draft:

> **Acknowledgment.** I designed the study, chose the three systems and the
> evaluation protocol, built the object-wise split and audited its ambiguous
> boundaries, ran and checked every experiment, verified all numerical claims
> and citations, and wrote and approved the final text. AI coding assistants
> (OpenAI Codex, Anthropic Claude Code) were used as tools under my direction:
> Codex for editing and shortening the manuscript from my draft and results,
> Claude Code for implementation help on scripts, for a logged first pass on
> ambiguous object boundaries that I then reviewed in full, and for
> implementing the second training round and the System D harness to my
> specification. GPT-4o is not an assistant here; it is the model evaluated
> as Systems C and D.

Typeset it as a single `\section*{Acknowledgment}` paragraph. Check the PDF
for a stray line break after "Section" (that was the fragment R4 saw).

---

## 5. Space budget

v2 already fills 5 pages. Everything above is net additive (roughly 250 to
350 words plus one table row). Cuts to make room, in order of preference:

1. Trim System D method paragraph 2 (the three-menu description) by about a third; the table carries it.
2. Drop the per-object equal-weight numbers (51.3 / 75.4 / 10.5) to one clause.
3. Merge the round-2 System B paragraph in Results into three sentences: what changed, 84.0% with CI, and that the 79.7% vs. ResNet34 gap was seed noise.
4. If still over: drop Figure 1 to `width=0.85\columnwidth`, or move the split table (Table 1) into one sentence of prose (164/620, 35/140, 35/123).
5. Last resort: shorten bibliography entries (remove page ranges).

Do not cut: the failure taxonomy table, the System D table, the 40.7 vs 57.7
distinction, or the limitations paragraph. R4 named all of these.

---

## 6. Work order and schedule

| Day | Task |
|---|---|
| 25 Sept | Recover raw Cornell data and `review_tracking.csv` from Drive. Write and run the orientation-ceiling script. Commit script and output |
| 26 Sept | Reproduce the pre-correction System A run at commit `afcd99a`; produce per-image CSV; rerun clustered stats with the clean 40.7%. Commit results to `data/interim/` |
| 27 Sept | Text edits: title, abstract, intro (focal factors, contribution list, "unified" definition), related work clauses |
| 28 Sept | Text edits: design section additions, results table and stats paragraph, discussion rewrite, implications paragraph, acknowledgment |
| 29 Sept | Compile, measure pages, apply cuts from section 5 until it fits 5 pages. Check every number in the text against `data/interim/` |
| 30 Sept | Full read for consistency: every place 57.7 appears is labeled post-hoc; every place "VLM" appears in a claim is qualified as GPT-4o; no em dashes; no orphan lines |
| 1 Oct | Second build, PDF check (fonts embedded, IEEE template compliance, 5 pages). Save as `final_submission/icdm2026_teen.pdf`. Diff against v2 and record changes in `reviewer_feedback_2026-09-24.md` under a "Response" heading |
| 2 to 3 Oct | Buffer. Handle the camera-ready instructions email (copyright form, registration). Start the poster from the same figures |
| 4 Oct | Submit before 11:59 p.m. |

Also required by the acceptance email, outside the paper itself:
- At least one author registered for the conference.
- A poster, presented in person in Shenyang by a high school author. Start it once the camera-ready is locked; reuse Figure 1, Table 2, Table 3 and the System D table.

---

## 7. Verification checklist before submission

- [ ] Page count is 5 or fewer including references
- [ ] Title and abstract sentence 1 say GPT-4o
- [ ] Every 57.7% is labeled post-hoc; every statistical comparison in the results text uses 40.7% or is explicitly labeled post-hoc
- [ ] Orientation ceiling figure appears and matches the script output
- [ ] Dropped-image reason and boundary counts appear in the dataset paragraph
- [ ] Two focal factors named in the introduction and answered in the conclusion
- [ ] Practical-implications paragraph present
- [ ] Acknowledgment is one clean paragraph with the student/AI split
- [ ] Every number in the tex matches a file in `data/interim/`
- [ ] No em dashes anywhere in the tex
- [ ] `reviewer_feedback_2026-09-24.md` has a response table mapping each point to the change made
