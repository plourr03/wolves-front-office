"""F4 scaffolding: the permutation-invariant set-attention primary
(spec 8.4 architecture 2).

Structure, exactly as specified: per-player embedding of the K-dim skill
vector; self-attention WITHIN the offense set and within the defense set
(pairwise interactions are the entire point); cross-attention offense ->
defense; mean-pooled readout concatenated with context covariates
(home_share, rest_delta, season index) into a small head. Two attention
blocks, width 64-128, deliberately small.

Permutation invariance is structural (attention + mean pool, no
positional anything) and TESTED, not asserted: shuffling the five players
of either side must not change the prediction to float precision
(tests/test_set_attention.py).

NO real fit until F3 vectors exist (directive 2026-07-03 item 4). The
trainer runs on synthetic data in the smoke tests: it must (a) beat the
additive linear baseline on synthetic data with planted pairwise synergy,
and (b) hold permutation invariance after training.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn


class AttentionBlock(nn.Module):
    def __init__(self, width: int, heads: int = 4):
        super().__init__()
        self.attn = nn.MultiheadAttention(width, heads, batch_first=True)
        self.norm1 = nn.LayerNorm(width)
        self.ff = nn.Sequential(nn.Linear(width, width * 2), nn.GELU(),
                                nn.Linear(width * 2, width))
        self.norm2 = nn.LayerNorm(width)

    def forward(self, x, kv=None):
        kv = x if kv is None else kv
        a, _ = self.attn(x, kv, kv, need_weights=False)
        x = self.norm1(x + a)
        return self.norm2(x + self.ff(x))


class SetSynergyNet(nn.Module):
    """f(offense five, defense five, context) -> points per 100."""

    def __init__(self, k_dim: int, width: int = 64, n_context: int = 3):
        super().__init__()
        self.embed = nn.Sequential(nn.Linear(k_dim, width), nn.GELU(),
                                   nn.Linear(width, width))
        self.off_self = AttentionBlock(width)
        self.def_self = AttentionBlock(width)
        self.cross = AttentionBlock(width)
        self.head = nn.Sequential(
            nn.Linear(2 * width + n_context, width), nn.GELU(),
            nn.Linear(width, 1))
        # target normalization, set by train(); predictions always come
        # back in real points-per-100 units
        self.register_buffer("y_loc", torch.tensor(0.0))
        self.register_buffer("y_scale", torch.tensor(1.0))

    def forward(self, off_z, def_z, context):
        """off_z/def_z: (B, 5, K); context: (B, n_context)."""
        o = self.off_self(self.embed(off_z))
        d = self.def_self(self.embed(def_z))
        o = self.cross(o, kv=d)
        pooled = torch.cat([o.mean(dim=1), d.mean(dim=1), context], dim=-1)
        return self.head(pooled).squeeze(-1) * self.y_scale + self.y_loc


def train(model: SetSynergyNet, off_z, def_z, context, y, poss_w,
          epochs: int = 200, lr: float = 1e-3, batch: int = 512,
          seed: int = 20260702, patience: int = 20,
          val_frac: float = 0.15, verbose: bool = False) -> dict:
    """Possession-weighted MSE, AdamW, early stopping on a random split
    (temporal splits are the CALLER's job at G3; this trainer is split-
    agnostic plumbing)."""
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    n = len(y)
    idx = rng.permutation(n)
    n_val = max(1, int(n * val_frac))
    vi, ti = idx[:n_val], idx[n_val:]

    t = lambda a: torch.as_tensor(np.asarray(a), dtype=torch.float32)
    off_z, def_z, context = t(off_z), t(def_z), t(context)
    y, poss_w = t(y), t(poss_w)

    # normalize the target once (points-per-100 sits around 110 with sd
    # ~15; a head starting at 0 wastes its whole budget climbing there)
    y_tr, w_tr = y[ti], poss_w[ti]
    loc = float((y_tr * w_tr).sum() / w_tr.sum())
    scale = float(torch.sqrt(((y_tr - loc) ** 2 * w_tr).sum() / w_tr.sum()))
    model.y_loc.fill_(loc)
    model.y_scale.fill_(max(scale, 1e-6))

    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    best, best_state, stale = float("inf"), None, 0
    for epoch in range(epochs):
        model.train()
        perm = rng.permutation(len(ti))
        for s in range(0, len(ti), batch):
            b = ti[perm[s:s + batch]]
            opt.zero_grad()
            pred = model(off_z[b], def_z[b], context[b])
            loss = ((pred - y[b]) ** 2 * poss_w[b]).sum() / poss_w[b].sum()
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            vp = model(off_z[vi], def_z[vi], context[vi])
            vloss = float(((vp - y[vi]) ** 2 * poss_w[vi]).sum()
                          / poss_w[vi].sum())
        if vloss < best - 1e-6:
            best, stale = vloss, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            stale += 1
            if stale >= patience:
                break
        if verbose and epoch % 10 == 0:
            print(f"  epoch {epoch}: val {vloss:.4f}")
    if best_state is not None:
        model.load_state_dict(best_state)
    return {"val_mse": best, "epochs_ran": epoch + 1}
