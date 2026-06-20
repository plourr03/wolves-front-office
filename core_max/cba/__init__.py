"""core_max.cba — the CBA-feasibility gate for the Core Maximization project.

This package OWNS a clean, typed, config-driven gate. The deterministic CBA math
(matching brackets, apron hard caps, aggregation rules, the multi-leg hard-cap
latch, TPE consumption) is REUSED unchanged from the verified offseason engine,
reached through the single adapter in `engine_bridge`. Nothing else in core_max
imports the offseason code directly.
"""

__version__ = "0.1.0"
