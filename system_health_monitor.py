"""
System Health Monitor
Monitors system resources, processes, and overall bot health
"""

import os
import psutil
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class SystemHealthMonitor:
    def __init__(self, monitoring_interval=60):
        self.monitoring_interval = monitoring_interval
        self.running = False
        self.health_data = {}
        self.alerts_sent = set()
        self.monitor_thread = None
        
        # Health thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'network_errors': 10,
            'process_count': 500
        }
    
    def get_system_health(self) -> Dict:
        """Get comprehensive system health metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            process_count = len(psutil.pids())
            
            # Bot-specific metrics
            bot_processes = self._get_bot_processes()
            
            health_data = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'percent': swap.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv,
                    'errin': network.errin,
                    'errout': network.errout,
                    'dropin': network.dropin,
                    'dropout': network.dropout
                },
                'processes': {
                    'total_count': process_count,
                    'bot_processes': bot_processes
                }
            }
            
            return health_data
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _get_bot_processes(self) -> List[Dict]:
        """Get information about bot-related processes"""
        bot_processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    process_info = proc.info
                    process_name = process_info['name'].lower()
                    
                    # Check if process is related to our bot
                    if any(keyword in process_name for keyword in ['python', 'sniper', 'bot']):
                        # Get command line to verify it's our bot
                        try:
                            cmdline = ' '.join(proc.cmdline())
                            if any(script in cmdline for script in ['main.py', 'runner.py', 'sniper_swing.py']):
                                bot_processes.append({
                                    'pid': process_info['pid'],
                                    'name': process_info['name'],
                                    'cpu_percent': process_info['cpu_percent'],
                                    'memory_percent': process_info['memory_percent'],
                                    'status': process_info['status'],
                                    'cmdline': cmdline
                                })
                        except (psutil.AccessDenied, psutil.ZombieProcess):
                            continue
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            logger.error(f"Error getting bot processes: {e}")
        
        return bot_processes
    
    def check_health_alerts(self, health_data: Dict) -> List[str]:
        """Check for health alerts and return list of alert messages"""
        alerts = []
        
        try:
            # CPU alert
            cpu_percent = health_data.get('cpu', {}).get('percent', 0)
            if cpu_percent > self.thresholds['cpu_percent']:
                alert = f"🚨 HIGH CPU USAGE: {cpu_percent:.1f}%"
                alerts.append(alert)
            
            # Memory alert
            memory_percent = health_data.get('memory', {}).get('percent', 0)
            if memory_percent > self.thresholds['memory_percent']:
                alert = f"🚨 HIGH MEMORY USAGE: {memory_percent:.1f}%"
                alerts.append(alert)
            
            # Disk alert
            disk_percent = health_data.get('disk', {}).get('percent', 0)
            if disk_percent > self.thresholds['disk_percent']:
                alert = f"🚨 HIGH DISK USAGE: {disk_percent:.1f}%"
                alerts.append(alert)
            
            # Network errors alert
            network = health_data.get('network', {})
            total_errors = network.get('errin', 0) + network.get('errout', 0)
            if total_errors > self.thresholds['network_errors']:
                alert = f"🚨 NETWORK ERRORS: {total_errors} errors detected"
                alerts.append(alert)
            
            # Process count alert
            process_count = health_data.get('processes', {}).get('total_count', 0)
            if process_count > self.thresholds['process_count']:
                alert = f"🚨 HIGH PROCESS COUNT: {process_count} processes"
                alerts.append(alert)
            
            # Bot process alert
            bot_processes = health_data.get('processes', {}).get('bot_processes', [])
            if not bot_processes:
                alert = "🚨 NO BOT PROCESSES DETECTED"
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error checking health alerts: {e}")
            alerts.append(f"❌ Error checking health: {e}")
        
        return alerts
    
    def get_health_summary(self) -> str:
        """Get formatted health summary for notifications"""
        try:
            health_data = self.get_system_health()
            
            if 'error' in health_data:
                return f"❌ System Health Error: {health_data['error']}"
            
            cpu_percent = health_data.get('cpu', {}).get('percent', 0)
            memory_percent = health_data.get('memory', {}).get('percent', 0)
            disk_percent = health_data.get('disk', {}).get('percent', 0)
            process_count = health_data.get('processes', {}).get('total_count', 0)
            bot_processes = len(health_data.get('processes', {}).get('bot_processes', []))
            
            summary = "📊 System Health Status\n\n"
            summary += f"🖥️ CPU: {cpu_percent:.1f}%\n"
            summary += f"🧠 Memory: {memory_percent:.1f}%\n"
            summary += f"💾 Disk: {disk_percent:.1f}%\n"
            summary += f"⚙️ Processes: {process_count}\n"
            summary += f"🤖 Bot Processes: {bot_processes}\n"
            
            # Add alerts if any
            alerts = self.check_health_alerts(health_data)
            if alerts:
                summary += f"\n⚠️ ALERTS:\n"
                for alert in alerts:
                    summary += f"• {alert}\n"
            else:
                summary += f"\n✅ All systems normal"
            
            return summary
            
        except Exception as e:
            return f"❌ Error generating health summary: {e}"
    
    def monitor_health(self):
        """Continuous health monitoring loop"""
        logger.info("🏥 System health monitoring started")
        
        while self.running:
            try:
                health_data = self.get_system_health()
                self.health_data = health_data
                
                # Check for alerts
                alerts = self.check_health_alerts(health_data)
                
                # Send alerts (avoid spam by tracking sent alerts)
                for alert in alerts:
                    alert_key = alert[:50]  # Use first 50 chars as key
                    if alert_key not in self.alerts_sent:
                        self.alerts_sent.add(alert_key)
                        logger.warning(f"Health Alert: {alert}")
                        
                        # Send telegram notification if available
                        try:
                            from telegram_commands import send_telegram_message
                            send_telegram_message(f"🏥 SYSTEM HEALTH ALERT\n{alert}")
                        except Exception as e:
                            logger.error(f"Failed to send health alert: {e}")
                
                # Clear old alerts after some time
                if len(self.alerts_sent) > 20:
                    self.alerts_sent.clear()
                
                # Save health data to file for analysis
                self._save_health_data(health_data)
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
            
            time.sleep(self.monitoring_interval)
    
    def _save_health_data(self, health_data: Dict):
        """Save health data to file for analysis"""
        try:
            health_file = "system_health.json"
            
            # Load existing data
            if os.path.exists(health_file):
                with open(health_file, 'r') as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            
            # Add new data
            existing_data.append(health_data)
            
            # Keep only last 100 entries to prevent file from growing too large
            if len(existing_data) > 100:
                existing_data = existing_data[-100:]
            
            # Save back to file
            with open(health_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving health data: {e}")
    
    def start_monitoring(self):
        """Start health monitoring in background thread"""
        if self.running:
            logger.warning("Health monitoring already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_health, daemon=True)
        self.monitor_thread.start()
        logger.info("🚀 System health monitoring thread started")
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 System health monitoring stopped")

# Global health monitor instance
_health_monitor = None

def get_health_monitor() -> SystemHealthMonitor:
    """Get the global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = SystemHealthMonitor()
    return _health_monitor

