"""Prompt development for System C. TRAIN only, 30 fixed images.

WHAT THIS IS FOR, AND WHAT IT IS NOT FOR
----------------------------------------
The prompt is a hyperparameter, so it needs somewhere to be developed,
and that somewhere has to be train -- the same images System B was
allowed to fit. Val and test are never opened here; the id list is
re-checked against load_split() and this script hard-fails otherwise.

The SELECTION CRITERION is parse success rate and geometric sanity, not
grasp accuracy. A prompt reworded until the accuracy climbs is a prompt
fitted to the metric, and System C would stop being a zero-shot
baseline. So the prompt is chosen on whether the model returns
well-formed, interpretable answers.

Train accuracy IS printed, clearly labelled, because it is the only
thing that would catch a systematic frame error -- a prompt that parses
perfectly every time while the model reads y from the bottom would show
a clean 100% parse rate and near-zero accuracy, and there is no other
signal that separates that from "the model is bad at grasping". It is a
diagnostic. It is not what picks the prompt.

Usage:
    python scripts/system_c_dev.py            score whatever dev calls exist
    python scripts/system_c_dev.py --call     make the calls first
"""

import sys
from collections import Counter

import numpy as np

from cornell_data import load_rects, load_split
from grasp_metric import is_correct
from system_c_client import load_raw, run_calls
from system_c_prompt import (MAX_JAW_PX, MAX_OPEN_PX, OK, PROMPT,
                             PROMPT_VERSION, parse_response, response_to_rect)
from system_c_run import assert_split, pick

DEV_N = 30
DEV_REPEATS = 2
TAG = "dev"


def dev_ids():
    ids = pick("train", DEV_N)
    assert_split(ids, "train")
    return ids


def make_calls():
    ids = dev_ids()
    jobs = [(p, r) for p in ids for r in range(DEV_REPEATS)]
    print(f"\ndev: {len(ids)} train images x {DEV_REPEATS} repeats = "
          f"{len(jobs)} calls (prompt {PROMPT_VERSION})")
    run_calls(jobs, PROMPT, tag=TAG)


def report():
    """Parse rates and geometry first, accuracy last and labelled."""
    table = load_split()
    records = [r for r in load_raw(TAG) if table.get(r["pcd_id"], (0, ""))[1] == "train"]
    if not records:
        raise SystemExit("no dev records yet; run with --call")

    outcomes, reasons = Counter(), Counter()
    rects, correct = [], []
    for rec in records:
        if rec.get("text") is None:
            outcomes[rec.get("outcome_override", "api_fail")] += 1
            continue
        outcome, meta = parse_response(rec["text"])
        outcomes[outcome] += 1
        if outcome != OK:
            reasons[meta.get("reason", "?")] += 1
            continue
        rect = response_to_rect(meta)
        rects.append(rect)
        gts = load_rects(rec["pcd_id"])
        correct.append(bool(gts) and is_correct(rect, gts)[0])

    n = len(records)
    print(f"\nPrompt {PROMPT_VERSION}, {n} calls over {len({r['pcd_id'] for r in records})} "
          "train images\n")
    print("SELECTION CRITERION -- parse outcomes")
    for k, v in outcomes.most_common():
        print(f"  {k:<12} {v:4d}  ({v / n * 100:5.1f}%)")
    if reasons:
        print("\n  why the failures failed")
        for k, v in reasons.most_common(6):
            print(f"    {v:3d}x  {k}")

    if rects:
        a = np.array(rects)
        print("\nSELECTION CRITERION -- geometric sanity of parsed grasps")
        print(f"  opening px   median {np.median(a[:, 3]):6.1f}  "
              f"range {a[:, 3].min():.0f}-{a[:, 3].max():.0f}  "
              f"(cap {MAX_OPEN_PX:.0f})")
        print(f"  jaw px       median {np.median(a[:, 4]):6.1f}  "
              f"range {a[:, 4].min():.0f}-{a[:, 4].max():.0f}  "
              f"(cap {MAX_JAW_PX:.0f})")
        print(f"  theta deg    spread {a[:, 2].std():6.1f}  "
              f"range {a[:, 2].min():.0f} to {a[:, 2].max():.0f}")
        print(f"  centre px    x {a[:, 0].mean():5.0f} +/- {a[:, 0].std():4.0f}   "
              f"y {a[:, 1].mean():5.0f} +/- {a[:, 1].std():4.0f}")

    if correct:
        print("\nDIAGNOSTIC ONLY -- train accuracy (does NOT select the prompt)")
        print(f"  {np.mean(correct) * 100:.1f}% of parsed dev grasps match a train label")
        print("  near zero here with a clean parse rate would mean a systematic")
        print("  frame error, not a model that is bad at grasping.")


def main():
    if "--call" in sys.argv:
        make_calls()
    report()


if __name__ == "__main__":
    main()
