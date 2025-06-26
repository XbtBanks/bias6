import pandas as pd
import numpy as np
import streamlit as st

class MarketStructureAnalyzer:
    """
    Advanced market structure analysis for support/resistance, trend strength, and price action patterns
    """
    
    def __init__(self):
        pass
    
    def analyze_market_structure(self, data, ema_data):
        """
        Comprehensive market structure analysis
        """
        return {
            'support_resistance': self._find_support_resistance(data),
            'trend_strength': self._calculate_trend_strength(data, ema_data),
            'price_action_patterns': self._detect_price_patterns(data),
            'volume_profile': self._analyze_volume_profile(data),
            'breakout_probability': self._calculate_breakout_probability(data, ema_data),
            'institutional_levels': self._find_institutional_levels(data)
        }
    
    def _find_support_resistance(self, data):
        """
        Dynamic support and resistance level detection
        """
        try:
            highs = data['High'].values
            lows = data['Low'].values
            closes = data['Close'].values
            
            # Find swing highs and lows
            swing_highs = []
            swing_lows = []
            
            for i in range(2, len(highs) - 2):
                if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                    swing_highs.append(highs[i])
                
                if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                    swing_lows.append(lows[i])
            
            current_price = closes[-1]
            
            # Find closest levels
            resistance_levels = [h for h in swing_highs if h > current_price]
            support_levels = [l for l in swing_lows if l < current_price]
            
            nearest_resistance = min(resistance_levels) if len(resistance_levels) > 0 else None
            nearest_support = max(support_levels) if len(support_levels) > 0 else None
            
            return {
                'nearest_resistance': nearest_resistance,
                'nearest_support': nearest_support,
                'resistance_strength': len([r for r in resistance_levels if abs(r - nearest_resistance) < current_price * 0.01]) if nearest_resistance else 0,
                'support_strength': len([s for s in support_levels if abs(s - nearest_support) < current_price * 0.01]) if nearest_support else 0,
                'price_position': 'resistance_zone' if nearest_resistance and (current_price / nearest_resistance) > 0.98 else 'support_zone' if nearest_support and (current_price / nearest_support) < 1.02 else 'neutral'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_trend_strength(self, data, ema_data):
        """
        Calculate trend strength using multiple factors
        """
        try:
            closes = data['Close'].values
            volumes = data['Volume'].values
            
            # Price momentum
            short_ma = np.mean(closes[-5:])
            long_ma = np.mean(closes[-20:])
            momentum = (short_ma - long_ma) / long_ma * 100
            
            # EMA alignment score
            ema_keys = list(ema_data.keys())
            alignment_score = 0
            
            for i in range(len(ema_keys) - 1):
                current_ema = ema_data[ema_keys[i]].iloc[-1]
                next_ema = ema_data[ema_keys[i + 1]].iloc[-1]
                
                if current_ema > next_ema:
                    alignment_score += 1
                elif current_ema < next_ema:
                    alignment_score -= 1
            
            alignment_percentage = (alignment_score / (len(ema_keys) - 1)) * 100
            
            # Volume confirmation
            recent_volume = np.mean(volumes[-5:])
            avg_volume = np.mean(volumes[-20:])
            volume_confirmation = recent_volume / avg_volume
            
            # Overall trend strength
            if alignment_percentage > 60 and momentum > 1:
                trend_direction = 'Strong Bullish'
                trend_score = min(100, abs(alignment_percentage) + abs(momentum) * 10)
            elif alignment_percentage < -60 and momentum < -1:
                trend_direction = 'Strong Bearish'
                trend_score = min(100, abs(alignment_percentage) + abs(momentum) * 10)
            elif abs(alignment_percentage) > 30:
                trend_direction = 'Moderate ' + ('Bullish' if alignment_percentage > 0 else 'Bearish')
                trend_score = abs(alignment_percentage) + abs(momentum) * 5
            else:
                trend_direction = 'Sideways'
                trend_score = 20
            
            return {
                'direction': trend_direction,
                'strength_score': trend_score,
                'momentum': momentum,
                'ema_alignment': alignment_percentage,
                'volume_confirmation': volume_confirmation,
                'reliability': 'High' if volume_confirmation > 1.2 and abs(alignment_percentage) > 50 else 'Medium' if abs(alignment_percentage) > 30 else 'Low'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _detect_price_patterns(self, data):
        """
        Detect common price action patterns
        """
        try:
            closes = data['Close'].values[-20:]  # Last 20 periods
            highs = data['High'].values[-20:]
            lows = data['Low'].values[-20:]
            
            patterns = []
            
            # Higher highs and higher lows (uptrend)
            if len(closes) >= 10:
                recent_highs = highs[-5:]
                recent_lows = lows[-5:]
                
                if all(recent_highs[i] >= recent_highs[i-1] for i in range(1, len(recent_highs))):
                    if all(recent_lows[i] >= recent_lows[i-1] for i in range(1, len(recent_lows))):
                        patterns.append('Higher Highs & Higher Lows (Bullish)')
                
                # Lower highs and lower lows (downtrend)
                if all(recent_highs[i] <= recent_highs[i-1] for i in range(1, len(recent_highs))):
                    if all(recent_lows[i] <= recent_lows[i-1] for i in range(1, len(recent_lows))):
                        patterns.append('Lower Highs & Lower Lows (Bearish)')
            
            # Consolidation pattern
            price_range = (max(closes) - min(closes)) / np.mean(closes) * 100
            if price_range < 3:  # Less than 3% range
                patterns.append('Tight Consolidation')
            
            # Breakout pattern
            if len(closes) >= 15:
                consolidation_subset = closes[-10:-2]
                if len(consolidation_subset) > 0:
                    consolidation_range = max(consolidation_subset) - min(consolidation_subset)
                    recent_move = abs(closes[-1] - closes[-3])
                    
                    if recent_move > consolidation_range * 1.5:
                        direction = 'Upward' if closes[-1] > closes[-3] else 'Downward'
                        patterns.append(f'{direction} Breakout')
            
            return {
                'detected_patterns': patterns,
                'pattern_count': len(patterns),
                'market_character': 'Trending' if any('Bullish' in p or 'Bearish' in p for p in patterns) else 'Ranging'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_volume_profile(self, data):
        """
        Analyze volume distribution and strength
        """
        try:
            volumes = data['Volume'].values
            closes = data['Close'].values
            
            # Volume trend
            recent_avg = np.mean(volumes[-5:])
            longer_avg = np.mean(volumes[-20:])
            volume_trend = (recent_avg - longer_avg) / longer_avg * 100
            
            # Volume-price correlation
            price_changes = np.diff(closes[-10:])
            volume_changes = volumes[-9:]  # Align with price_changes length
            
            correlation = np.corrcoef(price_changes, volume_changes)[0, 1] if len(price_changes) == len(volume_changes) else 0
            
            # Volume quality assessment
            if volume_trend > 20 and correlation > 0.3:
                volume_quality = 'Excellent'
            elif volume_trend > 0 and correlation > 0:
                volume_quality = 'Good'
            elif volume_trend > -10:
                volume_quality = 'Average'
            else:
                volume_quality = 'Poor'
            
            return {
                'volume_trend': volume_trend,
                'price_volume_correlation': correlation,
                'quality': volume_quality,
                'current_volume_vs_avg': recent_avg / longer_avg,
                'interpretation': self._interpret_volume(volume_trend, correlation)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _interpret_volume(self, trend, correlation):
        """
        Interpret volume analysis
        """
        if trend > 20 and correlation > 0.5:
            return 'Strong volume confirmation - High probability moves'
        elif trend > 0 and correlation > 0.2:
            return 'Moderate volume support - Good for trend continuation'
        elif trend < -20:
            return 'Declining volume - Possible trend exhaustion'
        else:
            return 'Mixed volume signals - Use caution'
    
    def _calculate_breakout_probability(self, data, ema_data):
        """
        Calculate probability of price breakout
        """
        try:
            closes = data['Close'].values
            volumes = data['Volume'].values
            
            # Price compression (lower volatility = higher breakout probability)
            recent_volatility = np.std(closes[-10:]) / np.mean(closes[-10:])
            historical_volatility = np.std(closes[-30:]) / np.mean(closes[-30:])
            compression_ratio = historical_volatility / recent_volatility if recent_volatility > 0 else 1
            
            # Volume accumulation
            volume_ratio = np.mean(volumes[-5:]) / np.mean(volumes[-20:])
            
            # EMA convergence
            ema_values = [ema_data[key].iloc[-1] for key in ema_data.keys()]
            if len(ema_values) > 0:
                ema_range = (max(ema_values) - min(ema_values)) / np.mean(ema_values) * 100
            else:
                ema_range = 0
            
            # Calculate breakout probability
            base_probability = 30
            
            if compression_ratio > 1.5:
                base_probability += 25
            if volume_ratio > 1.2:
                base_probability += 20
            if ema_range < 2:
                base_probability += 15
            
            breakout_probability = min(95, base_probability)
            
            return {
                'probability': breakout_probability,
                'compression_ratio': compression_ratio,
                'volume_accumulation': volume_ratio,
                'ema_convergence': ema_range,
                'timeframe_estimate': '1-5 periods' if breakout_probability > 70 else '5-15 periods' if breakout_probability > 50 else 'Uncertain'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _find_institutional_levels(self, data):
        """
        Identify potential institutional price levels (round numbers, previous day/week highs/lows)
        """
        try:
            current_price = data['Close'].iloc[-1]
            
            # Round number levels
            price_magnitude = 10 ** (len(str(int(current_price))) - 2)
            round_levels = []
            
            for multiplier in [0.5, 1, 1.5, 2, 2.5, 3]:
                level = round(current_price / price_magnitude) * price_magnitude * multiplier
                if abs(level - current_price) / current_price < 0.1:  # Within 10%
                    round_levels.append(level)
            
            # Previous period levels
            if len(data) >= 24:  # At least 24 periods
                prev_day_high = data['High'].iloc[-24:].max()
                prev_day_low = data['Low'].iloc[-24:].min()
            else:
                prev_day_high = data['High'].max()
                prev_day_low = data['Low'].min()
            
            # Key psychological levels
            psychological_levels = []
            base = int(current_price / 100) * 100
            for offset in [0, 50, 100, 150, 200]:
                level = base + offset
                if abs(level - current_price) / current_price < 0.15:
                    psychological_levels.append(level)
            
            return {
                'round_numbers': round_levels,
                'previous_day_high': prev_day_high,
                'previous_day_low': prev_day_low,
                'psychological_levels': psychological_levels,
                'nearest_institutional_level': min(round_levels + psychological_levels, key=lambda x: abs(x - current_price)) if (round_levels or psychological_levels) and len(round_levels + psychological_levels) > 0 else None
            }
        except Exception as e:
            return {'error': str(e)}