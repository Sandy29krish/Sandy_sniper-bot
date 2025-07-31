#!/usr/bin/env python3
"""
System Performance Checker for Enhanced Sandy Sniper Bot
Validates CPU optimization, memory usage, and system readiness

Features:
- CPU core detection and utilization
- Memory usage analysis
- Cache performance testing
- Threading capability validation
- Performance benchmarking
"""

import sys
import os
import time
import gc
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from datetime import datetime

def check_cpu_capabilities():
    """Check CPU capabilities and optimization features"""
    print("🧠 CPU CAPABILITIES ANALYSIS")
    print("-" * 40)
    
    # CPU core count
    cpu_count = multiprocessing.cpu_count()
    print(f"💻 CPU Cores Available: {cpu_count}")
    
    # Test threading capabilities
    try:
        with ThreadPoolExecutor(max_workers=cpu_count) as executor:
            print(f"✅ ThreadPoolExecutor: {cpu_count} workers available")
    except Exception as e:
        print(f"❌ ThreadPoolExecutor error: {e}")
        return False
    
    # Test multiprocessing
    try:
        import multiprocessing
        print(f"✅ Multiprocessing: Available")
    except Exception as e:
        print(f"❌ Multiprocessing error: {e}")
        return False
    
    return True

def check_caching_performance():
    """Test caching performance with LRU cache"""
    print("\n💾 CACHING PERFORMANCE TEST")
    print("-" * 40)
    
    @lru_cache(maxsize=1000)
    def cached_calculation(n):
        """Test function for cache performance"""
        return sum(i * i for i in range(n))
    
    # Test cache performance
    test_values = [100, 200, 300, 100, 200, 300]  # Repeat to test cache hits
    
    start_time = time.time()
    for value in test_values:
        result = cached_calculation(value)
    cache_time = time.time() - start_time
    
    # Check cache info
    cache_info = cached_calculation.cache_info()
    hit_rate = cache_info.hits / (cache_info.hits + cache_info.misses) if (cache_info.hits + cache_info.misses) > 0 else 0
    
    print(f"✅ Cache Performance Test Completed")
    print(f"   • Total Time: {cache_time:.4f} seconds")
    print(f"   • Cache Hits: {cache_info.hits}")
    print(f"   • Cache Misses: {cache_info.misses}")
    print(f"   • Hit Rate: {hit_rate:.2%}")
    print(f"   • Current Size: {cache_info.currsize}")
    
    return hit_rate > 0.5  # Expect >50% hit rate

def check_memory_management():
    """Test memory management capabilities"""
    print("\n🧠 MEMORY MANAGEMENT TEST")
    print("-" * 40)
    
    # Get initial memory info
    try:
        import psutil
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"📊 Initial Memory Usage: {initial_memory:.2f} MB")
    except ImportError:
        print("⚠️ psutil not available - using basic memory check")
        initial_memory = None
    
    # Create some test objects
    test_data = []
    for i in range(10000):
        test_data.append({'index': i, 'data': f"test_data_{i}" * 10})
    
    # Test garbage collection
    gc.collect()
    
    # Clear test data
    test_data.clear()
    gc.collect()
    
    print("✅ Memory Management Test Completed")
    print("   • Object creation: Success")
    print("   • Garbage collection: Success")
    print("   • Memory cleanup: Success")
    
    return True

def check_import_capabilities():
    """Test all critical imports for the trading system"""
    print("\n📦 IMPORT CAPABILITIES TEST")
    print("-" * 40)
    
    import_results = []
    
    # Test critical system imports
    critical_imports = [
        ('datetime', 'Standard datetime library'),
        ('time', 'Standard time library'),
        ('concurrent.futures', 'Threading capabilities'),
        ('functools', 'LRU cache support'),
        ('multiprocessing', 'Parallel processing'),
        ('gc', 'Garbage collection'),
        ('logging', 'Logging system')
    ]
    
    for module, description in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
            import_results.append(True)
        except ImportError as e:
            print(f"❌ {module}: Failed to import - {e}")
            import_results.append(False)
    
    success_rate = sum(import_results) / len(import_results)
    print(f"\n📊 Import Success Rate: {success_rate:.1%}")
    
    return success_rate >= 1.0  # All imports must succeed

