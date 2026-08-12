"""Design system for the UFC Analytics dashboard.

Everything visual lives here: tokens, Streamlit chrome overrides, and component
styles. Nothing in this module touches data or the model.
"""

# ---------------------------------------------------------------------------
# Tokens (kept in Python too, so charts/inline styles can reuse them)
# ---------------------------------------------------------------------------

BG = "#070A12"
SURFACE = "#0E1320"
SURFACE_2 = "#141927"
ELEVATED = "#181E2D"
BORDER = "rgba(255,255,255,0.08)"
TEXT = "#F5F7FA"
MUTED = "#8B93A7"
RED = "#EF4444"
BLUE = "#3B82F6"
GOLD = "#F5B942"

MAX_WIDTH = 1360


CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

/* ===================================================================
   1. TOKENS
   =================================================================== */
:root {{
    --bg:            {BG};
    --surface:       {SURFACE};
    --surface-2:     {SURFACE_2};
    --elevated:      {ELEVATED};
    --border:        {BORDER};
    --border-strong: rgba(255,255,255,0.14);
    --text:          {TEXT};
    --muted:         {MUTED};
    --red:           {RED};
    --blue:          {BLUE};
    --gold:          {GOLD};

    --font-display: 'Barlow Condensed', 'Helvetica Neue', system-ui, sans-serif;
    --font-body: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;

    --radius: 14px;
    --radius-sm: 9px;
    --maxw: {MAX_WIDTH}px;
}}

/* ===================================================================
   2. STREAMLIT CHROME
   Keep these overrides shallow + attribute-based; Streamlit's generated
   class names change between releases, data-testid values are stable.
   =================================================================== */

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-body);
}}

/* Centered application container */
[data-testid="stMainBlockContainer"] {{
    max-width: var(--maxw);
    padding: 0.5rem 2rem 5rem 2rem;
}}

/* Strip default chrome: floating toolbar, decoration bar, footer */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu, footer {{ display: none !important; }}

[data-testid="stHeader"] {{ background: transparent; height: 0; }}

/* Tighten Streamlit's default vertical rhythm so our own spacing wins */
[data-testid="stVerticalBlock"] {{ gap: 0.6rem; }}
[data-testid="stElementContainer"]:has(> .ufc-flush) {{ margin: 0; }}

/* --- Inputs ------------------------------------------------------- */
/* One rule for every widget label keeps selects, number inputs and the
   segmented controls typographically identical. */
[data-testid="stWidgetLabel"] p {{
    font-family: var(--font-body);
    font-size: 0.66rem !important;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted) !important;
}}

[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stNumberInput"] div[data-baseweb="input"] {{
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text);
    transition: border-color .18s ease, box-shadow .18s ease;
    min-height: 46px;
}}

[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
[data-testid="stNumberInput"] div[data-baseweb="input"]:hover {{
    border-color: var(--border-strong);
}}

[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within,
[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {{
    border-color: rgba(245,185,66,0.55);
    box-shadow: 0 0 0 3px rgba(245,185,66,0.10);
}}

/* Corner-tinted selects, driven by a wrapper class */
.ufc-pick-red [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
    border-left: 3px solid var(--red);
}}
.ufc-pick-blue [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
    border-left: 3px solid var(--blue);
}}

/* Dropdown menu */
div[data-baseweb="popover"] ul {{
    background: var(--elevated) !important;
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-sm);
}}
div[data-baseweb="popover"] li {{ font-family: var(--font-body); font-size: 0.9rem; }}
div[data-baseweb="popover"] li:hover {{ background: rgba(255,255,255,0.06) !important; }}

/* Number input steppers: quiet them down */
[data-testid="stNumberInput"] button {{
    background: transparent;
    border: none;
    color: var(--muted);
}}
[data-testid="stNumberInput"] button:hover {{ color: var(--text); background: rgba(255,255,255,0.05); }}

/* --- Segmented control (mode toggle) ------------------------------ */
[data-testid="stButtonGroup"] > div {{
    display: inline-flex;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 3px;
    gap: 2px;
}}
button[data-variant="segmented_control"] {{
    border: none !important;
    background: transparent !important;
    border-radius: 999px !important;
    color: var(--muted) !important;
    font-family: var(--font-body) !important;
    font-size: 0.74rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.44rem 1.4rem !important;
    box-shadow: none !important;
    transition: color .18s ease, background .18s ease;
}}
button[data-variant="segmented_control"]:hover {{ color: var(--text) !important; }}
button[data-variant="segmented_control"][data-selected="true"] {{
    background: var(--elevated) !important;
    color: var(--text) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.45) !important;
}}

