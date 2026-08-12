"""UFC Analytics - fight prediction dashboard.

This module is the presentation layer. The model artefacts, the feature
definitions and the arithmetic that builds a feature row are intentionally
unchanged from the original implementation - see `build_feature_row`.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from ui import components as C
from ui.data import get_fighter_info, get_profile, load_fighter_profiles
from ui.format import american_to_implied, esc, is_missing, remove_vig
from ui.theme import CSS

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="UFC Analytics | Fight Prediction Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ===========================================================================
# MODEL LOADING  -  unchanged behaviour, cached so reruns don't re-read disk
# ===========================================================================

@st.cache_resource(show_spinner=False)
def load_core():
    return (
        joblib.load(BASE_DIR / "model.pkl"),
        joblib.load(BASE_DIR / "features.pkl"),
        joblib.load(BASE_DIR / "fighter_db.pkl"),
    )


@st.cache_resource(show_spinner=False)
def load_enhanced():
    """Optional outcome/round/method ensemble. Absent models degrade gracefully."""
    try:
        models = (
            joblib.load(BASE_DIR / "models/outcome_model.pkl"),
            joblib.load(BASE_DIR / "models/round_model.pkl"),
            joblib.load(BASE_DIR / "models/method_model.pkl"),
        )
        with open(BASE_DIR / "models/metadata.json") as handle:
            return (*models, json.load(handle), True)
    except Exception:
        return (None, None, None, {}, False)


model, features, fighter_db = load_core()
outcome_model, round_model, method_model, metadata, enhanced_mode = load_enhanced()
profiles = load_fighter_profiles()

# Stats the model needs; used only to warn before a prediction is attempted.
REQUIRED_STATS = [
    ("height", "height"),
    ("reach", "reach"),
    ("age", "age"),
    ("win_streak", "win streak"),
    ("longest_streak", "longest streak"),
    ("wins", "wins"),
    ("losses", "losses"),
    ("sig_str", "strikes per minute"),
    ("td", "takedowns"),
    ("sig_str_pct", "strike accuracy"),
    ("td_pct", "takedown accuracy"),
]


# ===========================================================================
# PREDICTION
# The feature names, the subtraction order and the column ordering must keep
# matching the training pipeline in train_enhanced_models.py. Reindexing by
# `features` (loaded from the trained artefacts) is what guarantees that.
# ===========================================================================

def build_feature_row(r_stats: dict, b_stats: dict, r_odds: float, b_odds: float,
                      fight_length: int) -> pd.DataFrame:
    return pd.DataFrame([{
        'height_dif': r_stats['height'] - b_stats['height'],
        'reach_dif': r_stats['reach'] - b_stats['reach'],
        'age_dif': r_stats['age'] - b_stats['age'],
        'win_streak_dif': r_stats['win_streak'] - b_stats['win_streak'],
        'longest_win_streak_dif': r_stats['longest_streak'] - b_stats['longest_streak'],
        'win_dif': r_stats['wins'] - b_stats['wins'],
        'sig_str_dif': r_stats['sig_str'] - b_stats['sig_str'],
        'avg_td_dif': r_stats['td'] - b_stats['td'],
        'sig_str_pct_dif': r_stats['sig_str_pct'] - b_stats['sig_str_pct'],
        'td_pct_dif': r_stats['td_pct'] - b_stats['td_pct'],
        'losses_dif': r_stats['losses'] - b_stats['losses'],
        'odds_dif': r_odds - b_odds,
        'no_of_rounds': fight_length,
    }])[features]


# ===========================================================================
# DATA HELPERS
# ===========================================================================

def get_stats_from_db(name: str) -> dict:
    row = fighter_db.loc[name]
    return {
        'height': row['height'], 'reach': row['reach'], 'age': row['age'],
        'win_streak': row['win_streak'], 'longest_streak': row['longest_streak'],
        'wins': row['wins'], 'losses': row['losses'], 'sig_str': row['sig_str'],
        'sig_str_pct': row['sig_str_pct'], 'td': row['td'], 'td_pct': row['td_pct'],
    }


def missing_stats(stats: dict) -> list[str]:
    """Labels of stats the model needs but the database doesn't have."""
    return [label for key, label in REQUIRED_STATS if is_missing(stats.get(key))]


