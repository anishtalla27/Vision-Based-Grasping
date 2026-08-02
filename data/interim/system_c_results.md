# System C results (vision-language model baseline)

Spec section 5.4, scored with the same section 6 metric and the same 123 held-out test images as Systems A and B. GPT-4o via OpenRouter, prompt v1, frozen on a 30-image train dev batch before this run. 5 independent repeats per image, no shared conversation, default temperature -- the spec's premise is that out-of-the-box output varies run to run, so nothing here suppresses that.


## Headline

**System C (GPT-4o) — 12.4% mean per-repeat accuracy** (min 9.8%, max 14.6%, std 1.9, over 5 independent repeats of the 123-image test split).

This is what a deployed system making one call per image actually gets, spread included rather than averaged away. Per-repeat accuracies: 13.0%, 14.6%, 13.8%, 10.6%, 9.8%.


## Not the headline: upper-bound numbers

Reported for completeness, explicitly not comparable to System A/B's single-prediction numbers as a fair baseline figure -- both require either multiple calls or knowing the answer in a way a real one-shot deployment would not.

| | Accuracy | Note |
|---|---|---|
| Best-of-5 | 35.0% | at least 1 of 5 repeats correct |
| Majority-consensus | 12.2% | the repeat that agrees most with the other repeats, scored (123/123 images had a parsed repeat to choose from) |

## Parse outcomes, end to end

615 calls total (123 images x 5 repeats).

| Outcome | Count | Share |
|---|---|---|
| ok | 614 | 99.8% |
| parse_fail | 1 | 0.2% |
| schema_fail | 0 | 0.0% |
| range_fail | 0 | 0.0% |
| api_fail | 0 | 0.0% |

Parse failures are never silently scored as a wrong grasp -- the headline above already counts every non-`ok` call as a miss for its repeat (end-to-end). Accuracy computed on parsed (`ok`) calls only would be 12.4% vs 99.8% of calls actually parsing -- see the per-repeat table above for the honest, end-to-end figure.


## Failure taxonomy (of parsed calls)

| Outcome | Count | Share of parsed calls |
|---|---|---|
| correct | 76 | 12.4% |
| angle_only | 85 | 13.8% |
| iou_only | 88 | 14.3% |
| both | 365 | 59.4% |

614 of 615 calls parsed to a scoreable rectangle.


## Self-agreement, at n=5 repeats (the real curve, not the 2-repeat dev preview)

Mean self-agreement: 22.0%  (median 20.0%), over 123/123 images with at least 2 parsed repeats to compare.

Mean pairwise angle spread between repeats: 5.8 deg. Mean pairwise IoU between repeats: 0.13.


**Outcome histogram** -- of the 5 repeats, how many scored correct:

| Repeats correct | Images | Share |
|---|---|---|
| 5/5 | 1 | 0.8% |
| 4/5 | 3 | 2.4% |
| 3/5 | 6 | 4.9% |
| 2/5 | 8 | 6.5% |
| 1/5 | 25 | 20.3% |
| 0/5 | 80 | 65.0% |

**Consistency rate** (all 5 repeats agreed on the outcome, either 5/5 or 0/5): **65.9%** (81/123 images). The remaining 42 images are the unstable band -- the same model, the same pixels, sometimes producing a passing grasp and sometimes not.


**Abstention curve** -- if the system only acts when self-agreement is at or above a threshold, what accuracy does it get on the images it acts on, and what coverage does it keep:

| Threshold | Coverage | Accuracy on covered |
|---|---|---|
| >= 0.0 | 100.0% | 35.0% |
| >= 0.2 | 54.5% | 44.8% |
| >= 0.4 | 21.1% | 57.7% |
| >= 0.6 | 5.7% | 42.9% |
| >= 0.8 | 0.8% | 0.0% |
| >= 1.0 | 0.8% | 0.0% |

Read this as **self-agreement is a usable confidence signal for this task**, not as System C being competitive under any real deployment. A gripper that only acted when its 5 repeats agreed at least 40% of the time would see 57.7% accuracy on the 21.1% of images it acted on -- a genuine, non-obvious finding, and a real basis for an abstain-and-ask-for-help policy. But the system this project is actually comparing against Systems A and B is the one-call-per-image deployment, which is the 12.4% headline above. The 57.7%-on-21% figure does not change that comparison: it describes which grasps to trust among five expensive repeated calls, not what a single call gets you. The two numbers answer different questions and neither should be read in place of the other.

