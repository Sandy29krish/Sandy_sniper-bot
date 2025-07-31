import requests
import logging
import os
import pytz
from datetime import datetime

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

def get_indian_time():
    """Get current Indian Standard Time"""
    return datetime.now(IST)

class Notifier:
    def __init__(self, token=None, chat_id=None):
        # Auto-load from GitHub secrets/environment if not provided
        if not token:
            token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not chat_id:
            chat_id = os.getenv('TELEGRAM_ID')
            
        self.token = token
        self.chat_id = chat_id
        
        if not self.token or not self.chat_id:
            logging.warning("⚠️  Telegram credentials not found - notifications disabled")

    def send_message(self, text: str) -> bool:
        """Send message via Telegram (alias for send_telegram)"""
        return self.send_telegram(text)

    def send_telegram(self, text: str) -> bool:
        """
        Send a Telegram message using the provided token and chat ID.
        """
        if not self.token or not self.chat_id:
            logging.warning("⚠️  Telegram token or chat ID missing - notification skipped")
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logging.error("❌ Failed to send Telegram message: %s", response.text)
                return False
            logging.info("📱 Telegram message sent successfully")
            return True
        except Exception as e:
            logging.error(f"❌ Error sending telegram message: {e}")
            return False


def send_telegram(message, silent=False, parse_mode='HTML'):
    """Send message to Telegram with bulletproof error handling"""
    try:
        # Auto-load credentials from GitHub secrets
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_ID')
        
        if not bot_token or not chat_id:
            logging.warning("⚠️ Telegram credentials not found in environment")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': parse_mode,
            'disable_notification': silent
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            logging.info("✅ Telegram message sent successfully")
            return True
        else:
            logging.error(f"❌ Telegram API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Telegram send failed: {e}")
        return False

def check_telegram_health() -> dict:
    """
    🏥 Check Telegram bot health and connectivity
    Returns detailed health status for monitoring
    """
    try:
        logging.info("🔍 Checking Telegram health...")
        
        # Check environment variables
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_ID')
        
        health_status = {
            'timestamp': get_indian_time().isoformat(),
            'bot_token_present': bool(bot_token),
            'chat_id_present': bool(chat_id),
            'api_connectivity': False,
            'bot_info': None,
            'chat_info': None,
            'overall_health': 'UNHEALTHY',
            'issues': []
        }
        
        if not bot_token:
            health_status['issues'].append('Missing TELEGRAM_BOT_TOKEN')
        
        if not chat_id:
            health_status['issues'].append('Missing TELEGRAM_ID')
            
        if not bot_token or not chat_id:
            logging.warning("⚠️ Telegram credentials missing")
            return health_status
        
        # Test API connectivity
        try:
            # Get bot info
            bot_url = f"https://api.telegram.org/bot{bot_token}/getMe"
            bot_response = requests.get(bot_url, timeout=10)
            
            if bot_response.status_code == 200:
                health_status['api_connectivity'] = True
                health_status['bot_info'] = bot_response.json().get('result', {})
                logging.info(f"✅ Bot info retrieved: {health_status['bot_info'].get('username', 'Unknown')}")
            else:
                health_status['issues'].append(f'Bot API error: {bot_response.status_code}')
                logging.error(f"❌ Bot API error: {bot_response.status_code} - {bot_response.text}")
                
        except Exception as e:
            health_status['issues'].append(f'API connectivity failed: {str(e)}')
            logging.error(f"❌ Telegram API connectivity failed: {e}")
        
        # Test chat access
        try:
            chat_url = f"https://api.telegram.org/bot{bot_token}/getChat"
            chat_response = requests.get(chat_url, params={'chat_id': chat_id}, timeout=10)
            
            if chat_response.status_code == 200:
                health_status['chat_info'] = chat_response.json().get('result', {})
                logging.info(f"✅ Chat info retrieved: {health_status['chat_info'].get('type', 'Unknown')}")
            else:
                health_status['issues'].append(f'Chat access error: {chat_response.status_code}')
                logging.error(f"❌ Chat access error: {chat_response.status_code} - {chat_response.text}")
                
        except Exception as e:
            health_status['issues'].append(f'Chat access failed: {str(e)}')
            logging.error(f"❌ Chat access failed: {e}")
        
        # Determine overall health
        if health_status['api_connectivity'] and not health_status['issues']:
            health_status['overall_health'] = 'HEALTHY'
        elif health_status['api_connectivity']:
            health_status['overall_health'] = 'DEGRADED'
        else:
            health_status['overall_health'] = 'UNHEALTHY'
        
        # Send test message if healthy
        if health_status['overall_health'] == 'HEALTHY':
            test_message = f"🏥 Telegram Health Check ✅\n📅 {get_indian_time().strftime('%Y-%m-%d %H:%M:%S IST')}\n🤖 Bot: {health_status['bot_info'].get('username', 'Unknown')}\n💬 Chat: {health_status['chat_info'].get('type', 'Unknown')}"
            
            try:
                send_telegram(test_message, silent=True)
                logging.info("✅ Test message sent successfully")
            except Exception as e:
                health_status['issues'].append(f'Test message failed: {str(e)}')
                health_status['overall_health'] = 'DEGRADED'
        
        logging.info(f"🏥 Telegram health check complete: {health_status['overall_health']}")
        return health_status
        
    except Exception as e:
        logging.error(f"❌ Telegram health check failed: {e}")
        return {
            'timestamp': get_indian_time().isoformat(),
            'overall_health': 'CRITICAL',
            'error': str(e),
            'issues': [f'Health check crashed: {str(e)}']
        }

# Convenience function for backward compatibility
def send_notification(message: str, notification_type: str = "INFO") -> bool:
    """Send notification with specified type"""
    emoji_map = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌",
        "TRADE": "💰"
    }
    
    emoji = emoji_map.get(notification_type, "📢")
    formatted_message = f"{emoji} {message}"
    
    return send_telegram(formatted_message)
