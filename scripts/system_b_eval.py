"""Final System B evaluation. The only file in the project that opens test.

THE ONE TRAP WORTH NAMING
-------------------------
Three architectures were trained. Reporting whichever of them happens to
score best ON TEST would be test leakage wearing a lab coat: the test
split would then have influenced a choice, and the headline number would
be optimistically biased by exactly the amount of that choice.

So the architecture is selected on VAL, in system_b_train.py, before this
script runs. All three test numbers are printed for transparency, but the
headline is the val-selected model, and this script states which one that
is and why. Test is evaluated once.

Everything else mirrors System A's evaluation so the comparison is like
for like: the same frozen metric, the same 123 held-out images, the same
per-category and failure-case reporting.

Usage:
    python scripts/system_b_eval.py     (after system_b_train.py)

Outputs:
    data/interim/system_b_predictions.csv
    data/interim/system_b_results.md
    data/interim/system_b_sheets/*.png
"""

import csv
import json

import numpy as np
import torch
from PIL import Image, ImageDraw
from torch.utils.data import DataLoader

from cornell_data import INTERIM, rect_to_corners
from grasp_dataset import SIZE, GraspDataset
from grasp_metric import ANGLE_TOL_DEG, IOU_MIN, angle_diff, is_correct
from system_b_model import MODELS, build, decode
from system_b_train import CKPT_DIR, device

PRED_CSV = INTERIM / "system_b_predictions.csv"
RESULTS_MD = INTERIM / "system_b_results.md"
SHEETS = INTERIM / "system_b_sheets"
TRAINING_JSON = INTERIM / "system_b_training.json"

# System A's numbers, for the head-to-head. Frozen facts from commit f3124c6.
SYSTEM_A_ACC = 57.7
SYSTEM_A_DETECTOR_ONLY = 22.8
SYSTEM_A_ANGLE_ONLY_FAILURES = 13
SYSTEM_A_TOTAL_FAILURES = 52


def load_test():
    """Build the test dataset, asserting it is genuinely test-only."""
    ds = GraspDataset("test", augment=False)
    from cornell_data import load_split
    table = load_split()
    leaked = [p for p in ds.ids if table[p][1] != "test"]
    if leaked:
        raise SystemExit(f"SPLIT LEAK: {len(leaked)} non-test images in the test set")
    print(f"Split hygiene OK: {len(ds.ids)} images, all test, zero train/val.")
    return ds


def predict(model, ds, dev):
    """Run one model over the test split. Returns [(pred, gts)] per image."""
    model.eval()
    out = []
    loader = DataLoader(ds, batch_size=32, shuffle=False, num_workers=0)
    with torch.inference_mode():
        for x, targets, n in loader:
            preds = decode(model(x.to(dev)))
            t = targets.numpy()
            for i in range(len(preds)):
                gts = [(t[i, k, 0] * SIZE, t[i, k, 1] * SIZE, t[i, k, 2],
                        t[i, k, 3] * SIZE, t[i, k, 4] * SIZE)
                       for k in range(int(n[i]))]
                out.append((tuple(float(v) for v in preds[i]), gts))
    return out


def score(rows):
    """Section 6 accuracy plus the diagnostics the write-up needs."""
    n_ok = 0
    angle_only = iou_only = 0
    records = []
    for pred, gts in rows:
        ok, _, best_iou, best_ang = is_correct(pred, gts)
        n_ok += ok
        if not ok:
            # Which criterion did it miss on? Distinguishes "wrong place"
            # from "right place, wrong rotation", which is exactly the
            # axis System A was pinned on.
            if best_iou > IOU_MIN and best_ang > ANGLE_TOL_DEG:
                angle_only += 1
            elif best_ang <= ANGLE_TOL_DEG and best_iou <= IOU_MIN:
                iou_only += 1
        records.append((pred, gts, ok, best_iou, best_ang))
    n = len(rows)
    ang_err = float(np.mean([min(angle_diff(p[2], g[2]) for g in gs)
                             for p, gs in rows]))
    return {"n": n, "correct": n_ok, "acc": n_ok / n * 100,
            "angle_only": angle_only, "iou_only": iou_only,
            "mean_angle_err": ang_err, "records": records}


