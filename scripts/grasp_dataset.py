"""Dataset, cropping and augmentation for System B (spec section 5.3).

THE CROP
--------
Cornell images are 640x480 with the object on a platform, so feeding the
whole frame to a 224x224 network wastes most of the input on carpet and
furniture. A 400x400 crop centred at (320, 240) was chosen instead,
because measured on the TRAIN split it contains 100% of ground-truth
grasp centres (a 300x300 crop would lose 0.4% of them). No grasp is ever
cropped away, so no label is silently destroyed by preprocessing.

The crop is then resized to 224x224, a uniform scale of 0.56. Uniform
matters: a non-square resize would shear the grasp rectangles and make
the angle meaningless.

AUGMENT CORNERS, NEVER PARAMETERS
---------------------------------
Every geometric augmentation is one affine matrix. It is applied to the
image, and to the rectangle's four CORNER POINTS via rect_to_corners;
the (cx, cy, theta, opening, jaw) parameters are then recovered with
corners_to_rect. Both of those functions are frozen and already
validated in cornell_data.

This is the whole safety argument. There is no hand-written rule for
"how does theta transform under a vertical flip" that could be
backwards, because theta is never transformed at all -- it is re-derived
from where the corners actually moved. A label transform that is subtly
wrong corrupts training silently and never raises an exception, so the
design removes the opportunity rather than trying to test for it after
the fact. verify_augmentation.py then checks the result anyway.

Note that a flip is an improper transform (it reverses winding), which
is exactly why deriving theta by hand is error-prone and why the corner
route is worth the small extra cost.

SPLIT DISCIPLINE
----------------
GraspDataset asserts that every image it holds belongs to the split it
was asked for, and raises otherwise. Augmentation is applied to train
only; val and test are the deterministic centre crop with no randomness,
so a val number never moves for a reason unrelated to the model.

No dataset statistic is computed anywhere: normalisation uses the
external ImageNet constants, so there is nothing that could leak from
one split into another through preprocessing.
"""

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset

from cornell_data import (IMG_H, IMG_W, corners_to_rect, find_images,
                          load_rects, load_split, rect_to_corners)

CROP = 400                     # covers 100% of train grasp centres
SIZE = 224                     # ResNet input
SCALE = SIZE / CROP            # 0.56
CROP_X0 = (IMG_W - CROP) / 2.0  # 120.0
CROP_Y0 = (IMG_H - CROP) / 2.0  # 40.0

# ImageNet statistics. External constants on purpose -- see module docstring.
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

MAX_RECTS = 32                 # dataset max is 25; padded for batching

ROT_RANGE = 360.0
SCALE_JITTER = (0.9, 1.1)
BRIGHTNESS_JITTER = 0.25


def affine_matrix(angle_deg, scale, flip_x, flip_y, cx, cy):
    """Build one 3x3 affine about (cx, cy): flip, then scale, then rotate.

    Returned in image coordinates (y grows downward), which is the frame
    both the pixels and the corner points live in, so the same matrix
    can drive both.
    """
    t = np.radians(angle_deg)
    cos, sin = np.cos(t), np.sin(t)
    sx = -scale if flip_x else scale
    sy = -scale if flip_y else scale

    # rotate @ scale-and-flip, all about the origin
    m = np.array([[cos, -sin], [sin, cos]]) @ np.array([[sx, 0.0], [0.0, sy]])
    out = np.eye(3)
    out[:2, :2] = m
    out[:2, 2] = np.array([cx, cy]) - m @ np.array([cx, cy])
    return out


def apply_affine(points, m):
    """Apply a 3x3 affine to an (N, 2) array of points."""
    p = np.hstack([points, np.ones((len(points), 1))])
    return (p @ m.T)[:, :2]


def transform_rect(rect, m):
    """Move one grasp rectangle through an affine, via its corners.

    The point of the whole module: parameters out, corners moved,
    parameters back, using only frozen validated helpers.
    """
    return corners_to_rect(apply_affine(rect_to_corners(*rect), m))


def crop_matrix():
    """The fixed centre-crop-and-resize, as an affine so it composes."""
    m = np.eye(3)
    m[0, 0] = m[1, 1] = SCALE
    m[0, 2] = -CROP_X0 * SCALE
    m[1, 2] = -CROP_Y0 * SCALE
    return m


def load_image(path):
    """Full-resolution RGB as float32 in [0, 1]."""
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0


