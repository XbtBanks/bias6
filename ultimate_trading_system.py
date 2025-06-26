import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

class UltimateTradingSystem:
    """
    Ultimate Trading Analysis System - Combines all powerful features:
    - EMA Bias Analysis with fixed periods (45, 89, 144, 200, 276)
    - Smart Money Concepts (Order Blocks, FVG, Liquidity)
    - Institutional Levels (Daily, Weekly, Monthly, Yearly)
    - Funding & CVD Analysis (crypto only)
    - DXY Analysis (forex only)
    - Advanced Market Structure
    - Scalping Signals
    - Multi-timeframe confluence
    """
    
    def __init__(self):
        self.ema_periods = [45, 89, 144, 200, 276]
        self.timezone = pytz.timezone('UTC')
        
    def get_ultimate_analysis(self, data, symbol, timeframe='1h'):
        """
        Get comprehensive ultimate trading analysis
        """
        try:
            if data is None or len(data) < 50:
                return self._get_fallback_analysis()
            
            current_price = float(data['Close'].iloc[-1])
            
            # Determine asset type
            is_crypto = any(symbol.upper().endswith(suffix) for suffix in ['USDT', 'USDC', 'BTC', 'ETH']) or '.P' in symbol.upper()
            is_forex = any(symbol.upper().endswith(pair) for pair in ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD']) and len(symbol) <= 7
            
            # Core analysis components
            analysis = {
                'symbol': symbol,
                'current_price': current_price,
                'asset_type': 'crypto' if is_crypto else 'forex' if is_forex else 'other',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                
                # Primary analysis
                'ema_bias': self._calculate_ema_bias(data),
                'smart_money': self._analyze_smart_money_concepts(data, current_price),
                'institutional_levels': self._calculate_institutional_levels(data),
                'market_structure': self._analyze_market_structure(data, current_price),
                'scalp_signals': self._generate_scalp_signals(data, current_price),
                
                # Asset-specific analysis
                'funding_cvd': self._analyze_funding_cvd(data, symbol) if is_crypto else None,
                'dxy_impact': self._analyze_dxy_impact(symbol) if is_forex else None,
                
                # Ultimate signal
                'ultimate_signal': None,
                'confidence_score': 0,
                'trading_recommendation': '',
                'risk_level': 'Medium'
            }
            
            # Calculate ultimate signal by combining all components
            analysis['ultimate_signal'] = self._calculate_ultimate_signal(analysis)
            
            return analysis
            
        except Exception as e:
            print(f"Ultimate analysis error: {e}")
            return self._get_fallback_analysis()
    
    def _calculate_ema_bias(self, data):
        """Calculate EMA bias using fixed periods"""
        try:
            close_prices = pd.Series(data['Close'].values, dtype=float)
            
            # Calculate EMAs
            emas = {}
            for period in self.ema_periods:
                emas[period] = close_prices.ewm(span=period).mean()
            
            current_price = close_prices.iloc[-1]
            
            # Determine bias based on EMA sequence
            ema_values = [emas[period].iloc[-1] for period in self.ema_periods]
            
            # Check if EMAs are in ascending order (bullish) or descending (bearish)
            ascending = all(ema_values[i] <= ema_values[i+1] for i in range(len(ema_values)-1))
            descending = all(ema_values[i] >= ema_values[i+1] for i in range(len(ema_values)-1))
            
            # Price position relative to EMAs
            above_all_emas = all(current_price > ema for ema in ema_values)
            below_all_emas = all(current_price < ema for ema in ema_values)
            
            # Calculate bias strength (0-100)
            if above_all_emas and ascending:
                bias = 'Very Bullish'
                strength = 90
            elif above_all_emas:
                bias = 'Bullish'
                strength = 75
            elif below_all_emas and descending:
                bias = 'Very Bearish'
                strength = 90
            elif below_all_emas:
                bias = 'Bearish'
                strength = 75
            else:
                bias = 'Neutral'
                strength = 50
            
            return {
                'bias': bias,
                'strength': strength,
                'ema_values': {period: emas[period].iloc[-1] for period in self.ema_periods},
                'price_above_emas': sum(1 for ema in ema_values if current_price > ema),
                'ema_sequence': 'Ascending' if ascending else 'Descending' if descending else 'Mixed'
            }
            
        except Exception as e:
            return {'bias': 'Neutral', 'strength': 50, 'error': str(e)}
    
    def _analyze_smart_money_concepts(self, data, current_price):
        """Analyze Smart Money concepts"""
        try:
            # Order Blocks - simplified swing detection
            order_blocks = self._detect_order_blocks(data, current_price)
            
            # Fair Value Gaps (FVG)
            fvg_analysis = self._detect_fair_value_gaps(data, current_price)
            
            # Liquidity zones
            liquidity_analysis = self._analyze_liquidity_zones(data, current_price)
            
            return {
                'order_blocks': order_blocks,
                'fair_value_gaps': fvg_analysis,
                'liquidity_zones': liquidity_analysis,
                'overall_smc_bias': self._determine_smc_bias(order_blocks, fvg_analysis, liquidity_analysis)
            }
            
        except Exception as e:
            return {'error': str(e), 'overall_smc_bias': 'Neutral'}
    
    def _detect_order_blocks(self, data, current_price):
        """Detect Order Blocks using swing analysis"""
        try:
            if len(data) < 20:
                return {'bullish_obs': [], 'bearish_obs': [], 'nearest_ob': None}
            
            lookback = 5
            swing_highs = []
            swing_lows = []
            
            for i in range(lookback, len(data) - lookback):
                # Swing high detection
                is_swing_high = True
                current_high = float(data['High'].iloc[i])
                
                for j in range(i - lookback, i + lookback + 1):
                    if j != i and float(data['High'].iloc[j]) >= current_high:
                        is_swing_high = False
                        break
                
                if is_swing_high:
                    swing_highs.append({'price': current_high, 'index': i})
                
                # Swing low detection
                is_swing_low = True
                current_low = float(data['Low'].iloc[i])
                
                for j in range(i - lookback, i + lookback + 1):
                    if j != i and float(data['Low'].iloc[j]) <= current_low:
                        is_swing_low = False
                        break
                
                if is_swing_low:
                    swing_lows.append({'price': current_low, 'index': i})
            
            # Get recent and relevant order blocks
            bullish_obs = [ob for ob in swing_lows[-10:] if abs(ob['price'] - current_price) / current_price < 0.15]
            bearish_obs = [ob for ob in swing_highs[-10:] if abs(ob['price'] - current_price) / current_price < 0.15]
            
            # Find nearest OB
            all_obs = [(ob['price'], 'bullish') for ob in bullish_obs] + [(ob['price'], 'bearish') for ob in bearish_obs]
            nearest_ob = min(all_obs, key=lambda x: abs(x[0] - current_price)) if all_obs else None
            
            return {
                'bullish_obs': bullish_obs[:5],
                'bearish_obs': bearish_obs[:5],
                'nearest_ob': nearest_ob
            }
            
        except Exception as e:
            return {'bullish_obs': [], 'bearish_obs': [], 'nearest_ob': None}
    
    def _detect_fair_value_gaps(self, data, current_price):
        """Detect Fair Value Gaps"""
        try:
            if len(data) < 5:
                return {'bullish_fvgs': [], 'bearish_fvgs': [], 'nearest_fvg': None}
            
            gaps = []
            
            for i in range(2, len(data) - 1):
                prev_high = float(data['High'].iloc[i-1])
                prev_low = float(data['Low'].iloc[i-1])
                curr_high = float(data['High'].iloc[i])
                curr_low = float(data['Low'].iloc[i])
                curr_close = float(data['Close'].iloc[i])
                
                # Bullish FVG
                if prev_low > curr_high:
                    gap_size = prev_low - curr_high
                    gap_pct = (gap_size / curr_close) * 100
                    if gap_pct > 0.1:
                        gaps.append({
                            'type': 'bullish',
                            'top': prev_low,
                            'bottom': curr_high,
                            'size_pct': gap_pct,
                            'distance_pct': abs((prev_low + curr_high) / 2 - current_price) / current_price * 100
                        })
                
                # Bearish FVG
                if prev_high < curr_low:
                    gap_size = curr_low - prev_high
                    gap_pct = (gap_size / curr_close) * 100
                    if gap_pct > 0.1:
                        gaps.append({
                            'type': 'bearish',
                            'top': curr_low,
                            'bottom': prev_high,
                            'size_pct': gap_pct,
                            'distance_pct': abs((curr_low + prev_high) / 2 - current_price) / current_price * 100
                        })
            
            # Filter relevant gaps
            relevant_gaps = [g for g in gaps[-20:] if g['distance_pct'] < 10 and g['size_pct'] > 0.3]
            
            bullish_fvgs = [g for g in relevant_gaps if g['type'] == 'bullish'][:3]
            bearish_fvgs = [g for g in relevant_gaps if g['type'] == 'bearish'][:3]
            
            nearest_fvg = min(relevant_gaps, key=lambda x: x['distance_pct']) if relevant_gaps else None
            
            return {
                'bullish_fvgs': bullish_fvgs,
                'bearish_fvgs': bearish_fvgs,
                'nearest_fvg': nearest_fvg
            }
            
        except Exception as e:
            return {'bullish_fvgs': [], 'bearish_fvgs': [], 'nearest_fvg': None}
    
    def _analyze_liquidity_zones(self, data, current_price):
        """Analyze liquidity accumulation zones"""
        try:
            # Simple liquidity analysis based on volume and price action
            if 'Volume' not in data.columns:
                return {'high_liquidity_zones': [], 'manipulation_risk': 'Unknown'}
            
            # Find high volume areas
            volume_ma = data['Volume'].rolling(window=20).mean()
            high_volume_threshold = volume_ma.quantile(0.8)
            
            high_liquidity_zones = []
            for i in range(len(data)):
                if data['Volume'].iloc[i] > high_volume_threshold:
                    price_level = (data['High'].iloc[i] + data['Low'].iloc[i]) / 2
                    distance_pct = abs(price_level - current_price) / current_price * 100
                    if distance_pct < 5:  # Within 5%
                        high_liquidity_zones.append({
                            'price': price_level,
                            'volume': data['Volume'].iloc[i],
                            'distance_pct': distance_pct
                        })
            
            # Determine manipulation risk based on current session
            current_hour = datetime.now().hour
            if 8 <= current_hour <= 16:  # London session
                manipulation_risk = 'High'
            elif 13 <= current_hour <= 22:  # US session
                manipulation_risk = 'Very High'
            else:
                manipulation_risk = 'Low'
            
            return {
                'high_liquidity_zones': sorted(high_liquidity_zones, key=lambda x: x['distance_pct'])[:5],
                'manipulation_risk': manipulation_risk
            }
            
        except Exception as e:
            return {'high_liquidity_zones': [], 'manipulation_risk': 'Unknown'}
    
    def _determine_smc_bias(self, order_blocks, fvg_analysis, liquidity_analysis):
        """Determine overall Smart Money bias"""
        bullish_signals = 0
        bearish_signals = 0
        
        # Order Blocks bias
        if len(order_blocks['bullish_obs']) > len(order_blocks['bearish_obs']):
            bullish_signals += 1
        elif len(order_blocks['bearish_obs']) > len(order_blocks['bullish_obs']):
            bearish_signals += 1
        
        # FVG bias
        if len(fvg_analysis['bullish_fvgs']) > len(fvg_analysis['bearish_fvgs']):
            bullish_signals += 1
        elif len(fvg_analysis['bearish_fvgs']) > len(fvg_analysis['bullish_fvgs']):
            bearish_signals += 1
        
        # Nearest important level
        if fvg_analysis['nearest_fvg']:
            if fvg_analysis['nearest_fvg']['type'] == 'bullish':
                bullish_signals += 1
            else:
                bearish_signals += 1
        
        if bullish_signals > bearish_signals:
            return 'Bullish'
        elif bearish_signals > bullish_signals:
            return 'Bearish'
        else:
            return 'Neutral'
    
    def _calculate_institutional_levels(self, data):
        """Calculate key institutional levels"""
        try:
            if len(data) < 20:
                return {'key_levels': [], 'nearest_support': None, 'nearest_resistance': None}
            
            current_price = float(data['Close'].iloc[-1])
            
            # Calculate various timeframe levels
            levels = []
            
            # Daily levels (last 5 days)
            for days_back in range(1, 6):
                if len(data) >= days_back * 24:  # Assuming hourly data
                    start_idx = max(0, len(data) - days_back * 24)
                    end_idx = len(data) - (days_back - 1) * 24
                    day_data = data.iloc[start_idx:end_idx]
                    
                    if not day_data.empty:
                        day_high = day_data['High'].max()
                        day_low = day_data['Low'].min()
                        day_open = day_data['Open'].iloc[0]
                        
                        levels.extend([
                            {'price': day_high, 'type': 'Daily High', 'timeframe': f'D-{days_back}'},
                            {'price': day_low, 'type': 'Daily Low', 'timeframe': f'D-{days_back}'},
                            {'price': day_open, 'type': 'Daily Open', 'timeframe': f'D-{days_back}'}
                        ])
            
            # Weekly levels
            if len(data) >= 168:  # 7 days * 24 hours
                week_data = data.iloc[-168:]
                week_high = week_data['High'].max()
                week_low = week_data['Low'].min()
                week_open = week_data['Open'].iloc[0]
                
                levels.extend([
                    {'price': week_high, 'type': 'Weekly High', 'timeframe': 'W'},
                    {'price': week_low, 'type': 'Weekly Low', 'timeframe': 'W'},
                    {'price': week_open, 'type': 'Weekly Open', 'timeframe': 'W'}
                ])
            
            # Calculate distances and filter relevant levels
            for level in levels:
                level['distance_pct'] = abs(level['price'] - current_price) / current_price * 100
            
            # Filter levels within 10% of current price
            relevant_levels = [l for l in levels if l['distance_pct'] < 10]
            relevant_levels.sort(key=lambda x: x['distance_pct'])
            
            # Find nearest support and resistance
            support_levels = [l for l in relevant_levels if l['price'] < current_price]
            resistance_levels = [l for l in relevant_levels if l['price'] > current_price]
            
            nearest_support = support_levels[0] if support_levels else None
            nearest_resistance = resistance_levels[0] if resistance_levels else None
            
            return {
                'key_levels': relevant_levels[:10],
                'nearest_support': nearest_support,
                'nearest_resistance': nearest_resistance
            }
            
        except Exception as e:
            return {'key_levels': [], 'nearest_support': None, 'nearest_resistance': None}
    
    def _analyze_market_structure(self, data, current_price):
        """Analyze market structure and trend"""
        try:
            if len(data) < 50:
                return {'trend': 'Unknown', 'strength': 50, 'structure_break': False}
            
            # Calculate trend using multiple EMAs
            ema_20 = data['Close'].ewm(span=20).mean()
            ema_50 = data['Close'].ewm(span=50).mean()
            
            current_ema20 = ema_20.iloc[-1]
            current_ema50 = ema_50.iloc[-1]
            
            # Determine trend
            if current_price > current_ema20 > current_ema50:
                trend = 'Strong Uptrend'
                strength = 85
            elif current_price > current_ema20:
                trend = 'Uptrend'
                strength = 70
            elif current_price < current_ema20 < current_ema50:
                trend = 'Strong Downtrend'
                strength = 85
            elif current_price < current_ema20:
                trend = 'Downtrend'
                strength = 70
            else:
                trend = 'Sideways'
                strength = 50
            
            # Check for structure break (simplified)
            recent_highs = data['High'].rolling(window=10).max()
            recent_lows = data['Low'].rolling(window=10).min()
            
            structure_break = False
            if len(data) >= 20:
                prev_high = recent_highs.iloc[-20]
                prev_low = recent_lows.iloc[-20]
                curr_high = recent_highs.iloc[-1]
                curr_low = recent_lows.iloc[-1]
                
                if curr_high > prev_high and curr_low > prev_low:
                    structure_break = True  # Bullish structure break
                elif curr_high < prev_high and curr_low < prev_low:
                    structure_break = True  # Bearish structure break
            
            return {
                'trend': trend,
                'strength': strength,
                'structure_break': structure_break,
                'ema20': current_ema20,
                'ema50': current_ema50
            }
            
        except Exception as e:
            return {'trend': 'Unknown', 'strength': 50, 'structure_break': False}
    
    def _generate_scalp_signals(self, data, current_price):
        """Generate scalping signals"""
        try:
            if len(data) < 20:
                return {'scalp_bias': 'Neutral', 'entry_signals': [], 'scalp_score': 50}
            
            # Fast EMAs for scalping
            ema_8 = data['Close'].ewm(span=8).mean()
            ema_21 = data['Close'].ewm(span=21).mean()
            
            current_ema8 = ema_8.iloc[-1]
            current_ema21 = ema_21.iloc[-1]
            
            # Scalp bias
            if current_price > current_ema8 > current_ema21:
                scalp_bias = 'Bullish'
                scalp_score = 75
            elif current_price < current_ema8 < current_ema21:
                scalp_bias = 'Bearish'
                scalp_score = 75
            else:
                scalp_bias = 'Neutral'
                scalp_score = 50
            
            # Entry signals based on EMA crossovers
            entry_signals = []
            if len(ema_8) >= 2 and len(ema_21) >= 2:
                if ema_8.iloc[-2] <= ema_21.iloc[-2] and ema_8.iloc[-1] > ema_21.iloc[-1]:
                    entry_signals.append({'type': 'Long', 'strength': 'Medium'})
                elif ema_8.iloc[-2] >= ema_21.iloc[-2] and ema_8.iloc[-1] < ema_21.iloc[-1]:
                    entry_signals.append({'type': 'Short', 'strength': 'Medium'})
            
            return {
                'scalp_bias': scalp_bias,
                'entry_signals': entry_signals,
                'scalp_score': scalp_score,
                'ema8': current_ema8,
                'ema21': current_ema21
            }
            
        except Exception as e:
            return {'scalp_bias': 'Neutral', 'entry_signals': [], 'scalp_score': 50}
    
    def _analyze_funding_cvd(self, data, symbol):
        """Analyze funding and CVD for crypto (simplified)"""
        try:
            # Simplified funding analysis based on price action
            if len(data) < 50:
                return {'funding_bias': 'Neutral', 'cvd_trend': 'Neutral', 'recommendation': 'Wait'}
            
            # Estimate funding sentiment from volatility and volume
            volatility = data['Close'].pct_change().std() * 100
            
            if 'Volume' in data.columns:
                volume_trend = data['Volume'].rolling(window=10).mean().iloc[-1] / data['Volume'].rolling(window=10).mean().iloc[-10]
                
                if volatility > 3 and volume_trend > 1.2:
                    funding_bias = 'High Positive'
                    recommendation = 'Watch for long liquidations'
                elif volatility < 1.5 and volume_trend < 0.8:
                    funding_bias = 'Negative'
                    recommendation = 'Potential long opportunity'
                else:
                    funding_bias = 'Neutral'
                    recommendation = 'Wait for clearer signals'
            else:
                funding_bias = 'Unknown'
                recommendation = 'Insufficient data'
            
            return {
                'funding_bias': funding_bias,
                'cvd_trend': 'Estimated from volume',
                'recommendation': recommendation
            }
            
        except Exception as e:
            return {'funding_bias': 'Unknown', 'cvd_trend': 'Unknown', 'recommendation': 'Error in analysis'}
    
    def _analyze_dxy_impact(self, symbol):
        """Analyze DXY impact for forex (simplified)"""
        try:
            # Simplified DXY impact based on USD pairs
            if 'USD' in symbol.upper():
                if symbol.upper().startswith('USD'):
                    return {
                        'dxy_correlation': 'Positive',
                        'impact': 'Strong DXY affects this pair directly',
                        'recommendation': 'Monitor DXY trends closely'
                    }
                else:
                    return {
                        'dxy_correlation': 'Negative',
                        'impact': 'Inverse relationship with DXY',
                        'recommendation': 'Watch for DXY reversals'
                    }
            else:
                return {
                    'dxy_correlation': 'Indirect',
                    'impact': 'Secondary effect through USD crosses',
                    'recommendation': 'Consider DXY as background factor'
                }
                
        except Exception as e:
            return {'dxy_correlation': 'Unknown', 'impact': 'Error in analysis', 'recommendation': 'Manual analysis required'}
    
    def _calculate_ultimate_signal(self, analysis):
        """Calculate the ultimate trading signal by combining all analysis"""
        try:
            bullish_score = 0
            bearish_score = 0
            confidence_factors = 0
            total_weight = 0
            
            # EMA Bias weight: 40% (most important)
            ema_bias = analysis['ema_bias']['bias']
            ema_strength = analysis['ema_bias']['strength']
            
            if ema_strength > 60:  # Only consider strong EMA signals
                if 'Very Bullish' in ema_bias:
                    bullish_score += 90 * 0.4
                    confidence_factors += 2
                elif 'Bullish' in ema_bias:
                    bullish_score += 75 * 0.4
                    confidence_factors += 1.5
                elif 'Very Bearish' in ema_bias:
                    bearish_score += 90 * 0.4
                    confidence_factors += 2
                elif 'Bearish' in ema_bias:
                    bearish_score += 75 * 0.4
                    confidence_factors += 1.5
                total_weight += 0.4
            
            # Smart Money bias weight: 30%
            smc_bias = analysis['smart_money']['overall_smc_bias']
            if smc_bias == 'Bullish':
                bullish_score += 80 * 0.3
                confidence_factors += 1
                total_weight += 0.3
            elif smc_bias == 'Bearish':
                bearish_score += 80 * 0.3
                confidence_factors += 1
                total_weight += 0.3
            
            # Market Structure weight: 20%
            structure = analysis['market_structure']
            if structure['strength'] > 70:  # Only strong trends
                if 'Strong Uptrend' in structure['trend']:
                    bullish_score += 85 * 0.2
                    confidence_factors += 1
                elif 'Uptrend' in structure['trend']:
                    bullish_score += 70 * 0.2
                    confidence_factors += 0.5
                elif 'Strong Downtrend' in structure['trend']:
                    bearish_score += 85 * 0.2
                    confidence_factors += 1
                elif 'Downtrend' in structure['trend']:
                    bearish_score += 70 * 0.2
                    confidence_factors += 0.5
                total_weight += 0.2
            
            # Scalp signals weight: 10%
            scalp = analysis['scalp_signals']
            if scalp['scalp_score'] > 70:
                if scalp['scalp_bias'] == 'Bullish':
                    bullish_score += scalp['scalp_score'] * 0.1
                elif scalp['scalp_bias'] == 'Bearish':
                    bearish_score += scalp['scalp_score'] * 0.1
                total_weight += 0.1
            
            # Only proceed if we have sufficient analysis weight
            if total_weight < 0.5:  # Less than 50% of analysis is meaningful
                return {
                    'signal': 'INSUFFICIENT DATA',
                    'bullish_score': round(bullish_score, 1),
                    'bearish_score': round(bearish_score, 1),
                    'confidence': 0,
                    'risk_level': 'Very High',
                    'recommendations': ['Veri yetersiz - daha fazla analiz gerekli', 'Farklı zaman dilimi deneyin'],
                    'score_breakdown': {'total_weight': total_weight, 'confidence_factors': confidence_factors}
                }
            
            # Normalize scores based on actual weight
            bullish_score = bullish_score / total_weight * 100 if total_weight > 0 else 0
            bearish_score = bearish_score / total_weight * 100 if total_weight > 0 else 0
            
            # Calculate confidence based on signal strength and agreement
            signal_strength = abs(bullish_score - bearish_score)
            base_confidence = min(95, confidence_factors * 25)  # Max confidence from factors
            strength_bonus = signal_strength * 0.5  # Bonus for clear signals
            confidence = min(95, base_confidence + strength_bonus)
            
            # Determine signal with higher thresholds
            score_difference = abs(bullish_score - bearish_score)
            
            if bullish_score > bearish_score:
                if score_difference >= 30 and confidence >= 75:
                    signal = 'STRONG BUY'
                    risk_level = 'Low'
                elif score_difference >= 15 and confidence >= 60:
                    signal = 'BUY'
                    risk_level = 'Medium'
                elif score_difference >= 10:
                    signal = 'WEAK BUY'
                    risk_level = 'High'
                else:
                    signal = 'NEUTRAL'
                    risk_level = 'Medium'
            elif bearish_score > bullish_score:
                if score_difference >= 30 and confidence >= 75:
                    signal = 'STRONG SELL'
                    risk_level = 'Low'
                elif score_difference >= 15 and confidence >= 60:
                    signal = 'SELL'
                    risk_level = 'Medium'
                elif score_difference >= 10:
                    signal = 'WEAK SELL'
                    risk_level = 'High'
                else:
                    signal = 'NEUTRAL'
                    risk_level = 'Medium'
            else:
                signal = 'NEUTRAL'
                risk_level = 'Medium'
            
            # Generate recommendation
            recommendations = []
            if signal in ['STRONG BUY', 'BUY']:
                recommendations.append(f"Alım pozisyonu öneriliyor")
                if analysis['scalp_signals']['entry_signals']:
                    recommendations.append("Scalp fırsatları mevcut")
            elif signal in ['STRONG SELL', 'SELL']:
                recommendations.append(f"Satım pozisyonu öneriliyor")
                if analysis['scalp_signals']['entry_signals']:
                    recommendations.append("Short scalp fırsatları mevcut")
            else:
                recommendations.append("Bekle - net sinyal yok")
                recommendations.append("Daha güçlü onay bekleyin")
            
            # Add asset-specific recommendations
            if analysis['funding_cvd']:
                recommendations.append(f"Funding analizi: {analysis['funding_cvd']['recommendation']}")
            
            if analysis['dxy_impact']:
                recommendations.append(f"DXY etkisi: {analysis['dxy_impact']['recommendation']}")
            
            return {
                'signal': signal,
                'bullish_score': round(bullish_score, 1),
                'bearish_score': round(bearish_score, 1),
                'confidence': round(confidence, 1),
                'risk_level': risk_level,
                'recommendations': recommendations[:3],  # Top 3 recommendations
                'score_breakdown': {
                    'ema_contribution': round(ema_strength * 0.3 if 'Bullish' in ema_bias or 'Bearish' in ema_bias else 0, 1),
                    'smc_contribution': round(75 * 0.25 if smc_bias != 'Neutral' else 0, 1),
                    'structure_contribution': round(structure['strength'] * 0.2 if 'trend' in structure['trend'].lower() else 0, 1),
                    'total_factors': confidence_factors
                }
            }
            
        except Exception as e:
            return {
                'signal': 'ERROR',
                'bullish_score': 0,
                'bearish_score': 0,
                'confidence': 0,
                'risk_level': 'High',
                'recommendations': ['Analysis error occurred'],
                'error': str(e)
            }
    
    def _get_fallback_analysis(self):
        """Fallback analysis when data is insufficient"""
        return {
            'symbol': 'Unknown',
            'current_price': 0,
            'asset_type': 'unknown',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'ema_bias': {'bias': 'Unknown', 'strength': 0},
            'smart_money': {'overall_smc_bias': 'Unknown'},
            'institutional_levels': {'key_levels': []},
            'market_structure': {'trend': 'Unknown', 'strength': 0},
            'scalp_signals': {'scalp_bias': 'Unknown', 'scalp_score': 0},
            'funding_cvd': None,
            'dxy_impact': None,
            'ultimate_signal': {
                'signal': 'NO DATA',
                'bullish_score': 0,
                'bearish_score': 0,
                'confidence': 0,
                'risk_level': 'High',
                'recommendations': ['Insufficient data for analysis']
            }
        }