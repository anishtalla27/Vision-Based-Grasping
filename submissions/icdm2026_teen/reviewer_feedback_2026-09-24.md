# ICDM 2026 Teen Research Track — Reviewer Feedback (S30345)

Accepted 24 Sept 2026. Camera-ready due **4 Oct 2026, 11:59 p.m.**
IEEE Computer Society template, **5 pages max including figures, tables, references.**

## Scores at a glance

| Reviewer | Relevant | Innovation | Tech quality | Presentation | Recommendation | Confidence |
|---|---|---|---|---|---|---|
| R1 | Yes | -2 marginal | -2 marginal | 3 good | 3 weak accept | High |
| R2 | **No** | -2 marginal | -2 marginal | 3 good | **2 weak reject** | High |
| R3 | Yes | -2 marginal | -2 marginal | 3 good | 3 weak accept | High |
| R4 | Yes | -2 marginal | **3 high** | 3 good | 3 weak accept | Medium |

**Overall pattern:** presentation is good. All four reviewers rate novelty as marginal, because the paper benchmarks existing methods rather than proposing a new one. Three of the four also rate technical quality as marginal. R4 was very positive about rigor and honesty.

---

## Reviewer 1 (weak accept)

1. **The systems aren't on equal footing.** ResNet18 is trained on Cornell grasp labels, and the heuristic gets detection and segmentation for free. GPT-4o gets no grasp training and no spatial help. So the paper compares three complete pipelines. It doesn't isolate rule-based vs. learned vs. VLM *reasoning*.
2. **The coordinate-binding explanation is speculative.** The paper never separately tests whether GPT-4o picks the right region in words and whether it can produce the right coordinates.
3. **Object identities rely partly on manual decisions.** The automated procedure agreed only 40% of the time on uncertain boundaries.

## Reviewer 2 (weak reject)

Strengths: the topic is important, and the results are counterintuitive and interesting.

1. **Motivation and prior work.** Explain more clearly why this study was done, and compare explicitly with earlier studies so the contribution stands out.
2. **Too many variables.** Too many factors differ among the three systems. Pick one or two factors to analyze, and put them up front in the introduction.
3. **Applications.** Add a discussion of how these conclusions would be used in practice.

## Reviewer 3 (weak accept)

1. **The contribution is modest.** It is a unified comparison plus error analysis, not a new model or learning principle.
2. **Post-hoc contamination of System A.** System A was changed after its test predictions had been inspected. The paper labels 57.7% as post-hoc and 40.7% as the clean result, which is good, but **several statistical comparisons still use 57.7%**. Keep the two numbers clearly separate, and base the clean comparisons on 40.7%.
3. **Evaluation is narrow.** One small dataset, one split, one VLM, one prompt, RGB only, and no robot. The paper acknowledges this, but it limits how general the conclusions can be.
4. **Development budgets differ.** System B got several architectures and validation tuning, while GPT-4o got one frozen prompt. "Unified" really means the same input/output and the same metric, not equal tuning.
5. **The acknowledgment is duplicated and badly typeset.** The track requires the student to be the primary contributor, so state exactly what you did vs. what AI tools (Codex, Claude Code) did.

## Reviewer 4 (weak accept, very positive)

**Praise:** the methods are unusually careful, and the reviewer says the paper wouldn't look out of place at a regular vision or robotics venue. They singled out:
- the fixed input, output, and metric across all three systems,
- the object-wise split and the asymmetric threshold logic,
- the object-clustered bootstrap and the paired permutation test,
- reporting both pooled-call and best-of-five results for GPT-4o, and not retrying parse failures,
- the failure taxonomy and the center-hull check (53.4% vs. 7.0% / 6.5%),
- honest reporting of 40.7% vs. 57.7% and disclosure of the formatting check.

**Concerns:**
1. **Title overreach.** Add "GPT-4o" to the title, or at least to the first sentence of the abstract, so readers don't generalize to all VLMs.
2. **The coordinate-binding hypothesis is underspecified.** The evidence is informal (you read the rationales). The 53.4% out-of-hull rate fits it, but so does another explanation: GPT-4o may not understand the coordinate system or the image scale. Frame it as one of several possible explanations until the Set-of-Mark follow-up is done.
3. **System A's two orientations are a design constraint, not a finding.** Report what fraction of Cornell test images have a labeled grasp within ±15° of 0° or 90°, which is System A's theoretical ceiling.
4. **No depth input.** This is fine and already stated. Note that 79.7% is competitive with RGB-only results in the literature.
5. **Sample size.** 123 images from 35 objects gives wide confidence intervals (for example, GPT-4o [8.0, 17.4]). This is adequate for now, but a future extension should use a bigger evaluation.

**Minor:**
- Say why the 2 dropped images couldn't be resolved: ambiguous segmentation or annotation error?
- Give the **number of uncertain boundary calls**, alongside 86.7% agreement on confident cases and 40.0% on uncertain ones.
- The acknowledgment ends with a duplicated fragment ("GPT-4o was evaluated separately as System C in Section…"). Clean it up.

---

## Consolidated fix list (for the camera-ready)

