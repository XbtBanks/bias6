import pandas as pd
import numpy as np
import streamlit as st

class AdvancedIndicators:
    """
    Advanced technical indicators for comprehensive market analysis
    """
    
    def __init__(self):
        pass
    
    def calculate_rsi(self, prices, period=14):
        """
        Calculate Relative Strength Index (RSI)
        """
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.fillna(50)
        except Exception as e:
            st.error(f"RSI hesaplama hatası: {str(e)}")
            return pd.Series([50] * len(prices), index=prices.index)
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """
        Calculate MACD (Moving Average Convergence Divergence)
        """
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }
        except Exception as e:
            st.error(f"MACD hesaplama hatası: {str(e)}")
            return {
                'macd': pd.Series([0] * len(prices), index=prices.index),
                'signal': pd.Series([0] * len(prices), index=prices.index),
                'histogram': pd.Series([0] * len(prices), index=prices.index)
            }
    
    def analyze_price_position(self, prices, ema_data):
        """
        Analyze price position relative to EMAs
        """
        try:
            current_price = prices.iloc[-1]
            position_analysis = {
                'above_all_emas': 0,
                'below_all_emas': 0,
                'mixed_position': 0,
                'ema_distances': {},
                'position_strength': 0
            }
            
            above_count = 0
            below_count = 0
            total_emas = len(ema_data)
            
            for ema_key, ema_series in ema_data.items():
                current_ema = ema_series.iloc[-1]
                distance = ((current_price - current_ema) / current_ema) * 100
                position_analysis['ema_distances'][ema_key] = distance
                
                if current_price > current_ema:
                    above_count += 1
                else:
                    below_count += 1
            
            if above_count == total_emas:
                position_analysis['above_all_emas'] = 1
                position_analysis['position_strength'] = 100
            elif below_count == total_emas:
                position_analysis['below_all_emas'] = 1
                position_analysis['position_strength'] = -100
            else:
                position_analysis['mixed_position'] = 1
                position_analysis['position_strength'] = ((above_count - below_count) / total_emas) * 100
            
            return position_analysis
        except Exception as e:
            st.error(f"Fiyat pozisyon analizi hatası: {str(e)}")
            return {'position_strength': 0, 'ema_distances': {}}
    
    def analyze_volume(self, volume, prices, period=20):
        """
        Advanced volume analysis
        """
        try:
            volume_sma = volume.rolling(window=period).mean()
            volume_ratio = volume / volume_sma
            
            # Volume-Price Trend (VPT)
            price_change = prices.pct_change()
            vpt = (volume * price_change).cumsum()
            
            # On-Balance Volume (OBV)
            obv = []
            obv_value = 0
            
            for i in range(len(prices)):
                if i == 0:
                    obv.append(volume.iloc[i])
                    obv_value = volume.iloc[i]
                else:
                    if prices.iloc[i] > prices.iloc[i-1]:
                        obv_value += volume.iloc[i]
                    elif prices.iloc[i] < prices.iloc[i-1]:
                        obv_value -= volume.iloc[i]
                    obv.append(obv_value)
            
            obv_series = pd.Series(obv, index=volume.index)
            
            # Volume analysis
            current_volume = volume.iloc[-1]
            avg_volume = volume_sma.iloc[-1]
            volume_strength = current_volume / avg_volume if avg_volume > 0 else 1
            
            return {
                'volume_ratio': volume_ratio,
                'volume_strength': volume_strength,
                'vpt': vpt,
                'obv': obv_series,
                'volume_trend': 'Yüksek' if volume_strength > 1.5 else 'Normal' if volume_strength > 0.8 else 'Düşük'
            }
        except Exception as e:
            st.error(f"Hacim analizi hatası: {str(e)}")
            return {'volume_strength': 1, 'volume_trend': 'Normal'}
    
    def ema_sequence_analysis(self, ema_data):
        """
        Analyze EMA sequence and alignment strength
        """
        try:
            ema_periods = sorted([int(key.split('_')[1]) for key in ema_data.keys()])
            current_values = {}
            
            for period in ema_periods:
                ema_key = f"EMA_{period}"
                current_values[period] = ema_data[ema_key].iloc[-1]
            
            # Check perfect sequence
            perfect_bullish = True
            perfect_bearish = True
            
            for i in range(len(ema_periods) - 1):
                current_ema = current_values[ema_periods[i]]
                next_ema = current_values[ema_periods[i + 1]]
                
                if current_ema <= next_ema:
                    perfect_bullish = False
                if current_ema >= next_ema:
                    perfect_bearish = False
            
            # Calculate alignment strength
            alignment_score = 0
            total_comparisons = len(ema_periods) - 1
            
            for i in range(total_comparisons):
                current_ema = current_values[ema_periods[i]]
                next_ema = current_values[ema_periods[i + 1]]
                
                if current_ema > next_ema:
                    alignment_score += 1
                elif current_ema < next_ema:
                    alignment_score -= 1
            
            alignment_strength = abs(alignment_score) / total_comparisons * 100
            
            # EMA slopes
            ema_slopes = {}
            for period in ema_periods:
                ema_key = f"EMA_{period}"
                ema_series = ema_data[ema_key]
                if len(ema_series) >= 5:
                    slope = (ema_series.iloc[-1] - ema_series.iloc[-5]) / ema_series.iloc[-5] * 100
                    ema_slopes[ema_key] = slope
            
            return {
                'perfect_bullish': perfect_bullish,
                'perfect_bearish': perfect_bearish,
                'alignment_strength': alignment_strength,
                'alignment_direction': 'Bullish' if alignment_score > 0 else 'Bearish' if alignment_score < 0 else 'Neutral',
                'ema_slopes': ema_slopes,
                'sequence_quality': 'Mükemmel' if alignment_strength > 90 else 'Güçlü' if alignment_strength > 70 else 'Orta' if alignment_strength > 50 else 'Zayıf'
            }
        except Exception as e:
            st.error(f"EMA sıralama analizi hatası: {str(e)}")
            return {'alignment_strength': 0, 'sequence_quality': 'Belirsiz'}
    
    def multi_timeframe_analysis(self, symbol, intervals, period, futures_fetcher):
        """
        Multi-timeframe EMA bias analysis
        """
        try:
            timeframe_data = {}
            
            for interval in intervals:
                try:
                    data = futures_fetcher.get_klines(symbol, interval, period)
                    if not data.empty:
                        timeframe_data[interval] = data
                except Exception as e:
                    st.warning(f"{interval} zaman dilimi verisi alınamadı: {str(e)}")
            
            return timeframe_data
        except Exception as e:
            st.error(f"Multi-timeframe analiz hatası: {str(e)}")
            return {}
    
    def calculate_confluence_score(self, ema_analysis, rsi, macd, volume_analysis, price_position):
        """
        Calculate overall confluence score
        """
        try:
            score = 0
            max_score = 100
            
            # EMA bias (40 points)
            if ema_analysis.get('perfect_bullish'):
                score += 40
            elif ema_analysis.get('perfect_bearish'):
                score -= 40
            else:
                alignment_strength = ema_analysis.get('alignment_strength', 0)
                if ema_analysis.get('alignment_direction') == 'Bullish':
                    score += (alignment_strength / 100) * 40
                elif ema_analysis.get('alignment_direction') == 'Bearish':
                    score -= (alignment_strength / 100) * 40
            
            # RSI (20 points)
            current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50
            if current_rsi > 70:
                score += 10  # Overbought but bullish
            elif current_rsi > 50:
                score += 20
            elif current_rsi < 30:
                score -= 10  # Oversold but bearish
            else:
                score -= 20
            
            # MACD (20 points)
            if isinstance(macd, dict):
                macd_line = macd.get('macd', pd.Series([0]))
                signal_line = macd.get('signal', pd.Series([0]))
                histogram = macd.get('histogram', pd.Series([0]))
                
                if len(macd_line) > 0 and len(signal_line) > 0:
                    if macd_line.iloc[-1] > signal_line.iloc[-1]:
                        score += 20
                    else:
                        score -= 20
            
            # Volume (10 points)
            volume_strength = volume_analysis.get('volume_strength', 1)
            if volume_strength > 1.5:
                score += 10
            elif volume_strength > 1:
                score += 5
            elif volume_strength < 0.8:
                score -= 5
            
            # Price position (10 points)
            position_strength = price_position.get('position_strength', 0)
            score += (position_strength / 100) * 10
            
            # Normalize to 0-100 scale
            normalized_score = max(0, min(100, (score + 100) / 2))
            
            return {
                'confluence_score': normalized_score,
                'signal_strength': 'Çok Güçlü' if normalized_score > 80 else 'Güçlü' if normalized_score > 65 else 'Orta' if normalized_score > 35 else 'Zayıf' if normalized_score > 20 else 'Çok Zayıf',
                'overall_bias': 'Bullish' if normalized_score > 60 else 'Bearish' if normalized_score < 40 else 'Neutral'
            }
        except Exception as e:
            st.error(f"Confluence score hesaplama hatası: {str(e)}")
            return {'confluence_score': 50, 'signal_strength': 'Belirsiz', 'overall_bias': 'Neutral'}