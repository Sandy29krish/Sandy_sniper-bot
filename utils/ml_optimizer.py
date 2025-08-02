#!/usr/bin/env python3
"""
🧠 MACHINE LEARNING OPTIMIZER
AI-powered trading optimization that learns from Saki's patterns
"""

import numpy as np
import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import logging

logger = logging.getLogger(__name__)

class MLTradingOptimizer:
    def __init__(self):
        self.model_dir = "ml_models"
        self.ensure_model_directory()
        
        # Signal prediction model
        self.signal_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        # Risk optimization model
        self.risk_optimizer = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        # Feature scaler
        self.scaler = StandardScaler()
        
        # Trading data storage
        self.trading_history = []
        self.model_trained = False
        self.last_training_time = None
        self.min_samples_for_training = 50
        
        # Performance tracking
        self.ml_stats = {
            'signal_accuracy': 0.0,
            'risk_prediction_error': 0.0,
            'profitable_trades_predicted': 0,
            'total_predictions': 0,
            'model_confidence': 0.0,
            'last_optimization_time': None
        }
        
        # Load existing models if available
        self.load_models()
    
    def train_model(self, features, labels):
        """Basic model training method for testing compatibility"""
        try:
            if len(features) < 5:
                logger.warning("Not enough data for training")
                return False
            
            # Train signal classifier
            self.signal_classifier.fit(features, labels)
            self.model_trained = True
            logger.info("✅ Model trained successfully")
            return True
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False
    
    def predict(self, features):
        """Basic prediction method for testing compatibility"""
        try:
            if not self.model_trained:
                return [0.5]  # Default prediction
            
            prediction = self.signal_classifier.predict_proba(features)
            return prediction[0] if len(prediction) > 0 else [0.5]
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return [0.5]
    
    def ensure_model_directory(self):
        """Create ML models directory if it doesn't exist"""
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
    
    def extract_features(self, market_data, position_data=None):
        """Extract ML features from market data and position history"""
        try:
            if len(market_data) < 20:
                return None
            
            latest = market_data.iloc[-1]
            
            # Technical indicator features
            features = {
                # Price action features
                'price_momentum_5': (latest['close'] - market_data['close'].iloc[-6]) / market_data['close'].iloc[-6],
                'price_momentum_10': (latest['close'] - market_data['close'].iloc[-11]) / market_data['close'].iloc[-11],
                'price_volatility': market_data['close'].tail(20).std() / market_data['close'].tail(20).mean(),
                
                # Moving average features
                'ma_alignment_score': self.calculate_ma_alignment_score(market_data),
                'price_above_ma9': 1 if latest['close'] > latest['ema_9'] else 0,
                'price_above_ma20': 1 if latest['close'] > latest['sma_20'] else 0,
                'price_above_ma50': 1 if latest['close'] > latest['ema_50'] else 0,
                
                # RSI features
                'rsi_value': latest['rsi'],
                'rsi_momentum': latest['rsi'] - market_data['rsi'].iloc[-6],
                'rsi_hierarchy_score': self.calculate_rsi_hierarchy_score(market_data),
                
                # Volume features
                'volume_ratio': latest['volume'] / latest['volume_ma'],
                'volume_momentum': (latest['volume'] - market_data['volume'].iloc[-6]) / market_data['volume'].iloc[-6],
                'pvi_momentum': (latest['pvi'] - market_data['pvi'].iloc[-6]) / market_data['pvi'].iloc[-6],
                
                # Trend features
                'lr_slope': latest['lr_slope'],
                'lr_slope_momentum': latest['lr_slope'] - market_data['lr_slope'].iloc[-6],
                'trend_strength': abs(latest['lr_slope']) * latest['volume'] / latest['volume_ma'],
                
                # Market timing features
                'hour_of_day': datetime.now().hour,
                'day_of_week': datetime.now().weekday(),
                'time_since_market_open': self.get_time_since_market_open(),
                
                # Volatility features
                'atr_ratio': self.calculate_atr_ratio(market_data),
                'price_range_ratio': (latest['high'] - latest['low']) / latest['close'],
            }
            
            # Add position-specific features if available
            if position_data:
                features.update({
                    'open_positions_count': len(position_data),
                    'avg_position_age': self.calculate_avg_position_age(position_data),
                    'current_portfolio_risk': self.calculate_portfolio_risk(position_data),
                })
            else:
                features.update({
                    'open_positions_count': 0,
                    'avg_position_age': 0,
                    'current_portfolio_risk': 0,
                })
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return None
    
    def calculate_ma_alignment_score(self, df):
        """Calculate moving average alignment score (0-1)"""
        try:
            latest = df.iloc[-1]
            if pd.isna(latest['wma_200']):
                return 0.5
            
            mas = [latest['ema_9'], latest['sma_20'], latest['ema_50'], latest['wma_200']]
            price = latest['close']
            
            # Check if price is above all MAs and they're in correct order
            above_all = all(price > ma for ma in mas if not pd.isna(ma))
            correct_order = (latest['ema_9'] > latest['sma_20'] > 
                           latest['ema_50'] > latest['wma_200'])
            
            if above_all and correct_order:
                return 1.0
            elif above_all:
                return 0.8
            elif price > latest['ema_9']:
                return 0.6
            else:
                return 0.2
        except:
            return 0.5
    
    def calculate_rsi_hierarchy_score(self, df):
        """Calculate RSI hierarchy alignment score (0-1)"""
        try:
            latest = df.iloc[-1]
            
            rsi_hierarchy = (latest['rsi'] > latest['rsi_ma_9'] > 
                           latest['rsi_ma_14'] > latest['rsi_ma_26'])
            
            if rsi_hierarchy:
                # Additional scoring based on RSI level
                if 50 <= latest['rsi'] <= 70:
                    return 1.0  # Optimal bullish zone
                elif 40 <= latest['rsi'] <= 80:
                    return 0.8  # Good zone
                else:
                    return 0.6  # Acceptable
            else:
                return 0.3
        except:
            return 0.5
    
    def get_time_since_market_open(self):
        """Get hours since market open"""
        now = datetime.now()
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        
        if now < market_open:
            return 0
        else:
            return (now - market_open).total_seconds() / 3600
    
    def calculate_atr_ratio(self, df):
        """Calculate Average True Range ratio"""
        try:
            if len(df) < 14:
                return 0.02
            
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift())
            low_close = abs(df['low'] - df['close'].shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(14).mean().iloc[-1]
            
            return atr / df['close'].iloc[-1]
        except:
            return 0.02
    
    def calculate_avg_position_age(self, positions):
        """Calculate average age of open positions in hours"""
        if not positions:
            return 0
        
        now = datetime.now()
        total_age = 0
        
        for pos in positions.values():
            if pos['status'] == 'OPEN':
                age = (now - pos['timestamp']).total_seconds() / 3600
                total_age += age
        
        return total_age / len(positions) if positions else 0
    
    def calculate_portfolio_risk(self, positions):
        """Calculate current portfolio risk exposure"""
        if not positions:
            return 0
        
        total_risk = 0
        for pos in positions.values():
            if pos['status'] == 'OPEN':
                position_value = pos['entry_price'] * pos['quantity']
                total_risk += position_value * 0.08  # 8% stop loss risk
        
        return total_risk
    
    def record_trade_outcome(self, symbol, features, signal_predicted, actual_outcome, pnl):
        """Record trade outcome for learning"""
        try:
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'features': features,
                'signal_predicted': signal_predicted,
                'actual_outcome': actual_outcome,  # 'profitable', 'loss', 'breakeven'
                'pnl': pnl,
                'pnl_percentage': pnl / (features.get('current_portfolio_risk', 1000) + 1000),
            }
            
            self.trading_history.append(trade_record)
            
            # Retrain model if we have enough samples
            if len(self.trading_history) >= self.min_samples_for_training:
                if (self.last_training_time is None or 
                    (datetime.now() - self.last_training_time).days >= 1):
                    self.retrain_models()
            
        except Exception as e:
            logger.error(f"Failed to record trade outcome: {e}")
    
    def predict_signal_quality(self, features):
        """Predict signal quality using ML model"""
        try:
            if not self.model_trained or features is None:
                return 0.5, "Model not trained"
            
            # Convert features to array
            feature_array = np.array([list(features.values())]).reshape(1, -1)
            feature_array = self.scaler.transform(feature_array)
            
            # Predict probability of profitable trade
            signal_proba = self.signal_classifier.predict_proba(feature_array)[0]
            profitable_probability = signal_proba[1] if len(signal_proba) > 1 else 0.5
            
            # Get confidence level
            confidence = max(signal_proba) - min(signal_proba)
            
            # Update stats
            self.ml_stats['total_predictions'] += 1
            self.ml_stats['model_confidence'] = confidence
            
            return profitable_probability, f"ML Confidence: {confidence:.2f}"
            
        except Exception as e:
            logger.error(f"Signal prediction failed: {e}")
            return 0.5, f"Prediction error: {str(e)[:50]}"
    
    def optimize_position_size(self, features, base_risk_amount):
        """Optimize position size using ML"""
        try:
            if not self.model_trained or features is None:
                return base_risk_amount
            
            # Convert features to array
            feature_array = np.array([list(features.values())]).reshape(1, -1)
            feature_array = self.scaler.transform(feature_array)
            
            # Predict optimal risk multiplier
            risk_multiplier = self.risk_optimizer.predict(feature_array)[0]
            
            # Constrain multiplier between 0.5 and 2.0
            risk_multiplier = max(0.5, min(2.0, risk_multiplier))
            
            optimized_amount = base_risk_amount * risk_multiplier
            
            return optimized_amount
            
        except Exception as e:
            logger.error(f"Position size optimization failed: {e}")
            return base_risk_amount
    
    def retrain_models(self):
        """Retrain ML models with recent trading data"""
        try:
            if len(self.trading_history) < self.min_samples_for_training:
                return False
            
            logger.info(f"🧠 Retraining ML models with {len(self.trading_history)} samples...")
            
            # Prepare training data
            X = []
            y_signals = []
            y_returns = []
            
            for trade in self.trading_history[-200:]:  # Use last 200 trades
                if trade['features'] is not None:
                    X.append(list(trade['features'].values()))
                    
                    # Signal classification target (profitable = 1, loss = 0)
                    y_signals.append(1 if trade['actual_outcome'] == 'profitable' else 0)
                    
                    # Return prediction target
                    y_returns.append(trade['pnl_percentage'])
            
            if len(X) < 20:
                return False
            
            X = np.array(X)
            y_signals = np.array(y_signals)
            y_returns = np.array(y_returns)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train signal classifier
            if len(np.unique(y_signals)) > 1:  # Need both classes
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y_signals, test_size=0.2, random_state=42
                )
                
                self.signal_classifier.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = self.signal_classifier.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                self.ml_stats['signal_accuracy'] = accuracy
                
                logger.info(f"✅ Signal classifier retrained - Accuracy: {accuracy:.2f}")
            
            # Train risk optimizer
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_returns, test_size=0.2, random_state=42
            )
            
            self.risk_optimizer.fit(X_train, y_train)
            
            # Evaluate risk model
            y_pred = self.risk_optimizer.predict(X_test)
            mse = np.mean((y_test - y_pred) ** 2)
            self.ml_stats['risk_prediction_error'] = mse
            
            logger.info(f"✅ Risk optimizer retrained - MSE: {mse:.4f}")
            
            # Update training status
            self.model_trained = True
            self.last_training_time = datetime.now()
            self.ml_stats['last_optimization_time'] = self.last_training_time
            
            # Save models
            self.save_models()
            
            return True
            
        except Exception as e:
            logger.error(f"Model retraining failed: {e}")
            return False
    
    def save_models(self):
        """Save trained models to disk"""
        try:
            joblib.dump(self.signal_classifier, f"{self.model_dir}/signal_classifier.pkl")
            joblib.dump(self.risk_optimizer, f"{self.model_dir}/risk_optimizer.pkl")
            joblib.dump(self.scaler, f"{self.model_dir}/feature_scaler.pkl")
            
            # Save trading history
            with open(f"{self.model_dir}/trading_history.pkl", 'wb') as f:
                pickle.dump(self.trading_history, f)
            
            # Save ML stats
            with open(f"{self.model_dir}/ml_stats.pkl", 'wb') as f:
                pickle.dump(self.ml_stats, f)
            
            logger.info("✅ ML models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            classifier_path = f"{self.model_dir}/signal_classifier.pkl"
            optimizer_path = f"{self.model_dir}/risk_optimizer.pkl"
            scaler_path = f"{self.model_dir}/feature_scaler.pkl"
            
            if all(os.path.exists(path) for path in [classifier_path, optimizer_path, scaler_path]):
                self.signal_classifier = joblib.load(classifier_path)
                self.risk_optimizer = joblib.load(optimizer_path)
                self.scaler = joblib.load(scaler_path)
                
                # Load trading history
                history_path = f"{self.model_dir}/trading_history.pkl"
                if os.path.exists(history_path):
                    with open(history_path, 'rb') as f:
                        self.trading_history = pickle.load(f)
                
                # Load ML stats
                stats_path = f"{self.model_dir}/ml_stats.pkl"
                if os.path.exists(stats_path):
                    with open(stats_path, 'rb') as f:
                        self.ml_stats = pickle.load(f)
                
                self.model_trained = True
                logger.info("✅ ML models loaded successfully")
                
            else:
                logger.info("📊 No existing ML models found - will train from scratch")
                
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
    
    def get_ml_insights(self):
        """Get current ML model insights"""
        if not self.model_trained:
            return "🧠 ML Models: Training... (need more data)"
        
        insights = f"""
🧠 ML OPTIMIZER STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Signal Accuracy: {self.ml_stats['signal_accuracy']:.1%}
🎯 Risk Prediction Error: {self.ml_stats['risk_prediction_error']:.4f}
💰 Profitable Predictions: {self.ml_stats['profitable_trades_predicted']}/{self.ml_stats['total_predictions']}
📈 Model Confidence: {self.ml_stats['model_confidence']:.2f}
🕐 Last Training: {self.ml_stats['last_optimization_time'].strftime('%Y-%m-%d %H:%M') if self.ml_stats['last_optimization_time'] else 'Never'}
📚 Training Samples: {len(self.trading_history)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return insights
    
    def get_trade_recommendation(self, symbol, market_data, positions):
        """Get ML-enhanced trade recommendation"""
        try:
            features = self.extract_features(market_data, positions)
            if features is None:
                return "HOLD", "Insufficient data for ML analysis", 1.0
            
            # Get ML prediction
            signal_quality, ml_explanation = self.predict_signal_quality(features)
            
            # Determine recommendation based on ML confidence
            if signal_quality >= 0.75:
                recommendation = "STRONG_BUY"
                explanation = f"🧠 ML HIGH CONFIDENCE: {signal_quality:.1%} profitable probability"
            elif signal_quality >= 0.60:
                recommendation = "BUY"
                explanation = f"🤖 ML MODERATE CONFIDENCE: {signal_quality:.1%} profitable probability"
            elif signal_quality >= 0.40:
                recommendation = "HOLD"
                explanation = f"⚠️ ML UNCERTAIN: {signal_quality:.1%} profitable probability"
            else:
                recommendation = "AVOID"
                explanation = f"🚨 ML NEGATIVE: {signal_quality:.1%} profitable probability"
            
            return recommendation, explanation, signal_quality
            
        except Exception as e:
            logger.error(f"ML recommendation failed: {e}")
            return "HOLD", f"ML error: {str(e)[:50]}", 0.5

# Alias for backward compatibility
MLOptimizer = MLTradingOptimizer
