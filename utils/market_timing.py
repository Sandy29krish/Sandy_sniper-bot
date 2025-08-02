#!/usr/bin/env python3
"""
Market Timing Utilities for Sandy Sniper Bot
Includes Friday exit logic and market session management
"""

from datetime import datetime, time
import pytz

IST = pytz.timezone('Asia/Kolkata')

class FridayExitManager:
    """🚨 Friday Exit Logic Manager"""
    
    def __init__(self):
        self.restriction_time = time(14, 30)  # 2:30 PM IST
        self.warning_time = time(14, 50)      # 2:50 PM IST
        self.force_exit_time = time(15, 20)   # 3:20 PM IST
        
    def should_restrict_entry(self):
        """Check if new entries should be restricted (Friday after 2:30 PM)"""
        current_time = datetime.now(IST)
        if current_time.weekday() == 4:  # Friday is 4
            return current_time.time() >= self.restriction_time
        return False
    
    def should_show_warning(self):
        """Check if warning should be shown (Friday after 2:50 PM)"""
        current_time = datetime.now(IST)
        if current_time.weekday() == 4:  # Friday is 4
            return current_time.time() >= self.warning_time
        return False
    
    def should_force_exit(self):
        """Check if all positions should be force closed (Friday after 3:20 PM)"""
        current_time = datetime.now(IST)
        if current_time.weekday() == 4:  # Friday is 4
            return current_time.time() >= self.force_exit_time
        return False
    
    def get_friday_status(self):
        """Get current Friday trading status"""
        if not self.is_friday():
            return "NORMAL", "Regular trading day"
        
        if self.should_force_exit():
            return "FORCE_EXIT", "🚨 FRIDAY 3:20 PM - FORCE EXIT ALL POSITIONS!"
        elif self.should_show_warning():
            return "WARNING", "⚠️ FRIDAY 2:50 PM - Prepare for 3:20 PM exit!"
        elif self.should_restrict_entry():
            return "RESTRICTED", "🚫 FRIDAY 2:30 PM - No new entries!"
        else:
            return "NORMAL", "Friday morning - Normal trading"
    
    def is_friday(self):
        """Check if today is Friday"""
        return datetime.now(IST).weekday() == 4
    
    def is_friday_afternoon(self):
        """Check if it's Friday afternoon (after restriction time)"""
        current_time = datetime.now(IST)
        if current_time.weekday() == 4:  # Friday is 4
            return current_time.time() >= self.restriction_time
        return False
    
    def can_enter_trade(self, check_time, day_of_week):
        """Check if new trade entry is allowed"""
        if day_of_week == 4:  # Friday
            return check_time < self.restriction_time
        return True
    
    def should_force_exit_position(self, check_time, day_of_week):
        """Check if position should be force closed"""
        if day_of_week == 4:  # Friday
            return check_time >= self.force_exit_time
        return False
