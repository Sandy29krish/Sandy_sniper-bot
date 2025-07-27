#!/usr/bin/env python3
"""
Unit tests for entry signal logic in the trading bot.
Tests both PatternSignalGenerator and swing strategy entry conditions.
"""

import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pattern_signal_generator import PatternSignalGenerator
from sniper_swing import SniperSwingBot

class TestPatternSignalGenerator(unittest.TestCase):
    """Test cases for PatternSignalGenerator class"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample OHLCV data with indicators
        self.sample_data = pd.DataFrame({
            'open': [100, 102, 101, 105, 103, 108, 106, 110, 108, 112],
            'high': [103, 105, 104, 107, 106, 111, 109, 113, 111, 115],
            'low': [99, 101, 100, 104, 102, 107, 105, 109, 107, 111],
            'close': [102, 104, 103, 106, 105, 110, 108, 112, 110, 114],
            'volume': [1000, 1200, 800, 1500, 900, 1800, 1100, 2000, 1300, 2200],
            # Moving averages (bullish hierarchy)
            'ma3': [101, 103, 102, 105, 104, 109, 107, 111, 109, 113],
            'ma9': [100, 102, 101, 104, 103, 108, 106, 110, 108, 112],
            'ma20': [99, 101, 100, 103, 102, 107, 105, 109, 107, 111],
            'ma50': [98, 100, 99, 102, 101, 106, 104, 108, 106, 110],
            'ma200': [97, 99, 98, 101, 100, 105, 103, 107, 105, 109],
            # RSI indicators
            'rsi': [55, 60, 58, 65, 62, 70, 68, 75, 72, 78],
            'rsi_ma9': [50, 55, 53, 60, 57, 65, 63, 70, 67, 73],
            'rsi_ma14': [48, 53, 51, 58, 55, 63, 61, 68, 65, 71],
            'rsi_ma26': [45, 50, 48, 55, 52, 60, 58, 65, 62, 68],
            # Volume and slope indicators
            'pvi': [1000, 1020, 1015, 1035, 1030, 1055, 1050, 1075, 1070, 1095],
            'lr_slope': [0.5, 0.8, 0.6, 1.2, 0.9, 1.5, 1.3, 1.8, 1.6, 2.1],
            # CPR levels (optional)
            'cpr_top': [104, 106, 105, 108, 107, 112, 110, 114, 112, 116],
            'cpr_bottom': [98, 100, 99, 102, 101, 106, 104, 108, 106, 110]
        })
        
        self.generator = PatternSignalGenerator(self.sample_data)
    
    def test_bullish_engulfing_detection(self):
        """Test bullish engulfing pattern detection"""
        # Create specific data for bullish engulfing
        test_data = pd.DataFrame({
            'open': [100, 98],
            'high': [101, 103],
            'low': [99, 97],
            'close': [99, 102]  # Previous red, current green and engulfs
        })
        generator = PatternSignalGenerator(test_data)
        
        # Should detect bullish engulfing at index 1
        self.assertTrue(generator.detect_bullish_engulfing(1))
        self.assertFalse(generator.detect_bullish_engulfing(0))
    
    def test_bearish_engulfing_detection(self):
        """Test bearish engulfing pattern detection"""
        # Create specific data for bearish engulfing
        test_data = pd.DataFrame({
            'open': [100, 103],
            'high': [102, 104],
            'low': [99, 98],
            'close': [102, 99]  # Previous green, current red and engulfs
        })
        generator = PatternSignalGenerator(test_data)
        
        # Should detect bearish engulfing at index 1
        self.assertTrue(generator.detect_bearish_engulfing(1))
        self.assertFalse(generator.detect_bearish_engulfing(0))
    
    def test_bullish_entry_conditions(self):
        """Test bullish entry signal conditions"""
        # Test with the last row (index 9) which should be bullish
        signal = self.generator.check_entry_conditions(9)
        self.assertEqual(signal, "bullish")
    
    def test_bearish_entry_conditions(self):
        """Test bearish entry signal conditions"""
        # Create bearish data
        bearish_data = self.sample_data.copy()
        # Reverse the MA hierarchy for bearish signal
        bearish_data.loc[9, 'close'] = 95
        bearish_data.loc[9, 'ma9'] = 96
        bearish_data.loc[9, 'ma20'] = 97
        bearish_data.loc[9, 'ma50'] = 98
        bearish_data.loc[9, 'ma200'] = 99
        # Reverse RSI hierarchy
        bearish_data.loc[9, 'rsi'] = 40
        bearish_data.loc[9, 'rsi_ma26'] = 45
        bearish_data.loc[9, 'rsi_ma14'] = 50
        bearish_data.loc[9, 'rsi_ma9'] = 55
        # Negative indicators
        bearish_data.loc[9, 'pvi'] = 900  # Less than previous
        bearish_data.loc[9, 'lr_slope'] = -1.5
        
        generator = PatternSignalGenerator(bearish_data)
        signal = generator.check_entry_conditions(9)
        self.assertEqual(signal, "bearish")
    
    def test_no_signal_conditions(self):
        """Test when no clear signal should be generated"""
        # Create mixed/unclear data
        mixed_data = self.sample_data.copy()
        # Break MA hierarchy
        mixed_data.loc[9, 'ma9'] = 120  # Above close, breaks hierarchy
        
        generator = PatternSignalGenerator(mixed_data)
        signal = generator.check_entry_conditions(9)
        self.assertIsNone(signal)
    
    def test_cpr_confirmation(self):
        """Test CPR confirmation logic"""
        # Test bullish signal below CPR bottom (should be rejected)
        cpr_test_data = self.sample_data.copy()
        cpr_test_data.loc[9, 'close'] = 105  # Below CPR bottom
        cpr_test_data.loc[9, 'cpr_bottom'] = 110
        
        generator = PatternSignalGenerator(cpr_test_data)
        signal = generator.check_entry_conditions(9)
        self.assertIsNone(signal)  # Should be rejected due to CPR
    
    def test_exit_conditions(self):
        """Test exit condition detection"""
        # Test reversal candle exit
        exit_data = pd.DataFrame({
            'open': [100, 102, 98],
            'high': [103, 105, 103],
            'low': [99, 101, 97],
            'close': [102, 104, 99],  # Bearish engulfing at index 2
            'rsi': [60, 65, 55],
            'rsi_ma26': [55, 60, 60],  # RSI crosses below MA26
            'lr_slope': [1.5, 1.2, -0.5]  # Slope reverses
        })
        generator = PatternSignalGenerator(exit_data)
        
        # Should detect exit at index 2
        self.assertTrue(generator.check_exit_conditions(2))
    
    def test_signal_generation_flow(self):
        """Test complete signal generation flow"""
        signals = self.generator.generate_signals()
        
        # Should have signals for each data point
        self.assertEqual(len(signals), len(self.sample_data))
        
        # Check signal structure
        for signal in signals:
            self.assertIn('index', signal)
            self.assertIn('signal', signal)
            self.assertIn(signal['signal'], [
                'enter_bullish', 'enter_bearish', 'exit_bullish', 
                'exit_bearish', 'hold_bullish', 'hold_bearish', 'no_action'
            ])


class TestSniperSwingBotEntryLogic(unittest.TestCase):
    """Test cases for SniperSwingBot entry logic"""
    
    def setUp(self):
        """Set up test bot instance"""
        self.config = {
            "telegram_token": "test_token",
            "telegram_id": "test_id"
        }
        self.capital = 100000
        
        # Mock dependencies
        with patch('sniper_swing.Notifier'), \
             patch('sniper_swing.StateManager'):
            self.bot = SniperSwingBot(self.config, self.capital)
    
    def test_validate_entry_conditions_bullish(self):
        """Test bullish entry condition validation"""
        indicators = {
            "rsi": 70,
            "rsi_ma26": 65,
            "ma_hierarchy": True,
            "pvi_positive": True,
            "lr_slope_positive": True
        }
        
        result = self.bot._validate_entry_conditions(indicators)
        self.assertTrue(result)
    
    def test_validate_entry_conditions_bearish_rejected(self):
        """Test that bearish-like conditions are rejected"""
        indicators = {
            "rsi": 60,
            "rsi_ma26": 65,  # RSI below MA26
            "ma_hierarchy": True,
            "pvi_positive": True,
            "lr_slope_positive": True
        }
        
        result = self.bot._validate_entry_conditions(indicators)
        self.assertFalse(result)
    
    def test_validate_entry_conditions_missing_hierarchy(self):
        """Test rejection when MA hierarchy is broken"""
        indicators = {
            "rsi": 70,
            "rsi_ma26": 65,
            "ma_hierarchy": False,  # Broken hierarchy
            "pvi_positive": True,
            "lr_slope_positive": True
        }
        
        result = self.bot._validate_entry_conditions(indicators)
        self.assertFalse(result)
    
    def test_calculate_lot_size(self):
        """Test lot size calculation logic"""
        # Test normal case
        premium = 50
        lot_size = 75
        expected_lots = int((self.capital / 3) / (premium * lot_size)) * lot_size
        
        result = self.bot.calculate_lot_size(premium, lot_size)
        self.assertEqual(result, expected_lots)
    
    def test_calculate_lot_size_zero_premium(self):
        """Test lot size calculation with zero premium"""
        result = self.bot.calculate_lot_size(0, 75)
        self.assertEqual(result, 0)
    
    def test_calculate_lot_size_negative_premium(self):
        """Test lot size calculation with negative premium"""
        result = self.bot.calculate_lot_size(-10, 75)
        self.assertEqual(result, 0)
    
    @patch('sniper_swing.get_indicators_15m_30m')
    def test_evaluate_symbol_entry_no_signal(self, mock_indicators):
        """Test symbol evaluation when no signal is present"""
        mock_indicators.return_value = (None, {})
        
        # Should return early without processing
        result = self.bot._evaluate_symbol_entry("NIFTY")
        self.assertIsNone(result)
    
    @patch('sniper_swing.get_indicators_15m_30m')
    @patch('sniper_swing.get_next_expiry_date')
    @patch('sniper_swing.get_swing_strike')
    def test_evaluate_symbol_entry_invalid_conditions(self, mock_strike, mock_expiry, mock_indicators):
        """Test symbol evaluation with invalid entry conditions"""
        mock_indicators.return_value = ("bullish", {
            "rsi": 60,
            "rsi_ma26": 65,  # Invalid: RSI below MA26
            "ma_hierarchy": True,
            "pvi_positive": True,
            "lr_slope_positive": True
        })
        
        # Should return early due to invalid conditions
        result = self.bot._evaluate_symbol_entry("NIFTY")
        self.assertIsNone(result)
        
        # Should not call further functions
        mock_expiry.assert_not_called()
        mock_strike.assert_not_called()
    
    def test_friday_315_detection(self):
        """Test Friday 3:15 PM detection"""
        # Mock datetime to Friday 3:20 PM
        with patch('sniper_swing.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.weekday.return_value = 4  # Friday
            mock_now.time.return_value = Mock()
            mock_now.time.return_value.__ge__ = lambda x, y: True  # >= 15:15
            mock_datetime.now.return_value = mock_now
            
            result = self.bot.is_friday_315()
            self.assertTrue(result)
    
    def test_not_friday_315_detection(self):
        """Test non-Friday or before 3:15 PM detection"""
        # Mock datetime to Thursday 3:20 PM
        with patch('sniper_swing.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.weekday.return_value = 3  # Thursday
            mock_now.time.return_value = Mock()
            mock_now.time.return_value.__ge__ = lambda x, y: True
            mock_datetime.now.return_value = mock_now
            
            result = self.bot.is_friday_315()
            self.assertFalse(result)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete signal flow"""
    
    def test_complete_bullish_signal_flow(self):
        """Test complete flow from data to bullish signal"""
        # Create realistic bullish market data
        data = pd.DataFrame({
            'open': [17800, 17850, 17900],
            'high': [17850, 17900, 17950],
            'low': [17750, 17800, 17850],
            'close': [17840, 17890, 17940],
            'volume': [1000000, 1200000, 1100000],
            'ma3': [17835, 17885, 17935],
            'ma9': [17830, 17880, 17930],
            'ma20': [17820, 17870, 17920],
            'ma50': [17800, 17850, 17900],
            'ma200': [17750, 17800, 17850],
            'rsi': [65, 68, 72],
            'rsi_ma9': [60, 63, 67],
            'rsi_ma14': [58, 61, 65],
            'rsi_ma26': [55, 58, 62],
            'pvi': [1000, 1020, 1035],
            'lr_slope': [1.2, 1.5, 1.8]
        })
        
        generator = PatternSignalGenerator(data)
        
        # Check last candle for bullish signal
        signal = generator.check_entry_conditions(2)
        self.assertEqual(signal, "bullish")
    
    def test_complete_bearish_signal_flow(self):
        """Test complete flow from data to bearish signal"""
        # Create realistic bearish market data
        data = pd.DataFrame({
            'open': [17900, 17850, 17800],
            'high': [17920, 17870, 17820],
            'low': [17850, 17800, 17750],
            'close': [17860, 17810, 17760],
            'volume': [1000000, 1200000, 1100000],
            'ma3': [17865, 17815, 17765],
            'ma9': [17870, 17820, 17770],
            'ma20': [17880, 17830, 17780],
            'ma50': [17900, 17850, 17800],
            'ma200': [17950, 17900, 17850],
            'rsi': [35, 32, 28],
            'rsi_ma9': [40, 37, 33],
            'rsi_ma14': [42, 39, 35],
            'rsi_ma26': [45, 42, 38],
            'pvi': [1000, 995, 985],  # Decreasing
            'lr_slope': [-1.2, -1.5, -1.8]  # Negative slope
        })
        
        generator = PatternSignalGenerator(data)
        
        # Check last candle for bearish signal
        signal = generator.check_entry_conditions(2)
        self.assertEqual(signal, "bearish")


def run_tests():
    """Run all tests with detailed output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPatternSignalGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestSniperSwingBotEntryLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationScenarios))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TESTS RUN: {result.testsRun}")
    print(f"FAILURES: {len(result.failures)}")
    print(f"ERRORS: {len(result.errors)}")
    print(f"SUCCESS RATE: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)