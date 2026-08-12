#!/usr/bin/env python3
"""
UFC Fight Predictor - Unified prediction interface for any fight
"""
import numpy as np
import pandas as pd
import joblib
import json
import sys
from typing import Dict, List, Tuple

class UFCPredictor:
    def __init__(self):
        """Initialize all models and data"""
        self.outcome_model = joblib.load('models/outcome_model.pkl')
        self.round_model = joblib.load('models/round_model.pkl')
        self.method_model = joblib.load('models/method_model.pkl')

        with open('models/metadata.json') as f:
            self.metadata = json.load(f)

        self.features = self.metadata['features']
        self.df = pd.read_csv('data/ufc-master.csv')

    def get_fighter_stats(self, fighter_name: str) -> Dict:
        """Get fighter stats from database"""
        try:
            fighter_db = joblib.load('fighter_db.pkl')
            stats = fighter_db.loc[fighter_name].to_dict()
            return stats
        except:
            return None

    def predict_fight(self, fighter1_stats: Dict, fighter2_stats: Dict,
                     fighter1_name: str = "Fighter 1",
                     fighter2_name: str = "Fighter 2",
                     fight_length: int = None) -> Dict:
        """
        Predict a fight between two fighters

        Args:
            fighter1_stats: Dictionary with fighter stats (height, reach, age, wins, losses, etc.)
            fighter2_stats: Dictionary with opponent stats
            fighter1_name: Name of fighter 1
            fighter2_name: Name of fighter 2
            fight_length: 3 or 5 rounds. This is a real model feature, so it
                changes the outcome, round and method predictions. Defaults to 3.

        Returns:
            Dictionary with predictions (outcome, round, method, etc.)
        """
        # 3 rounds is the default scheduled distance for a non-title bout.
        fight_length = 3 if fight_length is None else int(fight_length)

        # Create feature differences
        features_dict = {
            'height_dif': fighter1_stats['height'] - fighter2_stats['height'],
            'reach_dif': fighter1_stats['reach'] - fighter2_stats['reach'],
            'age_dif': fighter1_stats['age'] - fighter2_stats['age'],
            'win_streak_dif': fighter1_stats['win_streak'] - fighter2_stats['win_streak'],
            'longest_win_streak_dif': fighter1_stats['longest_streak'] - fighter2_stats['longest_streak'],
            'win_dif': fighter1_stats['wins'] - fighter2_stats['wins'],
            'sig_str_dif': fighter1_stats['sig_str'] - fighter2_stats['sig_str'],
            'avg_td_dif': fighter1_stats['td'] - fighter2_stats['td'],
            'sig_str_pct_dif': fighter1_stats['sig_str_pct'] - fighter2_stats['sig_str_pct'],
            'td_pct_dif': fighter1_stats['td_pct'] - fighter2_stats['td_pct'],
            'losses_dif': fighter1_stats['losses'] - fighter2_stats['losses'],
            'odds_dif': fighter1_stats.get('odds', 0) - fighter2_stats.get('odds', 0),
            'no_of_rounds': fight_length,
        }

        # Create DataFrame with correct feature order
        row = pd.DataFrame([features_dict])[self.features]

        # Get predictions
        outcome_probs = self.outcome_model.predict_proba(row)[0]
        round_probs = self.round_model.predict_proba(row)[0]
        method_probs = self.method_model.predict_proba(row)[0]

        prob_fighter1 = outcome_probs[1]
        prob_fighter2 = 1 - prob_fighter1

        round_classes = sorted(self.round_model.classes_)
        method_classes = sorted(self.method_model.classes_)

        # A fight cannot end after its scheduled distance. Drop unreachable
        # rounds and renormalise so the reported probabilities sum to 1.
        reachable = [(int(r), float(p)) for r, p in zip(round_classes, round_probs)
                     if int(r) <= fight_length]
        total = sum(p for _, p in reachable)
        if total > 0:
            reachable = [(r, p / total) for r, p in reachable]
        round_classes = [r for r, _ in reachable]
        round_probs = np.array([p for _, p in reachable])

        predicted_round = round_classes[round_probs.argmax()]
        predicted_method = method_classes[method_probs.argmax()]
        predicted_winner = fighter1_name if prob_fighter1 > 0.5 else fighter2_name

        return {
            'fight': f"{fighter1_name} vs {fighter2_name}",
            'fight_length': fight_length,
            'outcome': {
                'winner': predicted_winner,
                'prob_fighter1': prob_fighter1,
                'prob_fighter2': prob_fighter2,
            },
            'round': {
                'predicted': predicted_round,
                'probabilities': {f"Round {r}": float(p) for r, p in zip(round_classes, round_probs)},
            },
            'method': {
                'predicted': predicted_method,
                'probabilities': {m: float(p) for m, p in zip(method_classes, method_probs)},
            },
            'fighter1_stats': fighter1_stats,
            'fighter2_stats': fighter2_stats,
        }

    def print_prediction(self, prediction: Dict):
        """Pretty print prediction results"""
        print(f"\n{'='*60}")
        print(f"  {prediction['fight']}")
        print(f"{'='*60}")

        if prediction['fight_length']:
            print(f"Fight Length: {prediction['fight_length']} rounds\n")

        # Outcome
        outcome = prediction['outcome']
        print("🎯 PREDICTED OUTCOME:")
        print(f"  Winner: {outcome['winner']}")
        print(f"  Fighter 1: {outcome['prob_fighter1']:.1%}")
        print(f"  Fighter 2: {outcome['prob_fighter2']:.1%}")

        # Round
        print("\n📊 PREDICTED ROUND:")
        print(f"  Most Probable: Round {prediction['round']['predicted']}")
        for round_name, prob in prediction['round']['probabilities'].items():
            bar = "█" * int(prob * 30) + "░" * (30 - int(prob * 30))
            print(f"    {round_name}: {bar} {prob:.1%}")

        # Method
        print("\n⚔️  PREDICTED METHOD OF VICTORY:")
        print(f"  Most Probable: {prediction['method']['predicted']}")
        for method, prob in prediction['method']['probabilities'].items():
            bar = "█" * int(prob * 30) + "░" * (30 - int(prob * 30))
            print(f"    {method}: {bar} {prob:.1%}")

        print(f"\n{'='*60}\n")


