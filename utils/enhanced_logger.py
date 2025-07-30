#!/usr/bin/env python3
"""
Enhanced Logging System for Sniper Swing Trading Bot
- Structured logging with JSON output
- Performance metrics tracking
- System health indicators
- Trade performance analytics
- Memory and CPU usage monitoring
"""

import logging
import json
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler
import os
from collections import defaultdict, deque
import sys

class PerformanceMetrics:
    """Track performance metrics for the trading bot"""
    
    def __init__(self):
        self.start_time = time.time()
        self.trade_metrics = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'avg_execution_time': 0.0,
            'max_execution_time': 0.0,
            'min_execution_time': float('inf')
        }
        self.system_metrics = {
            'cpu_usage': deque(maxlen=60),  # Last 60 readings
            'memory_usage': deque(maxlen=60),
            'api_call_count': 0,
            'api_success_rate': 0.0,
            'uptime': 0.0
        }
        self.daily_metrics = defaultdict(lambda: {
            'trades': 0,
            'profit': 0.0,
            'success_rate': 0.0
        })
        self.symbol_metrics = defaultdict(lambda: {
            'trades': 0,
            'success_rate': 0.0,
            'avg_profit': 0.0
        })
        
    def update_system_metrics(self):
        """Update system performance metrics"""
        try:
            # CPU and Memory usage
            cpu_percent = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()
            
            self.system_metrics['cpu_usage'].append(cpu_percent)
            self.system_metrics['memory_usage'].append(memory_info.percent)
            self.system_metrics['uptime'] = time.time() - self.start_time
            
        except Exception as e:
            print(f"Error updating system metrics: {e}")
    
    def record_trade(self, symbol: str, success: bool, profit: float, execution_time: float):
        """Record trade performance metrics"""
        self.trade_metrics['total_trades'] += 1
        
        if success:
            self.trade_metrics['successful_trades'] += 1
            self.trade_metrics['total_profit'] += profit
        else:
            self.trade_metrics['failed_trades'] += 1
            self.trade_metrics['total_loss'] += abs(profit)
        
        # Update execution time metrics
        self.trade_metrics['avg_execution_time'] = (
            (self.trade_metrics['avg_execution_time'] * (self.trade_metrics['total_trades'] - 1) + execution_time) 
            / self.trade_metrics['total_trades']
        )
        self.trade_metrics['max_execution_time'] = max(self.trade_metrics['max_execution_time'], execution_time)
        self.trade_metrics['min_execution_time'] = min(self.trade_metrics['min_execution_time'], execution_time)
        
        # Update daily metrics
        today = datetime.now().strftime('%Y-%m-%d')
        self.daily_metrics[today]['trades'] += 1
        self.daily_metrics[today]['profit'] += profit
        
        # Update symbol metrics
        self.symbol_metrics[symbol]['trades'] += 1
        if success:
            current_avg = self.symbol_metrics[symbol]['avg_profit']
            trade_count = self.symbol_metrics[symbol]['trades']
            self.symbol_metrics[symbol]['avg_profit'] = (
                (current_avg * (trade_count - 1) + profit) / trade_count
            )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        total_trades = self.trade_metrics['total_trades']
        success_rate = (self.trade_metrics['successful_trades'] / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'trade_performance': {
                'total_trades': total_trades,
                'success_rate': round(success_rate, 2),
                'total_profit': round(self.trade_metrics['total_profit'], 2),
                'total_loss': round(self.trade_metrics['total_loss'], 2),
                'net_profit': round(self.trade_metrics['total_profit'] - self.trade_metrics['total_loss'], 2),
                'avg_execution_time': round(self.trade_metrics['avg_execution_time'], 3),
                'max_execution_time': round(self.trade_metrics['max_execution_time'], 3)
            },
            'system_performance': {
                'uptime_hours': round(self.system_metrics['uptime'] / 3600, 2),
                'avg_cpu_usage': round(sum(self.system_metrics['cpu_usage']) / len(self.system_metrics['cpu_usage']), 2) if self.system_metrics['cpu_usage'] else 0,
                'avg_memory_usage': round(sum(self.system_metrics['memory_usage']) / len(self.system_metrics['memory_usage']), 2) if self.system_metrics['memory_usage'] else 0,
                'current_cpu': round(list(self.system_metrics['cpu_usage'])[-1], 2) if self.system_metrics['cpu_usage'] else 0,
                'current_memory': round(list(self.system_metrics['memory_usage'])[-1], 2) if self.system_metrics['memory_usage'] else 0,
                'api_calls': self.system_metrics['api_call_count'],
                'api_success_rate': round(self.system_metrics['api_success_rate'], 2)
            },
            'daily_summary': dict(self.daily_metrics),
            'symbol_summary': dict(self.symbol_metrics)
        }

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'symbol'):
            log_data['symbol'] = record.symbol
        if hasattr(record, 'trade_id'):
            log_data['trade_id'] = record.trade_id
        if hasattr(record, 'execution_time'):
            log_data['execution_time'] = record.execution_time
        if hasattr(record, 'profit'):
            log_data['profit'] = record.profit
        if hasattr(record, 'cpu_usage'):
            log_data['cpu_usage'] = record.cpu_usage
        if hasattr(record, 'memory_usage'):
            log_data['memory_usage'] = record.memory_usage
        
        return json.dumps(log_data)

