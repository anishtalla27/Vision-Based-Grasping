"""Train System B. TRAIN fits, VAL selects, TEST is not reachable from here.

BEST-MATCH LOSS
---------------
Cornell labels about six grasps per image, and 41.5% of train images
have grasps spanning more than the metric's 30-degree tolerance. The
obvious thing, regressing to the average of them, is provably capped:
measured on train, a model that predicts that average PERFECTLY still
only scores 86.5%, because averaging a handle grasp and a rim grasp
lands between them where neither is valid.

So the loss is computed against every labelled grasp and only the
smallest is backpropagated. That makes the training objective agree with
the metric, which already counts a prediction correct if it matches ANY
ground truth. The measured ceiling for that framing is 100%.

The known risk is early instability, with the target flipping between
grasps before the model has learned anything. Mitigated with a short
warmup against the most central grasp, after which the assignment
switches. Both are logged.

WHY THE LOSS FAMILIES DIFFER PER TERM
-------------------------------------
  position  Smooth L1. Huber resists the occasional far-outlier label;
            plain MSE lets one bad grasp dominate a batch.
  orient    MSE on the unit vector, which equals 2 - 2cos(2 dt). That is
            a proper angular loss, monotone in angle error, with no
            wraparound seam. Not a lazy default.
  size      Smooth L1, same outlier argument; opening spans 3-139 px.

TEST IS UNREACHABLE FROM THIS FILE
----------------------------------
loaders() raises on "test". There is no code path here that can open a
test image, which is a stronger guarantee than remembering not to.
Model selection, early stopping and every hyperparameter are decided on
val alone.

Usage:
    python scripts/system_b_train.py            (trains all three)
"""

import json
import os
import time

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader

from cornell_data import INTERIM
from grasp_dataset import SIZE, GraspDataset
from grasp_metric import ANGLE_TOL_DEG, IOU_MIN, angle_diff, rect_iou
from system_b_model import MODELS, ResNetGrasp, build, decode, encode_theta

CKPT_DIR = INTERIM / "system_b_checkpoints"

SEED = 42
BATCH = 32
MAX_EPOCHS = 150
PATIENCE = 25
WARMUP_EPOCHS = 3

HEAD_LR = 1e-3
BACKBONE_LR = 1e-4
WEIGHT_DECAY = 1e-4

# Loss weights. Start equal; any change is decided on VAL only.
W_POS, W_ORI, W_SIZE = 1.0, 1.0, 1.0


def device():
    return torch.device("mps" if torch.backends.mps.is_available() else "cpu")


def loaders(split, augment, shuffle):
    """Build a loader. Refuses to touch test, by construction."""
    if split == "test":
        raise SystemExit(
            "system_b_train.py must never read the test split. Test is opened "
            "only by system_b_eval.py, once, at the end.")
    ds = GraspDataset(split, augment=augment, seed=SEED)
    return ds, DataLoader(ds, batch_size=BATCH, shuffle=shuffle, num_workers=0)


def per_rect_loss(out, targets, mask):
    """Loss of each prediction against EVERY labelled grasp. (B, R) tensor.

    Broadcasting the prediction across the rectangle axis is what makes
    the best-match minimum cheap enough to do every step.
    """
    pos = out["pos"].unsqueeze(1)                      # (B, 1, 2)
    ori = out["ori"].unsqueeze(1)
    size = out["size"].unsqueeze(1)

    t_pos = targets[:, :, 0:2]
    t_ori = encode_theta(targets[:, :, 2])
    t_size = targets[:, :, 3:5]

    l_pos = nn.functional.smooth_l1_loss(
        pos.expand_as(t_pos), t_pos, reduction="none", beta=0.05).sum(-1)
    l_ori = ((ori - t_ori) ** 2).sum(-1)
    l_size = nn.functional.smooth_l1_loss(
        size.expand_as(t_size), t_size, reduction="none", beta=0.05).sum(-1)

    total = W_POS * l_pos + W_ORI * l_ori + W_SIZE * l_size
    # Padded slots must never be selected by the min.
    return total.masked_fill(~mask, float("inf"))


def central_index(targets, mask):
    """Index of the grasp closest to the image centre, for the warmup target."""
    d = ((targets[:, :, 0:2] - 0.5) ** 2).sum(-1)
    return d.masked_fill(~mask, float("inf")).argmin(dim=1)


def batch_loss(out, targets, n, epoch):
    """Best-match loss, with a warmup on the most central grasp."""
    r = targets.shape[1]
    mask = torch.arange(r, device=targets.device)[None, :] < n[:, None]
    per = per_rect_loss(out, targets, mask)

    if epoch < WARMUP_EPOCHS:
        idx = central_index(targets, mask)
        return per.gather(1, idx[:, None]).squeeze(1).mean()
    return per.min(dim=1).values.mean()


