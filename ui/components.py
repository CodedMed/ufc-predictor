"""HTML renderers for the dashboard.

Each function returns a self-contained HTML string. Rendering whole sections as
one block (rather than stitching them out of st.columns) is what lets the layout
use real CSS grid and stop looking like a Streamlit form.

These functions only format values that are handed to them - they never compute
a prediction.
"""

from __future__ import annotations

from typing import Optional

from .format import NA, esc, fmt, fmt_odds, fmt_pct, fmt_signed_pct, is_missing, split_name

# ---------------------------------------------------------------------------
# Small building blocks
# ---------------------------------------------------------------------------

def section(title: str) -> str:
    """A section heading with a trailing rule."""
    return f'<div class="ufc-section"><h2>{esc(title)}</h2><div class="rule"></div></div>'


def note(message: str, kind: str = "info") -> str:
    """An inline advisory. `message` may contain <strong> tags."""
    cls = "ufc-note err" if kind == "error" else "ufc-note"
    return f'<div class="{cls}"><div>{message}</div></div>'


def empty_state(message: str) -> str:
    return f'<div class="ufc-empty">{esc(message)}</div>'


def _silhouette() -> str:
    """Neutral fighter placeholder - built from divs so it renders everywhere,
    and deliberately not an emoji."""
    return (
        '<div class="silhouette">'
        '<div class="sil-head"></div>'
        '<div class="sil-body"></div>'
        "</div>"
    )


def _portrait(info: dict, name: str) -> str:
    image = (info or {}).get("image")
    if image:
        return f'<img src="{esc(image)}" alt="{esc(name)}" loading="lazy" />'
    return _silhouette()


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def nav(accuracy: Optional[float], fighter_count: int) -> str:
    """Compact header. Only shows destinations/stats that genuinely exist."""
    acc = f"{accuracy * 100:.1f}%" if accuracy is not None else NA
    return f"""
    <div class="ufc-nav">
      <div class="brand">
        <div class="bolt">&#9889;</div>
        <div>
          <div class="brand-name">UFC Analytics</div>
          <div class="brand-sub">Fight Prediction Engine</div>
        </div>
      </div>
      <div class="meta">
        <div class="stat">
          <div class="v">{esc(acc)}</div>
          <div class="k">Outcome accuracy</div>
        </div>
        <div class="stat">
          <div class="v">{fighter_count:,}</div>
          <div class="k">Fighters</div>
        </div>
        <div class="ufc-badge"><span class="dot"></span>ML Powered</div>
      </div>
    </div>
    """


# ---------------------------------------------------------------------------
# Matchup hero + tale of the tape
# ---------------------------------------------------------------------------

def _fighter_side(corner: str, name: str, stats: dict, info: dict, profile: dict) -> str:
    first, last = split_name(name)
    label = "Red Corner" if corner == "red" else "Blue Corner"
    division = (profile or {}).get("weight_class")

    wins, losses = stats.get("wins"), stats.get("losses")
    record = NA if is_missing(wins) or is_missing(losses) else f"{int(wins)}-{int(losses)}"

    first_html = f'<span class="first">{esc(first)}</span>' if first else ""

    return f"""
    <div class="fighter {corner}">
      <div class="corner"><span class="pip"></span>{esc(label)}</div>
      <div class="portrait">{_portrait(info, name)}</div>
      <div class="name">{first_html}<span class="last">{esc(last)}</span></div>
      <div class="record">{esc(record)}<span class="tag">Record</span></div>
      <div class="division">{esc(division or "Division N/A")}</div>
    </div>
    """


# Physical attributes shown in the hero. Height/reach/age are context-dependent
# in MMA, so none of them get a "winner" highlight here.
_TAPE_ROWS = [
    ("height", "Height", lambda v: fmt(v, "{:.0f}", " cm")),
    ("reach", "Reach", lambda v: fmt(v, "{:.0f}", " cm")),
    ("age", "Age", lambda v: fmt(v, "{:.0f}")),
]


