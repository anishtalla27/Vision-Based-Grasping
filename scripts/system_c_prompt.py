"""System C's FROZEN prompt, response schema, and output parser.

=====================================================================
THIS PROMPT AND PARSER ARE FROZEN. DO NOT TUNE THEM AGAINST TEST.
=====================================================================
The prompt is a hyperparameter. Reworded until the test number improves,
it becomes a 123-image training set and System C stops being a zero-shot
baseline. So the same discipline System A used for its lookup table
applies here:

  * Prompt wording is developed on a fixed 30-image subset of TRAIN
    (system_c_dev.py), selected on PARSE SUCCESS RATE and geometric
    sanity, never on grasp accuracy.
  * Every version tried is kept below as PROMPT_V1, PROMPT_V2, ... with
    PROMPT pointing at the one in force, so the iteration is visible in
    the file rather than rewritten over.
  * This module imports nothing from the evaluation code, so it cannot
    see a score even in principle.
  * It is committed in its own commit, before system_c_eval.py exists.
    Git history is the audit trail.

WHY THE MODEL IS ASKED FOR FINGER POSITIONS, NOT AN ANGLE
---------------------------------------------------------
This is the single most important decision in System C.

The obvious prompt asks for (cx, cy, theta, w, h) directly. That is a
trap. "theta" invites four independent convention disagreements --
degrees vs radians, clockwise vs counter-clockwise, measured from x-axis
vs y-axis, and y-up vs y-down (images are y-down, but cornell_data
measures theta y-up). Any one of them is a silent 90-degree error that
runs fine, scores as a failed grasp, and looks exactly like the model
being bad at grasping. There is no way to tell the two apart from the
accuracy number.

So the model is never asked about an angle at all. It is asked where the
two fingertips touch, which is the more natural physical question and
has no convention to get wrong, and theta is DERIVED from those points
by cornell_data.corners_to_rect -- literally the same function that
produced every ground-truth angle in this project. There is no second
derivation of theta anywhere in System C.

This mirrors System B's augmentation discipline: never hand-write a rule
for how theta transforms, move the corners and re-derive it.

WHAT COUNTS AS A PARSE FAILURE, AND WHY THE BOUNDS ARE GENEROUS
---------------------------------------------------------------
A malformed reply must never be silently scored as a wrong grasp -- that
would blame the model's grasping for what was a formatting problem. So
every call lands in exactly one labelled bucket (see OUTCOMES) and the
results report two accuracies side by side, the same way System A
reported "with fallback" next to "detector-only".

The geometric bounds below are deliberately WIDE. Their job is to catch
replies that are not interpretable as a rectangle at all -- a point off
the image (the model misunderstood the coordinate frame), or a
zero-area grasp (the metric would divide by nothing). Their job is NOT
to filter out bad grasps. A 200-pixel-wide grasp is implausible for a
real gripper but is a perfectly interpretable answer, and the section 6
metric is the right thing to judge it, not this file. Rejecting it here
would quietly remove the model's bad answers from the denominator and
flatter the score.
"""

import json
import re

import numpy as np

from cornell_data import IMG_H, IMG_W, corners_to_rect

# ---------------------------------------------------------------- outcomes

OK = "ok"
PARSE_FAIL = "parse_fail"        # no JSON object could be extracted at all
SCHEMA_FAIL = "schema_fail"      # JSON present, required field missing/non-numeric
RANGE_FAIL = "range_fail"        # parsed, but not interpretable as a rectangle
API_FAIL = "api_fail"            # the call never returned (set by the client)

OUTCOMES = (OK, PARSE_FAIL, SCHEMA_FAIL, RANGE_FAIL, API_FAIL)

# Interpretability bounds, not plausibility bounds. See module docstring.
MIN_OPEN_PX, MAX_OPEN_PX = 5.0, 300.0
MIN_JAW_PX, MAX_JAW_PX = 3.0, 150.0

REQUIRED = ("finger_a", "finger_b", "jaw_width_px")

# ---------------------------------------------------------------- the prompt

SYSTEM_MSG = (
    "You are a robotic grasping assistant. You are shown a photograph "
    "from a fixed camera mounted above a table, and you decide where a "
    "two-fingered parallel-jaw gripper should close on the object in the "
    "photograph. You reply with a single JSON object and no other text."
)