def evaluate(model, ds, dev):
    """Section 6 accuracy on a split, using the shared frozen metric."""
    model.eval()
    loader = DataLoader(ds, batch_size=BATCH, shuffle=False, num_workers=0)
    correct = total = 0
    ang_err = []
    with torch.inference_mode():
        for x, targets, n in loader:
            preds = decode(model(x.to(dev)))
            t = targets.numpy()
            for i in range(len(preds)):
                gts = [(t[i, k, 0] * SIZE, t[i, k, 1] * SIZE, t[i, k, 2],
                        t[i, k, 3] * SIZE, t[i, k, 4] * SIZE)
                       for k in range(int(n[i]))]
                p = tuple(preds[i])
                hit = any(angle_diff(p[2], g[2]) <= ANGLE_TOL_DEG
                          and rect_iou(p, g) > IOU_MIN for g in gts)
                correct += hit
                total += 1
                ang_err.append(min(angle_diff(p[2], g[2]) for g in gts))
    return correct / total, float(np.mean(ang_err))


def train_one(name, wandb_run=None):
    """Train a single architecture, selecting on val accuracy."""
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    dev = device()

    train_ds, train_loader = loaders("train", augment=True, shuffle=True)
    val_ds, _ = loaders("val", augment=False, shuffle=False)

    model = build(name).to(dev)
    n_par = sum(p.numel() for p in model.parameters())
    if isinstance(model, ResNetGrasp):
        opt = torch.optim.AdamW(model.param_groups(BACKBONE_LR, HEAD_LR),
                                weight_decay=WEIGHT_DECAY)
    else:
        opt = torch.optim.AdamW(model.parameters(), lr=HEAD_LR,
                                weight_decay=WEIGHT_DECAY)

    print(f"\n=== {name} ({n_par/1e6:.1f}M params) on {dev.type} ===")
    print(f"train {len(train_ds)} images (augmented), val {len(val_ds)} images")

    best_acc, best_epoch, history = -1.0, -1, []
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    ckpt = CKPT_DIR / f"{name}.pt"
    t0 = time.time()

    for epoch in range(MAX_EPOCHS):
        model.train()
        losses = []
        for x, targets, n in train_loader:
            x, targets, n = x.to(dev), targets.to(dev), n.to(dev)
            opt.zero_grad()
            loss = batch_loss(model(x), targets, n, epoch)
            loss.backward()
            opt.step()
            losses.append(float(loss))

        train_loss = float(np.mean(losses))
        val_acc, val_ang = evaluate(model, val_ds, dev)
        history.append({"epoch": epoch, "train_loss": train_loss,
                        "val_acc": val_acc, "val_angle_err": val_ang})

        tag = ""
        if val_acc > best_acc:
            best_acc, best_epoch = val_acc, epoch
            torch.save(model.state_dict(), ckpt)
            tag = "  <- best"
        if epoch == WARMUP_EPOCHS - 1:
            tag += "  (warmup ends, best-match assignment starts next epoch)"

        if epoch % 5 == 0 or tag:
            print(f"  epoch {epoch:3d}  loss {train_loss:.4f}  "
                  f"val_acc {val_acc*100:5.1f}%  val_ang {val_ang:5.1f}deg{tag}")

        if wandb_run is not None:
            wandb_run.log({f"{name}/train_loss": train_loss,
                           f"{name}/val_acc": val_acc,
                           f"{name}/val_angle_err": val_ang, "epoch": epoch})

        if epoch - best_epoch >= PATIENCE:
            print(f"  early stop: no val improvement for {PATIENCE} epochs")
            break

    mins = (time.time() - t0) / 60
    print(f"  best val accuracy {best_acc*100:.1f}% at epoch {best_epoch} "
          f"({mins:.1f} min) -> {ckpt}")
    return {"model": name, "params": n_par, "best_val_acc": best_acc,
            "best_epoch": best_epoch, "minutes": mins, "history": history}


def start_wandb():
    """W&B if a key is present, otherwise carry on without it."""
    if not os.environ.get("WANDB_API_KEY"):
        print("WANDB_API_KEY not set; training without W&B logging.")
        return None
    import wandb
    return wandb.init(project="vision-grasp-research", name="system-b",
                      config={"batch": BATCH, "head_lr": HEAD_LR,
                              "backbone_lr": BACKBONE_LR, "seed": SEED,
                              "warmup_epochs": WARMUP_EPOCHS})


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    run = start_wandb()
    results = [train_one(name, run) for name in MODELS]

    out = INTERIM / "system_b_training.json"
    out.write_text(json.dumps(results, indent=2))

    print("\n=== val selection (test has not been touched) ===")
    for r in sorted(results, key=lambda r: -r["best_val_acc"]):
        print(f"  {r['model']:<10} {r['params']/1e6:5.1f}M params  "
              f"val {r['best_val_acc']*100:5.1f}%  epoch {r['best_epoch']}")
    pick = max(results, key=lambda r: r["best_val_acc"])
    print(f"\nSelected on VAL: {pick['model']}")
    print(f"Wrote {out}")
    if run is not None:
        run.finish()


if __name__ == "__main__":
    main()
