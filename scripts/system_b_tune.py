"""Choose the size-loss weight on VAL. The only tuned hyperparameter.

WHY THIS EXISTS
---------------
The overfit sanity check exposed a real imbalance. Grasp rectangles are
small relative to the frame, so a normalised size target is around
0.03-0.07 while a position target is around 0.5. With all three loss
terms weighted equally the size term contributes almost nothing, and
the model collapses the rectangle towards a small near-square. A
near-square rectangle has no meaningful orientation, so the angle
becomes degenerate too and the prediction fails on IoU.

On 8 memorised train images, W_SIZE 1.0 reached 87.5% and W_SIZE 3.0
reached 100%. That diagnosed the cause, but 8 images is far too little
to set a hyperparameter from, so the actual value is chosen here on VAL,
which is what val is for.

Only W_SIZE is swept. Position and orientation stay at 1.0, so there is
one degree of freedom rather than a grid, and the result is easy to
report honestly in the methods section.

Test is never touched: this imports loaders() from system_b_train, which
raises on "test".

Usage:
    python scripts/system_b_tune.py
"""

import json

import numpy as np
import torch
from torch.utils.data import DataLoader

import system_b_train as T
from cornell_data import INTERIM
from grasp_dataset import GraspDataset
from system_b_model import build

WEIGHTS = (1.0, 3.0, 10.0)
EPOCHS = 30
ARCH = "resnet18"          # swept on one architecture; applied to all three

# The custom CNN gets its own learning-rate sweep, for fairness rather
# than for score. The ResNets were given a considered discriminative
# scheme (1e-4 backbone, 1e-3 heads, the standard fine-tuning setup),
# while the from-scratch CNN simply inherited the head rate at 1e-3 with
# nobody ever asking whether that suits a network trained from nothing.
# Reporting "pretrained beats from-scratch" off the back of that would
# confound the architecture question with the tuning question, and the
# custom-CNN comparison is something spec section 5.3 explicitly asks
# for. Sweeping on VAL equalises the care the two arms received.
CNN_LRS = (1e-4, 3e-4, 1e-3, 3e-3)
CNN_EPOCHS = 45

OUT = INTERIM / "system_b_tuning.json"


def run(w):
    torch.manual_seed(T.SEED)
    np.random.seed(T.SEED)
    T.W_SIZE = w
    dev = T.device()

    train_ds, train_loader = T.loaders("train", augment=True, shuffle=True)
    val_ds, _ = T.loaders("val", augment=False, shuffle=False)

    model = build(ARCH).to(dev)
    opt = torch.optim.AdamW(model.param_groups(T.BACKBONE_LR, T.HEAD_LR),
                            weight_decay=T.WEIGHT_DECAY)

    best = -1.0
    for epoch in range(EPOCHS):
        model.train()
        for x, t, n in train_loader:
            opt.zero_grad()
            T.batch_loss(model(x.to(dev)), t.to(dev), n.to(dev), epoch).backward()
            opt.step()
        acc, ang = T.evaluate(model, val_ds, dev)
        best = max(best, acc)
        if epoch % 10 == 0 or epoch == EPOCHS - 1:
            print(f"    epoch {epoch:3d}  val_acc {acc*100:5.1f}%  val_ang {ang:5.1f}deg")
    return best


def run_cnn(lr):
    """Train the from-scratch CNN at one learning rate. Val only."""
    torch.manual_seed(T.SEED)
    np.random.seed(T.SEED)
    T.W_SIZE = 1.0
    dev = T.device()

    _, train_loader = T.loaders("train", augment=True, shuffle=True)
    val_ds, _ = T.loaders("val", augment=False, shuffle=False)

    model = build("cnn").to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=lr,
                            weight_decay=T.WEIGHT_DECAY)

    best, best_ang, last_loss = -1.0, 90.0, float("nan")
    for epoch in range(CNN_EPOCHS):
        model.train()
        losses = []
        for x, t, n in train_loader:
            opt.zero_grad()
            loss = T.batch_loss(model(x.to(dev)), t.to(dev), n.to(dev), epoch)
            loss.backward()
            opt.step()
            losses.append(loss.item())
        last_loss = float(np.mean(losses))
        acc, ang = T.evaluate(model, val_ds, dev)
        if epoch >= T.WARMUP_EPOCHS and acc > best:
            best, best_ang = acc, ang
        if epoch % 15 == 0 or epoch == CNN_EPOCHS - 1:
            print(f"    epoch {epoch:3d}  loss {last_loss:.4f}  "
                  f"val_acc {acc*100:5.1f}%  val_ang {ang:5.1f}deg")
    return best, best_ang, last_loss


def main():
    print(f"Tuning W_SIZE on VAL with {ARCH}, {EPOCHS} epochs each.")
    print("Test is unreachable from here (system_b_train.loaders raises on it).\n")

    results = {}
    for w in WEIGHTS:
        print(f"  W_SIZE = {w}")
        results[w] = run(w)
        print(f"  -> best val accuracy {results[w]*100:.1f}%\n")

    pick = max(results, key=results.get)
    print("=== val results ===")
    for w in WEIGHTS:
        star = "  <- selected" if w == pick else ""
        print(f"  W_SIZE {w:5.1f}   val {results[w]*100:5.1f}%{star}")
    print(f"\nPaste W_SIZE = {pick} into system_b_train.py")

    print(f"\n\nTuning the custom CNN's learning rate on VAL, "
          f"{CNN_EPOCHS} epochs each.")
    print("Fairness, not score: the ResNets got a tuned scheme and the CNN "
          "did not.\n")
    cnn = {}
    for lr in CNN_LRS:
        print(f"  cnn lr = {lr:g}")
        acc, ang, loss = run_cnn(lr)
        cnn[lr] = {"val_acc": acc, "val_angle_err": ang, "final_train_loss": loss}
        print(f"  -> best val {acc*100:.1f}%, angle err {ang:.1f}deg, "
              f"final loss {loss:.4f}\n")

    cnn_pick = max(cnn, key=lambda k: cnn[k]["val_acc"])
    print("=== cnn learning-rate results (val) ===")
    for lr in CNN_LRS:
        star = "  <- selected" if lr == cnn_pick else ""
        print(f"  lr {lr:<7g} val {cnn[lr]['val_acc']*100:5.1f}%  "
              f"ang {cnn[lr]['val_angle_err']:5.1f}deg  "
              f"loss {cnn[lr]['final_train_loss']:.4f}{star}")
    print(f"\nPaste CNN_LR = {cnn_pick:g} into system_b_train.py")

    OUT.write_text(json.dumps(
        {"swept": "W_SIZE", "arch": ARCH, "epochs": EPOCHS,
         "val_accuracy": {str(k): v for k, v in results.items()},
         "selected": pick,
         "cnn_lr_sweep": {str(k): v for k, v in cnn.items()},
         "cnn_lr_selected": cnn_pick}, indent=2))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
