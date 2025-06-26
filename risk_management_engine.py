import pandas as pd
import numpy as np
import streamlit as st

class RiskManagementEngine:
    """
    Advanced risk management and position sizing calculator
    """
    
    def __init__(self):
        self.risk_levels = {
            'conservative': 0.5,
            'moderate': 1.0,
            'aggressive': 1.0,
            'very_aggressive': 1.0
        }
    
    def calculate_position_parameters(self, data, ema_data, confluence_score, market_structure):
        """
        Calculate comprehensive position parameters including entry, stop loss, take profit
        """
        current_price = data['Close'].iloc[-1]
        atr = self._calculate_atr(data)
        
        # Determine risk profile based on confluence and market structure
        risk_profile = self._determine_risk_profile(confluence_score, market_structure)
        
        # Calculate dynamic stop loss based on market structure
        stop_loss_data = self._calculate_dynamic_stop_loss(data, ema_data, market_structure, atr)
        
        # Calculate take profit levels
        take_profit_data = self._calculate_take_profit_levels(current_price, stop_loss_data, market_structure, atr)
        
        # Position sizing
        position_size_data = self._calculate_position_sizing(current_price, stop_loss_data, risk_profile)
        
        return {
            'entry_price': current_price,
            'stop_loss': stop_loss_data,
            'take_profit': take_profit_data,
            'position_sizing': position_size_data,
            'risk_profile': risk_profile,
            'atr': atr,
            'risk_reward_analysis': self._analyze_risk_reward(current_price, stop_loss_data, take_profit_data)
        }
    
    def _calculate_atr(self, data, period=14):
        """
        Calculate Average True Range for volatility-based stops
        """
        try:
            high = data['High'].values
            low = data['Low'].values
            close = data['Close'].values
            
            # Calculate True Range
            tr_values = []
            for i in range(1, len(high)):
                tr = max(
                    high[i] - low[i],
                    abs(high[i] - close[i-1]),
                    abs(low[i] - close[i-1])
                )
                tr_values.append(tr)
            
            # Calculate ATR
            if len(tr_values) >= period:
                atr = np.mean(tr_values[-period:])
                return atr
            else:
                return high[-1] - low[-1]
        except:
            return data['High'].values[-1] - data['Low'].values[-1]
    
    def _determine_risk_profile(self, confluence_score, market_structure):
        """
        Determine risk profile based on signal quality
        """
        trend_strength = market_structure.get('trend_strength', {}).get('strength_score', 50)
        breakout_prob = market_structure.get('breakout_probability', {}).get('probability', 50)
        
        combined_score = (confluence_score + trend_strength + breakout_prob) / 3
        
        if combined_score > 80:
            return 'very_aggressive'
        elif combined_score > 65:
            return 'aggressive'
        elif combined_score > 50:
            return 'moderate'
        else:
            return 'conservative'
    
    def _calculate_dynamic_stop_loss(self, data, ema_data, market_structure, atr):
        """
        Calculate dynamic stop loss using multiple methods
        """
        current_price = data['Close'].iloc[-1]
        
        # Method 1: ATR-based stop
        atr_multiplier = 2.0
        atr_stop_long = current_price - (atr * atr_multiplier)
        atr_stop_short = current_price + (atr * atr_multiplier)
        
        # Method 2: EMA-based stop
        ema_45 = ema_data['EMA_45'].iloc[-1]
        ema_89 = ema_data['EMA_89'].iloc[-1]
        
        # Method 3: Support/Resistance based stop
        support_level = market_structure.get('support_resistance', {}).get('nearest_support')
        resistance_level = market_structure.get('support_resistance', {}).get('nearest_resistance')
        
        # Method 4: Previous swing points
        swing_low = data['Low'].iloc[-20:].min()
        swing_high = data['High'].iloc[-20:].max()
        
        # Determine bias direction and optimal stop
        ema_bias = 'bullish' if ema_45 > ema_89 else 'bearish'
        
        if ema_bias == 'bullish':
            # For long positions
            stop_options = [atr_stop_long, ema_45, ema_89]
            if support_level:
                stop_options.append(support_level * 0.995)  # 0.5% buffer below support
            stop_options.append(swing_low * 0.995)
            
            # Choose the highest stop (least risk)
            valid_stops = [s for s in stop_options if s < current_price * 0.95]
            optimal_stop = max(valid_stops) if valid_stops else current_price * 0.98  # Fallback to 2% stop
            stop_method = 'Long Position Stop'
            
        else:
            # For short positions
            stop_options = [atr_stop_short, ema_45, ema_89]
            if resistance_level:
                stop_options.append(resistance_level * 1.005)  # 0.5% buffer above resistance
            stop_options.append(swing_high * 1.005)
            
            # Choose the lowest stop (least risk)
            valid_stops = [s for s in stop_options if s > current_price * 1.05]
            optimal_stop = min(valid_stops) if valid_stops else current_price * 1.02  # Fallback to 2% stop
            stop_method = 'Short Position Stop'
        
        risk_percentage = abs(current_price - optimal_stop) / current_price * 100
        
        return {
            'price': optimal_stop,
            'method': stop_method,
            'risk_percentage': risk_percentage,
            'atr_based': atr_stop_long if ema_bias == 'bullish' else atr_stop_short,
            'ema_based': ema_45,
            'structure_based': support_level if ema_bias == 'bullish' else resistance_level
        }
    
    def _calculate_take_profit_levels(self, entry_price, stop_loss_data, market_structure, atr):
        """
        Calculate multiple take profit levels
        """
        stop_price = stop_loss_data['price']
        risk_amount = abs(entry_price - stop_price)
        
        # Resistance/Support levels for targets
        resistance = market_structure.get('support_resistance', {}).get('nearest_resistance')
        support = market_structure.get('support_resistance', {}).get('nearest_support')
        
        # ATR-based targets
        atr_target_1 = entry_price + (atr * 1.5) if entry_price > stop_price else entry_price - (atr * 1.5)
        atr_target_2 = entry_price + (atr * 3.0) if entry_price > stop_price else entry_price - (atr * 3.0)
        
        # Risk-reward based targets (adjusted to 1.5R standard)
        rr_1_target = entry_price + (risk_amount * 1.5) if entry_price > stop_price else entry_price - (risk_amount * 1.5)
        rr_2_target = entry_price + (risk_amount * 2.0) if entry_price > stop_price else entry_price - (risk_amount * 2.0)
        rr_3_target = entry_price + (risk_amount * 3.0) if entry_price > stop_price else entry_price - (risk_amount * 3.0)
        
        # Choose optimal targets
        targets = []
        
        if entry_price > stop_price:  # Long position
            target_1 = min(rr_1_target, resistance * 0.995) if resistance else rr_1_target
            target_2 = min(rr_2_target, atr_target_2) if resistance else rr_2_target
            target_3 = rr_3_target
        else:  # Short position
            target_1 = max(rr_1_target, support * 1.005) if support else rr_1_target
            target_2 = max(rr_2_target, atr_target_2) if support else rr_2_target
            target_3 = rr_3_target
        
        return {
            'target_1': {
                'price': target_1,
                'risk_reward': abs(target_1 - entry_price) / risk_amount,
                'percentage': 40  # 40% position close
            },
            'target_2': {
                'price': target_2,
                'risk_reward': abs(target_2 - entry_price) / risk_amount,
                'percentage': 35  # 35% position close
            },
            'target_3': {
                'price': target_3,
                'risk_reward': abs(target_3 - entry_price) / risk_amount,
                'percentage': 25  # 25% position close (trailing stop)
            }
        }
    
    def _calculate_position_sizing(self, entry_price, stop_loss_data, risk_profile):
        """
        Calculate position sizing based on risk management
        """
        account_sizes = [1000, 5000, 10000, 25000, 50000, 100000]  # Different account sizes
        max_risk_percentage = self.risk_levels[risk_profile]
        
        stop_price = stop_loss_data['price']
        risk_per_share = abs(entry_price - stop_price)
        
        position_sizes = {}
        
        for account_size in account_sizes:
            max_risk_amount = account_size * (max_risk_percentage / 100)
            position_size = max_risk_amount / risk_per_share if risk_per_share > 0 else 0
            
            position_sizes[f"${account_size:,}"] = {
                'position_size': round(position_size, 2),
                'risk_amount': round(max_risk_amount, 2),
                'position_value': round(position_size * entry_price, 2),
                'position_percentage': round((position_size * entry_price) / account_size * 100, 1)
            }
        
        return {
            'risk_profile': risk_profile,
            'max_risk_percentage': max_risk_percentage,
            'by_account_size': position_sizes,
            'risk_per_unit': risk_per_share
        }
    
    def _analyze_risk_reward(self, entry_price, stop_loss_data, take_profit_data):
        """
        Analyze risk-reward characteristics
        """
        stop_price = stop_loss_data['price']
        risk_amount = abs(entry_price - stop_price)
        
        target_1 = take_profit_data['target_1']['price']
        target_2 = take_profit_data['target_2']['price']
        target_3 = take_profit_data['target_3']['price']
        
        # Calculate weighted average reward
        weighted_reward = (
            abs(target_1 - entry_price) * 0.4 +
            abs(target_2 - entry_price) * 0.35 +
            abs(target_3 - entry_price) * 0.25
        )
        
        avg_risk_reward = weighted_reward / risk_amount if risk_amount > 0 else 0
        
        # Probability-adjusted returns
        win_probability = self._estimate_win_probability(avg_risk_reward)
        expected_return = (win_probability * weighted_reward) - ((1 - win_probability) * risk_amount)
        
        return {
            'average_risk_reward': round(avg_risk_reward, 2),
            'estimated_win_probability': round(win_probability * 100, 1),
            'expected_return_percentage': round((expected_return / abs(entry_price - stop_price)) * 100, 1),
            'trade_quality': self._assess_trade_quality(avg_risk_reward, win_probability)
        }
    
    def _estimate_win_probability(self, risk_reward_ratio):
        """
        Estimate win probability based on risk-reward ratio and typical trading statistics
        """
        # Base probability starts at 50%
        base_prob = 0.50
        
        # Adjust based on risk-reward ratio
        if risk_reward_ratio >= 3.0:
            return min(0.85, base_prob + 0.25)
        elif risk_reward_ratio >= 2.0:
            return min(0.75, base_prob + 0.15)
        elif risk_reward_ratio >= 1.5:
            return min(0.65, base_prob + 0.10)
        elif risk_reward_ratio >= 1.0:
            return base_prob
        else:
            return max(0.30, base_prob - 0.15)
    
    def _assess_trade_quality(self, risk_reward, win_probability):
        """
        Assess overall trade quality
        """
        if risk_reward >= 2.5 and win_probability >= 0.65:
            return 'Excellent'
        elif risk_reward >= 2.0 and win_probability >= 0.55:
            return 'Very Good'
        elif risk_reward >= 1.5 and win_probability >= 0.50:
            return 'Good'
        elif risk_reward >= 1.0 and win_probability >= 0.45:
            return 'Fair'
        else:
            return 'Poor'