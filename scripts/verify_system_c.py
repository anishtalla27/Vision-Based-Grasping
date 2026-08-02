"""Checks on System C's conversion and parsing, before any API call is made.

WHY THIS EXISTS
---------------
System C has one failure mode that would be invisible in its own
results: if the contact-point-to-rectangle conversion has a sign error,
every predicted grasp comes out rotated or mirrored, the pipeline runs
perfectly, and the output is a low accuracy that reads as "GPT-4o is bad
at grasping". Nothing about that number says the geometry was broken.
The same is true of a parser that quietly drops a valid reply.

So both are asserted against known answers here, offline, before a
single call is paid for. Every check runs with no API key set.

Usage:
    python scripts/verify_system_c.py
"""

import subprocess
import tempfile
from pathlib import Path

import numpy as np

from cornell_data import load_rects, split_ids
from grasp_metric import is_correct, rect_iou
from system_c_consistency import (abstention_curve, consensus_index,
                                  outcome_histogram, pairwise_angle_spread,
                                  self_agreement)
from system_c_prompt import (OK, PARSE_FAIL, RANGE_FAIL, SCHEMA_FAIL,
                             extract_json, parse_response, rect_to_response,
                             response_to_rect)

FROZEN_AT = "026032d"        # the commit that froze cornell_data + grasp_metric

FAILURES = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  ' + detail if detail else ''}")
    if not ok:
        FAILURES.append(name)


# ------------------------------------------------------- 1. the round trip


def test_roundtrip():
    """A known rectangle, encoded as a reply and decoded, must come back exactly.

    This is the check that catches a sign or axis error in the
    contact-point conversion. Real train rectangles are used rather than
    synthetic ones so the angles exercised are the ones the dataset
    actually contains, including the negative ones.
    """
    print("\n1. Contact points -> rectangle round trip")
    rects = []
    for pcd in split_ids("train")[:80]:
        rects.extend(load_rects(pcd))
    check("train rectangles available to test against", len(rects) > 200,
          f"n={len(rects)}")

    worst_param, worst_iou = 0.0, 1.0
    for r in rects:
        back = response_to_rect(rect_to_response(r))
        worst_param = max(worst_param, max(abs(a - b) for a, b in zip(r, back)))
        worst_iou = min(worst_iou, rect_iou(r, back))
    check("all five parameters survive the round trip", worst_param < 1e-6,
          f"worst error {worst_param:.2e}")
    check("round-tripped rectangle is its own IoU 1.0", worst_iou > 0.9999,
          f"worst IoU {worst_iou:.6f}")
    check("round-tripped rectangle scores correct against itself",
          all(is_correct(response_to_rect(rect_to_response(r)), [r])[0]
              for r in rects[:300]))


def test_convention():
    """Hand-computed answers, because a round trip cannot catch a shared error.

    test_roundtrip proves the encode and decode agree with each other. It
    would still pass if BOTH were rotated 90 degrees, or if both swapped
    the opening and jaw axes. These cases pin the absolute convention
    instead: the answers below were worked out by hand from
    cornell_data's stated rule (theta is the direction of the p0->p1
    opening edge, measured y-up, folded into [-90, 90)).
    """
    print("\n1b. Absolute convention, against hand-computed answers")
    cases = [
        # (finger_a, finger_b, jaw, expected cx, cy, theta, opening)
        ("left to right", (300, 240), (360, 240), 20, 330, 240, 0.0, 60.0),
        ("bottom to top", (300, 240), (300, 180), 20, 300, 210, -90.0, 60.0),
        ("up and to the right", (300, 240), (360, 180), 20, 330, 210, 45.0,
         float(np.hypot(60, 60))),
        ("down and to the right", (300, 180), (360, 240), 20, 330, 210, -45.0,
         float(np.hypot(60, 60))),
    ]
    for name, a, b, jaw, cx, cy, th, op in cases:
        got = response_to_rect({"a": a, "b": b, "jaw": jaw})
        ok = (abs(got[0] - cx) < 1e-9 and abs(got[1] - cy) < 1e-9
              and abs(got[2] - th) < 1e-9 and abs(got[3] - op) < 1e-9
              and abs(got[4] - jaw) < 1e-9)
        check(f"{name}: theta {th:+.0f}, opening {op:.1f}", ok,
              "" if ok else f"got theta {got[2]:+.1f}, opening {got[3]:.1f}, "
                            f"jaw {got[4]:.1f}, centre ({got[0]:.0f}, {got[1]:.0f})")

    # The finger separation is the OPENING, never the jaw width. A
    # conversion that swapped the two axes would put 60 in the jaw slot.
    got = response_to_rect({"a": (300, 240), "b": (360, 240), "jaw": 20})
    check("finger separation lands in the opening slot, not the jaw slot",
          got[3] == 60.0 and got[4] == 20.0, f"opening {got[3]}, jaw {got[4]}")

    # Which finger is called a and which b is arbitrary, and a grasp
    # flipped end for end is the same grasp, so the rectangle must not
    # depend on the order.
    fwd = response_to_rect({"a": (280, 300), "b": (355, 215), "jaw": 22})
    rev = response_to_rect({"a": (355, 215), "b": (280, 300), "jaw": 22})
    check("swapping finger_a and finger_b gives the same rectangle",
          max(abs(x - y) for x, y in zip(fwd, rev)) < 1e-9,
          f"{fwd} vs {rev}")


