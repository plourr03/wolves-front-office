"""The Charlotte lineage is load-bearing (sets Model A's mu[CHA], which drives
swap value): CHH 1989-2002 belongs to the CHARLOTTE franchise; the 2003+ New
Orleans club is NOP. Plus relocation spot checks."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.etl.franchise_map import to_franchise


def test_charlotte_lineage():
    assert to_franchise("CHH", 1989) == "CHA"
    assert to_franchise("CHH", 2002) == "CHA"
    assert to_franchise("CHA", 2005) == "CHA"   # Bobcats
    assert to_franchise("CHO", 2015) == "CHA"
    assert to_franchise("CHO", 2026) == "CHA"
    assert to_franchise("NOH", 2003) == "NOP"   # New Orleans is NOT CHH's heir
    assert to_franchise("NOK", 2006) == "NOP"
    assert to_franchise("NOH", 2013) == "NOP"
    assert to_franchise("NOP", 2014) == "NOP"


def test_relocations():
    assert to_franchise("SEA", 2008) == "OKC"
    assert to_franchise("OKC", 2009) == "OKC"
    assert to_franchise("VAN", 2001) == "MEM"
    assert to_franchise("MEM", 2002) == "MEM"
    assert to_franchise("NJN", 2012) == "BKN"
    assert to_franchise("BRK", 2013) == "BKN"
    assert to_franchise("WSB", 1997) == "WAS"
    assert to_franchise("WAS", 1998) == "WAS"
    assert to_franchise("SDC", 1984) == "LAC"
    assert to_franchise("LAC", 1985) == "LAC"
    assert to_franchise("KCK", 1985) == "SAC"
    assert to_franchise("NOJ", 1979) == "UTA"
    assert to_franchise("PHO", 1990) == "PHX"


def test_unmapped_raises():
    with pytest.raises(KeyError):
        to_franchise("XYZ", 2000)
    with pytest.raises(KeyError):
        to_franchise("CHH", 2004)  # no Charlotte team existed in 2003-04
