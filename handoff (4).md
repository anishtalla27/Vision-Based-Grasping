# Handoff — Vision Grasp Project: All Systems Sealed, Now Entering Paper-Writing Phase

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
