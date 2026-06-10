#!/usr/bin/env python3
"""
age_curve.py  -- standard NBA aging prior applied to the (un-aged) RAPM/consensus spine.

The spine is backward-looking 3-season RAPM with NO aging adjustment, so it rates a
39-year-old Conley at +1.49 (his age 36-38 value) and that drives the rotation question.
This applies a documented aging delta from the recency-weighted window center (~1.5 years
before 2026-27) to the player's 2026-27 age, split 50/50 across offense and defense.

Rates are per-year net-impact change, centered so prime (24-27) is roughly flat:
  <24 +0.30 | 24-27 +0.05 | 28-30 -0.15 | 31-32 -0.35 | 33-34 -0.50 | 35-36 -0.70 |
  37-38 -1.00 | 39+ -1.40   (older = steeper; 39 is the cliff)
This is a STANDARD prior, not fit to make any scenario look good; magnitude is a stated
assumption and the cluster is reported with and without it.
"""

import os
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMORTEM = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POSTMORTEM)
from lib import db  # noqa: E402

LOOKBACK = 1.5            # years from recency-weighted window center to 2026-27
SEASON_START = date(2026, 10, 1)
_AGE = {}


def _rate(a):
    if a < 24: return 0.30
    if a < 28: return 0.05
    if a < 31: return -0.15
    if a < 33: return -0.35
    if a < 35: return -0.50
    if a < 37: return -0.70
    if a < 39: return -1.00
    return -1.40


def ages_2026_27(player_ids):
    """{player_id(str): age at 2026-27 season start} from nba_player_bio.birthdate."""
    need = [int(p) for p in player_ids if str(p) not in _AGE and str(p).isdigit()]
    if need:
        r = db.query("SELECT player_id, birthdate FROM nba_player_bio WHERE player_id = ANY(%s)", (need,))
        for _, x in r.iterrows():
            if x["birthdate"]:
                _AGE[str(int(x["player_id"]))] = (SEASON_START - x["birthdate"]).days / 365.25
    return {str(p): _AGE.get(str(p)) for p in player_ids}


def age_delta(age):
    """Net-impact delta to apply for 2026-27, integrated over [age-LOOKBACK, age]."""
    if age is None:
        return 0.0
    d, a = 0.0, age - LOOKBACK
    step = 0.25
    while a < age:
        d += _rate(a) * step
        a += step
    return d


def aged_impacts(imp, ids=None, decline_only=False):
    """Return a copy of imp with the aging delta applied (off += d/2, def -= d/2, since
    def is lower=better, so a decline raises def). decline_only=True applies only NEGATIVE
    deltas (zeros young-player improvement) -- the conservative floor for the asymmetric
    band, since old-age decline is a reliable regularity but young-age improvement has a
    long tail of non-improvers."""
    import copy
    out = copy.deepcopy(imp)
    target = ids or list(imp.keys())
    ages = ages_2026_27([t for t in target if t in imp and t != "REPLACEMENT"])
    for pid in target:
        if pid not in out or pid == "REPLACEMENT":
            continue
        d = age_delta(ages.get(pid))
        if decline_only and d > 0:
            d = 0.0
        out[pid]["off"] = out[pid]["off"] + d / 2.0
        out[pid]["def"] = out[pid]["def"] - d / 2.0
    return out


if __name__ == "__main__":
    import build_team_ratings as A
    sys.path.insert(0, HERE)
    imp = A.load_impacts()
    chk = {"Conley": "201144", "Dosunmu": "1630245", "Kyrie": "202681", "AD": "203076",
           "Markkanen": "1628374", "Giddey": "1630581", "Tre Jones": "1630200", "Naz": "1629675"}
    ages = ages_2026_27(list(chk.values()))
    print(f"{'player':12}{'age':>6}{'delta':>8}{'net pre':>9}{'net aged':>10}")
    for nm, pid in chk.items():
        net = imp[pid]["off"] - imp[pid]["def"]; d = age_delta(ages[pid])
        print(f"{nm:12}{ages[pid]:>6.1f}{d:>+8.2f}{net:>9.2f}{net + d:>10.2f}")
