"""Prove that augmented grasp labels still describe the augmented image.

WHY THIS EXISTS
---------------
This is the highest-risk code in System B. If a rotation moves the
pixels one way and the label another, nothing raises, no shape mismatch
occurs, training runs to completion, and the only symptom is a model
that never quite works for a reason no metric points at. Spec section
10.5 says to validate independently wherever an error would be
expensive and silent, and this qualifies twice over.

The checks below are chosen so that passing them requires the label
transform to actually be right, not merely self-consistent:

  1. RASTERISED CROSS-CHECK. Draw a grasp as a filled mask and warp the
     MASK through the image pipeline; separately warp the CORNERS and
     draw the result. These two paths share no geometry code, so their
     agreement is evidence rather than a tautology. This is the same
     trick that validated the metric itself.
  2. INVARIANCE. A rigid transform cannot change the IoU between two
     rectangles. If the label transform is wrong, this breaks at once.
  3. ALGEBRAIC IDENTITIES. Composition and involution properties that
     any correct transform must satisfy.
  4. DISTRIBUTION. Rotation augmentation must actually spread the angles.
     Catches a transform that silently collapses or biases orientation.
  5. VISUAL SHEETS. Rendered for eyeballing, because some mistakes are
     obvious to a human and invisible to an assertion.

Train split only.

Usage:
    python scripts/verify_augmentation.py
"""

import numpy as np
from PIL import Image, ImageDraw

from cornell_data import IMG_H, IMG_W, INTERIM, rect_to_corners
from grasp_dataset import (SIZE, GraspDataset, affine_matrix, apply_affine,
                           build_matrix, crop_matrix, transform_rect,
                           warp_image)
from grasp_metric import angle_diff, rect_iou

SHEETS = INTERIM / "system_b_aug_sheets"
FAILURES = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  ' + detail if detail else ''}")
    if not ok:
        FAILURES.append(name)


def rasterise(rect, w=SIZE, h=SIZE):
    """Fill a grasp rectangle by exact point-in-rectangle test at pixel centres.

    Deliberately NOT PIL's polygon fill. An earlier version of this
    check used PIL at both resolutions and failed at IoU 0.84, which
    looked like a label bug. It was not: PIL's polygon fill is inclusive
    of its boundary, so a shape drawn at 640x480 and one drawn at
    224x224 carry a boundary bias that differs by the scale factor, and
    that showed up as a systematic ~1px centroid offset between the two
    routes. Diagnosing it rather than relaxing the threshold mattered,
    because a genuine 1px label shift and a rasterisation artefact look
    identical from the IoU alone.

    A projection test onto the rectangle's own axes has no convention to
    disagree about, so both routes are measured the same way.
    """
    cx, cy, th, op, jw = rect
    t = np.radians(th)
    ux, uy = np.cos(t), -np.sin(t)
    ys, xs = np.mgrid[0:h, 0:w]
    dx, dy = xs - cx, ys - cy
    along = dx * ux + dy * uy
    across = dx * -uy + dy * ux
    return ((np.abs(along) <= op / 2) & (np.abs(across) <= jw / 2)).astype(np.float32)


def mask_iou(a, b, thresh=0.5):
    a, b = a > thresh, b > thresh
    u = (a | b).sum()
    return 0.0 if u == 0 else (a & b).sum() / u


