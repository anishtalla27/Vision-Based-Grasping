"""Test-time augmentation for System B, with medoid selection.

WHY
---
Grasp prediction is equivariant under the dihedral group of the image:
rotate the picture by 90 degrees and the correct grasp rotates with it.
A network trained with rotation augmentation approximates that
equivariance but does not have it exactly, so running the eight
dihedral views (4 rotations x optional flip), mapping each prediction
back into the reference frame and combining them removes some of the
view-dependent noise.

WHY MEDOID AND NOT MEAN
-----------------------
Averaging rectangles has the same problem the training loss avoided:
the mean of a handle grasp and a rim grasp lies between them where no
grasp exists. The medoid (the single view prediction closest to all the
others) is always one of the actual predictions, so it can never land in
that no-man's-land. Distance between two rectangles is position + size
in image fractions plus the chord distance between their (cos 2t, sin 2t)
orientation vectors, the same three quantities the loss is built from.

The mapping back uses the same corner-based transform as training
(transform_rect), so no hand-written rule about how theta behaves under
a flip exists here either.
"""

import numpy as np
import torch

from grasp_dataset import (MEAN, SIZE, STD, build_matrix, crop_matrix,
                           transform_rect)
from system_b_model import decode

# The eight dihedral views, expressed as the augmentation dicts the
# dataset already understands. angle is degrees, flips are booleans.
VIEWS = [dict(angle=a, scale=1.0, flip_x=f, flip_y=False)
         for a in (0.0, 90.0, 180.0, 270.0) for f in (False, True)]


def _distance(r1, r2):
    """Rectangle distance in the loss's own units (image fractions + orientation chord)."""
    dp = np.hypot(r1[0] - r2[0], r1[1] - r2[1]) / SIZE
    t1, t2 = np.radians(2 * r1[2]), np.radians(2 * r2[2])
    do = np.hypot(np.cos(t1) - np.cos(t2), np.sin(t1) - np.sin(t2))
    ds = (abs(r1[3] - r2[3]) + abs(r1[4] - r2[4])) / SIZE
    return dp + do + ds


def medoid(rects):
    d = np.array([[_distance(a, b) for b in rects] for a in rects])
    return rects[int(d.sum(1).argmin())]


def predict_tta(model, ds, dev, views=VIEWS):
    """Return one rectangle per image in the plain centre-crop frame.

    For each view the image is warped with build_matrix(view), the model
    predicts in that frame, and the rectangle is carried back through the
    inverse warp into full-resolution coordinates and then through the
    plain crop, so every view's prediction lands in the same frame the
    ground truth uses.
    """
    model.eval()
    to_ref = crop_matrix()
    out = []
    with torch.inference_mode():
        for i in range(len(ds)):
            cands = []
            for v in views:
                img, _ = ds.sample(i, v)
                x = torch.from_numpy(((img - MEAN) / STD).transpose(2, 0, 1).copy())
                pred = decode(model(x[None].float().to(dev)))[0]
                back = np.linalg.inv(build_matrix(v))
                full = transform_rect(tuple(float(p) for p in pred), back)
                cands.append(transform_rect(full, to_ref))
            out.append(medoid(cands))
    return out
