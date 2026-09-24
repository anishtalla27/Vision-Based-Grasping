"""System D's FROZEN prompt and parser (Set-of-Mark grasp selection).

Same discipline as system_c_prompt.py: developed on the same 30 fixed
TRAIN images, selected on parse rate only, frozen before test is
called, and versioned in place rather than overwritten. This module
imports nothing from the evaluation code.

WHAT IS DIFFERENT FROM SYSTEM C
-------------------------------
The model is never asked for a coordinate. It sees the object with a
numbered set of candidate grasps drawn on it (system_d_candidates.py)
and returns the number of the one it would use. Everything geometric
comes from the candidate, so the only thing being measured is whether
the model can pick a good grasp when it can SEE the options -- which is
exactly the capability System C's coordinate output was hypothesised
to be hiding.
"""

import json
import re

OK = "ok"
PARSE_FAIL = "parse_fail"      # no JSON object / no integer choice found
RANGE_FAIL = "range_fail"      # a number, but not one of the marks shown
API_FAIL = "api_fail"

SYSTEM_MSG = (
    "You are a robotic grasping assistant. You are shown a photograph of "
    "one object on a table, taken from a camera above it, with several "
    "candidate grasps drawn on the object as numbered coloured lines. You "
    "choose one candidate. You reply with a single JSON object and no "
    "other text."
)

PROMPT_V1 = """This photograph shows one object on a table, zoomed in. A two-fingered
parallel-jaw gripper will descend vertically and close on the object.

{k} candidate grasps are drawn on the image. Each candidate is a coloured
line with a small tick at each end and a numbered circle next to one
end. The line shows where the two fingertips would be placed: the
fingertips start at the two ends of the line and close along it toward
each other. So a candidate grasp closes ACROSS the part of the object
its line crosses.

Choose the candidate most likely to pick the object up and hold it:
usually one that closes across a narrow part of the object, near its
centre of mass, with both fingertips landing on the object rather than
on the table.

Reply with exactly one JSON object and nothing else:

{{
  "object": "<two or three words naming the object>",
  "reasoning": "<one sentence: which part of the object that candidate grasps, and why>",
  "choice": <the number of the chosen candidate, 1 to {k}>,
  "confidence": "<low|medium|high>"
}}"""

# V1 -> V2, recorded rather than overwritten. Dev batch (30 train images
# x 2 repeats, tag "dev"): 58/58 parsed, so parse rate did not motivate
# a change. What did was a CONVENTION check of the kind system_c_dev.py
# was written to catch: in 34 of 58 replies the model chose the
# candidate whose line runs along the object's LONG axis (random would
# be ~25%) while its own reasoning said "closes across the narrowest
# part". That is the signature of reading the drawn line as the finger
# plates rather than as the closing direction, i.e. a rendering
# ambiguity, not a grasp choice. V2 changes the glyph (thick fingertip
# pads plus inward arrowheads, see system_d_candidates.render) and the
# wording below to describe that glyph. Accuracy played no part: the
# V1 dev accuracy is recorded in system_d_dev_summary.json and was, for
# the record, at the random floor.
PROMPT_V2 = """This photograph shows one object on a table, zoomed in. A two-fingered
parallel-jaw gripper will descend vertically and close on the object.

{k} candidate grasps are drawn on the image, each in its own colour with
a numbered circle beside it. Each candidate shows the gripper's two
fingertips as two short THICK bars. The thin line joining the two bars
is the direction the fingertips move: the arrowheads on that line point
inward, and the two fingertips slide toward each other along it until
they squeeze whatever lies between them. So a candidate grips the part
of the object that lies between its two thick bars.

Choose the candidate most likely to pick the object up and hold it:
usually one whose two bars sit on opposite sides of a narrow part of
the object, near its centre of mass, so that the fingertips squeeze the
object rather than closing on empty table.

Reply with exactly one JSON object and nothing else:

{{
  "object": "<two or three words naming the object>",
  "reasoning": "<one sentence: which part of the object lies between that candidate's two bars, and why it is a good grip>",
  "choice": <the number of the chosen candidate, 1 to {k}>,
  "confidence": "<low|medium|high>"
}}"""

# Used only for the "equal" menu (system_d_run.py): PROMPT_V2 plus one
# sentence saying the drawn length is not to scale. Nothing else changes.
import re as _re
PROMPT_V2_EQUAL = _re.sub(
    r"So a candidate grips the part\s+of the object that lies between its two thick bars\.",
    "All candidates are drawn at the same length, which is NOT to scale: a mark\n"
    "shows only where the grip is centred and the direction the fingertips close\n"
    "along. So a candidate grips the part of the object that the line between\n"
    "its two bars crosses, at the marked centre.",
    PROMPT_V2)
assert PROMPT_V2_EQUAL != PROMPT_V2

PROMPT = PROMPT_V2
PROMPT_VERSION = "v2"


def _balanced_span(text):
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


def parse_response(text, k):
    """Reply -> (outcome, meta). meta['choice'] is a 1-based mark number when OK."""
    if not text or not text.strip():
        return PARSE_FAIL, {"reason": "empty reply"}
    obj = None
    for cand in (text.strip(),
                 (re.search(r"```(?:json)?\s*(.*?)```", text, re.S | re.I) or [None, ""])[1],
                 _balanced_span(text)):
        if not cand:
            continue
        for attempt in (cand, re.sub(r",(\s*[}\]])", r"\1", cand)):
            try:
                o = json.loads(attempt)
            except (ValueError, TypeError):
                continue
            if isinstance(o, dict):
                obj = o
                break
        if obj is not None:
            break
    if obj is None or "choice" not in obj:
        return PARSE_FAIL, {"reason": "no JSON object with a choice field"}
    v = obj["choice"]
    if isinstance(v, str):
        m = re.search(r"-?\d+", v)
        v = int(m.group()) if m else None
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v is None:
        return PARSE_FAIL, {"reason": f"choice is not a number: {obj['choice']!r}"}
    v = int(v)
    meta = {"choice": v, "object": str(obj.get("object", ""))[:60],
            "reasoning": str(obj.get("reasoning", ""))[:300],
            "confidence": str(obj.get("confidence", "")).lower()[:10]}
    if not 1 <= v <= k:
        meta["reason"] = f"choice {v} not in 1..{k}"
        return RANGE_FAIL, meta
    return OK, meta
