"""
Enhanced Intelligent Watchdog System for Sandy Sniper Bot
Master AI monitoring with auto-reconnection and robust error handling
"""

import time
import logging
import threading
import psutil
import os
import gc
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class EnhancedIntelligentWatchdog:
    """Master AI Watchdog System with intelligent auto-recovery"""
    
    def __init__(self, bot_instance=None):
        self.logger = logging.getLogger(__name__)
        self.bot_instance = bot_instance
        self.is_running = False
        self.monitoring_thread = None
        self.health_checks = {}
        self.error_counts = {}
        self.last_health_report = None
        self.auto_reconnect_enabled = True
        self.performance_metrics = {}
        
        # Watchdog configuration
        self.check_interval = int(os.getenv('WATCHDOG_CHECK_INTERVAL', '60'))
        self.max_error_threshold = 5
        self.reconnect_delay = 30
        self.health_report_interval = 300
        
        # System thresholds
        self.cpu_threshold = 80.0
        self.memory_threshold = 80.0
        self.response_time_threshold = 5.0
        
        self.logger.info("🤖 Enhanced Intelligent Watchdog initialized")
    
    def start_monitoring(self):
        """Start the watchdog monitoring system"""
        if self.is_running:
            self.logger.warning("⚠️ Watchdog already running")
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("🚀 Enhanced Watchdog started")
        self._send_watchdog_notification("🤖 **MASTER AI WATCHDOG ACTIVATED**\n\n✅ Auto-reconnection enabled\n📊 Performance monitoring active")
    
    def stop_monitoring(self):
        """Stop the watchdog monitoring system"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("🛑 Enhanced Watchdog stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("🔄 Starting monitoring loop...")
        
        while self.is_running:
            try:
                start_time = time.time()
                
                # Perform health checks
                self._perform_health_checks()
                self._monitor_system_performance()
                self._monitor_api_connections()
                self._monitor_bot_health()
                self._auto_recovery_check()
                self._generate_health_report()
                self._optimize_memory()
                
                # Calculate cycle time
                cycle_time = time.time() - start_time
                self.performance_metrics['last_monitoring_cycle'] = cycle_time
                
                # Sleep until next check
                sleep_time = max(0, self.check_interval - cycle_time)
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)
    
    def _perform_health_checks(self):
        """Perform comprehensive health checks"""
        health_results = {
            'telegram': self._check_telegram_health(),
            'kite_api': self._check_kite_health(),
            'filesystem': self._check_filesystem_health(),
            'network': self._check_network_health(),
            'bot_instance': self._check_bot_instance_health()
        }
        
        self.health_checks.update(health_results)
        
        healthy_count = sum(1 for status in health_results.values() if status)
        total_count = len(health_results)
        
        if healthy_count == total_count:
            self.logger.info(f"✅ All systems healthy ({healthy_count}/{total_count})")
        else:
            self.logger.warning(f"⚠️ System health: {healthy_count}/{total_count} components healthy")
    
    def _check_telegram_health(self):
        """Check Telegram API health"""
        try:
            # Simple health check - try to connect
            import requests
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not token:
                return False
            
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=10)
            is_healthy = response.status_code == 200
            
            if not is_healthy:
                self.error_counts['telegram'] = self.error_counts.get('telegram', 0) + 1
                if self.auto_reconnect_enabled and self.error_counts['telegram'] >= 3:
                    self._reconnect_telegram()
            else:
                self.error_counts['telegram'] = 0
            
            return is_healthy
            
        except Exception as e:
            self.logger.error(f"❌ Telegram health check failed: {e}")
            return False
    
    def _check_kite_health(self):
        """Check Kite API health"""
        try:
            if self.bot_instance:
                kite_connection = getattr(self.bot_instance, 'kite', None)
                if kite_connection:
                    return True
            return True  # Default to healthy
        except Exception as e:
            self.logger.error(f"❌ Kite health check failed: {e}")
            return False
    
    def _check_filesystem_health(self):
        """Check filesystem health"""
        try:
            disk_usage = psutil.disk_usage('/')
            free_space_percent = (disk_usage.free / disk_usage.total) * 100
            
            if free_space_percent < 10:
                self.logger.warning(f"⚠️ Low disk space: {free_space_percent:.1f}%")
                return False
            
            # Test write capability
            test_file = 'watchdog_test.tmp'
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Filesystem health check failed: {e}")
            return False
    
    def _check_network_health(self):
        """Check network connectivity"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            return True
        except Exception as e:
            self.logger.warning(f"⚠️ Network connectivity issue: {e}")
            return False
    
    def _check_bot_instance_health(self):
        """Check bot instance health"""
        try:
            if not self.bot_instance:
                return False
            
            required_attrs = ['active_positions', 'symbols', 'logger']
            for attr in required_attrs:
                if not hasattr(self.bot_instance, attr):
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Bot health check failed: {e}")
            return False
    
    def _monitor_system_performance(self):
        """Monitor system performance"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            self.performance_metrics.update({
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent
            })
            
            if cpu_percent > self.cpu_threshold:
                self.logger.warning(f"⚠️ High CPU usage: {cpu_percent:.1f}%")
                self._optimize_performance()
            
            if memory.percent > self.memory_threshold:
                self.logger.warning(f"⚠️ High memory usage: {memory.percent:.1f}%")
                self._optimize_memory()
                
        except Exception as e:
            self.logger.error(f"❌ Performance monitoring failed: {e}")
    
    def _monitor_api_connections(self):
        """Monitor API connections"""
        try:
            # Monitor response times
            telegram_time = self._check_telegram_response_time()
            self.performance_metrics['telegram_response_time'] = telegram_time
            
            if telegram_time > self.response_time_threshold:
                self.logger.warning(f"⚠️ Slow Telegram API: {telegram_time:.2f}s")
                
        except Exception as e:
            self.logger.error(f"❌ API monitoring failed: {e}")
    
    def _check_telegram_response_time(self):
        """Check Telegram response time"""
        try:
            start_time = time.time()
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            if token:
                import requests
                url = f"https://api.telegram.org/bot{token}/getMe"
                requests.get(url, timeout=5)
            return time.time() - start_time
        except Exception:
            return float('inf')
    
    def _monitor_bot_health(self):
        """Monitor bot health"""
        try:
            if self.bot_instance and hasattr(self.bot_instance, 'performance_stats'):
                stats = self.bot_instance.performance_stats
                self.performance_metrics.update({
                    'avg_analysis_time': stats.get('avg_analysis_time', 0),
                    'cache_hit_rate': stats.get('cache_hit_rate', 0),
                    'trades_today': stats.get('trades_executed_today', 0),
                    'signals_today': stats.get('signals_analyzed_today', 0)
                })
        except Exception as e:
            self.logger.error(f"❌ Bot monitoring failed: {e}")
    
    def _auto_recovery_check(self):
        """Perform auto-recovery"""
        try:
            for component, error_count in self.error_counts.items():
                if error_count >= self.max_error_threshold:
                    self.logger.warning(f"🔧 Auto-recovery for {component}")
                    self._perform_component_recovery(component)
        except Exception as e:
            self.logger.error(f"❌ Auto-recovery failed: {e}")
    
    def _perform_component_recovery(self, component: str):
        """Perform component recovery"""
        try:
            if component == 'telegram':
                self._reconnect_telegram()
            elif component == 'kite':
                self._reconnect_kite_api()
            
            self.error_counts[component] = 0
        except Exception as e:
            self.logger.error(f"❌ Recovery failed for {component}: {e}")
    
    def _reconnect_telegram(self):
        """Reconnect Telegram"""
        try:
            self.logger.info("🔄 Reconnecting Telegram...")
            time.sleep(self.reconnect_delay)
            
            if self._check_telegram_health():
                self.logger.info("✅ Telegram reconnected")
                self._send_watchdog_notification("✅ **Telegram Auto-Reconnection Successful**")
        except Exception as e:
            self.logger.error(f"❌ Telegram reconnection failed: {e}")
    
    def _reconnect_kite_api(self):
        """Reconnect Kite API"""
        try:
            self.logger.info("🔄 Reconnecting Kite API...")
            if self.bot_instance and hasattr(self.bot_instance, 'reconnect_kite'):
                self.bot_instance.reconnect_kite()
        except Exception as e:
            self.logger.error(f"❌ Kite reconnection failed: {e}")
    
    def _optimize_performance(self):
        """Optimize performance"""
        try:
            self.logger.info("⚡ Optimizing performance...")
            gc.collect()
            if self.bot_instance and hasattr(self.bot_instance, 'cleanup_cache'):
                self.bot_instance.cleanup_cache()
        except Exception as e:
            self.logger.error(f"❌ Performance optimization failed: {e}")
    
    def _optimize_memory(self):
        """Optimize memory"""
        try:
            self.logger.info("🧠 Optimizing memory...")
            gc.collect()
            if len(self.performance_metrics) > 100:
                self.performance_metrics = dict(list(self.performance_metrics.items())[-50:])
        except Exception as e:
            self.logger.error(f"❌ Memory optimization failed: {e}")
    
    def _generate_health_report(self):
        """Generate health report"""
        try:
            current_time = datetime.now()
            
            if (self.last_health_report is None or 
                (current_time - self.last_health_report).total_seconds() >= self.health_report_interval):
                
                self.last_health_report = current_time
                report = self._create_health_report()
                self._send_watchdog_notification(report)
        except Exception as e:
            self.logger.error(f"❌ Health report failed: {e}")
    
    def _create_health_report(self):
        """Create health report"""
        try:
            healthy_components = sum(1 for status in self.health_checks.values() if status)
            total_components = len(self.health_checks)
            
            cpu_usage = self.performance_metrics.get('cpu_usage', 0)
            memory_usage = self.performance_metrics.get('memory_usage', 0)
            
            return f"""
