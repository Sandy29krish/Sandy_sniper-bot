#!/usr/bin/env python3
"""
Production Deployment Runner for Enhanced Sandy Sniper Bot
CPU-Optimized Trading System with Full Feature Set

Usage:
    python production_runner.py [--validate-only]
    
Features:
- CPU-optimized parallel processing
- 5-condition signal analysis
- AI-enhanced 3/5 signal support
- CPR price action scenarios
- Real-time performance monitoring
- Comprehensive error handling
"""

import sys
import os
import time
import logging
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_production_logging():
    """Setup production-grade logging"""
    log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('production_sniper.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('ProductionRunner')

def validate_system():
    """Validate system components before deployment"""
    logger = logging.getLogger('SystemValidator')
    logger.info("🔍 Starting system validation...")
    
    validation_errors = []
    
    # Test critical imports
    try:
        import enhanced_sniper_swing
        logger.info("✅ Enhanced Sniper Swing module imported successfully")
    except Exception as e:
        error = f"❌ Failed to import enhanced_sniper_swing: {e}"
        validation_errors.append(error)
        logger.error(error)
    
    try:
        from utils.enhanced_market_timing import is_friday_315, is_within_first_15_minutes
        logger.info("✅ Enhanced market timing functions imported successfully")
    except Exception as e:
        error = f"❌ Failed to import enhanced market timing: {e}"
        validation_errors.append(error)
        logger.error(error)
    
    try:
        from utils.cpu_optimizer import OptimizedCPUManager
        logger.info("✅ CPU optimizer imported successfully")
    except Exception as e:
        error = f"❌ Failed to import CPU optimizer: {e}"
        validation_errors.append(error)
        logger.error(error)
    
    # Test file existence
    critical_files = [
        'enhanced_sniper_swing.py',
        'utils/enhanced_market_timing.py',
        'utils/cpu_optimizer.py',
        'utils/kite_api.py',
        'utils/notifications.py'
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            logger.info(f"✅ Critical file exists: {file_path}")
        else:
            error = f"❌ Critical file missing: {file_path}"
            validation_errors.append(error)
            logger.error(error)
    
    if validation_errors:
        logger.error(f"❌ System validation failed with {len(validation_errors)} errors")
        for error in validation_errors:
            logger.error(f"   {error}")
        return False
    
    logger.info("✅ System validation completed successfully")
    return True

def run_production_system():
    """Run the production trading system"""
    logger = logging.getLogger('ProductionSystem')
    
    try:
        logger.info("🚀 Starting Enhanced Sandy Sniper Bot - Production Mode")
        logger.info("📊 Features: CPU-Optimized, 5-Condition Analysis, AI-Enhanced")
        
        # Import and initialize the enhanced system
        from enhanced_sniper_swing import EnhancedSniperSwingBot
        
        # Create bot instance
        bot = EnhancedSniperSwingBot()
        logger.info("✅ Enhanced Sniper Swing Bot initialized successfully")
        
        # Log system capabilities
        logger.info("🎯 System Capabilities:")
        logger.info("   • 5-Condition Signal Analysis")
        logger.info("   • AI-Enhanced 3/5 Signal Support")
        logger.info("   • CPR Price Action Scenarios")
        logger.info("   • CPU-Optimized Parallel Processing")
        logger.info("   • Real-time Performance Monitoring")
        
        # Start the enhanced system
        logger.info("🔄 Starting main trading loop...")
        bot.run_enhanced_system()
        
    except KeyboardInterrupt:
        logger.info("🛑 System shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Critical error in production system: {e}")
        raise

def main():
    """Main entry point"""
    # Setup logging
    logger = setup_production_logging()
    
    # Check command line arguments
    validate_only = len(sys.argv) > 1 and sys.argv[1] == '--validate-only'
    
    logger.info("🎯 ENHANCED SANDY SNIPER BOT - PRODUCTION DEPLOYMENT")
    logger.info("=" * 60)
    logger.info(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🐍 Python Version: {sys.version}")
    logger.info(f"📁 Working Directory: {os.getcwd()}")
    logger.info("=" * 60)
    
    # Validate system
    if not validate_system():
        logger.error("❌ System validation failed - Deployment aborted")
        sys.exit(1)
    
    if validate_only:
        logger.info("✅ Validation complete - System ready for deployment")
        sys.exit(0)
    
    # Run production system
    try:
        run_production_system()
    except Exception as e:
        logger.error(f"❌ Production system failed: {e}")
        sys.exit(1)
    
    logger.info("✅ Production system completed successfully")

if __name__ == "__main__":
    main()