def html(markup: str) -> None:
    """Render raw HTML.

    Uses st.html (not st.markdown) so the markup skips markdown parsing, and
    strips per-line indentation first - four leading spaces would otherwise be
    parsed as a fenced code block and dumped on screen verbatim.
    """
    st.html("\n".join(line.strip() for line in markup.strip().splitlines()))


# ===========================================================================
# HEADER
# ===========================================================================

html(CSS)
html(C.nav(metadata.get("outcome_accuracy") if enhanced_mode else None, len(fighter_db)))


# ===========================================================================
# MATCHUP SELECTION
# ===========================================================================

html(C.section("Matchup"))

mode_col, length_col = st.columns([1, 1])

with mode_col:
    mode = st.segmented_control(
        "Input mode",
        options=["Fighter Search", "Manual Entry"],
        default="Fighter Search",
        key="mode",
    ) or "Fighter Search"

with length_col:
    fight_length = st.segmented_control(
        "Fight length",
        options=[3, 5],
        default=3,
        format_func=lambda rounds: f"{rounds} Rounds",
        key="fight_length",
    ) or 3

fighter_names = sorted(fighter_db.index.tolist())
search_mode = mode == "Fighter Search"

if search_mode:
    left, middle, right = st.columns([1, 0.16, 1])

    with left:
        html('<div class="ufc-pick-red">')
        r_name = st.selectbox(
            "Red Corner", fighter_names, index=0, key="r_name",
            format_func=lambda name: name.strip(),
        )
        html("</div>")

    with middle:
        html('<div style="text-align:center;padding-top:1.9rem;" class="ufc-label">vs</div>')

    with right:
        html('<div class="ufc-pick-blue">')
        b_name = st.selectbox(
            "Blue Corner", fighter_names, index=1, key="b_name",
            format_func=lambda name: name.strip(),
        )
        html("</div>")

    r_stats = get_stats_from_db(r_name)
    b_stats = get_stats_from_db(b_name)
    r_display, b_display = r_name.strip(), b_name.strip()
    r_profile, b_profile = get_profile(profiles, r_name), get_profile(profiles, b_name)
    r_info, b_info = get_fighter_info(r_name), get_fighter_info(b_name)

else:
    r_display, b_display = "Red Fighter", "Blue Fighter"
    r_profile = b_profile = {"weight_class": None, "stance": None}
    r_info = b_info = {"image": None, "summary": None}

    left, right = st.columns(2)

    def manual_inputs(prefix: str, label: str) -> dict:
        """Same widgets, ranges and defaults as before - just grouped."""
        html(f'<div class="ufc-label" style="margin:0.6rem 0 0.2rem 0;">{label}</div>')
        col1, col2, col3 = st.columns(3)
        with col1:
            height = st.number_input("Height (cm)", 150.0, 220.0, 180.0, key=f"{prefix}_h")
            reach = st.number_input("Reach (cm)", 150.0, 230.0, 185.0, key=f"{prefix}_r")
            age = st.number_input("Age", 18, 50, 28, key=f"{prefix}_a")
            longest = st.number_input("Longest streak", 0, 20, 3, key=f"{prefix}_ls")
        with col2:
            wins = st.number_input("Wins", 0, 50, 10, key=f"{prefix}_w")
            losses = st.number_input("Losses", 0, 30, 3, key=f"{prefix}_l")
            streak = st.number_input("Win streak", 0, 20, 2, key=f"{prefix}_ws")
        with col3:
            sig_str = st.number_input("Strikes / min", 0.0, 15.0, 4.0, key=f"{prefix}_ss")
            takedowns = st.number_input("Takedowns", 0.0, 10.0, 1.5, key=f"{prefix}_td")
        sig_pct = st.slider("Strike accuracy (%)", 0, 100, 45, key=f"{prefix}_sp") / 100
        td_pct = st.slider("Takedown accuracy (%)", 0, 100, 40, key=f"{prefix}_tp") / 100

        return {
            'height': height, 'reach': reach, 'age': age,
            'win_streak': streak, 'longest_streak': longest,
            'wins': wins, 'losses': losses, 'sig_str': sig_str,
            'sig_str_pct': sig_pct, 'td': takedowns, 'td_pct': td_pct,
        }

    with left:
        r_stats = manual_inputs("r", "Red Corner")
    with right:
        b_stats = manual_inputs("b", "Blue Corner")


