"""System B, round 2: a more stable training recipe, run over several seeds.

WHY THIS FILE EXISTS
--------------------
Round 1 (system_b_train.py) trained each architecture exactly once, at
seed 42, with a constant learning rate, and picked the checkpoint with the
highest val accuracy over roughly a hundred epochs. Two problems with
that, both visible in system_b_training.json:

  1. Val accuracy on 140 images swings 7-12 points between consecutive
     epochs (the last five ResNet18 epochs were 68.6, 47.9, 66.4, 63.6,
     71.4). Taking the MAX over ~100 such draws is a lottery, and the
     83.6% val figure is biased upward by exactly that lottery.
  2. Every claim about ResNet18 vs ResNet34 rests on one run each. With
     that much run-to-run noise, a 9-point test gap between two single
     runs is not evidence that the smaller network is better.

This recipe fixes both without changing the model, the loss, the data,
the metric, or the split:

  * Cosine learning-rate decay after the same 3-epoch warmup, so the
    final epochs are taken at a small step size and the weights settle
    instead of bouncing.
  * An exponential moving average (EMA) of the weights, evaluated on val
    alongside the raw weights. The EMA model is the one saved.
  * A FIXED epoch budget and NO checkpoint selection for the headline:
    the round-2 headline is the final-epoch EMA weights. The val-best EMA
    checkpoint is also saved, and its test score is printed for
    transparency, but the rule "headline = final EMA" is written here,
    before any round-2 test number exists, so test cannot influence it.
  * Several seeds per architecture, so the paper can report a mean and a
    spread instead of one draw.

The original recipe can also be re-run under a new seed (--recipe orig),
which is how the seed variance of the published 79.7% is measured.

TEST IS STILL UNREACHABLE FROM HERE. loaders() is imported from the
round-1 trainer and refuses to build a test split.

Usage:
    python scripts/system_b_train_v2.py --model resnet18 --seed 0
    python scripts/system_b_train_v2.py --model resnet18 --seed 0 --recipe orig
"""

import argparse
import copy
import json
import math
import time

import numpy as np
import torch

from cornell_data import INTERIM
from system_b_model import ResNetGrasp, build
from system_b_train import (BACKBONE_LR, CNN_LR, HEAD_LR, MIN_EPOCHS,
                            PATIENCE, WARMUP_EPOCHS, WEIGHT_DECAY, batch_loss,
                            device, evaluate, loaders)

OUT_DIR = INTERIM / "system_b_v2"

# Fixed budget. 60 was tried first (one seed per architecture, kept in
# system_b_v2/budget60/): with the cosine decay the effective learning
# budget is about half the epoch count, and both architectures' RAW val
# accuracy was still rising at epoch 59 (resnet18 59%, resnet34 71%),
# i.e. the decay cut training short. Raised to 100 on that val evidence,
# before any round-2 test number existed.
V2_EPOCHS = 100
EMA_DECAY = 0.995       # ~200-step horizon, about 10 epochs at 20 steps/epoch
LR_FLOOR = 0.01         # cosine decays to 1% of the base rate


class EMA:
    """Exponential moving average of a model's parameters and buffers."""

    def __init__(self, model, decay):
        self.decay = decay
        self.model = copy.deepcopy(model).eval()
        for p in self.model.parameters():
            p.requires_grad_(False)

    @torch.no_grad()
    def update(self, model):
        for e, m in zip(self.model.parameters(), model.parameters()):
            e.mul_(self.decay).add_(m.detach(), alpha=1 - self.decay)
        for e, m in zip(self.model.buffers(), model.buffers()):
            e.copy_(m)      # BatchNorm running stats: copy, do not average


def lr_factor(step, total_steps, warmup_steps):
    """Linear warmup then cosine decay to LR_FLOOR. Per optimiser step."""
    if step < warmup_steps:
        return (step + 1) / warmup_steps
    t = (step - warmup_steps) / max(1, total_steps - warmup_steps)
    return LR_FLOOR + (1 - LR_FLOOR) * 0.5 * (1 + math.cos(math.pi * t))


def make_optimizer(model):
    if isinstance(model, ResNetGrasp):
        return torch.optim.AdamW(model.param_groups(BACKBONE_LR, HEAD_LR),
                                 weight_decay=WEIGHT_DECAY)
    return torch.optim.AdamW(model.parameters(), lr=CNN_LR,
                             weight_decay=WEIGHT_DECAY)