PROMPT_V1 = """This is a 640 x 480 RGB photograph of one object resting on a table,
taken from a fixed camera looking down at it. A two-fingered parallel-jaw
gripper will descend vertically and close on the object.

Decide where the two fingertips should make contact.

Coordinates are in pixels of this 640 x 480 image. x runs from 0 at the
left edge to 639 at the right edge. y runs from 0 at the top edge to 479
at the bottom edge. Report whole numbers.

Reply with exactly one JSON object and nothing else:

{
  "object": "<two or three words naming the object>",
  "reasoning": "<one sentence: which part of the object you are grasping, and why>",
  "finger_a": [x, y],
  "finger_b": [x, y],
  "jaw_width_px": <integer>,
  "force": "<low|medium|high>",
  "confidence": "<low|medium|high>"
}

Rules:
- finger_a and finger_b are the two points where the fingertips touch the
  object. The gripper closes along the line between them, so they must be
  on OPPOSITE sides of the part you are grasping. Do not put both points
  at the object's centre, and do not put both on the same side.
- The distance between finger_a and finger_b is how far the jaws open. It
  must be wider than the part being grasped and no more than 150 pixels.
- jaw_width_px is how much of the object the flat face of one fingertip
  covers, measured perpendicular to the closing direction. Usually 15 to 40.
- Grasp the object itself. Do not place a fingertip on the table, on the
  background, or on the object's shadow.
- If more than one grasp would work, choose the one most likely to hold:
  across a narrow part of the object, close to its centre of mass."""

# The version in force. Any later version is added ABOVE this line as
# PROMPT_V2 etc and this pointer is moved, so nothing is overwritten.
PROMPT = PROMPT_V1
PROMPT_VERSION = "v1"

# Contamination probe (spec-adjacent, reported as an indicator not a test).
# Deliberately does not mention grasping, robotics, or Cornell, so a
# recognition is the model volunteering it rather than being led there.
PROBE_PROMPT = (
    "What dataset is this image from? If you recognise it, name the "
    "dataset and the paper or authors it comes from. If you do not "
    "recognise it, say so plainly. Answer in one or two sentences."
)

# ---------------------------------------------------------------- parsing


def _strip_trailing_commas(s):
    """Remove `,` immediately before a closing brace or bracket.

    Trailing commas are the single most common way an otherwise perfect
    JSON reply fails json.loads, and repairing one changes no value.
    """
    return re.sub(r",(\s*[}\]])", r"\1", s)


def _balanced_span(text):
    """Return the first balanced {...} span in `text`, or None.

    Tracks string state and escapes so a brace inside the "reasoning"
    string cannot end the span early.
    """
    start = text.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            c = text[i]
            if esc:
                esc = False
                continue
            if c == "\\" and in_str:
                esc = True
            elif c == '"':
                in_str = not in_str
            elif not in_str:
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        return text[start:i + 1]
        start = text.find("{", start + 1)
    return None


def extract_json(text):
    """Pull a JSON object out of a model reply. Returns a dict or None.

    Three attempts, cheapest first: the whole reply, a fenced ```json
    block, then the first balanced brace span. Each attempt is retried
    once with trailing commas stripped.
    """
    if not text or not text.strip():
        return None

    candidates = [text.strip()]
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S | re.I)
    if fenced:
        candidates.append(fenced.group(1).strip())
    span = _balanced_span(text)
    if span:
        candidates.append(span)

    for c in candidates:
        for attempt in (c, _strip_trailing_commas(c)):
            try:
                obj = json.loads(attempt)
            except (ValueError, TypeError):
                continue
            if isinstance(obj, dict):
                return obj
    return None


def _number(v):
    """Coerce a JSON value to float, or None if it is not a number.

    Numeric strings are accepted ("320" and 320 mean the same grasp, and
    quoting a number is a formatting quirk, not a grasping mistake). This
    leniency is decided here, before any test response has been seen.
    """
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v) if np.isfinite(v) else None
    if isinstance(v, str):
        try:
            f = float(v.strip())
        except ValueError:
            return None
        return f if np.isfinite(f) else None
    return None


