"""
Signal Strength Analyzer
Analyzes and ranks trading signals based on multiple technical indicators
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class SignalAnalysis:
    """Container for signal analysis results"""
    symbol: str
    signal_type: str
    total_strength: float
    strength_grade: str
    component_scores: Dict[str, float]
    confidence_level: str
    indicators: Dict

# Signal strength thresholds
STRENGTH_THRESHOLDS = {
    'SUPER_STRONG': 9.0,
    'VERY_STRONG': 8.0,
    'STRONG': 7.0,
    'MODERATE': 5.0,
    'WEAK': 3.0
}

# Component weights for signal strength calculation
COMPONENT_WEIGHTS = {
    'trend_alignment': 0.25,
    'momentum_strength': 0.20,
    'volume_confirmation': 0.15,
    'support_resistance': 0.15,
    'rsi_position': 0.10,
    'moving_average_confluence': 0.10,
    'volatility_factor': 0.05
}

def analyze_signal_strength(symbol: str, signal_type: str, indicators: Dict) -> SignalAnalysis:
    """
    Analyze the strength of a trading signal based on multiple technical factors
    
    Args:
        symbol: Trading symbol (e.g., 'NIFTY')
        signal_type: 'bullish' or 'bearish'
        indicators: Dictionary containing technical indicators
    
    Returns:
        SignalAnalysis object with strength assessment
    """
    try:
        component_scores = {}
        
        # 1. Trend Alignment Score (0-10)
        component_scores['trend_alignment'] = _calculate_trend_alignment_score(indicators, signal_type)
        
        # 2. Momentum Strength Score (0-10)
        component_scores['momentum_strength'] = _calculate_momentum_score(indicators, signal_type)
        
        # 3. Volume Confirmation Score (0-10)
        component_scores['volume_confirmation'] = _calculate_volume_score(indicators)
        
        # 4. Support/Resistance Score (0-10)
        component_scores['support_resistance'] = _calculate_support_resistance_score(indicators, signal_type)
        
        # 5. RSI Position Score (0-10)
        component_scores['rsi_position'] = _calculate_rsi_score(indicators, signal_type)
        
        # 6. Moving Average Confluence Score (0-10)
        component_scores['moving_average_confluence'] = _calculate_ma_confluence_score(indicators, signal_type)
        
        # 7. Volatility Factor Score (0-10)
        component_scores['volatility_factor'] = _calculate_volatility_score(indicators)
        
        # Calculate weighted total strength
        total_strength = sum(
            score * COMPONENT_WEIGHTS.get(component, 0.1)
            for component, score in component_scores.items()
        ) * 10  # Scale to 0-10
        
        # Determine strength grade
        strength_grade = _get_strength_grade(total_strength)
        
        # Determine confidence level
        confidence_level = _get_confidence_level(component_scores)
        
        return SignalAnalysis(
            symbol=symbol,
            signal_type=signal_type,
            total_strength=total_strength,
            strength_grade=strength_grade,
            component_scores=component_scores,
            confidence_level=confidence_level,
            indicators=indicators
        )
        
    except Exception as e:
        logger.error(f"Error analyzing signal strength for {symbol}: {e}")
        return SignalAnalysis(
            symbol=symbol,
            signal_type=signal_type,
            total_strength=0.0,
            strength_grade='ERROR',
            component_scores={},
            confidence_level='LOW',
            indicators=indicators
        )

def _calculate_trend_alignment_score(indicators: Dict, signal_type: str) -> float:
    """Calculate trend alignment score (0-10)"""
    try:
        score = 0.0
        
        # MA hierarchy alignment
        if indicators.get('ma_hierarchy', False):
            score += 3.0
        
        # Linear regression slope alignment
        lr_slope = indicators.get('lr_slope_positive', False)
        if (signal_type == 'bullish' and lr_slope) or (signal_type == 'bearish' and not lr_slope):
            score += 2.5
        
        # Price vs MA position
        price = indicators.get('close', 0)
        ema_9 = indicators.get('ema_9', 0)
        if price and ema_9:
            if (signal_type == 'bullish' and price > ema_9) or (signal_type == 'bearish' and price < ema_9):
                score += 2.0
        
        # Trend strength from ADX if available
        adx = indicators.get('adx', 0)
        if adx > 25:  # Strong trend
            score += 2.5
        elif adx > 20:  # Moderate trend
            score += 1.5
        
        return min(score, 10.0)
        
    except Exception as e:
        logger.error(f"Error calculating trend alignment score: {e}")
        return 0.0

def _calculate_momentum_score(indicators: Dict, signal_type: str) -> float:
    """Calculate momentum strength score (0-10)"""
    try:
        score = 0.0
        
        # RSI momentum
        rsi = indicators.get('rsi', 50)
        rsi_ma = indicators.get('rsi_ma26', 50)
        
        if signal_type == 'bullish':
            if rsi > rsi_ma:
                score += 3.0
            if rsi > 60:
                score += 2.0
        else:  # bearish
            if rsi < rsi_ma:
                score += 3.0
            if rsi < 40:
                score += 2.0
        
        # MACD if available
        macd_line = indicators.get('macd_line', 0)
        macd_signal = indicators.get('macd_signal', 0)
        if macd_line and macd_signal:
            if (signal_type == 'bullish' and macd_line > macd_signal) or \
               (signal_type == 'bearish' and macd_line < macd_signal):
                score += 2.5
        
        # Stochastic if available
        stoch_k = indicators.get('stoch_k', 50)
        stoch_d = indicators.get('stoch_d', 50)
        if stoch_k and stoch_d:
            if (signal_type == 'bullish' and stoch_k > stoch_d and stoch_k > 20) or \
               (signal_type == 'bearish' and stoch_k < stoch_d and stoch_k < 80):
                score += 2.5
        
        return min(score, 10.0)
        
    except Exception as e:
        logger.error(f"Error calculating momentum score: {e}")
        return 0.0

def _calculate_volume_score(indicators: Dict) -> float:
    """Calculate volume confirmation score (0-10)"""
    try:
        score = 0.0
        
        # PVI (Positive Volume Index) positive
        if indicators.get('pvi_positive', False):
            score += 5.0
        
        # Volume trend
        volume = indicators.get('volume', 0)
        volume_ma = indicators.get('volume_ma', 0)
        if volume and volume_ma and volume > volume_ma:
            score += 3.0
        
        # Volume spike detection
        if volume and volume_ma:
            volume_ratio = volume / volume_ma if volume_ma > 0 else 1.0
            if volume_ratio > 1.5:  # 50% above average
                score += 2.0
            elif volume_ratio > 1.2:  # 20% above average
                score += 1.0
        
        return min(score, 10.0)
        
    except Exception as e:
        logger.error(f"Error calculating volume score: {e}")
        return 0.0

def _calculate_support_resistance_score(indicators: Dict, signal_type: str) -> float:
    """Calculate support/resistance alignment score (0-10)"""
    try:
        score = 0.0
        
        # CPR (Central Pivot Range) analysis if available
        cpr_support = indicators.get('cpr_support', 0)
        cpr_resistance = indicators.get('cpr_resistance', 0)
        price = indicators.get('close', 0)
        
        if price and cpr_support and cpr_resistance:
            if signal_type == 'bullish' and price > cpr_resistance:
                score += 4.0
            elif signal_type == 'bullish' and price > cpr_support:
                score += 2.0
            elif signal_type == 'bearish' and price < cpr_support:
                score += 4.0
            elif signal_type == 'bearish' and price < cpr_resistance:
                score += 2.0
        
        # Bollinger Bands position if available
        bb_upper = indicators.get('bb_upper', 0)
        bb_lower = indicators.get('bb_lower', 0)
        bb_middle = indicators.get('bb_middle', 0)
        
        if price and bb_upper and bb_lower:
            if signal_type == 'bullish' and price > bb_middle:
                score += 2.0
            elif signal_type == 'bearish' and price < bb_middle:
                score += 2.0
        
        # Key level proximity (simplified)
        # This would ideally check proximity to major support/resistance levels
        score += 2.0  # Base score for level awareness
        
        return min(score, 10.0)
        
    except Exception as e:
        logger.error(f"Error calculating support/resistance score: {e}")
        return 0.0

def _calculate_rsi_score(indicators: Dict, signal_type: str) -> float:
    """Calculate RSI position score (0-10)"""
    try:
        rsi = indicators.get('rsi', 50)
        score = 0.0
        
        if signal_type == 'bullish':
            if 30 <= rsi <= 70:  # Not overbought, good for bullish
                score += 5.0
            elif rsi < 30:  # Oversold, potentially good for reversal
                score += 7.0
            elif rsi > 70:  # Overbought, risky for bullish
                score += 2.0
        else:  # bearish
            if 30 <= rsi <= 70:  # Not oversold, good for bearish
                score += 5.0
            elif rsi > 70:  # Overbought, potentially good for reversal
                score += 7.0
            elif rsi < 30:  # Oversold, risky for bearish
                score += 2.0
        
        # RSI vs RSI MA alignment
        rsi_ma = indicators.get('rsi_ma26', 50)
        if (signal_type == 'bullish' and rsi > rsi_ma) or \
           (signal_type == 'bearish' and rsi < rsi_ma):
            score += 3.0
        
        return min(score, 10.0)
        
    except Exception as e:
        logger.error(f"Error calculating RSI score: {e}")
        return 0.0

def _calculate_ma_confluence_score(indicators: Dict, signal_type: str) -> float:
    """Calculate moving average confluence score (0-10)"""
    try:
        score = 0.0
        
        # MA hierarchy
        if indicators.get('ma_hierarchy', False):
            score += 4.0
        
        # Price vs key MAs
        price = indicators.get('close', 0)
        ema_9 = indicators.get('ema_9', 0)
        ema_21 = indicators.get('ema_21', 0)
        
        if price and ema_9 and ema_21:
            if signal_type == 'bullish':
                if price > ema_9 > ema_21:
                    score += 3.0
                elif price > ema_9:
                    score += 1.5
            else:  # bearish
                if price < ema_9 < ema_21:
                    score += 3.0
                elif price < ema_9:
                    score += 1.5
        
        # MA separation (wider separation = stronger trend)
        if ema_9 and ema_21:
            separation_pct = abs(ema_9 - ema_21) / ema_21 * 100 if ema_21 > 0 else 0
            if separation_pct > 2.0:
                score += 3.0
            elif separation_pct > 1.0:
                score += 1.5
        
        return min(score, 10.0)
        
    except Exception as e:
        logger.error(f"Error calculating MA confluence score: {e}")
        return 0.0

def _calculate_volatility_score(indicators: Dict) -> float:
    """Calculate volatility factor score (0-10)"""
    try:
        score = 5.0  # Base score
        
        # ATR-based volatility if available
        atr = indicators.get('atr', 0)
        price = indicators.get('close', 0)
        
        if atr and price:
            volatility_pct = (atr / price) * 100
            if 1.0 <= volatility_pct <= 3.0:  # Optimal volatility range
                score += 3.0
            elif volatility_pct < 0.5:  # Too low volatility
                score -= 2.0
            elif volatility_pct > 5.0:  # Too high volatility
                score -= 2.0
        
        # Bollinger Band width if available
        bb_upper = indicators.get('bb_upper', 0)
        bb_lower = indicators.get('bb_lower', 0)
        bb_middle = indicators.get('bb_middle', 0)
        
        if bb_upper and bb_lower and bb_middle:
            bb_width = (bb_upper - bb_lower) / bb_middle * 100
            if 2.0 <= bb_width <= 8.0:  # Good volatility range
                score += 2.0
        
        return max(min(score, 10.0), 0.0)
        
    except Exception as e:
        logger.error(f"Error calculating volatility score: {e}")
        return 5.0

def _get_strength_grade(total_strength: float) -> str:
    """Get strength grade based on total strength score"""
    if total_strength >= STRENGTH_THRESHOLDS['SUPER_STRONG']:
        return 'SUPER_STRONG'
    elif total_strength >= STRENGTH_THRESHOLDS['VERY_STRONG']:
        return 'VERY_STRONG'
    elif total_strength >= STRENGTH_THRESHOLDS['STRONG']:
        return 'STRONG'
    elif total_strength >= STRENGTH_THRESHOLDS['MODERATE']:
        return 'MODERATE'
    else:
        return 'WEAK'

def _get_confidence_level(component_scores: Dict[str, float]) -> str:
    """Get confidence level based on component score consistency"""
    try:
        scores = list(component_scores.values())
        if not scores:
            return 'LOW'
        
        avg_score = np.mean(scores)
        std_score = np.std(scores)
        
        # Lower standard deviation = higher confidence
        if avg_score >= 7.0 and std_score <= 1.5:
            return 'VERY_HIGH'
        elif avg_score >= 6.0 and std_score <= 2.0:
            return 'HIGH'
        elif avg_score >= 5.0 and std_score <= 2.5:
            return 'MEDIUM'
        else:
            return 'LOW'
            
    except Exception as e:
        logger.error(f"Error calculating confidence level: {e}")
        return 'LOW'

def rank_trading_signals(signal_candidates: List[Dict]) -> List[Dict]:
    """
    Rank trading signals by strength and return sorted list
    
    Args:
        signal_candidates: List of signal candidate dictionaries
    
    Returns:
        List of ranked signals with strength analysis
    """
    try:
        ranked_signals = []
        
        for candidate in signal_candidates:
            symbol = candidate['symbol']
            signal_type = candidate['signal_type']
            indicators = candidate['indicators']
            
            # Analyze signal strength
            analysis = analyze_signal_strength(symbol, signal_type, indicators)
            
            # Only include signals above minimum threshold
            if analysis.total_strength >= STRENGTH_THRESHOLDS['STRONG']:
                ranked_signals.append({
                    'symbol': symbol,
                    'signal_type': signal_type,
                    'total_strength': analysis.total_strength,
                    'strength_grade': analysis.strength_grade,
                    'confidence_level': analysis.confidence_level,
                    'component_scores': analysis.component_scores,
                    'indicators': indicators,
                    'analysis': analysis
                })
        
        # Sort by total strength (descending)
        ranked_signals.sort(key=lambda x: x['total_strength'], reverse=True)
        
        logger.info(f"📊 Ranked {len(ranked_signals)} signals from {len(signal_candidates)} candidates")
        
        return ranked_signals
        
    except Exception as e:
        logger.error(f"Error ranking trading signals: {e}")
        return []

def signal_strength_analyzer(symbol: str, signal_type: str, indicators: Dict) -> Dict:
    """
    Legacy wrapper function for backward compatibility
    """
    analysis = analyze_signal_strength(symbol, signal_type, indicators)
    return {
        'strength': analysis.total_strength,
        'grade': analysis.strength_grade,
        'confidence': analysis.confidence_level,
        'components': analysis.component_scores
    }

def get_signal_strength_summary(analysis: SignalAnalysis) -> str:
    """Get formatted summary of signal strength analysis"""
    try:
        summary = f"🎯 {analysis.symbol} {analysis.signal_type.upper()} Signal Analysis\n\n"
        summary += f"📊 Total Strength: {analysis.total_strength:.2f}/10\n"
        summary += f"🏆 Grade: {analysis.strength_grade}\n"
        summary += f"🎖️ Confidence: {analysis.confidence_level}\n\n"
        
        summary += "📈 Component Breakdown:\n"
        for component, score in analysis.component_scores.items():
            component_name = component.replace('_', ' ').title()
            emoji = "🟢" if score >= 7 else "🟡" if score >= 5 else "🔴"
            summary += f"{emoji} {component_name}: {score:.1f}/10\n"
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating signal summary: {e}")
        return f"❌ Error generating summary for {analysis.symbol}"

if __name__ == "__main__":
    # Test the signal strength analyzer
    print("=== Signal Strength Analyzer Test ===")
    
    # Sample indicators for testing
    test_indicators = {
        'rsi': 65.5,
        'rsi_ma26': 60.2,
        'ma_hierarchy': True,
        'pvi_positive': True,
        'lr_slope_positive': True,
        'close': 19500,
        'ema_9': 19450,
        'ema_21': 19400,
        'volume': 1000000,
        'volume_ma': 800000,
        'atr': 150,
        'adx': 28
    }
    
    # Test signal analysis
    analysis = analyze_signal_strength('NIFTY', 'bullish', test_indicators)
    print(get_signal_strength_summary(analysis))
    
    # Test ranking
    candidates = [
        {'symbol': 'NIFTY', 'signal_type': 'bullish', 'indicators': test_indicators},
        {'symbol': 'BANKNIFTY', 'signal_type': 'bearish', 'indicators': {**test_indicators, 'rsi': 35}}
    ]
    
    ranked = rank_trading_signals(candidates)
    print(f"\nRanked {len(ranked)} signals")
    for i, signal in enumerate(ranked, 1):
        print(f"{i}. {signal['symbol']} - {signal['strength_grade']} ({signal['total_strength']:.2f})")
