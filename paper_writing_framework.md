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

**Length:** 200–300 words (see Section 5, which is authoritative on all length
targets). Write this last.

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

**Length:** 650–950 words (see Section 5, which is authoritative on all length
targets).

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

**Length:** 250–380 words (see Section 5, which is authoritative on all length
targets).

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
the parenthetical and give just the page: Jiang et al. introduced the five-parameter
grasping rectangle (3306).

**Two authors:** name both, last name only, joined with "and": (Redmon and Angelova 1316).
In the Works Cited entry, invert only the first: "Redmon, Joseph, and Anelia Angelova."

**Three or more authors:** first author's last name plus "et al.", both in text and in
Works Cited: (Lenz et al. 712), and the entry reads "Lenz, Ian, et al." This is the MLA 9
rule and it changed from older editions. MLA 7 listed up to three authors in full, so
guidance found online may still show "Lenz, Lee, and Saxena." Do not follow it. The cutoff
is three, not four, and it applies to every source in this paper with three or more names:
Jiang, Kumra, Lenz, and Morrison.

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