def train(name, seed, recipe, epochs):
    torch.manual_seed(seed)
    np.random.seed(seed)
    dev = device()
    tag = f"{name}_{recipe}_s{seed}"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    train_ds, train_loader = loaders("train", augment=True, shuffle=True)
    # The dataset's own RNG drives augmentation; seed it per run too.
    train_ds.rng = np.random.default_rng(seed)
    val_ds, _ = loaders("val", augment=False, shuffle=False)

    model = build(name).to(dev)
    opt = make_optimizer(model)
    base_lrs = [g["lr"] for g in opt.param_groups]
    steps_per_epoch = len(train_loader)
    total_steps = epochs * steps_per_epoch
    ema = EMA(model, EMA_DECAY) if recipe == "v2" else None

    print(f"\n=== {tag}: {name} on {dev.type}, recipe={recipe}, "
          f"{epochs} max epochs, {steps_per_epoch} steps/epoch ===")

    history, best_val, best_epoch, step = [], -1.0, -1, 0
    t0 = time.time()
    for epoch in range(epochs):
        model.train()
        losses = []
        for x, targets, n in train_loader:
            if recipe == "v2":
                f = lr_factor(step, total_steps, WARMUP_EPOCHS * steps_per_epoch)
                for g, b in zip(opt.param_groups, base_lrs):
                    g["lr"] = b * f
            x, targets, n = x.to(dev), targets.to(dev), n.to(dev)
            opt.zero_grad()
            loss = batch_loss(model(x), targets, n, epoch)
            loss.backward()
            opt.step()
            if ema is not None:
                ema.update(model)
            losses.append(loss.item())
            step += 1

        raw_acc, raw_ang = evaluate(model, val_ds, dev)
        rec = {"epoch": epoch, "train_loss": float(np.mean(losses)),
               "val_acc": raw_acc, "val_angle_err": raw_ang}
        if ema is not None:
            ema_acc, ema_ang = evaluate(ema.model, val_ds, dev)
            rec.update({"ema_val_acc": ema_acc, "ema_val_angle_err": ema_ang})
        history.append(rec)

        # Selection candidate: EMA weights under v2, raw weights under orig.
        sel_model = ema.model if ema is not None else model
        sel_acc = rec.get("ema_val_acc", raw_acc)
        tag_s = ""
        if epoch >= WARMUP_EPOCHS and sel_acc > best_val:
            best_val, best_epoch = sel_acc, epoch
            torch.save(sel_model.state_dict(), OUT_DIR / f"{tag}_valbest.pt")
            tag_s = "  <- val best"
        if epoch % 5 == 0 or tag_s:
            extra = f"  ema_val {rec['ema_val_acc']*100:5.1f}%" if ema else ""
            print(f"  epoch {epoch:3d}  loss {rec['train_loss']:.4f}  "
                  f"val {raw_acc*100:5.1f}%{extra}{tag_s}")

        if recipe == "orig" and epoch >= MIN_EPOCHS and epoch - best_epoch >= PATIENCE:
            print(f"  early stop: no val improvement for {PATIENCE} epochs")
            break

    final_model = ema.model if ema is not None else model
    torch.save(final_model.state_dict(), OUT_DIR / f"{tag}_final.pt")
    final_acc = history[-1].get("ema_val_acc", history[-1]["val_acc"])
    mins = (time.time() - t0) / 60
    print(f"  done in {mins:.1f} min: final-epoch val {final_acc*100:.1f}%, "
          f"val-best {best_val*100:.1f}% at epoch {best_epoch}")

    summary = {"model": name, "seed": seed, "recipe": recipe, "epochs": len(history),
               "final_val_acc": final_acc, "best_val_acc": best_val,
               "best_epoch": best_epoch, "minutes": mins, "history": history}
    (OUT_DIR / f"{tag}.json").write_text(json.dumps(summary, indent=2))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="resnet18")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--recipe", choices=["v2", "orig"], default="v2")
    ap.add_argument("--epochs", type=int, default=None,
                    help="default: 60 for v2, 150 with early stopping for orig")
    a = ap.parse_args()
    epochs = a.epochs or (V2_EPOCHS if a.recipe == "v2" else 150)
    train(a.model, a.seed, a.recipe, epochs)


if __name__ == "__main__":
    main()