## Training-data contamination

The direction of this risk only inflates System C, never deflates it, so "System C underperforms System B" survives it and "System C does surprisingly well" does not -- it would need to be read as an upper bound, not clean zero-shot capability.

Contamination probe (10 train images, asked to name the dataset without being told the task is grasping): **0/10 recognised it.** Non-recognition is not proof of no exposure -- memorised weights do not have to be able to name their source -- so this is reported as a mild indicator, not a clearance.


## Three-way comparison, same sealed 123-image test set

| System | Test accuracy |
|---|---|
| A (rule-based) | 57.7% |
| B (resnet18, val-selected) | **79.7%** |
| C (GPT-4o, mean of 5 repeats) | 12.4% |

System C trails System A (-45.3 points) and trails System B (-67.3 points) on the identical sealed test split. Given the contamination risk above, any reading of System C beating a trained baseline should be treated cautiously; a reading of System C trailing one is not affected by that risk.


## Method note: the coordinate-binding limitation

The dominant test-time failure mode, consistent with what the train-30 dev batch showed, is a **text-to-coordinate binding limitation of this prompting approach** -- asking a VLM to emit precise pixel coordinates as free-text JSON. Several failed replies carried plausible, specific `reasoning` strings describing a real part of the object, while the `finger_a`/`finger_b` coordinates in the same reply did not land on the object at all. This is stated as a limitation of prompting for coordinates via free text specifically, not as a general claim about GPT-4o's or VLMs' spatial grounding capability -- a different elicitation method (e.g. point-and-click grounding tools, set-of-marks prompting) might bind reasoning to coordinates more reliably. That comparison is out of scope here.

## Method note: verification discipline as a project pattern

Before this number was reported, an automated contamination-probe check flagged 1/10 as a dataset recognition. Manual reading of the same 10 replies (done independently, before the automated check) said 0/10. The disagreement was chased down rather than either number being trusted on its own: the automated check's negation logic tested for a straight apostrophe (`don't`) and the model's reply used a curly one (`don't`, U+2019), so the check silently failed to match and mis-flagged a plain non-recognition as a hit. Fixed and re-scored against the frozen raw text -- a re-parse, not a re-call, per this project's rule that re-parsing sealed data is allowed and re-querying the model is not.

This is the third time in this project that a self-authored check caught a bug in the project's own code before a number was reported, rather than after: System B's early-stopping floor initially anchored on an untrained epoch-0 fluke, caught and fixed before it was reported as a result; an earlier corruption in split-generation output was caught and fixed before the frozen train/val/test split was used for anything; and now this smart-quote mismatch. None of these were caught by an external reviewer or by a suspicious-looking headline number -- each was caught by deliberately cross-checking an automated result against an independent method (a second computation, a manual read, a synthetic case) before accepting it. That cross-checking habit is a methodological property of how this project was built, not an incidental detail, and is named here explicitly rather than only benefited from silently.

## Amendment 2 (2026-08-02): a post-seal fix to a verification script, not to the result

While building the Section 6 cross-system comparison, `verify_system_c.py`'s sentinel-hygiene check started failing every run. The check (added when System C's verification suite was first written) asserted that `data/interim/system_c_test_called.json` -- the sentinel that stops the sealed test phase from being run twice -- **does not exist**. That was true and meaningful right up until the sealed test run legitimately happened; after that, the file is supposed to exist permanently, so the assertion became permanently false through no fault in the code it was checking. It was testing "has the real sentinel been touched," badly, by testing "is the real sentinel absent."

**Before:** `check("the real test sentinel was not created by this check", not real.exists())`.

**After:** the check now records whether the real sentinel existed before the check ran, exercises `seal_test()` only against a throwaway temp-directory path (as it always did), and then asserts the real sentinel's existence is unchanged by that: `check("this check did not create or remove the real test sentinel", real.exists() == existed_before)`. This is what the check was always meant to verify -- that exercising the sentinel logic in the test suite never touches the real one -- expressed in a form that stays true both before and after a legitimate sealed run, rather than only before.

**Confirmed: this touches no prompt, no parser, no raw API data, and no reported number.** It is a correction to a test assertion's phrasing, not a re-opening of the sealed test run -- the same distinction that makes the approved re-parse-not-re-call rule work: the file being asserted about (the sentinel) and the data it protects (`system_c_raw.jsonl`, all `system_c_predictions.csv` / `system_c_results.md` figures above) are untouched. Nothing in this document changed as a result.

