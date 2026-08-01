"""System B architectures and the orientation encoding (spec section 5.3).

THE ORIENTATION ENCODING IS THE POINT
-------------------------------------
System A topped out because axis-aligned COCO boxes can only ever emit 0
or 90 degrees; 13 of its 52 test failures cleared the IoU bar and failed
on angle alone. So orientation is where System B has to actually win.

theta cannot be regressed directly. Under the metric's 180-degree
symmetry -89 and +89 degrees are 2 degrees apart physically but 178
apart numerically, and any regression loss would treat that seam as a
huge error and pull predictions to the middle of the range.

Instead the network emits (cos 2t, sin 2t), L2-normalised onto the unit
circle, and decoding is t = 0.5 * atan2(sin, cos). Doubling the angle
maps the 180-degree-symmetric grasp space onto a full circle, so the
representation is continuous everywhere with no seam and no
quantisation floor. It also matches GG-CNN and GR-ConvNet, which keeps
the numbers comparable to published Cornell results.

A quiet bonus: MSE on that unit vector equals 2 - 2cos(2 dt), which is a
proper angular loss, monotone in angle error. So "plain MSE" on this
head is not a lazy default, it is the right family.

THREE HEADS, NOT ONE
--------------------
The three quantities have genuinely different output geometry: position
is a bounded coordinate, orientation is a point on a circle, size is a
bounded extent. A single six-wide linear layer would force one
activation choice on all three. Separate heads let each carry its own
constraint (sigmoid, L2-normalise, sigmoid) and make the per-term loss
weights mean something rather than being entangled in one matrix.

The trunk is shared because "where is the object and how is it lying"
is common to all three.
"""

import numpy as np
import torch
from torch import nn
from torchvision.models import (ResNet18_Weights, ResNet34_Weights, resnet18,
                                resnet34)

from grasp_dataset import SIZE

TRUNK = 256


def decode(out):
    """Model output dict -> (N, 5) array of (cx, cy, theta, opening, jaw) in pixels.

    Inverse of how GraspDataset normalises its targets, so a decoded
    prediction is directly comparable to a ground-truth rectangle and
    can be handed straight to grasp_metric.
    """
    pos = out["pos"].detach().cpu().numpy() * SIZE
    ori = out["ori"].detach().cpu().numpy()
    size = out["size"].detach().cpu().numpy() * SIZE
    theta = np.degrees(np.arctan2(ori[:, 1], ori[:, 0])) / 2.0
    theta = (theta + 90.0) % 180.0 - 90.0          # fold into [-90, 90)
    return np.stack([pos[:, 0], pos[:, 1], theta, size[:, 0], size[:, 1]], axis=1)


def encode_theta(theta_deg):
    """(cx, cy, theta, ...) target angle -> (cos 2t, sin 2t) on the unit circle."""
    t = torch.deg2rad(theta_deg) * 2.0
    return torch.stack([torch.cos(t), torch.sin(t)], dim=-1)


class Heads(nn.Module):
    """Shared trunk plus the three constrained output heads."""

    def __init__(self, in_features):
        super().__init__()
        self.trunk = nn.Sequential(
            nn.Linear(in_features, TRUNK), nn.ReLU(inplace=True), nn.Dropout(0.3))
        self.pos = nn.Linear(TRUNK, 2)
        self.ori = nn.Linear(TRUNK, 2)
        self.size = nn.Linear(TRUNK, 2)

    def forward(self, f):
        f = self.trunk(f)
        # Position and size are bounded fractions of the image, so sigmoid
        # keeps them in range without the loss having to police it.
        # Orientation is projected onto the unit circle instead, which is
        # what makes the angle decode well-defined.
        return {
            "pos": torch.sigmoid(self.pos(f)),
            "ori": nn.functional.normalize(self.ori(f), dim=-1, eps=1e-6),
            "size": torch.sigmoid(self.size(f)),
        }


class CustomCNN(nn.Module):
    """From-scratch baseline (spec 5.3 item 1). ~2M parameters.

    BatchNorm is not decoration here: training from scratch on 620
    images is unstable without it.
    """

    def __init__(self):
        super().__init__()
        chans = [3, 32, 64, 128, 256, 256]
        layers = []
        for a, b in zip(chans[:-1], chans[1:]):
            layers += [nn.Conv2d(a, b, 3, stride=2, padding=1),
                       nn.BatchNorm2d(b), nn.ReLU(inplace=True)]
        self.features = nn.Sequential(*layers)
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.heads = Heads(chans[-1])

    def forward(self, x):
        return self.heads(torch.flatten(self.pool(self.features(x)), 1))


class ResNetGrasp(nn.Module):
    """ImageNet-pretrained ResNet with the classifier replaced by grasp heads."""

    def __init__(self, depth=18, pretrained=True):
        super().__init__()
        if depth == 18:
            net = resnet18(weights=ResNet18_Weights.DEFAULT if pretrained else None)
        elif depth == 34:
            net = resnet34(weights=ResNet34_Weights.DEFAULT if pretrained else None)
        else:
            raise ValueError(f"unsupported depth {depth}")
        self.backbone = nn.Sequential(*list(net.children())[:-1])
        self.heads = Heads(net.fc.in_features)

    def forward(self, x):
        return self.heads(torch.flatten(self.backbone(x), 1))

    def param_groups(self, backbone_lr, head_lr):
        """Discriminative learning rates: the pretrained trunk moves slowly.

        Fine-tuning a backbone at the head's learning rate on 620 images
        destroys the ImageNet features faster than it learns anything.
        """
        return [{"params": self.backbone.parameters(), "lr": backbone_lr},
                {"params": self.heads.parameters(), "lr": head_lr}]


def build(name):
    """Name -> model. The three architectures the spec asks to compare."""
    if name == "cnn":
        return CustomCNN()
    if name == "resnet18":
        return ResNetGrasp(18)
    if name == "resnet34":
        return ResNetGrasp(34)
    raise ValueError(f"unknown model {name!r}")


MODELS = ("cnn", "resnet18", "resnet34")
