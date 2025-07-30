import logging
import os
import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression

MODEL_PATH = "ai_learning_model.pkl"
DATA_PATH = "ai_learning_trades.pkl"

class AILearningEngine:
    def __init__(self):
        self.past_trades = []
        self.model = LogisticRegression()
        self.is_model_trained = False
        self.load_data()
        self.load_model()

    def extract_features(self, trade_data):
        # Example: extract relevant features as a numerical list
        # You should replace this with actual meaningful features for your strategy
        # Example features: [entry_price, exit_price, volume, holding_time]
        return [
            trade_data.get("entry_price", 0),
            trade_data.get("exit_price", 0),
            trade_data.get("volume", 0),
            trade_data.get("holding_time", 0)
        ]

    def record_trade(self, trade_data):
        try:
            features = self.extract_features(trade_data)
            outcome = 1 if trade_data.get("profit", 0) > 0 else 0
            self.past_trades.append((features, outcome))
            self.save_data()
            logging.info(f"Recorded trade data: {trade_data}")
            self.train_model()
        except Exception as e:
            logging.error(f"Error recording trade: {e}")

    def train_model(self):
        try:
            if len(self.past_trades) >= 10:  # Train only if enough data
                X, y = zip(*self.past_trades)
                self.model.fit(np.array(X), np.array(y))
                self.is_model_trained = True
                self.save_model()
                logging.info("Trained learning model with current trade data.")
            else:
                logging.info("Not enough trades to train the model yet.")
        except Exception as e:
            logging.error(f"Error training model: {e}")

    def predict_trade_profitability(self, trade_data):
        try:
            if not self.is_model_trained:
                return 0.5  # Neutral if not enough data
            features = self.extract_features(trade_data)
            prob = self.model.predict_proba([features])[0][1]
            return prob
        except Exception as e:
            logging.error(f"Error predicting trade profitability: {e}")
            return 0.5

    def should_execute_trade(self, trade_data, threshold=0.7):
        prob = self.predict_trade_profitability(trade_data)
        return prob >= threshold

    def analyze_trades(self):
        try:
            logging.info(f"Analyzing {len(self.past_trades)} trades for learning")
            if not self.past_trades:
                return {"win_rate": None}
            total = len(self.past_trades)
            wins = sum(1 for _, outcome in self.past_trades if outcome)
            win_rate = wins / total
            return {"win_rate": win_rate}
        except Exception as e:
            logging.error(f"Error analyzing trades: {e}")
            return {}

    def suggest_improvements(self):
        try:
            analysis = self.analyze_trades()
            logging.info("Suggesting strategy improvements based on trade analysis")
            # Placeholder: add real insights here
            if analysis.get("win_rate") is not None and analysis["win_rate"] < 0.5:
                return ["Consider revising entry/exit signals."]
            else:
                return ["Continue current strategy or optimize further."]
        except Exception as e:
            logging.error(f"Error suggesting improvements: {e}")
            return []

    def save_model(self):
        try:
            with open(MODEL_PATH, "wb") as f:
                pickle.dump(self.model, f)
        except Exception as e:
            logging.error(f"Error saving model: {e}")

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
                self.is_model_trained = True
                logging.info("Loaded trained model from disk.")
            except Exception as e:
                logging.error(f"Error loading model: {e}")

    def save_data(self):
        try:
            with open(DATA_PATH, "wb") as f:
                pickle.dump(self.past_trades, f)
        except Exception as e:
            logging.error(f"Error saving trade data: {e}")

    def load_data(self):
        if os.path.exists(DATA_PATH):
            try:
                with open(DATA_PATH, "rb") as f:
                    self.past_trades = pickle.load(f)
                logging.info("Loaded trade data from disk.")
            except Exception as e:
                logging.error(f"Error loading trade data: {e}")
