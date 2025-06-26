"""
FinansLab Tam Otomatik Sinyal Sistemi
=====================================

Hiçbir müdahale gerektirmeden tüm sinyalleri otomatik tespit eder.
En iyi performans gösteren dakika aralıklarında çalışır.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import threading
import json
import os

class TamOtomatikSistem:
    def __init__(self):
        # Core settings
        self.ema_periods = [45, 89, 144, 200, 276]
        self.symbols = {
            'crypto': ['BTC-USD', 'ETH-USD', 'SOL-USD'],
            'forex': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X'],
            'commodities': ['GC=F', 'CL=F'],
            'indices': ['^GSPC', '^IXIC']
        }
        
        # Performance-optimized intervals
        self.intervals = {
            'hizli': 5,      # Yüksek volatilite dönemlerinde
            'normal': 10,    # Standart kullanım
            'yavas': 15,     # Düşük volatilite dönemlerinde
            'uzun': 20       # Trend takibi için
        }
        
        # Trading sessions (UTC)
        self.sessions = {
            'sydney': (22, 7),
            'london': (7, 16), 
            'newyork': (12, 21),
            'overlap': (12, 16)  # En aktif dönem
        }
        
        # Signal tracking
        self.signal_history = []
        self.performance_stats = {}
        self.current_mode = 'normal'
        self.running = True
        
    def get_current_session(self):
        """Şu anki trading sessionu belirle"""
        hour = datetime.utcnow().hour
        
        if 7 <= hour < 12:
            return 'london', 'orta'
        elif 12 <= hour < 16:
            return 'overlap', 'yuksek'  # En iyi dönem
        elif 16 <= hour < 21:
            return 'newyork', 'orta'
        elif 21 <= hour < 22:
            return 'closing', 'yuksek'
        else:
            return 'quiet', 'dusuk'
    
    def adaptive_interval(self):
        """Piyasa durumuna göre otomatik interval seçimi"""
        session, volatility = self.get_current_session()
        
        if volatility == 'yuksek':
            return self.intervals['hizli']  # 5 dakika
        elif volatility == 'orta':
            return self.intervals['normal']  # 10 dakika
        else:
            return self.intervals['yavas']   # 15 dakika
    
    def analyze_symbol(self, symbol):
        """Gelişmiş sembol analizi"""
        try:
            # Veri getir
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='2mo', interval='1h')
            
            if len(data) < 100:
                return None
            
            close = data['Close']
            high = data['High']
            low = data['Low']
            volume = data['Volume']
            
            current_price = close.iloc[-1]
            
            # EMA analizi
            emas = {}
            for period in self.ema_periods:
                emas[period] = close.ewm(span=period).mean()
            
            # Bias hesaplama
            above_emas = sum(1 for period in self.ema_periods 
                           if current_price > emas[period].iloc[-1])
            bias_strength = (above_emas / len(self.ema_periods)) * 100
            
            # Momentum analizi
            momentum = self.calculate_momentum(close, emas)
            
            # Volatilite analizi
            volatility = self.calculate_volatility(close)
            
            # FVG tespiti
            fvgs = self.detect_advanced_fvgs(data)
            
            # Volume profil
            volume_profile = self.analyze_volume(volume, close)
            
            # Confluence score
            confluence = self.calculate_confluence(
                bias_strength, momentum, volatility, len(fvgs), volume_profile
            )
            
            # Signal generation
            signal = self.generate_signal(
                bias_strength, momentum, confluence, symbol
            )
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'price': round(current_price, 6),
                'bias_strength': round(bias_strength, 1),
                'momentum': round(momentum, 2),
                'volatility': round(volatility, 2),
                'fvg_count': len(fvgs),
                'volume_profile': volume_profile,
                'confluence': confluence,
                'signal': signal,
                'emas': {k: round(v.iloc[-1], 6) for k, v in emas.items()}
            }
            
        except Exception as e:
            return None
    
    def calculate_momentum(self, close, emas):
        """Momentum hesaplama"""
        # EMA eğimleri
        slopes = []
        for period, ema in emas.items():
            if len(ema) >= 5:
                slope = (ema.iloc[-1] - ema.iloc[-5]) / ema.iloc[-5] * 100
                slopes.append(slope)
        
        return np.mean(slopes) if slopes else 0
    
    def calculate_volatility(self, close):
        """Volatilite hesaplama"""
        returns = close.pct_change().dropna()
        return returns.std() * 100 if len(returns) > 0 else 0
    
    def detect_advanced_fvgs(self, data):
        """Gelişmiş FVG tespiti"""
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        fvgs = []
        current_price = close.iloc[-1]
        
        # Son 30 bar içinde FVG ara
        for i in range(3, min(30, len(high))):
            idx = -i
            
            # Bullish FVG
            if (low.iloc[idx] > high.iloc[idx-2] and 
                close.iloc[idx] > close.iloc[idx-1] and
                low.iloc[idx] > current_price):  # Unfilled
                
                strength = abs(close.iloc[idx] - close.iloc[idx-1]) / close.iloc[idx-1]
                if strength > 0.01:  # En az %1 hareket
                    fvgs.append({
                        'type': 'bullish',
                        'level': low.iloc[idx],
                        'strength': strength,
                        'age': i
                    })
            
            # Bearish FVG
            if (high.iloc[idx] < low.iloc[idx-2] and 
                close.iloc[idx] < close.iloc[idx-1] and
                high.iloc[idx] < current_price):  # Unfilled
                
                strength = abs(close.iloc[idx] - close.iloc[idx-1]) / close.iloc[idx-1]
                if strength > 0.01:
                    fvgs.append({
                        'type': 'bearish',
                        'level': high.iloc[idx],
                        'strength': strength,
                        'age': i
                    })
        
        # En güçlü FVG'leri seç
        fvgs.sort(key=lambda x: x['strength'], reverse=True)
        return fvgs[:3]
    
    def analyze_volume(self, volume, close):
        """Volume profil analizi"""
        try:
            recent_volume = volume.iloc[-20:].mean()
            avg_volume = volume.mean()
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Price-volume divergence
            price_change = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5]
            volume_change = (recent_volume - volume.iloc[-25:-5].mean()) / volume.iloc[-25:-5].mean()
            
            if volume_ratio > 1.5:
                return 'yuksek'
            elif volume_ratio > 1.2:
                return 'normal'
            else:
                return 'dusuk'
                
        except:
            return 'normal'
    
    def calculate_confluence(self, bias, momentum, volatility, fvg_count, volume):
        """Confluence skoru hesaplama"""
        score = 0
        
        # Bias gücü
        if bias >= 80 or bias <= 20:
            score += 3
        elif bias >= 60 or bias <= 40:
            score += 2
        
        # Momentum
        if abs(momentum) > 2:
            score += 2
        elif abs(momentum) > 1:
            score += 1
        
        # FVG sayısı
        score += min(fvg_count, 2)
        
        # Volume
        if volume == 'yuksek':
            score += 2
        elif volume == 'normal':
            score += 1
        
        # Volatilite
        if 1 < volatility < 5:
            score += 1
        
        if score >= 7:
            return 'cok_yuksek'
        elif score >= 5:
            return 'yuksek'
        elif score >= 3:
            return 'orta'
        else:
            return 'dusuk'
    
    def generate_signal(self, bias, momentum, confluence, symbol):
        """Sinyal üretimi"""
        # Direction
        if bias >= 70 and momentum > 0:
            direction = 'STRONG_LONG'
        elif bias >= 55:
            direction = 'LONG'
        elif bias <= 30 and momentum < 0:
            direction = 'STRONG_SHORT'
        elif bias <= 45:
            direction = 'SHORT'
        else:
            direction = 'NEUTRAL'
        
        # Quality
        if confluence in ['cok_yuksek', 'yuksek'] and direction.startswith('STRONG'):
            quality = 'EXCELLENT'
        elif confluence == 'yuksek' or direction.startswith('STRONG'):
            quality = 'GOOD'
        elif confluence == 'orta':
            quality = 'FAIR'
        else:
            quality = 'WEAK'
        
        return {
            'direction': direction,
            'quality': quality,
            'confidence': self.calculate_confidence(bias, momentum, confluence)
        }
    
    def calculate_confidence(self, bias, momentum, confluence):
        """Güven skoru hesaplama"""
        confidence = 0
        
        # Bias extremes
        if bias >= 90 or bias <= 10:
            confidence += 40
        elif bias >= 70 or bias <= 30:
            confidence += 25
        
        # Momentum
        confidence += min(abs(momentum) * 10, 25)
        
        # Confluence
        confluence_scores = {
            'cok_yuksek': 35,
            'yuksek': 25,
            'orta': 15,
            'dusuk': 5
        }
        confidence += confluence_scores.get(confluence, 0)
        
        return min(confidence, 100)
    
    def scan_all_markets(self):
        """Tüm piyasaları tara"""
        session, volatility = self.get_current_session()
        timestamp = datetime.now()
        
        print(f"\n{'='*80}")
        print(f"🕐 OTOMATIK TARAMA - {timestamp.strftime('%H:%M:%S')}")
        print(f"📊 Session: {session.upper()} | Volatilite: {volatility.upper()}")
        print(f"⏱️ Interval: {self.adaptive_interval()} dakika")
        print(f"{'='*80}")
        
        all_results = []
        excellent_signals = []
        good_signals = []
        
        # Her kategoriden sembol tara
        for category, symbols in self.symbols.items():
            print(f"\n📈 {category.upper()} PIYASASI:")
            print("-" * 40)
            
            for symbol in symbols:
                result = self.analyze_symbol(symbol)
                if result:
                    all_results.append(result)
                    signal = result['signal']
                    
                    # Emoji mapping
                    direction_emoji = {
                        'STRONG_LONG': '🟢🚀',
                        'LONG': '🟢',
                        'STRONG_SHORT': '🔴🚀', 
                        'SHORT': '🔴',
                        'NEUTRAL': '🟡'
                    }
                    
                    quality_emoji = {
                        'EXCELLENT': '🔥',
                        'GOOD': '⭐',
                        'FAIR': '📊',
                        'WEAK': '⚪'
                    }
                    
                    emoji = direction_emoji.get(signal['direction'], '🟡')
                    quality = quality_emoji.get(signal['quality'], '⚪')
                    
                    print(f"{quality} {emoji} {result['symbol']:<12} | "
                          f"{signal['direction']:<12} | "
                          f"Bias: {result['bias_strength']:>5.1f}% | "
                          f"Conf: {signal['confidence']:>3.0f}% | "
                          f"FVG: {result['fvg_count']} | "
                          f"Price: {result['price']}")
                    
                    # Collect best signals
                    if signal['quality'] == 'EXCELLENT':
                        excellent_signals.append(result)
                    elif signal['quality'] == 'GOOD':
                        good_signals.append(result)
        
        # Signal summary
        self.print_signal_summary(excellent_signals, good_signals, session, volatility)
        
        # Save to history
        self.signal_history.append({
            'timestamp': timestamp,
            'session': session,
            'volatility': volatility,
            'results': all_results,
            'excellent_count': len(excellent_signals),
            'good_count': len(good_signals)
        })
        
        return all_results, excellent_signals, good_signals
    
    def print_signal_summary(self, excellent, good, session, volatility):
        """Sinyal özeti yazdır"""
        print(f"\n🎯 SINYAL ÖZETİ")
        print("=" * 50)
        
        if excellent:
            print(f"🔥 MÜKEMMEL SİNYALLER ({len(excellent)} adet):")
            for signal in excellent:
                direction = signal['signal']['direction']
                conf = signal['signal']['confidence']
                print(f"   🚀 {signal['symbol']}: {direction} (Güven: {conf:.0f}%)")
        
        if good:
            print(f"\n⭐ İYİ SİNYALLER ({len(good)} adet):")
            for signal in good:
                direction = signal['signal']['direction']
                conf = signal['signal']['confidence']
                print(f"   📈 {signal['symbol']}: {direction} (Güven: {conf:.0f}%)")
        
        if not excellent and not good:
            print("😴 Şu anda güçlü sinyal bulunmuyor")
        
        # Next scan info
        next_interval = self.adaptive_interval()
        next_scan = datetime.now() + timedelta(minutes=next_interval)
        print(f"\n⏳ Sonraki tarama: {next_scan.strftime('%H:%M:%S')} ({next_interval} dk)")
        
        # Trading recommendation
        if session == 'overlap':
            print("💡 ÖNERİ: London-NY overlap - En aktif dönem!")
        elif volatility == 'yuksek':
            print("💡 ÖNERİ: Yüksek volatilite - Dikkatli olun!")
        elif volatility == 'dusuk':
            print("💡 ÖNERİ: Düşük volatilite - Sabırlı olun!")
    
    def start_auto_monitoring(self):
        """Tam otomatik izleme başlat"""
        print("🚀 FinansLab Tam Otomatik Sinyal Sistemi Başlatıldı!")
        print("⚡ Piyasa durumuna göre otomatik interval ayarlaması")
        print("📊 Tüm major piyasalar izleniyor")
        print("🎯 Sadece en iyi sinyaller raporlanıyor")
        print("🛑 Durdurmak için Ctrl+C\n")
        
        cycle_count = 0
        
        try:
            while self.running:
                cycle_count += 1
                
                # Market scan
                results, excellent, good = self.scan_all_markets()
                
                # Adaptive interval
                next_interval = self.adaptive_interval()
                
                # Wait for next scan
                print(f"\n💤 {next_interval} dakika bekleniyor...")
                time.sleep(next_interval * 60)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Sistem durduruldu.")
            print(f"📊 Toplam {cycle_count} tarama tamamlandı")
            self.print_session_stats()
    
    def print_session_stats(self):
        """Session istatistikleri"""
        if not self.signal_history:
            return
            
        total_excellent = sum(h['excellent_count'] for h in self.signal_history)
        total_good = sum(h['good_count'] for h in self.signal_history)
        
        print(f"\n📈 SESSION İSTATİSTİKLERİ:")
        print(f"🔥 Toplam mükemmel sinyal: {total_excellent}")
        print(f"⭐ Toplam iyi sinyal: {total_good}")
        print(f"🕐 Toplam çalışma süresi: {len(self.signal_history)} tarama")

def main():
    """Ana otomatik sistem"""
    sistem = TamOtomatikSistem()
    sistem.start_auto_monitoring()

if __name__ == "__main__":
    main()