import pandas as pd
import numpy as np
from datetime import datetime

class FVGDetector:
    """
    Fair Value Gap (FVG) Detection System
    
    Detects price imbalances where gaps exist between candle wicks
    that represent unfilled institutional orders and potential reversal zones
    """
    
    def __init__(self):
        self.min_gap_percentage = 0.1  # Minimum gap size as percentage of price
        self.max_lookback = 50  # Maximum candles to look back for FVG validation
        
    def detect_fvgs(self, data):
        """
        Main FVG detection function
        
        Args:
            data (pd.DataFrame): OHLCV data
            
        Returns:
            dict: FVG analysis results
        """
        try:
            if len(data) < 3:
                return self._get_empty_result()
                
            bullish_fvgs = self._detect_bullish_fvgs(data)
            bearish_fvgs = self._detect_bearish_fvgs(data)
            
            # Analyze current price relative to FVGs
            current_price = data['Close'].iloc[-1]
            fvg_analysis = self._analyze_price_vs_fvgs(current_price, bullish_fvgs, bearish_fvgs)
            
            # Check for recent FVG formations
            recent_fvgs = self._get_recent_fvgs(bullish_fvgs, bearish_fvgs, lookback=5)
            
            return {
                'bullish_fvgs': bullish_fvgs,
                'bearish_fvgs': bearish_fvgs,
                'total_fvgs': len(bullish_fvgs) + len(bearish_fvgs),
                'current_analysis': fvg_analysis,
                'recent_fvgs': recent_fvgs,
                'fvg_signals': self._generate_fvg_signals(fvg_analysis, recent_fvgs),
                'nearest_fvg': self._find_nearest_fvg(current_price, bullish_fvgs, bearish_fvgs)
            }
            
        except Exception as e:
            return {'error': str(e), 'total_fvgs': 0}
    
    def _detect_bullish_fvgs(self, data):
        """Detect bullish FVGs - 3 candle pattern where middle candle creates gap"""
        fvgs = []
        
        for i in range(2, len(data)):
            # 3-candle FVG pattern: candle[i-2], candle[i-1], candle[i]
            # For bullish FVG: Low[i] > High[i-2] (gap between candle i and i-2)
            candle_1_high = data['High'].iloc[i-2]  # First candle high
            candle_2_low = data['Low'].iloc[i-1]    # Middle candle low
            candle_2_high = data['High'].iloc[i-1]  # Middle candle high
            candle_3_low = data['Low'].iloc[i]      # Third candle low
            
            # Bullish FVG: Gap where third candle's low is above first candle's high
            if candle_3_low > candle_1_high:
                gap_size = candle_3_low - candle_1_high
                gap_percentage = (gap_size / candle_1_high) * 100
                
                # More sensitive gap detection for crypto markets
                if gap_percentage >= 0.05:  # Lower threshold for better detection
                    fvg = {
                        'type': 'bullish',
                        'index': i-1,  # Middle candle index
                        'timestamp': data.index[i-1],
                        'top': candle_3_low,
                        'bottom': candle_1_high,
                        'gap_size': gap_size,
                        'gap_percentage': gap_percentage,
                        'filled': False,
                        'fill_percentage': 0,
                        'candle_pattern': f"{i-2}-{i-1}-{i}"
                    }
                    
                    # Check if FVG has been filled by subsequent price action
                    self._check_fvg_fill_status(fvg, data, i)
                    fvgs.append(fvg)
        
        return fvgs
    
    def _detect_bearish_fvgs(self, data):
        """Detect bearish FVGs - 3 candle pattern where middle candle creates gap"""
        fvgs = []
        
        for i in range(2, len(data)):
            # 3-candle FVG pattern: candle[i-2], candle[i-1], candle[i]
            # For bearish FVG: High[i] < Low[i-2] (gap between candle i and i-2)
            candle_1_low = data['Low'].iloc[i-2]    # First candle low
            candle_2_low = data['Low'].iloc[i-1]    # Middle candle low
            candle_2_high = data['High'].iloc[i-1]  # Middle candle high
            candle_3_high = data['High'].iloc[i]    # Third candle high
            
            # Bearish FVG: Gap where third candle's high is below first candle's low
            if candle_3_high < candle_1_low:
                gap_size = candle_1_low - candle_3_high
                gap_percentage = (gap_size / candle_3_high) * 100
                
                # More sensitive gap detection for crypto markets
                if gap_percentage >= 0.05:  # Lower threshold for better detection
                    fvg = {
                        'type': 'bearish',
                        'index': i-1,  # Middle candle index
                        'timestamp': data.index[i-1],
                        'top': candle_1_low,
                        'bottom': candle_3_high,
                        'gap_size': gap_size,
                        'gap_percentage': gap_percentage,
                        'filled': False,
                        'fill_percentage': 0,
                        'candle_pattern': f"{i-2}-{i-1}-{i}"
                    }
                    
                    # Check if FVG has been filled by subsequent price action
                    self._check_fvg_fill_status(fvg, data, i)
                    fvgs.append(fvg)
        
        return fvgs
    
    def _check_fvg_fill_status(self, fvg, data, start_index):
        """Check if an FVG has been filled by subsequent price action"""
        gap_range = fvg['top'] - fvg['bottom']
        
        for i in range(start_index, len(data)):
            candle_low = data['Low'].iloc[i]
            candle_high = data['High'].iloc[i]
            
            # Calculate how much of the FVG has been filled
            if fvg['type'] == 'bullish':
                # For bullish FVG, check if price has moved down into the gap
                if candle_low <= fvg['top']:
                    filled_amount = min(fvg['top'] - candle_low, gap_range)
                    fvg['fill_percentage'] = (filled_amount / gap_range) * 100
                    
                    if candle_low <= fvg['bottom']:
                        fvg['filled'] = True
                        fvg['fill_percentage'] = 100
                        break
                        
            else:  # bearish FVG
                # For bearish FVG, check if price has moved up into the gap
                if candle_high >= fvg['bottom']:
                    filled_amount = min(candle_high - fvg['bottom'], gap_range)
                    fvg['fill_percentage'] = (filled_amount / gap_range) * 100
                    
                    if candle_high >= fvg['top']:
                        fvg['filled'] = True
                        fvg['fill_percentage'] = 100
                        break
    
    def _analyze_price_vs_fvgs(self, current_price, bullish_fvgs, bearish_fvgs):
        """Analyze current price position relative to FVGs"""
        analysis = {
            'above_bullish_fvgs': 0,
            'below_bearish_fvgs': 0,
            'inside_fvg': None,
            'nearest_support_fvg': None,
            'nearest_resistance_fvg': None
        }
        
        # Check position relative to bullish FVGs (potential support)
        for fvg in bullish_fvgs:
            if not fvg['filled'] and current_price > fvg['top']:
                analysis['above_bullish_fvgs'] += 1
            elif not fvg['filled'] and fvg['bottom'] <= current_price <= fvg['top']:
                analysis['inside_fvg'] = fvg
        
        # Check position relative to bearish FVGs (potential resistance)
        for fvg in bearish_fvgs:
            if not fvg['filled'] and current_price < fvg['bottom']:
                analysis['below_bearish_fvgs'] += 1
            elif not fvg['filled'] and fvg['bottom'] <= current_price <= fvg['top']:
                analysis['inside_fvg'] = fvg
        
        # Find nearest unfilled FVGs
        unfilled_bullish = [fvg for fvg in bullish_fvgs if not fvg['filled'] and fvg['top'] < current_price]
        unfilled_bearish = [fvg for fvg in bearish_fvgs if not fvg['filled'] and fvg['bottom'] > current_price]
        
        if unfilled_bullish:
            analysis['nearest_support_fvg'] = max(unfilled_bullish, key=lambda x: x['top'])
        if unfilled_bearish:
            analysis['nearest_resistance_fvg'] = min(unfilled_bearish, key=lambda x: x['bottom'])
        
        return analysis
    
    def _get_recent_fvgs(self, bullish_fvgs, bearish_fvgs, lookback=5):
        """Get FVGs formed in recent candles"""
        recent_fvgs = []
        
        # Get most recent FVGs
        all_fvgs = bullish_fvgs + bearish_fvgs
        if all_fvgs:
            # Sort by index (most recent first)
            all_fvgs.sort(key=lambda x: x['index'], reverse=True)
            recent_fvgs = all_fvgs[:lookback]
        
        return recent_fvgs
    
    def _generate_fvg_signals(self, fvg_analysis, recent_fvgs):
        """Generate trading signals based on FVG analysis"""
        signals = {
            'signal_strength': 0,
            'primary_signal': 'neutral',
            'signals': [],
            'recommendations': []
        }
        
        # Check if price is inside an FVG
        if fvg_analysis['inside_fvg']:
            fvg = fvg_analysis['inside_fvg']
            if fvg['type'] == 'bullish':
                signals['primary_signal'] = 'bullish_support'
                signals['signals'].append('Price inside bullish FVG - potential support zone')
                signals['signal_strength'] = 70
            else:
                signals['primary_signal'] = 'bearish_resistance'
                signals['signals'].append('Price inside bearish FVG - potential resistance zone')
                signals['signal_strength'] = 70
        
        # Check for recent FVG formations
        if recent_fvgs:
            latest_fvg = recent_fvgs[0]
            if latest_fvg['type'] == 'bullish':
                signals['signals'].append('Recent bullish FVG formed - watch for support')
                signals['signal_strength'] += 20
            else:
                signals['signals'].append('Recent bearish FVG formed - watch for resistance')
                signals['signal_strength'] += 20
        
        # Generate recommendations
        if fvg_analysis['nearest_support_fvg']:
            support_fvg = fvg_analysis['nearest_support_fvg']
            signals['recommendations'].append(f"Nearest support FVG: ${support_fvg['bottom']:.4f} - ${support_fvg['top']:.4f}")
        
        if fvg_analysis['nearest_resistance_fvg']:
            resistance_fvg = fvg_analysis['nearest_resistance_fvg']
            signals['recommendations'].append(f"Nearest resistance FVG: ${resistance_fvg['bottom']:.4f} - ${resistance_fvg['top']:.4f}")
        
        signals['signal_strength'] = min(signals['signal_strength'], 100)
        return signals
    
    def _find_nearest_fvg(self, current_price, bullish_fvgs, bearish_fvgs):
        """Find the nearest unfilled FVG to current price"""
        nearest = None
        min_distance = float('inf')
        
        # Check all unfilled FVGs
        all_unfilled = [fvg for fvg in bullish_fvgs + bearish_fvgs if not fvg['filled']]
        
        for fvg in all_unfilled:
            # Calculate distance to FVG center
            fvg_center = (fvg['top'] + fvg['bottom']) / 2
            distance = abs(current_price - fvg_center)
            
            if distance < min_distance:
                min_distance = distance
                nearest = fvg
        
        return nearest
    
    def _get_empty_result(self):
        """Return empty result structure"""
        return {
            'bullish_fvgs': [],
            'bearish_fvgs': [],
            'total_fvgs': 0,
            'current_analysis': {
                'above_bullish_fvgs': 0,
                'below_bearish_fvgs': 0,
                'inside_fvg': None,
                'nearest_support_fvg': None,
                'nearest_resistance_fvg': None
            },
            'recent_fvgs': [],
            'fvg_signals': {
                'signal_strength': 0,
                'primary_signal': 'neutral',
                'signals': [],
                'recommendations': []
            },
            'nearest_fvg': None
        }