/* --- Primary CTA -------------------------------------------------- */
[data-testid="stButton"] button {{
    background: var(--red);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0.85rem 2rem;
    font-family: var(--font-body);
    font-weight: 700;
    font-size: 0.82rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    width: 100%;
    transition: transform .18s ease, box-shadow .18s ease, filter .18s ease;
    box-shadow: 0 2px 10px rgba(239,68,68,0.22);
}}
[data-testid="stButton"] button:hover {{
    filter: brightness(1.1);
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(239,68,68,0.28);
}}
[data-testid="stButton"] button:active {{ transform: translateY(0); }}
[data-testid="stButton"] button:focus {{ box-shadow: 0 0 0 3px rgba(239,68,68,0.35); }}

/* --- Expander ----------------------------------------------------- */
[data-testid="stExpander"] details {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
}}
[data-testid="stExpander"] summary {{
    font-family: var(--font-body);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
}}
[data-testid="stExpander"] summary:hover {{ color: var(--text); }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: var(--bg); }}
::-webkit-scrollbar-thumb {{ background: #232A3D; border-radius: 6px; }}
::-webkit-scrollbar-thumb:hover {{ background: #303854; }}


/* ===================================================================
   3. PRIMITIVES
   =================================================================== */

.ufc-label {{
    font-family: var(--font-body);
    font-size: 0.66rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
}}

.ufc-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
}}

.ufc-section {{
    display: flex;
    align-items: center;
    gap: 0.9rem;
    margin: 2.6rem 0 1rem 0;
}}
.ufc-section h2 {{
    font-family: var(--font-display);
    font-size: 1.28rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text);
    margin: 0;
    white-space: nowrap;
}}
.ufc-section .rule {{ flex: 1; height: 1px; background: var(--border); }}


/* ===================================================================
   4. NAVIGATION
   =================================================================== */

.ufc-nav {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.85rem 0.2rem 0.95rem 0.2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.6rem;
    flex-wrap: wrap;
}}
.ufc-nav .brand {{ display: flex; align-items: center; gap: 0.7rem; }}
.ufc-nav .bolt {{
    width: 30px; height: 30px; border-radius: 8px;
    background: linear-gradient(140deg, var(--red), #B91C1C);
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
}}
.ufc-nav .brand-name {{
    font-family: var(--font-display);
    font-size: 1.16rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--text); line-height: 1.05;
}}
.ufc-nav .brand-sub {{
    font-size: 0.62rem; font-weight: 500; letter-spacing: 0.2em;
    text-transform: uppercase; color: var(--muted); line-height: 1.5;
}}
.ufc-nav .meta {{ display: flex; align-items: center; gap: 1.4rem; flex-wrap: wrap; }}
.ufc-nav .stat {{ text-align: right; }}
.ufc-nav .stat .v {{
    font-family: var(--font-display); font-size: 1rem; font-weight: 600;
    color: var(--text); line-height: 1.1;
}}
.ufc-nav .stat .k {{
    font-size: 0.56rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted);
}}
.ufc-badge {{
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.32rem 0.7rem; border-radius: 999px;
    background: rgba(245,185,66,0.10);
    border: 1px solid rgba(245,185,66,0.30);
    color: var(--gold);
    font-size: 0.6rem; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase;
}}
.ufc-badge .dot {{
    width: 5px; height: 5px; border-radius: 50%; background: var(--gold);
}}


/* ===================================================================
   5. MATCHUP HERO
   =================================================================== */

.ufc-hero {{
    position: relative;
    background:
        radial-gradient(760px 300px at 8% 0%,  rgba(239,68,68,0.11), transparent 62%),
        radial-gradient(760px 300px at 92% 0%, rgba(59,130,246,0.11), transparent 62%),
        var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 2.2rem 2rem 1.6rem 2rem;
    overflow: hidden;
    animation: ufc-rise .42s cubic-bezier(.22,.9,.3,1) both;
}}

/* Inner width is tighter than the card so the two fighters frame the VS mark
   instead of drifting to opposite edges of a wide monitor. */
