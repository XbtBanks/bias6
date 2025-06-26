import pandas as pd
import numpy as np
from ema_calculator import EMACalculator

class BiasAnalyzer:
    """
    Bias Analyzer for EMA-based market bias determination
    
    This class analyzes the relationship between multiple EMAs to determine
    market bias (bullish, bearish, or neutral) and calculate bias strength.
    """
    
    def __init__(self, ema_periods):
        """
        Initialize the bias analyzer
        
        Args:
            ema_periods (list): List of EMA periods in ascending order
        """
        self.ema_periods = sorted(ema_periods)  # Ensure periods are sorted
        self.ema_calculator = EMACalculator()
    
    def analyze_bias(self, prices, ema_data=None):
        """
        Analyze market bias based on EMA relationships
        
        Args:
            prices (pd.Series): Price data
            ema_data (dict): Pre-calculated EMA data (optional)
            
        Returns:
            dict: Bias analysis results
        """
        # Calculate EMAs if not provided
        if ema_data is None:
            ema_data = self.ema_calculator.calculate_multiple_emas(prices, self.ema_periods)
        
        # Analyze bias for each time point
        bias_history = []
        bias_strength_history = []
        aligned_emas_history = []
        
        # Get the length of valid data (excluding NaN values)
        valid_length = len(prices)
        for period in self.ema_periods:
            ema_key = f"EMA_{period}"
            valid_start = ema_data[ema_key].first_valid_index()
            if valid_start is not None:
                valid_length = min(valid_length, len(prices.loc[valid_start:]))
        
        # Analyze bias for each valid time point
        for i in range(len(prices)):
            bias_result = self._calculate_point_bias(ema_data, i)
            bias_history.append(bias_result['bias'])
            bias_strength_history.append(bias_result['strength'])
            aligned_emas_history.append(bias_result['aligned_emas'])
        
        # Get current values (last valid point)
        current_bias = bias_history[-1] if bias_history else "Neutral"
        current_strength = bias_strength_history[-1] if bias_strength_history else 0
        current_aligned = aligned_emas_history[-1] if aligned_emas_history else 0
        
        return {
            'overall_bias': current_bias.lower() if isinstance(current_bias, str) else 'neutral',
            'current_bias': current_bias.lower() if isinstance(current_bias, str) else 'neutral',
            'bias_strength': current_strength,
            'aligned_emas': current_aligned,
            'bias_history': bias_history,
            'bias_strength_history': bias_strength_history,
            'aligned_emas_history': aligned_emas_history
        }
    
    def _calculate_point_bias(self, ema_data, index):
        """
        Calculate bias for a specific time point
        
        Args:
            ema_data (dict): EMA data dictionary
            index (int): Time point index
            
        Returns:
            dict: Bias calculation results for the point
        """
        # Check if we have valid data for all EMAs at this point
        ema_values = []
        for period in self.ema_periods:
            # Support both period keys (45) and EMA_period keys (EMA_45)
            ema_key = period if period in ema_data else f"EMA_{period}"
            
            if ema_key in ema_data and index < len(ema_data[ema_key]) and not pd.isna(ema_data[ema_key].iloc[index]):
                ema_values.append(ema_data[ema_key].iloc[index])
            else:
                # Not enough data for this point
                return {'bias': 'Neutral', 'strength': 0, 'aligned_emas': 0}
        
        if len(ema_values) < len(self.ema_periods):
            return {'bias': 'Neutral', 'strength': 0, 'aligned_emas': 0}
        
        # Count bullish and bearish alignments
        bullish_alignments = 0
        bearish_alignments = 0
        total_comparisons = len(self.ema_periods) - 1
        
        for i in range(total_comparisons):
            shorter_ema = ema_values[i]
            longer_ema = ema_values[i + 1]
            
            if shorter_ema > longer_ema:
                bullish_alignments += 1
            elif shorter_ema < longer_ema:
                bearish_alignments += 1
        
        # Determine bias
        if bullish_alignments > bearish_alignments:
            bias = "Bullish"
            aligned_emas = bullish_alignments
        elif bearish_alignments > bullish_alignments:
            bias = "Bearish"
            aligned_emas = bearish_alignments
        else:
            bias = "Neutral"
            aligned_emas = 0
        
        # Calculate strength as percentage of aligned EMAs
        strength = (aligned_emas / total_comparisons) * 100 if total_comparisons > 0 else 0
        
        return {
            'bias': bias,
            'strength': strength,
            'aligned_emas': aligned_emas
        }
    
    def get_bias_signals(self, prices, ema_data=None):
        """
        Get bias change signals (when bias switches from one state to another)
        
        Args:
            prices (pd.Series): Price data
            ema_data (dict): Pre-calculated EMA data (optional)
            
        Returns:
            dict: Bias change signals
        """
        if ema_data is None:
            ema_data = self.ema_calculator.calculate_multiple_emas(prices, self.ema_periods)
        
        bias_analysis = self.analyze_bias(prices, ema_data)
        bias_history = bias_analysis['bias_history']
        
        signals = {
            'bullish_signals': [],
            'bearish_signals': [],
            'neutral_signals': []
        }
        
        # Find bias changes
        for i in range(1, len(bias_history)):
            prev_bias = bias_history[i-1]
            curr_bias = bias_history[i]
            
            if prev_bias != curr_bias:
                signal_date = prices.index[i]
                
                if curr_bias == "Bullish":
                    signals['bullish_signals'].append(signal_date)
                elif curr_bias == "Bearish":
                    signals['bearish_signals'].append(signal_date)
                else:
                    signals['neutral_signals'].append(signal_date)
        
        return signals
    
    def calculate_bias_divergence(self, prices, ema_data=None):
        """
        Calculate divergence between price and EMA bias
        
        Args:
            prices (pd.Series): Price data
            ema_data (dict): Pre-calculated EMA data (optional)
            
        Returns:
            dict: Divergence analysis
        """
        if ema_data is None:
            ema_data = self.ema_calculator.calculate_multiple_emas(prices, self.ema_periods)
        
        bias_analysis = self.analyze_bias(prices, ema_data)
        bias_history = bias_analysis['bias_history']
        
        # Calculate price momentum (simple price change over period)
        price_momentum = prices.pct_change(periods=5).fillna(0)
        
        divergences = []
        
        for i in range(5, len(prices)):
            price_trend = "Up" if price_momentum.iloc[i] > 0 else "Down"
            ema_bias = bias_history[i]
            
            # Check for divergence
            if (price_trend == "Up" and ema_bias == "Bearish") or \
               (price_trend == "Down" and ema_bias == "Bullish"):
                divergences.append({
                    'date': prices.index[i],
                    'type': 'bearish' if price_trend == "Up" else 'bullish',
                    'price_trend': price_trend,
                    'ema_bias': ema_bias
                })
        
        return divergences
    
    def get_bias_statistics(self, prices, ema_data=None):
        """
        Get statistical summary of bias analysis
        
        Args:
            prices (pd.Series): Price data
            ema_data (dict): Pre-calculated EMA data (optional)
            
        Returns:
            dict: Bias statistics
        """
        if ema_data is None:
            ema_data = self.ema_calculator.calculate_multiple_emas(prices, self.ema_periods)
        
        bias_analysis = self.analyze_bias(prices, ema_data)
        bias_history = bias_analysis['bias_history']
        strength_history = bias_analysis['bias_strength_history']
        
        # Count bias occurrences
        bias_counts = {
            'Bullish': bias_history.count('Bullish'),
            'Bearish': bias_history.count('Bearish'),
            'Neutral': bias_history.count('Neutral')
        }
        
        total_points = len(bias_history)
        
        # Calculate percentages
        bias_percentages = {
            bias: (count / total_points) * 100 if total_points > 0 else 0
            for bias, count in bias_counts.items()
        }
        
        # Calculate average strength
        valid_strengths = [s for s in strength_history if s > 0]
        avg_strength = np.mean(valid_strengths) if valid_strengths else 0
        
        return {
            'bias_counts': bias_counts,
            'bias_percentages': bias_percentages,
            'average_strength': avg_strength,
            'total_data_points': total_points,
            'strongest_bias_period': max(strength_history) if strength_history else 0
        }
