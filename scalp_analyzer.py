import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ScalpAnalyzer:
    """
    Specialized analyzer for scalp trading with faster EMA signals and micro-trend detection
    """
    
    def __init__(self, scalp_ema_periods=None):
        self.scalp_ema_periods = scalp_ema_periods or [8, 21, 45, 89]  # Fast EMAs for scalp
        self.scalp_timeframes = ['1m', '5m', '15m']
        self.entry_threshold = 0.7  # Scalp entry threshold
        self.exit_threshold = 0.3   # Quick exit threshold
        
    def analyze_scalp_signals(self, data, ema_data):
        """
        Generate scalp trading signals based on fast EMA movements
        """
        try:
            # Fast EMA crossover signals
            crossover_signals = self._detect_fast_crossovers(ema_data)
            
            # Micro-trend analysis
            micro_trends = self._analyze_micro_trends(data)
            
            # Momentum scalp signals
            momentum_signals = self._detect_momentum_scalp_signals(data)
            
            # Volume confirmation for scalp trades
            volume_confirmation = self._analyze_scalp_volume(data)
            
            # Price action scalp patterns
            price_patterns = self._detect_scalp_patterns(data)
            
            # Combine all signals for scalp score
            scalp_score = self._calculate_scalp_score(
                crossover_signals, micro_trends, momentum_signals, 
                volume_confirmation, price_patterns
            )
            
            # Generate specific scalp trade recommendations
            trade_signals = self._generate_scalp_trade_signals(data, ema_data, scalp_score)
            
            return {
                'scalp_score': scalp_score,
                'crossover_signals': crossover_signals,
                'micro_trends': micro_trends,
                'momentum_signals': momentum_signals,
                'volume_confirmation': volume_confirmation,
                'price_patterns': price_patterns,
                'entry_signals': self._generate_entry_signals(scalp_score, crossover_signals),
                'exit_signals': self._generate_exit_signals(data, ema_data),
                'trade_signals': trade_signals,
                'scalp_timeframe': '1-5 dakika',
                'recommended_hold_time': '5-30 dakika'
            }
        except Exception as e:
            return {'error': str(e), 'scalp_score': 0}
    
    def _generate_scalp_trade_signals(self, data, ema_data, scalp_score):
        """
        Generate specific scalp trade entry/exit signals with price levels
        """
        try:
            current_price = data['Close'].iloc[-1]
            
            # Quick scalp signals for 1-5 minute trades
            signals = {
                'action': 'HOLD',
                'confidence': 0,
                'entry_price': None,
                'stop_loss': None,
                'take_profit_1': None,
                'take_profit_2': None,
                'hold_time': '5-15 dakika',
                'risk_reward': '1:2'
            }
            
            # Fast EMA signals
            if 'ema_21' in ema_data and 'ema_45' in ema_data:
                ema_21 = ema_data['ema_21'].iloc[-1]
                ema_45 = ema_data['ema_45'].iloc[-1]
                
                price_above_21 = current_price > ema_21
                price_above_45 = current_price > ema_45
                ema_21_above_45 = ema_21 > ema_45
                
                # Dynamic risk/reward based on timeframe and volatility
                volatility_factor = self._calculate_volatility_factor(data)
                
                # Adjust risk levels based on timeframe (extracted from global context if available)
                timeframe_risk = {
                    '1m': {'stop': 0.15, 'tp1': 0.25, 'tp2': 0.45},
                    '3m': {'stop': 0.2, 'tp1': 0.35, 'tp2': 0.6},
                    '5m': {'stop': 0.25, 'tp1': 0.4, 'tp2': 0.75},
                    '10m': {'stop': 0.3, 'tp1': 0.5, 'tp2': 0.9},
                    '15m': {'stop': 0.35, 'tp1': 0.6, 'tp2': 1.1},
                    '20m': {'stop': 0.4, 'tp1': 0.7, 'tp2': 1.3},
                    '30m': {'stop': 0.5, 'tp1': 0.8, 'tp2': 1.5},
                    '45m': {'stop': 0.6, 'tp1': 1.0, 'tp2': 1.8},
                    '55m': {'stop': 0.7, 'tp1': 1.2, 'tp2': 2.0},
                    '1h': {'stop': 0.8, 'tp1': 1.4, 'tp2': 2.5}
                }
                
                # Default to 10m if timeframe not found
                risk_params = timeframe_risk.get('10m', timeframe_risk['10m'])
                
                # Apply volatility adjustment
                stop_pct = risk_params['stop'] * volatility_factor
                tp1_pct = risk_params['tp1'] * volatility_factor  
                tp2_pct = risk_params['tp2'] * volatility_factor
                
                # Bullish scalp setup
                if price_above_21 and ema_21_above_45 and scalp_score > 60:
                    signals.update({
                        'action': 'LONG',
                        'confidence': min(scalp_score, 95),
                        'entry_price': current_price,
                        'stop_loss': current_price * (1 - stop_pct/100),
                        'take_profit_1': current_price * (1 + tp1_pct/100),
                        'take_profit_2': current_price * (1 + tp2_pct/100),
                        'stop_pct': stop_pct,
                        'tp1_pct': tp1_pct,
                        'tp2_pct': tp2_pct
                    })
                
                # Bearish scalp setup
                elif not price_above_21 and not ema_21_above_45 and scalp_score > 60:
                    signals.update({
                        'action': 'SHORT',
                        'confidence': min(scalp_score, 95),
                        'entry_price': current_price,
                        'stop_loss': current_price * (1 + stop_pct/100),
                        'take_profit_1': current_price * (1 - tp1_pct/100),
                        'take_profit_2': current_price * (1 - tp2_pct/100),
                        'stop_pct': stop_pct,
                        'tp1_pct': tp1_pct,
                        'tp2_pct': tp2_pct
                    })
            
            return signals
            
        except Exception as e:
            return {
                'action': 'HOLD',
                'confidence': 0,
                'error': str(e)
            }
    
    def _calculate_volatility_factor(self, data):
        """
        Calculate volatility factor to adjust risk parameters
        """
        try:
            # Calculate ATR-based volatility
            if len(data) < 14:
                return 1.0
                
            high_low = data['High'] - data['Low']
            high_close = abs(data['High'] - data['Close'].shift(1))
            low_close = abs(data['Low'] - data['Close'].shift(1))
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr_series = true_range.rolling(14).mean()
            try:
                if isinstance(atr_series, pd.Series) and len(atr_series) > 0:
                    last_value = atr_series.values[-1]
                    atr_value = float(last_value) if not pd.isna(last_value) else 0.01
                else:
                    atr_value = 0.01
            except (IndexError, TypeError, AttributeError):
                atr_value = 0.01
            
            # Normalize ATR as percentage of current price
            current_price = data['Close'].iloc[-1]
            atr_pct = (atr_value / current_price) * 100
            
            # Volatility factor: 1.0 = normal, >1.0 = high volatility, <1.0 = low volatility
            if atr_pct > 2.0:
                return 1.5  # High volatility - increase risk parameters
            elif atr_pct > 1.0:
                return 1.2  # Medium volatility
            elif atr_pct < 0.5:
                return 0.8  # Low volatility - decrease risk parameters
            else:
                return 1.0  # Normal volatility
                
        except Exception:
            return 1.0  # Default volatility factor
    
    def _detect_fast_crossovers(self, ema_data):
        """
        Detect fast EMA crossovers for scalp signals
        """
        try:
            signals = []
            
            # Use optimized scalp EMAs - 21 vs 45 for faster signals
            ema_21_key = None
            ema_45_key = None
            
            # Find available EMA keys that match our scalp periods
            for key in ema_data.keys():
                if '21' in key:
                    ema_21_key = key
                elif '45' in key:
                    ema_45_key = key
            
            # Fallback to closest available EMAs
            if not ema_21_key:
                ema_21_key = 'EMA_45'  # Use 45 as fast EMA if 21 not available
            if not ema_45_key:
                ema_45_key = 'EMA_89'  # Use 89 as slow EMA if 45 not available
                
            ema_fast = ema_data.get(ema_21_key, pd.Series())
            ema_slow = ema_data.get(ema_45_key, pd.Series())
            
            if len(ema_fast) < 3 or len(ema_slow) < 3:
                return {'signals': [], 'strength': 0, 'direction': 'neutral'}
            
            # Check for recent crossovers in last 3 periods
            current_above = ema_fast.iloc[-1] > ema_slow.iloc[-1]
            prev_above = ema_fast.iloc[-2] > ema_slow.iloc[-2]
            prev2_above = ema_fast.iloc[-3] > ema_slow.iloc[-3]
            
            crossover_strength = 0
            direction = 'neutral'
            
            # Bullish crossover
            if current_above and not prev_above:
                signals.append('Bullish Crossover - Fresh')
                crossover_strength = 80
                direction = 'bullish'
            elif current_above and prev_above and not prev2_above:
                signals.append('Bullish Crossover - Continuation')
                crossover_strength = 60
                direction = 'bullish'
            
            # Bearish crossover
            elif not current_above and prev_above:
                signals.append('Bearish Crossover - Fresh')
                crossover_strength = 80
                direction = 'bearish'
            elif not current_above and not prev_above and prev2_above:
                signals.append('Bearish Crossover - Continuation')
                crossover_strength = 60
                direction = 'bearish'
            
            # Trending signals
            elif current_above and prev_above and prev2_above:
                signals.append('Strong Bullish Trend')
                crossover_strength = 40
                direction = 'bullish'
            elif not current_above and not prev_above and not prev2_above:
                signals.append('Strong Bearish Trend')
                crossover_strength = 40
                direction = 'bearish'
            
            return {
                'signals': signals,
                'strength': crossover_strength,
                'direction': direction,
                'ema_separation': abs(ema_fast.iloc[-1] - ema_slow.iloc[-1]) / ema_slow.iloc[-1] * 100,
                'fast_ema_period': ema_21_key,
                'slow_ema_period': ema_45_key
            }
        except Exception as e:
            return {'signals': [], 'strength': 0, 'direction': 'neutral', 'error': str(e)}
    
    def _analyze_micro_trends(self, data):
        """
        Analyze micro-trends for scalp trading
        """
        try:
            closes = data['Close'].values
            
            if len(closes) < 10:
                return {'trend': 'insufficient_data', 'strength': 0}
            
            # Analyze last 5 and 10 periods
            short_trend = (closes[-1] - closes[-5]) / closes[-5] * 100
            medium_trend = (closes[-1] - closes[-10]) / closes[-10] * 100
            
            # Price velocity (rate of change)
            velocity = np.mean(np.diff(closes[-5:]))
            
            # Determine micro-trend
            if short_trend > 0.5 and medium_trend > 0:
                trend = 'strong_bullish'
                strength = min(100, abs(short_trend) * 20)
            elif short_trend > 0.1:
                trend = 'weak_bullish'
                strength = min(100, abs(short_trend) * 30)
            elif short_trend < -0.5 and medium_trend < 0:
                trend = 'strong_bearish'
                strength = min(100, abs(short_trend) * 20)
            elif short_trend < -0.1:
                trend = 'weak_bearish'
                strength = min(100, abs(short_trend) * 30)
            else:
                trend = 'sideways'
                strength = 10
            
            return {
                'trend': trend,
                'strength': strength,
                'short_change': short_trend,
                'medium_change': medium_trend,
                'velocity': velocity
            }
        except Exception as e:
            return {'trend': 'error', 'strength': 0, 'error': str(e)}
    
    def _detect_momentum_scalp_signals(self, data):
        """
        Detect momentum-based scalp signals
        """
        try:
            closes = data['Close'].values
            highs = data['High'].values
            lows = data['Low'].values
            
            if len(closes) < 5:
                return {'momentum': 0, 'signals': []}
            
            # Price momentum indicators
            roc_3 = (closes[-1] - closes[-3]) / closes[-3] * 100  # 3-period ROC
            roc_5 = (closes[-1] - closes[-5]) / closes[-5] * 100  # 5-period ROC
            
            # High/Low momentum
            recent_high = max(highs[-3:])
            recent_low = min(lows[-3:])
            price_position = (closes[-1] - recent_low) / (recent_high - recent_low) * 100
            
            signals = []
            momentum_score = 0
            
            # Strong momentum signals
            if roc_3 > 0.3 and roc_5 > 0.5:
                signals.append('Strong Bullish Momentum')
                momentum_score = 80
            elif roc_3 < -0.3 and roc_5 < -0.5:
                signals.append('Strong Bearish Momentum')
                momentum_score = 80
            
            # Medium momentum
            elif roc_3 > 0.1 and price_position > 70:
                signals.append('Moderate Bullish Momentum')
                momentum_score = 60
            elif roc_3 < -0.1 and price_position < 30:
                signals.append('Moderate Bearish Momentum')
                momentum_score = 60
            
            # Momentum exhaustion
            elif abs(roc_3) > 1.0:
                signals.append('Momentum Exhaustion - Reversal Risk')
                momentum_score = 20
            
            return {
                'momentum_score': momentum_score,
                'signals': signals,
                'roc_3': roc_3,
                'roc_5': roc_5,
                'price_position': price_position
            }
        except Exception as e:
            return {'momentum_score': 0, 'signals': [], 'error': str(e)}
    
    def _analyze_scalp_volume(self, data):
        """
        Analyze volume for scalp trade confirmation
        """
        try:
            volumes = data['Volume'].values
            closes = data['Close'].values
            
            if len(volumes) < 5:
                return {'volume_confirmation': 'insufficient_data', 'strength': 0}
            
            # Recent volume vs average
            recent_volume = np.mean(volumes[-3:])
            avg_volume = np.mean(volumes[-10:]) if len(volumes) >= 10 else recent_volume
            
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Volume-price relationship
            price_change = (closes[-1] - closes[-3]) / closes[-3] * 100
            
            # Volume confirmation logic
            if volume_ratio > 1.5 and abs(price_change) > 0.2:
                confirmation = 'strong_confirmation'
                strength = min(100, volume_ratio * 30)
            elif volume_ratio > 1.2:
                confirmation = 'moderate_confirmation'
                strength = min(100, volume_ratio * 20)
            elif volume_ratio < 0.8:
                confirmation = 'weak_volume'
                strength = 20
            else:
                confirmation = 'neutral_volume'
                strength = 50
            
            return {
                'volume_confirmation': confirmation,
                'strength': strength,
                'volume_ratio': volume_ratio,
                'recent_volume': recent_volume
            }
        except Exception as e:
            return {'volume_confirmation': 'error', 'strength': 0, 'error': str(e)}
    
    def _detect_scalp_patterns(self, data):
        """
        Detect scalp-specific price patterns
        """
        try:
            closes = data['Close'].values
            highs = data['High'].values
            lows = data['Low'].values
            
            if len(closes) < 5:
                return {'patterns': [], 'pattern_score': 0}
            
            patterns = []
            pattern_score = 0
            
            # Micro pullback pattern
            if len(closes) >= 5:
                trend_up = closes[-5] < closes[-1]
                pullback = closes[-3] < closes[-2] and closes[-2] > closes[-1]
                
                if trend_up and pullback:
                    patterns.append('Bullish Micro Pullback')
                    pattern_score += 30
                
                trend_down = closes[-5] > closes[-1]
                bounce = closes[-3] > closes[-2] and closes[-2] < closes[-1]
                
                if trend_down and bounce:
                    patterns.append('Bearish Micro Bounce')
                    pattern_score += 30
            
            # Quick reversal pattern
            if len(closes) >= 3:
                quick_reversal_bull = lows[-2] < lows[-3] and closes[-1] > closes[-2]
                quick_reversal_bear = highs[-2] > highs[-3] and closes[-1] < closes[-2]
                
                if quick_reversal_bull:
                    patterns.append('Quick Bullish Reversal')
                    pattern_score += 25
                
                if quick_reversal_bear:
                    patterns.append('Quick Bearish Reversal')
                    pattern_score += 25
            
            # Micro breakout
            recent_range = max(highs[-5:]) - min(lows[-5:]) if len(highs) >= 5 else 0
            if recent_range > 0:
                breakout_bull = closes[-1] > max(highs[-5:-1])
                breakout_bear = closes[-1] < min(lows[-5:-1])
                
                if breakout_bull:
                    patterns.append('Micro Bullish Breakout')
                    pattern_score += 35
                
                if breakout_bear:
                    patterns.append('Micro Bearish Breakout')
                    pattern_score += 35
            
            return {
                'patterns': patterns,
                'pattern_score': min(100, pattern_score)
            }
        except Exception as e:
            return {'patterns': [], 'pattern_score': 0, 'error': str(e)}
    
    def _calculate_scalp_score(self, crossover_signals, micro_trends, momentum_signals, volume_confirmation, price_patterns):
        """
        Calculate overall scalp trading score
        """
        try:
            # Weight different components
            crossover_weight = 0.30
            trend_weight = 0.25
            momentum_weight = 0.25
            volume_weight = 0.15
            pattern_weight = 0.05
            
            crossover_score = crossover_signals.get('strength', 0)
            trend_score = micro_trends.get('strength', 0)
            momentum_score = momentum_signals.get('momentum_score', 0)
            volume_score = volume_confirmation.get('strength', 0)
            pattern_score = price_patterns.get('pattern_score', 0)
            
            # Calculate weighted score
            total_score = (
                crossover_score * crossover_weight +
                trend_score * trend_weight +
                momentum_score * momentum_weight +
                volume_score * volume_weight +
                pattern_score * pattern_weight
            )
            
            # Determine scalp quality
            if total_score > 75:
                quality = 'Excellent Scalp'
            elif total_score > 60:
                quality = 'Good Scalp'
            elif total_score > 45:
                quality = 'Moderate Scalp'
            elif total_score > 30:
                quality = 'Weak Scalp'
            else:
                quality = 'No Scalp Signal'
            
            return {
                'total_score': total_score,
                'quality': quality,
                'component_scores': {
                    'crossover': crossover_score,
                    'trend': trend_score,
                    'momentum': momentum_score,
                    'volume': volume_score,
                    'patterns': pattern_score
                }
            }
        except Exception as e:
            return {'total_score': 0, 'quality': 'Error', 'error': str(e)}
    
    def _generate_entry_signals(self, scalp_score, crossover_signals):
        """
        Generate specific entry signals for scalp trades
        """
        try:
            entry_signals = []
            
            score = scalp_score.get('total_score', 0)
            direction = crossover_signals.get('direction', 'neutral')
            
            if score > 70 and direction == 'bullish':
                entry_signals.append({
                    'signal': 'STRONG BUY SCALP',
                    'confidence': 'High',
                    'timeframe': '1-5 minutes',
                    'action': 'Enter long position immediately'
                })
            elif score > 60 and direction == 'bullish':
                entry_signals.append({
                    'signal': 'BUY SCALP',
                    'confidence': 'Medium',
                    'timeframe': '3-10 minutes',
                    'action': 'Consider long position'
                })
            elif score > 70 and direction == 'bearish':
                entry_signals.append({
                    'signal': 'STRONG SELL SCALP',
                    'confidence': 'High',
                    'timeframe': '1-5 minutes',
                    'action': 'Enter short position immediately'
                })
            elif score > 60 and direction == 'bearish':
                entry_signals.append({
                    'signal': 'SELL SCALP',
                    'confidence': 'Medium',
                    'timeframe': '3-10 minutes',
                    'action': 'Consider short position'
                })
            else:
                entry_signals.append({
                    'signal': 'NO SCALP SIGNAL',
                    'confidence': 'Low',
                    'timeframe': 'Wait',
                    'action': 'Wait for better setup'
                })
            
            return entry_signals
        except Exception as e:
            return [{'signal': 'ERROR', 'error': str(e)}]
    
    def _generate_exit_signals(self, data, ema_data):
        """
        Generate exit signals for scalp trades
        """
        try:
            exit_signals = []
            
            closes = data['Close'].values
            if len(closes) < 3:
                return [{'signal': 'Insufficient data for exit signals'}]
            
            # Quick profit target (0.2-0.5% for scalp)
            current_price = closes[-1]
            
            # EMA-based exit - use the fastest available EMA
            fastest_ema_key = 'EMA_45'  # Default to 45 EMA
            if 'EMA_21' in ema_data:
                fastest_ema_key = 'EMA_21'
            elif 'EMA_8' in ema_data:
                fastest_ema_key = 'EMA_8'
                
            fastest_ema = ema_data.get(fastest_ema_key, pd.Series())
            if len(fastest_ema) > 0:
                ema_distance = abs(current_price - fastest_ema.iloc[-1]) / current_price * 100
                
                if ema_distance > 0.3:  # More than 0.3% from EMA
                    exit_signals.append({
                        'signal': 'EMA Exit Signal',
                        'reason': f'Price {ema_distance:.2f}% from EMA45',
                        'action': 'Consider taking profits'
                    })
            
            # Momentum exhaustion exit
            recent_change = (closes[-1] - closes[-3]) / closes[-3] * 100
            if abs(recent_change) > 0.8:  # More than 0.8% move
                exit_signals.append({
                    'signal': 'Momentum Exhaustion',
                    'reason': f'{recent_change:.2f}% move in 3 periods',
                    'action': 'Take profits on momentum exhaustion'
                })
            
            # Time-based exit (scalp trades should be quick)
            exit_signals.append({
                'signal': 'Time Exit',
                'reason': 'Scalp trades should be held 1-15 minutes max',
                'action': 'Exit if position open >15 minutes'
            })
            
            return exit_signals
        except Exception as e:
            return [{'signal': 'ERROR', 'error': str(e)}]