def _point(v):
    """Coerce a JSON value to an (x, y) float pair, or None."""
    if isinstance(v, dict):
        v = [v.get("x"), v.get("y")]
    if not isinstance(v, (list, tuple)) or len(v) != 2:
        return None
    x, y = _number(v[0]), _number(v[1])
    if x is None or y is None:
        return None
    return (x, y)


def parse_response(text):
    """Model reply -> (outcome, payload).

    payload is a dict with keys a, b, jaw, object, reasoning, force,
    confidence when the outcome is OK, and carries whatever diagnostic
    detail is available otherwise. Never raises: a reply this cannot
    handle comes back as a labelled failure, because a crash here would
    take down a whole batch over one malformed string.
    """
    obj = extract_json(text)
    if obj is None:
        return PARSE_FAIL, {"reason": "no JSON object in reply"}

    missing = [k for k in REQUIRED if k not in obj]
    if missing:
        return SCHEMA_FAIL, {"reason": f"missing {', '.join(missing)}"}

    a, b = _point(obj["finger_a"]), _point(obj["finger_b"])
    jaw = _number(obj["jaw_width_px"])
    if a is None or b is None:
        return SCHEMA_FAIL, {"reason": "finger_a/finger_b are not [x, y] numbers"}
    if jaw is None:
        return SCHEMA_FAIL, {"reason": "jaw_width_px is not a number"}

    meta = {"a": a, "b": b, "jaw": jaw,
            "object": str(obj.get("object", ""))[:60],
            "reasoning": str(obj.get("reasoning", ""))[:300],
            "force": str(obj.get("force", "")).lower()[:10],
            "confidence": str(obj.get("confidence", "")).lower()[:10]}

    for name, (x, y) in (("finger_a", a), ("finger_b", b)):
        if not (0 <= x < IMG_W and 0 <= y < IMG_H):
            meta["reason"] = f"{name} ({x:.0f}, {y:.0f}) is outside the 640x480 image"
            return RANGE_FAIL, meta

    opening = float(np.hypot(b[0] - a[0], b[1] - a[1]))
    if not MIN_OPEN_PX <= opening <= MAX_OPEN_PX:
        meta["reason"] = f"opening {opening:.1f}px outside [{MIN_OPEN_PX}, {MAX_OPEN_PX}]"
        return RANGE_FAIL, meta
    if not MIN_JAW_PX <= jaw <= MAX_JAW_PX:
        meta["reason"] = f"jaw {jaw:.1f}px outside [{MIN_JAW_PX}, {MAX_JAW_PX}]"
        return RANGE_FAIL, meta

    return OK, meta


# ---------------------------------------------------------------- geometry


def response_to_rect(meta):
    """(finger_a, finger_b, jaw width) -> (cx, cy, theta, opening, jaw).

    The two contact points and the jaw width define four corners in the
    dataset's own p0->p1-is-the-opening-edge order, and corners_to_rect
    does the rest. theta is therefore produced by the same frozen
    function that produced every ground-truth angle, so there is no
    convention here to get backwards.
    """
    a, b = np.asarray(meta["a"], float), np.asarray(meta["b"], float)
    d = b - a
    n = float(np.hypot(d[0], d[1]))
    u = d / n                                   # along the opening edge
    perp = np.array([-u[1], u[0]])              # along the jaw edge
    half = meta["jaw"] / 2.0
    corners = np.array([a - perp * half, b - perp * half,
                        b + perp * half, a + perp * half])
    return corners_to_rect(corners)


def rect_to_response(rect):
    """Inverse of response_to_rect, used only by verify_system_c.py.

    Turns a known rectangle into the response that should encode it, so
    the round trip can be asserted exactly. Nothing in the live pipeline
    calls this -- it exists so that a sign error in the conversion above
    is caught by a test rather than by a disappointing accuracy.
    """
    from cornell_data import rect_to_corners
    c = rect_to_corners(*rect)
    return {"a": tuple((c[0] + c[3]) / 2.0), "b": tuple((c[1] + c[2]) / 2.0),
            "jaw": float(np.hypot(*(c[2] - c[1])))}
