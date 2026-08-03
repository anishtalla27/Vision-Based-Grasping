Next Gen Scholar Research Paper Competition Submission
Submission Deadline: August 7, 2026, at 11:59 PM EST

Submission Requirements
All papers must:

Be submitted as a PDF document.
Follow MLA formatting guidelines.
Be written in clear, professional English.
Use 12-point Times New Roman font.
Be double-spaced.
Include 1-inch margins.
Include page numbers.
Include proper MLA in-text citations.
Include a complete Works Cited page.
Be thoroughly proofread before submission.
Required Paper Structure
Each paper should include the following sections when applicable:

Abstract
Introduction
Methods / Discussion
Results
Conclusion
References / Works Cited

Publication Opportunity
One of the goals of NextGen Scholars is to make research publication more accessible to students.

Any submission that follows all formatting, citation, originality, and academic integrity requirements will be eligible for publication in the NextGen Scholars Research Journal and on the NextGen Scholars website. Publication is available to all qualifying authors who wish to have their work published.

Judging Criteria
Submissions will be reviewed by professors and other qualified professionals. Papers will be evaluated based on:

Research quality and depth
Originality and innovation
Analysis and critical thinking
Organization and clarity of writing
Proper MLA formatting and citations
Use of credible and reliable sources
Strength of conclusions and supporting evidence
Overall academic quality and professionalism
The highest-scoring submissions will receive special recognition, and the overall winner will be awarded a scholarship funded through sponsorships and donations supporting the competition.

Groups should only have one person submit!# Handoff — Vision Grasp Project: All Systems Sealed, Now Entering Paper-Writing Phase

Purpose: pick up exactly where this chat left off. Read this before doing anything else if resuming in a new session.

---

## Where things stand

All three technical systems are complete, sealed, and closed out. This chat's job shifted from experiment execution to preparing for a research paper submission (competition deadline **August 27, 2026, 11:59 PM EST**, NextGen Scholars National Research Paper Competition).

### The three sealed systems (spec Sections 5.1–5.4), all on the same 123-image test split