.ufc-hero-grid, .tape {{
    max-width: 1000px;
    margin-left: auto;
    margin-right: auto;
}}

.ufc-hero-grid {{
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 1.6rem;
}}

/* --- fighter side --- */
.fighter {{ display: flex; flex-direction: column; align-items: center; text-align: center; }}

.fighter .corner {{
    display: inline-flex; align-items: center; gap: 0.45rem;
    font-size: 0.6rem; font-weight: 700; letter-spacing: 0.2em;
    text-transform: uppercase; margin-bottom: 1rem;
}}
.fighter .corner .pip {{ width: 6px; height: 6px; border-radius: 50%; }}
.fighter.red  .corner {{ color: var(--red); }}
.fighter.blue .corner {{ color: var(--blue); }}
.fighter.red  .corner .pip {{ background: var(--red); box-shadow: 0 0 8px rgba(239,68,68,0.7); }}
.fighter.blue .corner .pip {{ background: var(--blue); box-shadow: 0 0 8px rgba(59,130,246,0.7); }}

.fighter .portrait {{
    width: 172px; height: 208px;
    border-radius: 14px;
    overflow: hidden;
    background: var(--surface-2);
    border: 1px solid var(--border);
    display: flex; align-items: flex-end; justify-content: center;
    position: relative;
    transition: border-color .25s ease, transform .25s ease;
}}
.fighter .portrait img {{
    width: 100%; height: 100%; object-fit: cover; object-position: top center;
    display: block;
}}
.fighter.red  .portrait {{ border-color: rgba(239,68,68,0.34); background:
    radial-gradient(120% 90% at 50% 0%, rgba(239,68,68,0.16), transparent 70%), var(--surface-2); }}
.fighter.blue .portrait {{ border-color: rgba(59,130,246,0.34); background:
    radial-gradient(120% 90% at 50% 0%, rgba(59,130,246,0.16), transparent 70%), var(--surface-2); }}
.fighter .portrait:hover {{ transform: translateY(-3px); }}

