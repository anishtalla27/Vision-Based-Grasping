"""System A, step 3: predict grasps on the test split and score them.

WHAT THIS DOES
--------------
For every test image: take the detector's box (or, when the detector
found nothing, fall back to the platform-geometry segmentation already
written and validated for the object-wise split), look the category up
in the FROZEN table, convert the box to a grasp rectangle, and score it
with the shared spec section 6 metric.

TWO ACCURACY NUMBERS ARE REPORTED, ON PURPOSE
---------------------------------------------
COCO's 80 classes do not cover most of what Cornell photographs
(staplers, sunglasses, combs, assorted household oddities). If System A
were scored only on images where the detector fired, the number would
mostly measure COCO's vocabulary rather than whether the grasp rule is
any good, and Systems B and C would be compared against a distorted
floor. So both are reported:

  detector-only   every image the detector missed counts as a failure.
                  The pure "detector plus lookup table" baseline.
  with fallback   detector misses fall back to segmentation geometry
                  and the DEFAULT table entry. The headline number.

Reporting both lets the paper separate "COCO does not know what a
stapler is" from "the grasp rule is wrong", which are different
findings with different implications for Systems B and C.

Grip force is reported as a DISTRIBUTION only, never as an accuracy.
Spec section 6 is explicit that the dataset contains no ground truth
for force, so any accuracy figure there would be invented.

Usage:
    python scripts/system_a_run.py     (after detect + calibrate + freeze)

Outputs:
    data/interim/system_a_predictions.csv
    data/interim/system_a_results.md
    data/interim/system_a_sheets/*.png
"""

import csv
from collections import Counter, defaultdict

import numpy as np
from PIL import Image, ImageDraw

from cornell_data import (INTERIM, find_images, load_rects, load_split,
                          rect_to_corners)
from cornell_object_grouping import load as load_small
from cornell_object_grouping import segment
from grasp_metric import ANGLE_TOL_DEG, IOU_MIN, is_correct
from system_a_calibrate import load_detections
from system_a_lookup import DEFAULT, lookup
from system_a_lookup import predict_rect

PRED_CSV = INTERIM / "system_a_predictions.csv"
RESULTS_MD = INTERIM / "system_a_results.md"
SHEETS = INTERIM / "system_a_sheets"

N_SHEETS = 12


def mask_bbox(mask):
    """Full-resolution bounding box of a half-resolution segmentation mask."""
    ys, xs = np.where(mask)
    return (float(xs.min() * 2), float(ys.min() * 2),
            float(xs.max() * 2), float(ys.max() * 2))


def predict_all(ids, paths, dets):
    """Predict a grasp rectangle for every id. Reads no grasp labels."""
    preds = {}
    for pcd in ids:
        mask = segment(load_small(paths[pcd]))

        if pcd in dets:
            category, score, bbox = dets[pcd]
            region, force = lookup(category)
            source = "detector"
        elif mask is not None:
            category, score, bbox = "", 0.0, mask_bbox(mask)
            region, force = DEFAULT
            source = "fallback"
        else:
            # Neither the detector nor the segmentation found anything.
            # There is nothing to guess from, so this is simply a miss.
            preds[pcd] = (None, "", 0.0, "", "", "none")
            continue

        rect = predict_rect(bbox, region, mask)
        preds[pcd] = (rect, category, score, region, force, source)
    return preds


def draw_sheets(ids, paths, preds, gts):
    """Render prediction (red) against ground truth (green) for eyeballing.

    Cheap insurance: if the orientation rule were inverted, every red
    rectangle would sit at right angles to the green ones and it would
    be obvious at a glance, where a percentage alone would not be.
    """
    SHEETS.mkdir(parents=True, exist_ok=True)
    for pcd in ids[:N_SHEETS]:
        rect = preds[pcd][0]
        img = Image.open(paths[pcd]).convert("RGB")
        d = ImageDraw.Draw(img)
        for gt in gts[pcd]:
            d.polygon([tuple(p) for p in rect_to_corners(*gt)], outline=(0, 220, 0))
        if rect is not None:
            d.polygon([tuple(p) for p in rect_to_corners(*rect)],
                      outline=(255, 40, 40), width=3)
        d.text((6, 6), f"pcd{pcd:04d}  green=ground truth  red=System A", fill=(255, 255, 0))
        img.save(SHEETS / f"system_a_{pcd:04d}.png")


