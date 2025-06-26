import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests

class FundingCVDAnalyzer:
    """
    Funding & CVD (Cumulative Volume Delta) Analysis for crypto markets
    
    Analyzes funding rates and volume delta to predict market movements:
    - Positive funding = Longs paying shorts (potential sell pressure)
    - Negative funding = Shorts paying longs (potential buy pressure)
    - CVD divergence = Price vs volume flow mismatch
    """
    
    def __init__(self):
        self.funding_thresholds = {
            'extreme_positive': 0.05,  # 5% annual rate
            'high_positive': 0.02,     # 2% annual rate
            'neutral': 0.005,          # 0.5% annual rate
            'high_negative': -0.02,    # -2% annual rate
            'extreme_negative': -0.05  # -5% annual rate
        }
    
    def analyze_funding_sentiment(self, symbol='BTCUSDT'):
        """
        Analyze funding rates to determine market sentiment
        """
        try:
            # Simulate funding rate analysis (replace with real API in production)
            current_funding = self._get_simulated_funding_rate()
            funding_history = self._get_simulated_funding_history()
            
            # Analyze current funding rate
            funding_analysis = self._analyze_funding_rate(current_funding)
            
            # Analyze funding trend
            trend_analysis = self._analyze_funding_trend(funding_history)
            
            # Generate market sentiment
            sentiment = self._generate_funding_sentiment(funding_analysis, trend_analysis)
            
            return {
                'current_funding_rate': current_funding,
                'funding_analysis': funding_analysis,
                'trend_analysis': trend_analysis,
                'market_sentiment': sentiment,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            return self._get_fallback_funding_analysis()
    
    def analyze_cvd_patterns(self, data):
        """
        Analyze Cumulative Volume Delta patterns
        """
        try:
            if data is None or data.empty:
                return self._get_fallback_cvd_analysis()
            
            # Calculate volume delta (simplified approach)
            volume = data['Volume'].values
            close_prices = data['Close'].values
            
            # Estimate buying vs selling pressure
            price_changes = np.diff(close_prices)
            volume_delta = []
            
            for i in range(len(price_changes)):
                if price_changes[i] > 0:
                    # Price up = buying pressure
                    volume_delta.append(volume[i+1])
                elif price_changes[i] < 0:
                    # Price down = selling pressure
                    volume_delta.append(-volume[i+1])
                else:
                    volume_delta.append(0)
            
            # Calculate cumulative volume delta
            cvd = np.cumsum(volume_delta)
            
            # Analyze CVD trend
            cvd_trend = self._analyze_cvd_trend(cvd, close_prices[1:])
            
            # Detect divergence
            divergence = self._detect_cvd_divergence(cvd, close_prices[1:])
            
            return {
                'cvd_current': cvd[-1] if len(cvd) > 0 else 0,
                'cvd_trend': cvd_trend,
                'divergence': divergence,
                'volume_flow': self._interpret_volume_flow(cvd[-10:] if len(cvd) >= 10 else cvd)
            }
            
        except Exception as e:
            return self._get_fallback_cvd_analysis()
    
    def get_comprehensive_funding_cvd_analysis(self, data, symbol='BTCUSDT'):
        """
        Get comprehensive funding and CVD analysis
        """
        funding_analysis = self.analyze_funding_sentiment(symbol)
        cvd_analysis = self.analyze_cvd_patterns(data)
        
        # Combine insights
        combined_sentiment = self._combine_funding_cvd_insights(funding_analysis, cvd_analysis)
        
        return {
            'funding_analysis': funding_analysis,
            'cvd_analysis': cvd_analysis,
            'combined_sentiment': combined_sentiment,
            'trading_recommendations': self._generate_trading_recommendations(combined_sentiment)
        }
    
    def _get_simulated_funding_rate(self):
        """
        Simulate current funding rate (replace with real API)
        """
        # Generate realistic funding rate between -0.1% to 0.1%
        import random
        return random.uniform(-0.001, 0.001)
    
    def _get_simulated_funding_history(self):
        """
        Simulate funding rate history (replace with real API)
        """
        import random
        history = []
        base_rate = 0.0001
        
        for i in range(24):  # 24 hours of data
            variation = random.uniform(-0.0005, 0.0005)
            rate = base_rate + variation
            history.append(rate)
            base_rate = rate * 0.9 + 0.0001 * 0.1  # Mean reversion
        
        return history
    
    def _analyze_funding_rate(self, funding_rate):
        """
        Analyze current funding rate
        """
        if funding_rate > self.funding_thresholds['extreme_positive']:
            sentiment = "Aşırı Pozitif"
            interpretation = "Longlar shorta ağır prim ödüyor - Güçlü satış baskısı beklenir"
            risk_level = "Yüksek"
        elif funding_rate > self.funding_thresholds['high_positive']:
            sentiment = "Pozitif"
            interpretation = "Long ağırlıklı piyasa - Hafif satış baskısı olabilir"
            risk_level = "Orta"
        elif funding_rate < self.funding_thresholds['extreme_negative']:
            sentiment = "Aşırı Negatif"
            interpretation = "Shortlar longa ağır prim ödüyor - Güçlü alım baskısı beklenir"
            risk_level = "Yüksek"
        elif funding_rate < self.funding_thresholds['high_negative']:
            sentiment = "Negatif"
            interpretation = "Short ağırlıklı piyasa - Hafif alım baskısı olabilir"
            risk_level = "Orta"
        else:
            sentiment = "Nötr"
            interpretation = "Dengeli piyasa - Funding etkisi minimal"
            risk_level = "Düşük"
        
        return {
            'sentiment': sentiment,
            'interpretation': interpretation,
            'risk_level': risk_level,
            'annual_rate': funding_rate * 365 * 3 * 100  # Convert to annual percentage
        }
    
    def _analyze_funding_trend(self, funding_history):
        """
        Analyze funding rate trend
        """
        if len(funding_history) < 5:
            return {'trend': 'Belirsiz', 'strength': 0}
        
        recent = funding_history[-5:]
        older = funding_history[-10:-5] if len(funding_history) >= 10 else funding_history[:-5]
        
        recent_avg = np.mean(recent)
        older_avg = np.mean(older) if older else recent_avg
        
        change = recent_avg - older_avg
        
        if abs(change) < 0.0001:
            trend = "Sabit"
            strength = 0
        elif change > 0:
            trend = "Yükseliyor"
            strength = min(100, abs(change) * 100000)
        else:
            trend = "Düşüyor"
            strength = min(100, abs(change) * 100000)
        
        return {
            'trend': trend,
            'strength': strength,
            'change': change * 100  # Convert to percentage
        }
    
    def _generate_funding_sentiment(self, funding_analysis, trend_analysis):
        """
        Generate overall market sentiment from funding data
        """
        current_sentiment = funding_analysis['sentiment']
        trend = trend_analysis['trend']
        
        if current_sentiment in ['Aşırı Pozitif', 'Pozitif'] and trend == 'Yükseliyor':
            overall = "Güçlü Düşüş Beklentisi"
            confidence = 85
        elif current_sentiment in ['Aşırı Negatif', 'Negatif'] and trend == 'Düşüyor':
            overall = "Güçlü Yükseliş Beklentisi"
            confidence = 85
        elif current_sentiment == 'Aşırı Pozitif':
            overall = "Düşüş Beklentisi"
            confidence = 70
        elif current_sentiment == 'Aşırı Negatif':
            overall = "Yükseliş Beklentisi"
            confidence = 70
        else:
            overall = "Nötr Beklenti"
            confidence = 40
        
        return {
            'overall_sentiment': overall,
            'confidence': confidence,
            'explanation': funding_analysis['interpretation']
        }
    
    def _analyze_cvd_trend(self, cvd, prices):
        """
        Analyze CVD trend relative to price
        """
        if len(cvd) < 5:
            return {'trend': 'Belirsiz', 'strength': 0}
        
        # Calculate trend slopes
        cvd_slope = np.polyfit(range(len(cvd)), cvd, 1)[0]
        price_slope = np.polyfit(range(len(prices)), prices, 1)[0]
        
        cvd_trend = "Yükseliş" if cvd_slope > 0 else "Düşüş" if cvd_slope < 0 else "Sabit"
        strength = min(100, abs(cvd_slope) / np.std(cvd) * 100) if np.std(cvd) > 0 else 0
        
        return {
            'trend': cvd_trend,
            'strength': strength,
            'slope': cvd_slope
        }
    
    def _detect_cvd_divergence(self, cvd, prices):
        """
        Detect divergence between CVD and price
        """
        if len(cvd) < 10:
            return {'divergence': False, 'type': 'None', 'strength': 0}
        
        # Compare recent trends
        recent_cvd = cvd[-5:]
        recent_prices = prices[-5:]
        
        cvd_change = recent_cvd[-1] - recent_cvd[0]
        price_change = recent_prices[-1] - recent_prices[0]
        
        # Normalize changes
        cvd_direction = 1 if cvd_change > 0 else -1 if cvd_change < 0 else 0
        price_direction = 1 if price_change > 0 else -1 if price_change < 0 else 0
        
        if cvd_direction != price_direction and cvd_direction != 0 and price_direction != 0:
            if price_direction > 0 and cvd_direction < 0:
                div_type = "Bearish Divergence"
                explanation = "Fiyat yükseliyor ama alım baskısı azalıyor"
            else:
                div_type = "Bullish Divergence"
                explanation = "Fiyat düşüyor ama satım baskısı azalıyor"
            
            strength = min(100, abs(cvd_change) / np.std(cvd) * 50) if np.std(cvd) > 0 else 50
            
            return {
                'divergence': True,
                'type': div_type,
                'strength': strength,
                'explanation': explanation
            }
        
        return {'divergence': False, 'type': 'None', 'strength': 0}
    
    def _interpret_volume_flow(self, recent_cvd):
        """
        Interpret recent volume flow
        """
        if len(recent_cvd) < 3:
            return "Belirsiz akış"
        
        total_flow = recent_cvd[-1] - recent_cvd[0]
        
        if total_flow > 0:
            return "Net alım akışı - Birikim var"
        elif total_flow < 0:
            return "Net satım akışı - Dağıtım var"
        else:
            return "Dengeli akış - Belirsizlik"
    
    def _combine_funding_cvd_insights(self, funding_analysis, cvd_analysis):
        """
        Combine funding and CVD insights
        """
        funding_sentiment = funding_analysis['market_sentiment']['overall_sentiment']
        cvd_divergence = cvd_analysis['divergence']
        
        if "Düşüş" in funding_sentiment and cvd_divergence['divergence'] and "Bearish" in cvd_divergence['type']:
            combined = "Güçlü Düşüş Sinyali"
            confidence = 90
        elif "Yükseliş" in funding_sentiment and cvd_divergence['divergence'] and "Bullish" in cvd_divergence['type']:
            combined = "Güçlü Yükseliş Sinyali"
            confidence = 90
        elif "Düşüş" in funding_sentiment:
            combined = "Düşüş Eğilimi"
            confidence = 70
        elif "Yükseliş" in funding_sentiment:
            combined = "Yükseliş Eğilimi"
            confidence = 70
        else:
            combined = "Karışık Sinyal"
            confidence = 40
        
        return {
            'combined_sentiment': combined,
            'confidence': confidence,
            'funding_weight': 60,
            'cvd_weight': 40
        }
    
    def _generate_trading_recommendations(self, combined_sentiment):
        """
        Generate trading recommendations based on combined analysis
        """
        sentiment = combined_sentiment['combined_sentiment']
        confidence = combined_sentiment['confidence']
        
        if confidence > 80:
            if "Güçlü Düşüş" in sentiment:
                return {
                    'action': 'Short Pozisyon',
                    'confidence': confidence,
                    'explanation': 'Funding ve CVD güçlü düşüş sinyali veriyor',
                    'risk_management': 'Sıkı stop loss kullan - Volatilite yüksek olabilir'
                }
            elif "Güçlü Yükseliş" in sentiment:
                return {
                    'action': 'Long Pozisyon',
                    'confidence': confidence,
                    'explanation': 'Funding ve CVD güçlü yükseliş sinyali veriyor',
                    'risk_management': 'Normal stop loss - Trend güçlü'
                }
        
        elif confidence > 60:
            if "Düşüş" in sentiment:
                return {
                    'action': 'Dikkatli Short',
                    'confidence': confidence,
                    'explanation': 'Funding düşüş gösteriyor ama CVD desteklemiyor',
                    'risk_management': 'Küçük pozisyon - Çabuk çık'
                }
            elif "Yükseliş" in sentiment:
                return {
                    'action': 'Dikkatli Long',
                    'confidence': confidence,
                    'explanation': 'Funding yükseliş gösteriyor ama CVD desteklemiyor',
                    'risk_management': 'Küçük pozisyon - Çabuk çık'
                }
        
        return {
            'action': 'Bekle',
            'confidence': confidence,
            'explanation': 'Funding ve CVD karışık sinyal veriyor',
            'risk_management': 'İşlem yapma - Daha net sinyal bekle'
        }
    
    def _get_fallback_funding_analysis(self):
        """
        Fallback analysis when data is unavailable
        """
        return {
            'current_funding_rate': 0.0001,
            'funding_analysis': {
                'sentiment': 'Nötr',
                'interpretation': 'Veri mevcut değil - Varsayılan analiz',
                'risk_level': 'Düşük',
                'annual_rate': 1.095
            },
            'trend_analysis': {
                'trend': 'Sabit',
                'strength': 0,
                'change': 0
            },
            'market_sentiment': {
                'overall_sentiment': 'Nötr Beklenti',
                'confidence': 30,
                'explanation': 'Funding verisi mevcut değil'
            }
        }
    
    def _get_fallback_cvd_analysis(self):
        """
        Fallback CVD analysis when data is unavailable
        """
        return {
            'cvd_current': 0,
            'cvd_trend': {'trend': 'Belirsiz', 'strength': 0},
            'divergence': {'divergence': False, 'type': 'None', 'strength': 0},
            'volume_flow': 'Veri mevcut değil'
        }