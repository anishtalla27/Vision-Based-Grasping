"""Score System D (Set-of-Mark selection) from its raw log. Makes no calls.

Every number is read against two label-free reference points computed
on the SAME candidate sets the model saw:

  oracle   an image counts if ANY candidate passes the metric (ceiling)
  random   expected accuracy of a uniformly random choice (floor)

plus the deterministic geometric rule (candidate 0: centroid, close
across the short axis), which is a non-learned baseline that can
express a diagonal grasp, unlike System A.

The comparison that answers the paper's open question is System D
(choose among marks) against System C (emit coordinates), same model,
same images, same metric, same five repeats.

Usage:
    python scripts/system_d_eval.py [dev|test]
"""

import csv
import json
import sys
from collections import Counter, defaultdict

import numpy as np

from cornell_data import INTERIM, find_images, load_rects, load_split
from grasp_metric import is_correct
from system_d_candidates import candidates
from system_d_prompt import OK, parse_response
from system_d_run import RAW_JSONL

C_CSV = INTERIM / "system_c_predictions.csv"


def load_records(tag):
    out = defaultdict(dict)
    for line in RAW_JSONL.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("tag") == tag:
                out[r["pcd_id"]][r["repeat"]] = r
    return out


def system_c_by_image():
    """Per-image per-repeat correctness of System C from its sealed csv."""
    if not C_CSV.exists():
        return {}
    out = defaultdict(list)
    for r in csv.DictReader(open(C_CSV)):
        out[int(r["pcd_id"])].append(int(r["correct"] or 0))
    return out


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "test"
    menu = "equal" if tag.endswith("_equal") else "sparse" if tag.endswith("_sparse") else "full"
    recs = load_records(tag)
    if not recs:
        raise SystemExit(f"no '{tag}' records in {RAW_JSONL}")
    images = find_images()
    table = load_split()
    pcds = sorted(recs)
    n_rep = max(len(v) for v in recs.values())

    outcomes = Counter()
    per_image = {}
    for pcd in pcds:
        cands = candidates(images[pcd], menu)
        gts = load_rects(pcd)
        passing = [is_correct(c["rect"], gts)[0] for c in cands]
        row = {"pcd_id": pcd, "object_id": table[pcd][0], "n_cands": len(cands),
               "oracle": int(any(passing)), "random": float(np.mean(passing)) if passing else 0.0,
               "geometric": int(passing[0]) if passing else 0,
               "correct": [], "chosen": []}
        for rep in range(n_rep):
            r = recs[pcd].get(rep)
            if r is None or r.get("text") is None:
                outcomes[r.get("outcome_override", "api_fail") if r else "missing"] += 1
                row["correct"].append(0)
                row["chosen"].append(None)
                continue
            k = len(r["order"])
            outcome, meta = parse_response(r["text"], k)
            outcomes[outcome] += 1
            if outcome != OK:
                row["correct"].append(0)
                row["chosen"].append(None)
                continue
            ci = r["order"][meta["choice"] - 1]        # mark number -> physical candidate
            row["chosen"].append(ci)
            row["correct"].append(int(passing[ci]))
        per_image[pcd] = row

    n = len(pcds)
    rows = list(per_image.values())
    per_rep = [np.mean([r["correct"][k] for r in rows]) * 100 for k in range(n_rep)]
    mean_acc = float(np.mean(per_rep))
    best_of = np.mean([max(r["correct"]) for r in rows]) * 100
    oracle = np.mean([r["oracle"] for r in rows]) * 100
    rand = np.mean([r["random"] for r in rows]) * 100
    geo = np.mean([r["geometric"] for r in rows]) * 100
    agree = []
    for r in rows:
        ch = [c for c in r["chosen"] if c is not None]
        if len(ch) >= 2:
            pairs = [(a == b) for i, a in enumerate(ch) for b in ch[i + 1:]]
            agree.append(np.mean(pairs))
    n_nocand = sum(1 for r in rows if r["n_cands"] == 0)

    print(f"System D ({tag}, menu={menu}): {n} images x {n_rep} repeats, {n_nocand} images without candidates")
    # orientation preference, the quantity the sparse menus exist to measure
    orient = Counter()
    for r in rows:
        for ci in r["chosen"]:
            if ci is not None:
                orient[candidates(images[r["pcd_id"]], menu)[ci]["orient"]] += 1
    tot = sum(orient.values()) or 1
    print("chosen orientation offset (0 = across short axis):",
          {k: f"{v} ({v/tot*100:.0f}%)" for k, v in sorted(orient.items())})
    print("parse outcomes:", dict(outcomes))
    print(f"  mean per-repeat accuracy  {mean_acc:5.1f}%   per repeat {[round(p, 1) for p in per_rep]}")
    print(f"  best-of-{n_rep}                 {best_of:5.1f}%")
    print(f"  random-choice floor       {rand:5.1f}%")
    print(f"  geometric rule (cand 0)   {geo:5.1f}%")
    print(f"  oracle ceiling            {oracle:5.1f}%")
    print(f"  mean self-agreement on physical candidate {np.mean(agree)*100:.1f}%")

    c = system_c_by_image()
    if c and tag == "test":
        c_mean = np.mean([np.mean(c[p]) for p in pcds]) * 100
        print(f"\nSame model, same images: System C (coordinates) {c_mean:.1f}% vs "
              f"System D (choose a mark) {mean_acc:.1f}%")

    out_csv = INTERIM / f"system_d_{tag}_per_image.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pcd_id", "object_id", "n_cands", "oracle", "random", "geometric",
                    "d_repeats_correct", "chosen"])
        for r in rows:
            w.writerow([f"{r['pcd_id']:04d}", r["object_id"], r["n_cands"], r["oracle"],
                        f"{r['random']:.3f}", r["geometric"], sum(r["correct"]),
                        "|".join("-" if x is None else str(x) for x in r["chosen"])])
    summary = {"tag": tag, "n_images": n, "repeats": n_rep, "per_repeat": per_rep,
               "mean_acc": mean_acc, "best_of": best_of, "random": rand, "geometric": geo,
               "oracle": oracle, "self_agreement": float(np.mean(agree)) if agree else None,
               "outcomes": dict(outcomes), "no_candidates": n_nocand}
    (INTERIM / f"system_d_{tag}_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nWrote {out_csv}")


if __name__ == "__main__":
    main()