def _tale_of_the_tape(red_stats: dict, blue_stats: dict,
                      red_profile: dict, blue_profile: dict) -> str:
    rows = []
    for key, label, formatter in _TAPE_ROWS:
        left, right = formatter(red_stats.get(key)), formatter(blue_stats.get(key))
        left_cls = "v left na" if left == NA else "v left"
        right_cls = "v right na" if right == NA else "v right"
        rows.append(
            f'<div class="tape-row">'
            f'<div class="{left_cls}">{esc(left)}</div>'
            f'<div class="k">{esc(label)}</div>'
            f'<div class="{right_cls}">{esc(right)}</div>'
            f"</div>"
        )

    left_stance = (red_profile or {}).get("stance") or NA
    right_stance = (blue_profile or {}).get("stance") or NA
    rows.append(
        f'<div class="tape-row">'
        f'<div class="{"v left na" if left_stance == NA else "v left"}">{esc(left_stance)}</div>'
        f'<div class="k">Stance</div>'
        f'<div class="{"v right na" if right_stance == NA else "v right"}">{esc(right_stance)}</div>'
        f"</div>"
    )

    return f'<div class="tape">{"".join(rows)}</div>'


def matchup_hero(red: dict, blue: dict, rounds: Optional[int] = None) -> str:
    """The centrepiece: two fighters, a VS mark, and the tale of the tape."""
    red_division = (red.get("profile") or {}).get("weight_class")
    blue_division = (blue.get("profile") or {}).get("weight_class")

    if red_division and blue_division and red_division == blue_division:
        bout = red_division
    elif red_division and blue_division:
        bout = "Catchweight"
    else:
        bout = "Bout"

    # Division and length go on separate lines so neither ever wraps mid-phrase.
    bout_html = f"<span>{esc(bout)}</span>"
    if rounds:
        bout_html += f'<span class="rounds">{rounds} Rounds</span>'

    return f"""
    <div class="ufc-hero">
      <div class="ufc-hero-grid">
        {_fighter_side("red", red["name"], red["stats"], red["info"], red.get("profile", {}))}
        <div class="vs">
          <div class="rail"></div>
          <div class="mark">VS</div>
          <div class="bout">{bout_html}</div>
          <div class="rail bottom"></div>
        </div>
        {_fighter_side("blue", blue["name"], blue["stats"], blue["info"], blue.get("profile", {}))}
      </div>
      {_tale_of_the_tape(red["stats"], blue["stats"],
                         red.get("profile", {}), blue.get("profile", {}))}
    </div>
    """


# ---------------------------------------------------------------------------
# Model prediction
# ---------------------------------------------------------------------------

def prediction_card(red_name: str, blue_name: str, prob_red: float, prob_blue: float,
                    extras: Optional[list[tuple[str, str, str]]] = None) -> str:
    """The headline result. `extras` is a list of (label, value, sub) cells."""
    red_wins = prob_red >= prob_blue
    pick_name = red_name if red_wins else blue_name
    pick_corner = "red" if red_wins else "blue"
    confidence = max(prob_red, prob_blue)

    # Percentages are rounded for display but the bar uses full precision.
    left_pct = f"{prob_red * 100:.0f}%"
    right_pct = f"{prob_blue * 100:.0f}%"

    cells = [
        (
            "Model pick",
            f'<span class="pick {pick_corner}">{esc(pick_name)}</span>',
            "Higher modelled win probability",
        ),
        ("Confidence", f"{confidence * 100:.1f}%", "Probability assigned to the pick"),
    ]
    for label, value, sub in (extras or []):
        cells.append((label, value, sub))

    cell_html = "".join(
        f'<div class="cell"><div class="k">{esc(label)}</div>'
        f'<div class="v">{value}</div>'
        f'<div class="sub">{esc(sub)}</div></div>'
        for label, value, sub in cells
    )

    return f"""
    <div class="pred">
      <div class="pred-head">
        <div class="t">{esc(red_name)} <span class="sep">vs</span> {esc(blue_name)}</div>
        <div class="ufc-badge"><span class="dot"></span>Model output</div>
      </div>

      <div class="pred-split">
        <div class="pred-side l{'' if red_wins else ' dim'}">
          <div class="who">{esc(red_name)}</div>
          <div class="pct">{left_pct}</div>
        </div>
        <div class="mid">Win probability</div>
        <div class="pred-side r{' dim' if red_wins else ''}">
          <div class="who">{esc(blue_name)}</div>
          <div class="pct">{right_pct}</div>
        </div>
      </div>

      <div class="pbar">
        <div class="seg l" style="width:{prob_red * 100:.4f}%"></div>
        <div class="gap"></div>
        <div class="seg r" style="width:{prob_blue * 100:.4f}%"></div>
      </div>

      <div class="pred-foot">{cell_html}</div>
    </div>
    """