| System | Description | Test accuracy | Notes |
|---|---|---|---|
| A | Rule-based baseline: COCO detector + fixed category→grasp lookup | 57.7% (71/123), 95% Wilson [48.9, 66.1] | Frozen table, `system_a_lookup.py`, commit-verified freeze predates first eval |
| B | Custom CNN + fine-tuned ResNet18/34, trained on Cornell | ResNet18 **79.7%** (98/123) [71.7, 85.8] (val-selected); ResNet34 70.7%; custom CNN 23.6% | sin(2θ)/cos(2θ) orientation encoding, matches GG-CNN/GR-ConvNet convention |
| C | GPT-4o (via OpenRouter) zero-shot VLM, 5 repeats/image | 12.4% mean per-repeat (76/615), 95% Wilson [10.0, 15.2]; best-of-5 ceiling 35.0% | Frozen prompt, dominant failure = text-coordinate binding (reasoning often correct, emitted coordinates don't match it) |

**Statistical comparison (Section 6, sealed):**
- McNemar A vs B: p = 1.4e-4 (11 vs 38 discordant pairs)
- A vs C, B vs C: tested against each of C's 5 repeats separately; worst-of-5 p-values 5e-12 and 1.6e-20
- Strongest defensible ordering claim: **C's best-of-5 ceiling (35.0%, upper bound 43.7%) sits below A's single-call lower bound (48.9%)** — non-overlapping, doesn't rest on point estimates
- **Key finding (the spine of the paper's argument):** on images where every labelled grasp is diagonal, A drops 21.2 points, B *gains* 12.3 points, C moves only 2.0 points — three systems, three different directions, on one externally-sourced split
- Failure taxonomy inverts between A and B as predicted (A: mostly angle-only failures; B: mostly IoU-only/overlap failures); C's dominant failure mode is neither — 365/615 (59.4%) fail both criteria at once, consistent with the coordinate-binding explanation
- A weaker axis (grasps-per-image) was tested, found to contradict its own premise, and explicitly **not** used to argue anything — this restraint is itself a stated part of the methodology

All of this is verified via `verify_comparison.py` (27 checks), including re-scoring all three systems through one shared code path in a common 640×480 frame, exactly reproducing the sealed per-system counts.

### Artifacts, all tracked in git (same `.gitignore` negation pattern used for every system)

- `data/interim/system_a_results.md`, `system_a_predictions.csv`, `system_a_detections.csv`, 12 sheets
- `data/interim/system_b_results.md`, `system_b_predictions.csv`, `system_b_tuning.json`, `system_b_training.json`, 36 sheets (12 images × 3 models)
- `data/interim/system_c_results.md`, `system_c_predictions.csv`, `system_c_consistency.csv`, 12 sheets, `scripts/system_c_eval.py`
- `data/interim/comparison_results.md`, `comparison_per_image.csv`, `comparison_by_object.csv`, 12 comparison sheets (green GT, red A, blue B, orange C×5), `scripts/system_all_compare.py`, `verify_comparison.py`
- `vision_grasp_project_source_of_truth.md` — governing spec, now through addendum **Section 10.11** (Section 6 comparative analysis). Sections 10.6/10.7/10.9 cover Systems A/B/C individually.

### Amendments on record (dated, before/after states logged — do not treat as arbitrary edits)

- **System A Amendment 1:** unlisted-COCO-category handling, both result sets kept on record (40.7% and 57.7% commits)
- **System C Amendment 2** (`4b53132`, dated 2026-08-02): fixed a post-seal test-assertion bug in `verify_system_c.py` (the sentinel-existence check was permanently failing after the sealed run because it asserted the sentinel *didn't* exist, which was only true pre-run). Rewritten to assert what it actually meant (no sentinel manipulation occurred). **No prompt, parser, raw data, or reported number was touched** — logged and committed separately from the Section 6 bundle for auditability.

### Verification discipline — now an explicit named pattern in the project

Three separate bugs were caught and fixed *before* they corrupted a reported number, and this is written up in the docs as a real methodological finding, not just incidental competence:
1. Split-generation: an early pixel-diff heuristic was rejected after direct inspection showed same/different-object score distributions overlapped completely
2. System B: an early-stopping bug (no floor) let an untrained epoch-0 checkpoint become "best" by luck; fixed with `MIN_EPOCHS=40` + warmup-ineligible checkpoints, applied uniformly across all three architectures (not just the one that broke)
3. System C: a smart-quote encoding bug silently failed a contamination-probe negation check; caught, fixed, re-verified via re-parsing the frozen raw text (not a re-call)

---

## Next steps

### 1. Small open item — object labeling
8 object groups (26, 50, 56, 151, 183, 221, 230, 231) had disagreeing model-generated labels (split-review free text vs. VLM label). Both guesses are recorded but neither was adopted — all 8 show a neutral `object N (label uncertain)` placeholder in `comparison_by_object.csv`, `comparison_per_image.csv`, and `comparison_results.md`. **Review objects 26, 56, 230, and 231 directly** (in `comparison_sheets/` or source Cornell images) before deciding whether either guess is usable.

### 2. Research/proposal task — in progress, bounded scope
A prompt was just issued to Claude Code (Opus 4.8, high effort) to:
- Find and summarize 6–10 papers relevant to positioning this project (Cornell dataset paper, GG-CNN/GR-ConvNet, VLM zero-shot spatial grounding literature, any rule-based/trained/foundation-model comparison work)
- Assess where our results are genuinely novel vs. already well-covered — specifically whether the orientation-axis finding (A/B/C moving in three different directions) has precedent in the literature or is a new framing
- Propose 3–5 ranked, scoped improvements (analysis on existing data, sharper framing, specific citations, precise limitation statements) — explicitly **not** new experiments unless separately flagged and approved
- Deliver as `research_findings.md`, **not committed to git**, pending Anish's review

**When resuming:** check whether `research_findings.md` has been delivered. If yes, review it with Anish before anything from it gets tracked in git or acted on.

### 3. The actual paper
Target structure, per the competition's required sections (Abstract / Introduction / Methods-Discussion combined / Results / Conclusion / Works Cited), MLA format, 12pt Times New Roman, double-spaced, 1-inch margins, page numbers, PDF, submitted via the Google Form linked in the competition announcement.

Gap analysis (existing project material vs. what a real paper needs):
- **Methods, Results:** mostly ready — reuse from `system_a/b/c_results.md` and `comparison_results.md`, especially the System A methods paragraph (already assessed as near-publication-quality) and the Section 6 statistical framing
- **Introduction:** missing — needs an explicit stated research question (e.g., "how does zero-shot VLM grasp prediction compare to rule-based and learned approaches, and what does the pattern of failure reveal about the underlying problem?"), currently only implicit in spec sections
- **Related work / literature grounding:** the single biggest gap — this is what the Part 1 research task above is meant to fill
- **Discussion:** missing — needs to go beyond "what happened" (Results) to "what it means" (e.g., the coordinate-binding finding's implications for how VLMs might be integrated into robotics pipelines via structured output rather than free text)
- **Limitations section:** real material already exists but is scattered (contamination-risk caveat, the 552-rectangle format-check disclosure re: touching some test images, Jacquard unavailability, abstention-curve small-n caveat) — needs consolidating into one place
- **Abstract, Title:** write last, once the rest exists

**Time-boxed rough plan (as of Aug 2, deadline Aug 27):**
- This week: literature review / research_findings.md review
- Next 1–2 weeks: Anish writes the paper, section by section, in his own words
- Final week: MLA/formatting pass, proofread, submit

---

## Standing reminders for whoever continues this

- **Canary:** every Claude Code message starts with "Anish," including short/repetitive progress updates, no exceptions. If it drops under long mechanical loops, a direct nudge is enough — no need to wipe the session.
- **Model/effort convention:** Opus 4.8 + high for judgment-heavy design or research/proposal work; Sonnet 5 + medium/low for well-specified, mechanical execution. State plan mode on/off explicitly per prompt. (Plan mode doesn't strictly apply to research/proposal-only tasks — the deliverable there is the proposal itself, not code.)
- **No self-authored ground truth** for any primary metric — still the governing principle; nothing in the paper-writing phase should introduce a claim that isn't backed by the sealed, verified results.
- **Frozen-artifact discipline carries into the writing phase:** nothing in `source_of_truth.md`, any `results.md`, any CSV, sheet, or sealed-system script gets modified during the writing/research phase. Amendments, if any become necessary, follow the same dated, before/after, separately-committed pattern as Amendments 1 and 2.
- **Verify-before-trusting habit applies to the literature search too:** citations and claims about "does the literature already show this" should be spot-checked before use.
- **Writing style for the paper itself:** plain vocabulary, transition words, no em dashes, conversational but accurate tone.

---

## Reference files (in the project repo)

- `vision_grasp_project_source_of_truth.md` — governing spec, read this first in any new session, current through Section 10.11
- `data/interim/system_a_results.md`, `system_b_results.md`, `system_c_results.md` — per-system sealed results and methods prose
- `data/interim/comparison_results.md`, `comparison_per_image.csv`, `comparison_by_object.csv` — Section 6 cross-system analysis
- `scripts/system_all_compare.py`, `verify_comparison.py` — the comparison pipeline and its 27 verification checks
- `research_findings.md` — pending delivery from the literature/proposal task described above; not yet reviewed or committed

## Separately open, not part of this thread's immediate scope

- **SR project ideation** (five finalists vs. the wearable safety device direction) — unresolved since brainstorming, not blocking the grasping paper but not resolved either
- **Fall pillars** (multi-signal slip detection, real-time recovery) — need hardware (FSR/piezoelectric sensors), not started
# Paper Writing Framework — NextGen Scholars Research Paper Competition

**Purpose:** Anyone should be able to read this file and know exactly how to write the
competition submission, without needing prior context on the project. It covers what to
write, how long each part should be, what tables/figures go where, the tone to write in,
and how to strip out anything that reads as AI-generated before submitting.


**Submission format:** PDF **or** Word (.doc/.docx) — the competition-specific rules
allow PDF only; the general site submission rules allow either. Since this is going into
the competition specifically, **submit as PDF** to satisfy the stricter of the two rule
sets, but draft in a word processor that exports cleanly to both (Google Docs or Word),
so a .docx copy exists too in case it's ever needed.

MLA format, 12-point Times New Roman, double-spaced, 1-inch margins, page numbers.
Submitted via the competition's Google Form.

**Submission category:** this is an **Original Research** submission (per the site's four
accepted categories: Original Research, Literature Review, Opinion/Perspective, Science
Communication) — "new findings from your own experiments or studies." Every section of
this paper should read like original research, not a literature summary or a general-
audience explainer. The literature review work done for this project is grounding and
context for the original findings, not the paper's main content — don't let the related-
work material accidentally take over more than its share of the page count (see Section 5
for the word budget).

**Eligibility reminders that affect how this gets written, not just formatted:**
- Open to middle school and high school students. Write like a strong student paper, not
  like an attempt to sound like a professional academic beyond what's natural — see
  Section 2 on tone.
- **The work must be entirely your own and not previously published anywhere else.**
  This paper, and the underlying project, satisfies this — nothing here has been
  published elsewhere.
- **Write in clear, US English**, and check grammar and spelling specifically for US
  conventions (e.g. "color" not "colour," "-ize" not "-ise" endings) — this is stated as
  its own guideline, separate from general proofreading, so treat it as its own pass.
- **Plagiarism is a rejection condition, not just a deduction.** Every claim taken from a
  source needs an in-text citation (see Section 3.7a). Paraphrasing a source closely
  without citing it, or citing it but keeping the original wording too close, both count
  as plagiarism — when summarizing a paper's finding, restate it in your own words and
  still cite it.
- **Groups should only have one person submit** — not directly relevant here since this
  is a solo submission, but worth double-checking the submission form only lists Anish,
  not a team, if the form has a multi-name field.


---

## 1. Judging criteria (what actually earns points)

Per the competition rules, professors and qualified reviewers score submissions on:

1. Research quality and depth
2. Originality and innovation
3. Analysis and critical thinking
4. Organization and clarity of writing
5. Proper MLA formatting and citations
6. Use of credible and reliable sources
7. Strength of conclusions and supporting evidence
8. Overall academic quality and professionalism

**Where this project is already strong (don't over-invest further here):**
depth (3 sealed systems, statistically tested), strength of conclusions (Wilson CIs,
McNemar tests, non-overlapping confidence intervals).

**Where the real remaining points are:**
originality/innovation (needs the literature-grounded reframing — see Section 4, Sources
1, 3, 5 in the research findings), use of credible sources (currently the weakest area —
this is the literature review), and organization/clarity (currently scattered across
engineering docs, not yet shaped into a paper's argument).

---

## 2. Tone and voice

**Overall register:** plain, direct, technically precise, quietly confident. Not
inflated. This project's actual strength is that every claim is backed by something real
— write like someone who trusts their evidence and doesn't need to dress it up.

**Specific instructions:**
- Plain vocabulary. Use the simplest word that's still accurate. Say "shows" not
  "demonstrates," say "used" not "utilized," unless a term is a genuine technical term of
  art (e.g. "object-wise split," "Wilson confidence interval" — keep those, they're
  precise, not inflated).
- Use transition words naturally: however, furthermore, on the other hand, because, so.
  Don't force them into every paragraph.
- No em dashes anywhere in the paper. Use commas, periods, or parentheses instead.
- Conversational but accurate. It's fine to write "this result is surprising" or "we
  didn't expect this" — a real researcher has reactions to their own data. Don't fake
  detached neutrality for its own sake.
- First person is fine and expected in a student research paper: "I built three systems,"
  "I found," "my results show." Don't switch to a stiff passive voice to sound more
  formal — that's a step backward, not forward.
- State limitations plainly, not defensively. "System C performed worse than expected"
  is stronger writing than any hedge around it.
- Vary sentence length and structure. Don't let every paragraph fall into the same
  three-sentence rhythm.
- It is fine, and often better, to have an actual opinion about a result: "the from-CNN
  losing to a from-scratch CNN is the most surprising thing in this project" reads as
  a real person who understands their own work, not just a report generator.

**What NOT to sound like:** a press release, a corporate blog post, a Wikipedia article,
or a chatbot response. See Section 7 for the specific patterns to avoid — this section
covers what to write, Section 7 covers what to cut once it's written.

---

## 3. Full paper structure

The competition's required structure, stated in two places in their guidelines and
consistent both times, is six sections:

1. Abstract
2. Introduction
3. Methods / Discussion
4. **Results**
5. Conclusion
6. References / Works Cited

**Results is its own required section, separate from Methods/Discussion.** This is a
literal structural requirement, not just an organizational suggestion, so the paper needs
an actual section header that says "Results," containing the numbers, tables, and
statistical tests, distinct from the section that explains how the systems were built and
what the numbers mean. Methods and Discussion are combined into one section together
(unusual — most papers separate those two — but that's what this competition asks for),
while Results stands alone in between them structurally.

Practically, that means: **Methods/Discussion explains what was built, why it was built
that way, and what the results mean once they exist. Results is where the actual numbers,
tables, and statistical tests live**, reported with minimal interpretation. Some brief
framing sentences in Results are fine and normal ("Table 2 compares System B against a
comparable published architecture"), but the interpretive argument (why the gap is
explainable, what the coordinate-binding finding suggests, what the orientation-axis
result means) belongs in Methods/Discussion, not Results.

This is a different arrangement than the underlying project's own spec organizes things
(which folds numbers and interpretation together per system), so content needs to be
actively remapped into the competition's structure, not copy-pasted in project order.

Target total length: **4,500–6,000 words** of body text (roughly 10–13 double-spaced
pages before Works Cited, at 12pt Times New Roman). This is a reasonable length for a
strong student research paper — long enough to show real depth, short enough that a
reviewer reads the whole thing carefully rather than skimming. Extra weight goes to the
Introduction, System C, and Discussion, since those are where the paper's own thinking
lives and are the parts worth genuinely expanding rather than padding.

Write the sections in this order (not the order they appear in the final paper):
**Results (has the most existing source material, and is mostly assembling tables from
already-sealed data) → Methods → Discussion → Introduction → Limitations (folds into
Discussion or stands alone) → Abstract → Title, last.**

---

### 3.1 Title

**Length:** one line, 12–18 words.

Name the actual finding, not just the method. Avoid generic titles like "Adaptive
Robotic Grasping Through Vision-Informed Grip Decisions" on its own — that names the
project, not what was found. Consider naming the comparative structure or the
orientation/coordinate-binding finding directly.

Working options to choose from or riff on:
- "Three Ways to Fail at Grasping: A Controlled Comparison of Rule-Based, Learned, and
  Zero-Shot Vision-Language Approaches"
- "Where Grasp Prediction Breaks: An Orientation-Stratified Comparison of Three
  Grasping Techniques"
- "What a Zero-Shot Vision-Language Model's Coordinates Actually Miss: A Three-System
  Grasp Prediction Comparison"

Pick whichever best matches the paper's actual center of gravity once it's drafted —
don't lock the title until the Discussion is written.

---

### 3.2 Abstract

**Length:** 150–250 words. Write this last.

**Structure (roughly one to two sentences each):**
1. The problem / research question — why grasp prediction technique comparison matters
2. The approach — three systems (rule-based, trained CNN/ResNet, zero-shot VLM), same
   frozen Cornell Grasping Dataset test split, same evaluation metric
3. The headline result — the three accuracy numbers, framed with the strongest
   defensible statistical claim (non-overlapping confidence bounds), not just raw
   percentages
4. The most interesting finding — pick ONE: either the orientation-axis stratification
   (three systems moving three directions) or the coordinate-binding diagnosis for
   System C. Don't try to fit both in the abstract; pick whichever ends up being the
   paper's actual spine once Discussion is written.
5. One sentence on what it means / why it matters

**No citations in the abstract.** No hedging language ("this paper attempts to..."). State
findings directly.

---

### 3.3 Introduction

**Length:** 400–600 words.

**Structure:**
1. **Open with the real-world problem**, briefly: robotic grasping needs a way to decide
   where and how to grip an object, and there are fundamentally different approaches to
   doing this (hand-written rules, learned models, general-purpose AI). One paragraph.
2. **State the research question directly, once, in plain language.** Something like:
   "This project compares three fundamentally different approaches to predicting robotic
   grasp points, using the same dataset and the same scoring method, to answer a simple
   question: which approach works, and where does each one break down?"
3. **Briefly preview the three systems** (one sentence each: rule-based baseline using a
   pretrained object detector, a custom CNN and fine-tuned ResNet trained specifically for
   this task, and a zero-shot vision-language model with no grasp-specific training at
   all).
4. **Cite the field context here** — this is where citations 1 and 2 from the literature
   findings go (Jiang/Moseson/Saxena for the dataset and rectangle representation, Lenz/
   Lee/Saxena for the evaluation metric this project reuses). State plainly that this
   project uses the same dataset, representation, and scoring convention as the published
   literature, which is what makes the results comparable to prior work.
5. **Close with what the paper actually contributes** — not "we solve grasping" (it
   doesn't, and claiming that would be an unforced error the judging criteria would
   penalize) but something closer to: "This project does not aim to beat state-of-the-art
   accuracy. It aims to measure, under identical conditions, how three different
   technique families fail — and to show that the shape of failure, not just the accuracy
   number, is itself informative." This framing sets up both the System B reframe (P1) and
   the System C reframe (P2) without giving them away yet.

**Sources to cite here:** Jiang, Moseson, Saxena 2011; Lenz, Lee, Saxena 2015.

---

### 3.4 Methods / Discussion (combined, per the competition's required structure)

**Length:** 1,100–1,600 words. Numbers, tables, and statistical tests do NOT go here —
they go in the standalone Results section (3.5) that follows. This section covers what
was built, why, and what the numbers (once reported in Results) mean.

#### 3.4.1 Data and evaluation methods (~250–350 words)

Reuse System A's methods paragraph almost directly — it was already assessed as
near-publication-quality prose. Cover:
- Cornell Grasping Dataset, why it was chosen (Jacquard was ruled out — briefly explain
  why, one sentence, the EULA/signature blocker)
- The object-wise split methodology: why a naive pixel-diff heuristic failed, how the
  segmentation-based approach fixed it, the asymmetric confidence threshold reasoning
  (merge errors are harmless, split errors are dangerous), the two-layer human validation
  process with its 86.7%/40% confident/uncertain accuracy split
- Final split numbers: 234 objects, 883 images, 620/140/123 train/val/test (the actual
  Table 1 with these numbers belongs in Results, 3.5.1 — here, just describe how the
  split was built)
- **State the protocol limitation explicitly here, not left for a reviewer to catch:**
  published Cornell results typically use 5-fold cross-validation over all 885 images;
  this project used a single frozen object-wise split, opened once. This is a real
  protocol difference and should be named plainly.
- The evaluation metric: angle within 30°, IoU (Jaccard) > 25%, matched against any one
  of an image's multiple labeled grasps — and cite Lenz, Lee, and Saxena 2015 here
  directly, since that's the paper that established this exact convention.

#### 3.4.2 System A — rule-based baseline, method (~120–180 words)

- Method only: pretrained COCO detector, fixed category-to-grasp lookup table, frozen
  before any evaluation, commit-verified
- One sentence on why this design predicts a specific limitation: axis-aligned bounding
  boxes can only produce 0° or 90° orientations, which should fail on diagonal objects by
  construction — state this as a prediction here, then confirm it's what happened once
  Results (3.5.2) reports the actual number

#### 3.4.3 System B — trained CNN/ResNet, method and interpretation (~300–400 words)

- Method: custom CNN and fine-tuned ResNet18/34, sin(2θ)/cos(2θ) orientation encoding
- **Cite Redmon and Angelova 2015 here explicitly**, stating that this encoding and the
  overall architecture (global regression: backbone → pooled features → output heads)
  matches their "Direct Regression" approach specifically, not GG-CNN or GR-ConvNet (which
  are pixel-wise, a fundamentally different architecture family — this distinction matters
  and should be stated, not glossed over)
- Note briefly why three architectures were tested (ResNet18, ResNet34, a from-scratch
  CNN), and that ResNet34's extra capacity was expected to be hard to use well with only
  620 training images — state the expectation here, confirm the outcome in Results
- **This is where P1's interpretive reframe belongs — write the argument here, report the
  numbers in Results.** State plainly: every resource difference between this project and
  Redmon and Angelova 2015 (RGB-only vs. RGB-D, 620 real images vs. ~3,000 augmented
  examples per image) points the same direction and explains the accuracy gap without
  appealing to anything unmeasured. This is what turns the Results-section number into a
  "comparable in-family result under materially tighter constraints" story rather than a
  "far below state of the art" story. Don't cite GR-ConvNet's number here without this
  same context, or explain clearly why it's the wrong comparison to reach for.

**Figure recommendation:** 2–3 example sheets from `system_b_sheets/` showing predicted
vs. ground-truth rectangles — pick ones that show a correct case and a clean failure case
(prefer an angle-only miss, since that's the theoretically interesting failure mode).
Figures can live in either Methods/Discussion or Results, wherever the surrounding text
references them — keep the figure next to the paragraph that explains it.

#### 3.4.4 System C — zero-shot VLM, method and interpretation (~350–450 words)

- Method: GPT-4o accessed via API, 5 independent repeats per test image, frozen prompt,
  contact-point-to-rectangle conversion
- **This is where P2's reframe belongs — the paper's most important interpretive move.**
  State that the field of VLM-based grasping systems does not, as a rule, ask a VLM for
  raw coordinates: cite Jiao et al. 2025 (FreeGrasp — GPT-4o only selects which object,
  a separate module produces the actual grasp geometry), Kulshrestha et al. 2025
  (VLAD-Grasp — the VLM generates a goal image rather than numbers), and Yang et al. 2023
  (Set-of-Mark — the model refers to a labeled region instead of emitting coordinates).
  State the interpretive claim precisely: System C's headline number, reported in Results,
  is not evidence that VLMs are simply "bad at grasping" (an established, uninteresting
  fact by this point in the paper) — it is closer to a controlled measurement of what the
  field's near-universal design choice (avoid asking VLMs for raw coordinates) is actually
  worth, since none of the papers found actually benchmark that avoided path on a standard
  dataset under a standard metric.
- Explain the mechanism behind the failure taxonomy (numbers reported in Results, 3.5.4):
  the dominant compound-failure pattern is consistent with a specific mechanism, a
  text-coordinate binding problem, where the model's reasoning is often correct but the
  emitted numbers don't correspond to it.
- **Cite Wang et al. 2025 (COGNITION) here as independent cross-domain support** — this is
  the single strongest citation in the whole paper for this claim, since it documents the
  identical failure pattern (correct verbal reasoning, badly mismatched coordinates) in a
  completely different task domain (CAPTCHA solving) with a different model. Quote or
  closely paraphrase the specific example (target at a known location, model correctly
  described the path but clicked over 700 pixels off) — **verify this directly from
  COGNITION Sections A.3.2/A.3.3 before citing it, do not cite from a secondhand summary.**

**Figure recommendation:** 2–3 sheets from `comparison_sheets/` showing all three systems'
predictions overlaid on the same image (green GT, red A, blue B, orange C×5). Pick one
where C's coordinate-binding failure is visually obvious (the handoff notes pcd0285 as a
strong example).

#### 3.4.5 Cross-system interpretation and the orientation-axis finding (~300–400 words)

- Introduce why the orientation axis was tested: axis-aligned rectangles can't represent
  diagonal grasps (predicted for System A), sin/cos encoding is designed to handle
  rotation (predicted for System B), and System C has no comparable structural handling
  either way — state the hypothesis here, report the actual per-system movement in
  Results (3.5.5)
- **Present the orientation-axis finding as a methodological framing, not an empirical
  claim once the numbers are reported** (this distinction matters and was flagged directly
  in the literature review): stratifying results by ground-truth orientation as a
  diagnostic tool, using the direction each system moves on a shared, externally-sourced
  axis to localize where each technique family breaks, did not turn up precedent in the
  literature search conducted for this project. Frame it as a method other researchers
  could reuse, not as a discovered fact about grasping.
- **State the sample size limitation directly, not hidden in a separate limitations
  section:** n = 20 diagonal images. The individual per-system numbers are weak evidence
  on their own; what's robust is the direction each system class moves, not the exact
  magnitude.
- Note the corroborating detail: System C's flat response on the diagonal stratum (Results
  will report the exact figure) is consistent with, not just coincidentally alongside, the
  compound-failure taxonomy finding from 3.4.4 — two independent measurements pointing at
  the same underlying mechanism (System C has effectively no orientation signal) is
  stronger evidence than either alone, and this is worth saying explicitly.
- Note the grasps-per-image axis was also tested, found to contradict its own premise, and
  was explicitly not used to argue anything (the raw finding is reported in Results,
  3.5.5). This negative result is worth including briefly here as evidence the same
  standard of proof was applied even when it didn't produce a usable finding.

#### 3.4.6 Discussion (~300–450 words)

This is the "so what" section — go beyond what happened to what it means.

- **The mechanism-level argument (P4):** the coordinate-binding diagnosis makes a
  falsifiable prediction. If the failure is in binding language reasoning to emitted
  numbers, rather than in visual perception itself, then interventions that remove the
  need for numeric emission should help disproportionately, while interventions aimed only
  at improving perception should not. Cite Set-of-Mark (Yang et al. 2023 — replacing
  coordinate emission with mark selection improved zero-shot grounding substantially),
  VLAD-Grasp (Kulshrestha et al. 2025 — pictorial rather than numeric grasp encoding), and
  FreeGrasp (Jiao et al. 2025 — the VLM never emits geometry at all) as existing evidence
  consistent with this prediction, without claiming this project tested it directly.
- **Name explicitly what's novel and what isn't, plainly, without defensiveness.** State
  the sin/cos(2θ) encoding is standard practice since 2015 and is not being claimed as a
  contribution. State that "VLMs struggle with precise coordinates" is an established
  phenomenon, not a new discovery — what this project adds is a controlled measurement of
  that phenomenon under a standard benchmark and metric, alongside independent cross-domain
  corroboration (the COGNITION citation) of the specific mechanism. This kind of honest
  self-assessment is a real strength for a judged competition — a reviewer who catches
  overselling stops trusting the parts of the paper that are actually true.
- **The verification discipline as a methodological point (N5), briefly.** Worth one or
  two sentences near the end of the discussion: three separate implementation bugs (an
  early split-generation heuristic, a training early-stopping bug that would have reported
  an untrained model's score, a text-encoding bug in a contamination check) were each
  caught and fixed before they reached a reported number, and one disputed set of object
  labels was left explicitly unresolved rather than settled by picking the more plausible
  of two AI-generated guesses. This is worth stating plainly as part of how the results
  were produced, not as a boast — it's evidence for why the numbers in this paper can be
  trusted.
- **Close with a clearly scoped, honest note on future work**, not a vague "the future
  looks bright" ending (see Section 7, pattern 24 — avoid this explicitly). A strong,
  specific option: name Set-of-Mark prompting as the most directly testable next
  experiment the coordinate-binding diagnosis predicts should help, and state plainly that
  it was identified but not run, given the project's timeline — "identifying the
  intervention the diagnosis predicts should work, and scoping it as future work" is
  itself a legitimate and honest way to end a discussion section.

**Sources to cite in this subsection:** Yang et al. 2023 (Set-of-Mark), Kulshrestha et al.
2025 (VLAD-Grasp), Jiao et al. 2025 (FreeGrasp).

---

### 3.5 Results

**Length:** 500–700 words, plus tables. This is a required standalone section, not a
subsection of Methods/Discussion — give it its own top-level heading in the paper.
Report numbers plainly here; save the "why it matters" argument for the Methods/
Discussion section above, which the reader has already read by this point.

Keep the prose here short and let the tables carry the weight. A reasonable rhythm per
subsection: one sentence introducing the table or figure, the table or figure itself, one
or two sentences stating the headline number(s) precisely, and a single sentence pointing
back to where the interpretation lives ("see Discussion" is fine and normal in a
structure like this one).

#### 3.5.1 Data split (~50–80 words)

State the final split numbers plainly: 234 objects, 883 images, 620/140/123 train/val/
test.

**Table 1 goes here:** the split summary (objects/images per train/val/test).

#### 3.5.2 System A results (~80–120 words)

State the result: 57.7% (71/123), Wilson 95% confidence interval [48.9, 66.1]. Confirm
the predicted failure mode from Methods: report the count of angle-only failures, and
note this matches the axis-aligned-representation prediction.

#### 3.5.3 System B results (~120–170 words)

State results for all three architectures: ResNet18 79.7% (98/123) [71.7, 85.8], best of
the three; ResNet34 70.7%; the from-scratch CNN 23.6%. Confirm this matches the Methods
section's expectation that limited training data can't make good use of ResNet34's extra
capacity.

**Table 2 goes here:** System B vs. Redmon & Angelova 2015 (architecture, angle encoding,
input type, training data size, object-wise accuracy, side by side — the comparison
table already drafted in the research findings).

#### 3.5.4 System C results (~150–200 words)

State the headline number plainly, without softening: 12.4% mean per-repeat accuracy
(76/615), Wilson 95% confidence interval [10.0, 15.2]. Report best-of-5 (35.0%) and
majority-consensus (12.2%) as explicitly secondary, clearly labeled as not the headline.
Report the failure taxonomy: 76 correct, 85 angle-only fail, 88 IoU-only fail, 365
both-fail (59.4%).

**Table 3 goes here:** the three-way failure taxonomy (angle-only / IoU-only / both),
computed identically for A, B, and C — this table is one of the paper's strongest single
visual arguments, since it shows the failure mode inverting between A and B and taking a
third, different shape for C.

#### 3.5.5 Cross-system comparison and orientation-axis results (~150–200 words)

Report the statistical tests plainly: McNemar A vs. B (p = 1.4e-4); A vs. C and B vs. C
tested against each of C's 5 repeats separately (worst-of-5 p-values 5e-12 and 1.6e-20).
State the ordering result precisely: C's best-of-5 ceiling (35.0%, upper bound 43.7%)
sits below A's single-call lower bound (48.9%), a non-overlapping comparison.

Report the orientation-axis numbers: on the diagonal-grasp stratum (n=20), System A drops
21.2 points, System B gains 12.3 points, System C moves 2.0 points. Report the
grasps-per-image finding plainly as a negative result: all three systems performed worse,
not better, on images with more labeled grasps, despite more chances to match; this axis
was not used to argue anything further.

**Table 4 (optional, if space allows):** the orientation-stratified accuracy table (A/B/C
× diagonal/non-diagonal).

---

### 3.6 Limitations

Can be its own short subsection at the end of Discussion, or folded in as a paragraph — a
standalone subsection is probably cleaner given how much real material there is. If kept
separate, place it at the end of the Methods/Discussion section (3.4.6), before Results —
limitations are methodological context, not a result, so they read more naturally before
the numbers than after.

**Length:** 200–350 words.

Consolidate everything already scattered across the results docs into one place, each
stated in one or two plain sentences, no more:
- Single frozen object-wise split (not 5-fold cross-validation, unlike most published
  Cornell results) — already stated in Methods, can be referenced briefly here rather than
  repeated in full
- Jacquard Dataset was unavailable (EULA required institutional signature not obtainable
  over the summer) — the project used Cornell only
- The 552-rectangle format-verification sample, done early in the split process, likely
  touched a small number of test-split images — disclosed plainly, and no constant or
  frozen table derives from that sample
- Contamination risk for System C: GPT-4o may have seen Cornell or Cornell-derived
  content during training. **Cite that this is a general, known problem with evaluating
  frontier models on public benchmarks, not a quirk unique to this project, if a suitable
  citation was found** — otherwise state it as a known limitation without an unverified
  citation. State the contamination probe result (0/10) as a mild indicator, not a
  clearance, and note that contamination could only have inflated System C's number, which
  it still trailed badly with even if fully clean.
- The orientation-axis stratum is small (n=20 diagonal images) — already flagged in that
  subsection, can be referenced rather than repeated
- System C used one model (GPT-4o) and one frozen prompt — the coordinate-binding finding
  is about this specific prompting approach (free-text coordinate emission), not a general
  claim about all VLMs or all possible prompting strategies
- RGB-only input throughout (no depth channel), unlike some published approaches that use
  RGB-D

---

### 3.7 Conclusion

**Length:** 150–250 words.

Do not simply restate the abstract. A conclusion should feel like it's zooming back out
after all the detail in Methods/Discussion.

**Structure:**
1. One sentence restating the research question
2. One or two sentences on the headline comparative finding, stated with appropriate
   confidence (reference the non-overlapping CI framing again briefly)
3. One or two sentences on what the paper's actual contribution is, precisely: not "we
   built a better grasping system" but something like "under identical conditions and a
   shared evaluation standard, this project shows that three technique families fail in
   three distinguishable, mechanistically different ways — and that failure mode, not
   just accuracy, is informative about where each approach belongs"
4. Close on the specific, scoped future-work note (Set-of-Mark), not a vague closer

---

### 3.8 References / Works Cited

MLA 9 format, alphabetized by author last name. **Every citation in this file needs to be
independently verified before submission** — several are marked `[SEARCH-ONLY]` in the
literature research and must not be used until confirmed against the actual source. See
the verification checklist in Section 6.

Minimum citation count for a paper this technical: aim for the full set already found (10
papers), though not all 10 need to make it into the final paper if some don't earn their
place in the argument. Do not pad with citations that aren't actually load-bearing for a
claim being made.

#### 3.8a In-text citation mechanics (needed throughout the paper, not just here)

The competition explicitly requires "proper MLA in-text citations" as its own separate
line item, distinct from the Works Cited page — every claim pulled from a source needs
both an in-text citation where the claim appears AND a matching entry in Works Cited.
Missing either one is incomplete, and missing both is treated as plagiarism per the
site's stated policy.

**Standard format:** parenthetical, author's last name and page number, no comma between
them: (Jiang 3306). If the author's name is already stated in the sentence, drop it from
the parenthetical and give just the page: Jiang, Moseson, and Saxena introduced the
five-parameter grasping rectangle (3306).

**Two or three authors:** name all of them, last name only, joined with "and": (Lenz, Lee,
and Saxena 712).

**Four or more authors:** first author's last name plus "et al.": (Wang et al. 14).

**Sources with no page numbers (most of the literature found for this project — arXiv
preprints don't have fixed page numbers the way journal articles do):** use a paragraph
or section number if the source has one, or just the author name with no number at all if
neither exists. For example, citing COGNITION's appendix section directly: (Wang et al.,
sec. A.3.2). For a source with no internal numbering at all, author name alone is
acceptable: (Jiao et al.).

**Multiple sources for one claim:** separate with a semicolon inside one parenthetical:
(Morrison et al.; Kumra et al.).

**Direct quotes over four lines** need to be set off as a block quote (indented, no
quotation marks, citation after the final period) rather than run into the paragraph —
this is unlikely to come up much in this paper since most citations here are
paraphrased findings, not long quotes, but the COGNITION example quote in 3.4.4 is short
enough to run inline with quotation marks.

#### 3.8b Works Cited page formatting

- Starts on its own new page, titled "Works Cited" (not "References," not "Bibliography"
  — MLA specifically uses "Works Cited"), centered, no bold or underline
- Alphabetized by first author's last name
- **Hanging indent**: the first line of each entry starts at the left margin, every
  subsequent line of that entry is indented half an inch. (Most word processors have a
  "hanging indent" paragraph setting — don't do this by hand with spaces or tabs, it
  breaks when the PDF is generated.)
- Double-spaced, same as the rest of the paper, no extra blank line between entries
- Titles of full works (books, journals, conference proceedings) are italicized. Titles
  of articles or papers within a larger work are in quotation marks, not italicized
- For conference papers (most of the sources found for this project): Author(s). "Paper
  Title." *Conference/Proceedings Name*, Publisher, Year, page range.
- For arXiv preprints (several of the sources found for this project, since they haven't
  been published in a formal venue): Author(s). "Paper Title." *arXiv*, day month year of
  posting, arxiv.org/abs/XXXXX.XXXXX. Include the specific date if known, not just the
  year, since arXiv preprints can be revised.
- Every source cited anywhere in-text must have a matching Works Cited entry, and every
  Works Cited entry must be cited somewhere in-text. No orphaned citations either
  direction — this is worth a manual cross-check pass right before submission (see
  Section 8).

---

## 4. Full list of tables and figures

| # | Type | Content | Section | Source data |
|---|---|---|---|---|
| 1 | Table | Object-wise split summary (train/val/test, objects, images) | Results 3.5.1 | `final_split.csv` |
| 2 | Table | System B vs. Redmon & Angelova 2015 (architecture, encoding, input, training size, accuracy) | Results 3.5.3 | `system_b_results.md` + literature |
| 3 | Table | Three-way failure taxonomy (angle-only / IoU-only / both), A vs. B vs. C | Results 3.5.4 | `comparison_results.md` |
| 4 | Table (optional) | Orientation-stratified accuracy, A/B/C × diagonal/non-diagonal | Results 3.5.5 | `comparison_by_object.csv` or equivalent |
| 5 | Figure | 2–3 System B sheets (correct case + angle-only failure case) | Methods 3.4.3 (referenced), placed near Results 3.5.3 | `system_b_sheets/` |
| 6 | Figure | 2–3 comparison sheets, all three systems overlaid, one showing C's coordinate-binding failure clearly | Methods 3.4.4 (referenced), placed near Results 3.5.4 | `comparison_sheets/` (pcd0285 flagged as a strong example) |

**Note on figure placement:** figures are visual evidence, so they can sit in the
Results section next to the numbers they illustrate, even though the sentence explaining
*why* they matter is back in Methods/Discussion. That's normal in papers with this kind
of split structure — the reader has already read the explanation by the time they reach
the picture.

**Formatting note:** MLA does not use "Figure 1 / Table 1" numbering the same way
scientific papers do by default — check current MLA guidance on labeling visuals (typically
labeled as "Fig. 1" with a caption below, tables labeled "Table 1" with a caption above)
and apply consistently. Every table and figure needs a caption and an in-text reference
("see Table 2") — don't just drop a table in with no surrounding sentence pointing to it.

**Total visual count:** aim for 3–4 tables and 2–4 figures. Don't include all 6+
possibilities above if it starts crowding a ~7–9 page paper — Table 3 (failure taxonomy)
and Table 2 (System B reframe) are the two highest-value items; treat the rest as
optional depending on space.

---

## 5. Section-by-section length summary

| Section | Word count target |
|---|---|
| Title | 12–18 words |
| Abstract | 200–300 |
| Introduction | 650–950 |
| **Methods / Discussion (combined section)** | **2,500–3,200** |
| — Data & evaluation methods | 300–450 |
| — System A method | 150–220 |
| — System B method + interpretation | 400–550 |
| — System C method + interpretation | 500–650 |
| — Cross-system interpretation + orientation framing | 350–450 |
| — Discussion | 450–600 |
| — Limitations (if kept inside this section) | 250–350 |
| **Results (standalone section)** | **900–1,250** |
| — Data split numbers | 80–120 |
| — System A results | 150–220 |
| — System B results | 200–280 |
| — System C results | 250–330 |
| — Cross-system + orientation numbers | 250–320 |
| Conclusion | 250–380 |
| **Total body text** | **~4,500–6,000 words** |
| Works Cited | not counted toward body length |

(Subsection targets within Methods/Discussion and within Results each sum to slightly
more than their parent section's range — that's expected; some tightening happens
naturally in the edit pass. If Limitations is kept as its own top-level section rather
than folded into Methods/Discussion, subtract its word count from the Methods/Discussion
range above.)

---

## 6. Verification checklist — do this before any of these sources go in the paper

From the literature research, confirm each of these directly against the source, not
from a search summary, before citing:

- [ ] Read COGNITION Sections A.3.2 and A.3.3 directly. A search-engine summary blended
      this quote with content from other papers in one pass; it was only caught by
      fetching the full text.
- [ ] Confirm ViewSpatial-Bench's actual results table (the 34.98% GPT-4o / 26.33% chance
      figures) — these were reported by search results and not confirmed from the paper's
      abstract directly.
- [ ] Confirm whether GraspMAS, ThinkGrasp, SegGrasp, and Lan-grasp actually follow the
      same "VLM avoids raw coordinates" pattern claimed for them — this was verified
      directly only for FreeGrasp, VLAD-Grasp, and Set-of-Mark. If unconfirmed, either
      drop these four from that sentence or verify them individually first.
- [ ] Confirm VLAD-Grasp's stated motivation — the method itself is verified, but not
      whether the authors actually justify it by citing VLM numeric-output weakness.
- [ ] Verify page number ranges for all 10 citations — author, title, venue, and year
      were verified with high confidence; page ranges were reported inconsistently across
      search results and need a direct check.

Also, separately, before the paper is finalized:

- [ ] Look at object groups 26, 56, 230, and 231 directly (in `comparison_sheets/` or the
      source Cornell images) — these have disputed labels from two different
      AI-generated guesses, and neither should be adopted without Anish confirming it
      visually. If a name is needed in the paper for readability, use only what's
      directly confirmed, or the neutral group ID.

---

## 7. Humanizer pass — remove AI-writing patterns before submission

Run every section through this checklist. This is a
**writing edit pass**,  this step is about catching leftover patterns that
happen to overlap with common AI tells

### How to use this section

1. Read the draft section carefully.
2. Check it against the patterns below.
4. Do a final self-check pass: read the section out loud. If a sentence sounds like
   something a chatbot would say, or like a press release, or like every paragraph has the
   exact same shape, revise it.

### Content patterns to avoid

**1. Inflated significance language.** Don't write that something "stands as a testament
to," "marks a pivotal moment in," "underscores the significance of," or "reflects a
broader trend." If a result matters, say specifically why, don't gesture at vague
importance.
*Bad:* "This finding represents a significant contribution to the evolving landscape of
robotic grasping research."
*Better:* "This finding shows that a system's failure mode changes depending on how you
condition the test set — something the existing Cornell literature doesn't report."

**2. Notability-stacking.** Don't list credentials or coverage as a substitute for
substance ("this method has been cited by leading researchers"). Cite the actual claim,
not the fact that someone said something.

**3. Superficial "-ing" phrases tacked onto sentences for fake depth.** Watch for
"highlighting," "underscoring," "reflecting," "showcasing," "emphasizing," "ensuring,"
"contributing to" used as sentence-tail flourishes rather than doing real work.
*Bad:* "System B outperformed System A, highlighting the value of learned representations."
*Better:* "System B outperformed System A by 22 points, consistent with prior Cornell
results showing learned models beat rule-based baselines."

**4. Promotional language.** Avoid "vibrant," "rich," "groundbreaking," "cutting-edge,"
"robust" (unless used precisely, e.g. "statistically robust"), "showcases," "boasts a."
This is a research paper, not marketing copy — describe results plainly.

**5. Vague attributions.** Never write "researchers have shown" or "studies suggest"
without naming who and citing the paper. Every claim needs a specific source or it needs
to be dropped.

**6. Formulaic "Challenges and Future Directions" sections.** Don't write a generic
paragraph listing challenges with no specifics. The Limitations section (3.5) already
covers this properly with specific, concrete items — don't also add a vague "despite these
challenges" paragraph elsewhere.

**7. Overused AI-vocabulary words.** Watch specifically for: additionally, align with,
crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight (as a verb),
interplay, intricate/intricacies, key (as a filler adjective), landscape (abstract, e.g.
"the research landscape"), pivotal, showcase, tapestry, testament, underscore (as a
verb), valuable, vibrant. These words aren't banned outright but each instance should be
checked — usually a plainer word works better.

**8. Copula avoidance.** Don't write "the model serves as a baseline" when "the model is a
baseline" says the same thing more plainly. Watch for "serves as," "stands as," "functions
as," "represents a," "boasts," "features," "offers" used where "is" or "has" would work.

**9. Negative parallelism ("It's not just X, it's Y").** Cut this construction wherever
it shows up. State the point once, directly.

**10. Rule-of-three overuse.** Don't force findings into groups of exactly three just to
sound comprehensive ("this shows depth, rigor, and innovation"). If there are two real
points, make two. If there are five, make five.

**11. Elegant variation / synonym cycling.** Don't call the same thing by five different
names across a paragraph to avoid repetition (e.g. "the model... the system... the
architecture... the approach..." all referring to one thing). Repeating the same term is
clearer and more precise in technical writing — plain repetition of "System B" is better
than synonym-hopping.

**12. False ranges.** Avoid "from X to Y" constructions where X and Y aren't actually
points on a real scale (e.g. "from rule-based systems to the frontiers of AI reasoning").

**13. Em dash overuse.** No em dashes anywhere. Already a standing preference — enforce it
strictly in the paper. Use commas or separate sentences instead.

**14. Boldface and inline-header bullet overuse.** In prose sections, don't bold random
phrases for emphasis, and don't write list items as "**Speed:** description..." Convert
to plain sentences. (Tables are fine and expected — this is about prose paragraphs
specifically.)

**15. Title case in headings.** Use sentence case for headings ("Cross-system
comparison"), not "Cross-System Comparison."

**16. Emojis.** None, anywhere, in an academic paper.

**17. Curly quotation marks.** Use straight quotes throughout for consistency (word
processors often auto-convert — check the final PDF).

**18. Chatbot correspondence artifacts.** Obviously shouldn't appear in a paper draft, but
double check no stray "I hope this helps" or "let me know if you'd like me to expand"
survived a copy-paste from any AI tool interaction.

**19. Sycophantic tone.** Not really a risk in a research paper written in first person,
but watch for over-hedged, overly agreeable phrasing that doesn't sound like a person
stating their own findings confidently.

**20. Filler phrases.** Replace "in order to" with "to," "due to the fact that" with
"because," "at this point in time" with "now," "it is important to note that X" with
just "X."

**21. Excessive hedging.** "It could potentially possibly be argued that..." → say the
thing directly, or state the specific degree of uncertainty precisely (e.g. "n=20, so this
is suggestive rather than conclusive" is good hedging — it's specific and earns its
place; "might possibly perhaps" is not).

**22. Generic positive conclusions.** No "the future looks bright," "exciting
possibilities lie ahead," "this represents an important step forward" as a closing line.
End on the specific future-work note (Set-of-Mark prompting) instead.

**23. Hyphenation over-consistency.** AI text hyphenates compound modifiers with
mechanical consistency ("real-time," "data-driven," "well-known") every single time.
Human writing is more inconsistent about this. Don't worry about fixing this
aggressively — it's a minor tell — but if a paragraph reads like every possible compound
got hyphenated, loosen a few.

### Final self-audit, per section

After drafting and revising a section, ask directly: **"What makes this sound
AI-generated?"** List anything you notice (uniform sentence rhythm, no real opinions
expressed, every paragraph the same length, overly clean transitions). Then revise once
more specifically to fix those things. This two-pass habit catches what a single edit pass
misses.

### What good, human academic writing sounds like (for calibration)

Real research papers, including strong ones written by actual professors, have:
- Sentences of noticeably different lengths right next to each other
- Occasional first-person reactions to their own findings ("this result surprised us,"
  "we did not expect...")
- Specific numbers instead of vague qualifiers wherever possible
- Genuine hedges that are precise about what's uncertain and why, not generic
  disclaimers
- A conclusion that adds a new thought, not just a summary of what was already said

This project already has an unusual amount of real material to work with: honest
limitations, a self-caught research error (the search-summary blending in the COGNITION
citation), a negative result reported and explicitly not oversold (the grasps-per-image
axis), and a genuine, specific reaction to an unexpected finding (the from-scratch CNN
beating a frontier VLM). Lean into these — they're what makes writing sound human, because
they're the parts that actually are.

---

## 8. Final proofread and submission checklist

The competition lists "be thoroughly proofread before submission" as its own explicit
requirement, separate from formatting and citation correctness. Treat this as its own
final pass, done after every other section in this file, not folded into the writing or
humanizer passes.

### Formatting, line by line against the stated rules

- [ ] PDF file format (competition-specific rule is stricter than the general site rule
      which also allows .doc/.docx — submit PDF)
- [ ] 12-point Times New Roman throughout, including headings and Works Cited
- [ ] Double-spaced throughout, including Works Cited (no extra blank lines between
      Works Cited entries — double-spacing alone provides the separation)
- [ ] 1-inch margins on all four sides
- [ ] Page numbers present (MLA convention: upper right corner, with last name before the
      number, e.g. "Talla 4")
- [ ] MLA heading present on page 1 (name, instructor/mentor if applicable, course/
      competition name, date — top left corner, not centered)
- [ ] Title centered, plain text, no bold/italic/underline, no larger font size
- [ ] Every table has a caption and is referenced by name in the surrounding prose
- [ ] Every figure has a caption and is referenced by name in the surrounding prose
- [ ] No curly quotation marks anywhere (check the final exported PDF specifically —
      word processors often auto-convert straight quotes to curly ones on export even if
      they looked correct while editing)
- [ ] No em dashes anywhere in the final PDF

### Citation cross-check

- [ ] Every source cited in-text has a matching Works Cited entry
- [ ] Every Works Cited entry is cited at least once in-text (no orphaned sources)
- [ ] Every `[SEARCH-ONLY]`-flagged claim from the literature research (Section 6's
      checklist) has been independently verified before being cited, or has been dropped
      from the paper if it couldn't be confirmed
- [ ] Works Cited is alphabetized correctly by first author's last name
- [ ] Works Cited uses hanging indent, not manual spacing or tabs
- [ ] No claim in the paper is taken from a source without a citation attached at the
      point the claim is made (not just somewhere in the same paragraph)

### Content and integrity

- [ ] Object labels for groups 26, 56, 230, and 231 (if used anywhere in the paper) were
      confirmed by Anish looking at the actual images, not adopted from either
      AI-generated guess unconfirmed
- [ ] Spelling and grammar checked specifically for US English conventions
- [ ] The paper has not been published or submitted anywhere else previously
- [ ] Read the full paper aloud once, start to finish, as the very last step before
      exporting to PDF — this catches both grammar issues and any remaining sentences
      that sound off in a way silent reading misses

### Word count and structure sanity check

- [ ] All six required sections present with clear headers: Abstract, Introduction,
      Methods/Discussion, Results, Conclusion, Works Cited
- [ ] Results contains numbers and tables, not interpretation — spot-check that no
      paragraph in Results has drifted into arguing a point rather than reporting one
- [ ] Total body length falls roughly within 4,500–6,000 words (Section 5) — significantly
      under or over that range is worth a second look, not necessarily a problem, but
      worth knowing why
- [ ] Final exported PDF opens correctly and all pages are present, before submitting
      through the Google Form

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

**Still to do before submission:** confirm object groups 26, 56, 230, 231 visually if you name any object; US-English spelling pass; MLA formatting in a word processor; read aloud once.

**Word count:** 5,875 words of body text, inside the 4,500-6,000 target. Four of the five top-level sections are in band; Methods and discussion runs 39 words over its 3,200 cap, about 1.2%. I stopped trimming there rather than cut material the reviewer panel flagged as load-bearing. Placeholders, tables, and this note excluded.

---

# Three Ways to Miss a Grasp: A Controlled Comparison of Rule-Based, Learned, and Zero-Shot Vision-Language Prediction

> **[MLA-FORMAT]** Before export: MLA header block at top left of page 1 (name, mentor, competition, date), title centered in plain 12pt Times New Roman with no bold or italic, page numbers upper right as "Talla N", double spacing throughout including Works Cited, 1-inch margins, hanging indents on Works Cited entries. Delete this note and all scaffolding above it.

## Abstract

A robot cannot pick anything up until something decides where on the object to place the fingers and at what angle. That decision can come from a hand-written rule, from a model trained to predict grasps from images, or from a general-purpose vision-language model never trained on grasping at all. I built one system of each kind and scored all three against the same external answer key, the Cornell Grasping Dataset's hand-labeled grasp rectangles, on one held-out split of 123 images covering 35 objects that appear nowhere in training. The rule-based system reached 57.7%, the fine-tuned ResNet18 reached 79.7%, and zero-shot GPT-4o reached 12.4% averaged over five runs per image. The first gap is significant under McNemar's exact test, and the vision-language model trails so far that even its best-of-five ceiling of 35.0% sits below the rule-based system's lower 95% confidence bound of 48.9%. The ranking is not the interesting part. Splitting the test set by whether an image's labeled grasps run diagonally shows three systems moving three different ways: the rule-based system loses 21.2 points, the learned model gains 12.3, and the vision-language model barely moves. Its failures explain why it does not respond to that axis. Its written explanation frequently named the correct part of the object while the coordinates in the same reply landed nowhere near it, and on 53.4% of calls the predicted center fell outside the region holding every labeled grasp, roughly eight times either other system's rate. A published system using the same model class, zero-shot, on this same dataset does far better while never asking for a coordinate, though under a looser success test than mine. Together these point at free-text coordinate emission, rather than visual recognition, as the binding constraint when a general-purpose model is asked to predict grasps.

## Introduction

Before a gripper closes on anything, something has to choose a contact point, an approach angle, and how wide to open the fingers. Every piece of motion that follows depends on that choice being roughly right. A robot arm can be mechanically excellent and still fail constantly if the thing telling it where to grip is wrong, which makes grasp prediction one of the places where a small accuracy difference turns into a large behavioral difference. It is also a problem that has to be solved from thin information. In most real settings a robot gets a camera image and little else: no model of the object, no label saying what it is, no annotation marking the handle.

There are three broadly different ways to make that decision, and they are not variations on a single method. A programmer can write the rule directly, saying that mugs get grasped by the handle and bottles around the neck. A model can be trained on thousands of hand-labeled examples until it learns to map pixels to grasp rectangles. Or a general-purpose vision-language model, trained on web text and images and never shown a grasping dataset, can simply be asked in plain language where to grip. Each is a bet about where the useful intelligence in a robot's perception stack should live: in a person's explicit rules, in weights fitted to task-specific data, or in a large model's general knowledge of the world.

That third option is new enough that the field has not settled how to use it. Foundation models arrived in robotics quickly, and the literature is still working out which parts of a manipulation pipeline they should own. The question matters practically, because the three approaches demand very different resources. A lookup table needs only hand-specified rules. A learned predictor needs a task-specific annotated dataset and the compute to train on it. Prompting a hosted vision-language model needs an API key and almost no setup, which is exactly why it is tempting, and exactly why it deserves to be measured rather than assumed.

Comparisons across those three families are rarer than you might expect. Most published grasp-detection work benchmarks within a family, comparing one trained architecture against another on the same dataset. That produces useful leaderboards but does not tell you what you gain or give up by changing approach entirely. Rule-based baselines, when they appear, are often described rather than scored. Vision-language models usually appear embedded inside a larger system, where their individual contribution cannot be isolated. I wanted a comparison where all three sat on the same test images, produced the same kind of output, and were scored by the same code.

This project is that comparison, and the question is plain: which approach actually works, and where does each one break down? I care about the second half at least as much as the first. An accuracy number tells you a system is wrong. The shape of its errors tells you why, and that is the part that transfers to whatever somebody builds next.

The measuring apparatus is borrowed rather than invented, which matters more than it might seem. A grasp here is a rectangle with a center point, an orientation, and a width matched to how far the gripper opens, the representation Jiang, Moseson, and Saxena introduced with the Cornell Grasping Dataset (3304). Each image carries several labeled grasps rather than one, since most objects can be picked up in more than one valid way, and a prediction counts as correct if it matches any of them. The matching rule is that the predicted angle falls within 30 degrees of a labeled grasp and the intersection over union between the two rectangles exceeds 25%, the convention established by Lenz, Lee, and Saxena (712). I chose an external answer key deliberately. An earlier design would have had me write the ground truth myself and then grade my own rule-based system against it, which is close to circular. The dataset's existing annotations remove that problem and make my numbers comparable to published ones.

The three systems are as follows. System A is the rule-based baseline: a COCO-pretrained detector identifies the object, and a small fixed table maps the detected category to a grasp region. In practice the detector recognizes fewer than half the images, since Cornell photographs many objects COCO has no category for, so a geometric fallback that segments the object against the photography platform covers the rest. System B is the learned predictor, a small convolutional network built from scratch alongside fine-tuned ResNet18 and ResNet34 models, trained on the Cornell training split. System C is GPT-4o, prompted directly with the raw image and given no task-specific training whatsoever.

I want to be clear about what this paper is not. It does not beat state-of-the-art grasp detection and does not try to. Published pixel-wise systems reach accuracies I am not competing with, and pretending otherwise would be an easy way to lose a reader early. What this paper does is measure, under identical conditions, how three families of technique fail, and argue that the shape of each failure carries information the accuracy number does not. That argument turns out to matter most for the system that scored worst, which is not where I expected to end up.

## Methods and discussion

### Dataset and evaluation

Every system was evaluated on the Cornell Grasping Dataset, roughly a thousand photographs of household objects with hand-labeled grasp rectangles. I looked into Jacquard as a second source, since training on one dataset and testing on another is the cleanest generalization check available, but its full distribution requires a signed institutional agreement I could not obtain over the summer.

Cornell ships no object identity metadata, and that became the hardest methodological problem in the project. The split I needed was object-wise, meaning no physical object may appear in both training and test. An image-wise split lets a model memorize one stapler from six angles and then rewards it for recognizing that same stapler at test time, inflating every number afterward without anyone noticing. With no object labels to group by, identity had to be reconstructed from the image sequence.

My first attempt compared consecutive frames by raw pixel difference. It failed because the dataset deliberately rotates each object between shots, so same-object and different-object scores overlapped almost completely and no threshold separated them. The approach that worked segmented each frame using the geometry of the photography platform, since the object appears as a gap in an otherwise uniform surface, then compared those regions with descriptors that ignore rotation, color histogram and pixel area.

Acceptance thresholds were set asymmetrically, because the two mistakes are not equally costly. Merging two different objects into one group is nearly harmless, since the merged group still lands entirely on one side of the split. Splitting one real object into two is dangerous, because the halves can land on opposite sides and every accuracy number quietly inflates. So the automatic "different object" threshold went below the lowest score seen for any confirmed same-object pair, while the "same object" threshold stayed loose.

The ambiguous band was reviewed in two layers. An AI assistant made a first pass over each boundary in it, logging a confidence level per decision. I then classified a 30-boundary stratified sample myself, blind to its calls and oversampled toward the ones it had marked uncertain. We agreed on 86.7% of its confident calls and 40.0% of its uncertain ones. That gap set the review policy, since it showed the stated confidence carried real information. I personally decided every uncertain call, every confident "different" call, and every call whose stated basis matched an error the sample had exposed. Confident "same" calls not caught by those rules were accepted unreviewed, since an error in that direction is harmless by construction.

The result is 234 objects across 883 images, split 620 for training, 140 for validation, and 123 for test. One protocol difference needs stating: most published Cornell results use five-fold cross-validation over all 885 images, while I used a single frozen split opened once. Those are not the same experiment even under the same metric.

### System A, rule-based baseline

System A detects an object with a COCO-pretrained detector, looks the category up in a fixed table, and converts the result into a rectangle centered on the object with an orientation drawn from the box. The table was committed before any evaluation code existed, so no entry could be tuned toward a score. That was enforced structurally, not by good intentions.

One thing needs stating up front rather than in Results, because it changes how the headline should be read. COCO's 80 categories do not cover most of what Cornell photographs, so the detector produces nothing on more than half the test images. Those fall through to a geometric fallback, the platform-segmentation routine written for the split, which locates the object without knowing what it is. System A is therefore a hybrid: a category rule where the detector fires, a category-free geometric estimate where it does not. Calling it rule-based is fair since nothing is learned from grasp labels, but the lookup table is not doing most of the work.

The design also has a limitation I could state before running anything. A detector's box is axis-aligned, so the orientation rule emits only 0 or 90 degrees, and any diagonal object is unreachable however well the box is placed. That is a prediction from the representation, not an explanation invented afterward.

### System B, learned grasp predictor

System B regresses a grasp rectangle directly from an image: a backbone produces features, those features are pooled, and regression heads emit the rectangle's parameters. Orientation is encoded not as a raw angle but as the sine and cosine of twice the angle. The reason is that a parallel-jaw gripper rotated 180 degrees is mechanically identical, so the metric treats orientation as symmetric across half a turn. Regressing a raw angle would make two grasps two degrees apart look 178 degrees apart whenever they straddle the wraparound point, punishing the model for being right. Redmon and Angelova introduced this encoding for grasp regression (1316), and Morrison, Corke, and Leitner later used it in GG-CNN.

I trained three architectures: a small network built from scratch, a fine-tuned ResNet18, and a fine-tuned ResNet34. I expected ResNet34's extra capacity to be hard to use with only 620 training images, the classic setup for a larger model overfitting rather than generalizing. Architecture selection happened entirely on the validation split, before test was opened, so the model I report is the one validation chose rather than whichever got lucky on sealed data. That ordering is easy to get wrong and hard to detect afterward, which is why I fixed it in advance.

Two training details changed what the model learns. The loss was computed against every labeled grasp on an image, with only the best match backpropagated. Regressing toward the average of an image's grasps sounds reasonable and is actually harmful, since the average of a handle grasp and a rim grasp lands between them where neither is valid. Augmentation handled labels by pushing the rectangle's four corners through the same affine transform as the pixels and re-deriving the parameters, rather than writing a rule for how the angle behaves under a flip. Hand-written rules for that are easy to get backward, and the error stays invisible until accuracy is mysteriously bad.

Which published result System B should be measured against is worth getting right, because getting it wrong makes the paper tell the wrong story. GR-ConvNet reports 97.7% image-wise and 96.6% object-wise on Cornell (Kumra, Joshi, and Sahin 9626), and next to those numbers System B looks poor. But GR-ConvNet and GG-CNN are pixel-wise: they predict a grasp at every pixel of the input in a single pass, which is what lets GG-CNN close a control loop at 50 Hz (Morrison, Corke, and Leitner). System B does nothing of the kind. It pools a backbone's features and regresses one rectangle for the whole image, architecturally the same design Redmon and Angelova published in 2015, reporting 84.9% object-wise (1316). Against that comparison the gap is small, and every remaining difference points the same direction: they used RGB-D where I used RGB only, and roughly 3,000 augmented examples per original image where I used 620 real images total. None of that requires appealing to anything I did not measure.

### System C, zero-shot vision-language model

System C prompts GPT-4o with each test image and asks where the two gripper fingertips should touch. It receives no training, no examples, and no fine-tuning. The prompt was frozen after development on a 30-image training batch and never revised after test was opened.

One design decision closed off a whole category of false conclusions. I never asked for an angle. The model reports two contact points, and orientation is derived from them by the same function that produced every ground-truth angle in the dataset. Had I asked for an angle directly, a silent convention mismatch over degrees versus radians would have produced wrong scores indistinguishable from the model being bad at grasping. Each image was run five times, since output varies between calls, and that variation is reported rather than averaged away.

The temptation is to read 12.4% as confirming that vision-language models are bad at spatial tasks. That would be unsurprising and, I think, the wrong lesson. More telling is what published vision-language grasping systems do with the model. FreeGrasp has GPT-4o choose which object to grasp and in what order, using marks overlaid on the image rather than raw numbers (Jiao et al.). Lan-grasp picks which part to grasp, then hands the pose to a conventional planner (Mirjalili et al.). ThinkGrasp uses GPT-4o for clutter strategy, deciding what to move to uncover a target (Qian et al.). Set-of-Mark replaces coordinate output with a choice among labeled regions, letting zero-shot GPT-4V beat a fine-tuned referring-expression model on RefCOCOg (Yang et al.). VLAD-Grasp goes furthest, having the model draw a goal image with a virtual gripper intersecting the object (Kulshrestha et al.).

In all five, the model's output is a choice, a label, an ordering, or a picture, and the numeric pose comes from something else. I want to be careful about what I infer, since these systems solve different problems, several involving clutter my task does not have, so handing geometry to a planner may be the natural architecture rather than a judgment about coordinates. What I can say is narrower: I did not find a published grasping system that treats free-text coordinate emission as its primary geometric output, nor any benchmark of that path against non-VLM baselines on a shared split. System C is that measurement.

The failure pattern points at a mechanism. Of 615 calls, 365 missed on angle and overlap simultaneously, far more than either single-axis failure. A supplementary geometric check on the frozen predictions, outside the Cornell metric and used only as a diagnostic, asked whether each predicted center fell inside the convex hull of all labeled grasp rectangles. That is the loosest spatial test a prediction can fail, since the hull is larger than any single rectangle. System C failed it on 53.4% of calls, against 7.0% for System A and 6.5% for System B. That gap is real but not like-for-like: System B was trained on this distribution, and System A's center is built from a detected box or a segmentation, so both are close to guaranteed to land on the object. System C is the only one free to place a center anywhere, so the comparison shows its errors are a different kind, not simply more of the same.

Reading the model's written explanation alongside its coordinates on sampled failures showed the pattern behind that number. The explanation would name a real part of the object, the handle or the narrow end, while the coordinates in the same reply landed somewhere unrelated. That is a binding failure between two channels of one response rather than a failure to perceive. I treat that text as observable output, not as a transcript of how the model arrived at anything. Wang et al. document the same disconnect in an unrelated domain, finding models that describe a correct procedure on a visual puzzle and then click hundreds of pixels away: the model "solves the puzzle in words" but fails to ground those words into acceptable pixel coordinates (Wang et al., sec. 5.3.2). Their examples use a different model on a CAPTCHA task, so this corroborates the mechanism across contexts rather than repeating my experiment.

### The orientation axis

Each system's design predicts something different about how orientation should affect it, and those predictions can be checked against an axis sourced from the dataset rather than from any system's output. System A should suffer badly on diagonal objects, since its representation cannot express them. System B should be largely unaffected, since its encoding handles rotation by construction. System C has no structural position either way, so its behavior was open before I looked.

Splitting the test set by whether an image's labeled grasps sit more than 15 degrees off axis produced exactly that pattern. On the 20 diagonal images System A drops 21.2 points relative to the axis-aligned images, System B gains 12.3 points, and System C moves 2.0 points. Three systems, three directions, one split.

I want to be careful about what to claim. That axis-aligned boxes cannot represent diagonal grasps is derivable from the representation alone, and that rotation-aware encodings handle rotation is the entire reason those encodings exist. Neither is a discovery. What I could not find precedent for is using the stratification as a diagnostic instrument, taking an axis sourced from the dataset's own annotations and reading off which direction each technique family moves. Published Cornell work reports image-wise and object-wise splits, which measure generalization, not orientation-conditioned breakdowns of where a representation gives out. So I offer this as a method others could reuse cheaply, not as a fact about grasping.

The honest caveat is sample size. The diagonal stratum holds 20 images, its intervals are wide, and I ran no test of the joint three-way pattern against a null, so I cannot say how unlikely it is by chance. One cell is firmer: System A's drop was predicted from its representation before the stratum was scored, which makes it a confirmed prediction rather than a pattern found afterward. The rest is exploratory. The divergence earns its place as the diagnostic that pointed at the mechanism, not as a general result, and the effect sizes need a larger diagonal sample before anyone leans on them.

System C's near-flat response is doing quiet work there. A system with no working orientation signal should look flat on an orientation-stratified split, and it does, which agrees with the compound-failure taxonomy by a separate route.

I also tested a second axis, the number of grasps labeled per image, expecting a difficulty proxy. It did not behave like one. All three systems did worst on images carrying the most labeled grasps, even though more labeled grasps means more rectangles a prediction may match. My guess is that annotators labeled many grasps on objects that afford many, so the count tracks complexity rather than how generous the metric is. I report it because I measured it, and I use it to argue nothing.

### What this means

The coordinate-binding explanation makes a prediction that can be tested rather than asserted. If the problem is binding reasoning to emitted numbers rather than perceiving the object, then removing the numeric channel should help substantially, while sharpening perception alone should not. The literature is consistent with that without anyone framing it as a test. Set-of-Mark lets zero-shot GPT-4V beat a fine-tuned specialist purely by replacing coordinate emission with region selection (Yang et al.). VLAD-Grasp scores far above System C on Cornell, training-free, by having the model draw the grasp rather than state it (Kulshrestha et al.).

That second comparison is the one I find striking, and it reframes my own worst result, but two things stop it from being a number I can set against my 12.4%. VLAD-Grasp does not merely ask for a picture instead of a number. It then predicts depth and segmentation to lift that image into three dimensions and aligns point clouds to recover a pose, a geometric pipeline System C has no equivalent to. It also counts a grasp correct on overlap alone, without the 30-degree angle requirement I apply throughout, and reports 91.4% under that looser test. That the same evaluation scores GR-ConvNet at 72.1%, against the 97.7% it reports for itself, shows the two protocols are not on one scale. The dropped angle criterion matters most, since orientation is the axis this paper spends its Results on.

What survives the caveat is still worth stating. Two zero-shot uses of one pretrained model on the same benchmark produce very different outcomes, and the one that works never asks for a coordinate. Put that beside the failure taxonomy and beside Wang et al.'s independent observation, and the useful reading is that requesting raw coordinates carries a large cost unrelated to whether the model can see the object.

It is worth being plain about what is new here and what is not. The sine and cosine encoding has been standard since 2015. That vision-language models produce imprecise coordinates is established, not discovered. That learned models beat rule-based baselines on Cornell was settled a decade ago, so System A against System B confirms a known result, and its value here is as a controlled instrument for the orientation analysis. What this project adds is a measurement of the coordinate weakness on a standard benchmark, against two baselines on the identical split, with a mechanism-level account corroborated from an unrelated domain.

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

> **[FIGURE 2]** Insert `data/interim/comparison_sheets/compare_0348.png`. Caption below: "Fig. 2. An orientation-only failure. The predicted rectangle overlaps the object well (IoU 0.38) but is rotated 47 degrees from any labeled grasp." Note: of ResNet18's four angle-only failures (pcd0676, pcd0348, pcd0824, pcd0316) only pcd0348 has a rendered sheet.

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

Systems A and B agreed on 74 of 123 images, both correct on 60 and both wrong on 14. They disagreed on 49, which is the set where the learned model's contribution is visible. Counting System C as correct if any of its five repeats passed, all three systems succeeded on 22 images and all three failed on 10. Those 10 are the closest thing this test set has to a difficulty floor, since they defeat every technique family tried here even when the vision-language model is given five attempts.

The grasps-per-image axis is reported as a negative result. Grouped into images with 2 to 4 labeled grasps, 5 to 7, and 8 to 25, all three systems scored worst on the last group (48.0%, 64.0%, and 11.2% for A, B, and C) rather than the first, contradicting the premise that more labeled grasps should make a match easier. This axis supports no claim in this paper.

## Conclusion

Scoring three approaches through one pipeline showed that their errors are not interchangeable, and that is the finding I would keep if I could keep only one. The accuracies set the stage rather than settling anything: 57.7% for the rule-based system, 79.7% for the fine-tuned ResNet18, and 12.4% for zero-shot GPT-4o, whose best-of-five ceiling still falls below the rule-based system's lower 95% confidence bound.

What the comparison bought was the ability to see three failure modes side by side on the same images, scored by the same code. System A locates objects but cannot rotate the gripper, because an axis-aligned box has no way to express a diagonal grasp. System B rotates well, to within about four degrees, and its remaining errors are mostly about placing the rectangle rather than turning it. System C fails before either question is reached, because the coordinates it emits are frequently not bound to the object its own sentences have just described correctly. Those are three distinguishable problems, and knowing which one you have tells you what to fix.

The third failure is the one worth carrying forward, because another system does not have it. VLAD-Grasp uses a pretrained vision-language model zero-shot on this same dataset and scores far higher, and it never asks for a coordinate. It also does considerably more downstream and grades itself without the angle criterion I use, so its number and my 12.4% cannot simply be subtracted. What I can say is that asking a vision-language model for raw pixel coordinates carries a large, measurable cost, that the cost appears as the written explanation and the emitted numbers diverging rather than as the model failing to see, and that the same divergence has been observed independently in a completely different task.

If that reading is right, it makes a prediction worth testing. Rerunning System C with Set-of-Mark prompting, where the model selects among labeled regions instead of emitting coordinates, should recover a substantial part of the gap. If it does not, my diagnosis is wrong and the problem lies in perception after all, which would be worth knowing too. That experiment is cheap, it is the obvious next step, and I have not run it.

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
