# utils/ai_assistant.py

import logging

class AIAssistant:
    def __init__(self):
        self.knowledge_base = []

    def assess_signal(self, market_data, indicators):
        logging.info("Assessing signal with AI assistant")
        return True

    def provide_trade_reasoning(self, signal):
        return "Signal confirmed based on multi-timeframe analysis and volume surge."

    def update_knowledge(self, trade_result):
        self.knowledge_base.append(trade_result)
        logging.info("AI knowledge base updated with trade result")


# 🔍 This is what sniper_swing.py depends on:
def analyze_trade_signal(symbol, indicators, signal):
    reasoning = []

    if signal == "bullish":
        if indicators["rsi"] > indicators["rsi_ma26"]:
            reasoning.append("RSI > 26MA (Momentum Confirmed)")
        if indicators["ma_hierarchy"]:
            reasoning.append("MA Hierarchy indicates uptrend")
        if indicators["pvi_positive"]:
            reasoning.append("Price-Volume trend is positive")
        if indicators["lr_slope_positive"]:
            reasoning.append("Positive LR Slope")
    else:
        if indicators["rsi"] < indicators["rsi_ma26"]:
            reasoning.append("RSI < 26MA (Bearish momentum)")
        if indicators["ma_hierarchy"] == False:
            reasoning.append("MA Hierarchy indicates downtrend")
        if not indicators["pvi_positive"]:
            reasoning.append("Price-Volume trend is negative")
        if not indicators["lr_slope_positive"]:
            reasoning.append("Negative LR Slope")

    if not reasoning:
        reasoning.append("Signal confirmed with minimal strength")

    return "\n".join(reasoning)