def main():
    """CLI interface for fight predictions"""
    predictor = UFCPredictor()

    if len(sys.argv) < 3:
        print("Usage: python predict.py <fighter1_name> <fighter2_name> [fight_length]")
        print("\nExample:")
        print("  python predict.py 'Conor McGregor' 'Dustin Poirier' 5")
        sys.exit(1)

    fighter1_name = sys.argv[1]
    fighter2_name = sys.argv[2]
    fight_length = int(sys.argv[3]) if len(sys.argv) > 3 else None

    # Get stats
    print(f"Loading fighter data...")
    fighter1_stats = predictor.get_fighter_stats(fighter1_name)
    fighter2_stats = predictor.get_fighter_stats(fighter2_name)

    if not fighter1_stats or not fighter2_stats:
        print(f"Error: Could not find stats for one or both fighters")
        print(f"  {fighter1_name}: {'✓' if fighter1_stats else '✗'}")
        print(f"  {fighter2_name}: {'✓' if fighter2_stats else '✗'}")
        sys.exit(1)

    # Make prediction
    prediction = predictor.predict_fight(
        fighter1_stats, fighter2_stats,
        fighter1_name, fighter2_name,
        fight_length
    )

    # Display results
    predictor.print_prediction(prediction)

    # Also return as JSON for scripting
    import json
    prediction_json = prediction.copy()
    prediction_json['fighter1_stats'] = {k: float(v) if isinstance(v, (int, float)) else v
                                          for k, v in fighter1_stats.items()}
    prediction_json['fighter2_stats'] = {k: float(v) if isinstance(v, (int, float)) else v
                                          for k, v in fighter2_stats.items()}
    return prediction_json


if __name__ == '__main__':
    main()
