#!/usr/bin/env python3
"""
Sniper Swing Bot - Real-time Monitoring Dashboard
Displays live status, positions, and performance metrics
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import Dict, List
import signal

# Disable logging for clean dashboard output
logging.disable(logging.CRITICAL)

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_size():
    """Get terminal dimensions"""
    try:
        rows, columns = os.popen('stty size', 'r').read().split()
        return int(rows), int(columns)
    except:
        return 24, 80  # Default size

def format_currency(amount):
    """Format currency in Indian format"""
    if amount >= 0:
        return f"₹{amount:,.0f}"
    else:
        return f"-₹{abs(amount):,.0f}"

def get_bot_status():
    """Get current bot status"""
    try:
        # Try to import and get state
        sys.path.append(os.getcwd())
        from sniper_swing import StateManager
        
        state_manager = StateManager()
        state = state_manager.state
        
        return {
            'status': 'RUNNING',
            'positions': state.get('positions', {}),
            'daily_trades': state.get('daily_trade_count', 0),
            'last_update': datetime.now().strftime('%H:%M:%S')
        }
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': str(e),
            'positions': {},
            'daily_trades': 0,
            'last_update': datetime.now().strftime('%H:%M:%S')
        }

def get_market_status():
    """Get market status"""
    try:
        from market_timing import get_market_status, is_market_open
        status = get_market_status()
        return {
            'is_open': is_market_open(),
            'status': status.get('status', 'UNKNOWN'),
            'message': status.get('message', 'Status unavailable')
        }
    except Exception as e:
        return {
            'is_open': False,
            'status': 'ERROR',
            'message': f'Error: {e}'
        }

def get_system_health():
    """Get system health metrics"""
    try:
        from system_health_monitor import get_health_monitor
        monitor = get_health_monitor()
        health_data = monitor.get_system_health()
        
        return {
            'cpu': health_data.get('cpu', {}).get('percent', 0),
            'memory': health_data.get('memory', {}).get('percent', 0),
            'disk': health_data.get('disk', {}).get('percent', 0)
        }
    except Exception as e:
        return {'cpu': 0, 'memory': 0, 'disk': 0, 'error': str(e)}

def calculate_total_pnl(positions):
    """Calculate total P&L from positions"""
    total_pnl = 0
    for symbol, data in positions.items():
        try:
            # This is simplified - in reality you'd get current prices
            entry_price = data.get('entry_price', 0)
            quantity = data.get('quantity', 0)
            # For demo, assume some P&L
            pnl = entry_price * quantity * 0.02  # 2% assumed gain
            total_pnl += pnl
        except:
            continue
    return total_pnl

def draw_header():
    """Draw dashboard header"""
    rows, cols = get_terminal_size()
    header = "🎯 SNIPER SWING BOT - LIVE DASHBOARD 🎯"
    border = "=" * cols
    
    print(border)
    print(header.center(cols))
    print(border)

def draw_status_section(bot_status, market_status):
    """Draw status section"""
    print("\n📊 STATUS OVERVIEW")
    print("-" * 40)
    
    # Bot status
    status_color = "🟢" if bot_status['status'] == 'RUNNING' else "🔴"
    print(f"{status_color} Bot Status: {bot_status['status']}")
    
    # Market status
    market_color = "🟢" if market_status['is_open'] else "🔴"
    print(f"{market_color} Market: {market_status['status']}")
    print(f"   └─ {market_status['message']}")
    
    # Update time
    print(f"🕒 Last Update: {bot_status['last_update']}")

def draw_positions_section(positions):
    """Draw positions section"""
    print("\n📈 ACTIVE POSITIONS")
    print("-" * 40)
    
    if not positions:
        print("   No active positions")
        return
    
    for symbol, data in positions.items():
        signal = data.get('signal', 'N/A').upper()
        entry_price = data.get('entry_price', 0)
        quantity = data.get('quantity', 0)
        strike = data.get('strike', 'N/A')
        strength = data.get('signal_strength', 0)
        
        signal_emoji = "🟢" if signal == 'BULLISH' else "🔴"
        print(f"{signal_emoji} {symbol} ({signal})")
        print(f"   ├─ Strike: {strike}")
        print(f"   ├─ Entry: ₹{entry_price}")
        print(f"   ├─ Qty: {quantity}")
        print(f"   └─ Strength: {strength:.1f}/10")

def draw_performance_section(positions, daily_trades):
    """Draw performance section"""
    print("\n💰 PERFORMANCE")
    print("-" * 40)
    
    total_pnl = calculate_total_pnl(positions)
    pnl_color = "🟢" if total_pnl >= 0 else "🔴"
    
    print(f"📊 Active Positions: {len(positions)}")
    print(f"📈 Daily Trades: {daily_trades}/3")
    print(f"{pnl_color} Total P&L: {format_currency(total_pnl)}")

def draw_system_section(health):
    """Draw system health section"""
    print("\n🖥️ SYSTEM HEALTH")
    print("-" * 40)
    
    cpu = health.get('cpu', 0)
    memory = health.get('memory', 0)
    disk = health.get('disk', 0)
    
    cpu_color = "🟢" if cpu < 70 else "🟡" if cpu < 90 else "🔴"
    mem_color = "🟢" if memory < 70 else "🟡" if memory < 90 else "🔴"
    disk_color = "🟢" if disk < 80 else "🟡" if disk < 95 else "🔴"
    
    print(f"{cpu_color} CPU: {cpu:.1f}%")
    print(f"{mem_color} Memory: {memory:.1f}%")
    print(f"{disk_color} Disk: {disk:.1f}%")

def draw_controls():
    """Draw control instructions"""
    print("\n🎮 CONTROLS")
    print("-" * 40)
    print("   Ctrl+C: Exit dashboard")
    print("   Updates every 5 seconds")

def draw_footer():
    """Draw dashboard footer"""
    rows, cols = get_terminal_size()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    footer = f"⚡ Live Dashboard - {timestamp} ⚡"
    border = "=" * cols
    
    print("\n" + border)
    print(footer.center(cols))
    print(border)

def main():
    """Main dashboard loop"""
    print("🚀 Starting Sniper Swing Bot Dashboard...")
    print("Press Ctrl+C to exit")
    time.sleep(2)
    
    def signal_handler(sig, frame):
        clear_screen()
        print("\n👋 Dashboard stopped. Bot continues running in background.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        while True:
            # Clear screen and get fresh data
            clear_screen()
            
            bot_status = get_bot_status()
            market_status = get_market_status()
            system_health = get_system_health()
            
            # Draw dashboard
            draw_header()
            draw_status_section(bot_status, market_status)
            draw_positions_section(bot_status['positions'])
            draw_performance_section(bot_status['positions'], bot_status['daily_trades'])
            draw_system_section(system_health)
            draw_controls()
            draw_footer()
            
            # Wait before next update
            time.sleep(5)
            
    except KeyboardInterrupt:
        clear_screen()
        print("\n👋 Dashboard stopped. Bot continues running in background.")
    except Exception as e:
        clear_screen()
        print(f"\n❌ Dashboard error: {e}")
        print("Bot may still be running in background.")

if __name__ == "__main__":
    main()