def start_system_health_monitor():
    """Start the system health monitor"""
    monitor = get_health_monitor()
    monitor.start_monitoring()

def stop_system_health_monitor():
    """Stop the system health monitor"""
    monitor = get_health_monitor()
    monitor.stop_monitoring()

def get_system_health_summary() -> str:
    """Get system health summary"""
    monitor = get_health_monitor()
    return monitor.get_health_summary()

def is_system_healthy() -> bool:
    """Check if system is healthy (no critical alerts)"""
    try:
        monitor = get_health_monitor()
        health_data = monitor.get_system_health()
        alerts = monitor.check_health_alerts(health_data)
        
        # System is healthy if no critical alerts
        critical_keywords = ['HIGH CPU', 'HIGH MEMORY', 'HIGH DISK', 'NO BOT PROCESSES']
        critical_alerts = [alert for alert in alerts if any(keyword in alert for keyword in critical_keywords)]
        
        return len(critical_alerts) == 0
        
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return False

if __name__ == "__main__":
    # Test the system health monitor
    print("=== System Health Monitor Test ===")
    
    monitor = SystemHealthMonitor()
    
    # Get current health
    health = monitor.get_system_health()
    print("Current Health Data:")
    print(json.dumps(health, indent=2))
    
    # Get health summary
    print("\nHealth Summary:")
    print(monitor.get_health_summary())
    
    # Check if system is healthy
    print(f"\nSystem Healthy: {is_system_healthy()}")
    
    # Start monitoring for a short test
    print("\nStarting monitoring for 10 seconds...")
    monitor.start_monitoring()
    time.sleep(10)
    monitor.stop_monitoring()
