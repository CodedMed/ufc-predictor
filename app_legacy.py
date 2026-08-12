import streamlit as st
import pandas as pd
import joblib
import requests
import json
import plotly.graph_objects as go

# Load original models
model = joblib.load('model.pkl')
features = joblib.load('features.pkl')
fighter_db = joblib.load('fighter_db.pkl')

# Load enhanced models
try:
    outcome_model = joblib.load('models/outcome_model.pkl')
    round_model = joblib.load('models/round_model.pkl')
    method_model = joblib.load('models/method_model.pkl')
    with open('models/metadata.json') as f:
        metadata = json.load(f)
    enhanced_mode = True
except:
    enhanced_mode = False

# ============ PAGE CONFIG & STYLING ============
st.set_page_config(
    page_title="UFC Analytics Dashboard",
    page_icon="🥊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme and premium styling
st.markdown("""
<style>
    :root {
        --ufc-red: #EF3B39;
        --ufc-blue: #0066CC;
        --dark-bg: #0A0E27;
        --card-bg: #151B2F;
        --accent-gold: #C7954D;
        --text-primary: #FFFFFF;
        --text-secondary: #B0B8CC;
        --border-color: #2A3350;
    }

    * {
        margin: 0;
        padding: 0;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--dark-bg);
        color: var(--text-primary);
    }

    [data-testid="stHeader"] {
        background-color: transparent;
        border-bottom: 2px solid var(--border-color);
    }

    [data-testid="stMain"] {
        background-color: var(--dark-bg);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--card-bg);
        border-right: 2px solid var(--border-color);
    }

    /* Titles and headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    h1 {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, var(--ufc-red), var(--accent-gold));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--ufc-red), #FF5252);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(239, 59, 57, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(239, 59, 57, 0.5);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Radio buttons */
    [data-testid="stRadio"] > label {
        color: var(--text-primary);
        font-weight: 600;
    }

    /* Input fields */
    .stNumberInput input,
    .stSelectbox select,
    .stSlider input {
        background-color: var(--card-bg);
        color: var(--text-primary);
        border: 2px solid var(--border-color);
        border-radius: 8px;
    }

    .stNumberInput input:focus,
    .stSelectbox select:focus {
        border-color: var(--ufc-red);
        box-shadow: 0 0 10px rgba(239, 59, 57, 0.3);
    }

    /* Fighter cards */
    .fighter-card {
        background: linear-gradient(135deg, var(--card-bg), #1a1f36);
        border: 2px solid var(--border-color);
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }

    .fighter-card:hover {
        border-color: var(--ufc-red);
        box-shadow: 0 12px 36px rgba(239, 59, 57, 0.15);
        transform: translateY(-4px);
    }

    .fighter-card.red {
        border-left: 5px solid var(--ufc-red);
    }

    .fighter-card.blue {
        border-left: 5px solid var(--ufc-blue);
    }

    /* Prediction results container */
    .prediction-container {
        background: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: 12px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }

    /* Metrics */
    .metric-box {
        background: linear-gradient(135deg, var(--card-bg), #1a1f36);
        border: 2px solid var(--border-color);
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-box:hover {
        border-color: var(--ufc-red);
        box-shadow: 0 8px 20px rgba(239, 59, 57, 0.15);
        transform: translateY(-2px);
    }

    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        color: var(--text-primary);
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }

    .metric-delta {
        color: var(--accent-gold);
        font-size: 0.9rem;
        font-weight: 600;
    }

    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }

    .stat-item {
        background: rgba(239, 59, 57, 0.05);
        border-left: 4px solid var(--ufc-red);
        padding: 1rem;
        border-radius: 6px;
    }

    .stat-label {
        color: var(--text-secondary);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }

    .stat-value {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 700;
    }

    /* Progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--ufc-red), #FF5252);
        border-radius: 4px;
    }

    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        background: var(--card-bg);
    }

    .dataframe {
        background-color: var(--card-bg);
        color: var(--text-primary);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-primary);
        font-weight: 600;
    }

    .streamlit-expanderContent {
        background-color: rgba(21, 27, 47, 0.8);
        border: 2px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 8px 8px;
        color: var(--text-primary);
    }

    /* Dividers */
    hr {
        border-color: var(--border-color);
        margin: 2rem 0;
    }

    /* Caption and text styling */
    .caption-text {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }

    .section-title {
        color: var(--text-primary);
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding-bottom: 1rem;
        border-bottom: 3px solid var(--border-color);
    }

    .red-corner-title {
        color: var(--ufc-red);
    }

    .blue-corner-title {
        color: var(--ufc-blue);
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: var(--dark-bg);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--ufc-red);
    }
</style>
""", unsafe_allow_html=True)

# ============ HELPER FUNCTIONS ============

@st.cache_data(show_spinner=False)
def get_fighter_info(name):
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query", "list": "search", "srsearch": f"{name} UFC fighter",
            "format": "json", "srlimit": 1
        }
        r = requests.get(search_url, params=params, timeout=3).json()
        results = r.get("query", {}).get("search", [])
        if not results:
            return {'image': None, 'summary': None}

        title = results[0]['title']
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
        resp = requests.get(summary_url, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            return {
                'image': data.get('thumbnail', {}).get('source'),
                'summary': data.get('extract')
            }
    except Exception:
        pass
    return {'image': None, 'summary': None}


def get_stats_from_db(name):
    row = fighter_db.loc[name]
    return {
        'height': row['height'], 'reach': row['reach'], 'age': row['age'],
        'win_streak': row['win_streak'], 'longest_streak': row['longest_streak'],
        'wins': row['wins'], 'losses': row['losses'], 'sig_str': row['sig_str'],
        'sig_str_pct': row['sig_str_pct'], 'td': row['td'], 'td_pct': row['td_pct'],
    }


def render_fighter_card(name, stats, info, odds, corner_color):
    """Render a styled fighter card"""
    card_class = "red" if corner_color == "red" else "blue"
    color_label = "🔴 Red Corner" if corner_color == "red" else "🔵 Blue Corner"

    st.markdown(f"""
    <div class="fighter-card {card_class}">
        <div style="margin-bottom: 1.5rem;">
            <h3 style="color: var(--text-primary); margin: 0; font-size: 1.8rem;">{name}</h3>
            <p style="color: var(--text-secondary); margin: 0.5rem 0 0 0; font-weight: 600;">{color_label}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fighter image and basic info
    img_col, info_col = st.columns([1, 2])

    with img_col:
        if info['image']:
            st.image(info['image'], width=140)
        else:
            st.markdown("""
                <div style='width:140px;height:160px;border-radius:12px;
                background:linear-gradient(135deg, #1a1f36, #151B2F);
                display:flex;align-items:center;justify-content:center;
                font-size:64px; border: 2px solid #2A3350;'>🥊</div>
            """, unsafe_allow_html=True)

    with info_col:
        # Basic record
        st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <p style="margin: 0.5rem 0; font-size: 1.1rem;">
                    <strong style="color: var(--accent-gold);">Record:</strong>
                    <span style="color: var(--text-primary); font-weight: 600;">{int(stats['wins'])}-{int(stats['losses'])}</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Physical attributes
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="stat-item">
                    <div class="stat-label">Height</div>
                    <div class="stat-value">{stats['height']:.0f}cm</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="stat-item">
                    <div class="stat-label">Reach</div>
                    <div class="stat-value">{stats['reach']:.0f}cm</div>
                </div>
            """, unsafe_allow_html=True)

    # Detailed stats grid
    st.markdown("""
        <h4 style="color: var(--text-primary); margin-top: 1.5rem; margin-bottom: 1rem;
        font-size: 1rem; text-transform: uppercase; letter-spacing: 1px;">Combat Statistics</h4>
    """, unsafe_allow_html=True)

    stat_cols = st.columns(5)

    stats_to_show = [
        ("Age", stats['age']),
        ("Win Streak", stats['win_streak']),
        ("Striking", f"{stats['sig_str']:.1f}/min"),
        ("Accuracy", f"{stats['sig_str_pct']*100:.0f}%"),
        ("Takedowns", f"{stats['td_pct']*100:.0f}%"),
    ]

    for col, (label, value) in zip(stat_cols, stats_to_show):
        with col:
            st.markdown(f"""
                <div class="stat-item">
                    <div class="stat-label">{label}</div>
                    <div class="stat-value">{value}</div>
                </div>
            """, unsafe_allow_html=True)

    # Fighter bio
    if info['summary']:
        with st.expander("📖 Fighter Bio"):
            st.write(info['summary'])

    return stats


def create_win_probability_chart(prob_red, prob_blue, fighter1_name, fighter2_name):
    """Create an interactive win probability chart"""
    fig = go.Figure(data=[
        go.Bar(
            y=[fighter1_name],
            x=[prob_red * 100],
            orientation='h',
            marker=dict(color='#EF3B39', line=dict(color='#FF5252', width=2)),
            text=f'{prob_red*100:.1f}%',
            textposition='inside',
            textfont=dict(color='white', size=18, family='Arial Black'),
            hovertemplate=f'{fighter1_name}<br>Win Probability: %{{x:.1f}}%<extra></extra>',
            showlegend=False,
        ),
        go.Bar(
            y=[fighter2_name],
            x=[prob_blue * 100],
            orientation='h',
            marker=dict(color='#0066CC', line=dict(color='#0052A3', width=2)),
            text=f'{prob_blue*100:.1f}%',
            textposition='inside',
            textfont=dict(color='white', size=18, family='Arial Black'),
            hovertemplate=f'{fighter2_name}<br>Win Probability: %{{x:.1f}}%<extra></extra>',
            showlegend=False,
        ),
    ])

    fig.update_layout(
        xaxis=dict(
            range=[0, 100],
            showgrid=True,
            gridwidth=1,
            gridcolor='#2A3350',
            tickfont=dict(color='#B0B8CC', size=12),
            title='',
        ),
        yaxis=dict(
            tickfont=dict(color='var(--text-primary)', size=14),
            categoryorder='total ascending',
        ),
        plot_bgcolor='rgba(21, 27, 47, 0.5)',
        paper_bgcolor='rgba(10, 14, 39, 0)',
        margin=dict(l=200, r=50, t=20, b=20),
        height=300,
        hovermode='y unified',
    )

    return fig


# ============ HEADER ============

st.markdown("""
    <div style="margin-bottom: 2rem; text-align: center;">
        <h1 style="margin: 0; font-size: 2.5rem;">⚡ UFC ANALYTICS</h1>
        <p style="color: var(--text-secondary); font-size: 1.1rem; margin-top: 0.5rem;
        letter-spacing: 2px; text-transform: uppercase;">FIGHT PREDICTION ENGINE</p>
        <div style="height: 3px; background: linear-gradient(90deg, #EF3B39, #0066CC, #C7954D);
        margin: 1rem 0; border-radius: 2px;"></div>
    </div>
""", unsafe_allow_html=True)

# ============ MODE SELECTION ============

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mode = st.radio(
        "Select Mode",
        ["Search by fighter name", "Manual stat entry"],
        horizontal=True,
        label_visibility="collapsed"
    )

fighter_names = sorted(fighter_db.index.tolist())

# ============ FIGHTER INPUT ============

if mode == "Search by fighter name":
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<h3 class="red-corner-title">🔴 Red Corner</h3>', unsafe_allow_html=True)
        r_name = st.selectbox("Select Red Fighter", fighter_names, index=0, key="r_name")
        r_stats = get_stats_from_db(r_name)
        r_info = get_fighter_info(r_name)
        render_fighter_card(r_name, r_stats, r_info, None, "red")
        r_odds = st.number_input("Moneyline Odds (American)", -1000, 1000, -150, key="r_o")

    with col2:
        st.markdown('<h3 class="blue-corner-title">🔵 Blue Corner</h3>', unsafe_allow_html=True)
        b_name = st.selectbox("Select Blue Fighter", fighter_names, index=1, key="b_name")
        b_stats = get_stats_from_db(b_name)
        b_info = get_fighter_info(b_name)
        render_fighter_card(b_name, b_stats, b_info, None, "blue")
        b_odds = st.number_input("Moneyline Odds (American)", -1000, 1000, 130, key="b_o")

else:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<h3 class="red-corner-title">🔴 Red Corner - Manual Entry</h3>', unsafe_allow_html=True)
        r_stats = {
            'height': st.number_input("Height (cm)", 150.0, 220.0, 180.0, key="r_h"),
            'reach': st.number_input("Reach (cm)", 150.0, 230.0, 185.0, key="r_r"),
            'age': st.number_input("Age", 18, 50, 28, key="r_a"),
            'win_streak': st.number_input("Current win streak", 0, 20, 2, key="r_ws"),
            'longest_streak': st.number_input("Longest win streak", 0, 20, 3, key="r_ls"),
            'wins': st.number_input("Total wins", 0, 50, 10, key="r_w"),
            'losses': st.number_input("Total losses", 0, 30, 3, key="r_l"),
            'sig_str': st.number_input("Avg sig. strikes landed/min", 0.0, 15.0, 4.0, key="r_ss"),
            'sig_str_pct': st.slider("Sig. strike accuracy (%)", 0, 100, 45, key="r_sp") / 100,
            'td': st.number_input("Avg takedowns landed", 0.0, 10.0, 1.5, key="r_td"),
            'td_pct': st.slider("Takedown accuracy (%)", 0, 100, 40, key="r_tp") / 100,
        }
        r_odds = st.number_input("Moneyline odds (American)", -1000, 1000, -150, key="r_o2")

    with col2:
        st.markdown('<h3 class="blue-corner-title">🔵 Blue Corner - Manual Entry</h3>', unsafe_allow_html=True)
        b_stats = {
            'height': st.number_input("Height (cm)", 150.0, 220.0, 180.0, key="b_h"),
            'reach': st.number_input("Reach (cm)", 150.0, 230.0, 185.0, key="b_r"),
            'age': st.number_input("Age", 18, 50, 28, key="b_a"),
            'win_streak': st.number_input("Current win streak", 0, 20, 2, key="b_ws"),
            'longest_streak': st.number_input("Longest win streak", 0, 20, 3, key="b_ls"),
            'wins': st.number_input("Total wins", 0, 50, 10, key="b_w"),
            'losses': st.number_input("Total losses", 0, 30, 3, key="b_l"),
            'sig_str': st.number_input("Avg sig. strikes landed/min", 0.0, 15.0, 4.0, key="b_ss"),
            'sig_str_pct': st.slider("Sig. strike accuracy (%)", 0, 100, 45, key="b_sp") / 100,
            'td': st.number_input("Avg takedowns landed", 0.0, 10.0, 1.5, key="b_td"),
            'td_pct': st.slider("Takedown accuracy (%)", 0, 100, 40, key="b_tp") / 100,
        }
        b_odds = st.number_input("Moneyline odds (American)", -1000, 1000, 130, key="b_o2")

# ============ PREDICTION BUTTON ============

st.markdown("<br>", unsafe_allow_html=True)
button_col1, button_col2, button_col3 = st.columns([1, 2, 1])
with button_col2:
    predict_clicked = st.button("⚡ ANALYZE FIGHT", key="predict", use_container_width=True)

# ============ RESULTS ============

if predict_clicked:
    # Calculate features
    row = pd.DataFrame([{
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
    }])[features]

    prob_red = model.predict_proba(row)[0][1]
    prob_blue = 1 - prob_red

    # Get fighter names
    fighter1_name = r_name if mode == "Search by fighter name" else "Fighter 1"
    fighter2_name = b_name if mode == "Search by fighter name" else "Fighter 2"

    # ===== PREDICTION RESULTS HEADER =====
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <h2 style="text-align: center; color: var(--text-primary); font-size: 2rem;
        margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 1px;">
        📊 FIGHT ANALYSIS
        </h2>
    """, unsafe_allow_html=True)

    # ===== OUTCOME PREDICTION - LARGE VISUALIZATION =====
    st.markdown("""
        <div class="prediction-container">
            <h3 style="color: var(--text-primary); margin-bottom: 1.5rem; text-transform: uppercase;
            letter-spacing: 1px;">🎯 Win Probability Analysis</h3>
        </div>
    """, unsafe_allow_html=True)

    # Display chart
    fig = create_win_probability_chart(prob_red, prob_blue, fighter1_name, fighter2_name)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Probability metrics
    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Red Corner</div>
                <div class="metric-value" style="color: #EF3B39;">{prob_red*100:.1f}%</div>
                <div class="metric-delta">Win Probability</div>
            </div>
        """, unsafe_allow_html=True)

    with metric_col2:
        winner = fighter1_name if prob_red > 0.5 else fighter2_name
        winner_color = "#EF3B39" if prob_red > 0.5 else "#0066CC"
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Predicted Winner</div>
                <div class="metric-value" style="color: {winner_color};">{winner}</div>
                <div class="metric-delta">{max(prob_red, prob_blue)*100:.1f}% Confidence</div>
            </div>
        """, unsafe_allow_html=True)

    with metric_col3:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Blue Corner</div>
                <div class="metric-value" style="color: #0066CC;">{prob_blue*100:.1f}%</div>
                <div class="metric-delta">Win Probability</div>
            </div>
        """, unsafe_allow_html=True)

    # ===== ENHANCED PREDICTIONS =====
    if enhanced_mode:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="prediction-container">
                <h3 style="color: var(--text-primary); margin-bottom: 1.5rem; text-transform: uppercase;
                letter-spacing: 1px;">📈 Detailed Fight Breakdown</h3>
            </div>
        """, unsafe_allow_html=True)

        # Get predictions
        round_probs = round_model.predict_proba(row)[0]
        round_classes = sorted(round_model.classes_)

        method_probs = method_model.predict_proba(row)[0]
        method_classes = sorted(method_model.classes_)

        predicted_round = round_classes[round_probs.argmax()]
        predicted_method = method_classes[method_probs.argmax()]

        # Key predictions
        pred_col1, pred_col2, pred_col3 = st.columns(3)

        with pred_col1:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">Most Probable Round</div>
                    <div class="metric-value" style="color: var(--accent-gold);">R{int(predicted_round)}</div>
                    <div class="metric-delta">{round_probs.max()*100:.1f}% Confidence</div>
                </div>
            """, unsafe_allow_html=True)

        with pred_col2:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">Method of Victory</div>
                    <div class="metric-value" style="font-size: 1.5rem; color: var(--accent-gold);">{predicted_method}</div>
                    <div class="metric-delta">{method_probs.max()*100:.1f}% Confidence</div>
                </div>
            """, unsafe_allow_html=True)

        with pred_col3:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">Model Ensemble</div>
                    <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                        <div>Outcome: {metadata['outcome_accuracy']:.0f}%</div>
                        <div>Round: {metadata['round_accuracy']:.0f}%</div>
                        <div>Method: {metadata['method_accuracy']:.0f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Round breakdown
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <h4 style="color: var(--text-primary); margin-top: 2rem; margin-bottom: 1rem;
            text-transform: uppercase; letter-spacing: 1px; font-size: 1rem;">📊 Round Probability</h4>
        """, unsafe_allow_html=True)

        round_data = pd.DataFrame({
            'Round': [f"Round {int(r)}" for r in round_classes],
            'Probability': [f"{p*100:.1f}%" for p in round_probs]
        })

        st.dataframe(round_data, use_container_width=True, hide_index=True,
                    column_config={
                        'Round': st.column_config.TextColumn(width='medium'),
                        'Probability': st.column_config.TextColumn(width='medium'),
                    })

        # Method breakdown
        st.markdown("""
            <h4 style="color: var(--text-primary); margin-top: 2rem; margin-bottom: 1rem;
            text-transform: uppercase; letter-spacing: 1px; font-size: 1rem;">⚔️ Method of Victory</h4>
        """, unsafe_allow_html=True)

        method_data = pd.DataFrame({
            'Method': method_classes,
            'Probability': [f"{p*100:.1f}%" for p in method_probs]
        })

        st.dataframe(method_data, use_container_width=True, hide_index=True,
                    column_config={
                        'Method': st.column_config.TextColumn(width='medium'),
                        'Probability': st.column_config.TextColumn(width='medium'),
                    })

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding: 2rem; border-top: 2px solid var(--border-color);
        margin-top: 2rem; color: var(--text-secondary);">
            <p style="margin: 0; font-size: 0.9rem;">
                ⚡ UFC Analytics powered by machine learning models trained on historical fight data
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; letter-spacing: 1px;">
                PREDICTIONS ARE STATISTICAL ESTIMATES · NOT GUARANTEED
            </p>
        </div>
    """, unsafe_allow_html=True)
