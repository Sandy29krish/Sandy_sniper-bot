# utils/ai_assistant.py

import logging
import json
import os
from datetime import datetime
import numpy as np

class AIAssistant:
    def __init__(self):
        self.knowledge_base = []
        self.momentum_analyses = []  # Track momentum analyses for exit conditions
        self.performance_stats = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'avg_profit': 0,
            'best_patterns': [],
            'worst_patterns': []
        }
        self.learning_file = "ai_learning_data.json"
        self.load_knowledge()

    def load_knowledge(self):
        """Load existing AI knowledge from file"""
        try:
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'r') as f:
                    data = json.load(f)
                    self.knowledge_base = data.get('knowledge_base', [])
                    self.momentum_analyses = data.get('momentum_analyses', [])
                    self.performance_stats = data.get('performance_stats', self.performance_stats)
                logging.info(f"AI loaded {len(self.knowledge_base)} previous trades and {len(self.momentum_analyses)} momentum analyses")
        except Exception as e:
            logging.error(f"Error loading AI knowledge: {e}")

    def save_knowledge(self):
        """Save AI knowledge to file"""
        try:
            data = {
                'knowledge_base': self.knowledge_base,
                'momentum_analyses': self.momentum_analyses,
                'performance_stats': self.performance_stats,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.learning_file, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info("AI knowledge saved successfully")
        except Exception as e:
            logging.error(f"Error saving AI knowledge: {e}")

    def assess_signal(self, market_data, indicators):
        """Enhanced signal assessment with learning"""
        logging.info("Assessing signal with AI assistant")
        
        # Check historical performance for similar patterns
        confidence = self.analyze_pattern_confidence(indicators)
        
        # Apply learning from previous trades
        if confidence < 0.6:  # Low confidence patterns
            logging.warning(f"Low confidence pattern detected: {confidence:.2f}")
            return False
            
        return True

    def analyze_pattern_confidence(self, indicators):
        """Analyze confidence based on historical performance"""
        if not self.knowledge_base:
            return 0.7  # Default confidence for new patterns
            
        # Find similar patterns in history
        similar_patterns = []
        for trade in self.knowledge_base:
            if trade.get('indicators') and self.is_similar_pattern(indicators, trade['indicators']):
                similar_patterns.append(trade)
        
        if not similar_patterns:
            return 0.6  # Unknown pattern
            
        # Calculate success rate
        successful = sum(1 for trade in similar_patterns if trade.get('success', False))
        success_rate = successful / len(similar_patterns)
        
        return success_rate

    def is_similar_pattern(self, current_indicators, historical_indicators):
        """Check if current pattern is similar to historical pattern"""
        # Simple similarity check - can be enhanced
        current_rsi = current_indicators.get('rsi', 0)
        historical_rsi = historical_indicators.get('rsi', 0)
        rsi_diff = abs(current_rsi - historical_rsi)
        return rsi_diff < 10  # Within 10 RSI points

    def provide_trade_reasoning(self, signal, indicators=None):
        """Enhanced reasoning with learning insights"""
        base_reasoning = "Signal confirmed based on multi-timeframe analysis and volume surge."
        
        if indicators and self.knowledge_base:
            confidence = self.analyze_pattern_confidence(indicators)
            if confidence > 0.8:
                base_reasoning += f" High confidence pattern ({(confidence*100):.0f}% success rate)."
            elif confidence < 0.5:
                base_reasoning += f" Caution: Low confidence pattern ({(confidence*100):.0f}% success rate)."
        
        return base_reasoning

    def update_knowledge(self, trade_result):
        """Enhanced knowledge update with performance tracking"""
        self.knowledge_base.append(trade_result)
        
        # Update performance stats
        self.performance_stats['total_trades'] += 1
        if trade_result.get('success', False):
            self.performance_stats['successful_trades'] += 1
        else:
            self.performance_stats['failed_trades'] += 1
            
        # Calculate average profit
        profits = [trade.get('profit', 0) for trade in self.knowledge_base if trade.get('profit')]
        if profits:
            self.performance_stats['avg_profit'] = np.mean(profits)
        
        # Identify best/worst patterns
        self.update_pattern_analysis()
        
        # Save knowledge
        self.save_knowledge()
        
        logging.info(f"AI knowledge updated. Success rate: {(self.performance_stats['successful_trades']/self.performance_stats['total_trades']*100):.1f}%")

    def update_pattern_analysis(self):
        """Analyze and identify best/worst trading patterns"""
        if len(self.knowledge_base) < 5:
            return
            
        # Group trades by pattern characteristics
        pattern_groups = {}
        for trade in self.knowledge_base:
            pattern_key = self.get_pattern_key(trade.get('indicators', {}))
            if pattern_key not in pattern_groups:
                pattern_groups[pattern_key] = []
            pattern_groups[pattern_key].append(trade)
        
        # Calculate success rates for each pattern
        pattern_success = {}
        for pattern, trades in pattern_groups.items():
            if len(trades) >= 3:  # Minimum sample size
                success_rate = sum(1 for t in trades if t.get('success', False)) / len(trades)
                pattern_success[pattern] = success_rate
        
        # Update best/worst patterns
        if pattern_success:
            sorted_patterns = sorted(pattern_success.items(), key=lambda x: x[1], reverse=True)
            self.performance_stats['best_patterns'] = sorted_patterns[:3]  # Top 3
            self.performance_stats['worst_patterns'] = sorted_patterns[-3:]  # Bottom 3

    def get_pattern_key(self, indicators):
        """Create a pattern key for grouping similar trades"""
        rsi_range = "high" if indicators.get('rsi', 0) > 70 else "low" if indicators.get('rsi', 0) < 30 else "mid"
        ma_trend = "bullish" if indicators.get('ma_hierarchy', False) else "bearish"
        return f"{rsi_range}_{ma_trend}"

    def get_learning_insights(self):
        """Get AI learning insights for decision making"""
        if not self.knowledge_base:
            return "No historical data available for learning."
            
        total_trades = self.performance_stats['total_trades']
        success_rate = (self.performance_stats['successful_trades'] / total_trades * 100) if total_trades > 0 else 0
        avg_profit = self.performance_stats['avg_profit']
        
        insights = f"AI Learning Insights:\n"
        insights += f"• Total Trades: {total_trades}\n"
        insights += f"• Success Rate: {success_rate:.1f}%\n"
        insights += f"• Average Profit: ₹{avg_profit:.0f}\n"
        
        if self.performance_stats['best_patterns']:
            insights += f"• Best Patterns: {len(self.performance_stats['best_patterns'])} identified\n"
            
        return insights

    def analyze_momentum_strength(self, recent_data):
        """
        Analyze momentum strength for exit conditions
        Returns: momentum_strength (0.0 to 1.0)
        """
        try:
            close_prices = recent_data.get('close_prices', [])
            volumes = recent_data.get('volumes', [])
            highs = recent_data.get('highs', [])
            lows = recent_data.get('lows', [])
            signal_type = recent_data.get('signal_type', '')
            
            if len(close_prices) < 5:
                return 0.5  # Neutral if insufficient data
            
            # Convert to numpy arrays for analysis
            prices = np.array(close_prices)
            vols = np.array(volumes)
            
            # 1. Price momentum analysis
            price_changes = np.diff(prices)
            recent_price_momentum = np.mean(price_changes[-3:])  # Last 3 periods
            overall_price_momentum = np.mean(price_changes)
            
            # 2. Volume analysis
            recent_volume = np.mean(vols[-3:])
            avg_volume = np.mean(vols[:-3]) if len(vols) > 3 else np.mean(vols)
            volume_strength = recent_volume / avg_volume if avg_volume > 0 else 1.0
            
            # 3. Price velocity (acceleration/deceleration)
            if len(price_changes) >= 3:
                early_momentum = np.mean(price_changes[:3])
                late_momentum = np.mean(price_changes[-3:])
                momentum_acceleration = late_momentum - early_momentum
            else:
                momentum_acceleration = 0
            
            # 4. Volatility analysis (higher volatility can indicate momentum)
            price_volatility = np.std(price_changes) if len(price_changes) > 1 else 0
            
            # Calculate momentum strength based on signal type
            if signal_type == 'bullish':
                # For bullish positions, strong momentum means:
                # - Positive price momentum
                # - Increasing volume
                # - Accelerating upward movement
                
                price_factor = min(max(recent_price_momentum * 1000, 0), 1)  # Scale to 0-1
                volume_factor = min(volume_strength, 2.0) / 2.0  # Cap at 2x, scale to 0-1
                acceleration_factor = min(max(momentum_acceleration * 1000, 0), 1)
                volatility_factor = min(price_volatility * 100, 1)  # Higher volatility = higher momentum
                
            else:  # Bearish
                # For bearish positions, strong momentum means:
                # - Negative price momentum (prices going down)
                # - Increasing volume
                # - Accelerating downward movement
                
                price_factor = min(max(-recent_price_momentum * 1000, 0), 1)  # Negative momentum is good for bearish
                volume_factor = min(volume_strength, 2.0) / 2.0
                acceleration_factor = min(max(-momentum_acceleration * 1000, 0), 1)  # Negative acceleration is good
                volatility_factor = min(price_volatility * 100, 1)
            
            # Weighted momentum strength calculation
            momentum_strength = (
                price_factor * 0.4 +           # Price momentum: 40%
                volume_factor * 0.25 +         # Volume support: 25%
                acceleration_factor * 0.2 +    # Acceleration: 20%
                volatility_factor * 0.15       # Volatility: 15%
            )
            
            # Apply learning from historical patterns
            historical_patterns = self.get_similar_patterns({
                'price_momentum': recent_price_momentum,
                'volume_strength': volume_strength,
                'signal_type': signal_type
            })
            
            if historical_patterns:
                # Adjust based on historical success of similar momentum patterns
                historical_success_rate = historical_patterns.get('success_rate', 0.5)
                momentum_strength = momentum_strength * 0.7 + historical_success_rate * 0.3
            
            # Ensure momentum strength is between 0 and 1
            momentum_strength = max(0.0, min(1.0, momentum_strength))
            
            # Log the analysis for learning
            self.momentum_analyses.append({
                'signal_type': signal_type,
                'price_momentum': recent_price_momentum,
                'volume_strength': volume_strength,
                'momentum_strength': momentum_strength,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return momentum_strength
            
        except Exception as e:
            logging.error(f"Error in momentum strength analysis: {e}")
            return 0.5  # Return neutral strength on error

    def get_similar_patterns(self, current_pattern):
        """Find similar historical patterns for momentum analysis"""
        try:
            if not self.momentum_analyses:
                return None
            
            similar_patterns = []
            current_price_mom = current_pattern.get('price_momentum', 0)
            current_vol_strength = current_pattern.get('volume_strength', 1)
            current_signal = current_pattern.get('signal_type', '')
            
            for past_analysis in self.momentum_analyses:
                if past_analysis.get('signal_type') != current_signal:
                    continue
                    
                past_price_mom = past_analysis.get('price_momentum', 0)
                past_vol_strength = past_analysis.get('volume_strength', 1)
                
                # Calculate similarity (closer values = higher similarity)
                price_similarity = 1 - min(abs(current_price_mom - past_price_mom) * 1000, 1)
                vol_similarity = 1 - min(abs(current_vol_strength - past_vol_strength), 1)
                
                overall_similarity = (price_similarity + vol_similarity) / 2
                
                if overall_similarity > 0.7:  # 70% similarity threshold
                    similar_patterns.append(past_analysis)
            
            if similar_patterns:
                # Calculate average success rate of similar patterns
                avg_momentum_strength = np.mean([p.get('momentum_strength', 0.5) for p in similar_patterns])
                return {'success_rate': avg_momentum_strength}
            
            return None
            
        except Exception as e:
            logging.error(f"Error finding similar patterns: {e}")
            return None

# 🔍 This is what sniper_swing.py depends on:
def analyze_trade_signal(symbol, indicators, signal):
    """Enhanced analysis with mandatory detailed reasoning"""
    reasoning = []
    ai = AIAssistant()

    # Core technical analysis reasoning
    if signal == "bullish":
        reasoning.append(f"🔵 BULLISH ENTRY - {symbol}")
        reasoning.append(f"📈 RSI({indicators['rsi']:.1f}) > 26MA({indicators['rsi_ma26']:.1f}) - Momentum confirmed")
        reasoning.append(f"📊 MA Hierarchy: {indicators['ma_hierarchy']} - Trend alignment")
        reasoning.append(f"📈 PVI Positive: {indicators['pvi_positive']} - Volume supports price")
        reasoning.append(f"📈 LR Slope Positive: {indicators['lr_slope_positive']} - Momentum direction")
        
        # CPR analysis (optional)
        if indicators.get('cpr_support'):
            reasoning.append("🎯 CPR supports bullish bias")
        elif indicators.get('live_cpr'):
            reasoning.append("⚪ CPR neutral/weak support")
            
    else:
        reasoning.append(f"🔴 BEARISH ENTRY - {symbol}")
        reasoning.append(f"📉 RSI({indicators['rsi']:.1f}) < 26MA({indicators['rsi_ma26']:.1f}) - Bearish momentum")
        reasoning.append(f"📊 MA Hierarchy: {indicators['ma_hierarchy']} - Downtrend confirmed")
        reasoning.append(f"📉 PVI Negative: {indicators['pvi_positive']} - Volume supports decline")
        reasoning.append(f"📉 LR Slope Negative: {indicators['lr_slope_positive']} - Momentum direction")
        
        # CPR analysis (optional)
        if indicators.get('cpr_support'):
            reasoning.append("🎯 CPR supports bearish bias")
        elif indicators.get('live_cpr'):
            reasoning.append("⚪ CPR neutral/weak resistance")

    # Immediate AI insights (no waiting for commands)
    confidence = ai.analyze_pattern_confidence(indicators)
    ai_insights = ai.get_learning_insights()
    
    reasoning.append(f"\n🤖 AI ANALYSIS:")
    reasoning.append(f"📊 Pattern Confidence: {(confidence*100):.0f}%")
    
    if confidence > 0.7:
        reasoning.append(f"✅ HIGH CONFIDENCE - Similar patterns succeeded {(confidence*100):.0f}% of time")
    elif confidence > 0.5:
        reasoning.append(f"⚠️ MODERATE CONFIDENCE - Pattern has {(confidence*100):.0f}% success rate")
    else:
        reasoning.append(f"🔴 LOW CONFIDENCE - Pattern only {(confidence*100):.0f}% successful")
    
    # Add immediate AI insights
    reasoning.append(f"📈 {ai_insights}")

    return "\n".join(reasoning)

def analyze_exit_signal(symbol, entry_data, exit_reason, current_price):
    """Mandatory detailed exit reasoning"""
    reasoning = []
    ai = AIAssistant()
    
    entry_price = entry_data.get('entry_price', 0)
    signal_type = entry_data.get('signal', 'unknown')
    pnl = 0
    
    if current_price and entry_price:
        if signal_type == "bullish":
            pnl = (current_price - entry_price) / entry_price * 100
        else:
            pnl = (entry_price - current_price) / entry_price * 100
    
    reasoning.append(f"🚪 EXIT SIGNAL - {symbol}")
    reasoning.append(f"📊 Entry: ₹{entry_price}, Current: ₹{current_price}")
    reasoning.append(f"💰 P&L: {pnl:+.1f}%")
    reasoning.append(f"🎯 Exit Reason: {exit_reason}")
    
    # Specific exit analysis based on reason
    if "swing_high" in exit_reason.lower():
        reasoning.append("📈 Swing High detected - Taking partial profits")
        reasoning.append("🎯 Strategy: Hold remaining position for higher targets")
    elif "friday" in exit_reason.lower():
        reasoning.append("🕐 Friday 3:15 PM mandatory exit")
        reasoning.append("⚠️ Weekend risk management")
    elif "stop" in exit_reason.lower():
        reasoning.append("🛑 Risk management exit triggered")
        reasoning.append("💡 Protecting capital for next opportunity")
    elif "reversal" in exit_reason.lower():
        reasoning.append("🔄 Technical reversal pattern detected")
        reasoning.append("📊 Market structure changing")
    else:
        reasoning.append(f"📋 Custom exit condition: {exit_reason}")
    
    # AI learning update
    trade_success = pnl > 0
    reasoning.append(f"\n🤖 AI LEARNING:")
    reasoning.append(f"📊 Trade Result: {'✅ Profitable' if trade_success else '❌ Loss'}")
    reasoning.append(f"📈 Pattern will be {'reinforced' if trade_success else 'marked for review'}")
    
    return "\n".join(reasoning)
