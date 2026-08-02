"""How much System C disagrees with itself across repeated prompts.

WHY THIS IS ITS OWN MODULE
--------------------------
Spec section 5.4 asks for consistency across repeated prompts, and says
it "becomes a data point in the results, not something to average away".
This is the one place System C can produce a kind of finding neither A
nor B can: A is deterministic and B is a fixed checkpoint, so both give
the same answer to the same image forever. A VLM does not.

TWO DIFFERENT THINGS ARE MEASURED, AND THEY ARE NOT THE SAME
------------------------------------------------------------
  * OUTCOME consistency -- of the N repeats, how many scored correct.
    This needs ground truth. An image at 5/5 or 0/5 is stable; an image
    at 1-4 out of 5 is one where the same model, given the same pixels,
    flips between a valid and an invalid grasp.

  * GEOMETRIC self-agreement -- how much the N predicted rectangles
    disagree with EACH OTHER, ground truth left out entirely. Measured
    by running the frozen section 6 metric between pairs of repeats,
    with one repeat standing in as the other's ground truth.

The second one reuses is_correct rather than inventing a second notion
of "these two grasps are basically the same". That matters: a bespoke
similarity threshold would be a new free parameter nobody calibrated,
and the consistency number would no longer be on the same footing as
the accuracy number it sits next to in the results table.

Self-agreement is also the interesting one for a real gripper, because
it needs no labels. If it predicts correctness, a robot can refuse to
act when the model disagrees with itself. If it does not, the variance
is noise rather than uncertainty -- also worth reporting.
"""

from itertools import combinations

import numpy as np

from grasp_metric import angle_diff, is_correct, rect_iou


def pairs(rects):
    """All unordered pairs of repeats. Empty when fewer than two parsed."""
    return list(combinations(range(len(rects)), 2))


def self_agreement(rects):
    """Fraction of repeat pairs that pass the section 6 metric against each other.

    is_correct is symmetric in its two rectangles (IoU is symmetric and
    angle_diff is symmetric), so which repeat plays ground truth does not
    matter and each pair is counted once.

    Returns nan for fewer than two parsed repeats -- an image with one
    usable answer has no self-agreement, which is different from having
    poor self-agreement, and averaging a zero in would understate it.
    """
    ps = pairs(rects)
    if not ps:
        return float("nan")
    return float(np.mean([is_correct(rects[i], [rects[j]])[0] for i, j in ps]))


def pairwise_angle_spread(rects):
    """Mean angle between repeats, degrees. Folds at 180 like the metric."""
    ps = pairs(rects)
    if not ps:
        return float("nan")
    return float(np.mean([angle_diff(rects[i][2], rects[j][2]) for i, j in ps]))


def pairwise_iou(rects):
    """Mean IoU between repeats."""
    ps = pairs(rects)
    if not ps:
        return float("nan")
    return float(np.mean([rect_iou(rects[i], rects[j]) for i, j in ps]))


def consensus_index(rects):
    """Index of the repeat that agrees most with the other repeats.

    Used only for the explicitly-not-the-headline consensus row in the
    results. Picking this rectangle is an ensemble nobody actually runs,
    which is exactly why it is reported separately rather than as the
    System C number.
    """
    if not rects:
        return None
    if len(rects) == 1:
        return 0
    scores = [np.mean([rect_iou(r, o) for k, o in enumerate(rects) if k != i])
              for i, r in enumerate(rects)]
    return int(np.argmax(scores))


def outcome_histogram(per_image_correct, repeats):
    """{k: number of images where exactly k of the repeats were correct}."""
    hist = {k: 0 for k in range(repeats + 1)}
    for flags in per_image_correct:
        hist[sum(bool(f) for f in flags)] += 1
    return hist


def abstention_curve(agreements, correct_flags, thresholds=None):
    """If the robot only acts when self-agreement >= t, what does it get?

    Returns rows of (threshold, coverage, accuracy_on_covered). A flat
    accuracy column means self-agreement carries no signal about
    correctness, which is a real finding and not a failed experiment.
    """
    if thresholds is None:
        thresholds = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    a = np.asarray(agreements, float)
    c = np.asarray(correct_flags, float)
    keep_all = np.isfinite(a)
    rows = []
    for t in thresholds:
        keep = keep_all & (a >= t)
        n = int(keep.sum())
        rows.append((t, n / len(a) if len(a) else float("nan"),
                     float(c[keep].mean()) if n else float("nan")))
    return rows