def test_raster_cross_check():
    """Warp the mask vs warp the corners. Two independent routes."""
    print("\n1. Rasterised cross-check (mask pipeline vs corner pipeline)")
    rng = np.random.default_rng(0)
    worst, n = 1.0, 0
    for _ in range(60):
        rect = (rng.uniform(180, 460), rng.uniform(140, 340),
                rng.uniform(-90, 90), rng.uniform(30, 90), rng.uniform(20, 50))
        m = build_matrix(dict(angle=rng.uniform(0, 360),
                              scale=rng.uniform(0.9, 1.1),
                              flip_x=bool(rng.integers(2)),
                              flip_y=bool(rng.integers(2))))

        # Route A: fill at full res, then warp the PIXELS through the
        # same code path the training images take.
        warped_mask = warp_image(rasterise(rect, IMG_W, IMG_H)[:, :, None],
                                 m, SIZE)[:, :, 0]

        # Route B: warp the CORNERS, then fill at output resolution.
        corner_mask = rasterise(transform_rect(rect, m))

        iou = mask_iou(warped_mask, corner_mask)
        worst = min(worst, iou)
        n += 1
    # The residual gap is bilinear blur from the 0.56x downsample eating
    # a fraction of a pixel at the border, which is why this is 0.95 and
    # not 0.999. A label shift would show up far below this.
    check("warped mask agrees with warped corners (IoU > 0.95)", worst > 0.95,
          f"worst {worst:.4f} over {n} random augmentations")


def test_invariance():
    """A rigid transform cannot change the IoU between two rectangles."""
    print("\n2. Rigid-transform invariance of IoU and relative angle")
    rng = np.random.default_rng(1)
    worst_iou, worst_ang = 0.0, 0.0
    for _ in range(300):
        r1 = (rng.uniform(200, 440), rng.uniform(150, 330), rng.uniform(-90, 90),
              rng.uniform(30, 90), rng.uniform(20, 50))
        r2 = (r1[0] + rng.uniform(-30, 30), r1[1] + rng.uniform(-30, 30),
              rng.uniform(-90, 90), rng.uniform(30, 90), rng.uniform(20, 50))
        # Rotation and flips only: no scaling, so IoU must be preserved.
        m = affine_matrix(rng.uniform(0, 360), 1.0, bool(rng.integers(2)),
                          bool(rng.integers(2)), 320, 240)
        t1, t2 = transform_rect(r1, m), transform_rect(r2, m)
        worst_iou = max(worst_iou, abs(rect_iou(r1, r2) - rect_iou(t1, t2)))
        worst_ang = max(worst_ang,
                        abs(angle_diff(r1[2], r2[2]) - angle_diff(t1[2], t2[2])))
    check("IoU unchanged by rotation and flips", worst_iou < 1e-6,
          f"max drift {worst_iou:.2e}")
    check("relative angle unchanged by rotation and flips", worst_ang < 1e-6,
          f"max drift {worst_ang:.2e}")


def test_identities():
    """Composition and involution properties of the transform."""
    print("\n3. Algebraic identities")
    rng = np.random.default_rng(2)
    rects = [(rng.uniform(200, 440), rng.uniform(150, 330), rng.uniform(-90, 90),
              rng.uniform(30, 90), rng.uniform(20, 50)) for _ in range(50)]

    def close(a, b, tol=1e-6):
        return (abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol
                and angle_diff(a[2], b[2]) < tol
                and abs(a[3] - b[3]) < tol and abs(a[4] - b[4]) < tol)

    ident = affine_matrix(0, 1.0, False, False, 320, 240)
    check("rotation by 0 is the identity",
          all(close(transform_rect(r, ident), r) for r in rects))

    fx = affine_matrix(0, 1.0, True, False, 320, 240)
    check("horizontal flip is an involution",
          all(close(transform_rect(transform_rect(r, fx), fx), r) for r in rects))

    r90 = affine_matrix(90, 1.0, False, False, 320, 240)
    r180 = affine_matrix(180, 1.0, False, False, 320, 240)
    check("rot(90) twice equals rot(180)",
          all(close(transform_rect(transform_rect(r, r90), r90),
                    transform_rect(r, r180)) for r in rects))

    # A grasp rotated 180 degrees about ITS OWN CENTRE is the same
    # physical grasp, so the metric must not be able to tell them apart.
    # (About the image centre it is a different grasp somewhere else in
    # the frame, which is what an earlier version of this check got
    # wrong -- the test was broken, not the transform.)
    check("rot(180) about a grasp's own centre is the same grasp",
          all(rect_iou(transform_rect(r, affine_matrix(180, 1.0, False, False,
                                                       r[0], r[1])), r) > 0.999
              for r in rects))


