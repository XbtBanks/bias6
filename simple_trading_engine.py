import pandas as pd
import numpy as np

class SimpleTradingEngine:
    """
    En Basit Trading Sistemi - Sadece 2 şey:
    1. YÖN (Bullish/Bearish/Neutral)
    2. İŞLEM SİNYALİ (Buy/Sell/Wait)
    """
    
    def __init__(self):
        self.ema_periods = [45, 89, 144, 200, 276]
    
    def get_simple_signal(self, data, symbol):
        """
        Tek fonksiyon - sadece yön ve işlem sinyali döndürür
        """
        try:
            if data is None or len(data) < 50:
                return {
                    'direction': 'Unknown',
                    'signal': 'Wait',
                    'price': 0,
                    'confidence': 0,
                    'reason': 'Insufficient data'
                }
            
            current_price = float(data['Close'].iloc[-1])
            close_prices = pd.Series(data['Close'].values, dtype=float)
            
            # EMA hesapla
            emas = {}
            for period in self.ema_periods:
                emas[period] = close_prices.ewm(span=period).mean().iloc[-1]
            
            # 1. YÖN belirleme
            direction = self._determine_direction(current_price, emas)
            
            # 2. İŞLEM SİNYALİ belirleme
            signal, confidence, reason = self._determine_signal(current_price, emas, data)
            
            return {
                'direction': direction,
                'signal': signal,
                'price': current_price,
                'confidence': confidence,
                'reason': reason
            }
            
        except Exception as e:
            return {
                'direction': 'Error',
                'signal': 'Wait',
                'price': 0,
                'confidence': 0,
                'reason': f'Analysis error: {str(e)}'
            }
    
    def _determine_direction(self, current_price, emas):
        """YÖN belirleme - sadece EMA sıralaması"""
        ema_values = [emas[period] for period in self.ema_periods]
        
        # Fiyat tüm EMA'ların üstünde mi?
        above_all = all(current_price > ema for ema in ema_values)
        below_all = all(current_price < ema for ema in ema_values)
        
        # EMA'lar sıralı mı?
        ascending = all(ema_values[i] <= ema_values[i+1] for i in range(len(ema_values)-1))
        descending = all(ema_values[i] >= ema_values[i+1] for i in range(len(ema_values)-1))
        
        if above_all and ascending:
            return 'Strong Bullish'
        elif above_all or ascending:
            return 'Bullish'
        elif below_all and descending:
            return 'Strong Bearish'
        elif below_all or descending:
            return 'Bearish'
        else:
            return 'Neutral'
    
    def _determine_signal(self, current_price, emas, data):
        """İŞLEM SİNYALİ belirleme"""
        
        # Basit momentum kontrolü
        if len(data) >= 10:
            price_change_5 = (current_price - data['Close'].iloc[-5]) / data['Close'].iloc[-5] * 100
            price_change_10 = (current_price - data['Close'].iloc[-10]) / data['Close'].iloc[-10] * 100
        else:
            price_change_5 = 0
            price_change_10 = 0
        
        # EMA 45 ile fiyat ilişkisi (en önemli)
        ema_45 = emas[45]
        price_vs_ema45 = (current_price - ema_45) / ema_45 * 100
        
        # EMA eğimi
        if len(data) >= 5:
            ema_45_prev = pd.Series(data['Close'].iloc[-5:]).ewm(span=45).mean().iloc[-2]
            ema_slope = (ema_45 - ema_45_prev) / ema_45_prev * 100
        else:
            ema_slope = 0
        
        # Sinyal mantığı
        confidence = 50
        
        # ALIM sinyali koşulları
        if (price_vs_ema45 > 1 and ema_slope > 0.5 and price_change_5 > 2):
            signal = 'Strong Buy'
            confidence = 85
            reason = f"Fiyat EMA45'in %{price_vs_ema45:.1f} üstünde, güçlü momentum"
        elif (price_vs_ema45 > 0 and ema_slope > 0):
            signal = 'Buy'
            confidence = 70
            reason = f"Fiyat EMA45 üstünde, pozitif trend"
        
        # SATIM sinyali koşulları
        elif (price_vs_ema45 < -1 and ema_slope < -0.5 and price_change_5 < -2):
            signal = 'Strong Sell'
            confidence = 85
            reason = f"Fiyat EMA45'in %{abs(price_vs_ema45):.1f} altında, güçlü düşüş"
        elif (price_vs_ema45 < 0 and ema_slope < 0):
            signal = 'Sell'
            confidence = 70
            reason = f"Fiyat EMA45 altında, negatif trend"
        
        # BEKLE
        else:
            signal = 'Wait'
            confidence = max(30, 60 - abs(price_vs_ema45) * 5)
            reason = f"Net sinyal yok, fiyat EMA45'e %{price_vs_ema45:.1f} mesafede"
        
        return signal, confidence, reason