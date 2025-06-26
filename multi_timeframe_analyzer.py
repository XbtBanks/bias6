import pandas as pd
import numpy as np
from ema_calculator import EMACalculator
from bias_analyzer import BiasAnalyzer

class MultiTimeframeAnalyzer:
    """
    Multi-Timeframe EMA Bias Analyzer for higher accuracy signals
    
    Analyzes 4 timeframes simultaneously to find confluence:
    - Higher timeframe trend direction
    - Current timeframe entry signals
    - Lower timeframe precision entries
    """
    
    def __init__(self):
        self.ema_calculator = EMACalculator()
        self.bias_analyzer = BiasAnalyzer([45, 89, 144, 200, 276])
        
        # Timeframe hierarchy for different base intervals
        self.timeframe_maps = {
            '15m': ['1h', '15m', '5m', '1m'],
            '1h': ['4h', '1h', '15m', '5m'],
            '4h': ['1d', '4h', '1h', '15m'],
            '1d': ['1w', '1d', '4h', '1h']
        }
    
    def analyze_multi_timeframe_bias(self, symbol, base_interval, data_fetcher):
        """
        Analyze bias across multiple timeframes for confluence
        
        Args:
            symbol (str): Trading symbol
            base_interval (str): Base analysis interval
            data_fetcher: Data fetcher instance
            
        Returns:
            dict: Multi-timeframe analysis results
        """
        try:
            # Get timeframe hierarchy
            timeframes = self.timeframe_maps.get(base_interval, ['4h', '1h', '15m', '5m'])
            
            timeframe_results = {}
            confluence_score = 0
            trend_alignment = 0
            
            for i, tf in enumerate(timeframes):
                try:
                    # Get data for this timeframe
                    tf_data = data_fetcher.get_klines(symbol, tf, period='3mo')
                    
                    if tf_data is None or len(tf_data) < 276:
                        continue
                    
                    # Calculate EMA bias for this timeframe
                    bias_result = self.bias_analyzer.analyze_bias(tf_data['Close'])
                    
                    # Weight based on timeframe importance
                    weight = self._get_timeframe_weight(i)
                    
                    timeframe_results[tf] = {
                        'bias': bias_result['current_bias'],
                        'strength': bias_result['bias_strength'],
                        'weight': weight,
                        'weighted_score': bias_result['bias_strength'] * weight
                    }
                    
                    # Calculate confluence
                    if bias_result['current_bias'] == 'bullish':
                        confluence_score += weight
                        trend_alignment += weight
                    elif bias_result['current_bias'] == 'bearish':
                        confluence_score += weight
                        trend_alignment -= weight
                    
                except Exception as e:
                    continue
            
            # Calculate final scores
            max_weight = sum([self._get_timeframe_weight(i) for i in range(len(timeframes))])
            confluence_percentage = (confluence_score / max_weight * 100) if max_weight > 0 else 0
            trend_direction = 'bullish' if trend_alignment > 0 else 'bearish' if trend_alignment < 0 else 'neutral'
            
            return {
                'timeframe_results': timeframe_results,
                'confluence_score': confluence_percentage,
                'trend_direction': trend_direction,
                'signal_strength': self._calculate_signal_strength(confluence_percentage, timeframe_results),
                'entry_confidence': self._calculate_entry_confidence(timeframe_results),
                'recommendation': self._generate_mtf_recommendation(confluence_percentage, trend_direction)
            }
            
        except Exception as e:
            return self._get_fallback_mtf_analysis()
    
    def _get_timeframe_weight(self, index):
        """
        Get weight for timeframe based on hierarchy position
        Higher timeframes get more weight
        """
        weights = [0.4, 0.3, 0.2, 0.1]  # Higher TF = more weight
        return weights[index] if index < len(weights) else 0.05
    
    def _calculate_signal_strength(self, confluence_score, timeframe_results):
        """
        Calculate overall signal strength from multi-timeframe analysis
        """
        if confluence_score >= 85:
            return 'very_strong'
        elif confluence_score >= 70:
            return 'strong'
        elif confluence_score >= 55:
            return 'moderate'
        else:
            return 'weak'
    
    def _calculate_entry_confidence(self, timeframe_results):
        """
        Calculate entry confidence based on timeframe alignment
        """
        if not timeframe_results:
            return 0
        
        # Check alignment between timeframes
        biases = [tf['bias'] for tf in timeframe_results.values()]
        strengths = [tf['strength'] for tf in timeframe_results.values()]
        
        # Count aligned timeframes
        bullish_count = biases.count('bullish')
        bearish_count = biases.count('bearish')
        total_count = len(biases)
        
        # Calculate alignment percentage
        alignment = max(bullish_count, bearish_count) / total_count if total_count > 0 else 0
        
        # Factor in average strength
        avg_strength = np.mean(strengths) if strengths else 0
        
        # Combine alignment and strength
        confidence = (alignment * 0.7 + (avg_strength / 100) * 0.3) * 100
        
        return min(confidence, 100.0)
    
    def _generate_mtf_recommendation(self, confluence_score, trend_direction):
        """
        Generate trading recommendation based on multi-timeframe analysis
        """
        if confluence_score >= 80 and trend_direction != 'neutral':
            return {
                'action': 'strong_buy' if trend_direction == 'bullish' else 'strong_sell',
                'confidence': 'high',
                'reasoning': f'Güçlü {trend_direction} trend - tüm timeframe\'ler uyumlu'
            }
        elif confluence_score >= 65 and trend_direction != 'neutral':
            return {
                'action': 'buy' if trend_direction == 'bullish' else 'sell',
                'confidence': 'medium',
                'reasoning': f'Orta güçlü {trend_direction} trend - çoğu timeframe uyumlu'
            }
        elif confluence_score >= 50:
            return {
                'action': 'weak_buy' if trend_direction == 'bullish' else 'weak_sell',
                'confidence': 'low',
                'reasoning': 'Zayıf sinyal - dikkatli pozisyon'
            }
        else:
            return {
                'action': 'wait',
                'confidence': 'very_low',
                'reasoning': 'Timeframe\'ler uyumsuz - bekle'
            }
    
    def _get_fallback_mtf_analysis(self):
        """
        Fallback analysis when multi-timeframe fails
        """
        return {
            'timeframe_results': {},
            'confluence_score': 50,
            'trend_direction': 'neutral',
            'signal_strength': 'weak',
            'entry_confidence': 30,
            'recommendation': {
                'action': 'wait',
                'confidence': 'low',
                'reasoning': 'Multi-timeframe analizi başarısız'
            }
        }
    
    def get_timeframe_summary(self, mtf_analysis):
        """
        Get summary of multi-timeframe analysis for display
        """
        try:
            tf_results = mtf_analysis['timeframe_results']
            
            summary = {
                'higher_tf_trend': 'unknown',
                'current_tf_bias': 'unknown',
                'lower_tf_entry': 'unknown',
                'alignment_strength': mtf_analysis['confluence_score']
            }
            
            timeframes = list(tf_results.keys())
            
            if len(timeframes) >= 1:
                summary['higher_tf_trend'] = tf_results[timeframes[0]]['bias']
            if len(timeframes) >= 2:
                summary['current_tf_bias'] = tf_results[timeframes[1]]['bias']
            if len(timeframes) >= 3:
                summary['lower_tf_entry'] = tf_results[timeframes[2]]['bias']
            
            return summary
            
        except Exception:
            return {
                'higher_tf_trend': 'unknown',
                'current_tf_bias': 'unknown', 
                'lower_tf_entry': 'unknown',
                'alignment_strength': 0
            }