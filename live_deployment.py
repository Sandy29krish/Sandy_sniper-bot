#!/usr/bin/env python3
"""
🚀 SANDY SNIPER BOT - LIVE DEPLOYMENT MONITOR
Real-time monitoring and live trading deployment
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup real-time logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('live_deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("LiveDeployment")

def live_system_monitor():
    """Monitor all systems in real-time"""
    logger.info("🔍 Starting live system monitoring...")
    
    while True:
        try:
            # Check GitHub secrets
            from utils.kite_api import get_github_secrets
            secrets = get_github_secrets()
            logger.info(f"🔐 GitHub Secrets: {len(secrets)} active")
            
            # Check Kite connection
            from utils.kite_api import get_kite_instance
            kite = get_kite_instance()
            if kite:
                logger.info("✅ Kite API: Connection healthy")
            else:
                logger.warning("⚠️  Kite API: In fallback mode")
            
            # Check market status
            from market_timing import is_market_open, get_market_status
            market_status = get_market_status()
            is_open = is_market_open()
            logger.info(f"📈 Market: {market_status} ({'OPEN' if is_open else 'CLOSED'})")
            
            # Test live price fetching
            from utils.kite_api import get_live_price_bulletproof
            try:
                nifty_price = get_live_price_bulletproof("NIFTY")
                banknifty_price = get_live_price_bulletproof("BANKNIFTY")
                logger.info(f"📊 NIFTY: ₹{nifty_price:,.2f} | BANKNIFTY: ₹{banknifty_price:,.2f}")
            except Exception as e:
                logger.warning(f"⚠️  Price fetch error: {e}")
            
            # Sleep before next check
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error(f"❌ Monitor error: {e}")
            time.sleep(60)  # Wait longer on error

def live_trading_engine():
    """Live trading engine with real-time execution"""
    logger.info("🎯 Starting live trading engine...")
    
    try:
        from sniper_swing import SniperSwingBot
        from market_timing import is_market_open
        
                # Initialize trading bot with required parameters
        logger.info("🎯 Initializing Sandy Sniper Bot...")
        
        # Import config and capital from swing_config
        from utils.swing_config import CAPITAL
        
        # Create a simple config object
        config = {
            "trading_enabled": True,
            "max_positions": 3,
            "risk_per_trade": 0.02
        }
        
        bot = SniperSwingBot(config, CAPITAL)
        logger.info("✅ Trading bot initialized successfully")
        
        while True:
            try:
                current_time = datetime.now()
                
                if is_market_open():
                    logger.info(f"📈 Market OPEN at {current_time.strftime('%H:%M:%S')} - Running trading cycle")
                    
                    # Run trading cycle - use the existing run() method
                    if hasattr(bot, 'run'):
                        bot.run()
                    else:
                        logger.warning("⚠️  Bot does not have run() method - using basic cycle")
                        bot.run_trading_cycle()  # Fallback
                    
                    # Sleep between trading cycles (market open)
                    time.sleep(60)  # 1 minute between cycles
                else:
                    logger.info(f"🌙 Market CLOSED at {current_time.strftime('%H:%M:%S')} - Monitoring mode")
                    
                    # Sleep longer when market is closed
                    time.sleep(300)  # 5 minutes when closed
                    
            except Exception as e:
                logger.error(f"❌ Trading engine error: {e}")
                logger.exception("Full error details:")
                time.sleep(120)  # Wait 2 minutes on error
                
    except Exception as e:
        logger.error(f"💥 Critical trading engine error: {e}")
        logger.exception("Full critical error details:")

def live_notification_system():
    """Live notification system for real-time alerts"""
    logger.info("📱 Starting live notification system...")
    
    try:
        from utils.notifications import Notifier
        notifier = Notifier()
        
        # Send deployment start notification
        notifier.send_message(
            "🚀 SANDY SNIPER BOT - LIVE DEPLOYMENT STARTED!\n"
            f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "🛡️ Bulletproof mode: ACTIVE\n"
            "📊 Real-time monitoring: ENABLED"
        )
        logger.info("📱 Deployment notification sent")
        
        # Send periodic status updates
        while True:
            try:
                time.sleep(1800)  # Every 30 minutes
                
                current_time = datetime.now()
                from market_timing import is_market_open
                market_status = "OPEN" if is_market_open() else "CLOSED"
                
                # Send status update
                notifier.send_message(
                    f"🛡️ SANDY SNIPER BOT - STATUS UPDATE\n"
                    f"🕒 Time: {current_time.strftime('%H:%M:%S')}\n"
                    f"📈 Market: {market_status}\n"
                    f"✅ System: OPERATIONAL"
                )
                logger.info("📱 Status update sent")
                
            except Exception as e:
                logger.warning(f"⚠️  Notification error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
                
    except Exception as e:
        logger.error(f"❌ Notification system error: {e}")

def main():
    """Main live deployment function"""
    logger.info("🚀 SANDY SNIPER BOT - STARTING LIVE DEPLOYMENT")
    logger.info("=" * 60)
    
    try:
        # Start system monitor thread
        monitor_thread = threading.Thread(target=live_system_monitor, daemon=True)
        monitor_thread.start()
        logger.info("🔍 System monitor started")
        
        # Start notification system thread
        notification_thread = threading.Thread(target=live_notification_system, daemon=True)
        notification_thread.start()
        logger.info("📱 Notification system started")
        
        # Start trading engine (main thread)
        logger.info("🎯 Starting trading engine in main thread...")
        live_trading_engine()
        
    except KeyboardInterrupt:
        logger.info("🛑 Live deployment stopped by user")
    except Exception as e:
        logger.error(f"💥 Live deployment error: {e}")
        logger.exception("Full deployment error details:")
    finally:
        logger.info("🛑 Live deployment shutdown complete")

if __name__ == "__main__":
    main()