def draw_sheets(ds, records, name, k=12):
    """Prediction (red) vs ground truth (green) on the test images."""
    SHEETS.mkdir(parents=True, exist_ok=True)
    for i in range(min(k, len(records))):
        img, _ = ds.sample(i, None)
        im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
        d = ImageDraw.Draw(im)
        pred, gts, ok, iou, ang = records[i]
        for g in gts:
            d.polygon([tuple(p) for p in rect_to_corners(*g)], outline=(0, 230, 0))
        d.polygon([tuple(p) for p in rect_to_corners(*pred)],
                  outline=(255, 40, 40), width=2)
        d.text((3, 3), f"pcd{ds.ids[i]:04d} {'OK' if ok else 'MISS'} "
                       f"iou={iou:.2f} ang={ang:.0f}", fill=(255, 255, 0))
        im.save(SHEETS / f"{name}_{ds.ids[i]:04d}.png")


def write_results(scores, picked, training):
    L = []
    L.append("# System B results (learned grasp predictor)\n")
    L.append("Spec section 5.3, scored with the same section 6 metric and the same "
             "123 held-out test images as System A. Train (620) fit the models, val "
             "(140) selected them, test was opened once, here.\n")

    s = scores[picked]
    L.append("\n## Headline\n")
    L.append(f"**{picked} — {s['acc']:.1f}%** ({s['correct']}/{s['n']}) on the test split.\n")
    L.append(f"System A was {SYSTEM_A_ACC}%, so System B is "
             f"**+{s['acc'] - SYSTEM_A_ACC:.1f} points**.\n")

    L.append("\n## All three architectures\n")
    L.append("The headline is the model selected on **val**, not the one that scored "
             "best on test. Picking by test score would be leakage, so all three test "
             "numbers are shown and the selection rule is stated rather than implied.\n")
    L.append("| Model | Params | Best val acc | Test acc | Selected |")
    L.append("|---|---|---|---|---|")
    for m in MODELS:
        tr = next((t for t in training if t["model"] == m), None)
        v = f"{tr['best_val_acc']*100:.1f}%" if tr else "n/a"
        mark = "**yes**" if m == picked else ""
        p = f"{tr['params']/1e6:.1f}M" if tr else "n/a"
        L.append(f"| {m} | {p} | {v} | {scores[m]['acc']:.1f}% | {mark} |")

    L.append("\n## Against System A, on the axis that limited it\n")
    L.append("System A could only ever emit 0 or 90 degrees, because COCO boxes are "
             "axis-aligned. That put a hard floor under its angle error and accounted "
             f"for {SYSTEM_A_ANGLE_ONLY_FAILURES} of its {SYSTEM_A_TOTAL_FAILURES} "
             "failures. The sin/cos(2t) head removes that restriction entirely.\n")
    L.append("| | System A | System B |")
    L.append("|---|---|---|")
    L.append(f"| Test accuracy | {SYSTEM_A_ACC}% | **{s['acc']:.1f}%** |")
    L.append(f"| Orientations representable | 2 (0 and 90 deg) | continuous |")
    L.append(f"| Mean angle error | n/a (quantised) | {s['mean_angle_err']:.1f} deg |")
    L.append(f"| Failures on angle alone | {SYSTEM_A_ANGLE_ONLY_FAILURES}"
             f"/{SYSTEM_A_TOTAL_FAILURES} | {s['angle_only']}/{s['n']-s['correct']} |")
    L.append(f"| Failures on overlap alone | not measured | "
             f"{s['iou_only']}/{s['n']-s['correct']} |")

    L.append("\n## Failure cases\n")
    L.append("Closest miss first. `best IoU` and `angle err` are against whichever "
             "ground-truth grasp the prediction overlapped most.\n")
    L.append("| Image | Best IoU | Angle err | Missed on |")
    L.append("|---|---|---|---|")
    misses = [(i, r) for i, r in enumerate(s["records"]) if not r[2]]
    for i, (pred, gts, ok, iou, ang) in sorted(misses, key=lambda x: -x[1][3])[:8]:
        why = ("angle only" if iou > IOU_MIN else
               "overlap only" if ang <= ANGLE_TOL_DEG else "both")
        L.append(f"| index {i} | {iou:.2f} | {ang:.0f} deg | {why} |")

    L.append("\n## Method notes for the write-up\n")
    L.append("- Orientation is regressed as (cos 2t, sin 2t) on the unit circle. "
             "Direct theta regression would see a 178-degree error between two grasps "
             "2 degrees apart, because the metric treats orientation as 180-degree "
             "symmetric.\n")
    L.append("- The loss is assigned best-match: computed against every labelled grasp, "
             "only the minimum backpropagated. Measured on train, regressing to the "
             "average of each image's grasps is capped at 86.5% even with a perfect "
             "model, because the average of a handle grasp and a rim grasp lies between "
             "them where neither is valid. Best-match is capped at 100%.\n")
    L.append("- Only one hyperparameter was tuned (the size-loss weight), on val. The "
             "8-image overfit check preferred 3.0; val preferred 1.0 and val won.\n")
    L.append("- Augmentation transforms grasp rectangles by moving their four corners "
             "through the same affine as the pixels, then re-deriving the parameters, "
             "so no hand-written rule for how theta behaves under a flip can be "
             "backwards.\n")

    L.append("\n## Caveat: the val figures are optimistically biased\n")
    L.append("The val accuracies in the table above are each a MAXIMUM over ~50-120 "
             "epochs, and val accuracy is very noisy: on 140 images one image is worth "
             "0.71 points, and the measured mean epoch-to-epoch swing is 6.7 to 11.9 "
             "points, with single jumps as large as 49. Taking the best of that many "
             "noisy draws is upward biased by construction, so a val number is not an "
             "unbiased estimate of anything.\n")
    L.append("Val is still the right tool for its actual job, which is choosing between "
             "checkpoints and architectures. It is simply not a performance figure. "
             "**Only the test column may be compared against System A's 57.7%**, and "
             "only once, which is what this script does. Any 'System B beats System A "
             "by N points' claim made from a val number would be comparing a "
             "best-of-many-draws figure on one split against a single sealed "
             "measurement on another.\n")

    RESULTS_MD.write_text("\n".join(L) + "\n")


