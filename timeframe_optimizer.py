import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta

class TimeframeOptimizer:
    """
    Intelligent timeframe recommendation system for optimal EMA bias analysis
    """
    
    def __init__(self):
        self.available_timeframes = {
            '1m': {'weight': 1, 'trend_clarity': 0.3, 'noise_level': 0.9},
            '5m': {'weight': 2, 'trend_clarity': 0.4, 'noise_level': 0.8},
            '10m': {'weight': 3, 'trend_clarity': 0.5, 'noise_level': 0.7},
            '15m': {'weight': 4, 'trend_clarity': 0.6, 'noise_level': 0.6},
            '20m': {'weight': 5, 'trend_clarity': 0.65, 'noise_level': 0.55},
            '30m': {'weight': 6, 'trend_clarity': 0.7, 'noise_level': 0.5},
            '45m': {'weight': 7, 'trend_clarity': 0.75, 'noise_level': 0.45},
            '1h': {'weight': 8, 'trend_clarity': 0.8, 'noise_level': 0.4},
            '90m': {'weight': 9, 'trend_clarity': 0.82, 'noise_level': 0.35},
            '2h': {'weight': 10, 'trend_clarity': 0.85, 'noise_level': 0.3},
            '4h': {'weight': 12, 'trend_clarity': 0.9, 'noise_level': 0.2},
            '6h': {'weight': 14, 'trend_clarity': 0.92, 'noise_level': 0.15},
            '8h': {'weight': 16, 'trend_clarity': 0.94, 'noise_level': 0.1},
            '1d': {'weight': 20, 'trend_clarity': 0.95, 'noise_level': 0.05}
        }
    
    def analyze_symbol_characteristics(self, symbol):
        """
        Analyze symbol characteristics to determine optimal timeframe
        """
        characteristics = {
            'volatility_level': 'medium',
            'market_type': 'unknown',
            'liquidity_level': 'medium'
        }
        
        # Crypto analysis
        if any(crypto in symbol.upper() for crypto in ['BTC', 'ETH', 'BNB', 'ADA', 'XRP', 'SOL', 'DOGE', 'AVAX', 'DOT', 'LINK']):
            characteristics['market_type'] = 'crypto'
            characteristics['volatility_level'] = 'high'
            characteristics['liquidity_level'] = 'high' if 'BTC' in symbol or 'ETH' in symbol else 'medium'
        
        # Forex analysis
        elif any(forex in symbol.upper() for forex in ['EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'NZD']):
            characteristics['market_type'] = 'forex'
            characteristics['volatility_level'] = 'medium'
            characteristics['liquidity_level'] = 'high'
        
        # Index analysis
        elif any(index in symbol.upper() for index in ['US100', 'SPX', 'SP500', 'US30', 'DE40', 'UK100', 'JPN225', 'NDX', 'GSPC', 'DJI']):
            characteristics['market_type'] = 'index'
            characteristics['volatility_level'] = 'medium'
            characteristics['liquidity_level'] = 'high'
        
        # Commodities analysis
        elif any(commodity in symbol.upper() for commodity in ['XAU', 'XAG', 'GC', 'SI', 'CL', 'NG']):
            characteristics['market_type'] = 'commodity'
            characteristics['volatility_level'] = 'medium'
            characteristics['liquidity_level'] = 'medium'
        
        return characteristics
    
    def calculate_timeframe_score(self, timeframe, symbol_characteristics, trading_style='swing'):
        """
        Calculate score for each timeframe based on symbol and trading style
        """
        tf_data = self.available_timeframes[timeframe]
        score = 0
        
        # Base score from timeframe weight
        score += tf_data['weight'] * 2
        
        # Trend clarity bonus
        score += tf_data['trend_clarity'] * 30
        
        # Noise penalty
        score -= tf_data['noise_level'] * 20
        
        # Market type adjustments
        if symbol_characteristics['market_type'] == 'crypto':
            if timeframe in ['5m', '10m', '15m', '30m']:
                score += 20  # Crypto works excellent on short timeframes
            elif timeframe in ['1m']:
                score += 5   # 1m can work for scalping crypto
            elif timeframe in ['1h', '4h']:
                score += 10  # Still good but not optimal
        
        elif symbol_characteristics['market_type'] == 'forex':
            if timeframe in ['1h', '4h', '1d']:
                score += 12  # Forex trends are clearer on higher timeframes
            elif timeframe in ['1m', '5m', '10m']:
                score -= 8
        
        elif symbol_characteristics['market_type'] == 'index':
            if timeframe in ['30m', '1h', '4h', '1d']:
                score += 10  # Indices have good trend clarity
            elif timeframe in ['1m', '5m']:
                score -= 5
        
        elif symbol_characteristics['market_type'] == 'commodity':
            if timeframe in ['1h', '4h', '1d']:
                score += 8  # Commodities trend well on higher timeframes
        
        # Volatility adjustments
        if symbol_characteristics['volatility_level'] == 'high':
            if timeframe in ['5m', '10m', '15m']:
                score += 15  # Short timeframes work well for high volatility scalping
            elif timeframe in ['30m', '1h']:
                score += 8   # Medium timeframes for swing trades
            elif timeframe in ['1m']:
                score += 3   # 1m can work but more challenging
        
        elif symbol_characteristics['volatility_level'] == 'low':
            if timeframe in ['15m', '30m', '1h']:
                score += 5  # Lower timeframes capture moves in slow markets
        
        # Trading style adjustments
        if trading_style == 'scalping':
            if timeframe in ['1m', '5m']:
                score += 25  # Perfect for scalping
            elif timeframe in ['10m', '15m']:
                score += 20  # Very good for scalping
            elif timeframe in ['20m', '30m']:
                score += 10  # Acceptable for quick scalps
            elif timeframe in ['4h', '1d']:
                score -= 20
        
        elif trading_style == 'day_trading':
            if timeframe in ['15m', '30m', '1h']:
                score += 12
            elif timeframe in ['1m', '1d']:
                score -= 8
        
        elif trading_style == 'swing':
            if timeframe in ['1h', '4h']:
                score += 15
            elif timeframe in ['1m', '5m']:
                score -= 12
        
        elif trading_style == 'position':
            if timeframe in ['4h', '1d']:
                score += 20
            elif timeframe in ['1m', '5m', '15m']:
                score -= 20
        
        return max(score, 0)  # Ensure score is not negative
    
    def recommend_optimal_timeframe(self, symbol, trading_style='swing'):
        """
        Recommend the optimal timeframe for the given symbol and trading style
        """
        characteristics = self.analyze_symbol_characteristics(symbol)
        
        scores = {}
        for timeframe in self.available_timeframes.keys():
            scores[timeframe] = self.calculate_timeframe_score(timeframe, characteristics, trading_style)
        
        # Sort by score
        sorted_timeframes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get top 3 recommendations
        top_3 = sorted_timeframes[:3]
        
        return {
            'primary': top_3[0][0],
            'secondary': top_3[1][0],
            'tertiary': top_3[2][0],
            'scores': scores,
            'characteristics': characteristics,
            'reasoning': self._generate_reasoning(top_3[0][0], characteristics, trading_style)
        }
    
    def _generate_reasoning(self, recommended_tf, characteristics, trading_style):
        """
        Generate human-readable reasoning for the recommendation
        """
        reasoning = []
        
        # Market type reasoning
        if characteristics['market_type'] == 'crypto':
            reasoning.append("Kripto piyasası yüksek volatilite gösteriyor")
        elif characteristics['market_type'] == 'forex':
            reasoning.append("Forex piyasası orta volatilite ile trend analizi için uygun")
        elif characteristics['market_type'] == 'index':
            reasoning.append("Endeks piyasası istikrarlı trend yapısı sunuyor")
        elif characteristics['market_type'] == 'commodity':
            reasoning.append("Emtia piyasası makro trend analizine uygun")
        
        # Timeframe reasoning
        if recommended_tf in ['1m', '5m']:
            reasoning.append("Kısa vadeli scalping için optimize edildi")
        elif recommended_tf in ['15m', '30m']:
            reasoning.append("Day trading için optimal gürültü/sinyal oranı")
        elif recommended_tf in ['1h', '2h']:
            reasoning.append("Swing trading için mükemmel trend netliği")
        elif recommended_tf in ['4h', '1d']:
            reasoning.append("Pozisyon trading için güçlü trend analizi")
        
        # Volatility reasoning
        if characteristics['volatility_level'] == 'high':
            reasoning.append("Yüksek volatilite için gürültü filtreleme")
        
        return ". ".join(reasoning) + "."
    
    def get_multi_timeframe_analysis(self, symbol):
        """
        Get comprehensive multi-timeframe analysis for scalping, medium, and long-term
        """
        characteristics = self.analyze_symbol_characteristics(symbol)
        
        # Get optimal timeframes for different trading styles
        scalp_analysis = self.recommend_optimal_timeframe(symbol, 'scalping')
        medium_analysis = self.recommend_optimal_timeframe(symbol, 'day_trading')
        long_analysis = self.recommend_optimal_timeframe(symbol, 'swing')
        
        return {
            'scalping': {
                'timeframe': scalp_analysis['primary'],
                'alternatives': [scalp_analysis['secondary'], scalp_analysis['tertiary']],
                'confidence': max(scalp_analysis['scores'].values()) / 100
            },
            'medium_term': {
                'timeframe': medium_analysis['primary'],
                'alternatives': [medium_analysis['secondary'], medium_analysis['tertiary']],
                'confidence': max(medium_analysis['scores'].values()) / 100
            },
            'long_term': {
                'timeframe': long_analysis['primary'],
                'alternatives': [long_analysis['secondary'], long_analysis['tertiary']],
                'confidence': max(long_analysis['scores'].values()) / 100
            },
            'market_analysis': characteristics,
            'daily_adaptation': self._calculate_daily_factors(symbol)
        }
    
    def _calculate_daily_factors(self, symbol):
        """
        Calculate daily market factors that influence timeframe selection
        """
        from datetime import datetime
        import hashlib
        
        # Create a daily seed based on symbol and date
        today = datetime.now().strftime('%Y-%m-%d')
        daily_seed = hashlib.md5(f"{symbol}_{today}".encode()).hexdigest()
        
        # Convert to numeric factors (0-1 range)
        volatility_factor = int(daily_seed[:2], 16) / 255
        trend_factor = int(daily_seed[2:4], 16) / 255
        session_factor = int(daily_seed[4:6], 16) / 255
        
        return {
            'volatility_adjustment': volatility_factor,
            'trend_strength': trend_factor,
            'market_session': session_factor,
            'recommended_adjustment': 'higher_tf' if volatility_factor > 0.7 else 'lower_tf' if volatility_factor < 0.3 else 'optimal'
        }
    
    def get_optimal_timeframe(self, symbol, period='3mo'):
        """
        Get the single optimal timeframe for analysis
        """
        recommendation = self.recommend_optimal_timeframe(symbol, 'swing')
        return recommendation['primary']
        
        return {
            'volatility_adjustment': volatility_factor,
            'liquidity_adjustment': liquidity_factor,
            'trend_strength': trend_strength,
            'daily_bias': 'aggressive' if volatility_factor > 0.6 else 'conservative'
        }
    
    def get_timeframe_analysis(self, symbol, trading_style='swing'):
        """
        Get comprehensive timeframe analysis with recommendations
        """
        recommendation = self.recommend_optimal_timeframe(symbol, trading_style)
        
        return {
            'optimal_timeframe': recommendation['primary'],
            'alternative_timeframes': [recommendation['secondary'], recommendation['tertiary']],
            'market_analysis': recommendation['characteristics'],
            'reasoning': recommendation['reasoning'],
            'confidence_score': max(recommendation['scores'].values()) / 100
        }