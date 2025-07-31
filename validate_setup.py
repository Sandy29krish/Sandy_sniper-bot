#!/usr/bin/env python3
"""
Setup Validation Script for Sniper Swing Bot
Validates all dependencies, configurations, and connections
"""

import os
import sys
import importlib
from typing import Dict, List, Tuple
import logging

# Setup logging for validation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is compatible"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
        else:
            return False, f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)"
    except Exception as e:
        return False, f"❌ Error checking Python version: {e}"

def check_required_packages() -> Tuple[bool, List[str]]:
    """Check if all required packages are installed"""
    required_packages = [
        'requests', 'kiteconnect', 'pandas', 'numpy', 'matplotlib',
        'python-dotenv', 'schedule', 'psutil', 'selenium', 'pytz',
        'yaml', 'telegram', 'bs4', 'lxml', 'sklearn', 'yfinance', 'pyotp'
    ]
    
    results = []
    all_ok = True
    
    for package in required_packages:
        try:
            # Handle special package names
            if package == 'yaml':
                import_name = 'yaml'
            elif package == 'telegram':
                import_name = 'telegram'
            elif package == 'bs4':
                import_name = 'bs4'
            elif package == 'sklearn':
                import_name = 'sklearn'
            else:
                import_name = package.replace('-', '_')
            
            importlib.import_module(import_name)
            results.append(f"✅ {package}")
        except ImportError:
            results.append(f"❌ {package} (missing)")
            all_ok = False
        except Exception as e:
            results.append(f"⚠️ {package} (error: {e})")
            all_ok = False
    
    return all_ok, results

def check_environment_variables() -> Tuple[bool, List[str]]:
    """Check if required environment variables are set"""
    required_vars = [
        'KITE_API_KEY', 'KITE_API_SECRET', 'KITE_USER_ID',
        'TELEGRAM_BOT_TOKEN', 'TELEGRAM_ID', 'CAPITAL'
    ]
    
    results = []
    all_ok = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'TOKEN' in var or 'SECRET' in var or 'PASSWORD' in var:
                display_value = f"{value[:8]}{'*' * (len(value) - 8)}"
            else:
                display_value = value
            results.append(f"✅ {var}={display_value}")
        else:
            results.append(f"❌ {var} (not set)")
            all_ok = False
    
    return all_ok, results

def check_file_structure() -> Tuple[bool, List[str]]:
    """Check if all required files exist"""
    required_files = [
        'main.py', 'sniper_swing.py', 'runner.py', 'config.yaml',
        'requirements.txt', 'market_timing.py', 'telegram_commands.py',
        'system_health_monitor.py'
    ]
    
    required_dirs = [
        'utils'
    ]
    
    results = []
    all_ok = True
    
    # Check files
    for file_path in required_files:
        if os.path.exists(file_path):
            results.append(f"✅ {file_path}")
        else:
            results.append(f"❌ {file_path} (missing)")
            all_ok = False
    
    # Check directories
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            results.append(f"✅ {dir_path}/ (directory)")
        else:
            results.append(f"❌ {dir_path}/ (missing directory)")
            all_ok = False
    
    return all_ok, results

def check_utils_modules() -> Tuple[bool, List[str]]:
    """Check if all utils modules exist"""
    utils_modules = [
        'swing_config', 'kite_api', 'notifications', 'indicators',
        'nse_data', 'lot_manager', 'trade_logger', 'ai_assistant',
        'zerodha_auth', 'signal_strength_analyzer', 'advanced_exit_manager'
    ]
    
    results = []
    all_ok = True
    
    for module in utils_modules:
        module_path = f"utils/{module}.py"
        if os.path.exists(module_path):
            results.append(f"✅ utils/{module}.py")
        else:
            results.append(f"❌ utils/{module}.py (missing)")
            all_ok = False
    
    return all_ok, results

def test_imports() -> Tuple[bool, List[str]]:
    """Test importing key modules"""
    test_imports = [
        ('sniper_swing', 'SniperSwingBot'),
        ('market_timing', 'is_market_open'),
        ('telegram_commands', 'start_telegram_command_server'),
        ('system_health_monitor', 'start_system_health_monitor'),
        ('utils.swing_config', 'SWING_CONFIG'),
        ('utils.notifications', 'Notifier')
    ]
    
    results = []
    all_ok = True
    
    for module_name, class_or_func in test_imports:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_or_func):
                results.append(f"✅ {module_name}.{class_or_func}")
            else:
                results.append(f"⚠️ {module_name}.{class_or_func} (not found)")
                all_ok = False
        except ImportError as e:
            results.append(f"❌ {module_name} (import error: {e})")
            all_ok = False
        except Exception as e:
            results.append(f"⚠️ {module_name} (error: {e})")
            all_ok = False
    
    return all_ok, results

def check_configuration() -> Tuple[bool, List[str]]:
    """Check configuration files"""
    results = []
    all_ok = True
    
    # Check .env file
    if os.path.exists('.env'):
        results.append("✅ .env file exists")
    else:
        results.append("⚠️ .env file missing (using environment variables)")
    
    # Check config.yaml
    if os.path.exists('config.yaml'):
        try:
            import yaml
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            results.append("✅ config.yaml (valid YAML)")
        except Exception as e:
            results.append(f"❌ config.yaml (invalid: {e})")
            all_ok = False
    else:
        results.append("❌ config.yaml (missing)")
        all_ok = False
    
    return all_ok, results

def test_connections() -> Tuple[bool, List[str]]:
    """Test external connections"""
    results = []
    all_ok = True
    
    # Test Telegram connection
    try:
        from telegram_commands import test_telegram_connection
        success, message = test_telegram_connection()
        if success:
            results.append(f"✅ Telegram: {message}")
        else:
            results.append(f"❌ Telegram: {message}")
            all_ok = False
    except Exception as e:
        results.append(f"⚠️ Telegram test failed: {e}")
        all_ok = False
    
    # Test market timing
    try:
        from market_timing import get_market_status
        status = get_market_status()
        results.append(f"✅ Market Status: {status['status']}")
    except Exception as e:
        results.append(f"⚠️ Market timing test failed: {e}")
        all_ok = False
    
    return all_ok, results

def main():
    """Run all validation checks"""
    print("🔍 Sniper Swing Bot - Setup Validation")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("Environment Variables", check_environment_variables),
        ("File Structure", check_file_structure),
        ("Utils Modules", check_utils_modules),
        ("Module Imports", test_imports),
        ("Configuration", check_configuration),
        ("External Connections", test_connections)
    ]
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        print("-" * 30)
        
        try:
            if check_func.__name__ in ['check_python_version']:
                success, result = check_func()
                print(result)
                if not success:
                    all_checks_passed = False
            else:
                success, results = check_func()
                for result in results:
                    print(result)
                if not success:
                    all_checks_passed = False
        except Exception as e:
            print(f"❌ Error running {check_name}: {e}")
            all_checks_passed = False
    
    # Final summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your bot setup is ready to run!")
        print("\n🚀 To start the bot:")
        print("   python main.py")
        return 0
    else:
        print("⚠️ SOME CHECKS FAILED!")
        print("❌ Please fix the issues above before running the bot")
        print("\n🔧 Common fixes:")
        print("   1. Install missing packages: pip install -r requirements.txt")
        print("   2. Set up environment variables in .env file")
        print("   3. Check file permissions and paths")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
