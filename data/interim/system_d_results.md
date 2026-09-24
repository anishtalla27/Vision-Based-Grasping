# System D results (Set-of-Mark grasp selection, GPT-4o)

The experiment the paper named as its untested next step. Same model
(`openai/gpt-4o` via OpenRouter), same sealed 123-image test split, same
metric, same five independent single-turn repeats per image as System C.
The only change: the model is shown 12 label-free candidate grasps drawn
on a zoomed crop of the object and asked to CHOOSE one by number. It
never emits a coordinate. Test was called once (`system_d_test_called.json`).

Candidates come from the platform segmentation mask alone (PCA centroid
and axes, 3 positions x 4 orientations 45 degrees apart, System A's
train-calibrated opening and jaw constants). No grasp label is read
anywhere in candidate generation. 11 test images have no mask and
therefore no candidates; they count as misses for every row below,
including the floor and ceiling, so the comparisons stay paired.

## Headline

| Measure | Test | Object-clustered 95% CI |
|---|---|---|
| **System D, mean per-repeat accuracy** | **18.7%** (per repeat 17.1, 17.1, 17.9, 20.3, 21.1) | [9.5, 29.7] |
| Random choice among the same candidates (floor) | 20.1% | [14.6, 26.6] |
| Any candidate passes (oracle ceiling) | 79.7% | [67.2, 90.0] |
| Geometric rule alone, candidate 0 (no VLM) | 55.3% | [41.8, 68.0] |
| System D best-of-5 | 39.0% | [26.2, 52.3] |
| System C (same model, emit coordinates) | 12.4% | [8.0, 17.4] |
| Parse rate | 560/560 called (100%) | |

Paired, object-clustered (20,000 bootstrap resamples, 20,000 permutations):

| Difference | Points | 95% CI | Permutation p |
|---|---|---|---|
| D minus random floor | -1.4 | [-6.6, +4.0] | 0.62 |
| D minus C (marks vs coordinates) | +6.3 | [-1.6, +15.0] | 0.19 |
| Geometric rule minus System A | -2.4 | [-10.1, +5.4] | 0.68 |
| Geometric rule minus D | +36.6 | [+24.3, +49.4] | 5e-5 |
| System B minus geometric rule | +24.4 | [+9.6, +39.4] | 0.005 |

## What it means

The coordinate-binding hypothesis predicted that removing the coordinate
output would recover the model's grasp choice. It did not. Given a menu
whose ceiling is 79.7%, GPT-4o's choice is indistinguishable from a
uniformly random draw from that menu. The candidate it prefers is not
random, though: it is systematically wrong.

| Chosen candidate type (560 parsed calls) | Share chosen | Pass rate of that type on test |
|---|---|---|
| jaws travel along the LONG axis, near one end (position -0.35, orient 90) | 342/560 = 61% (70% chose that orientation at any position) | 17.0% |
| centroid, jaws travel across the SHORT axis (candidate 0) | 34/560 = 6% | 60.7% |

Across all 12 types the model chose the long-axis orientation in 391 of
560 calls; the four short-axis candidates, which pass 33-61% of the time,
were chosen 55 times. Its written reasoning for the long-axis end pinch
was typically "grips the narrow top edge near the centre of mass". From a
top-down photograph, a candidate whose two pads straddle the end of an
elongated object does look like it pinches a narrow part. In three
dimensions the second finger would land on top of the object, not beside
it. This reads as a failure of 3-D grasp reasoning from a 2-D view, not
of binding text to coordinates.

Stated confidence carried no information: "high" on 556 of 560 calls,
21% of them correct.

Self-agreement across repeats (same physical candidate chosen, with
numbering re-shuffled every call) was 44.3%, twice System C's 22.0%,
which is consistent with a stable preference rather than noise.

## Prompt development record

Two dev passes on the same 30 fixed TRAIN images used by System C, 2
repeats each, selected on parse rate and rendering convention only:

- V1 (thin line, small end ticks): 58/58 parsed. The model chose
  long-axis lines in 34/58 calls while describing a grasp "across the
  narrowest part", which could have been a misreading of the glyph.
