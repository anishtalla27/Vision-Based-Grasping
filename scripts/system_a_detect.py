"""System A, step 1: run a COCO-pretrained detector over the dataset.

WHY THIS IS A SEPARATE SCRIPT
-----------------------------
The plan had detection inside the lookup module, but there is an
ordering dependency: calibrating the lookup table's constants needs
bounding boxes on the TRAIN images, so detection has to happen before
the table can be frozen. Keeping detection here, with its own a-priori
configuration, means the frozen table never has to be touched again
after calibration.

Nothing in this file looks at a grasp label, so running it over the
whole dataset (test included) leaks nothing: it is plain inference,
exactly what System A would do at deployment time. Only the ground
truth is split-sensitive, and that lives in the calibration script.

THE SELECTION RULES ARE A PRIORI
--------------------------------
All four constants below were fixed by reasoning about the images, not
by looking at any accuracy number:

  * SCORE_MIN 0.5 is the conventional detection threshold.
  * The scene blocklist exists because Cornell photographs objects on a
    platform in a real room, so the detector cheerfully reports the
    table, the chair, and occasionally the photographer. Those are the
    scene, not the object to be grasped.
  * MAX_BOX_FRAC rejects boxes covering most of the frame, which are
    the room rather than the object.
  * Highest-scoring survivor wins; Cornell images contain one object.

Usage:
    python scripts/system_a_detect.py

Outputs:
    data/interim/system_a_detections.csv
"""

import csv

import torch
from PIL import Image
from torchvision.models import detection
from torchvision.transforms import functional as TF

from cornell_data import INTERIM, IMG_H, IMG_W, find_images, load_split

OUT_CSV = INTERIM / "system_a_detections.csv"

SCORE_MIN = 0.5
MAX_BOX_FRAC = 0.6
SCENE_CLASSES = {"dining table", "chair", "couch", "bed", "tv", "person"}

FRAME_AREA = IMG_W * IMG_H


def pick_device():
    """MPS if it works, else CPU. Detection is inference-only, so either is fine."""
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def best_detection(pred, labels):
    """Apply the a-priori selection rules; return (category, score, box) or None.

    Detections arrive sorted by score, so the first survivor is the
    highest-scoring one.
    """
    for score, label, box in zip(pred["scores"], pred["labels"], pred["boxes"]):
        s = float(score)
        if s < SCORE_MIN:
            break                                   # sorted: nothing later qualifies
        name = labels[int(label)]
        if name in SCENE_CLASSES:
            continue
        x1, y1, x2, y2 = (float(v) for v in box)
        if (x2 - x1) * (y2 - y1) > MAX_BOX_FRAC * FRAME_AREA:
            continue
        return name, s, (x1, y1, x2, y2)
    return None


def main():
    split = load_split()
    paths = find_images()
    ids = sorted(split)                             # the 883 in-play images
    print(f"Detecting over {len(ids)} images (all splits; inference only, no labels read)")

    device = pick_device()
    weights = detection.FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
    labels = weights.meta["categories"]
    model = detection.fasterrcnn_resnet50_fpn_v2(weights=weights).eval().to(device)
    print(f"Model: fasterrcnn_resnet50_fpn_v2 (COCO), device={device.type}")

    rows, n_hit = [], 0
    with torch.inference_mode():
        for i, pcd in enumerate(ids):
            img = TF.to_tensor(Image.open(paths[pcd]).convert("RGB")).to(device)
            pred = model([img])[0]
            hit = best_detection(pred, labels)
            if hit is None:
                rows.append([f"{pcd:04d}", "", "", "", "", "", ""])
            else:
                name, s, (x1, y1, x2, y2) = hit
                n_hit += 1
                rows.append([f"{pcd:04d}", name, f"{s:.4f}",
                             f"{x1:.1f}", f"{y1:.1f}", f"{x2:.1f}", f"{y2:.1f}"])
            if (i + 1) % 100 == 0:
                print(f"  {i+1}/{len(ids)}  detected so far: {n_hit}")

    INTERIM.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pcd_id", "category", "score", "x1", "y1", "x2", "y2"])
        w.writerows(rows)

    print(f"\nDetector coverage: {n_hit}/{len(ids)} ({n_hit/len(ids)*100:.1f}%)")
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
