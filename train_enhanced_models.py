"""
Enhanced UFC Fight Predictor - Trains models for outcome, round, and method of victory
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

# Load data
print("Loading UFC data...")
df = pd.read_csv('data/ufc-master.csv')

# Prepare features
print("Preparing features...")
df['sig_str_pct_dif'] = (df['R_avg_SIG_STR_pct'] - df['B_avg_SIG_STR_pct']).fillna(0)
df['td_pct_dif'] = (df['R_avg_TD_pct'] - df['B_avg_TD_pct']).fillna(0)
df['losses_dif'] = df['R_losses'] - df['B_losses']
df['odds_dif'] = df['R_odds'] - df['B_odds']

# 'no_of_rounds' (3 or 5) lets the models condition on the scheduled fight
# length. It costs a little method accuracy but makes the scheduled distance a
# real input rather than a display-only setting.
features = ['height_dif', 'reach_dif', 'age_dif', 'win_streak_dif',
            'longest_win_streak_dif', 'win_dif', 'sig_str_dif', 'avg_td_dif',
            'sig_str_pct_dif', 'td_pct_dif', 'losses_dif', 'odds_dif',
            'no_of_rounds']

# Clean data
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)
df = df[df['Winner'].isin(['Red', 'Blue'])].copy()
df = df.dropna(subset=features + ['finish_round'])
df['target'] = (df['Winner'] == 'Red').astype(int)

print(f"Total fights: {len(df)}")

# Train-test split (before 2024 = train)
cutoff = '2024-01-01'
train = df[df['date'] < cutoff]
test = df[df['date'] >= cutoff]

X_train = train[features]
y_train = train['target']
X_test = test[features]
y_test = test['target']

# ============ MODEL 1: OUTCOME PREDICTION ============
print("\nTraining outcome prediction model...")
outcome_model = LogisticRegression(max_iter=20000)
outcome_model.fit(X_train, y_train)
outcome_accuracy = outcome_model.score(X_test, y_test)
print(f"Outcome prediction accuracy: {outcome_accuracy:.2%}")

# ============ MODEL 2: ROUND PREDICTION ============
print("\nTraining round prediction model...")
df_clean = df.dropna(subset=['finish_round'])
df_clean['finish_round'] = df_clean['finish_round'].astype(int)

# Map to round categories (1, 2, 3, or 5)
df_clean['round_category'] = df_clean['finish_round'].clip(1, 5).astype(int)

train_round = df_clean[df_clean['date'] < cutoff]
test_round = df_clean[df_clean['date'] >= cutoff]

X_train_round = train_round[features]
y_train_round = train_round['round_category']
X_test_round = test_round[features]
y_test_round = test_round['round_category']

round_model = LogisticRegression(max_iter=20000, solver='lbfgs')
round_model.fit(X_train_round, y_train_round)
round_accuracy = round_model.score(X_test_round, y_test_round)
print(f"Round prediction accuracy: {round_accuracy:.2%}")
print(f"Possible rounds: {sorted(round_model.classes_.tolist())}")

# ============ MODEL 3: METHOD OF VICTORY ============
print("\nTraining method of victory prediction model...")
# Create method categories from 'finish' column
df_clean['method'] = 'Decision'
df_clean.loc[df_clean['finish'].str.contains('KO|TKO', case=False, na=False), 'method'] = 'KO/TKO'
df_clean.loc[df_clean['finish'].str.contains('SUB', case=False, na=False), 'method'] = 'Submission'

print(f"Method distribution:\n{df_clean['method'].value_counts()}")

train_method = df_clean[df_clean['date'] < cutoff]
test_method = df_clean[df_clean['date'] >= cutoff]

X_train_method = train_method[features]
y_train_method = train_method['method']
X_test_method = test_method[features]
y_test_method = test_method['method']

method_model = LogisticRegression(max_iter=20000, solver='lbfgs')
method_model.fit(X_train_method, y_train_method)
method_accuracy = method_model.score(X_test_method, y_test_method)
print(f"Method prediction accuracy: {method_accuracy:.2%}")

# ============ FIGHTER PERFORMANCE BY FIGHT LENGTH ============
print("\nAnalyzing fighter performance by fight length...")

def get_fighter_stats_by_length(df, fighter_name):
    """Get fighter stats separated by fight length (3 vs 5 rounds)"""
    # Red corner
    r_fights = df[df['R_fighter'] == fighter_name].copy()
    r_3round = r_fights[r_fights['no_of_rounds'] == 3]
    r_5round = r_fights[r_fights['no_of_rounds'] == 5]

    # Blue corner
    b_fights = df[df['B_fighter'] == fighter_name].copy()
    b_3round = b_fights[b_fights['no_of_rounds'] == 3]
    b_5round = b_fights[b_fights['no_of_rounds'] == 5]

    r_3_wins = ((r_3round['Winner'] == 'Red').sum()) if len(r_3round) > 0 else 0
    r_5_wins = ((r_5round['Winner'] == 'Red').sum()) if len(r_5round) > 0 else 0
    b_3_wins = ((b_3round['Winner'] == 'Blue').sum()) if len(b_3round) > 0 else 0
    b_5_wins = ((b_5round['Winner'] == 'Blue').sum()) if len(b_5round) > 0 else 0

    return {
        '3round_wins': r_3_wins + b_3_wins,
        '3round_total': len(r_3round) + len(b_3round),
        '5round_wins': r_5_wins + b_5_wins,
        '5round_total': len(r_5round) + len(b_5round),
    }

# Save models
print("\nSaving models...")
joblib.dump(outcome_model, 'models/outcome_model.pkl')
joblib.dump(round_model, 'models/round_model.pkl')
joblib.dump(method_model, 'models/method_model.pkl')
joblib.dump(features, 'models/features.pkl')

# The web app reads model.pkl / features.pkl at the project root. Write the same
# outcome model to both locations so the two can never disagree - they had
# drifted apart previously (max coefficient difference 0.30).
joblib.dump(outcome_model, 'model.pkl')
joblib.dump(features, 'features.pkl')

# Save metadata
metadata = {
    'outcome_accuracy': float(outcome_accuracy),
    'round_accuracy': float(round_accuracy),
    'method_accuracy': float(method_accuracy),
    'round_classes': sorted(round_model.classes_.tolist()),
    'method_classes': sorted(method_model.classes_.tolist()),
    'features': features,
}
import json
with open('models/metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print("✓ Models saved to models/ directory")
print(f"\nModel Performance Summary:")
print(f"  Outcome: {outcome_accuracy:.2%}")
print(f"  Round: {round_accuracy:.2%}")
print(f"  Method: {method_accuracy:.2%}")
