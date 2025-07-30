#!/usr/bin/env python3
"""
CPU Optimization Module for Sniper Swing Trading Bot
- Memory pooling and object reuse
- Efficient data structures and algorithms
- Caching and memoization strategies
- Thread pool optimization
- Garbage collection tuning
- CPU affinity and priority optimization
"""

import gc
import os
import sys
import threading
import time
import psutil
import weakref
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache, wraps
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from collections import deque
import numpy as np
import pandas as pd

@dataclass
class PerformanceConfig:
    """Configuration for performance optimizations"""
    enable_gc_optimization: bool = True
    enable_memory_pooling: bool = True
    enable_cpu_affinity: bool = True
    enable_thread_optimization: bool = True
    cache_size: int = 1024
    gc_threshold: tuple = (700, 10, 10)
    max_workers: int = 4
    memory_limit_mb: int = 500

class MemoryPool:
    """Object pool for frequently used data structures"""
    
    def __init__(self):
        self._dataframes = deque(maxlen=50)
        self._arrays = deque(maxlen=100)
        self._dicts = deque(maxlen=200)
        self._lists = deque(maxlen=200)
        self._lock = threading.Lock()
    
    def get_dataframe(self, shape: tuple = None) -> pd.DataFrame:
        """Get a DataFrame from pool or create new one"""
        with self._lock:
            if self._dataframes:
                df = self._dataframes.popleft()
                df.iloc[:] = np.nan  # Clear data
                return df
            return pd.DataFrame()
    
    def return_dataframe(self, df: pd.DataFrame):
        """Return DataFrame to pool"""
        with self._lock:
            if len(self._dataframes) < 50:
                self._dataframes.append(df)
    
    def get_array(self, shape: tuple = None) -> np.ndarray:
        """Get numpy array from pool"""
        with self._lock:
            if self._arrays and shape:
                for i, arr in enumerate(self._arrays):
                    if arr.shape == shape:
                        return self._arrays.popleft()
            return np.array([]) if not shape else np.zeros(shape)
    
    def return_array(self, arr: np.ndarray):
        """Return array to pool"""
        with self._lock:
            if len(self._arrays) < 100:
                self._arrays.append(arr)
    
    def get_dict(self) -> dict:
        """Get dictionary from pool"""
        with self._lock:
            if self._dicts:
                d = self._dicts.popleft()
                d.clear()
                return d
            return {}
    
    def return_dict(self, d: dict):
        """Return dictionary to pool"""
        with self._lock:
            if len(self._dicts) < 200:
                self._dicts.append(d)
    
    def get_list(self) -> list:
        """Get list from pool"""
        with self._lock:
            if self._lists:
                lst = self._lists.popleft()
                lst.clear()
                return lst
            return []
    
    def return_list(self, lst: list):
        """Return list to pool"""
        with self._lock:
            if len(self._lists) < 200:
                self._lists.append(lst)

