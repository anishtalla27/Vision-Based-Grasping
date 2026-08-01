"""System A, step 2: measure the three lookup-table scalars. TRAIN SPLIT ONLY.

WHY CALIBRATE AT ALL
--------------------
The alternative was picking the numbers by pure guesswork ("open to 60%
of the narrow side, seems reasonable"). That is immune to accusations
of tuning, but it makes System A an arbitrary strawman, and a baseline
nobody believes is not a useful comparison point for Systems B and C.

Measuring on the TRAIN split is the fair middle: System B trains on
exactly these 620 images, so letting the rule-based baseline see the
same images is a level playing field, not a favour. Test and val ground
truth are never opened here, and that is asserted rather than trusted.

WHAT IS MEASURED
----------------
Three global scalars, deliberately not per-category (per-category
numbers would be fitting a curve and calling it a lookup table):

  OPENING_FRAC     how wide to open, as a fraction of the box's narrow
                   side. Median over train grasps.
  JAW_PX           the jaw plate width in pixels. Median over train
                   grasps; it barely varies, being a property of the
                   annotators' gripper model rather than the object.
  END_OFFSET_FRAC  how far in from an end an "END" or "UPPER" grasp
                   sits, as a fraction of the box's long side.

END_OFFSET_FRAC is measured only over train images whose detected
category maps to END or UPPER in the frozen table, and takes the
MOST end-ward valid grasp per image before taking the median across
images. Both choices are deliberate and were fixed before any number
was computed: averaging over all categories would drag the value to
0.5 (most objects are grasped centrally), which would silently collapse
END and UPPER into CENTER and make the whole region distinction a
no-op that nothing downstream would flag.

Usage:
    python scripts/system_a_calibrate.py     (after system_a_detect.py)
"""

import csv

import numpy as np

from cornell_data import INTERIM, find_images, load_rects, load_split
from cornell_object_grouping import load as load_small
from cornell_object_grouping import segment
from system_a_lookup import detection_on_object, lookup

DETECTIONS = INTERIM / "system_a_detections.csv"


def load_detections():
    """Return {pcd_id: (category, score, (x1, y1, x2, y2))} for detected images."""
    out = {}
    with open(DETECTIONS, newline="") as f:
        for row in csv.DictReader(f):
            if not row["category"]:
                continue
            out[int(row["pcd_id"])] = (
                row["category"], float(row["score"]),
                tuple(float(row[k]) for k in ("x1", "y1", "x2", "y2")),
            )
    return out


def main():
    split = load_split()
    train = {p for p, (_, s) in split.items() if s == "train"}
    forbidden = {p for p, (_, s) in split.items() if s != "train"}
    print(f"Calibrating on {len(train)} train images. "
          f"{len(forbidden)} val/test images are off limits.")

    dets = load_detections()
    paths = find_images()
    opened = set()

    openings, jaws, offsets = [], [], []
    n_used = n_clutter = 0

    for pcd in sorted(train):
        rects = load_rects(pcd)
        opened.add(pcd)
        if not rects:
            continue

        # JAW_PX needs no bounding box, so every train image contributes.
        jaws.extend(r[4] for r in rects)

        if pcd not in dets:
            continue
        # Amendment 1: a box sitting on background clutter would poison
        # OPENING_FRAC, since the ratio would be measured against the
        # size of some unrelated object across the room.
        if not detection_on_object(dets[pcd][2], segment(load_small(paths[pcd]))):
            n_clutter += 1
            continue
        category, _, (x1, y1, x2, y2) = dets[pcd]
        bw, bh = x2 - x1, y2 - y1
        if bw <= 0 or bh <= 0:
            continue
        n_used += 1

        narrow = min(bw, bh)
        openings.extend(r[3] / narrow for r in rects)

        region, _force = lookup(category)
        if region in ("END", "UPPER"):
            horizontal = bw >= bh
            fracs = []
            for cx, cy, *_ in rects:
                # Position along the LONG axis, normalised to [0, 1],
                # then folded so 0 = at an end, 0.5 = dead centre.
                p = (cx - x1) / bw if horizontal else (cy - y1) / bh
                fracs.append(min(max(p, 0.0), 1.0))
            folded = [min(p, 1 - p) for p in fracs]
            offsets.append(min(folded))          # most end-ward valid grasp

    # The split-hygiene guarantee, checked rather than asserted in prose.
    leaked = opened & forbidden
    if leaked:
        raise SystemExit(f"SPLIT LEAK: opened {len(leaked)} non-train images: "
                         f"{sorted(leaked)[:10]}")
    print(f"Split hygiene OK: opened {len(opened)} images, all train, zero val/test.\n")

    print(f"  detections rejected as clutter : {n_clutter} (amendment 1)")
    print(f"  train images with a usable box : {n_used}/{len(train)}")
    print(f"  grasp rectangles used          : {len(jaws)}")
    print(f"  END/UPPER images for offset    : {len(offsets)}")

    opening_frac = float(np.median(openings))
    jaw_px = float(np.median(jaws))
    end_offset = float(np.median(offsets)) if offsets else float("nan")

    print("\nPaste these into system_a_lookup.py, then commit that file alone:")
    print(f"  OPENING_FRAC = {opening_frac:.3f}")
    print(f"  JAW_PX = {jaw_px:.1f}")
    print(f"  END_OFFSET_FRAC = {end_offset:.3f}")

    print("\nSpread (for the methods section, not for tuning):")
    for name, vals in (("opening/narrow", openings), ("jaw px", jaws),
                       ("end offset", offsets)):
        v = np.asarray(vals, dtype=float)
        if v.size:
            print(f"  {name:<15} n={v.size:<5d} "
                  f"p25={np.percentile(v, 25):.3f} "
                  f"median={np.median(v):.3f} p75={np.percentile(v, 75):.3f}")


if __name__ == "__main__":
    main()