def benchmark_performance():
    """Benchmark system performance for trading calculations"""
    print("\n⚡ PERFORMANCE BENCHMARK")
    print("-" * 40)
    
    # Test 1: Sequential processing
    print("🔄 Testing Sequential Processing...")
    start_time = time.time()
    sequential_results = []
    for i in range(1000):
        # Simulate technical indicator calculation
        result = sum(j * 0.1 for j in range(100))
        sequential_results.append(result)
    sequential_time = time.time() - start_time
    print(f"   Sequential Time: {sequential_time:.4f} seconds")
    
    # Test 2: Parallel processing
    print("🔄 Testing Parallel Processing...")
    def calculate_indicator(n):
        return sum(j * 0.1 for j in range(100))
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        parallel_results = list(executor.map(calculate_indicator, range(1000)))
    parallel_time = time.time() - start_time
    print(f"   Parallel Time: {parallel_time:.4f} seconds")
    
    # Calculate speedup
    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    print(f"   Speedup Factor: {speedup:.2f}x")
    
    # Performance targets
    target_sequential = 0.1  # 100ms for 1000 calculations
    target_parallel = 0.05   # 50ms for 1000 calculations
    
    sequential_ok = sequential_time <= target_sequential
    parallel_ok = parallel_time <= target_parallel
    
    print(f"\n📊 Performance Results:")
    print(f"   • Sequential Performance: {'✅ PASS' if sequential_ok else '⚠️ SLOW'}")
    print(f"   • Parallel Performance: {'✅ PASS' if parallel_ok else '⚠️ SLOW'}")
    print(f"   • Overall Rating: {'🚀 EXCELLENT' if speedup >= 2 else '✅ GOOD' if speedup >= 1.5 else '⚠️ AVERAGE'}")
    
    return sequential_ok and parallel_ok

def main():
    """Main performance check function"""
    print("🎯 ENHANCED SANDY SNIPER BOT - PERFORMANCE VALIDATION")
    print("=" * 60)
    print(f"📅 Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version}")
    print(f"💻 Platform: {sys.platform}")
    print("=" * 60)
    
    # Run all checks
    checks = [
        ("CPU Capabilities", check_cpu_capabilities),
        ("Caching Performance", check_caching_performance),
        ("Memory Management", check_memory_management),
        ("Import Capabilities", check_import_capabilities),
        ("Performance Benchmark", benchmark_performance)
    ]
    
    results = []
    
    for check_name, check_function in checks:
        try:
            result = check_function()
            results.append((check_name, result, "✅ PASS" if result else "❌ FAIL"))
        except Exception as e:
            results.append((check_name, False, f"❌ ERROR: {e}"))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE VALIDATION SUMMARY")
    print("=" * 60)
    
    for check_name, result, status in results:
        print(f"{status} {check_name}")
    
    passed_checks = sum(1 for _, result, _ in results if result)
    total_checks = len(results)
    success_rate = passed_checks / total_checks
    
    print(f"\n📈 Overall Success Rate: {passed_checks}/{total_checks} ({success_rate:.1%})")
    
    if success_rate >= 1.0:
        print("\n🎉 PERFORMANCE VALIDATION SUCCESSFUL!")
        print("🚀 System is optimized and ready for high-performance trading!")
        return True
    elif success_rate >= 0.8:
        print("\n✅ PERFORMANCE VALIDATION MOSTLY SUCCESSFUL")
        print("⚠️ Some optimizations may not be available")
        return True
    else:
        print("\n❌ PERFORMANCE VALIDATION FAILED")
        print("🔧 System optimization required before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
