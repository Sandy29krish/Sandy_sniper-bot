#!/usr/bin/env python3
"""
Enhanced Telegram Notifications for Sandy Sniper Bot
Includes good morning/evening messages with IST timezone
"""

import os
import requests
import datetime
import pytz
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Indian Standard Time
IST = pytz.timezone('Asia/Kolkata')

def get_indian_time() -> datetime.datetime:
    """Get current time in Indian Standard Time"""
    return datetime.datetime.now(IST)

class Notifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send_telegram(self, text: str) -> bool:
        """Send a Telegram message with IST timestamp"""
        if not self.token or not self.chat_id:
            logging.error("Telegram token or chat ID missing.")
            return False

        # Add IST timestamp to message
        ist_time = get_indian_time()
        timestamped_text = f"{text}\n\n🕐 {ist_time.strftime('%I:%M %p IST, %B %d, %Y')}"

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": timestamped_text,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logging.error("Failed to send Telegram message: %s", response.text)
                return False
            return True
        except Exception as e:
            logging.exception(f"Error sending telegram message: {e}")
            return False

# Enhanced notification functions
def send_telegram_message(message: str, parse_mode: str = 'Markdown') -> bool:
    """Send message to Telegram using environment variables"""
    try:
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_ID')
        
        if not token or not chat_id:
            logger.error("❌ Telegram credentials not configured")
            return False
        
        notifier = Notifier(token, chat_id)
        return notifier.send_telegram(message)
        
    except Exception as e:
        logger.error(f"❌ Error sending Telegram message: {e}")
        return False

def send_good_morning_message() -> bool:
    """Send personalized good morning message to Saki"""
    try:
        current_time = get_indian_time()
        
        message = f"""
🌅 **Good Morning Saki!**

Today is {current_time.strftime('%A, %B %d, %Y')}

🚀 **Sandy Sniper Bot Status:**
✅ System initialized and ready
✅ Market data connections active  
✅ Indian timezone configured
✅ Risk management enabled

📊 **Today's Market:**
• Market opens at 9:15 AM IST
• Your trading capital: ₹1,70,000
• Max trades today: 3
• Risk per trade: 2%
• Target profit: 6%

🎯 **Ready to hunt for profitable opportunities!**

Have a great trading day! 💪
        """
        
        return send_telegram_message(message)
        
    except Exception as e:
        logger.error(f"❌ Error sending good morning message: {e}")
        return False

def send_good_evening_message(daily_summary: Optional[Dict[str, Any]] = None) -> bool:
    """Send personalized good evening message to Saki with daily summary"""
    try:
        current_time = get_indian_time()
        
        # Default summary if none provided
        if not daily_summary:
            daily_summary = {
                'trades_taken': 0,
                'pnl': 0.0,
                'win_rate': 0.0,
                'best_trade': 'No trades today'
            }
        
        message = f"""
🌆 **Good Evening Saki!**

Market has closed for today. Here's your summary:

📈 **Today's Performance:**
• Trades taken: {daily_summary.get('trades_taken', 0)}
• Total P&L: ₹{daily_summary.get('pnl', 0):,.0f}
• Win rate: {daily_summary.get('win_rate', 0):.1f}%
• Best trade: {daily_summary.get('best_trade', 'None')}

🎯 **Sandy Sniper Bot worked hard today!**

📊 **Tomorrow's Plan:**
• System will analyze overnight data
• Market opens 9:15 AM IST tomorrow
• Ready for new opportunities

Rest well and see you tomorrow! 😊

Good night! 🌙
        """
        
        return send_telegram_message(message)
        
    except Exception as e:
        logger.error(f"❌ Error sending good evening message: {e}")
        return False
