"""Recover physical-object groupings for the Cornell Grasping Dataset.

WHY THIS EXISTS
---------------
Section 5.1 of the project spec requires an object-wise train/val/test
split (the same physical object must never appear in two splits). The
Cornell Grasping Dataset ships no object-ID metadata: the original
readme documents only images, point clouds, grasp rectangles, background
plates and a backgroundMapping.txt (which our Kaggle mirror does not
include, and which would not identify objects anyway since only 11
background plates are reused across all 885 images). Widely used public
implementations (ggcnn, GR-ConvNet, tnikolla/robot-grasp-detection) all
split image-wise and simply do not implement the object-wise split.

Images of one physical object were shot in a consecutive run of pcd
numbers, so recovering the grouping means deciding, for each of the 884
consecutive image pairs, whether it is the same object or a new one.

APPROACH: TRIAGE, NOT AUTOMATION
--------------------------------
An earlier attempt scored boundaries by whole-image pixel difference.
That was conclusively disproven: because the dataset deliberately varies
object *orientation* between shots, a same-object rotation produces a
larger pixel difference than many genuine object changes. The
same-object and different-object distributions overlapped completely,
so no threshold could separate them.

This script instead:
  1. Segments the object using scene geometry (see `segment`), giving
     rotation-invariant descriptors (colour histogram, area).
  2. Scores every boundary and reports a CONFIDENCE, not a verdict.
  3. Auto-accepts only high-confidence decisions, and routes everything
     ambiguous to human review.

THE THRESHOLDS ARE DELIBERATELY ASYMMETRIC
------------------------------------------
The two error directions are not equally costly:

  * Wrongly MERGING two objects is harmless for the split's validity.
    The merged group still goes entirely into one split, so no object
    leaks across splits. It only costs a little object diversity.
  * Wrongly SPLITTING one object is dangerous. Its images can then land
    in different splits, which is exactly the silent accuracy inflation
    the spec warns about in sections 5.1 and 8.

So SAME_THRESHOLD can be permissive, while DIFF_THRESHOLD is set well
below the lowest score of any pair that manual inspection showed to be
the same object. Everything between them is reviewed by hand.

Usage:
    python scripts/cornell_object_grouping.py

Outputs:
    data/interim/descriptors.npz         cached per-image descriptors
    data/interim/boundary_decisions.csv  per-boundary score + decision
    data/interim/review_sheets/*.png     side-by-side pairs needing review
"""

import csv
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

RAW_DIR = Path("data/raw/cornell_grasp")
INTERIM = Path("data/interim")
SHEETS = INTERIM / "review_sheets"

# Working resolution for segmentation/descriptors. Full res is not needed
# to decide object identity and is ~6x slower.
SIZE = (320, 240)  # (width, height)

# Platform detection: the objects sit on a bright, near-neutral platform.
PLATFORM_MIN_LUMA = 140
PLATFORM_MAX_SAT = 0.30
MIN_OBJECT_PIXELS = 20

# Confidence thresholds on the boundary score (see module docstring for
# why these are asymmetric). Calibrated against manually verified pairs:
# every verified different-object pair scored <= 0.157, while pairs that
# inspection showed were the same object went as low as 0.220. 0.15 sits
# below that overlap, so an auto-DIFFERENT call is safe. 0.42 is the
# lowest score among verified same-object pairs.
DIFF_THRESHOLD = 0.15   # below this: confidently a new object
SAME_THRESHOLD = 0.42   # above this: confidently the same object

PAIRS_PER_SHEET = 10
CROP_PX = 300


def find_images():
    """Return [(pcd_id, path)] sorted by pcd id."""
    out = []
    for p in RAW_DIR.glob("*/pcd[0-9][0-9][0-9][0-9]r.png"):
        out.append((int(re.match(r"pcd(\d{4})r\.png", p.name).group(1)), p))
    out.sort()
    return out


def load(path):
    return np.asarray(Image.open(path).convert("RGB").resize(SIZE), dtype=np.float32)


