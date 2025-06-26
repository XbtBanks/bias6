import pandas as pd
import numpy as np

class EMACalculator:
    """
    Exponential Moving Average Calculator
    
    This class provides methods to calculate EMAs using different approaches
    and handles edge cases for financial data analysis.
    """
    
    def __init__(self):
        pass
    
    def calculate_ema(self, prices, period, smoothing_factor=2):
        """
        Calculate Exponential Moving Average
        
        Args:
            prices (pd.Series): Price data series
            period (int): EMA period
            smoothing_factor (float): Smoothing factor (default: 2)
            
        Returns:
            pd.Series: EMA values
        """
        if len(prices) < period:
            return pd.Series([np.nan] * len(prices), index=prices.index)
        
        # Calculate multiplier
        multiplier = smoothing_factor / (period + 1)
        
        # Initialize EMA series
        ema = pd.Series(index=prices.index, dtype=float)
        
        # First EMA value is SMA of first 'period' values
        ema.iloc[period-1] = prices.iloc[:period].mean()
        
        # Calculate subsequent EMA values
        for i in range(period, len(prices)):
            ema.iloc[i] = (prices.iloc[i] * multiplier) + (ema.iloc[i-1] * (1 - multiplier))
        
        return ema
    
    def calculate_multiple_emas(self, prices, periods):
        """
        Calculate multiple EMAs at once
        
        Args:
            prices (pd.Series): Price data series
            periods (list): List of EMA periods
            
        Returns:
            dict: Dictionary with EMA period as key and EMA series as value
        """
        emas = {}
        for period in periods:
            emas[f"EMA_{period}"] = self.calculate_ema(prices, period)
        
        return emas
    
    def get_ema_crossovers(self, short_ema, long_ema):
        """
        Detect EMA crossovers
        
        Args:
            short_ema (pd.Series): Shorter period EMA
            long_ema (pd.Series): Longer period EMA
            
        Returns:
            dict: Dictionary with bullish and bearish crossover points
        """
        # Calculate the difference
        diff = short_ema - long_ema
        
        # Find crossovers
        bullish_crossovers = []
        bearish_crossovers = []
        
        for i in range(1, len(diff)):
            if diff.iloc[i-1] < 0 and diff.iloc[i] > 0:
                # Bullish crossover (short EMA crosses above long EMA)
                bullish_crossovers.append(diff.index[i])
            elif diff.iloc[i-1] > 0 and diff.iloc[i] < 0:
                # Bearish crossover (short EMA crosses below long EMA)
                bearish_crossovers.append(diff.index[i])
        
        return {
            'bullish_crossovers': bullish_crossovers,
            'bearish_crossovers': bearish_crossovers
        }
    
    def calculate_ema_slope(self, ema_series, lookback_period=5):
        """
        Calculate EMA slope to determine trend direction
        
        Args:
            ema_series (pd.Series): EMA data series
            lookback_period (int): Period to calculate slope over
            
        Returns:
            pd.Series: Slope values
        """
        slopes = pd.Series(index=ema_series.index, dtype=float)
        
        for i in range(lookback_period, len(ema_series)):
            # Calculate slope using linear regression over lookback period
            y_values = ema_series.iloc[i-lookback_period:i+1].values
            x_values = np.arange(len(y_values))
            
            # Simple slope calculation
            slope = (y_values[-1] - y_values[0]) / (len(y_values) - 1)
            slopes.iloc[i] = slope
        
        return slopes
    
    def get_ema_support_resistance(self, prices, ema_series, tolerance=0.02):
        """
        Identify support and resistance levels based on EMA
        
        Args:
            prices (pd.Series): Price data
            ema_series (pd.Series): EMA data
            tolerance (float): Tolerance for support/resistance identification
            
        Returns:
            dict: Support and resistance levels
        """
        support_levels = []
        resistance_levels = []
        
        for i in range(1, len(prices)):
            price_ema_diff = abs(prices.iloc[i] - ema_series.iloc[i]) / ema_series.iloc[i]
            
            if price_ema_diff <= tolerance:
                if prices.iloc[i] >= ema_series.iloc[i]:
                    # Price bounced off EMA from above (resistance)
                    resistance_levels.append({
                        'date': prices.index[i],
                        'level': ema_series.iloc[i],
                        'price': prices.iloc[i]
                    })
                else:
                    # Price bounced off EMA from below (support)
                    support_levels.append({
                        'date': prices.index[i],
                        'level': ema_series.iloc[i],
                        'price': prices.iloc[i]
                    })
        
        return {
            'support_levels': support_levels,
            'resistance_levels': resistance_levels
        }
