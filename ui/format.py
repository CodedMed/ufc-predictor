"""Presentation-only helpers: value formatting and betting-odds arithmetic.

Nothing here feeds the model. These functions exist purely so the UI can render
missing data honestly and convert American odds into readable probabilities.
"""

from __future__ import annotations

import math
from html import escape
from typing import Optional

NA = "N/A"


# ---------------------------------------------------------------------------
# Missing-value handling
# ---------------------------------------------------------------------------

def is_missing(value) -> bool:
    """True for None / NaN. The fighter DB has real gaps (125 fighters lack
    striking data), and we surface those as N/A rather than printing 'nan'."""
    if value is None:
        return True
    try:
        return bool(math.isnan(float(value)))
    except (TypeError, ValueError):
        return False


def fmt(value, pattern: str = "{:.0f}", suffix: str = "") -> str:
    """Format a stat, degrading to N/A when the underlying value is missing."""
    if is_missing(value):
        return NA
    return pattern.format(float(value)) + suffix


def fmt_pct(value, decimals: int = 0) -> str:
    """Format a 0-1 ratio as a percentage."""
    if is_missing(value):
        return NA
    return f"{float(value) * 100:.{decimals}f}%"


def esc(text) -> str:
    """Escape user/data-derived text before it goes into an HTML template."""
    return escape(str(text), quote=True)


def split_name(name: str) -> tuple[str, str]:
    """Split a fighter name into (given names, surname) for the stacked
    broadcast-style treatment. Single-word names render entirely as surname."""
    parts = str(name).strip().split()
    if len(parts) <= 1:
        return "", (parts[0] if parts else "")
    return " ".join(parts[:-1]), parts[-1]


# ---------------------------------------------------------------------------
# American odds -> implied probability
# ---------------------------------------------------------------------------

def american_to_implied(odds: Optional[float]) -> Optional[float]:
    """Convert American moneyline odds to implied probability (0-1).

    Negative odds:  |odds| / (|odds| + 100)
    Positive odds:  100 / (odds + 100)

    Returns None for 0 / missing odds, which carry no market information.
    """
    if odds is None or is_missing(odds):
        return None
    odds = float(odds)
    if odds == 0:
        return None
    if odds < 0:
        return abs(odds) / (abs(odds) + 100.0)
    return 100.0 / (odds + 100.0)


def remove_vig(p_a: Optional[float], p_b: Optional[float]):
    """Normalise two implied probabilities so they sum to 1.

    Raw implied probabilities sum to >100% because the book's margin (vig) is
    baked in. Comparing a model probability against the raw number would
    overstate the model's edge, so we normalise before comparing and label the
    result as no-vig in the UI.

    Returns (p_a_novig, p_b_novig, margin) where margin is the book's overround
    (e.g. 0.035 == 3.5%). Returns (None, None, None) if either side is unknown.
    """
    if p_a is None or p_b is None:
        return None, None, None
    total = p_a + p_b
    if total <= 0:
        return None, None, None
    return p_a / total, p_b / total, total - 1.0


def fmt_odds(odds: Optional[float]) -> str:
    """Render moneyline odds the way a sportsbook would (+130 / -150)."""
    if odds is None or is_missing(odds):
        return NA
    odds = int(round(float(odds)))
    return f"+{odds}" if odds > 0 else str(odds)


def fmt_signed_pct(value: Optional[float]) -> str:
    """Render a probability delta as a signed percentage (+4.0% / -1.2%)."""
    if value is None or is_missing(value):
        return NA
    return f"{value * 100:+.1f}%"
