"""Shared loading helpers for the Cornell Grasping Dataset.

WHY THIS EXISTS
---------------
Systems A, B and C (spec sections 5.2-5.4) all need the same three
things: the image for a pcd id, that image's ground-truth grasp
rectangles, and which split the image belongs to. Writing that parsing
three times is how the three systems end up quietly disagreeing about
what a grasp rectangle is, which would make the section 6 comparison
meaningless. So it lives here once.

THE RECTANGLE CONVENTION
------------------------
Cornell stores each rectangle as four corner lines "x y", in order
around the rectangle. Which edge means what is not documented in the
mirror we have, so it was measured rather than assumed: over 552 parsed
rectangles the p0->p1 edge has median length 33.8px and the p1->p2 edge
23.7px, and p0->p1 is the longer edge in 85% of rectangles. That matches
the standard reading used in the grasping literature:

    p0 -> p1   the gripper OPENING (how far the jaws are apart)
    p1 -> p2   the jaw PLATE WIDTH (how wide each finger is)

so the grasp angle is the direction of the p0->p1 edge. We carry
rectangles around as (cx, cy, theta, opening, jaw):

    cx, cy    centre in full-resolution pixels (images are 640x480)
    theta     degrees in [-90, 90), counter-clockwise, y-up convention
    opening   length of the p0->p1 edge, pixels
    jaw       length of the p1->p2 edge, pixels

theta wraps at 180 degrees rather than 360 because a parallel-jaw grasp
rotated by 180 degrees is the same physical grasp.

QUIRKS THIS HANDLES
-------------------
  * Some corner lines have trailing whitespace, so parsing splits on
    whitespace rather than assuming a fixed layout.
  * pcd0165cpos.txt contains "NaN NaN" corners (the only such file in
    the dataset). That one rectangle is dropped; the other two in the
    file are still valid and are kept.
  * Two images (0435, 0782) are deliberately absent from the finalised
    split, per spec section 10.3. load_split() therefore returns 883
    entries, not 885, and is the authority on which images are in play.
"""

import csv
import re
from pathlib import Path

import numpy as np

RAW_DIR = Path("data/raw/cornell_grasp")
INTERIM = Path("data/interim")
SPLIT_CSV = INTERIM / "final_split.csv"

IMG_W, IMG_H = 640, 480


def find_images():
    """Return {pcd_id: path} for every RGB image in the raw dataset.

    Note this is all 885 raw images, including the two that the
    finalised split excludes. Use load_split() to get the 883 that are
    actually in play.
    """
    out = {}
    for p in RAW_DIR.glob("*/pcd[0-9][0-9][0-9][0-9]r.png"):
        out[int(re.match(r"pcd(\d{4})r\.png", p.name).group(1))] = p
    return out


def load_split():
    """Return {pcd_id: (object_id, split)} from the finalised object-wise split.

    This file is frozen per spec section 10.4 and is never regenerated
    here; it is read only.
    """
    out = {}
    with open(SPLIT_CSV, newline="") as f:
        for row in csv.DictReader(f):
            out[int(row["pcd_id"])] = (int(row["object_id"]), row["split"])
    return out


def split_ids(split):
    """Return sorted pcd ids belonging to one split ('train'/'val'/'test')."""
    return sorted(k for k, (_, s) in load_split().items() if s == split)


def rect_file(pcd_id, kind="cpos"):
    """Path to the cpos/cneg annotation file for a pcd id."""
    return RAW_DIR / f"{pcd_id // 100:02d}" / f"pcd{pcd_id:04d}{kind}.txt"


def corners_to_rect(c):
    """Convert 4 corner points to (cx, cy, theta, opening, jaw).

    See the module docstring for why p0->p1 is the opening edge. The
    y-negation converts image coordinates (y grows downward) into the
    y-up convention that makes theta read as a normal maths angle.
    """
    cx, cy = c[:, 0].mean(), c[:, 1].mean()
    dx, dy = c[1, 0] - c[0, 0], c[1, 1] - c[0, 1]
    theta = np.degrees(np.arctan2(-dy, dx))
    theta = (theta + 90) % 180 - 90          # fold into [-90, 90)
    opening = float(np.hypot(dx, dy))
    jaw = float(np.hypot(c[2, 0] - c[1, 0], c[2, 1] - c[1, 1]))
    return (float(cx), float(cy), float(theta), opening, jaw)


def load_rects(pcd_id, kind="cpos"):
    """Return [(cx, cy, theta, opening, jaw)] for one image.

    Rectangles containing NaN corners are silently dropped (see module
    docstring); everything else in the file is kept.
    """
    path = rect_file(pcd_id, kind)
    if not path.exists():
        return []
    nums = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) == 2:
            nums.append(parts)

    rects = []
    for i in range(0, len(nums) // 4 * 4, 4):
        try:
            c = np.array([[float(a), float(b)] for a, b in nums[i:i + 4]])
        except ValueError:
            continue
        if not np.isfinite(c).all():
            continue                          # the pcd0165 NaN rectangle
        rects.append(corners_to_rect(c))
    return rects


def rect_to_corners(cx, cy, theta, opening, jaw):
    """Inverse of corners_to_rect: (cx, cy, theta, opening, jaw) -> 4 corners.

    Used by the metric to turn any rectangle, predicted or ground truth,
    into a polygon it can intersect.
    """
    t = np.radians(theta)
    # Unit vector along the opening edge, back in image coordinates
    # (hence the negated sine, mirroring corners_to_rect).
    ux, uy = np.cos(t), -np.sin(t)
    vx, vy = -uy, ux                          # perpendicular: the jaw edge
    ho, hj = opening / 2, jaw / 2
    return np.array([
        [cx - ux * ho - vx * hj, cy - uy * ho - vy * hj],
        [cx + ux * ho - vx * hj, cy + uy * ho - vy * hj],
        [cx + ux * ho + vx * hj, cy + uy * ho + vy * hj],
        [cx - ux * ho + vx * hj, cy - uy * ho + vy * hj],
    ])