# ------------------------------------------------------- 2. parser fixtures

GOOD = ('{"object": "mug", "reasoning": "across the rim", '
        '"finger_a": [300, 220], "finger_b": [360, 240], '
        '"jaw_width_px": 25, "force": "medium", "confidence": "high"}')

FIXTURES = [
    ("clean JSON", GOOD, OK),
    ("fenced json block", "Here you go:\n```json\n" + GOOD + "\n```", OK),
    ("fenced plain block", "```\n" + GOOD + "\n```", OK),
    ("prose wrapped", "Sure! " + GOOD + " Hope that helps.", OK),
    ("trailing comma", GOOD.replace('"confidence": "high"}',
                                    '"confidence": "high",}'), OK),
    ("braces inside reasoning",
     GOOD.replace("across the rim", "the handle {left side}"), OK),
    ("string coordinates",
     GOOD.replace("[300, 220]", '["300", "220"]').replace(
         '"jaw_width_px": 25', '"jaw_width_px": "25"'), OK),
    ("empty reply", "", PARSE_FAIL),
    ("refusal prose", "I'm sorry, I can't determine a grasp from this image.",
     PARSE_FAIL),
    ("missing finger_b", GOOD.replace('"finger_b": [360, 240], ', ""), SCHEMA_FAIL),
    ("non-numeric coordinate",
     GOOD.replace("[300, 220]", '["left edge", "middle"]'), SCHEMA_FAIL),
    ("three-element point", GOOD.replace("[300, 220]", "[300, 220, 0]"), SCHEMA_FAIL),
    ("point off the image", GOOD.replace("[360, 240]", "[900, 240]"), RANGE_FAIL),
    ("negative coordinate", GOOD.replace("[300, 220]", "[-5, 220]"), RANGE_FAIL),
    ("degenerate zero opening", GOOD.replace("[360, 240]", "[300, 220]"), RANGE_FAIL),
    ("zero jaw width", GOOD.replace('"jaw_width_px": 25', '"jaw_width_px": 0'),
     RANGE_FAIL),
]


def test_parser():
    """Every reply shape that can plausibly arrive lands in the right bucket."""
    print("\n2. Parser fixtures")
    for name, text, want in FIXTURES:
        got, meta = parse_response(text)
        check(f"{name} -> {want}", got == want,
              "" if got == want else f"got {got} ({meta.get('reason', '')})")

    check("a reply that parses also converts",
          np.isfinite(response_to_rect(parse_response(GOOD)[1])).all())
    check("extract_json ignores a non-dict top level",
          extract_json("[1, 2, 3]") is None)

    # A large-but-interpretable grasp must be SCORED, not filtered out.
    # Excluding the model's implausible answers would flatter the score.
    wide = GOOD.replace("[360, 240]", "[480, 220]")     # 180px opening
    check("implausible-but-interpretable grasp is kept, not rejected",
          parse_response(wide)[0] == OK)


# ------------------------------------------------------- 3. self-agreement