- V2 (thick fingertip pads, inward arrowheads, wording that describes
  them): 58/58 parsed. Same behaviour, 41/58. Frozen. Dev accuracy was at
  the random floor (20.0%) in both versions and was not used to choose.

The persistence under an unambiguous glyph is what licenses reading the
test result as the model's preference rather than a drawing artefact.

## Scope

One model, one marking scheme (12 overlapping marks on a zoomed crop),
one candidate generator. One rendering caveat cuts the other way from the
V1/V2 concern: on thin objects the short-axis candidates are drawn with
the small opening the labels actually use (about 0.7 of the object's
width, clamped at 12 px), so the correct candidates on a pen or a bean
are visually the smallest marks on the image, while the long-axis
candidates are the largest. A model that favours large, salient marks
would show exactly this preference for a reason unrelated to grasping.
The marks are the same size the ground-truth rectangles would be, so
this is a property of the task's own representation, but it is a
plausible mechanism and is not ruled out here. A sparser menu, a different mark style, or a
model with a 3-D prior might do better; that is not tested here. What is
tested is the paper's specific claim, and the claim does not survive.

Cost: 615 test calls plus 120 dev calls, about $2.1 of OpenRouter credit.
Raw replies, mark permutations and the exact rendered images the model
saw are in `system_d_raw.jsonl` and `system_d_marked/`.

## Follow-up: sparse menus and the mark-size confound (13 September 2026)

The scope note above left one mechanism open: on thin objects the
correct marks are the smallest on the image, so a preference for large
marks would mimic a preference for the long-axis grasp. Two further
sealed test runs close it. Both use four candidates at the centroid
only (jaws travelling across the short axis, then +45, +90, +135
degrees), so position is removed and the end-straddling candidates that
dominated the full menu do not exist. They differ in one thing:

- **sparse**: each mark drawn at its real opening (long-axis mark largest)
- **equal**: same four candidates, same scored geometry, every mark drawn
  at one uniform length, with the prompt stating the length is not to
  scale (`PROMPT_V2_EQUAL`, one added sentence)

Same model, same 123 test images, five repeats, numbering re-shuffled
per call, prompt frozen after a one-repeat dev parse check on the 30
train images (29/29 parsed for both menus). Sentinels
`system_d_test_called_sparse.json` and `_equal.json`.

| Menu | Marks | D accuracy (CI) | Random floor | Oracle | Long-axis orientation chosen | Short-axis (correct-type) chosen |
|---|---|---|---|---|---|---|
| full (original) | 12 | 18.7% [9.5, 29.7] | 20.1% | 79.7% | 70% | 10% |
| sparse | 4 | 26.5% [17.8, 36.1] | 24.6% | 65.9% | 41% | 26% |
| equal size | 4 | 22.3% [12.9, 33.6] | 24.6% | 65.9% | 45% | 17% |

Paired, object-clustered: sparse minus its floor +1.9 [-2.2, +6.3]
p = 0.40; equal minus its floor -2.3 [-6.3, +1.7] p = 0.28; sparse minus
equal +4.2 [-0.5, +9.4] p = 0.14; sparse minus full +7.8 [+1.9, +13.9]
p = 0.02, but the sparse floor is also 4.5 points higher, so that gain
belongs to the menu, not to the model.

What this settles:

- **Mark size is not the driver.** With all four marks identical in
  size, the long-axis orientation is still chosen 45% of the time
  against a 25% chance rate, and the short-axis candidate, the one that
  passes on 55% of images, is chosen 17% of the time, below chance.
- **The preference is weaker without end-straddling candidates** (70%
  on the full menu, 41-45% on the centroid-only menus), so part of the
  full-menu result was the end-pinch illusion specifically, and part is
  a plain preference for closing along the long axis.
- **Accuracy is at chance on every menu.** Three menus, 1,845 calls,
  three random floors, no paired difference excludes zero.

Cost of the follow-up: 1,230 test calls plus 60 dev calls, about $3.9.