| # | Fix | Raised by | Effort |
|---|---|---|---|
| 1 | Add **System D** results: it separates region choice from coordinate generation and came out at chance level, which overturns the coordinate-binding hypothesis. Reframe the discussion around it. | R1, R4 | Medium (space) |
| 2 | Add "GPT-4o" to the title and the first sentence of the abstract | R4 | Trivial |
| 3 | Rewrite the acknowledgment: remove the duplicate, fix the typesetting, and give a clear split of student vs. AI work | R3, R4 | Small |
| 4 | Use the clean 40.7% for System A in the stats comparisons; mark 57.7% as post-hoc only | R3 | Small (rerun stats) |
| 5 | State that "unified" means same I/O + metric, not equal supervision or tuning; acknowledge the different budgets | R1, R3 | Small |
| 6 | Intro: sharper motivation, explicit comparison to prior work, and one or two focal factors named up front | R2 | Medium |
| 7 | Add a short practical-implications paragraph | R2 | Small |
| 8 | Report the % of test images with a grasp within ±15° of 0°/90° (System A's ceiling) | R4 | Small (compute) |
| 9 | Give the number of uncertain boundary calls and the reason the 2 images were dropped | R1, R4 | Trivial |
| 10 | Note that 79.7% is competitive with RGB-only literature results | R4 | Trivial |
| 11 | Decide how to report the System B multi-seed rerun (84.0% ResNet34); suggest keeping 79.7% as the headline plus a robustness note | — | Decision |

Everything must still fit in **5 pages**, so adding System D means cutting elsewhere.

---

## Response: what changed in the camera-ready (implemented 24 Sept 2026)

Working file: `icdm2026_teen.tex`. Built PDF: `final_submission/icdm2026_teen.pdf` (5 pages, IEEE CS conference template). New evidence files: `data/interim/orientation_ceiling.md`, `data/interim/system_a_predictions_precorrection.csv`, and an addendum in `data/interim/object_clustered_results.md`. New scripts: `scripts/analysis_orientation_ceiling.py`, `scripts/system_a_run_precorrection.py`.

| Point | Raised by | Change |
|---|---|---|
| Coordinate-binding hypothesis untested / underspecified | R1, R4 | System D (already in v2) is now framed from the abstract onward as the test of my own first explanation. The Discussion lists R4's alternative (the model does not understand the coordinate frame or scale) and notes that System D removes coordinates entirely, so every explanation of that family predicted recovery, and none occurred. |
| Title over-generalizes | R4 | Title now reads "... Zero-Shot GPT-4o Grasp Prediction ...". Abstract sentence 1 names GPT-4o and "one frozen prompt". |
| 57.7% is post-hoc but still used in stats | R3 | Reproduced the pre-correction run per image (50/123, asserted against the afcd99a commit) and reran the object-clustered stats. All paired tests in the text now use 40.7%: B leads by 39.0 [25.2, 52.9], p < 0.0001; A leads one-call C by 28.3 [16.9, 40.0], p = 0.0001; A vs. best-of-five C is 5.7 [-6.1, 18.0], p = 0.45, which no longer separates. The 57.7% comparisons are kept in one sentence labeled post-hoc. Table 2 has a pre-correction row; Table 3 has a clean column beside the post-hoc one. |
| "Unified" means I/O + metric, not equal supervision or tuning | R1, R3 | Stated in the abstract and defined in the introduction's second paragraph; repeated in the System B section and in Limitations. |
| Motivation and explicit comparison to prior work | R2 | Intro paragraph 1 rewritten around the three cheap starting points a practitioner has and why published numbers are not comparable. Related Work now says, per cited method, what this paper does differently. |
| Too many variables; name one or two | R2 | Intro paragraph 3 names two focal factors: orientation (two angles vs. a continuous head) and the VLM output interface (coordinates vs. a menu). The conclusion answers both. |
| Practical application | R2 | New paragraph in the Discussion: order of operations for a practitioner (short-axis rule first, fine-tuned ResNet with a few hundred labels, no raw-coordinate VLM planner). |
| Fraction of test images within ±15° of 0/90 | R4 | Computed from labels: 103/123 (83.7%) within 15°, 118/123 (95.9%) within 30°, the metric's own tolerance. Only five test images are unreachable, so the constraint caps A near 96%, not near its score. Reported in the System A section and discussed under the orientation factor. |
| Why the 2 images were dropped | R1, R4 | Dataset section: two boundaries had no directional lean after full manual review, so one image on the smaller side of each was excluded rather than guessed; neither was an annotation error. |
| Number of uncertain boundary calls | R4 | Dataset section: 884 boundaries, 478 auto-same, 155 auto-different, 251 (28.4%) routed to manual review; 30 of those were blind-audited. The count of assistant calls labeled "uncertain" within the 251 lives in the review log, which is not in the repo; the 251 figure is reported instead. |
| 79.7% competitive with RGB-only literature | R4 | Results now place 79.7% and 84.0% between Lenz et al. (75.6%, object-wise) and Redmon and Angelova (84.9%), both with depth. I did not claim "competitive with RGB-only literature" because modern RGB-only dense detectors score above 95%. |
| Acknowledgment duplicated, badly typeset, vague on student vs. AI | R3, R4 | Rewritten as one paragraph: what I did, what each assistant did under my direction, and that GPT-4o is the evaluated model, not an assistant. |
| Modest contribution, narrow evaluation, small sample | R1, R3, R4 | Not contested. Limitations paragraph keeps every item and adds the wide-interval note. |