/* Neutral silhouette placeholder (no emoji, no external asset) */
.fighter .silhouette {{
    width: 100%; height: 100%;
    display: flex; flex-direction: column;
    align-items: center; justify-content: flex-end;
    gap: 9px;
}}
.fighter .sil-head {{
    width: 50px; height: 50px; border-radius: 50%;
    background: #29314A; flex-shrink: 0;
}}
.fighter .sil-body {{
    width: 116px; height: 84px;
    border-radius: 58px 58px 0 0;
    background: #29314A;
}}
.fighter.red  .sil-head, .fighter.red  .sil-body {{ background: #33283A; }}
.fighter.blue .sil-head, .fighter.blue .sil-body {{ background: #25304A; }}

.fighter .name {{
    font-family: var(--font-display);
    font-weight: 700;
    text-transform: uppercase;
    line-height: 0.94;
    letter-spacing: 0.01em;
    color: var(--text);
    margin-top: 1.1rem;
}}
.fighter .name .first {{ display: block; font-size: 1.28rem; color: var(--muted); font-weight: 500; }}
.fighter .name .last  {{ display: block; font-size: 2.35rem; }}

.fighter .record {{
    margin-top: 0.65rem;
    display: inline-flex; align-items: center; gap: 0.55rem;
    font-family: var(--font-display);
    font-size: 1.02rem; font-weight: 600; letter-spacing: 0.06em;
    color: var(--text);
}}
.fighter .record .tag {{
    font-family: var(--font-body);
    font-size: 0.55rem; font-weight: 600; letter-spacing: 0.16em;
    color: var(--muted); text-transform: uppercase;
}}
.fighter .division {{
    margin-top: 0.5rem;
    font-size: 0.63rem; font-weight: 600; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--muted);
}}

/* --- VS column --- */
.vs {{ display: flex; flex-direction: column; align-items: center; gap: 0.85rem; }}
.vs .rail {{ width: 1px; flex: 1; min-height: 34px; background: linear-gradient(var(--border), transparent); }}
.vs .rail.bottom {{ background: linear-gradient(transparent, var(--border)); }}
.vs .mark {{
    font-family: var(--font-display);
    font-size: 2.5rem; font-weight: 700; letter-spacing: 0.04em;
    color: var(--text);
    width: 78px; height: 78px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    background: var(--elevated);
    border: 1px solid var(--border-strong);
    box-shadow: 0 8px 26px rgba(0,0,0,0.5);
    flex-shrink: 0;
}}
.vs .bout {{
    font-size: 0.58rem; font-weight: 600; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--muted); text-align: center;
    max-width: 150px; line-height: 1.6;
}}
.vs .bout span {{ display: block; white-space: nowrap; }}
.vs .bout .rounds {{ color: #6E7689; letter-spacing: 0.12em; }}


/* ===================================================================
   6. TALE OF THE TAPE
   =================================================================== */

.tape {{
    margin-top: 1.8rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
}}
.tape-row {{
    display: grid;
    grid-template-columns: 1fr 168px 1fr;
    align-items: center;
    padding: 0.62rem 0;
}}
.tape-row + .tape-row {{ border-top: 1px solid rgba(255,255,255,0.045); }}
.tape-row .v {{
    font-family: var(--font-display);
    font-size: 1.42rem; font-weight: 600; color: var(--text);
    letter-spacing: 0.02em;
}}
.tape-row .v.left  {{ text-align: right; padding-right: 1.4rem; }}
.tape-row .v.right {{ text-align: left;  padding-left: 1.4rem; }}
.tape-row .v.na {{ color: var(--muted); font-size: 1.05rem; }}
.tape-row .k {{
    text-align: center;
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--muted);
}}
/* subtle edge highlight — only where "higher" is genuinely an advantage */
.tape-row .v.edge {{ color: var(--gold); }}


/* ===================================================================
   7. MODEL PREDICTION
   =================================================================== */

.pred {{
    background:
        radial-gradient(900px 260px at 50% 0%, rgba(245,185,66,0.07), transparent 68%),
        var(--surface);
    border: 1px solid rgba(245,185,66,0.22);
    border-radius: 18px;
    padding: 2rem 2rem 1.8rem 2rem;
    animation: ufc-rise .45s cubic-bezier(.22,.9,.3,1) both;
}}

.pred-head {{
    display: flex; align-items: center; justify-content: space-between;
    gap: 1rem; margin-bottom: 1.7rem; flex-wrap: wrap;
}}
.pred-head .t {{
    font-family: var(--font-display);
    font-size: 1.2rem; font-weight: 600; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--text);
}}
.pred-head .t .sep {{ color: var(--muted); font-weight: 500; margin: 0 0.2rem; }}

.pred-split {{
    display: grid; grid-template-columns: 1fr auto 1fr;
    align-items: end; gap: 1rem; margin-bottom: 1.1rem;
}}
.pred-side {{ min-width: 0; }}
.pred-side.r {{ text-align: right; }}
.pred-side .who {{
    font-family: var(--font-display);
    font-size: 1.02rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--muted);
    margin-bottom: 0.3rem;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.pred-side .pct {{
    font-family: var(--font-display);
    font-size: 3.5rem; font-weight: 700; line-height: 0.92;
    animation: ufc-fade-up .5s .12s cubic-bezier(.22,.9,.3,1) both;
}}
.pred-side.l .pct {{ color: var(--red); }}
.pred-side.r .pct {{ color: var(--blue); }}
.pred-side.dim .pct {{ opacity: 0.5; }}
.pred-split .mid {{
    font-size: 0.56rem; letter-spacing: 0.18em; text-transform: uppercase;
    color: var(--muted); padding-bottom: 0.7rem;
}}

/* split probability bar */
.pbar {{
    display: flex; height: 13px; border-radius: 7px; overflow: hidden;
    background: var(--surface-2); border: 1px solid var(--border);
}}
.pbar .seg {{ height: 100%; animation: ufc-grow .6s cubic-bezier(.22,.9,.3,1) both; }}
.pbar .seg.l {{ background: linear-gradient(90deg, #B91C1C, var(--red)); }}
.pbar .seg.r {{ background: linear-gradient(90deg, var(--blue), #1D4ED8); }}
.pbar .gap {{ width: 2px; background: var(--bg); flex-shrink: 0; }}

.pred-foot {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 1px; margin-top: 1.7rem;
    background: var(--border); border: 1px solid var(--border);
    border-radius: var(--radius); overflow: hidden;
}}
.pred-foot .cell {{ background: var(--surface); padding: 1.05rem 1.2rem; }}
.pred-foot .k {{
    font-size: 0.58rem; font-weight: 600; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--muted); margin-bottom: 0.45rem;
}}
.pred-foot .v {{
    font-family: var(--font-display);
    font-size: 1.5rem; font-weight: 600; color: var(--text); line-height: 1.12;
}}
.pred-foot .v.red  {{ color: var(--red); }}
.pred-foot .v.blue {{ color: var(--blue); }}
.pred-foot .sub {{ font-size: 0.68rem; color: var(--muted); margin-top: 0.2rem; }}

/* The pick is the single most important output - it reads at the same weight
   as the other headline values, not as a small chip. */
.pick {{
    font-family: var(--font-display);
    font-size: 1.5rem; font-weight: 700; letter-spacing: 0.03em;
    text-transform: uppercase; line-height: 1.12;
}}
.pick.red  {{ color: var(--red); }}
.pick.blue {{ color: var(--blue); }}

/* The winning cell gets a restrained tint rather than a glow. */
.pred-foot .cell:first-child {{ position: relative; }}
.pred-foot .cell:first-child::before {{
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 2px;
    background: currentColor; opacity: 0.5;
}}
.pred-foot .cell:first-child:has(.pick.red)::before  {{ background: var(--red); }}
.pred-foot .cell:first-child:has(.pick.blue)::before {{ background: var(--blue); }}


/* ===================================================================
   8. MARKET VS MODEL
   =================================================================== */

.mvm {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); overflow: hidden;
}}
.mvm-row {{
    display: grid;
    grid-template-columns: minmax(0,1.7fr) repeat(5, minmax(0,1fr));
    align-items: center;
}}
.mvm-row .c {{ padding: 1rem 1.2rem; text-align: right; }}
.mvm-row .c.name {{
    text-align: left;
    font-family: var(--font-display); font-size: 1rem; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase; color: var(--text);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.mvm-row:not(.head) .c {{
    font-family: var(--font-display); font-size: 1.14rem; font-weight: 600; color: var(--text);
}}
.mvm-row.head {{ border-bottom: 1px solid var(--border); }}
.mvm-row.head .c.first {{ text-align: left; }}
.mvm-row.head .c {{
    padding: 0.85rem 1.2rem;
    font-family: var(--font-body);
    font-size: 0.57rem; font-weight: 600; letter-spacing: 0.15em;
    text-transform: uppercase; color: var(--muted); white-space: nowrap;
}}
.mvm-row + .mvm-row:not(.head) {{ border-top: 1px solid rgba(255,255,255,0.045); }}
.mvm-row .c .pip {{
    display: inline-block; width: 6px; height: 6px; border-radius: 50%;
    margin-right: 0.6rem; vertical-align: middle;
}}
.mvm-row .c .pip.red  {{ background: var(--red); }}
.mvm-row .c .pip.blue {{ background: var(--blue); }}
.mvm-row .c.model {{ color: var(--gold) !important; }}
.mvm-row .c.edge.pos {{ color: #4ADE80 !important; }}
.mvm-row .c.edge.neg {{ color: var(--muted) !important; }}
.mvm .note {{
    padding: 0.9rem 1.2rem; border-top: 1px solid var(--border);
    font-size: 0.72rem; color: var(--muted); line-height: 1.65; background: rgba(0,0,0,0.16);
}}
.mvm .note strong {{ color: var(--text); }}
.mvm .note em {{ color: #B6BECE; font-style: normal; font-weight: 600; }}


/* ===================================================================
   9. FIGHTER COMPARISON
   =================================================================== */

.cmp {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 0.4rem 1.5rem 1rem 1.5rem;
}}
/* Match the hero's inner width so the two sections line up. */
.cmp-head, .cmp-row {{ max-width: 1000px; margin-left: auto; margin-right: auto; }}
.cmp-head {{
    display: grid; grid-template-columns: 1fr 190px 1fr;
    align-items: center; padding: 1rem 0 0.9rem 0;
    border-bottom: 1px solid var(--border);
}}
.cmp-head .n {{
    font-family: var(--font-display); font-size: 1rem; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.cmp-head .n.l {{ text-align: right; color: var(--red); }}
.cmp-head .n.r {{ text-align: left;  color: var(--blue); }}

.cmp-row {{ padding: 0.95rem 0; }}
.cmp-row + .cmp-row {{ border-top: 1px solid rgba(255,255,255,0.045); }}
.cmp-vals {{
    display: grid; grid-template-columns: 1fr 190px 1fr;
    align-items: center; margin-bottom: 0.5rem;
}}
.cmp-vals .v {{
    font-family: var(--font-display); font-size: 1.34rem; font-weight: 600; color: var(--text);
}}
.cmp-vals .v.l {{ text-align: right; padding-right: 1.2rem; }}
.cmp-vals .v.r {{ text-align: left;  padding-left: 1.2rem; }}
.cmp-vals .v.na {{ color: var(--muted); font-size: 1rem; }}
.cmp-vals .v.win {{ color: var(--gold); }}
.cmp-vals .k {{
    text-align: center; font-size: 0.59rem; font-weight: 600;
    letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted);
}}

/* paired bars growing outward from the centre - deliberately short so they
   read as a supporting cue rather than the main content */
.cmp-bars {{ display: grid; grid-template-columns: 1fr 190px 1fr; align-items: center; }}
/* width:100% is required - a grid item sized only by max-width shrink-wraps
   to its percentage-width child, collapsing the track to zero. */
.cmp-bars .track {{
    height: 4px; width: 100%; max-width: 250px;
    background: rgba(255,255,255,0.05); border-radius: 3px;
    overflow: hidden; display: flex;
}}
.cmp-bars .track.l {{ justify-content: flex-end; margin-left: auto; margin-right: 1.2rem; }}
.cmp-bars .track.r {{ justify-content: flex-start; margin-right: auto; margin-left: 1.2rem; }}
.cmp-bars .fill {{ height: 100%; border-radius: 3px; animation: ufc-grow .55s cubic-bezier(.22,.9,.3,1) both; }}
.cmp-bars .fill.l {{ background: rgba(239,68,68,0.75); }}
.cmp-bars .fill.r {{ background: rgba(59,130,246,0.75); }}
/* Height / reach / age have no fair "winner", so their bars stay neutral. */
.cmp-bars .fill.neutral {{ background: rgba(255,255,255,0.16); }}
.cmp-bars .spacer {{ }}


/* ===================================================================
   10. SECONDARY BREAKDOWN (round / method)
   =================================================================== */

.brk {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.1rem;
}}
.brk-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.3rem 1.4rem;
}}
.brk-card .title {{
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--muted); margin-bottom: 1.1rem;
}}
.brk-item {{ margin-bottom: 0.85rem; }}
.brk-item:last-child {{ margin-bottom: 0; }}
.brk-item .top {{
    display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.36rem;
}}
.brk-item .lab {{ font-size: 0.8rem; color: var(--muted); font-weight: 500; }}
.brk-item.top-pick .lab {{ color: var(--text); font-weight: 600; }}
.brk-item .num {{ font-family: var(--font-display); font-size: 1rem; font-weight: 600; color: var(--muted); }}
.brk-item.top-pick .num {{ color: var(--gold); }}
.brk-note {{
    margin-top: 1.1rem; padding-top: 0.85rem;
    border-top: 1px solid var(--border);
    font-size: 0.7rem; line-height: 1.6; color: var(--muted);
}}
.brk-item .track {{ height: 5px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden; }}
.brk-item .fill {{
    height: 100%; border-radius: 3px; background: #2E3852;
    animation: ufc-grow .55s cubic-bezier(.22,.9,.3,1) both;
}}
.brk-item.top-pick .fill {{ background: var(--gold); }}


/* ===================================================================
   11. NOTICES / FOOTER
   =================================================================== */

.ufc-note {{
    display: flex; gap: 0.8rem; align-items: flex-start;
    background: rgba(245,185,66,0.06);
    border: 1px solid rgba(245,185,66,0.24);
    border-left: 3px solid var(--gold);
    border-radius: var(--radius-sm);
    padding: 0.9rem 1.1rem;
    font-size: 0.82rem; color: #E4DCC8; line-height: 1.6;
}}
.ufc-note.err {{
    background: rgba(239,68,68,0.07);
    border-color: rgba(239,68,68,0.3);
    border-left-color: var(--red);
    color: #F2D4D4;
}}
.ufc-note strong {{ color: var(--text); font-weight: 600; }}

.ufc-empty {{
    text-align: center; padding: 3.4rem 1rem;
    border: 1px dashed var(--border); border-radius: var(--radius);
    color: var(--muted); font-size: 0.86rem; letter-spacing: 0.04em;
}}

.ufc-footer {{
    margin-top: 3.5rem; padding-top: 1.4rem;
    border-top: 1px solid var(--border);
    display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
    font-size: 0.68rem; color: var(--muted); letter-spacing: 0.06em;
}}


/* ===================================================================
   12. ANIMATION
   =================================================================== */

@keyframes ufc-rise {{
    from {{ opacity: 0; transform: translateY(14px); }}
    to   {{ opacity: 1; transform: none; }}
}}
@keyframes ufc-fade-up {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: none; }}
}}
@keyframes ufc-grow {{
    from {{ width: 0 !important; }}
}}

@media (prefers-reduced-motion: reduce) {{
    * {{ animation: none !important; transition: none !important; }}
}}


/* ===================================================================
   13. RESPONSIVE
   =================================================================== */

@media (max-width: 900px) {{
    [data-testid="stMainBlockContainer"] {{ padding: 0.5rem 1rem 4rem 1rem; }}

    /* Hero + tape + comparison all collapse to a stacked layout */
    .ufc-hero-grid {{ grid-template-columns: 1fr; gap: 0.4rem; }}
    .vs {{ flex-direction: row; gap: 1rem; padding: 0.5rem 0; }}
    .vs .rail {{ height: 1px; width: auto; flex: 1; min-height: 0;
                 background: linear-gradient(90deg, transparent, var(--border)); }}
    .vs .rail.bottom {{ background: linear-gradient(90deg, var(--border), transparent); }}
    .vs .mark {{ width: 58px; height: 58px; font-size: 1.8rem; }}
    .vs .bout {{ display: none; }}

    .fighter .portrait {{ width: 140px; height: 172px; }}
    .fighter .name .last {{ font-size: 1.95rem; }}

    .tape-row, .cmp-vals, .cmp-bars, .cmp-head {{ grid-template-columns: 1fr 108px 1fr; }}
    .tape-row .v, .cmp-vals .v {{ font-size: 1.08rem; }}
    .tape-row .v.left, .cmp-vals .v.l {{ padding-right: 0.6rem; }}
    .tape-row .v.right, .cmp-vals .v.r {{ padding-left: 0.6rem; }}
    .cmp-bars .track.l {{ margin-right: 0.6rem; }}
    .cmp-bars .track.r {{ margin-left: 0.6rem; }}
    .tape-row .k, .cmp-vals .k {{ font-size: 0.52rem; letter-spacing: 0.1em; }}

    .pred {{ padding: 1.4rem 1.1rem; }}
    .pred-side .pct {{ font-size: 2.4rem; }}
    /* Let names wrap instead of truncating - there's room for two lines. */
    .pred-side .who {{ font-size: 0.8rem; white-space: normal; overflow: visible; }}
    .pred-split .mid {{ display: none; }}
    .pred-head .t {{ font-size: 1rem; }}
    .ufc-hero {{ padding: 1.5rem 1.1rem; }}

    /* Compact header: one row of stats, no wrapping to three lines. */
    .ufc-nav {{ padding: 0.7rem 0 0.75rem 0; margin-bottom: 1.1rem; gap: 0.6rem; }}
    .ufc-nav .meta {{ gap: 0.9rem; width: 100%; justify-content: space-between; }}
    .ufc-nav .brand-name {{ font-size: 1rem; }}
    .ufc-nav .brand-sub {{ font-size: 0.55rem; }}
    .ufc-nav .stat .v {{ font-size: 0.86rem; }}
    .ufc-nav .stat .k {{ font-size: 0.5rem; letter-spacing: 0.1em; }}
    .ufc-badge {{ font-size: 0.54rem; padding: 0.28rem 0.6rem; }}

    /* Drop the raw "implied" column on narrow screens; no-vig is the one that
       actually compares against the model. */
    .mvm-row {{ grid-template-columns: minmax(0,1.4fr) repeat(4, minmax(0,1fr)); }}
    .mvm-row .c:nth-child(3) {{ display: none; }}
    .mvm-row .c {{ padding: 0.7rem 0.5rem; font-size: 0.92rem !important; }}
    .mvm-row .c.name {{ font-size: 0.8rem; }}
    .mvm-row.head .c {{ font-size: 0.5rem; letter-spacing: 0.08em; padding: 0.7rem 0.5rem; }}

    .brk {{ grid-template-columns: 1fr; }}
    .pred-foot {{ grid-template-columns: 1fr; }}
}}
</style>
"""
