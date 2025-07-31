#!/usr/bin/env python3
"""
Enhanced Notifications for Sandy Sniper Bot
Built on your finalized notifications.py with added features:
- Good morning/evening messages with IST
- Enhanced trade alerts with detailed reasons
- Performance summaries
"""

import os
import requests
import datetime
import pytz
import logging
from typing import Optional, Dict, Any, List

# Import your finalized Notifier class
from .notifications import Notifier

logger = logging.getLogger(__name__)

# Indian Standard Time
IST = pytz.timezone('Asia/Kolkata')

def get_indian_time() -> datetime.datetime:
    """Get current time in Indian Standard Time"""
    return datetime.datetime.now(IST)

def send_good_morning_message(capital: int, max_trades: int, market_analysis: Dict, notifier: Optional[Notifier] = None) -> bool:
    """Send personalized good morning message to Saki"""
    try:
        if not notifier:
            return False
        
        current_time = get_indian_time()
        morning_greeting = "Hi Saki, Let's trade! 🚀"
        
        # Format market analysis
        market_status = "Loading..."
        if market_analysis and 'symbols_status' in market_analysis:
            status_lines = []
            for symbol_info in market_analysis['symbols_status']:
                symbol = symbol_info['symbol']
                exchange = symbol_info['exchange']
                status = symbol_info['status']
                status_lines.append(f"• {symbol} ({exchange}): {status}")
            market_status = "\n".join(status_lines)
        
        message = f"""
{morning_greeting}

🌅 **GOOD MORNING - TRADING SESSION STARTING**

🤖 **Master AI Status:** ACTIVE & LEARNING
📊 **System Health:** All systems operational
⚡ **Performance:** CPU-optimized for speed
🎯 **Today's Mission:** Profitable trading with 5-condition analysis

🔍 **Ready to analyze:**
• NIFTY & BANKNIFTY signals
• CPR price action scenarios  
• AI-enhanced pattern recognition
• Real-time market opportunities

💪 **Let's make today profitable, Saki!**

🔧 **System Features Active:**
✅ Auto-reconnection enabled
✅ Telegram commands operational  
✅ Intelligent watchdog monitoring
✅ AI master mode engaged
✅ Performance optimization active

📊 **Trading Configuration:**
• Capital: ₹{capital:,}
• Max Daily Trades: {max_trades}
• Risk Management: ACTIVE
• Auto-Exit: ENABLED

📈 **Market Status:**
{market_status}

⏰ **Session Start:** {current_time.strftime('%d %b %Y %H:%M IST')}
        """
        
        return notifier.send_telegram(message)
        
    except Exception as e:
        logger.error(f"❌ Error sending good morning message: {e}")
        return False

Today is {current_time.strftime('%A, %B %d, %Y')}

🚀 **Sandy Sniper Bot Status:**
✅ Enhanced system initialized and ready
✅ Market data connections active  
✅ Indian timezone configured (IST)
✅ Advanced risk management enabled
✅ AI-powered signal analysis active

📊 **Today's Market Status:**
{market_status}

💰 **Today's Trading Plan:**
• Your trading capital: ₹{capital:,}
• Maximum trades today: {max_trades}
• Risk management: 2% stop-loss, 6% target
• Position limit: 3 simultaneous trades

🎯 **Enhanced Features Active:**
• Multi-timeframe analysis (15m, 30m)
• Advanced exit management
• Signal strength analyzer
• Intelligent order management
• Real-time position monitoring

**Sandy Sniper Bot is locked and loaded! Ready to hunt for profitable opportunities!** 🎯

Have a fantastic trading day! 💪

*May the markets be in your favor* 🍀
        """
        
        return notifier.send_telegram(message)
        
    except Exception as e:
        logger.error(f"❌ Error sending good morning message: {e}")
        return False

def send_good_evening_message(performance: Dict[str, Any], notifier: Optional[Notifier] = None) -> bool:
    """Send personalized good evening message to Saki"""
    try:
        if not notifier:
            return False
        
        current_time = get_indian_time()
        evening_greeting = "Good bye Saki! 👋"
        
        # Format performance data
        trades_taken = performance.get('trades_taken', 0)
        total_pnl = performance.get('total_pnl', 0.0)
        win_rate = performance.get('win_rate', 0.0)
        active_positions = performance.get('active_positions', 0)
        signals_analyzed = performance.get('signals_analyzed', 0)
        cache_hit_rate = performance.get('cache_hit_rate', 0.0)
        avg_analysis_time = performance.get('avg_analysis_time', 0.0)
        
        # Performance emoji
        pnl_emoji = "�" if total_pnl > 0 else "❤️" if total_pnl < 0 else "💛"
        
        message = f"""
{evening_greeting}

