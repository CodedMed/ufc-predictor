# UFC Analytics

Machine learning predictions for UFC fights — who wins, in which round, and by
what method — served through a Streamlit dashboard.

Pick two fighters, set the scheduled distance and the moneyline odds, and the
app returns a win probability, a round and method breakdown, and a comparison
against what the betting market implies.

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## What it predicts

Three logistic regression models trained on 6,294 UFC fights from March 2010 to
March 2026. The split is chronological — everything before 2024-01-01 trains
(5,298 fights), everything after is held out (996 fights) — so the models are
always scored on fights that happened after the ones they learned from.

| Prediction | Accuracy | Majority-class baseline | Lift |
| --- | --- | --- | --- |
| **Outcome** (which corner wins) | **69.88%** | 54.92% | **+14.96pp** |
| **Round** of victory (1-5) | **58.43%** | 54.72% | +3.71pp |
| **Method** (Decision / KO-TKO / Submission) | **50.00%** | 51.81% | **−1.81pp** |

Read that last row carefully: **the method model performs slightly worse than
always guessing "Decision."** It is displayed in the app because the full
distribution is more informative than the single argmax, but the method pick
itself should not be trusted. The outcome model is the one carrying real signal.

## Inputs

Each prediction is built from thirteen features — twelve differences between the
two fighters, plus the scheduled fight length:

| Group | Features |
| --- | --- |
| Physical | height, reach, age |
| Record | wins, losses, current win streak, longest win streak |
| Striking | significant strikes per minute, strike accuracy |
| Grappling | takedowns, takedown accuracy |
| Market | moneyline odds difference |
| Bout | scheduled rounds (3 or 5) |

## Usage

### Web app

```bash
streamlit run app.py
```

Choose **Fighter Search** to pull stats for any of the 2,238 fighters in the
database, or **Manual Entry** to type them in. Set the fight length and odds,
then run the analysis.

### Command line

```bash
python predict.py "Israel Adesanya" "Sean Strickland" 5
```

The third argument is the scheduled rounds (3 or 5, defaults to 3).

### Python

```python
from predict import UFCPredictor

predictor = UFCPredictor()
red = predictor.get_fighter_stats("Israel Adesanya")
blue = predictor.get_fighter_stats("Sean Strickland")

prediction = predictor.predict_fight(red, blue, "Adesanya", "Strickland", fight_length=5)
predictor.print_prediction(prediction)
```

### Retraining

```bash
python train_enhanced_models.py
```

Writes `models/` and the root `model.pkl` / `features.pkl` from a single place,
so the two copies cannot drift apart.

---

## How fight length works

`no_of_rounds` is a real model feature, so the scheduled distance changes every
prediction rather than just relabelling the output:

| Adesanya vs Strickland (-150 / +130) | 3 rounds | 5 rounds |
| --- | --- | --- |
| Win probability | 66.6% | 63.2% |
| Round of victory | R3 (58.3%) | R5 (50.5%) |
| Method | Decision (48.3%) | KO/TKO (44.2%) |

The round distribution is also renormalised over reachable rounds, so a
three-round bout can never display a round 4 or 5 finish.

## Market vs model

Given moneyline odds, the app converts them to implied probability, removes the
book's margin so both sides sum to 100%, and compares that against the model.

```
-150  ->  60.0% implied  ->  58.0% no-vig
```

The difference is labelled as an edge, but see the limitations below before
reading anything into it.

---

## Limitations

Worth knowing before trusting any number this produces.

**The odds are an input, not just a comparison.** `odds_dif` is one of the
thirteen features, so the model has already absorbed the market's opinion.
Changing the odds moves the prediction substantially — the same matchup at
-150 gives 66.6% and at -400 gives 74.6%. The "model edge" shown against the
market is therefore not an independent second opinion, and it is not a
profitability signal.

**Fight length shifts every matchup identically.** These are plain logistic
regressions with no interaction terms, so `no_of_rounds` moves the outcome logit
by a constant: five rounds costs the red corner about 3 percentage points
regardless of who is fighting. The model cannot learn that a particular
fighter's cardio suits a longer fight. Interaction terms were tested and did not
earn their place (+0.00pp on outcome, across only 106 five-round fights in the
test set).

**The method model is below baseline**, as shown above.

**Some fighters have incomplete stats.** 125 of the 2,238 fighters are missing
striking or takedown data. The models need all thirteen features, so
those matchups cannot be scored — the app names the missing stat rather than
imputing a value and quietly changing the prediction.

**Records reflect this dataset only**, not a fighter's full professional record.

**Red vs blue corner is not arbitrary.** The red corner wins about 55% of the
time in this data, and the models learn that asymmetry, so swapping the corners
does not simply mirror the probability.

---

## Project structure

```
app.py                     Streamlit dashboard (presentation only)
ui/
  theme.py                 Design tokens and all CSS
  components.py            HTML renderers for each section
  data.py                  Fighter portraits, division and stance lookups
  format.py                Value formatting and American-odds conversion
predict.py                 CLI and Python API
train_enhanced_models.py   Trains and saves all three models
01_explore.ipynb           Exploration; builds fighter_db.pkl
data/ufc-master.csv        Source dataset
models/                    Trained models and metadata
fighter_db.pkl             Per-fighter stats used by the app
```

`fighter_db.pkl` is produced by the notebook, not by the training script, so it
is tracked in git rather than treated as a rebuildable artefact.

Fighter portraits are fetched from the Wikipedia API, which returns HTTP 403
without a descriptive `User-Agent`. Matches are checked against the fighter's
name so an unrelated article cannot supply a photo, and fighters without a usable
image fall back to a neutral silhouette.

## Requirements

Python 3.11+ and the packages in `requirements.txt` (streamlit, pandas,
scikit-learn, joblib, requests).

## Disclaimer

Statistical estimates from historical data, for research and entertainment. Not
betting advice.