def warp_image(img, m, out_size):
    """Warp an image by a 3x3 affine using inverse mapping + bilinear sampling.

    Written out rather than using torchvision's transforms so that the
    image and the corner points are driven by literally the same matrix.
    Two separate transform implementations that are meant to agree is
    precisely the setup that produces silent label corruption.
    """
    inv = np.linalg.inv(m)
    ys, xs = np.mgrid[0:out_size, 0:out_size]
    pts = np.stack([xs.ravel(), ys.ravel()], axis=1).astype(np.float64)
    src = apply_affine(pts, inv)

    h, w = img.shape[:2]
    x, y = src[:, 0], src[:, 1]
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = (x - x0)[:, None], (y - y0)[:, None]

    def at(xi, yi):
        ok = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
        v = np.zeros((len(xi), img.shape[2]), dtype=np.float32)
        v[ok] = img[np.clip(yi, 0, h - 1)[ok], np.clip(xi, 0, w - 1)[ok]]
        return v

    top = at(x0, y0) * (1 - fx) + at(x0 + 1, y0) * fx
    bot = at(x0, y0 + 1) * (1 - fx) + at(x0 + 1, y0 + 1) * fx
    return (top * (1 - fy) + bot * fy).reshape(out_size, out_size, img.shape[2])


def sample_augmentation(rng):
    """Draw one random geometric augmentation, in FULL-RESOLUTION space."""
    return dict(
        angle=rng.uniform(0, ROT_RANGE),
        scale=rng.uniform(*SCALE_JITTER),
        flip_x=bool(rng.integers(2)),
        flip_y=bool(rng.integers(2)),
    )


def build_matrix(aug):
    """Compose augmentation (about the crop centre) with the fixed crop."""
    if aug is None:
        return crop_matrix()
    a = affine_matrix(aug["angle"], aug["scale"], aug["flip_x"], aug["flip_y"],
                      IMG_W / 2.0, IMG_H / 2.0)
    return crop_matrix() @ a


class GraspDataset(Dataset):
    """Cornell grasps for one split. Refuses to hold an image from another.

    Yields (image, rects, n_rects) where rects is padded to MAX_RECTS so
    that variable grasp counts can be batched. Targets are normalised
    into [0, 1] by SIZE, except the orientation which is handed over as
    degrees and converted to (cos 2t, sin 2t) by the model code.
    """

    def __init__(self, split, augment=False, ids=None, seed=42):
        self.split = split
        self.augment = augment
        self.rng = np.random.default_rng(seed)

        table = load_split()
        self.ids = sorted(ids) if ids is not None else sorted(
            p for p, (_, s) in table.items() if s == split)

        # Split hygiene, asserted rather than trusted. Fail loudly.
        wrong = [p for p in self.ids if table[p][1] != split]
        if wrong:
            raise SystemExit(
                f"SPLIT LEAK: GraspDataset({split!r}) was given {len(wrong)} "
                f"images from other splits: {wrong[:10]}")

        self.paths = find_images()
        self.rects = {p: load_rects(p) for p in self.ids}
        empty = [p for p in self.ids if not self.rects[p]]
        if empty:
            raise SystemExit(f"images with no positive grasp: {empty}")

    def __len__(self):
        return len(self.ids)

    def sample(self, i, aug=None):
        """Return (image HWC float, [rects]) after crop and any augmentation.

        Exposed separately from __getitem__ so the verification script
        can drive a specific augmentation rather than a random one.
        """
        pcd = self.ids[i]
        img = load_image(self.paths[pcd])
        m = build_matrix(aug)
        out = warp_image(img, m, SIZE)
        rects = [transform_rect(r, m) for r in self.rects[pcd]]
        return out, rects

    def __getitem__(self, i):
        aug = sample_augmentation(self.rng) if self.augment else None
        img, rects = self.sample(i, aug)

        if self.augment:
            img = np.clip(img * self.rng.uniform(1 - BRIGHTNESS_JITTER,
                                                 1 + BRIGHTNESS_JITTER), 0, 1)

        # Keep only grasps whose centre survived inside the frame. With the
        # 400px crop this never triggers unaugmented; rotation can push a
        # grasp out, and a target outside the image would be unlearnable.
        rects = [r for r in rects if 0 <= r[0] < SIZE and 0 <= r[1] < SIZE]
        if not rects:
            # Degenerate augmentation; fall back to the plain centre crop
            # rather than handing the model an empty target.
            img, rects = self.sample(i, None)

        x = torch.from_numpy(((img - MEAN) / STD).transpose(2, 0, 1).copy())

        pad = np.zeros((MAX_RECTS, 5), dtype=np.float32)
        n = min(len(rects), MAX_RECTS)
        for k, r in enumerate(rects[:n]):
            pad[k] = (r[0] / SIZE, r[1] / SIZE, r[2], r[3] / SIZE, r[4] / SIZE)
        return x.float(), torch.from_numpy(pad), n
