"""Shared deep-learning utilities (reused by every PyTorch paper)."""
from __future__ import annotations

import os
import random

import numpy as np


def set_seed(seed: int = 0) -> None:
    """Make a run reproducible across python / numpy / torch."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def get_device():
    """Return the best available torch device (cuda if present, else cpu)."""
    import torch
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")