def main():
    split = load_split()
    test = sorted(p for p, (_, s) in split.items() if s == "test")
    non_test = {p for p, (_, s) in split.items() if s != "test"}
    paths = find_images()
    dets = {k: v for k, v in load_detections().items() if k in set(test)}

    print(f"System A on {len(test)} test images "
          f"(train and val are untouched, and left for System B)")

    preds = predict_all(test, paths, dets)

    gts, opened = {}, set()
    for pcd in test:
        gts[pcd] = load_rects(pcd)
        opened.add(pcd)
    leaked = opened & non_test
    if leaked:
        raise SystemExit(f"SPLIT LEAK: scored against {len(leaked)} non-test images")
    print(f"Split hygiene OK: scored {len(opened)} images, all test, zero train/val.\n")

    rows, by_cat, forces, sources = [], defaultdict(list), Counter(), Counter()
    n_ok_fallback = n_ok_detector = 0
    misses = []

    for pcd in test:
        rect, category, score, region, force, source = preds[pcd]
        sources[source] += 1

        if rect is None:
            correct, best_iou, best_ang = False, 0.0, float("nan")
            rows.append([f"{pcd:04d}", "", "", "", "", "", "", "", "none", "0"])
        else:
            correct, _, best_iou, best_ang = is_correct(rect, gts[pcd])
            forces[force] += 1
            rows.append([f"{pcd:04d}", f"{rect[0]:.1f}", f"{rect[1]:.1f}",
                         f"{rect[2]:.1f}", f"{rect[3]:.1f}", f"{rect[4]:.1f}",
                         region, force, source, "1" if correct else "0"])

        n_ok_fallback += correct
        # The pure baseline gives no credit for anything the detector missed.
        if source == "detector":
            n_ok_detector += correct
        by_cat[category or "(no detection)"].append(correct)
        if not correct:
            misses.append((pcd, category or "(no detection)", source,
                           best_iou, best_ang))

    n = len(test)
    n_det = sources["detector"]
    acc_fb = n_ok_fallback / n * 100
    acc_det = n_ok_detector / n * 100
    acc_det_only = (n_ok_detector / n_det * 100) if n_det else 0.0

    with open(PRED_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pcd_id", "cx", "cy", "theta", "opening", "jaw",
                    "region", "force", "source", "correct"])
        w.writerows(rows)

    print(f"Detector coverage : {n_det}/{n} ({n_det/n*100:.1f}%)")
    print(f"  fallback used   : {sources['fallback']}")
    print(f"  no prediction   : {sources['none']}")
    print(f"\nAccuracy (angle <= {ANGLE_TOL_DEG:g} deg AND IoU > {IOU_MIN:g}):")
    print(f"  with fallback (headline) : {n_ok_fallback}/{n} = {acc_fb:.1f}%")
    print(f"  detector-only (pure)     : {n_ok_detector}/{n} = {acc_det:.1f}%")
    print(f"  among detected images    : {n_ok_detector}/{n_det} = {acc_det_only:.1f}%")

    write_results(n, n_det, sources, n_ok_fallback, n_ok_detector,
                  acc_fb, acc_det, acc_det_only, by_cat, forces, misses)
    draw_sheets(test, paths, preds, gts)
    print(f"\nWrote {PRED_CSV}\nWrote {RESULTS_MD}\nWrote {N_SHEETS} sheets to {SHEETS}")


def write_results(n, n_det, sources, n_ok_fb, n_ok_det, acc_fb, acc_det,
                  acc_det_only, by_cat, forces, misses):
    """Write the results file in the spec's plain, student-authored voice."""
    L = []
    L.append("# System A results (rule-based baseline)\n")
    L.append("Spec section 5.2, scored with the section 6 metric on the test split "
             f"only ({n} images, 35 objects). Train and val were not touched.\n")
    L.append("The lookup table and its three constants were frozen before this ran, "
             "and were not adjusted afterwards.\n")

    L.append("\n## Headline\n")
    L.append("| Measure | Value |")
    L.append("|---|---|")
    L.append(f"| Accuracy, with segmentation fallback | **{acc_fb:.1f}%** ({n_ok_fb}/{n}) |")
    L.append(f"| Accuracy, detector-only (misses count as failures) | {acc_det:.1f}% ({n_ok_det}/{n}) |")
    L.append(f"| Accuracy among images the detector fired on | {acc_det_only:.1f}% ({n_ok_det}/{n_det}) |")
    L.append(f"| Detector coverage | {n_det}/{n} ({n_det/n*100:.1f}%) |")
    L.append(f"| Fallback used | {sources['fallback']} images |")
    L.append(f"| No prediction possible | {sources['none']} images |")

    L.append("\nThe gap between the first two rows is the point of reporting both. "
             "COCO's 80 classes do not cover most of what Cornell photographs, so "
             "the detector-only number is largely a statement about the detector's "
             "vocabulary rather than about whether the grasp rule works.\n")

    L.append("\n## Accuracy by detected category\n")
    L.append("| Category | Images | Correct | Accuracy |")
    L.append("|---|---|---|---|")
    for cat, vals in sorted(by_cat.items(), key=lambda kv: -len(kv[1])):
        L.append(f"| {cat} | {len(vals)} | {sum(vals)} | {sum(vals)/len(vals)*100:.0f}% |")

    L.append("\n## Grip force recommendations (descriptive only)\n")
    L.append("Not scored. The dataset has no ground truth for grip force, so per "
             "spec section 6 this is reported as a distribution and nothing more.\n")
    L.append("| Force level | Images | Share |")
    L.append("|---|---|---|")
    tot = sum(forces.values()) or 1
    for f_, c in forces.most_common():
        L.append(f"| {f_} | {c} | {c/tot*100:.0f}% |")

    L.append("\n## Failure cases\n")
    L.append("Closest miss first, so these are the informative failures rather than "
             "the hopeless ones. `best IoU` and `angle err` are measured against "
             "whichever ground-truth rectangle the prediction overlapped most.\n")
    L.append("| Image | Category | Source | Best IoU | Angle err |")
    L.append("|---|---|---|---|---|")
    ranked = sorted(misses, key=lambda m: -m[3])[:8]
    for pcd, cat, src, iou, ang in ranked:
        a = "n/a" if np.isnan(ang) else f"{ang:.0f} deg"
        L.append(f"| pcd{pcd:04d} | {cat} | {src} | {iou:.2f} | {a} |")

    near = [m for m in misses if m[3] > IOU_MIN and not np.isnan(m[4])
            and m[4] > ANGLE_TOL_DEG]
    L.append(f"\n{len(near)} of the {len(misses)} failures had good enough overlap "
             f"(IoU > {IOU_MIN:g}) but failed on angle alone. That is the expected "
             "signature of this baseline: because COCO boxes are axis-aligned, the "
             "orientation rule can only ever output 0 or 90 degrees, so any object "
             "sitting diagonally is unreachable no matter how well the box is "
             "placed. Fixing that would require a rotated box or a learned "
             "orientation, which is exactly what System B is for.\n")

    RESULTS_MD.write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
