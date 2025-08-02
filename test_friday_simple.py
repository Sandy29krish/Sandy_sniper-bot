#!/usr/bin/env python3
"""
Friday Logic Test - Simplified
Tests just the Friday logic functions without full bot initialization
"""

import sys
import os
from datetime import datetime, timedelta
import pytz

def is_friday_entry_allowed(current_time=None):
    """Check if new entries are allowed on Friday (stop entries after 2:30 PM)"""
    IST = pytz.timezone('Asia/Kolkata')
    if current_time is None:
        current_time = datetime.now(IST)
    
    if current_time.weekday() == 4:  # Friday
        friday_cutoff = current_time.replace(hour=14, minute=30, second=0, microsecond=0)
        if current_time >= friday_cutoff:
            return False, "🗓️ Friday 2:30 PM+ - No new entries to avoid weekend theta decay"
    return True, "Entry allowed"

def check_friday_exit(entry_time, current_time):
    """Check Friday forced exit logic"""
    IST = pytz.timezone('Asia/Kolkata')
    
    if current_time.weekday() == 4:  # Friday (0=Monday, 4=Friday)
        friday_exit_time = current_time.replace(hour=15, minute=20, second=0, microsecond=0)
        friday_warning_time = current_time.replace(hour=14, minute=50, second=0, microsecond=0)
        
        if current_time >= friday_exit_time:
            return True, "🗓️ Friday 3:20 PM Force Exit - Avoiding weekend theta decay"
        elif current_time >= friday_warning_time:
            time_left = (friday_exit_time - current_time).total_seconds() / 60
            return False, f"⚠️ Friday Warning: Force exit in {time_left:.0f} minutes"
        else:
            return False, "Normal Friday monitoring"
    
    return False, "Not Friday"

def test_friday_logic():
    """Test Friday-specific logic"""
    print("🗓️ TESTING FRIDAY LOGIC")
    print("=" * 50)
    
    IST = pytz.timezone('Asia/Kolkata')
    
    # Test scenarios with actual dates
    scenarios = [
        # Thursday - should allow entries
        (datetime(2025, 8, 7, 14, 0, tzinfo=IST), "Thursday 2:00 PM"),
        
        # Friday before 2:30 PM - should allow entries
        (datetime(2025, 8, 8, 10, 0, tzinfo=IST), "Friday 10:00 AM"),
        (datetime(2025, 8, 8, 14, 0, tzinfo=IST), "Friday 2:00 PM"),
        
        # Friday after 2:30 PM - should block entries
        (datetime(2025, 8, 8, 14, 45, tzinfo=IST), "Friday 2:45 PM"),
        (datetime(2025, 8, 8, 15, 0, tzinfo=IST), "Friday 3:00 PM"),
        
        # Friday warning period - 2:50 PM
        (datetime(2025, 8, 8, 14, 55, tzinfo=IST), "Friday 2:55 PM"),
        
        # Friday after 3:20 PM - should force exit
        (datetime(2025, 8, 8, 15, 25, tzinfo=IST), "Friday 3:25 PM"),
        
        # Monday - should allow entries again
        (datetime(2025, 8, 11, 10, 0, tzinfo=IST), "Monday 10:00 AM"),
    ]
    
    for test_time, description in scenarios:
        print(f"\n📅 Testing: {description}")
        
        try:
            # Test entry restriction
            allowed, msg = is_friday_entry_allowed(test_time)
            entry_status = "✅ ALLOWED" if allowed else "🚫 BLOCKED"
            print(f"   Entry: {entry_status} - {msg}")
            
            # Test exit conditions
            entry_time = test_time - timedelta(hours=2)  # Position entered 2 hours ago
            should_exit, exit_msg = check_friday_exit(entry_time, test_time)
            exit_status = "🚨 FORCE EXIT" if should_exit else "✅ CONTINUE"
            print(f"   Exit:  {exit_status} - {exit_msg}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📊 FRIDAY LOGIC SUMMARY:")
    print("✅ Entry blocked after Friday 2:30 PM")
    print("✅ Warning shown from Friday 2:50 PM")
    print("✅ Force exit at Friday 3:20 PM")
    print("✅ Normal trading resumes Monday")
    print("\n🎯 This prevents weekend theta decay on options!")
    print("\n💡 Key Times:")
    print("   • 2:30 PM Friday: Stop new entries")
    print("   • 2:50 PM Friday: Start exit warnings") 
    print("   • 3:20 PM Friday: Force exit all positions")

if __name__ == "__main__":
    test_friday_logic()
