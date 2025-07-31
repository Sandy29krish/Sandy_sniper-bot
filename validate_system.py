#!/usr/bin/env python3
"""
System validation script for Enhanced Sandy Sniper Bot
Tests all critical components and reports status
"""

import sys
import os
import traceback
from datetime import datetime

def validate_system():
    """Validate all system components"""
    print("🔍 ENHANCED SANDY SNIPER BOT - SYSTEM VALIDATION")
    print("=" * 60)
    print(f"📅 Validation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print("=" * 60)
    
    validation_results = []
    
    # Test 1: Enhanced Sniper Swing Main Module
    print("\n1️⃣ Testing Enhanced Sniper Swing Main Module...")
    try:
        import enhanced_sniper_swing
        validation_results.append("✅ Enhanced Sniper Swing: Import successful")
        print("   ✅ Main module imported successfully")
        
        # Test class instantiation
        try:
            bot = enhanced_sniper_swing.EnhancedSniperSwingBot()
            validation_results.append("✅ Enhanced Sniper Swing: Class instantiation successful")
            print("   ✅ Bot class instantiated successfully")
        except Exception as e:
            validation_results.append(f"❌ Enhanced Sniper Swing: Class instantiation failed - {e}")
            print(f"   ❌ Bot class instantiation failed: {e}")
            
    except Exception as e:
        validation_results.append(f"❌ Enhanced Sniper Swing: Import failed - {e}")
        print(f"   ❌ Import failed: {e}")
        traceback.print_exc()
    
    # Test 2: Enhanced Market Timing
    print("\n2️⃣ Testing Enhanced Market Timing...")
    try:
        from utils.enhanced_market_timing import is_friday_315, is_within_first_15_minutes
        validation_results.append("✅ Enhanced Market Timing: Import successful")
        print("   ✅ Enhanced market timing functions imported")
    except Exception as e:
        validation_results.append(f"❌ Enhanced Market Timing: Import failed - {e}")
        print(f"   ❌ Import failed: {e}")
        traceback.print_exc()
    
    # Test 3: CPU Optimizer
    print("\n3️⃣ Testing CPU Optimizer...")
    try:
        from utils.cpu_optimizer import OptimizedCPUManager
        validation_results.append("✅ CPU Optimizer: Import successful")
        print("   ✅ CPU optimizer imported successfully")
        
        # Test CPU manager instantiation
        try:
            cpu_manager = OptimizedCPUManager()
            validation_results.append("✅ CPU Optimizer: Instantiation successful")
            print("   ✅ CPU manager instantiated successfully")
        except Exception as e:
            validation_results.append(f"❌ CPU Optimizer: Instantiation failed - {e}")
            print(f"   ❌ CPU manager instantiation failed: {e}")
            
    except Exception as e:
        validation_results.append(f"❌ CPU Optimizer: Import failed - {e}")
        print(f"   ❌ Import failed: {e}")
        traceback.print_exc()
    
    # Test 4: Core Utilities
    print("\n4️⃣ Testing Core Utilities...")
    core_modules = [
        'utils.kite_api',
        'utils.notifications',
        'utils.indicators',
        'utils.swing_config'
    ]
    
    for module in core_modules:
        try:
            __import__(module)
            validation_results.append(f"✅ {module}: Import successful")
            print(f"   ✅ {module} imported successfully")
        except Exception as e:
            validation_results.append(f"❌ {module}: Import failed - {e}")
            print(f"   ❌ {module} import failed: {e}")
    
    # Test 5: File Structure
    print("\n5️⃣ Testing File Structure...")
    critical_files = [
        'enhanced_sniper_swing.py',
        'utils/enhanced_market_timing.py',
        'utils/cpu_optimizer.py',
        'utils/kite_api.py',
        'utils/notifications.py',
        'utils/indicators.py'
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            validation_results.append(f"✅ File exists: {file_path}")
            print(f"   ✅ {file_path} exists")
        else:
            validation_results.append(f"❌ File missing: {file_path}")
            print(f"   ❌ {file_path} missing")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    success_count = len([r for r in validation_results if r.startswith("✅")])
    total_count = len(validation_results)
    
    for result in validation_results:
        print(result)
    
    print(f"\n📈 Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("\n🎉 SYSTEM VALIDATION SUCCESSFUL!")
        print("🚀 Enhanced Sandy Sniper Bot is ready for deployment!")
        return True
    else:
        print(f"\n⚠️ VALIDATION INCOMPLETE: {total_count - success_count} issues found")
        print("🔧 Please resolve issues before deployment")
        return False

if __name__ == "__main__":
    success = validate_system()
    sys.exit(0 if success else 1)
