# UFC Fight Predictor - Usage Guide

Your predictor now includes **3 models** that work together to predict any UFC fight:

## What It Predicts

1. **Fight Outcome** - Who wins (Red vs Blue fighter)
   - Accuracy: ~69.9%

2. **Round of Victory** - Which round the fight ends (1, 2, 3, 4, or 5)
   - Accuracy: ~58.4%

3. **Method of Victory** - How the fight ends
   - Decision, KO/TKO, or Submission
   - Accuracy: ~50.0%

All three take the **scheduled fight length** (3 or 5 rounds) as an input.

## How to Use

### Option 1: Command Line (Easiest)

```bash
python predict.py "Fighter 1 Name" "Fighter 2 Name" [fight_length]
```

**Examples:**

```bash
# Predict Israel Adesanya vs Sean Strickland (5 rounds)
python predict.py "Israel Adesanya" "Sean Strickland" 5

# Predict Conor McGregor vs Dustin Poirier (5 rounds)
python predict.py "Conor McGregor" "Dustin Poirier" 5

# Predict a 3-round fight
python predict.py "Max Holloway" "Yair Rodriguez" 3
```

### Option 2: Python Script

```python
from predict import UFCPredictor

predictor = UFCPredictor()

# Get fighter stats from database
fighter1_stats = predictor.get_fighter_stats("Israel Adesanya")
fighter2_stats = predictor.get_fighter_stats("Sean Strickland")

# Make prediction
prediction = predictor.predict_fight(
    fighter1_stats, fighter2_stats,
    "Israel Adesanya", "Sean Strickland",
    fight_length=5
)

# Display results
predictor.print_prediction(prediction)

# Or access individual predictions
print(f"Winner: {prediction['outcome']['winner']}")
print(f"Predicted Round: {prediction['round']['predicted']}")
print(f"Method: {prediction['method']['predicted']}")
```

### Option 3: Streamlit Web App

```bash
streamlit run app.py
```

Then:
1. Choose **Fighter Search** or **Manual Entry** in the mode toggle
2. Set **Fight Length** to 3 or 5 rounds
3. Pick the red and blue corner fighters (the selectors autocomplete)
4. Adjust the moneyline odds if you have them
5. Click **Analyze Fight**
5. Review the model prediction, market-vs-model comparison, round/method
   breakdown, and the fighter comparison

Some fighters in the database are missing striking or takedown stats. The models
need all twelve features, so those matchups can't be scored - the app names the
missing stat instead of guessing a value.

### What fight length changes

`no_of_rounds` is the 13th model feature, so the scheduled distance feeds all
three predictions. Example (Adesanya vs Strickland, -150/+130):

| | 3 rounds | 5 rounds |
|---|---|---|
| Win probability (red) | 66.6% | 63.2% |
| Round of victory | R3 (58.3%) | R5 (50.5%) |
| Method | Decision (48.3%) | KO/TKO (44.2%) |

Retraining cost method accuracy (51.8% -> 50.0%) but round accuracy improved
substantially (54.6% -> 58.4%), partly from the new feature and partly because
`max_iter` was raised to 20,000 so the models actually converge.

**Known limitation.** These are plain logistic regressions with no interaction
terms, so `no_of_rounds` shifts the outcome logit by a constant: five rounds
always moves the red corner about -3pp regardless of who is fighting. The model
cannot learn that a particular fighter's cardio favours a longer fight. Adding
interaction terms was tested and did not justify itself (+0.00pp outcome,
+0.70pp method, on only 106 five-round fights in the test set).

The round distribution is still renormalised over reachable rounds. Now that the
model knows the distance it rarely puts weight on impossible rounds (~0.2%,
down from ~6.4%), but the guard remains so a 3-round bout can never display R4
or R5.

### Retraining

```bash
python train_enhanced_models.py
```

This writes `models/{outcome,round,method}_model.pkl`, `models/metadata.json`,
and also `model.pkl` / `features.pkl` at the project root - the web app reads
the root copies, and writing both from one script keeps them from drifting
apart (they previously had a max coefficient difference of 0.30).

Previous artefacts are preserved in the `model_backup_*/` directory.

## What The Models Look At

The predictions are based on comparing fighter statistics:

- **Physical**: Height, reach, age
- **Record**: Wins, losses, current/longest win streaks
- **Striking**: Average significant strikes landed, accuracy
- **Grappling**: Average takedowns, accuracy
- **Betting**: Moneyline odds (if available)

## Fighter Database

The predictors use stats from fighters who have competed since 2010. You can:

- Search by fighter name in the Streamlit app
- Enter custom stats manually
- Use the Python API to get stats: `predictor.get_fighter_stats("Fighter Name")`

## Prediction Output

For each fight, you'll get:

```
🎯 PREDICTED OUTCOME:
  Winner: Fighter Name
  Fighter 1: 55.9%
  Fighter 2: 44.1%

📊 PREDICTED ROUND:
  Most Probable: Round 3
  [Probability breakdown for rounds 1-5]

⚔️  PREDICTED METHOD OF VICTORY:
  Most Probable: Decision
  [Probability breakdown for KO/TKO, Submission, Decision]
```

## Notes

- These are statistical predictions based on historical data, not guaranteed
- The models work best for fighters in the database with recent fight history
- For new or emerging fighters, predictions may be less accurate
- Consider fight context (injuries, weight class changes, motivations) when evaluating predictions

## Files

- `predict.py` - Command-line and Python API for predictions
- `train_enhanced_models.py` - Trains all models from UFC data
- `app.py` - Streamlit web interface
- `app_legacy.py` - Previous version of the web interface, kept for reference
- `ui/` - Presentation layer for the web interface (no model logic)
  - `theme.py` - Design tokens and all CSS
  - `components.py` - HTML renderers for each section
  - `data.py` - Fighter portraits (Wikipedia) and division/stance lookups
  - `format.py` - Value formatting and American-odds conversion
- `models/` - Trained model files
  - `outcome_model.pkl` - Predicts winner
  - `round_model.pkl` - Predicts fight round
  - `method_model.pkl` - Predicts method of victory
