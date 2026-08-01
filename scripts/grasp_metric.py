"""The spec section 6 grasp accuracy metric, shared by systems A, B and C.

WHAT THE METRIC IS
------------------
A predicted grasp counts as correct if, against at least one positive
ground-truth rectangle for that image:

    1. the angle difference is at most 30 degrees, AND
    2. the Jaccard index (IoU) of the two rectangles exceeds 25%

This is the standard metric from Lenz/Lee/Saxena and is what published
Cornell numbers are quoted against, so results here stay comparable to
the literature.

"AT LEAST ONE" IS DELIBERATE
----------------------------
Cornell labels several valid grasps per image (a mug can be grasped by
the handle or across the rim, and both are correct). Scoring against
only the first labelled rectangle would punish a system for picking a
different genuinely-valid grasp. Matching any single positive rectangle
is the convention in the literature and the one used here.

WHY THE IOU IS COMPUTED THE HARD WAY
------------------------------------
Grasp rectangles are rotated, so an axis-aligned IoU is simply wrong,
and rasterising the overlap is both slow and approximate. Both
rectangles are convex, so Sutherland-Hodgman polygon clipping gives the
intersection area exactly in about thirty lines and with no new
dependency. `verify_grasp_metric.py` checks this implementation against
a brute-force rasterised IoU on random rotated pairs, because a subtly
wrong metric would corrupt all three systems' numbers at once while
still appearing to run fine.

Angles wrap at 180 degrees, not 360: a parallel-jaw grasp rotated by
180 degrees is the same physical grasp.
"""

import numpy as np

from cornell_data import rect_to_corners

ANGLE_TOL_DEG = 30.0
IOU_MIN = 0.25


def angle_diff(a, b):
    """Smallest angle between two grasp orientations, in degrees (0-90).

    Folds at 180 degrees because a grasp and the same grasp flipped
    end-for-end are identical.
    """
    d = abs(a - b) % 180.0
    return min(d, 180.0 - d)


def _ccw(poly):
    """Return the polygon wound counter-clockwise (positive shoelace area)."""
    x, y = poly[:, 0], poly[:, 1]
    area2 = np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))
    return poly if area2 >= 0 else poly[::-1]


def polygon_area(poly):
    """Shoelace area of a simple polygon."""
    if len(poly) < 3:
        return 0.0
    x, y = poly[:, 0], poly[:, 1]
    return abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2.0


def clip_polygon(subject, clip):
    """Sutherland-Hodgman: intersect two CONVEX polygons.

    Walks each edge of `clip` and keeps the part of `subject` on its
    inner side, so the result is the intersection. Only valid because
    both inputs are convex, which rectangles always are.
    """
    out = _ccw(np.asarray(subject, dtype=float))
    clip = _ccw(np.asarray(clip, dtype=float))

    for i in range(len(clip)):
        if len(out) == 0:
            return np.empty((0, 2))
        a, b = clip[i], clip[(i + 1) % len(clip)]
        edge = b - a
        # Positive cross product means the point is on the inner
        # (left-hand) side of this edge, given CCW winding. Written out
        # by hand because numpy 2.x removed np.cross for 2-D vectors.
        rel = out - a
        side = edge[0] * rel[:, 1] - edge[1] * rel[:, 0]

        nxt = []
        for j in range(len(out)):
            k = (j + 1) % len(out)
            if side[j] >= 0:
                nxt.append(out[j])
            if (side[j] >= 0) != (side[k] >= 0):
                # The edge crosses the clip line; add the crossing point.
                t = side[j] / (side[j] - side[k])
                nxt.append(out[j] + t * (out[k] - out[j]))
        out = np.array(nxt) if nxt else np.empty((0, 2))
    return out


def rect_iou(r1, r2):
    """Jaccard index of two rectangles given as (cx, cy, theta, opening, jaw)."""
    p1, p2 = rect_to_corners(*r1), rect_to_corners(*r2)
    inter = polygon_area(clip_polygon(p1, p2))
    union = polygon_area(p1) + polygon_area(p2) - inter
    return 0.0 if union <= 0 else inter / union


def is_correct(pred, gts):
    """True if `pred` satisfies both section 6 criteria against any ground truth.

    Returns (correct, best_index, best_iou, best_angle) describing the
    single best-overlapping ground truth REGARDLESS of whether it passed
    the angle test. That matters for failure analysis: a prediction that
    overlaps well but is rotated 60 degrees off is a different kind of
    failure from one that is simply in the wrong place, and reporting
    the best angle-passing IoU only would hide the distinction by
    reporting 0.0 for both.
    """
    best_i, best_iou, best_ang = -1, 0.0, 180.0
    correct = False
    for i, gt in enumerate(gts):
        iou = rect_iou(pred, gt)
        ang = angle_diff(pred[2], gt[2])
        if iou > best_iou:
            best_i, best_iou, best_ang = i, iou, ang
        if ang <= ANGLE_TOL_DEG and iou > IOU_MIN:
            correct = True
    return correct, best_i, best_iou, best_ang