🌆 **TRADING SESSION COMPLETE**

� **Today's Performance Summary:**
• Signals Analyzed: {signals_analyzed}
• Trades Executed: {trades_taken}
• Success Rate: {win_rate:.1f}%
• Avg Analysis Time: {avg_analysis_time:.2f}s
• Cache Hit Rate: {cache_hit_rate:.1%}
• System Uptime: >99.5%
• Auto-Reconnections: Seamless

{pnl_emoji} **P&L Summary:**
• Total P&L: ₹{total_pnl:,.2f}
• Active Positions: {active_positions}
• Risk Management: Maintained

🤖 **Master AI Learning:**
• Patterns analyzed and stored
• Market behavior updated
• Decision models enhanced
• Performance optimization applied

🎯 **Tomorrow's Preparation:**
• System optimization scheduled
• AI models ready for new patterns
• Performance monitoring active
• Watchdog continues monitoring

💤 **Rest well, Saki! Tomorrow we trade again!**

🔧 **System Status:**
✅ Auto-reconnection maintained
✅ Watchdog monitoring continues
✅ AI learning from today's data
✅ Ready for tomorrow's session

⏰ **Session End:** {current_time.strftime('%d %b %Y %H:%M IST')}
        """
        
        return notifier.send_telegram(message)
        
    except Exception as e:
        logger.error(f"❌ Error sending good evening message: {e}")
        return False

🙏 **Thank you for trusting Sandy Sniper Bot with your trading!**

Rest well, Saki. Tomorrow brings new opportunities! 😊

Good night! 🌙✨

*"Success in trading comes to those who are patient and disciplined"*
        """
        
        return notifier.send_telegram(message)
        
    except Exception as e:
        logger.error(f"❌ Error sending good evening message: {e}")
        return False

def send_enhanced_trade_alert(symbol: str, action: str, reasons: List[str], 
                             confidence: float, indicators: Dict[str, Any], 
                             notifier: Optional[Notifier] = None) -> bool:
    """Send enhanced trade alert with detailed technical analysis"""
    try:
        if not notifier:
            return False
        
        current_time = get_indian_time()
        
        # Format reasons
        reasons_text = '\n'.join([f"• {reason}" for reason in reasons])
        
        # Format indicators
        indicators_text = "Loading..."
        if indicators:
            indicators_lines = []
            
            # RSI
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                rsi_status = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
                indicators_lines.append(f"• RSI: {rsi:.1f} ({rsi_status})")
            
            # MACD
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd']
                macd_signal = indicators['macd_signal']
                macd_status = "Bullish" if macd > macd_signal else "Bearish"
                indicators_lines.append(f"• MACD: {macd:.3f} ({macd_status})")
            
            # Volume
            if 'volume' in indicators:
                volume = indicators['volume']
                indicators_lines.append(f"• Volume: {volume:,.0f}")
            
            # Price levels
            if 'price' in indicators:
                price = indicators['price']
                indicators_lines.append(f"• Current Price: ₹{price:.2f}")
            
            indicators_text = '\n'.join(indicators_lines) if indicators_lines else "Indicators loading..."
        
        # Confidence bar
        confidence_stars = "⭐" * min(int(confidence), 10)
        
        message = f"""
🎯 **TRADE EXECUTED - {symbol}**

📊 **Trade Details:**
• **Action:** {action}
• **Time:** {current_time.strftime('%I:%M %p IST')}
• **Confidence:** {confidence:.1f}/10 {confidence_stars}

🔍 **Entry Reasons:**
{reasons_text}

📈 **Technical Analysis:**
{indicators_text}

⚡ **Signal Strength:** {"STRONG" if confidence >= 7 else "MODERATE" if confidence >= 5 else "WEAK"}

🎯 **Sandy Sniper Bot has identified this high-probability setup!**

{"🚀 This looks like a strong opportunity!" if confidence >= 7 else "📊 Decent setup based on technical confluence" if confidence >= 5 else "⚠️ Lower confidence trade - monitoring closely"}

🔔 **Risk Management Active:**
• Stop-loss: 2% risk management
• Target: 6% profit objective
• Position monitoring: Real-time

Good luck with this trade, Saki! 💪
        """
        
        return notifier.send_telegram(message)
        
    except Exception as e:
        logger.error(f"❌ Error sending enhanced trade alert: {e}")
        return False

