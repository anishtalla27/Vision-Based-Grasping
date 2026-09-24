# Three Ways to Miss a Grasp

Code, data split, raw model outputs, and results for a comparison of four ways to predict a robot grasp from one RGB image, all scored by the same code on the same held-out objects.

Author: Anish Talla, Lightridge High School and Academies of Loudoun, Virginia. Contact: anish.talla99@gmail.com

## The question

A robot has to decide where to put its fingers before it can pick anything up. That decision can come from hand-written rules, from a network trained on labeled grasps, or from a general vision-language model that was never trained on grasping. Which one works, and when each fails, how does it fail?

## The four systems

| System | What it is | Trained on grasps? |
|---|---|---|
| A | COCO-pretrained Faster R-CNN detector plus a fixed lookup table, with a segmentation fallback. Outputs 0 or 90 degrees only. | No |
| B | ResNet18/34 regressing one grasp rectangle, angle encoded as (cos 2θ, sin 2θ), best-match loss. | Yes, 620 images |
| C | GPT-4o asked for two fingertip pixel coordinates and a jaw width. One frozen prompt, five calls per image. | No |
| D | GPT-4o shown numbered candidate grasps drawn on the image and asked to pick one. Candidates come from the object outline only, never from labels. | No |

Everything is scored with the standard Cornell rectangle metric: angle within 30 degrees of a labeled grasp and IoU above 25%. The split is object-wise (164 / 35 / 35 objects, 620 / 140 / 123 images), so no test object was seen in training. Confidence intervals resample whole objects (20,000 bootstrap draws).

## Results on the 123 test images

| System | Accuracy | 95% interval (object-clustered) |
|---|---|---|
| A, rules (40.7% before a post-hoc fix) | 57.7% | 46.2 to 68.2 |
| B, ResNet18, round 1, one seed | 79.7% | 70.8 to 87.1 |
| B, ResNet34, round 2, mean of three seeds | 84.0% | 73.9 to 92.1 |
| C, GPT-4o, one call | 12.4% | 8.0 to 17.4 |
| C, GPT-4o, best of five calls | 35.0% | 24.6 to 45.5 |

System D, same model and images, five calls per image:

| Candidate menu | Correct | Random-choice floor | Ceiling | Chose the lengthwise grasp |
|---|---|---|---|---|
| 12 marks, three positions | 18.7% | 20.1% | 79.7% | 70% |
| 4 marks at the center, real size | 26.5% | 24.6% | 65.9% | 41% |
| 4 marks at the center, all the same size | 22.3% | 24.6% | 65.9% | 45% |

What I take from this. GPT-4o put its grasp center outside the area covered by every labeled grasp on 53.4% of calls (about 7% for A and B), which looked like a problem with writing coordinates. System D removed the coordinates and the model still did no better than chance. It kept choosing a grasp that closes along the length of the object near one end. So the weak point is the grasp choice, not the coordinate output. A rule with no learning at all (close across the short axis at the object's center) scored 55.3%.

Things I got wrong and corrected are left in the record: System A's first score (40.7%) and the fix made after seeing test output, the round-1 claim that ResNet18 beats ResNet34 (three seeds showed it was noise), and a misdefined angle-error number in the first draft.

## What is in this repository

- `source_of_truth.md`: the project specification. Every decision was checked against it, and later changes are recorded there as addenda.
- `paper.tex`, `paper.pdf`: the full write-up.
- `scripts/`: all code. `grasp_metric.py` is the single scorer every system goes through, and `verify_grasp_metric.py` checks it against hand-computed cases.
- `data/interim/final_split.csv`: image id, reconstructed object id, and split for all 883 images. `boundary_decisions.csv` records how each ambiguous object boundary was decided.
- `data/interim/system_c_raw.jsonl`, `system_d_raw.jsonl`: every GPT-4o reply, verbatim, with the prompt version, the shuffled candidate order, and token counts. No API keys are in these files.
- `data/interim/*_results.md`, `*_predictions*.csv`, `*_per_image.csv`: the saved outputs behind every table above.
- `figures/`: images used in the paper.

The Cornell images themselves are not included. Model checkpoints are not included because of their size.

## Reproducing the numbers

You do not need a GPU or an API key to check the results, because the predictions and raw replies are saved.

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 1. check the scorer against hand-computed cases
python scripts/verify_grasp_metric.py

# 2. re-score the saved predictions and rebuild the comparison tables
python scripts/system_all_compare.py
python scripts/object_clustered_stats.py        # A, B, C with object-clustered intervals
python scripts/object_clustered_stats_v2.py     # System B round 2
python scripts/system_d_eval.py test            # System D, full menu
python scripts/system_d_eval.py test_sparse
python scripts/system_d_eval.py test_equal
python scripts/object_clustered_stats_d_menus.py
```

Steps 2 onward need the Cornell Grasping Dataset under `data/raw/` for the ground-truth rectangles. To rerun everything from scratch:

```bash
python scripts/cornell_object_grouping.py                 # rebuild the object-wise split
python scripts/system_a_run.py                            # System A (after detect + calibrate)
python scripts/system_b_train_v2.py --model resnet34 --seed 0   # repeat for seeds 1, 2 and resnet18
python scripts/system_b_eval_v2.py
python scripts/system_c_run.py test                       # needs OPENROUTER_API_KEY in .env, about $3
python scripts/system_d_run.py test full                  # also sparse, equal; about $2 each
```

The GPT-4o test runs are guarded by sentinel files so they cannot be called twice by accident. GPT-4o is not deterministic, so a rerun will not reproduce the saved replies exactly.

## Use of AI tools

GPT-4o is the model being studied. Separately, Anthropic's Claude Code was used as a coding and writing assistant throughout (code, a first pass at object boundaries that was then audited by hand, the second training round and System D implemented under my design, and help drafting and editing text). OpenAI Codex helped shorten a conference version. The research question, design, decisions, and checking of results are mine.

## Citation

If you use this work, please cite the write-up in this repository:

> A. Talla, "Three Ways to Miss a Grasp: A Same-Metric Comparison of Rule-Based, Learned, and Zero-Shot Vision-Language Grasp Prediction," 2026. https://github.com/anishtalla27/Vision-Based-Grasping

The Cornell Grasping Dataset is from Jiang, Moseson, and Saxena (ICRA 2011).