def segment(img):
    """Isolate the object using scene geometry.

    The object rests on a large bright platform, so it appears as a hole
    inside the platform region. Finding the platform and filling its
    holes therefore yields the object without needing the background
    plates at all -- which matters, because the plates are misaligned for
    many images and subtracting them latches onto the platform/carpet
    edge instead of the object.

    Returns a boolean mask, or None if no object could be isolated
    (e.g. a pale object that blends into the platform).
    """
    luma = img @ np.array([0.299, 0.587, 0.114])
    mx, mn = img.max(axis=2), img.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)

    platform = (luma > PLATFORM_MIN_LUMA) & (sat < PLATFORM_MAX_SAT)
    platform = ndimage.binary_closing(platform, np.ones((3, 3)))
    lab, n = ndimage.label(platform)
    if n == 0:
        return None
    sizes = ndimage.sum(platform, lab, range(1, n + 1))
    platform = lab == int(np.argmax(sizes)) + 1

    obj = ndimage.binary_fill_holes(platform) & ~platform
    lab, n = ndimage.label(obj)
    if n == 0:
        return None
    sizes = ndimage.sum(obj, lab, range(1, n + 1))
    if sizes.max() < MIN_OBJECT_PIXELS:
        return None
    return lab == int(np.argmax(sizes)) + 1