def test_consistency():
    """The consistency primitives behave at their extremes."""
    print("\n3. Self-agreement primitives")
    r = (320.0, 240.0, 10.0, 60.0, 25.0)
    same = [r] * 5
    perp = [(320.0, 240.0, 10.0, 60.0, 25.0), (320.0, 240.0, 100.0, 60.0, 25.0)]
    far = [(100.0, 100.0, 0.0, 60.0, 25.0), (500.0, 400.0, 0.0, 60.0, 25.0)]

    check("identical repeats agree completely", self_agreement(same) == 1.0)
    check("perpendicular repeats do not agree", self_agreement(perp) == 0.0)
    check("disjoint repeats do not agree", self_agreement(far) == 0.0)
    check("one repeat has no self-agreement, not zero",
          np.isnan(self_agreement([r])))
    check("angle spread of identical repeats is zero",
          pairwise_angle_spread(same) == 0.0)
    check("angle spread folds at 180 degrees",
          abs(pairwise_angle_spread([(0, 0, 89.0, 1, 1),
                                     (0, 0, -89.0, 1, 1)]) - 2.0) < 1e-9)
    check("consensus picks the repeat nearest the others",
          consensus_index([r, r, (0.0, 0.0, 0.0, 60.0, 25.0)]) in (0, 1))

    hist = outcome_histogram([[1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [1, 0, 1, 0, 0]], 5)
    check("outcome histogram counts the stable and unstable images",
          hist[5] == 1 and hist[0] == 1 and hist[2] == 1, str(hist))

    rows = abstention_curve([1.0, 0.0, 1.0, 0.0], [1, 0, 1, 0])
    check("abstention curve keeps everything at threshold 0",
          rows[0][1] == 1.0 and rows[0][2] == 0.5)
    check("abstention curve trades coverage for accuracy when signal exists",
          rows[-1][1] == 0.5 and rows[-1][2] == 1.0)


# ------------------------------------------------------- 4. split hygiene


def test_split_hygiene():
    """Train-only code refuses non-train ids; the test run refuses a second call."""
    print("\n4. Split hygiene and the sealed-run guard")
    import system_c_run as R

    val_id = split_ids("val")[0]
    try:
        R.assert_split([val_id], "train")
        check("dev refuses a val image", False, "no SystemExit raised")
    except SystemExit:
        check("dev refuses a val image", True, f"pcd{val_id:04d}")

    try:
        R.assert_split(split_ids("train")[:5], "train")
        check("dev accepts genuine train images", True)
    except SystemExit:
        check("dev accepts genuine train images", False)

    # Exercise the sentinel against a throwaway path so the real one is
    # never created here. Creating it for real would burn the sealed run.
    real = R.TEST_SENTINEL
    existed_before = real.exists()
    with tempfile.TemporaryDirectory() as tmp:
        R.TEST_SENTINEL = Path(tmp) / "sentinel.json"
        try:
            ids = R.seal_test()
            check("first test claim succeeds", len(ids) == 123, f"{len(ids)} ids")
            try:
                R.seal_test()
                check("second test claim is refused", False, "no SystemExit raised")
            except SystemExit:
                check("second test claim is refused", True)
        finally:
            R.TEST_SENTINEL = real
    # The claim is that THIS SCRIPT did not touch the real sentinel, not that
    # the sentinel does not exist. Once the sealed test run has legitimately
    # happened the file is there for good, and asserting its absence would
    # turn a correct state of the world into a permanent red check.
    check("this check did not create or remove the real test sentinel",
          real.exists() == existed_before,
          f"exists={real.exists()} before={existed_before}")


# ------------------------------------------------------- 5. frozen modules


def test_frozen_shared_code():
    """cornell_data and grasp_metric must be untouched since they were frozen."""
    print("\n5. Shared modules are still frozen")
    files = ["scripts/cornell_data.py", "scripts/grasp_metric.py"]
    since = subprocess.run(["git", "log", "--oneline", f"{FROZEN_AT}..HEAD", "--"]
                           + files, capture_output=True, text=True).stdout.strip()
    check("no commit has touched them since they were frozen", since == "",
          since.replace("\n", "; "))
    dirty = subprocess.run(["git", "status", "--porcelain", "--"] + files,
                           capture_output=True, text=True).stdout.strip()
    check("no uncommitted edits to them either", dirty == "", dirty)


def main():
    print("Verifying System C (offline; no API key required)")
    test_roundtrip()
    test_convention()
    test_parser()
    test_consistency()
    test_split_hygiene()
    test_frozen_shared_code()

    print()
    if FAILURES:
        raise SystemExit(f"{len(FAILURES)} CHECK(S) FAILED: {', '.join(FAILURES)}")
    print("All checks passed. Safe to spend money.")


if __name__ == "__main__":
    main()
