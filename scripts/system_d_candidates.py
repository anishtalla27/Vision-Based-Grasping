"""System D: label-free grasp candidates for Set-of-Mark selection.

WHY THIS EXISTS
---------------
System C asked GPT-4o to EMIT grasp coordinates and scored 12.4%. The
paper's central hypothesis is that the model can often see where to
grasp but cannot bind that choice to pixel coordinates in its output.
The paper names the test it did not run: give the same model a set of
marked candidate grasps and ask it to CHOOSE one. If the choice beats
random selection among the same candidates, the model's perception is
doing work that the coordinate channel was throwing away. If it does
not, the problem is perception.

THE CANDIDATES MUST NOT SEE THE LABELS
--------------------------------------
Everything here is derived from the platform segmentation mask that the
object-wise split and System A already use (cornell_object_grouping
.segment), plus System A's three train-calibrated constants. No grasp
annotation is read. The ceiling of the candidate set ("oracle": does ANY
candidate pass the metric?) and its floor ("random": expected accuracy
of a uniformly random choice) are both reported, and System D's score
has to be read against those two, not against zero.

THE SET
-------
Principal-component analysis of the mask gives the object's centroid,
its long axis and its extent. Candidates are the product of

    3 positions      centroid, and +/- 0.35 of the long-axis extent
    4 orientations   jaws travelling along the SHORT axis, then +45,
                     +90, +135 degrees

which is 12 marks. Orientations 45 degrees apart mean every possible
grasp angle is within 22.5 degrees of some candidate, inside the
metric's 30-degree tolerance, so orientation is never the reason a set
has no passing member. Opening is OPENING_FRAC times the object's
extent along the jaw-travel direction, clamped to System A's physical
limits; jaw plate width is JAW_PX. Candidate 0 (centroid, close across
the short axis) doubles as a non-learned geometric rule that, unlike
System A, can express a diagonal grasp.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from cornell_data import corners_to_rect
from cornell_object_grouping import load as load_small
from cornell_object_grouping import segment
from system_a_lookup import JAW_PX, MAX_OPEN_PX, MIN_OPEN_PX, OPENING_FRAC

POSITION_FRACS = (0.0, -0.35, 0.35)
ORIENT_OFFSETS = (0.0, 45.0, 90.0, 135.0)
MASK_SCALE = 2.0            # segment() works on a 320x240 image

COLOURS = [(255, 60, 60), (60, 160, 255), (60, 220, 60), (255, 170, 0),
           (220, 60, 220), (0, 210, 210), (255, 255, 0), (255, 120, 160),
           (150, 90, 255), (120, 200, 120), (255, 200, 120), (200, 200, 200)]


def object_geometry(path):
    """Centroid, unit long-axis vector, extents (full-res px) from the mask, or None."""
    mask = segment(load_small(path))
    if mask is None:
        return None
    ys, xs = np.where(mask)
    pts = np.stack([xs, ys], 1).astype(float) * MASK_SCALE
    c = pts.mean(0)
    cov = np.cov((pts - c).T)
    w, v = np.linalg.eigh(cov)
    major = v[:, np.argmax(w)]
    if major[0] < 0:
        major = -major
    proj = (pts - c) @ major
    return {"centre": c, "major": major, "pts": pts,
            "long_extent": float(proj.max() - proj.min())}


def _extent_along(pts, c, direction):
    proj = (pts - c) @ direction
    return float(proj.max() - proj.min())


def _rect_from_fingers(a, b, jaw):
    """Two fingertip points + jaw width -> rect, via the same frozen path System C used."""
    d = b - a
    u = d / np.hypot(*d)
    perp = np.array([-u[1], u[0]])
    corners = np.array([a - perp * jaw / 2, b - perp * jaw / 2,
                        b + perp * jaw / 2, a + perp * jaw / 2])
    return corners_to_rect(corners)


MENUS = ("full", "sparse", "equal")


def candidates(path, menu="full"):
    """Return a list of dicts {rect, a, b, position, orient} or [] if no mask.

    menu = "full"    3 positions x 4 orientations, real openings (System D)
    menu = "sparse"  centroid only x 4 orientations, real openings
    menu = "equal"   same four candidates and the same scored geometry as
                     "sparse", but render() draws every mark at one uniform
                     length (UNIFORM_LEN) and the prompt says the length is
                     not to scale, so all four marks are the same size

    "sparse" and "equal" exist to test whether System D's preference for
    the long-axis candidate is a preference for the largest mark. Because
    all four candidates share the centroid, a mark carries only its
    direction, which a uniform-length glyph conveys faithfully.
    """
    g = object_geometry(path)
    if g is None:
        return []
    c, major, pts = g["centre"], g["major"], g["pts"]
    minor = np.array([-major[1], major[0]])       # short axis, image coords
    base = np.degrees(np.arctan2(minor[1], minor[0]))
    positions = POSITION_FRACS if menu == "full" else (0.0,)
    out = []
    for pf in positions:
        centre = c + major * pf * g["long_extent"]
        for off in ORIENT_OFFSETS:
            t = np.radians(base + off)
            u = np.array([np.cos(t), np.sin(t)])      # jaw travel direction
            opening = float(np.clip(OPENING_FRAC * _extent_along(pts, c, u),
                                    MIN_OPEN_PX, MAX_OPEN_PX))
            a, b = centre - u * opening / 2, centre + u * opening / 2
            out.append({"rect": _rect_from_fingers(a, b, JAW_PX), "a": a, "b": b,
                        "position": pf, "orient": off})
    return out


ZOOM_OUT = 600            # rendered crop is ZOOM_OUT x ZOOM_OUT pixels
UNIFORM_LEN = 80          # drawn mark length, in crop pixels, for the 'equal' menu
ZOOM_MARGIN = 0.6         # half-size of crop = ZOOM_MARGIN * mark spread + 30px


def crop_box(cands):
    """Square crop around the candidates, clipped to the image, in full-res px."""
    pts = np.array([p for c in cands for p in (c["a"], c["b"])])
    centre = pts.mean(0)
    half = max(ZOOM_MARGIN * (pts.max(0) - pts.min(0)).max() + 30, 90)
    x0, y0 = max(0.0, centre[0] - half), max(0.0, centre[1] - half)
    x1, y1 = min(640.0, centre[0] + half), min(480.0, centre[1] + half)
    return x0, y0, x1, y1


def render(path, cands, order, out_path, uniform=False):
    """Draw numbered marks on a zoomed crop. `order[i]` is shown as number i+1.

    Each candidate is drawn as the line the two fingertips close along,
    with ticks at the fingertips and a numbered badge beyond the a-end.
    The crop is zoomed so marks on small objects stay legible; the model
    never outputs a coordinate, so the zoom cannot leak into scoring.
    Numbering is permuted per call (system_d_run.py), so the same
    physical candidate carries a different number on every repeat.
    """
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = crop_box(cands)
    scale = ZOOM_OUT / max(x1 - x0, y1 - y0)
    im = im.crop((int(x0), int(y0), int(round(x1)), int(round(y1)))).resize(
        (int(round((x1 - x0) * scale)), int(round((y1 - y0) * scale))), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17)
    except OSError:
        font = ImageFont.load_default()

    def S(p):
        return ((p[0] - x0) * scale, (p[1] - y0) * scale)

    for label, ci in enumerate(order, start=1):
        cnd = cands[ci]
        col = COLOURS[ci % len(COLOURS)]
        a, b = np.array(S(cnd["a"])), np.array(S(cnd["b"]))
        u = (b - a) / np.hypot(*(b - a))
        if uniform:
            # 'equal' menu: same centre and direction, one drawn length for
            # every mark, so mark size cannot act as a cue.
            m = (a + b) / 2
            a, b = m - u * UNIFORM_LEN / 2, m + u * UNIFORM_LEN / 2
        p = np.array([-u[1], u[0]])
        # RENDER V2. V1 drew a thin line with small end ticks, and the
        # model read the line as the finger plates (it chose long-axis
        # lines while describing a grasp "across the narrowest part").
        # V2 draws each fingertip as a thick pad perpendicular to the
        # closing direction, with an arrowhead pointing inward along the
        # thin line between the pads, so the closing direction is drawn
        # explicitly rather than implied.
        d.line([tuple(a), tuple(b)], fill=col, width=2)
        for e, inward in ((a, u), (b, -u)):
            d.line([tuple(e - p * 9), tuple(e + p * 9)], fill=col, width=6)
            tip = e + inward * 12
            d.polygon([tuple(tip), tuple(e + inward * 3 + p * 5),
                       tuple(e + inward * 3 - p * 5)], fill=col)
        bc = (a - u * 18) if (ci % 2 == 0) else (b + u * 18)
        r = 11
        d.ellipse([bc[0] - r, bc[1] - r, bc[0] + r, bc[1] + r], fill=col, outline=(0, 0, 0))
        tw = d.textlength(str(label), font=font)
        d.text((bc[0] - tw / 2, bc[1] - 10), str(label), fill=(0, 0, 0), font=font)
    im.save(out_path)