class OptimizedThreadPool:
    """Optimized thread pool with CPU affinity and priority"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="OptBot")
        self._setup_thread_optimization()
    
    def _setup_thread_optimization(self):
        """Setup thread optimization"""
        try:
            # Set CPU affinity for better cache utilization
            if hasattr(os, 'sched_setaffinity'):
                cpu_count = os.cpu_count()
                if cpu_count > 4:
                    # Use only high-performance cores (typically first half)
                    cores = list(range(min(4, cpu_count // 2)))
                    os.sched_setaffinity(0, cores)
            
            # Set process priority
            if hasattr(os, 'nice'):
                os.nice(-5)  # Higher priority (requires elevated privileges)
        except (OSError, PermissionError):
            pass  # Ignore if we don't have permissions
    
    def submit_optimized(self, fn: Callable, *args, **kwargs):
        """Submit task with optimization"""
        return self.executor.submit(fn, *args, **kwargs)
    
    def map_optimized(self, fn: Callable, *iterables, timeout=None, chunksize=1):
        """Optimized map operation"""
        return self.executor.map(fn, *iterables, timeout=timeout, chunksize=chunksize)
    
    def shutdown(self):
        """Shutdown thread pool"""
        self.executor.shutdown(wait=True)

class CPUOptimizer:
    """Main CPU optimization manager"""
    
    def __init__(self, config: PerformanceConfig = None):
        self.config = config or PerformanceConfig()
        self.memory_pool = MemoryPool()
        self.thread_pool = OptimizedThreadPool(self.config.max_workers)
        self.cache_stats = {'hits': 0, 'misses': 0}
        self._setup_optimizations()
    
    def _setup_optimizations(self):
        """Setup all CPU optimizations"""
        if self.config.enable_gc_optimization:
            self._optimize_garbage_collection()
        
        if self.config.enable_cpu_affinity:
            self._optimize_cpu_affinity()
        
        # Start background optimization thread
        self._start_background_optimizer()
    
    def _optimize_garbage_collection(self):
        """Optimize garbage collection settings"""
        # Set custom thresholds for better performance
        gc.set_threshold(*self.config.gc_threshold)
        
        # Only enable debug in development if explicitly requested
        if __debug__ and os.getenv('GC_DEBUG', '').lower() == 'true':
            gc.set_debug(gc.DEBUG_LEAK)
        
        # Keep automatic GC enabled but optimized
        gc.enable()
    
    def _optimize_cpu_affinity(self):
        """Optimize CPU affinity for better cache utilization"""
        try:
            if hasattr(os, 'sched_setaffinity'):
                # Get CPU info
                cpu_count = os.cpu_count()
                
                # For multi-core systems, use specific cores for better cache locality
                if cpu_count >= 4:
                    # Use first 4 cores (usually highest performance)
                    preferred_cores = list(range(min(4, cpu_count)))
                    os.sched_setaffinity(0, preferred_cores)
                    print(f"✅ Set CPU affinity to cores: {preferred_cores}")
        except (OSError, AttributeError):
            print("⚠️ CPU affinity optimization not available on this system")
    
    def _start_background_optimizer(self):
        """Start background thread for continuous optimization"""
        def background_optimize():
            while True:
                try:
                    # Only run optimization if enabled and memory usage is high
                    memory_percent = psutil.virtual_memory().percent
                    if memory_percent > 85:  # Only when memory is really high
                        if self.config.enable_gc_optimization:
                            collected = gc.collect()
                            if collected > 10:  # Only log if significant collection
                                print(f"🧹 GC collected {collected} objects")
                    
                    # Sleep for 60 seconds before next optimization cycle (less frequent)
                    time.sleep(60)
                    
                except Exception as e:
                    # Silently handle errors to avoid spam
                    time.sleep(60)
        
        optimizer_thread = threading.Thread(target=background_optimize, daemon=True)
        optimizer_thread.start()
    
    def optimized_cache(self, maxsize: int = 128, typed: bool = False):
        """Enhanced LRU cache with statistics"""
        def decorator(func):
            cached_func = lru_cache(maxsize=maxsize, typed=typed)(func)
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Get cache info before call
                info_before = cached_func.cache_info()
                
                # Call function
                result = cached_func(*args, **kwargs)
                
                # Update statistics
                info_after = cached_func.cache_info()
                if info_after.hits > info_before.hits:
                    self.cache_stats['hits'] += 1
                else:
                    self.cache_stats['misses'] += 1
                
                return result
            
            # Add cache management methods
            wrapper.cache_info = cached_func.cache_info
            wrapper.cache_clear = cached_func.cache_clear
            
            return wrapper
        return decorator
    
    def optimize_dataframe_operations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame operations for better performance"""
        try:
            # Use more efficient data types
            optimized_df = df.copy()
            
            # Convert float64 to float32 where possible (saves ~50% memory)
            float_cols = optimized_df.select_dtypes(include=['float64']).columns
            for col in float_cols:
                if optimized_df[col].dtype == 'float64':
                    # Check if values fit in float32 range
                    col_min, col_max = optimized_df[col].min(), optimized_df[col].max()
                    if (-3.4e38 <= col_min <= 3.4e38) and (-3.4e38 <= col_max <= 3.4e38):
                        optimized_df[col] = optimized_df[col].astype('float32')
            
            # Convert int64 to int32 where possible
            int_cols = optimized_df.select_dtypes(include=['int64']).columns
            for col in int_cols:
                col_min, col_max = optimized_df[col].min(), optimized_df[col].max()
                if -2147483648 <= col_min <= 2147483647 and -2147483648 <= col_max <= 2147483647:
                    optimized_df[col] = optimized_df[col].astype('int32')
            
            return optimized_df
        except Exception as e:
            print(f"Error optimizing DataFrame: {e}")
            return df
    
    def batch_process(self, items: List[Any], batch_size: int = 100, 
                     processor: Callable = None) -> List[Any]:
        """Process items in optimized batches"""
        if not processor:
            return items
        
        results = []
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
        
        # Use thread pool for parallel processing
        futures = []
        for batch in batches:
            future = self.thread_pool.submit_optimized(processor, batch)
            futures.append(future)
        
        # Collect results
        for future in as_completed(futures):
            try:
                batch_result = future.result(timeout=30)
                results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
            except Exception as e:
                print(f"Error processing batch: {e}")
        
        return results
    
    def memory_efficient_calculation(self, data: np.ndarray, operation: str) -> float:
        """Perform memory-efficient calculations on large arrays"""
        try:
            if operation == 'mean':
                # Use online algorithm for mean (Welford's)
                mean = 0.0
                for i, value in enumerate(data, 1):
                    mean += (value - mean) / i
                return mean
            
            elif operation == 'std':
                # Use online algorithm for standard deviation
                mean = 0.0
                m2 = 0.0
                for i, value in enumerate(data, 1):
                    delta = value - mean
                    mean += delta / i
                    delta2 = value - mean
                    m2 += delta * delta2
                
                if i < 2:
                    return 0.0
                return (m2 / (i - 1)) ** 0.5
            
            elif operation == 'sum':
                # Use Kahan summation for better numerical stability
                total = 0.0
                compensation = 0.0
                for value in data:
                    y = value - compensation
                    temp = total + y
                    compensation = (temp - total) - y
                    total = temp
                return total
            
            else:
                # Fallback to numpy
                return getattr(np, operation)(data)
                
        except Exception as e:
            print(f"Error in memory efficient calculation: {e}")
            return 0.0
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get current optimization statistics"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
            
            return {
                'memory_usage_mb': memory_info.rss / (1024 * 1024),
                'cpu_percent': cpu_percent,
                'cache_hits': self.cache_stats['hits'],
                'cache_misses': self.cache_stats['misses'],
                'cache_hit_rate': (
                    self.cache_stats['hits'] / (self.cache_stats['hits'] + self.cache_stats['misses']) * 100
                    if (self.cache_stats['hits'] + self.cache_stats['misses']) > 0 else 0
                ),
                'gc_counts': gc.get_count(),
                'thread_pool_active': len(self.thread_pool.executor._threads) if hasattr(self.thread_pool.executor, '_threads') else 0
            }
        except Exception as e:
            print(f"Error getting optimization stats: {e}")
            return {}
    
    def force_optimization(self):
        """Force immediate optimization (manual trigger)"""
        try:
            # Force garbage collection
            collected = gc.collect()
            print(f"🧹 Manual GC collected {collected} objects")
            
            # Clear caches if memory usage is high
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 75:
                print(f"⚠️ High memory usage ({memory_percent}%), clearing caches...")
                # Note: In real implementation, you'd clear specific caches
                
            return True
        except Exception as e:
            print(f"Error in force optimization: {e}")
            return False
    
    def shutdown(self):
        """Cleanup and shutdown optimizer"""
        try:
            self.thread_pool.shutdown()
            gc.enable()  # Ensure GC is enabled
            gc.set_debug(0)  # Disable debug output
            print("✅ CPU Optimizer shutdown complete")
        except Exception as e:
            print(f"Error during optimizer shutdown: {e}")