# ===========================================================================
# MATCHUP HERO
# ===========================================================================

html(C.matchup_hero(
    {"name": r_display, "stats": r_stats, "info": r_info, "profile": r_profile},
    {"name": b_display, "stats": b_stats, "info": b_info, "profile": b_profile},
    rounds=fight_length,
))


# ===========================================================================
# MARKET ODDS
# ===========================================================================

html(C.section("Market Odds"))

_, odds_left, odds_right, _ = st.columns([0.55, 1, 1, 0.55])
suffix = "" if search_mode else "2"
with odds_left:
    r_odds = st.number_input(
        f"{r_display} — moneyline", -1000, 1000, -150, key=f"r_o{suffix}",
    )
with odds_right:
    b_odds = st.number_input(
        f"{b_display} — moneyline", -1000, 1000, 130, key=f"b_o{suffix}",
    )


# ===========================================================================
# ANALYZE
# ===========================================================================

st.write("")
_, cta, _ = st.columns([1, 0.85, 1])
with cta:
    analyze = st.button("⚡ Analyze Fight", key="predict", use_container_width=True)

# A stored result belongs to one exact set of inputs. If anything changes, drop
# it rather than showing a prediction that no longer matches the form.
signature = json.dumps(
    {"mode": mode, "r": r_display, "b": b_display,
     "rs": {k: str(v) for k, v in r_stats.items()},
     "bs": {k: str(v) for k, v in b_stats.items()},
     "ro": r_odds, "bo": b_odds, "len": fight_length},
    sort_keys=True,
)
if st.session_state.get("signature") != signature:
    st.session_state.pop("result", None)

if analyze:
    blockers = []
    for label, stats in ((r_display, r_stats), (b_display, b_stats)):
        gaps = missing_stats(stats)
        if gaps:
            blockers.append(f"<strong>{esc(label)}</strong> is missing {esc(', '.join(gaps))}")

    if blockers:
        # The model cannot consume NaN, and imputing values here would silently
        # change what it predicts. Explain instead.
        st.session_state["result"] = {"error": " and ".join(blockers)}
    else:
        with st.spinner("Analyzing matchup…"):
            row = build_feature_row(r_stats, b_stats, r_odds, b_odds, fight_length)
            prob_red = float(model.predict_proba(row)[0][1])

            result = {"prob_red": prob_red, "prob_blue": 1.0 - prob_red}

            if enhanced_mode:
                round_probs = round_model.predict_proba(row)[0]
                round_classes = sorted(round_model.classes_)
                method_probs = method_model.predict_proba(row)[0]
                method_classes = sorted(method_model.classes_)

                # The round model is trained on 3- and 5-round bouts pooled, so
                # it always spreads probability across R1-R5. A 3-round fight
                # cannot reach R4/R5, so condition on the rounds that can
                # actually happen and renormalise over them. The model itself
                # is untouched - this is Bayes' rule on an impossible outcome.
                possible = [
                    (int(cls), float(p))
                    for cls, p in zip(round_classes, round_probs)
                    if int(cls) <= fight_length
                ]
                discarded = 1.0 - sum(p for _, p in possible)
                total = sum(p for _, p in possible)

                if total > 0:
                    possible = [(cls, p / total) for cls, p in possible]

                result["rounds"] = [(f"Round {cls}", p) for cls, p in possible]
                result["round_pick"], result["round_conf"] = max(
                    possible, key=lambda item: item[1]
                )
                result["round_discarded"] = discarded
                result["fight_length"] = fight_length

                result["methods"] = [
                    (str(cls), float(p)) for cls, p in zip(method_classes, method_probs)
                ]
                result["method_pick"] = str(method_classes[method_probs.argmax()])
                result["method_conf"] = float(method_probs.max())

        st.session_state["result"] = result

    st.session_state["signature"] = signature