class EnhancedLogger:
    """Enhanced logging system with performance tracking"""
    
    def __init__(self, name: str = "SniperSwingBot", log_dir: str = "logs"):
        self.name = name
        self.log_dir = log_dir
        self.metrics = PerformanceMetrics()
        self.logger = None
        self._setup_logging()
        
        # Start background metrics collection
        self._start_metrics_collection()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler with standard formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # File handler with structured JSON formatting
        json_handler = RotatingFileHandler(
            os.path.join(self.log_dir, f'{self.name.lower()}_structured.log'),
            maxBytes=50*1024*1024,  # 50MB
            backupCount=5
        )
        json_handler.setFormatter(StructuredFormatter())
        json_handler.setLevel(logging.INFO)
        
        # Performance metrics handler
        perf_handler = RotatingFileHandler(
            os.path.join(self.log_dir, f'{self.name.lower()}_performance.log'),
            maxBytes=20*1024*1024,  # 20MB
            backupCount=3
        )
        perf_formatter = logging.Formatter(
            '%(asctime)s [PERF] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        perf_handler.setFormatter(perf_formatter)
        perf_handler.setLevel(logging.INFO)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(json_handler)
        
        # Create performance logger
        self.perf_logger = logging.getLogger(f"{self.name}.performance")
        self.perf_logger.setLevel(logging.INFO)
        self.perf_logger.addHandler(perf_handler)
        self.perf_logger.propagate = False
    
    def _start_metrics_collection(self):
        """Start background thread for metrics collection"""
        def collect_metrics():
            while True:
                try:
                    self.metrics.update_system_metrics()
                    time.sleep(60)  # Update every minute
                except Exception as e:
                    self.logger.error(f"Error in metrics collection: {e}")
                    time.sleep(60)
        
        metrics_thread = threading.Thread(target=collect_metrics, daemon=True)
        metrics_thread.start()
    
    def log_trade_entry(self, symbol: str, trade_id: str, signal_type: str, price: float, quantity: int, reasoning: str):
        """Log trade entry with structured data"""
        self.logger.info(
            f"Trade Entry: {symbol} {signal_type.upper()} - Price: ₹{price}, Qty: {quantity}",
            extra={
                'symbol': symbol,
                'trade_id': trade_id,
                'signal_type': signal_type,
                'price': price,
                'quantity': quantity,
                'reasoning': reasoning,
                'event_type': 'trade_entry'
            }
        )
    
    def log_trade_exit(self, symbol: str, trade_id: str, entry_price: float, exit_price: float, 
                      profit: float, execution_time: float, success: bool):
        """Log trade exit with performance metrics"""
        self.metrics.record_trade(symbol, success, profit, execution_time)
        
        self.logger.info(
            f"Trade Exit: {symbol} - Entry: ₹{entry_price}, Exit: ₹{exit_price}, P&L: ₹{profit:.2f}",
            extra={
                'symbol': symbol,
                'trade_id': trade_id,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'profit': profit,
                'execution_time': execution_time,
                'success': success,
                'event_type': 'trade_exit'
            }
        )
    
    def log_system_health(self):
        """Log current system health metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.perf_logger.info(
                f"System Health - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%",
                extra={
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'disk_usage': disk.percent,
                    'available_memory': memory.available / (1024**3),  # GB
                    'event_type': 'system_health'
                }
            )
        except Exception as e:
            self.logger.error(f"Error logging system health: {e}")
    
    def log_performance_summary(self):
        """Log comprehensive performance summary"""
        summary = self.metrics.get_performance_summary()
        
        self.perf_logger.info(
            f"Performance Summary - Trades: {summary['trade_performance']['total_trades']}, "
            f"Success Rate: {summary['trade_performance']['success_rate']}%, "
            f"Net P&L: ₹{summary['trade_performance']['net_profit']}"
        )
        
        # Log detailed summary as JSON
        self.perf_logger.info(json.dumps(summary, indent=2))
    
    def log_api_call(self, endpoint: str, success: bool, response_time: float):
        """Log API call performance"""
        self.metrics.system_metrics['api_call_count'] += 1
        
        if success:
            current_success_count = self.metrics.system_metrics['api_success_rate'] * (self.metrics.system_metrics['api_call_count'] - 1)
            self.metrics.system_metrics['api_success_rate'] = (current_success_count + 1) / self.metrics.system_metrics['api_call_count']
        else:
            current_success_count = self.metrics.system_metrics['api_success_rate'] * (self.metrics.system_metrics['api_call_count'] - 1)
            self.metrics.system_metrics['api_success_rate'] = current_success_count / self.metrics.system_metrics['api_call_count']
        
        self.logger.info(
            f"API Call: {endpoint} - {'Success' if success else 'Failed'} - {response_time:.3f}s",
            extra={
                'endpoint': endpoint,
                'success': success,
                'response_time': response_time,
                'event_type': 'api_call'
            }
        )
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """Log error with additional context"""
        self.logger.error(
            f"Error: {type(error).__name__}: {str(error)}",
            extra={
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context,
                'event_type': 'error'
            },
            exc_info=True
        )
    
    def info(self, message: str, **kwargs):
        """Standard info logging with optional extra data"""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Standard error logging with optional extra data"""
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Standard warning logging with optional extra data"""
        self.logger.warning(message, extra=kwargs)

# Global logger instance
enhanced_logger = None

def get_enhanced_logger(name: str = "SniperSwingBot") -> EnhancedLogger:
    """Get or create the global enhanced logger instance"""
    global enhanced_logger
    if enhanced_logger is None:
        enhanced_logger = EnhancedLogger(name)
    return enhanced_logger

# Convenience functions for backward compatibility
def log_trade_entry(symbol: str, trade_id: str, signal_type: str, price: float, quantity: int, reasoning: str):
    logger = get_enhanced_logger()
    logger.log_trade_entry(symbol, trade_id, signal_type, price, quantity, reasoning)

def log_trade_exit(symbol: str, trade_id: str, entry_price: float, exit_price: float, profit: float, execution_time: float, success: bool):
    logger = get_enhanced_logger()
    logger.log_trade_exit(symbol, trade_id, entry_price, exit_price, profit, execution_time, success)

def log_system_health():
    logger = get_enhanced_logger()
    logger.log_system_health()

def log_performance_summary():
    logger = get_enhanced_logger()
    logger.log_performance_summary()

if __name__ == '__main__':
    # Test the enhanced logging system
    logger = get_enhanced_logger("TestBot")
    
    # Test various logging scenarios
    logger.info("Starting enhanced logging test")
    logger.log_system_health()
    
    # Simulate trade logging
    logger.log_trade_entry("NIFTY", "T001", "bullish", 24500, 75, "Strong MA hierarchy with RSI confirmation")
    time.sleep(2)
    logger.log_trade_exit("NIFTY", "T001", 24500, 24650, 150, 2.5, True)
    
    logger.log_performance_summary()
    print("✅ Enhanced logging test completed. Check logs/ directory for output files.") 