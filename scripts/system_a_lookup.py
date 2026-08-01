"""System A's FIXED lookup table and bounding-box-to-grasp conversion.

=====================================================================
THIS TABLE IS FROZEN. DO NOT TUNE IT AGAINST EVALUATION RESULTS.
=====================================================================
Spec section 5.2 requires the table to be "defined once, before any
evaluation is run, and not adjusted afterward to improve scores". That
is the entire methodological point of System A: it is the honest
non-learned floor that Systems B and C are measured against, and a
table quietly nudged until the number looked better would make the
comparison worthless.

The rule is enforced structurally, not by good intentions:

  * The three numeric scalars come from system_a_calibrate.py, which
    reads the TRAIN split only and hard-asserts it never opens a val or
    test image. Using train data is the fair choice, since System B
    gets to train on exactly the same images.
  * This module imports nothing from the evaluation code, so it has no
    way to see a score even in principle.
  * It is committed in its own commit, before the first evaluation run.
    Git history is therefore the audit trail: if that commit predates
    the first results commit, the rule provably held.

WHAT IS A PRIORI VS WHAT IS CALIBRATED
--------------------------------------
The STRUCTURE (which category grasps where, the three region shapes,
the orientation rule, the clamps) is a priori, reasoned from how a
parallel-jaw gripper physically works. Only three scalars are measured
from training data, and they are global rather than per-category on
purpose: per-category numerics would be curve-fitting wearing a lookup
table's clothes.

THE ORIENTATION RULE, WRITTEN OUT BECAUSE IT IS EASY TO INVERT
--------------------------------------------------------------
theta is the direction the jaws TRAVEL (the p0->p1 opening edge, see
cornell_data). A parallel-jaw gripper should close across the object's
NARROW dimension, so:

    box wider than tall -> narrow dimension is vertical   -> theta = 90
    box taller than wide -> narrow dimension is horizontal -> theta =  0

Getting this backwards would still run perfectly happily while
destroying the 30-degree criterion, so verify_system_a.py asserts it.
Because COCO boxes are axis-aligned this only ever yields 0 or 90
degrees, which is a real and acknowledged limitation of System A.

AMENDMENT 1 (recorded, not hidden)
----------------------------------
The table was first frozen in commit 853de49 and evaluated in afcd99a,
scoring 40.7%. Visual inspection of the rendered test sheets then found
that the detector often boxes background clutter -- a cardboard box
across the room, a chair, at one point a sandal -- rather than the
object on the photography platform, because Cornell shoots its objects
in an ordinary room rather than against a backdrop. Measured on the
TRAIN split, this affects 33.8% of detections (88 of 260).

`detection_on_object` below rejects those. The rule comes from the
dataset's own protocol (one object, on the platform) and was quantified
on train, not chosen by watching a test score move. It was nonetheless
NOTICED via a test-split image, so it is recorded here as an explicit
amendment rather than folded in silently, and both the pre-amendment
and post-amendment results are reported. The 40.7% stands on the record
in commit afcd99a.

Because the guard changes which boxes are trustworthy, the three
scalars were recalibrated on train after adding it.
"""

import numpy as np

# ---------------------------------------------------------------------
# CALIBRATED ON THE TRAIN SPLIT ONLY -- see system_a_calibrate.py.
# Frozen on first commit of this file; re-derived once when amendment 1
# changed which boxes feed the calibration, and not touched since.
# ---------------------------------------------------------------------
OPENING_FRAC = 0.696      # gt opening / bbox narrow side, median over 1224 train grasps
JAW_PX = 27.2             # gt jaw plate width in px, median over 3710 train grasps
END_OFFSET_FRAC = 0.115   # gt centre offset from nearest bbox end, median over 79 train images

# A-priori physical clamps: a real gripper has finite jaw travel, so the
# predicted opening cannot be arbitrarily small or large. Not tuned.
MIN_OPEN_PX = 12.0
MAX_OPEN_PX = 100.0

# ---------------------------------------------------------------------
# Category -> (grasp region, force level).
#
# Regions:
#   CENTER  grasp across the middle of the box
#   UPPER   grasp near the top (bottle necks, vase rims)
#   END     grasp near the thinner end along the long axis (handles)
#
# Force levels are carried through for the spec section 6 SECONDARY
# output only. They are reported descriptively and are never scored as
# an accuracy, because the dataset contains no ground truth for force.
# ---------------------------------------------------------------------
TABLE = {
    "bottle":      ("UPPER",  "LOW"),
    "wine glass":  ("UPPER",  "LOW"),
    "vase":        ("UPPER",  "LOW"),

    "cup":         ("END",    "LOW"),      # the spec's "mug -> handle" example
    "fork":        ("END",    "MEDIUM"),
    "knife":       ("END",    "MEDIUM"),
    "spoon":       ("END",    "MEDIUM"),
    "scissors":    ("END",    "MEDIUM"),
    "toothbrush":  ("END",    "LOW"),
    "hair drier":  ("END",    "LOW"),

    "bowl":        ("CENTER", "LOW"),
    "banana":      ("CENTER", "LOW"),
    "apple":       ("CENTER", "LOW"),
    "orange":      ("CENTER", "LOW"),
    "carrot":      ("CENTER", "LOW"),
    "broccoli":    ("CENTER", "LOW"),
    "teddy bear":  ("CENTER", "LOW"),

    "cell phone":  ("CENTER", "MEDIUM"),
    "remote":      ("CENTER", "MEDIUM"),
    "mouse":       ("CENTER", "MEDIUM"),
    "keyboard":    ("CENTER", "MEDIUM"),
    "book":        ("CENTER", "MEDIUM"),
    "clock":       ("CENTER", "MEDIUM"),
    "sports ball": ("CENTER", "MEDIUM"),
    "frisbee":     ("CENTER", "MEDIUM"),
    "tie":         ("CENTER", "MEDIUM"),
    "handbag":     ("CENTER", "MEDIUM"),
    "backpack":    ("CENTER", "MEDIUM"),
    "umbrella":    ("CENTER", "MEDIUM"),
}