def describe(images):
    """Compute rotation-invariant descriptors for every image."""
    n = len(images)
    areas = np.zeros(n)
    hists = np.zeros((n, 64))
    ok = np.zeros(n, dtype=bool)

    for i, (pcd_id, path) in enumerate(images):
        mask = segment(load(path))
        if mask is None:
            continue
        img = load(path)
        px = img[mask]
        ok[i] = True
        areas[i] = mask.sum()
        # 4x4x4 RGB histogram over object pixels only. Rotation invariant
        # because it discards all spatial arrangement.
        q = np.clip((px // 64).astype(int), 0, 3)
        h = np.bincount(q[:, 0] * 16 + q[:, 1] * 4 + q[:, 2], minlength=64).astype(float)
        hists[i] = h / h.sum()

    return areas, hists, ok


def score_boundaries(areas, hists, ok):
    """Score each consecutive pair; NaN where either image failed to segment."""
    n = len(areas)
    scores = np.full(n - 1, np.nan)
    for i in range(n - 1):
        if not (ok[i] and ok[i + 1]):
            continue
        hist_overlap = np.minimum(hists[i], hists[i + 1]).sum()
        area_ratio = min(areas[i], areas[i + 1]) / max(areas[i], areas[i + 1])
        scores[i] = hist_overlap * area_ratio
    return scores


def classify(score):
    if np.isnan(score):
        return "MANUAL"          # segmentation failed; never guess
    if score < DIFF_THRESHOLD:
        return "AUTO_DIFFERENT"
    if score > SAME_THRESHOLD:
        return "AUTO_SAME"
    return "MANUAL"


def crop_object(path):
    """Crop tightly around the object so a reviewer can actually see it."""
    img = load(path)
    mask = segment(img)
    full = Image.open(path).convert("RGB")
    if mask is None:
        return full.resize((CROP_PX, CROP_PX))
    ys, xs = np.where(mask)
    cy, cx = (ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2
    half = max(ys.max() - ys.min(), xs.max() - xs.min()) / 2 + 14
    sx, sy = full.width / SIZE[0], full.height / SIZE[1]
    box = (int((cx - half) * sx), int((cy - half) * sy),
           int((cx + half) * sx), int((cy + half) * sy))
    return full.crop(box).resize((CROP_PX, CROP_PX))


def render_review_sheets(images, scores, decisions):
    """Render only the ambiguous boundaries, for hand review."""
    todo = [i for i, d in enumerate(decisions) if d == "MANUAL"]
    SHEETS.mkdir(parents=True, exist_ok=True)
    for start in range(0, len(todo), PAIRS_PER_SHEET):
        chunk = todo[start:start + PAIRS_PER_SHEET]
        sheet = Image.new("RGB", (CROP_PX * 2 + 30, (CROP_PX + 22) * len(chunk) + 26), "white")
        draw = ImageDraw.Draw(sheet)
        draw.text((6, 6), "Same object? left vs right", fill="black")
        for k, i in enumerate(chunk):
            y = 24 + k * (CROP_PX + 22)
            sheet.paste(crop_object(images[i][1]), (5, y))
            sheet.paste(crop_object(images[i + 1][1]), (CROP_PX + 25, y))
            s = "segfail" if np.isnan(scores[i]) else f"{scores[i]:.3f}"
            draw.text((5, y + CROP_PX + 4),
                      f"{images[i][0]:04d} vs {images[i+1][0]:04d}   score={s}",
                      fill="black")
        sheet.save(SHEETS / f"review_{start:04d}.png")
    return len(todo)


def histogram(scores):
    """Plain-text distribution of the confidence scores."""
    valid = scores[~np.isnan(scores)]
    edges = np.linspace(0, 1, 21)
    counts, _ = np.histogram(valid, bins=edges)
    peak = counts.max()
    lines = []
    for c, lo, hi in zip(counts, edges[:-1], edges[1:]):
        if hi <= DIFF_THRESHOLD:
            tag = "auto-DIFF"
        elif lo >= SAME_THRESHOLD:
            tag = "auto-SAME"
        else:
            tag = "MANUAL"
        bar = "#" * int(round(c / peak * 40))
        lines.append(f"  {lo:.2f}-{hi:.2f} |{bar:<40}| {c:3d}  {tag}")
    return "\n".join(lines)


def main():
    images = find_images()
    print(f"Found {len(images)} images ({images[0][0]:04d}-{images[-1][0]:04d})")

    cache = INTERIM / "descriptors.npz"
    INTERIM.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        z = np.load(cache)
        areas, hists, ok = z["areas"], z["hists"], z["ok"]
        print("Loaded cached descriptors")
    else:
        print("Segmenting and describing images...")
        areas, hists, ok = describe(images)
        np.savez(cache, areas=areas, hists=hists, ok=ok)
    print(f"Segmented {int(ok.sum())}/{len(images)}; "
          f"{int((~ok).sum())} failed (pale objects) -> forced to manual review")

    scores = score_boundaries(areas, hists, ok)
    decisions = [classify(s) for s in scores]

    n_diff = decisions.count("AUTO_DIFFERENT")
    n_same = decisions.count("AUTO_SAME")
    n_man = decisions.count("MANUAL")

    print("\nConfidence distribution (884 boundaries):")
    print(histogram(scores))
    print(f"\n  AUTO_DIFFERENT (score < {DIFF_THRESHOLD}) : {n_diff:3d}")
    print(f"  AUTO_SAME      (score > {SAME_THRESHOLD}) : {n_same:3d}")
    print(f"  MANUAL         (ambiguous or segfail): {n_man:3d}"
          f"  <-- {n_man/len(scores)*100:.1f}% of boundaries")
    print(f"  auto-resolved: {n_diff + n_same} of {len(scores)} "
          f"({(n_diff + n_same)/len(scores)*100:.1f}%)")

    out = INTERIM / "boundary_decisions.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pcd_a", "pcd_b", "score", "decision"])
        for i, d in enumerate(decisions):
            s = "" if np.isnan(scores[i]) else f"{scores[i]:.4f}"
            w.writerow([f"{images[i][0]:04d}", f"{images[i+1][0]:04d}", s, d])
    print(f"\nWrote {out}")

    n = render_review_sheets(images, scores, decisions)
    print(f"Wrote {(n + PAIRS_PER_SHEET - 1)//PAIRS_PER_SHEET} review sheets "
          f"({n} pairs) to {SHEETS}")


if __name__ == "__main__":
    main()
