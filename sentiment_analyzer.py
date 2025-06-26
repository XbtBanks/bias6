import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class SentimentAnalyzer:
    """
    Advanced sentiment analysis using price action, volume, and volatility patterns
    """
    
    def __init__(self):
        self.sentiment_weights = {
            'price_momentum': 0.3,
            'volume_sentiment': 0.25,
            'volatility_analysis': 0.2,
            'institutional_flow': 0.15,
            'market_regime': 0.1
        }
    
    def analyze_market_sentiment(self, data, ema_data):
        """
        Comprehensive market sentiment analysis
        """
        sentiment_components = {
            'price_momentum': self._analyze_price_momentum(data),
            'volume_sentiment': self._analyze_volume_sentiment(data),
            'volatility_analysis': self._analyze_volatility_patterns(data),
            'institutional_flow': self._detect_institutional_flow(data),
            'market_regime': self._identify_market_regime(data, ema_data)
        }
        
        # Calculate weighted sentiment score
        overall_sentiment = self._calculate_overall_sentiment(sentiment_components)
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_components': sentiment_components,
            'sentiment_strength': self._calculate_sentiment_strength(sentiment_components),
            'market_psychology': self._interpret_market_psychology(overall_sentiment, sentiment_components)
        }
    
    def analyze_sentiment(self, data, ema_data, confluence):
        """
        Main sentiment analysis method called by the application
        """
        return self.analyze_market_sentiment(data, ema_data)
    
    def _analyze_price_momentum(self, data):
        """
        Analyze price momentum patterns
        """
        closes = data['Close'].values
        
        # Short-term momentum (5 periods)
        short_momentum = (closes[-1] - closes[-5]) / closes[-5] * 100 if len(closes) >= 5 else 0
        
        # Medium-term momentum (20 periods)
        medium_momentum = (closes[-1] - closes[-20]) / closes[-20] * 100 if len(closes) >= 20 else 0
        
        # Acceleration (momentum of momentum)
        recent_momentum = (closes[-1] - closes[-3]) / closes[-3] * 100 if len(closes) >= 3 else 0
        prev_momentum = (closes[-3] - closes[-6]) / closes[-6] * 100 if len(closes) >= 6 else 0
        acceleration = recent_momentum - prev_momentum
        
        # Price velocity
        price_changes = np.diff(closes[-10:]) if len(closes) >= 10 else np.array([0])
        velocity = np.mean(price_changes) / closes[-1] * 100
        
        momentum_score = (short_momentum * 0.4 + medium_momentum * 0.3 + acceleration * 0.2 + velocity * 0.1)
        
        return {
            'momentum_score': momentum_score,
            'short_term_momentum': short_momentum,
            'medium_term_momentum': medium_momentum,
            'acceleration': acceleration,
            'interpretation': self._interpret_momentum(momentum_score)
        }
    
    def _analyze_volume_sentiment(self, data):
        """
        Analyze volume-based sentiment indicators
        """
        volumes = data['Volume'].values
        closes = data['Close'].values
        
        # Volume-weighted average price vs current price
        if len(volumes) >= 10:
            vwap = np.sum(closes[-10:] * volumes[-10:]) / np.sum(volumes[-10:])
            vwap_sentiment = (closes[-1] - vwap) / vwap * 100
        else:
            vwap_sentiment = 0
        
        # Volume trend analysis
        recent_volume = np.mean(volumes[-5:]) if len(volumes) >= 5 else volumes[-1]
        avg_volume = np.mean(volumes[-20:]) if len(volumes) >= 20 else recent_volume
        volume_trend = (recent_volume - avg_volume) / avg_volume * 100
        
        # On-balance volume approximation
        price_changes = np.diff(closes[-20:]) if len(closes) >= 20 else np.array([0])
        obv_direction = np.sum(volumes[-19:] * np.sign(price_changes)) if len(price_changes) > 0 else 0
        obv_sentiment = obv_direction / np.sum(volumes[-19:]) * 100 if np.sum(volumes[-19:]) > 0 else 0
        
        volume_sentiment_score = (vwap_sentiment * 0.4 + volume_trend * 0.3 + obv_sentiment * 0.3)
        
        return {
            'volume_sentiment_score': volume_sentiment_score,
            'vwap_sentiment': vwap_sentiment,
            'volume_trend': volume_trend,
            'obv_sentiment': obv_sentiment,
            'interpretation': self._interpret_volume_sentiment(volume_sentiment_score)
        }
    
    def _analyze_volatility_patterns(self, data):
        """
        Analyze volatility patterns for sentiment insights
        """
        closes = data['Close'].values
        highs = data['High'].values
        lows = data['Low'].values
        
        # Calculate rolling volatility
        if len(closes) >= 20:
            returns = np.diff(np.log(closes[-20:]))
            volatility = np.std(returns) * np.sqrt(252) * 100  # Annualized volatility
            
            # Compare recent vs historical volatility
            recent_returns = np.diff(np.log(closes[-5:]))
            recent_volatility = np.std(recent_returns) * np.sqrt(252) * 100
            vol_ratio = recent_volatility / volatility if volatility > 0 else 1
        else:
            vol_ratio = 1
            volatility = 0
        
        # True range analysis
        true_ranges = []
        for i in range(1, min(len(highs), 14)):
            tr = max(
                highs[-i] - lows[-i],
                abs(highs[-i] - closes[-i-1]),
                abs(lows[-i] - closes[-i-1])
            )
            true_ranges.append(tr / closes[-i] * 100)
        
        avg_true_range = np.mean(true_ranges) if true_ranges else 0
        
        # Volatility sentiment (higher volatility can indicate uncertainty)
        volatility_sentiment = -10 if vol_ratio > 1.5 else 5 if vol_ratio < 0.7 else 0
        
        return {
            'volatility_sentiment': volatility_sentiment,
            'current_volatility': volatility,
            'volatility_ratio': vol_ratio,
            'average_true_range': avg_true_range,
            'interpretation': self._interpret_volatility(vol_ratio, volatility_sentiment)
        }
    
    def _detect_institutional_flow(self, data):
        """
        Detect potential institutional buying/selling patterns
        """
        volumes = data['Volume'].values
        closes = data['Close'].values
        
        # Large volume bars analysis
        if len(volumes) >= 20:
            volume_threshold = np.mean(volumes[-20:]) * 2  # 2x average volume
            large_volume_bars = volumes[-10:] > volume_threshold
            
            # Price action on large volume
            institutional_score = 0
            for i, is_large_vol in enumerate(large_volume_bars):
                if is_large_vol and i < len(closes) - 10:
                    price_change = (closes[-10+i+1] - closes[-10+i]) / closes[-10+i] * 100
                    institutional_score += price_change
        else:
            institutional_score = 0
        
        # Accumulation/Distribution approximation
        highs = data['High'].values
        lows = data['Low'].values
        if len(closes) >= 10:
            ad_line = 0
            for i in range(-10, -1):
                if highs[i] != lows[i]:
                    money_flow_multiplier = ((closes[i] - lows[i]) - (highs[i] - closes[i])) / (highs[i] - lows[i])
                    money_flow_volume = money_flow_multiplier * volumes[i]
                    ad_line += money_flow_volume
            
            ad_sentiment = ad_line / np.sum(volumes[-10:]) * 100 if np.sum(volumes[-10:]) > 0 else 0
        else:
            ad_sentiment = 0
        
        institutional_flow_score = (institutional_score * 0.6 + ad_sentiment * 0.4)
        
        return {
            'institutional_flow_score': institutional_flow_score,
            'accumulation_distribution': ad_sentiment,
            'large_volume_impact': institutional_score,
            'interpretation': self._interpret_institutional_flow(institutional_flow_score)
        }
    
    def _identify_market_regime(self, data, ema_data):
        """
        Identify current market regime (trending vs ranging)
        """
        closes = data['Close'].values
        
        # EMA spread analysis
        ema_values = [ema_data[key].iloc[-1] for key in ema_data.keys()]
        ema_spread = (max(ema_values) - min(ema_values)) / np.mean(ema_values) * 100
        
        # Trend consistency
        if len(closes) >= 20:
            trend_periods = []
            for i in range(5, 20, 5):
                trend_periods.append((closes[-1] - closes[-i]) / closes[-i] * 100)
            
            trend_consistency = np.std(trend_periods)
        else:
            trend_consistency = 0
        
        # Market regime determination
        if ema_spread > 3 and trend_consistency < 5:
            regime = 'Strong Trending'
            regime_score = 10
        elif ema_spread > 1.5:
            regime = 'Moderate Trending'
            regime_score = 5
        elif ema_spread < 0.5:
            regime = 'Tight Range'
            regime_score = -5
        else:
            regime = 'Ranging'
            regime_score = 0
        
        return {
            'regime': regime,
            'regime_score': regime_score,
            'ema_spread': ema_spread,
            'trend_consistency': trend_consistency,
            'interpretation': f"Market is in {regime.lower()} mode"
        }
    
    def _calculate_overall_sentiment(self, components):
        """
        Calculate weighted overall sentiment score
        """
        overall_score = 0
        for component_name, weight in self.sentiment_weights.items():
            if component_name in components:
                component_score = components[component_name].get(f'{component_name}_score', 0)
                if component_name == 'market_regime':
                    component_score = components[component_name].get('regime_score', 0)
                overall_score += component_score * weight
        
        # Normalize to -100 to +100 scale
        normalized_score = max(-100, min(100, overall_score))
        
        if normalized_score > 30:
            sentiment_label = 'Very Bullish'
        elif normalized_score > 10:
            sentiment_label = 'Bullish'
        elif normalized_score > -10:
            sentiment_label = 'Neutral'
        elif normalized_score > -30:
            sentiment_label = 'Bearish'
        else:
            sentiment_label = 'Very Bearish'
        
        return {
            'score': normalized_score,
            'label': sentiment_label,
            'confidence': min(100, abs(normalized_score) * 2)
        }
    
    def _calculate_sentiment_strength(self, components):
        """
        Calculate sentiment strength based on component alignment
        """
        scores = []
        for component_name in self.sentiment_weights.keys():
            if component_name in components:
                if component_name == 'market_regime':
                    score = components[component_name].get('regime_score', 0)
                else:
                    score = components[component_name].get(f'{component_name}_score', 0)
                scores.append(score)
        
        if not scores:
            return {'strength': 0, 'interpretation': 'Insufficient data'}
        
        # Calculate agreement (low standard deviation = high agreement)
        if len(scores) > 1:
            std_value = np.std(scores)
            agreement = 100 - (std_value * 10)
            agreement = max(0.0, min(100.0, float(agreement)))
        else:
            agreement = 50  # Default moderate agreement for single score
        
        strength_level = 'Very Strong' if agreement > 80 else 'Strong' if agreement > 60 else 'Moderate' if agreement > 40 else 'Weak'
        
        return {
            'strength': agreement,
            'interpretation': f'{strength_level} sentiment alignment'
        }
    
    def _interpret_market_psychology(self, overall_sentiment, components):
        """
        Interpret market psychology based on sentiment analysis
        """
        sentiment_score = overall_sentiment['score']
        sentiment_label = overall_sentiment['label']
        
        psychology_insights = []
        
        # Overall psychology
        if sentiment_score > 50:
            psychology_insights.append("Market shows strong optimism and risk appetite")
        elif sentiment_score > 20:
            psychology_insights.append("Moderate bullish sentiment with selective buying")
        elif sentiment_score > -20:
            psychology_insights.append("Mixed sentiment with uncertainty prevailing")
        elif sentiment_score > -50:
            psychology_insights.append("Bearish sentiment with defensive positioning")
        else:
            psychology_insights.append("Extreme pessimism and risk aversion")
        
        # Volume psychology
        volume_score = components.get('volume_sentiment', {}).get('volume_sentiment_score', 0)
        if volume_score > 10:
            psychology_insights.append("Strong institutional participation supporting moves")
        elif volume_score < -10:
            psychology_insights.append("Weak volume suggests lack of conviction")
        
        # Volatility psychology
        vol_ratio = components.get('volatility_analysis', {}).get('volatility_ratio', 1)
        if vol_ratio > 1.5:
            psychology_insights.append("High volatility indicates emotional trading")
        elif vol_ratio < 0.7:
            psychology_insights.append("Low volatility suggests complacency or accumulation")
        
        return {
            'primary_psychology': sentiment_label,
            'insights': psychology_insights,
            'market_mood': self._determine_market_mood(sentiment_score, vol_ratio)
        }
    
    def _determine_market_mood(self, sentiment_score, volatility_ratio):
        """
        Determine overall market mood
        """
        if sentiment_score > 30 and volatility_ratio < 1.2:
            return "Confident Bullish"
        elif sentiment_score > 30 and volatility_ratio > 1.5:
            return "Euphoric/Overextended"
        elif sentiment_score < -30 and volatility_ratio > 1.5:
            return "Panic/Fear"
        elif sentiment_score < -30 and volatility_ratio < 1.2:
            return "Despair/Capitulation"
        elif abs(sentiment_score) < 10:
            return "Uncertain/Sideways"
        else:
            return "Transitional"
    
    def _interpret_momentum(self, score):
        """Interpret momentum score"""
        if score > 5:
            return "Strong positive momentum"
        elif score > 1:
            return "Moderate positive momentum"
        elif score > -1:
            return "Neutral momentum"
        elif score > -5:
            return "Moderate negative momentum"
        else:
            return "Strong negative momentum"
    
    def _interpret_volume_sentiment(self, score):
        """Interpret volume sentiment score"""
        if score > 10:
            return "Strong buying pressure"
        elif score > 3:
            return "Moderate buying interest"
        elif score > -3:
            return "Balanced volume activity"
        elif score > -10:
            return "Moderate selling pressure"
        else:
            return "Strong selling pressure"
    
    def _interpret_volatility(self, ratio, sentiment):
        """Interpret volatility patterns"""
        if ratio > 1.5:
            return "High volatility - uncertainty/emotion"
        elif ratio > 1.2:
            return "Elevated volatility - increased activity"
        elif ratio < 0.7:
            return "Low volatility - potential breakout setup"
        else:
            return "Normal volatility levels"
    
    def _interpret_institutional_flow(self, score):
        """Interpret institutional flow score"""
        if score > 5:
            return "Institutional accumulation detected"
        elif score > 1:
            return "Moderate institutional buying"
        elif score > -1:
            return "Neutral institutional activity"
        elif score > -5:
            return "Moderate institutional selling"
        else:
            return "Institutional distribution detected"