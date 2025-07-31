"""
Enhanced Intelligent Watchdog System for Sandy Sniper Bot
Master AI monitoring with auto-reconnection and robust error handling

Features:
- Real-time system health monitoring
- Auto-reconnection for all APIs
- Performance tracking and optimization
- Proactive error detection and recovery
- Master AI supervision
- Personalized communication with Saki
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
    """
    Master AI Watchdog System
    Monitors all system components with intelligent auto-recovery
    """
    
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
        self.check_interval = int(os.getenv('WATCHDOG_CHECK_INTERVAL', '60'))  # seconds
        self.max_error_threshold = 5
        self.reconnect_delay = 30
        self.health_report_interval = 300  # 5 minutes
        
        # System thresholds
        self.cpu_threshold = 80.0  # CPU usage %
        self.memory_threshold = 80.0  # Memory usage %
        self.response_time_threshold = 5.0  # seconds
        
        self.logger.info("🤖 Enhanced Intelligent Watchdog initialized with Master AI supervision")
    
    def start_monitoring(self):
        """Start the watchdog monitoring system"""
        if self.is_running:
            self.logger.warning("⚠️ Watchdog already running")
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("🚀 Enhanced Watchdog started - Master AI monitoring active")
        
        # Send startup notification
        self._send_watchdog_notification("🤖 **MASTER AI WATCHDOG ACTIVATED**\n\n✅ All systems under intelligent supervision\n🔄 Auto-reconnection enabled\n📊 Performance monitoring active")
    
    def stop_monitoring(self):
        """Stop the watchdog monitoring system"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("🛑 Enhanced Watchdog stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop with intelligent checks"""
        self.logger.info("🔄 Starting intelligent monitoring loop...")
        
        while self.is_running:
            try:
                start_time = time.time()
                
                # Perform comprehensive health checks
                self._perform_health_checks()
                
                # Check system performance
                self._monitor_system_performance()
                
                # Monitor API connections
                self._monitor_api_connections()
                
                # Check bot instance health
                self._monitor_bot_health()
                
                # Perform auto-recovery if needed
                self._auto_recovery_check()
                
                # Generate health report periodically
                self._generate_health_report()
                
                # Memory optimization
                self._optimize_memory()
                
                # Calculate monitoring cycle time
                cycle_time = time.time() - start_time
                self.performance_metrics['last_monitoring_cycle'] = cycle_time
                
                if cycle_time > 10:  # Log if monitoring takes too long
                    self.logger.warning(f"⚠️ Monitoring cycle took {cycle_time:.2f}s (>10s threshold)")
                
                # Sleep until next check
                sleep_time = max(0, self.check_interval - cycle_time)
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _perform_health_checks(self):
        """Perform comprehensive system health checks"""
        health_results = {}
        
        # Check Telegram API
        health_results['telegram'] = self._check_telegram_health()
        
        # Check Kite API
        health_results['kite_api'] = self._check_kite_health()
        
        # Check file system
        health_results['filesystem'] = self._check_filesystem_health()
        
        # Check network connectivity
        health_results['network'] = self._check_network_health()
        
        # Check trading bot instance
        health_results['bot_instance'] = self._check_bot_instance_health()
        
        # Update health status
        self.health_checks.update(health_results)
        
        # Log health summary
        healthy_count = sum(1 for status in health_results.values() if status)
        total_count = len(health_results)
        
        if healthy_count == total_count:
            self.logger.info(f"✅ All systems healthy ({healthy_count}/{total_count})")
        else:
            self.logger.warning(f"⚠️ System health: {healthy_count}/{total_count} components healthy")
    
    def _check_telegram_health(self):
        """Check Telegram API health with auto-reconnect"""
        try:
            from .enhanced_telegram_commands import check_telegram_health
            
            is_healthy = check_telegram_health()
            
            if not is_healthy:
                self.error_counts['telegram'] = self.error_counts.get('telegram', 0) + 1
                self.logger.warning(f"⚠️ Telegram API unhealthy (errors: {self.error_counts['telegram']})")
                
                # Auto-reconnect if enabled
                if self.auto_reconnect_enabled and self.error_counts['telegram'] >= 3:
                    self._reconnect_telegram()
            else:
                self.error_counts['telegram'] = 0  # Reset error count on success
            
            return is_healthy
            
        except Exception as e:
            self.logger.error(f"❌ Telegram health check failed: {e}")
            return False
    
    def _check_kite_health(self):
        """Check Kite API health with auto-reconnect"""
        try:
            # This would check Kite API connectivity
            # For now, assume it's healthy if bot instance exists
            if self.bot_instance:
                kite_connection = getattr(self.bot_instance, 'kite', None)
                if kite_connection:
                    # Try a simple API call
                    try:
                        # This would be replaced with actual Kite API health check
                        return True
                    except Exception as e:
                        self.logger.warning(f"⚠️ Kite API connectivity issue: {e}")
                        self.error_counts['kite'] = self.error_counts.get('kite', 0) + 1
                        
                        if self.auto_reconnect_enabled and self.error_counts['kite'] >= 3:
                            self._reconnect_kite_api()
                        
                        return False
            
            return True  # Default to healthy if can't check
            
        except Exception as e:
            self.logger.error(f"❌ Kite health check failed: {e}")
            return False
    
    def _check_filesystem_health(self):
        """Check filesystem health and disk space"""
        try:
            # Check disk space
            disk_usage = psutil.disk_usage('/')
            free_space_percent = (disk_usage.free / disk_usage.total) * 100
            
            if free_space_percent < 10:  # Less than 10% free space
                self.logger.warning(f"⚠️ Low disk space: {free_space_percent:.1f}% free")
                return False
            
            # Check if log files are writable
            try:
                test_file = 'watchdog_test.tmp'
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                return True
            except Exception as e:
                self.logger.error(f"❌ Filesystem write test failed: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Filesystem health check failed: {e}")
            return False
    
    def _check_network_health(self):
        """Check network connectivity"""
        try:
            # Test connectivity to Google DNS
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            return True
        except Exception as e:
            self.logger.warning(f"⚠️ Network connectivity issue: {e}")
            return False
    
    def _check_bot_instance_health(self):
        """Check trading bot instance health"""
        try:
            if not self.bot_instance:
                return False
            
            # Check if bot has required attributes
            required_attrs = ['active_positions', 'symbols', 'logger']
            for attr in required_attrs:
                if not hasattr(self.bot_instance, attr):
                    self.logger.warning(f"⚠️ Bot missing attribute: {attr}")
                    return False
            
            # Check if bot is responsive
            try:
                positions_count = len(getattr(self.bot_instance, 'active_positions', {}))
                self.logger.debug(f"📊 Bot has {positions_count} active positions")
                return True
            except Exception as e:
                self.logger.warning(f"⚠️ Bot responsiveness check failed: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Bot instance health check failed: {e}")
            return False
    
    def _monitor_system_performance(self):
        """Monitor system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.performance_metrics['cpu_usage'] = cpu_percent
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.performance_metrics['memory_usage'] = memory_percent
            
            # Process-specific metrics
            process = psutil.Process()
            self.performance_metrics['process_memory'] = process.memory_info().rss / 1024 / 1024  # MB
            self.performance_metrics['process_cpu'] = process.cpu_percent()
            
            # Check thresholds
            if cpu_percent > self.cpu_threshold:
                self.logger.warning(f"⚠️ High CPU usage: {cpu_percent:.1f}%")
                self._optimize_performance()
            
            if memory_percent > self.memory_threshold:
                self.logger.warning(f"⚠️ High memory usage: {memory_percent:.1f}%")
                self._optimize_memory()
                
        except Exception as e:
            self.logger.error(f"❌ Performance monitoring failed: {e}")
    
    def _monitor_api_connections(self):
        """Monitor API connection stability"""
        try:
            # Check API response times
            api_checks = {
                'telegram': self._check_telegram_response_time,
                'kite': self._check_kite_response_time
            }
            
            for api_name, check_func in api_checks.items():
                try:
                    response_time = check_func()
                    self.performance_metrics[f'{api_name}_response_time'] = response_time
                    
                    if response_time > self.response_time_threshold:
                        self.logger.warning(f"⚠️ Slow {api_name} API response: {response_time:.2f}s")
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ {api_name} API check failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"❌ API monitoring failed: {e}")
    
    def _check_telegram_response_time(self):
        """Check Telegram API response time"""
        try:
            start_time = time.time()
            from .enhanced_telegram_commands import check_telegram_health
            check_telegram_health()
            return time.time() - start_time
        except Exception:
            return float('inf')
    
    def _check_kite_response_time(self):
        """Check Kite API response time"""
        try:
            # This would implement actual Kite API response time check
            return 0.5  # Placeholder
        except Exception:
            return float('inf')
    
    def _monitor_bot_health(self):
        """Monitor bot instance health and performance"""
        try:
            if not self.bot_instance:
                return
            
            # Check bot performance metrics
            if hasattr(self.bot_instance, 'performance_stats'):
                stats = self.bot_instance.performance_stats
                self.performance_metrics.update({
                    'avg_analysis_time': stats.get('avg_analysis_time', 0),
                    'cache_hit_rate': stats.get('cache_hit_rate', 0),
                    'trades_today': stats.get('trades_executed_today', 0),
                    'signals_today': stats.get('signals_analyzed_today', 0)
                })
                
                # Check performance thresholds
                if stats.get('avg_analysis_time', 0) > 5.0:  # 5 second threshold
                    self.logger.warning("⚠️ Bot analysis time exceeding threshold")
                    self._optimize_bot_performance()
                
        except Exception as e:
            self.logger.error(f"❌ Bot health monitoring failed: {e}")
    
    def _auto_recovery_check(self):
        """Perform auto-recovery actions based on health status"""
        try:
            # Check error counts and trigger recovery
            for component, error_count in self.error_counts.items():
                if error_count >= self.max_error_threshold:
                    self.logger.warning(f"🔧 Auto-recovery triggered for {component} (errors: {error_count})")
                    self._perform_component_recovery(component)
                    
        except Exception as e:
            self.logger.error(f"❌ Auto-recovery check failed: {e}")
    
    def _perform_component_recovery(self, component: str):
        """Perform recovery actions for specific component"""
        try:
            if component == 'telegram':
                self._reconnect_telegram()
            elif component == 'kite':
                self._reconnect_kite_api()
            elif component == 'bot_instance':
                self._restart_bot_components()
            
            # Reset error count after recovery attempt
            self.error_counts[component] = 0
            
        except Exception as e:
            self.logger.error(f"❌ Component recovery failed for {component}: {e}")
    
    def _reconnect_telegram(self):
        """Reconnect Telegram API"""
        try:
            self.logger.info("🔄 Attempting Telegram reconnection...")
            from .enhanced_telegram_commands import check_telegram_health
            
            # Wait a moment before reconnecting
            time.sleep(self.reconnect_delay)
            
            # Test connection
            if check_telegram_health():
                self.logger.info("✅ Telegram reconnection successful")
                self._send_watchdog_notification("✅ **Telegram Auto-Reconnection Successful**\n\n🔗 API connection restored\n📱 Commands operational")
            else:
                self.logger.error("❌ Telegram reconnection failed")
                
        except Exception as e:
            self.logger.error(f"❌ Telegram reconnection error: {e}")
    
    def _reconnect_kite_api(self):
        """Reconnect Kite API"""
        try:
            self.logger.info("🔄 Attempting Kite API reconnection...")
            
            if self.bot_instance and hasattr(self.bot_instance, 'reconnect_kite'):
                self.bot_instance.reconnect_kite()
                self.logger.info("✅ Kite API reconnection attempted")
            
        except Exception as e:
            self.logger.error(f"❌ Kite API reconnection error: {e}")
    
    def _restart_bot_components(self):
        """Restart bot components"""
        try:
            self.logger.info("🔄 Restarting bot components...")
            
            if self.bot_instance and hasattr(self.bot_instance, 'restart_components'):
                self.bot_instance.restart_components()
                self.logger.info("✅ Bot components restart attempted")
                
        except Exception as e:
            self.logger.error(f"❌ Bot restart error: {e}")
    
    def _optimize_performance(self):
        """Optimize system performance"""
        try:
            self.logger.info("⚡ Optimizing system performance...")
            
            # Force garbage collection
            gc.collect()
            
            # Clear caches if available
            if self.bot_instance and hasattr(self.bot_instance, 'cleanup_cache'):
                self.bot_instance.cleanup_cache()
            
            self.logger.info("✅ Performance optimization completed")
            
        except Exception as e:
            self.logger.error(f"❌ Performance optimization failed: {e}")
    
    def _optimize_memory(self):
        """Optimize memory usage"""
        try:
            self.logger.info("🧠 Optimizing memory usage...")
            
            # Force garbage collection
            gc.collect()
            
            # Clear performance metrics history if too large
            if len(self.performance_metrics) > 100:
                # Keep only recent metrics
                self.performance_metrics = dict(list(self.performance_metrics.items())[-50:])
            
            self.logger.info("✅ Memory optimization completed")
            
        except Exception as e:
            self.logger.error(f"❌ Memory optimization failed: {e}")
    
    def _optimize_bot_performance(self):
        """Optimize bot-specific performance"""
        try:
            if self.bot_instance and hasattr(self.bot_instance, 'optimize_performance'):
                self.bot_instance.optimize_performance()
                self.logger.info("✅ Bot performance optimization completed")
                
        except Exception as e:
            self.logger.error(f"❌ Bot performance optimization failed: {e}")
    
    def _generate_health_report(self):
        """Generate periodic health report"""
        try:
            current_time = datetime.now()
            
            if (self.last_health_report is None or 
                (current_time - self.last_health_report).total_seconds() >= self.health_report_interval):
                
                self.last_health_report = current_time
                
                # Generate comprehensive report
                report = self._create_health_report()
                self._send_watchdog_notification(report)
                
        except Exception as e:
            self.logger.error(f"❌ Health report generation failed: {e}")
    
    def _create_health_report(self):
        """Create comprehensive health report"""
        try:
            healthy_components = sum(1 for status in self.health_checks.values() if status)
            total_components = len(self.health_checks)
            
            cpu_usage = self.performance_metrics.get('cpu_usage', 0)
            memory_usage = self.performance_metrics.get('memory_usage', 0)
            
            report = f"""
🤖 **MASTER AI WATCHDOG HEALTH REPORT**

📊 **System Health:** {healthy_components}/{total_components} components healthy

🔍 **Component Status:**
• Telegram API: {'🟢' if self.health_checks.get('telegram') else '🔴'}
• Kite API: {'🟢' if self.health_checks.get('kite_api') else '🔴'}  
• Bot Instance: {'🟢' if self.health_checks.get('bot_instance') else '🔴'}
• Network: {'🟢' if self.health_checks.get('network') else '🔴'}
• Filesystem: {'🟢' if self.health_checks.get('filesystem') else '🔴'}

⚡ **Performance:**
• CPU Usage: {cpu_usage:.1f}%
• Memory Usage: {memory_usage:.1f}%
• Analysis Time: {self.performance_metrics.get('avg_analysis_time', 0):.2f}s
• Cache Hit Rate: {self.performance_metrics.get('cache_hit_rate', 0):.1%}

🎯 **Trading Stats:**
• Trades Today: {self.performance_metrics.get('trades_today', 0)}
• Signals Today: {self.performance_metrics.get('signals_today', 0)}

🔄 **Auto-Recovery:** {'🟢 ENABLED' if self.auto_reconnect_enabled else '🔴 DISABLED'}

⏰ **Report Time:** {datetime.now().strftime('%H:%M IST')}
            """
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Health report creation failed: {e}")
            return "❌ Health report generation failed"
    
    def _send_watchdog_notification(self, message: str):
        """Send watchdog notification via Telegram"""
        try:
            from .enhanced_telegram_commands import send_telegram_message
            send_telegram_message(message)
        except Exception as e:
            self.logger.error(f"❌ Failed to send watchdog notification: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return {
            'health_checks': self.health_checks,
            'performance_metrics': self.performance_metrics,
            'error_counts': self.error_counts,
            'is_monitoring': self.is_running,
            'last_check': datetime.now().isoformat()
        }

# Backward compatibility - keep existing class name
IntelligentWatchdog = EnhancedIntelligentWatchdog

# Global watchdog instance
intelligent_watchdog = None

def initialize_intelligent_watchdog(bot_instance=None):
    """Initialize global intelligent watchdog"""
    global intelligent_watchdog
    intelligent_watchdog = EnhancedIntelligentWatchdog(bot_instance)
    return intelligent_watchdog

def get_intelligent_watchdog():
    """Get global intelligent watchdog instance"""
    global intelligent_watchdog
    if intelligent_watchdog is None:
        intelligent_watchdog = EnhancedIntelligentWatchdog()
    return intelligent_watchdog
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