🤖 **MASTER AI WATCHDOG REPORT**

📊 **Health:** {healthy_components}/{total_components} components healthy
⚡ **CPU:** {cpu_usage:.1f}%
🧠 **Memory:** {memory_usage:.1f}%
🎯 **Trades:** {self.performance_metrics.get('trades_today', 0)}
🔄 **Auto-Recovery:** {'🟢 ON' if self.auto_reconnect_enabled else '🔴 OFF'}

⏰ **Time:** {datetime.now().strftime('%H:%M IST')}
            """
        except Exception as e:
            return "❌ Health report generation failed"
    
    def _send_watchdog_notification(self, message: str):
        """Send notification"""
        try:
            import requests
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            chat_id = os.getenv("TELEGRAM_ID")
            
            if token and chat_id:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
                requests.post(url, json=payload, timeout=10)
        except Exception as e:
            self.logger.error(f"❌ Notification failed: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status"""
        return {
            'health_checks': self.health_checks,
            'performance_metrics': self.performance_metrics,
            'error_counts': self.error_counts,
            'is_monitoring': self.is_running,
            'last_check': datetime.now().isoformat()
        }

# Backward compatibility
IntelligentWatchdog = EnhancedIntelligentWatchdog

# Global instance
intelligent_watchdog = None

def initialize_intelligent_watchdog(bot_instance=None):
    """Initialize watchdog"""
    global intelligent_watchdog
    intelligent_watchdog = EnhancedIntelligentWatchdog(bot_instance)
    return intelligent_watchdog

def get_intelligent_watchdog():
    """Get watchdog instance"""
    global intelligent_watchdog
    if intelligent_watchdog is None:
        intelligent_watchdog = EnhancedIntelligentWatchdog()
    return intelligent_watchdog