# ---------------------------------------------------------------------------
# Market vs model
# ---------------------------------------------------------------------------

def market_vs_model(red_name: str, blue_name: str,
                    red_odds: float, blue_odds: float,
                    red_implied: Optional[float], blue_implied: Optional[float],
                    red_novig: Optional[float], blue_novig: Optional[float],
                    margin: Optional[float],
                    prob_red: float, prob_blue: float) -> str:
    """Compare the book's implied probabilities against the model's."""
    if red_novig is None or blue_novig is None:
        return note(
            "<strong>Market comparison unavailable.</strong> Enter non-zero moneyline "
            "odds for both fighters to compare the book's implied probability "
            "against the model."
        )

    red_edge = prob_red - red_novig
    blue_edge = prob_blue - blue_novig

    def row(corner: str, name: str, odds: float,
            implied: Optional[float], novig: Optional[float], edge: float) -> str:
        edge_cls = "edge pos" if edge > 0 else "edge neg"
        return f"""
        <div class="mvm-row">
          <div class="c name"><span class="pip {corner}"></span>{esc(name)}</div>
          <div class="c">{esc(fmt_odds(odds))}</div>
          <div class="c">{esc(fmt_pct(implied, 1))}</div>
          <div class="c">{esc(fmt_pct(novig, 1))}</div>
          <div class="c model">{esc(fmt_pct(prob_red if corner == "red" else prob_blue, 1))}</div>
          <div class="c {edge_cls}">{esc(fmt_signed_pct(edge))}</div>
        </div>
        """

    leader, leader_edge = (
        (red_name, red_edge) if red_edge >= blue_edge else (blue_name, blue_edge)
    )
    margin_text = f"{margin * 100:.1f}%" if margin is not None else NA

    verdict = (
        f"The model is <strong>{esc(fmt_signed_pct(leader_edge))}</strong> more confident in "
        f"<strong>{esc(leader)}</strong> than the no-vig market."
        if leader_edge > 0
        else "The model does not disagree with the market on either fighter."
    )

    return f"""
    <div class="mvm">
      <div class="mvm-row head">
        <div class="c first">Fighter</div>
        <div class="c">Odds</div>
        <div class="c">Implied</div>
        <div class="c">No-vig</div>
        <div class="c">Model</div>
        <div class="c">Edge</div>
      </div>
      {row("red", red_name, red_odds, red_implied, red_novig, red_edge)}
      {row("blue", blue_name, blue_odds, blue_implied, blue_novig, blue_edge)}
      <div class="note">
        {verdict} &nbsp;·&nbsp; Book margin (vig): <strong>{esc(margin_text)}</strong>.
        <br/>
        <em>Implied</em> converts the American odds directly; <em>no-vig</em> removes the
        book's margin so the two probabilities sum to 100% and are comparable with the
        model. Edge is a difference of opinion between two estimates - it is not a
        profitability guarantee.
      </div>
    </div>
    """


# ---------------------------------------------------------------------------
# Fighter comparison
# ---------------------------------------------------------------------------

# direction: "high" = larger is better, "low" = smaller is better,
# "neutral" = no fair winner (physical traits are situational in MMA).
_COMPARISON_METRICS = [
    ("age", "Age", lambda v: fmt(v, "{:.0f}"), "neutral"),
    ("height", "Height", lambda v: fmt(v, "{:.0f}", " cm"), "neutral"),
    ("reach", "Reach", lambda v: fmt(v, "{:.0f}", " cm"), "neutral"),
    ("wins", "Wins", lambda v: fmt(v, "{:.0f}"), "high"),
    ("losses", "Losses", lambda v: fmt(v, "{:.0f}"), "low"),
    ("win_streak", "Win streak", lambda v: fmt(v, "{:.0f}"), "high"),
    ("longest_streak", "Longest streak", lambda v: fmt(v, "{:.0f}"), "high"),
    ("sig_str", "Strikes / min", lambda v: fmt(v, "{:.2f}"), "high"),
    ("sig_str_pct", "Strike accuracy", lambda v: fmt_pct(v), "high"),
    ("td", "Takedowns / fight", lambda v: fmt(v, "{:.2f}"), "high"),
    ("td_pct", "Takedown accuracy", lambda v: fmt_pct(v), "high"),
]


