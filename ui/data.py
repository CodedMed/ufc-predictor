"""Presentation-only data lookups.

These enrich the *display* of a matchup (portraits, division, stance). They are
deliberately isolated from the prediction pipeline: nothing here is ever fed to
a model, and every lookup fails soft so a network hiccup can never break the app.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, TypedDict

import pandas as pd
import requests
import streamlit as st

WIKI_API = "https://en.wikipedia.org/w/api.php"

# Wikipedia began returning 403 to unidentified clients, which is why portraits
# silently disappeared. A descriptive User-Agent is now required by their policy.
_HEADERS = {
    "User-Agent": (
        "UFC-Analytics/1.0 (fight prediction dashboard; "
        "https://github.com/ufc-analytics) python-requests"
    )
}

MASTER_CSV = Path(__file__).resolve().parent.parent / "data" / "ufc-master.csv"


class FighterInfo(TypedDict):
    image: Optional[str]
    summary: Optional[str]


# ---------------------------------------------------------------------------
# Wikipedia portraits
# ---------------------------------------------------------------------------

def _tokens(text: str) -> set[str]:
    return set(re.sub(r"[^a-z0-9 ]", " ", str(text).lower()).split())


def _is_plausible_match(name: str, title: str) -> bool:
    """Guard against Wikipedia's search returning a loosely-related page.

    Searching a lesser-known fighter can land on an article like "2026 in UFC",
    whose lead image is the UFC logo - which would then be rendered as that
    fighter's portrait. We require the surname to appear in the page title, or
    a strong overlap with the full name.
    """
    name_tokens = _tokens(name)
    title_tokens = _tokens(title)
    if not name_tokens:
        return False

    surname = str(name).strip().split()[-1].lower()
    if surname and surname in title_tokens:
        return True

    overlap = len(name_tokens & title_tokens) / len(name_tokens)
    return overlap >= 0.6


def _is_generic_image(url: str) -> bool:
    """Reject branding/placeholder assets that aren't a person."""
    lowered = url.lower()
    return any(token in lowered for token in ("logo", "ufc_logo", "icon", "wordmark"))


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def get_fighter_info(name: str) -> FighterInfo:
    """Fetch a portrait + short bio for a fighter. Always returns a dict."""
    empty: FighterInfo = {"image": None, "summary": None}
    query = str(name).strip()
    if not query:
        return empty

    try:
        response = requests.get(
            WIKI_API,
            headers=_HEADERS,
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": f"{query} UFC mixed martial artist",
                "gsrlimit": 1,
                "prop": "pageimages|extracts",
                "piprop": "thumbnail",
                # Large enough for the hero portrait rather than a 140px thumb.
                "pithumbsize": 800,
                "exintro": 1,
                "explaintext": 1,
                "exsentences": 3,
                "format": "json",
            },
            timeout=6,
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {})
    except Exception:
        # Offline, rate-limited, or malformed response: fall back to the
        # silhouette placeholder rather than surfacing an error.
        return empty

    for page in pages.values():
        title = page.get("title", "")
        if not _is_plausible_match(query, title):
            return empty

        image = (page.get("thumbnail") or {}).get("source")
        if image and _is_generic_image(image):
            image = None

        return {"image": image, "summary": page.get("extract") or None}

    return empty


# ---------------------------------------------------------------------------
# Division + stance (read-only, from the existing dataset)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_fighter_profiles() -> pd.DataFrame:
    """Most recent weight class + stance per fighter, from the master dataset.

    Read-only enrichment for the tale of the tape. The columns are never used as
    model features. Returns an empty frame if the dataset is unavailable.
    """
    try:
        raw = pd.read_csv(
            MASTER_CSV,
            usecols=["date", "R_fighter", "B_fighter", "weight_class", "R_Stance", "B_Stance"],
        )
    except Exception:
        return pd.DataFrame(columns=["weight_class", "stance"])

    red = raw[["date", "R_fighter", "weight_class", "R_Stance"]].rename(
        columns={"R_fighter": "fighter", "R_Stance": "stance"}
    )
    blue = raw[["date", "B_fighter", "weight_class", "B_Stance"]].rename(
        columns={"B_fighter": "fighter", "B_Stance": "stance"}
    )

    combined = pd.concat([red, blue], ignore_index=True)
    combined["date"] = pd.to_datetime(combined["date"], errors="coerce")
    combined = combined.sort_values("date")

    return combined.groupby("fighter").last()[["weight_class", "stance"]]


def get_profile(profiles: pd.DataFrame, name: str) -> dict:
    """Look up a fighter's division/stance, tolerating names absent from the set."""
    if name in profiles.index:
        row = profiles.loc[name]
        return {
            "weight_class": None if pd.isna(row["weight_class"]) else str(row["weight_class"]),
            "stance": None if pd.isna(row["stance"]) else str(row["stance"]),
        }
    return {"weight_class": None, "stance": None}