def test_distribution():
    """Rotation augmentation must genuinely spread the orientations."""
    print("\n4. Angle distribution after augmentation")
    ds = GraspDataset("train", augment=True, seed=7)
    angles = []
    for i in range(0, len(ds), 4):
        _, rects, n = ds[i]
        angles.extend(float(rects[k][2]) for k in range(int(n)))
    a = np.array(angles)
    counts, _ = np.histogram(a, bins=np.arange(-90, 91, 30))
    frac = counts / counts.sum()
    check("angles spread across all six 30-degree buckets", frac.min() > 0.08,
          f"min bucket {frac.min()*100:.1f}%, max {frac.max()*100:.1f}%, n={len(a)}")
    check("angles stay in [-90, 90)", a.min() >= -90 and a.max() < 90,
          f"range {a.min():.1f} to {a.max():.1f}")


def test_unaugmented_labels_land_on_object():
    """The plain crop must not move labels relative to the pixels."""
    print("\n5. Deterministic crop keeps labels aligned")
    ds = GraspDataset("train", augment=False)
    m = crop_matrix()
    # A grasp centre in full-res coords must map to the same place the
    # crop matrix says it does. Checked against the raw loader, not the
    # dataset's own output, so a bug in one is not hidden by the other.
    worst = 0.0
    for i in range(0, len(ds), 37):
        pcd = ds.ids[i]
        for r in ds.rects[pcd]:
            expect = apply_affine(np.array([[r[0], r[1]]]), m)[0]
            got = transform_rect(r, m)
            worst = max(worst, abs(expect[0] - got[0]), abs(expect[1] - got[1]))
    check("crop maps grasp centres exactly as the matrix says", worst < 1e-9,
          f"max drift {worst:.2e}")

    _, rects, n = ds[0]
    inside = all(0 <= rects[k][0] < 1 and 0 <= rects[k][1] < 1
                 for k in range(int(n)))
    check("normalised targets land inside [0, 1)", inside)


def draw_sheets(n=8):
    """Render augmented images with their transformed labels, for eyeballing."""
    SHEETS.mkdir(parents=True, exist_ok=True)
    ds = GraspDataset("train", augment=True, seed=3)
    rng = np.random.default_rng(11)
    for k in range(n):
        i = int(rng.integers(len(ds)))
        aug = dict(angle=rng.uniform(0, 360), scale=rng.uniform(0.9, 1.1),
                   flip_x=bool(rng.integers(2)), flip_y=bool(rng.integers(2)))
        img, rects = ds.sample(i, aug)
        im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
        d = ImageDraw.Draw(im)
        for r in rects:
            d.polygon([tuple(p) for p in rect_to_corners(*r)], outline=(0, 230, 0))
        d.text((4, 4), f"pcd{ds.ids[i]:04d} rot={aug['angle']:.0f} "
                       f"fx={int(aug['flip_x'])} fy={int(aug['flip_y'])}",
               fill=(255, 255, 0))
        im.save(SHEETS / f"aug_{k:02d}_pcd{ds.ids[i]:04d}.png")
    print(f"\nWrote {n} augmentation sheets to {SHEETS}")


def main():
    print("Verifying System B augmentation (train split only)")
    test_raster_cross_check()
    test_invariance()
    test_identities()
    test_distribution()
    test_unaugmented_labels_land_on_object()
    draw_sheets()

    print()
    if FAILURES:
        raise SystemExit(f"{len(FAILURES)} CHECK(S) FAILED: {', '.join(FAILURES)}")
    print("All checks passed. Augmented labels track the augmented pixels.")


if __name__ == "__main__":
    main()