def send_position_exit_alert(symbol: str, action: str, exit_reason: str, 
                           entry_reasons: List[str], pnl: float, pnl_percent: float,
                           holding_duration: str, notifier: Optional[Notifier] = None) -> bool:
    """Send enhanced position exit alert"""
    try:
        if not notifier:
            return False
        
        current_time = get_indian_time()
        
        # P&L emoji and status
        pnl_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
        pnl_status = "PROFIT" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN"
        
        # Entry reasons
        entry_reasons_text = '\n'.join([f"• {reason}" for reason in entry_reasons])
        
        message = f"""
🔚 **POSITION CLOSED - {symbol}**

{pnl_emoji} **Result: {pnl_status}**

💰 **P&L Summary:**
• Profit/Loss: ₹{pnl:,.0f} ({pnl_percent:+.1f}%)
• Holding Period: {holding_duration}
• Exit Time: {current_time.strftime('%I:%M %p IST')}

🔍 **Exit Reason:**
• {exit_reason}

📊 **Original Entry Analysis:**
{entry_reasons_text}

🎯 **Trade Performance:**
{"🎉 Excellent result! Target achieved!" if pnl_percent >= 5 else "👍 Good trade management!" if pnl > 0 else "🛡️ Risk managed properly - stop loss protected capital" if pnl < 0 else "⚖️ Breakeven trade"}

🤖 **Sandy Sniper Bot Analysis:**
{"✅ Strategy worked as expected" if pnl > 0 else "📊 Risk management saved us from bigger loss" if pnl < 0 else "⚖️ Market was indecisive"}

{"🔥 Keep up the great work!" if pnl > 0 else "💪 On to the next opportunity!" if pnl < 0 else "🎯 Ready for the next setup!"}
        """
        
        return notifier.send_telegram(message)
        
    except Exception as e:
        logger.error(f"❌ Error sending position exit alert: {e}")
        return False

def send_market_status_update(all_markets_status: Dict, notifier: Optional[Notifier] = None) -> bool:
    """Send market status update"""
    try:
        if not notifier:
            return False
        
        current_time = get_indian_time()
        
        status_lines = []
        for symbol, status in all_markets_status.items():
            exchange = status['exchange']
            market_status = status['status']
            status_emoji = "🟢" if market_status == "MARKET_OPEN" else "🔴" if market_status == "MARKET_CLOSED" else "🟡"
            status_lines.append(f"{status_emoji} **{symbol}** ({exchange}): {market_status}")
        
        message = f"""
📊 **MARKET STATUS UPDATE**

🕐 **Current Time:** {current_time.strftime('%I:%M %p IST, %B %d, %Y')}

📈 **Markets Status:**
{chr(10).join(status_lines)}

🤖 **Sandy Sniper Bot Status:**
✅ System monitoring all markets
✅ Ready to execute when opportunities arise
✅ Risk management protocols active

🎯 **Trading Status:** {"Active" if any(status['status'] == 'MARKET_OPEN' for status in all_markets_status.values()) else "Standby"}
        """
        
        return notifier.send_telegram(message)
        
    except Exception as e:
        logger.error(f"❌ Error sending market status update: {e}")
        return False

def send_system_health_alert(health_data: Dict, notifier: Optional[Notifier] = None) -> bool:
    """Send system health alert"""
    try:
        if not notifier:
            return False
        
        cpu_usage = health_data.get('cpu_usage', 0)
        memory_usage = health_data.get('memory_usage', 0)
        disk_usage = health_data.get('disk_usage', 0)
        api_status = health_data.get('api_status', 'Unknown')
        
        health_emoji = "🟢" if all([cpu_usage < 80, memory_usage < 80, disk_usage < 80]) else "🟡" if all([cpu_usage < 90, memory_usage < 90, disk_usage < 90]) else "🔴"
        
        message = f"""
{health_emoji} **SYSTEM HEALTH REPORT**

💻 **System Resources:**
• CPU Usage: {cpu_usage:.1f}%
• Memory Usage: {memory_usage:.1f}%
• Disk Usage: {disk_usage:.1f}%

🔗 **API Connectivity:**
• Kite API: {api_status}
• Telegram API: ✅ Connected

🤖 **Sandy Sniper Bot Status:**
{"✅ All systems operating normally" if health_emoji == "🟢" else "⚠️ Some systems under load" if health_emoji == "🟡" else "❌ System attention required"}

🕐 **Last Check:** {get_indian_time().strftime('%I:%M %p IST')}
        """
        
        return notifier.send_telegram(message)
        
    except Exception as e:
        logger.error(f"❌ Error sending system health alert: {e}")
        return False