# Global optimizer instance
cpu_optimizer = None

def get_cpu_optimizer(config: PerformanceConfig = None) -> CPUOptimizer:
    """Get or create global CPU optimizer instance"""
    global cpu_optimizer
    if cpu_optimizer is None:
        cpu_optimizer = CPUOptimizer(config)
    return cpu_optimizer

# Convenience decorators and functions
def optimized_function(maxsize: int = 128):
    """Decorator for optimizing function calls with caching"""
    def decorator(func):
        optimizer = get_cpu_optimizer()
        return optimizer.optimized_cache(maxsize=maxsize)(func)
    return decorator

def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize DataFrame memory usage"""
    optimizer = get_cpu_optimizer()
    return optimizer.optimize_dataframe_operations(df)

def batch_process_items(items: List[Any], processor: Callable, batch_size: int = 100) -> List[Any]:
    """Process items in optimized batches"""
    optimizer = get_cpu_optimizer()
    return optimizer.batch_process(items, batch_size, processor)

def get_performance_stats() -> Dict[str, Any]:
    """Get current performance statistics"""
    optimizer = get_cpu_optimizer()
    return optimizer.get_optimization_stats()

if __name__ == '__main__':
    # Test the CPU optimizer
    print("🚀 Testing CPU Optimizer...")
    
    config = PerformanceConfig(
        enable_gc_optimization=True,
        enable_memory_pooling=True,
        enable_cpu_affinity=True,
        cache_size=512
    )
    
    optimizer = CPUOptimizer(config)
    
    # Test caching
    @optimizer.optimized_cache(maxsize=100)
    def expensive_calculation(n):
        return sum(i * i for i in range(n))
    
    # Test the function
    print("Testing cached function...")
    start_time = time.time()
    result1 = expensive_calculation(10000)
    time1 = time.time() - start_time
    
    start_time = time.time()
    result2 = expensive_calculation(10000)  # Should be cached
    time2 = time.time() - start_time
    
    print(f"First call: {time1:.4f}s, Second call: {time2:.4f}s")
    print(f"Speedup: {time1/time2:.2f}x" if time2 > 0 else "Instant cache hit!")
    
    # Test DataFrame optimization
    print("Testing DataFrame optimization...")
    df = pd.DataFrame({
        'price': np.random.random(1000).astype('float64'),
        'volume': np.random.randint(1, 1000000, 1000).astype('int64')
    })
    
    original_memory = df.memory_usage(deep=True).sum()
    optimized_df = optimizer.optimize_dataframe_operations(df)
    optimized_memory = optimized_df.memory_usage(deep=True).sum()
    
    print(f"Memory usage: {original_memory} -> {optimized_memory} bytes")
    print(f"Memory savings: {(1 - optimized_memory/original_memory)*100:.1f}%")
    
    # Show stats
    stats = optimizer.get_optimization_stats()
    print(f"📊 Performance Stats: {stats}")
    
    print("✅ CPU Optimizer test completed!") 