# ===========================================================================
# RESULTS
# ===========================================================================

result = st.session_state.get("result")

if result and result.get("error"):
    html(C.section("Model Prediction"))
    html(C.note(
        f"{result['error']}. The model requires all twelve features, so this "
        "matchup can't be scored. Try another fighter, or switch to "
        "<strong>Manual Entry</strong> to supply the values yourself.",
        kind="error",
    ))

elif result:
    prob_red, prob_blue = result["prob_red"], result["prob_blue"]

    extras = []
    if result.get("round_pick") is not None:
        extras.append((
            "Projected round",
            f"R{result['round_pick']}",
            f"{result['round_conf'] * 100:.1f}% likely",
        ))
        extras.append((
            "Projected method",
            esc(result["method_pick"]),
            f"{result['method_conf'] * 100:.1f}% likely",
        ))

    html(C.section("Model Prediction"))
    html(C.prediction_card(r_display, b_display, prob_red, prob_blue, extras))

    # --- Market vs model -------------------------------------------------
    r_implied = american_to_implied(r_odds)
    b_implied = american_to_implied(b_odds)
    r_novig, b_novig, margin = remove_vig(r_implied, b_implied)

    html(C.section("Market vs Model"))
    html(C.market_vs_model(
        r_display, b_display, r_odds, b_odds,
        r_implied, b_implied, r_novig, b_novig, margin,
        prob_red, prob_blue,
    ))

    # --- Round / method breakdown ---------------------------------------
    if result.get("rounds"):
        length = result.get("fight_length", 3)
        discarded = result.get("round_discarded", 0.0)

        html(C.section("Fight Breakdown"))
        html(C.breakdown([
            C.distribution_card(
                "Round of victory",
                result["rounds"],
                footnote=(
                    f"Modelled as a {length}-round bout. A residual "
                    f"{discarded * 100:.1f}% still landed on rounds that cannot "
                    f"occur and was redistributed over the rest."
                ) if discarded > 0.0005 else f"Modelled as a {length}-round bout.",
            ),
            C.distribution_card(
                "Method of victory",
                result["methods"],
                footnote=f"Modelled as a {length}-round bout.",
            ),
        ]))

else:
    html(C.section("Model Prediction"))
    html(C.empty_state("Select both fighters and run the analysis to see the model's read."))


# ===========================================================================
# FIGHTER COMPARISON
# ===========================================================================

html(C.section("Fighter Comparison"))
html(C.comparison(r_display, b_display, r_stats, b_stats))

if search_mode and (r_info.get("summary") or b_info.get("summary")):
    bio_left, bio_right = st.columns(2)
    for column, name, info in ((bio_left, r_display, r_info), (bio_right, b_display, b_info)):
        if info.get("summary"):
            with column:
                with st.expander(f"{name} — background"):
                    st.write(info["summary"])


# ===========================================================================
# FOOTER
# ===========================================================================

snapshot = None
if "date" in fighter_db.columns:
    try:
        snapshot = pd.to_datetime(fighter_db["date"]).max().strftime("%b %Y")
    except Exception:
        snapshot = None

html(C.footer(snapshot))