# Used when the detector finds nothing, or finds a class not in TABLE.
#
# This fall-through carries more weight than expected. COCO does not just
# miss Cornell's objects, it confidently mislabels them: of 409 detections
# it reported 94 "laptop", 36 "kite", 18 "snowboard", 9 "skis", and one
# "refrigerator", so 171 of 409 land here rather than on a table entry.
#
# Those categories were deliberately NOT added to TABLE. Every one of them
# would map to CENTER anyway, which is what DEFAULT already returns, so
# adding them would change exactly one detection out of 409 (a lone
# "baseball bat"). Adding categories chosen by looking at which errors
# this particular dataset happens to produce would be fitting to the data
# for no measurable gain, which is the trade the spec warns against.
DEFAULT = ("CENTER", "MEDIUM")


def lookup(category):
    """Return (region, force) for a COCO category name; DEFAULT if unlisted."""
    return TABLE.get(category, DEFAULT)


def detection_on_object(bbox, mask):
    """Amendment 1: is this detection actually on the object being grasped?

    Cornell photographs one object on a bright platform, in a normal
    room, so the detector regularly reports something real but
    irrelevant elsewhere in the frame. A box that does not contain the
    segmented object's centroid is looking at the room, not the object.

    Returns True when there is no mask to check against: with no
    evidence either way, the detection is left alone rather than
    discarded on a guess.
    """
    if mask is None:
        return True
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return True
    cx, cy = xs.mean() * 2.0, ys.mean() * 2.0      # 320x240 -> 640x480
    x1, y1, x2, y2 = bbox
    return x1 <= cx <= x2 and y1 <= cy <= y2


def thinner_end(mask, bbox, horizontal):
    """Which half of the bounding box holds less object: 0 = low side, 1 = high side.

    A handle is the thin part of a handled object, so the end with fewer
    object pixels is the one to grasp. Returns None when there is no
    mask to measure, which makes the caller fall back to CENTER rather
    than guess a direction.

    `mask` is the half-resolution segmentation from the object-grouping
    script, so bbox coordinates are halved to match it.
    """
    if mask is None:
        return None
    x1, y1, x2, y2 = (v / 2.0 for v in bbox)       # 640x480 -> 320x240
    h, w = mask.shape
    xs = slice(max(0, int(x1)), min(w, int(np.ceil(x2))))
    ys = slice(max(0, int(y1)), min(h, int(np.ceil(y2))))
    sub = mask[ys, xs]
    if sub.size == 0 or not sub.any():
        return None

    half = (sub.shape[1] if horizontal else sub.shape[0]) // 2
    if half == 0:
        return None
    lo = sub[:, :half].sum() if horizontal else sub[:half, :].sum()
    hi = sub[:, half:].sum() if horizontal else sub[half:, :].sum()
    return 0 if lo < hi else 1


def predict_rect(bbox, region, mask=None):
    """Convert a detection box plus a qualitative region into a grasp rectangle.

    Returns (cx, cy, theta, opening, jaw) in full-resolution pixels, the
    same representation the metric scores ground truth in.
    """
    if OPENING_FRAC is None or JAW_PX is None or END_OFFSET_FRAC is None:
        raise SystemExit(
            "System A constants are unset. Run scripts/system_a_calibrate.py "
            "and paste its three values into system_a_lookup.py first."
        )

    x1, y1, x2, y2 = bbox
    bw, bh = x2 - x1, y2 - y1
    horizontal = bw >= bh                      # is the LONG axis horizontal?

    # Jaws close across the narrow dimension (see module docstring).
    theta = 90.0 if horizontal else 0.0

    opening = float(np.clip(OPENING_FRAC * min(bw, bh), MIN_OPEN_PX, MAX_OPEN_PX))
    cx, cy = x1 + bw / 2.0, y1 + bh / 2.0

    if region == "UPPER":
        cy = y1 + END_OFFSET_FRAC * bh
    elif region == "END":
        end = thinner_end(mask, bbox, horizontal)
        if end is not None:
            if horizontal:
                cx = x1 + END_OFFSET_FRAC * bw if end == 0 else x2 - END_OFFSET_FRAC * bw
            else:
                cy = y1 + END_OFFSET_FRAC * bh if end == 0 else y2 - END_OFFSET_FRAC * bh
        # else: no mask, so fall through to the CENTER anchor already set

    return (cx, cy, theta, opening, JAW_PX)