def main():
    ds = load_test()
    dev = device()
    training = json.loads(TRAINING_JSON.read_text())
    picked = max(training, key=lambda t: t["best_val_acc"])["model"]
    print(f"Architecture selected on VAL: {picked}\n")

    scores = {}
    for name in MODELS:
        ckpt = CKPT_DIR / f"{name}.pt"
        if not ckpt.exists():
            raise SystemExit(f"missing checkpoint {ckpt}; run system_b_train.py first")
        model = build(name).to(dev)
        model.load_state_dict(torch.load(ckpt, map_location=dev))
        s = score(predict(model, ds, dev))
        scores[name] = s
        mark = "  <- val-selected, headline" if name == picked else ""
        print(f"  {name:<10} test {s['acc']:5.1f}%  ({s['correct']}/{s['n']})  "
              f"mean angle err {s['mean_angle_err']:4.1f}deg{mark}")

    s = scores[picked]
    with open(PRED_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pcd_id", "cx", "cy", "theta", "opening", "jaw",
                    "best_iou", "angle_err", "correct"])
        for pcd, (pred, gts, ok, iou, ang) in zip(ds.ids, s["records"]):
            w.writerow([f"{pcd:04d}"] + [f"{v:.2f}" for v in pred]
                       + [f"{iou:.3f}", f"{ang:.1f}", int(ok)])

    write_results(scores, picked, training)
    draw_sheets(ds, s["records"], picked)

    print(f"\nHeadline: {picked} at {s['acc']:.1f}% vs System A at {SYSTEM_A_ACC}% "
          f"({s['acc'] - SYSTEM_A_ACC:+.1f} points)")
    print(f"Wrote {PRED_CSV}\nWrote {RESULTS_MD}\nWrote sheets to {SHEETS}")


if __name__ == "__main__":
    main()