def _bar_widths(left, right) -> tuple[float, float]:
    """Scale two values against the larger of the pair."""
    if is_missing(left) or is_missing(right):
        return 0.0, 0.0
    left, right = abs(float(left)), abs(float(right))
    peak = max(left, right)
    if peak <= 0:
        return 0.0, 0.0
    return left / peak * 100.0, right / peak * 100.0


def comparison(red_name: str, blue_name: str, red_stats: dict, blue_stats: dict) -> str:
    rows = []
    for key, label, formatter, direction in _COMPARISON_METRICS:
        left_raw, right_raw = red_stats.get(key), blue_stats.get(key)
        left_text, right_text = formatter(left_raw), formatter(right_raw)

        left_cls, right_cls = ["v", "l"], ["v", "r"]
        if left_text == NA:
            left_cls.append("na")
        if right_text == NA:
            right_cls.append("na")

        # Only highlight an advantage where "more" (or "less") is unambiguously better.
        if direction != "neutral" and not is_missing(left_raw) and not is_missing(right_raw):
            left_val, right_val = float(left_raw), float(right_raw)
            if left_val != right_val:
                left_better = left_val > right_val if direction == "high" else left_val < right_val
                (left_cls if left_better else right_cls).append("win")

        left_width, right_width = _bar_widths(left_raw, right_raw)
        tone = " neutral" if direction == "neutral" else ""

        rows.append(f"""
        <div class="cmp-row">
          <div class="cmp-vals">
            <div class="{' '.join(left_cls)}">{esc(left_text)}</div>
            <div class="k">{esc(label)}</div>
            <div class="{' '.join(right_cls)}">{esc(right_text)}</div>
          </div>
          <div class="cmp-bars">
            <div class="track l"><div class="fill l{tone}" style="width:{left_width:.2f}%"></div></div>
            <div class="spacer"></div>
            <div class="track r"><div class="fill r{tone}" style="width:{right_width:.2f}%"></div></div>
          </div>
        </div>
        """)

    return f"""
    <div class="cmp">
      <div class="cmp-head">
        <div class="n l">{esc(red_name)}</div>
        <div class="k"></div>
        <div class="n r">{esc(blue_name)}</div>
      </div>
      {''.join(rows)}
    </div>
    """


# ---------------------------------------------------------------------------
# Secondary breakdown (round / method)
# ---------------------------------------------------------------------------

def distribution_card(title: str, items: list[tuple[str, float]],
                      footnote: Optional[str] = None) -> str:
    """A labelled probability distribution, highest value emphasised."""
    if not items:
        return ""
    peak = max(probability for _, probability in items)

    body = "".join(
        f"""
        <div class="brk-item{' top-pick' if probability >= peak else ''}">
          <div class="top">
            <span class="lab">{esc(label)}</span>
            <span class="num">{probability * 100:.1f}%</span>
          </div>
          <div class="track"><div class="fill" style="width:{probability * 100:.2f}%"></div></div>
        </div>
        """
        for label, probability in items
    )

    note_html = f'<div class="brk-note">{esc(footnote)}</div>' if footnote else ""
    return (
        f'<div class="brk-card"><div class="title">{esc(title)}</div>'
        f"{body}{note_html}</div>"
    )


def breakdown(cards: list[str]) -> str:
    return f'<div class="brk">{"".join(cards)}</div>'


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

def footer(snapshot: Optional[str] = None) -> str:
    left = "Statistical estimates from models trained on historical UFC data."
    right = f"Fighter stats snapshot: {esc(snapshot)}" if snapshot else "Not betting advice."
    return f'<div class="ufc-footer"><div>{left}</div><div>{right}</div></div>'
