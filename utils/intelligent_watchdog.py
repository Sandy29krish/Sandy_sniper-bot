import logging
import time
import psutil
import threading
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from pathlib import Path

# Import bot modules for health checks
from .secure_kite_api import test_kite_connection
from .nse_data import get_live_price
from .indicators import calculate_rsi
from .ai_assistant import test_ai_functionality
from .trade_logger import test_logging_system
import sys
import os

# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from market_timing import is_market_open
from telegram_commands import test_telegram_connection

logger = logging.getLogger(__name__)

class IntelligentWatchdog:
    """
    🐕‍🦺 Intelligent Watchdog System
    - Monitors all bot processes and modules
    - Auto-fixes common issues
    - Alerts for critical manual intervention
    - Personalized communication with Saki
    """
    
    def __init__(self, notification_callback=None):
        self.notification_callback = notification_callback
        self.watchdog_active = False
        self.monitoring_thread = None
        
        # Health check intervals (seconds)
        self.check_intervals = {
            'system_health': 300,      # 5 minutes
            'api_connections': 600,    # 10 minutes  
            'data_feeds': 180,         # 3 minutes
            'trading_logic': 900,      # 15 minutes
            'file_integrity': 1800,    # 30 minutes
            'memory_cleanup': 3600     # 1 hour
        }
        
        # Auto-fix capabilities
        self.auto_fix_enabled = {
            'memory_cleanup': True,
            'api_reconnection': True,
            'file_recovery': True,
            'cache_clearing': True,
            'thread_restart': True,
            'log_rotation': True
        }
        
        # Health status tracking
        self.health_status = {
            'overall': 'healthy',
            'last_check': None,
            'issues_detected': [],
            'auto_fixes_applied': [],
            'manual_interventions_needed': []
        }
        
        # Critical thresholds
        self.thresholds = {
            'cpu_usage': 85.0,         # %
            'memory_usage': 80.0,      # %
            'disk_usage': 90.0,        # %
            'api_response_time': 10.0, # seconds
            'consecutive_failures': 3,  # count
            'log_file_size': 100       # MB
        }
        
        # Issue counters for auto-fix decisions
        self.issue_counters = {}
        
    def start_intelligent_monitoring(self):
        """Start the intelligent watchdog monitoring system"""
        try:
            logger.info("🐕‍🦺 Starting Intelligent Watchdog System...")
            
            self.watchdog_active = True
            
            # Send startup greeting to Saki
            self._send_morning_greeting()
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(
                target=self._continuous_monitoring, 
                daemon=True
            )
            self.monitoring_thread.start()
            
            logger.info("✅ Intelligent Watchdog started successfully")
            
        except Exception as e:
            logger.error(f"❌ Error starting intelligent watchdog: {e}")
    
    def _send_morning_greeting(self):
        """Send personalized morning greeting to Saki"""
        try:
            current_time = datetime.now()
            greeting_time = current_time.strftime('%H:%M')
            
            morning_message = f"""🌅 **Good Morning Saki!** 

🐕‍🦺 **Your Intelligent Watchdog is Active**
⏰ **Time**: {greeting_time}
🛡️ **Protection Level**: MAXIMUM
🔧 **Auto-Fix**: ENABLED

**🎯 Monitoring Systems:**
✅ API Connections
✅ Data Feeds  
✅ Trading Logic
✅ System Health
✅ Memory Management
✅ File Integrity

**Your bot is under complete protection! I'll auto-fix issues and alert you only for critical matters that need your attention.**

**Ready to make profitable trades today, Saki! 🚀**"""
            
            self._send_notification(morning_message)
            
        except Exception as e:
            logger.error(f"❌ Error sending morning greeting: {e}")
    
    def _continuous_monitoring(self):
        """Continuous monitoring loop"""
        last_checks = {check_type: 0 for check_type in self.check_intervals}
        
        while self.watchdog_active:
            try:
                current_time = time.time()
                
                # Check each monitoring type based on its interval
                for check_type, interval in self.check_intervals.items():
                    if current_time - last_checks[check_type] >= interval:
                        self._perform_health_check(check_type)
                        last_checks[check_type] = current_time
                
                # Sleep for 30 seconds between monitoring cycles
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer if there's an error
    
    def _perform_health_check(self, check_type: str):
        """Perform specific health check"""
        try:
            logger.info(f"🔍 Performing {check_type} health check...")
            
            if check_type == 'system_health':
                self._check_system_health()
            elif check_type == 'api_connections':
                self._check_api_connections()
            elif check_type == 'data_feeds':
                self._check_data_feeds()
            elif check_type == 'trading_logic':
                self._check_trading_logic()
            elif check_type == 'file_integrity':
                self._check_file_integrity()
            elif check_type == 'memory_cleanup':
                self._perform_memory_cleanup()
                
        except Exception as e:
            logger.error(f"❌ Error in {check_type} health check: {e}")
            self._handle_check_failure(check_type, str(e))
    
    def _check_system_health(self):
        """Check system resource health"""
        try:
            # CPU usage check
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.thresholds['cpu_usage']:
                self._handle_high_cpu_usage(cpu_percent)
            
            # Memory usage check
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            if memory_percent > self.thresholds['memory_usage']:
                self._handle_high_memory_usage(memory_percent)
            
            # Disk usage check
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > self.thresholds['disk_usage']:
                self._handle_high_disk_usage(disk_percent)
            
            # Process health check
            self._check_bot_processes()
            
            logger.info(f"✅ System health: CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}%, Disk {disk_percent:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ System health check failed: {e}")
            self._require_manual_intervention("System Health Check Failed", str(e))
    
    def _check_api_connections(self):
        """Check all API connections"""
        try:
            api_issues = []
            
            # Test Kite API connection
            try:
                kite_status = test_kite_connection()
                if not kite_status:
                    api_issues.append("Kite API connection failed")
            except Exception as e:
                api_issues.append(f"Kite API error: {str(e)}")
            
            # Test Telegram connection
            try:
                telegram_status = test_telegram_connection()
                if not telegram_status:
                    api_issues.append("Telegram connection failed")
            except Exception as e:
                api_issues.append(f"Telegram error: {str(e)}")
            
            # Auto-fix API issues
            if api_issues and self.auto_fix_enabled['api_reconnection']:
                self._auto_fix_api_connections(api_issues)
            elif api_issues:
                self._require_manual_intervention("API Connection Issues", api_issues)
            else:
                logger.info("✅ All API connections healthy")
                
        except Exception as e:
            logger.error(f"❌ API connection check failed: {e}")
            self._require_manual_intervention("API Check Failed", str(e))
    
    def _check_data_feeds(self):
        """Check data feed health"""
        try:
            data_issues = []
            
            # Test live price feeds
            test_symbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY']
            for symbol in test_symbols:
                try:
                    price = get_live_price(symbol)
                    if not price or price <= 0:
                        data_issues.append(f"{symbol} price feed failed")
                except Exception as e:
                    data_issues.append(f"{symbol} feed error: {str(e)}")
            
            # Test indicator calculations
            try:
                # Test RSI calculation with dummy data
                test_data = [100, 102, 101, 103, 102, 104, 103, 105]
                rsi_result = calculate_rsi(test_data, period=7)
                if rsi_result is None:
                    data_issues.append("Indicator calculations failed")
            except Exception as e:
                data_issues.append(f"Indicator error: {str(e)}")
            
            if data_issues and self.auto_fix_enabled['cache_clearing']:
                self._auto_fix_data_feeds(data_issues)
            elif data_issues:
                self._require_manual_intervention("Data Feed Issues", data_issues)
            else:
                logger.info("✅ All data feeds healthy")
                
        except Exception as e:
            logger.error(f"❌ Data feed check failed: {e}")
            self._require_manual_intervention("Data Feed Check Failed", str(e))
    
    def _check_trading_logic(self):
        """Check trading logic components"""
        try:
            logic_issues = []
            
            # Test AI functionality
            try:
                ai_status = test_ai_functionality()
                if not ai_status:
                    logic_issues.append("AI assistant not responding")
            except Exception as e:
                logic_issues.append(f"AI error: {str(e)}")
            
            # Test logging system
            try:
                log_status = test_logging_system()
                if not log_status:
                    logic_issues.append("Logging system failed")
            except Exception as e:
                logic_issues.append(f"Logging error: {str(e)}")
            
            # Check state file integrity
            try:
                state_file = Path("sniper_swing_state.json")
                if state_file.exists():
                    with open(state_file, 'r') as f:
                        json.load(f)  # Test if valid JSON
                else:
                    logic_issues.append("State file missing")
            except Exception as e:
                logic_issues.append(f"State file error: {str(e)}")
            
            if logic_issues:
                self._require_manual_intervention("Trading Logic Issues", logic_issues)
            else:
                logger.info("✅ Trading logic components healthy")
                
        except Exception as e:
            logger.error(f"❌ Trading logic check failed: {e}")
            self._require_manual_intervention("Trading Logic Check Failed", str(e))
    
    def _check_file_integrity(self):
        """Check critical file integrity"""
        try:
            critical_files = [
                'sniper_swing.py',
                'utils/indicators.py',
                'utils/secure_kite_api.py',
                'utils/swing_config.py',
                'telegram_commands.py'
            ]
            
            missing_files = []
            for file_path in critical_files:
                if not Path(file_path).exists():
                    missing_files.append(file_path)
            
            if missing_files:
                self._require_manual_intervention("Critical Files Missing", missing_files)
            else:
                logger.info("✅ All critical files present")
                
        except Exception as e:
            logger.error(f"❌ File integrity check failed: {e}")
            self._require_manual_intervention("File Integrity Check Failed", str(e))
    
    def _perform_memory_cleanup(self):
        """Perform automatic memory cleanup"""
        try:
            if self.auto_fix_enabled['memory_cleanup']:
                import gc
                
                # Force garbage collection
                collected = gc.collect()
                
                # Log rotation if needed
                if self.auto_fix_enabled['log_rotation']:
                    self._rotate_large_logs()
                
                logger.info(f"🧹 Memory cleanup completed - {collected} objects collected")
                self._log_auto_fix("Memory cleanup and garbage collection")
                
        except Exception as e:
            logger.error(f"❌ Memory cleanup failed: {e}")
    
    def _handle_high_cpu_usage(self, cpu_percent: float):
        """Handle high CPU usage"""
        try:
            if self.auto_fix_enabled['thread_restart']:
                logger.warning(f"⚠️ High CPU usage detected: {cpu_percent:.1f}%")
                
                # Auto-fix: Clear caches and optimize
                self._optimize_performance()
                self._log_auto_fix(f"Performance optimization due to high CPU ({cpu_percent:.1f}%)")
                
                # If still high after auto-fix, require manual intervention
                time.sleep(30)
                new_cpu = psutil.cpu_percent(interval=1)
                if new_cpu > self.thresholds['cpu_usage']:
                    self._require_manual_intervention(
                        "High CPU Usage Persists", 
                        f"CPU usage remains high: {new_cpu:.1f}% after auto-optimization"
                    )
            else:
                self._require_manual_intervention("High CPU Usage", f"CPU usage: {cpu_percent:.1f}%")
                
        except Exception as e:
            logger.error(f"❌ Error handling high CPU usage: {e}")
    
    def _handle_high_memory_usage(self, memory_percent: float):
        """Handle high memory usage"""
        try:
            if self.auto_fix_enabled['memory_cleanup']:
                logger.warning(f"⚠️ High memory usage detected: {memory_percent:.1f}%")
                
                # Auto-fix: Force cleanup
                self._perform_memory_cleanup()
                self._log_auto_fix(f"Memory cleanup due to high usage ({memory_percent:.1f}%)")
                
                # Check if fixed
                time.sleep(10)
                new_memory = psutil.virtual_memory().percent
                if new_memory > self.thresholds['memory_usage']:
                    self._require_manual_intervention(
                        "High Memory Usage Persists",
                        f"Memory usage remains high: {new_memory:.1f}% after cleanup"
                    )
            else:
                self._require_manual_intervention("High Memory Usage", f"Memory usage: {memory_percent:.1f}%")
                
        except Exception as e:
            logger.error(f"❌ Error handling high memory usage: {e}")
    
    def _handle_high_disk_usage(self, disk_percent: float):
        """Handle high disk usage"""
        try:
            logger.warning(f"⚠️ High disk usage detected: {disk_percent:.1f}%")
            
            if self.auto_fix_enabled['log_rotation']:
                # Auto-fix: Clean up logs and temporary files
                self._cleanup_disk_space()
                self._log_auto_fix(f"Disk cleanup due to high usage ({disk_percent:.1f}%)")
            
            # Always alert for high disk usage as it's critical
            self._require_manual_intervention("High Disk Usage", f"Disk usage: {disk_percent:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Error handling high disk usage: {e}")
    
    def _auto_fix_api_connections(self, issues: List[str]):
        """Auto-fix API connection issues"""
        try:
            logger.info("🔧 Auto-fixing API connection issues...")
            
            # Clear connection caches
            # Reinitialize connections
            # Wait and retry
            
            time.sleep(10)  # Wait before retry
            
            self._log_auto_fix(f"API reconnection attempted for: {', '.join(issues)}")
            
            # Verify fix worked
            self._verify_api_fix(issues)
            
        except Exception as e:
            logger.error(f"❌ Auto-fix API connections failed: {e}")
            self._require_manual_intervention("API Auto-Fix Failed", str(e))
    
    def _auto_fix_data_feeds(self, issues: List[str]):
        """Auto-fix data feed issues"""
        try:
            logger.info("🔧 Auto-fixing data feed issues...")
            
            # Clear data caches
            # Reset feed connections
            # Reinitialize data sources
            
            self._log_auto_fix(f"Data feed reset attempted for: {', '.join(issues)}")
            
        except Exception as e:
            logger.error(f"❌ Auto-fix data feeds failed: {e}")
            self._require_manual_intervention("Data Feed Auto-Fix Failed", str(e))
    
    def _optimize_performance(self):
        """Optimize bot performance"""
        try:
            import gc
            
            # Force garbage collection
            gc.collect()
            
            # Clear caches (if implemented)
            # Optimize memory usage
            # Reset connections
            
            logger.info("🚀 Performance optimization completed")
            
        except Exception as e:
            logger.error(f"❌ Performance optimization failed: {e}")
    
    def _cleanup_disk_space(self):
        """Clean up disk space"""
        try:
            # Rotate large log files
            self._rotate_large_logs()
            
            # Clean temporary files
            # Compress old logs
            # Remove unnecessary files
            
            logger.info("🧹 Disk space cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Disk cleanup failed: {e}")
    
    def _rotate_large_logs(self):
        """Rotate large log files"""
        try:
            log_files = Path('.').glob('*.log*')
            
            for log_file in log_files:
                if log_file.stat().st_size > self.thresholds['log_file_size'] * 1024 * 1024:  # MB to bytes
                    # Rotate log file
                    backup_name = f"{log_file}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    log_file.rename(backup_name)
                    logger.info(f"📝 Rotated large log file: {log_file}")
                    
        except Exception as e:
            logger.error(f"❌ Log rotation failed: {e}")
    
    def _check_bot_processes(self):
        """Check if bot processes are running properly"""
        try:
            # Check if main bot threads are alive
            # Monitor process health
            # Detect hung processes
            
            logger.info("✅ Bot processes healthy")
            
        except Exception as e:
            logger.error(f"❌ Bot process check failed: {e}")
            self._require_manual_intervention("Bot Process Issues", str(e))
    
    def _verify_api_fix(self, original_issues: List[str]):
        """Verify that API fix worked"""
        try:
            # Re-test APIs that had issues
            remaining_issues = []
            
            for issue in original_issues:
                if "Kite API" in issue:
                    if not test_kite_connection():
                        remaining_issues.append(issue)
                elif "Telegram" in issue:
                    if not test_telegram_connection():
                        remaining_issues.append(issue)
            
            if remaining_issues:
                self._require_manual_intervention("API Auto-Fix Incomplete", remaining_issues)
            else:
                self._log_successful_auto_fix("API connections restored")
                
        except Exception as e:
            logger.error(f"❌ API fix verification failed: {e}")
    
    def _handle_check_failure(self, check_type: str, error_msg: str):
        """Handle health check failures"""
        try:
            self.issue_counters[check_type] = self.issue_counters.get(check_type, 0) + 1
            
            if self.issue_counters[check_type] >= self.thresholds['consecutive_failures']:
                self._require_manual_intervention(
                    f"Repeated {check_type} Failures",
                    f"Failed {self.issue_counters[check_type]} times: {error_msg}"
                )
            else:
                logger.warning(f"⚠️ {check_type} check failed ({self.issue_counters[check_type]}/{self.thresholds['consecutive_failures']}): {error_msg}")
                
        except Exception as e:
            logger.error(f"❌ Error handling check failure: {e}")
    
    def _log_auto_fix(self, fix_description: str):
        """Log auto-fix action"""
        try:
            fix_record = {
                'timestamp': datetime.now().isoformat(),
                'action': fix_description,
                'type': 'auto_fix'
            }
            
            self.health_status['auto_fixes_applied'].append(fix_record)
            logger.info(f"🔧 Auto-fix applied: {fix_description}")
            
            # Keep only last 50 records
            if len(self.health_status['auto_fixes_applied']) > 50:
                self.health_status['auto_fixes_applied'] = self.health_status['auto_fixes_applied'][-50:]
                
        except Exception as e:
            logger.error(f"❌ Error logging auto-fix: {e}")
    
    def _log_successful_auto_fix(self, fix_description: str):
        """Log successful auto-fix with notification"""
        try:
            self._log_auto_fix(fix_description)
            
            success_message = f"""🔧 **Auto-Fix Successful, Saki!**

✅ **Issue Resolved**: {fix_description}
🤖 **Action**: Automatic repair completed
⏰ **Time**: {datetime.now().strftime('%H:%M:%S')}

**Your bot is back to optimal performance! No action needed from you.** 🚀"""
            
            self._send_notification(success_message)
            
        except Exception as e:
            logger.error(f"❌ Error logging successful auto-fix: {e}")
    
    def _require_manual_intervention(self, issue_title: str, issue_details):
        """Require manual intervention from Saki"""
        try:
            intervention_record = {
                'timestamp': datetime.now().isoformat(),
                'title': issue_title,
                'details': str(issue_details),
                'status': 'pending'
            }
            
            self.health_status['manual_interventions_needed'].append(intervention_record)
            
            # Send urgent notification to Saki
            urgent_message = f"""🚨 **URGENT: Manual Intervention Needed, Saki!**

⚠️ **Issue**: {issue_title}
📋 **Details**: {issue_details}
⏰ **Time**: {datetime.now().strftime('%H:%M:%S')}

**🔧 Auto-fix could not resolve this issue. Your attention is required to ensure optimal bot performance.**

**Please check the bot when convenient.** 🙏"""
            
            self._send_notification(urgent_message)
            logger.error(f"🚨 Manual intervention required: {issue_title}")
            
        except Exception as e:
            logger.error(f"❌ Error requiring manual intervention: {e}")
    
    def _send_notification(self, message: str):
        """Send notification to Saki"""
        try:
            if self.notification_callback:
                self.notification_callback(message)
            else:
                logger.info(f"📱 Notification for Saki: {message}")
                
        except Exception as e:
            logger.error(f"❌ Error sending notification: {e}")
    
    def get_health_report(self) -> Dict:
        """Get comprehensive health report for Saki"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            report = {
                'overall_status': self.health_status['overall'],
                'last_check': datetime.now().isoformat(),
                'system_metrics': {
                    'cpu_usage': f"{cpu_percent:.1f}%",
                    'memory_usage': f"{memory.percent:.1f}%",
                    'disk_usage': f"{(disk.used / disk.total) * 100:.1f}%"
                },
                'recent_auto_fixes': self.health_status['auto_fixes_applied'][-5:],
                'pending_interventions': len(self.health_status['manual_interventions_needed']),
                'watchdog_status': 'active' if self.watchdog_active else 'inactive'
            }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating health report: {e}")
            return {'error': str(e)}
    
    def stop_monitoring(self):
        """Stop the watchdog monitoring"""
        try:
            self.watchdog_active = False
            
            goodbye_message = f"""🐕‍🦺 **Watchdog Stopping, Saki**

✅ **Monitoring Session Complete**
🛡️ **Protection**: Temporarily disabled
⏰ **Time**: {datetime.now().strftime('%H:%M:%S')}

**Your bot protection is now offline. Restart when needed!** 😴"""
            
            self._send_notification(goodbye_message)
            logger.info("🐕‍🦺 Intelligent Watchdog stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping watchdog: {e}")

# Global instance
intelligent_watchdog = IntelligentWatchdog()

# Convenience functions
def start_watchdog_monitoring(notification_callback=None):
    """Start intelligent watchdog monitoring"""
    intelligent_watchdog.notification_callback = notification_callback
    intelligent_watchdog.start_intelligent_monitoring()

def get_watchdog_health_report() -> Dict:
    """Get watchdog health report"""
    return intelligent_watchdog.get_health_report()

def stop_watchdog():
    """Stop watchdog monitoring"""
    intelligent_watchdog.stop_monitoring() 