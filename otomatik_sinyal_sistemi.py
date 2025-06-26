"""
FinansLab Otomatik Sinyal Sistemi
================================

Belirli dakika/saat aralıklarında otomatik sinyal kontrolü yapan sistem.
En iyi trading saatleri ve otomatik alarmlar.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import threading

class OtomatikSinyalSistemi:
    """Otomatik sinyal takip ve alarm sistemi"""
    
    def __init__(self):
        self.ema_periods = [45, 89, 144, 200, 276]
        self.watched_symbols = ['BTC-USD', 'ETH-USD', 'EURUSD=X', 'GBPUSD=X', 'GC=F']
        self.last_signals = {}
        self.running = True
        
        # En iyi trading zamanları (UTC)
        self.best_times = {
            'FOREX': {
                'london_session': ['08:00', '17:00'],  # London açılış
                'newyork_session': ['13:00', '22:00'], # New York açılış
                'overlap': ['13:00', '17:00']          # Overlap (EN İYİ)
            },
            'CRYPTO': {
                'always': ['00:00', '23:59']           # 7/24 açık
            },
            'GOLD': {
                'london_open': ['08:00', '09:00'],     # London açılış
                'us_session': ['14:30', '21:00']       # US session
            }
        }
        
        # Sinyal kalite seviyeleri
        self.signal_quality = {
            'cok_iyi': {'bias_min': 80, 'fvg_min': 2, 'confluence': 'high'},
            'iyi': {'bias_min': 60, 'fvg_min': 1, 'confluence': 'medium'},
            'orta': {'bias_min': 40, 'fvg_min': 0, 'confluence': 'low'}
        }
    
    def get_current_time_info(self):
        """Şu anki zaman ve trading session bilgisi"""
        now = datetime.utcnow()
        current_hour = now.strftime('%H:%M')
        
        session_info = {
            'time': current_hour,
            'date': now.strftime('%Y-%m-%d'),
            'forex_session': self._get_forex_session(current_hour),
            'is_best_time': self._is_best_trading_time(current_hour),
            'recommendation': self._get_time_recommendation(current_hour)
        }
        
        return session_info
    
    def _get_forex_session(self, current_time):
        """Hangi forex sessionda olduğumuzu belirle"""
        hour = int(current_time.split(':')[0])
        
        if 0 <= hour < 8:
            return '🌙 Sydney/Tokyo Session'
        elif 8 <= hour < 13:
            return '🇬🇧 London Session'
        elif 13 <= hour < 17:
            return '⚡ London-NY Overlap (EN İYİ)'
        elif 17 <= hour < 22:
            return '🇺🇸 New York Session'
        else:
            return '🌙 Sydney Session'
    
    def _is_best_trading_time(self, current_time):
        """En iyi trading zamanında mıyız?"""
        hour = int(current_time.split(':')[0])
        
        # En iyi zamanlar:
        # 08:00-09:00 London açılış
        # 13:00-17:00 London-NY overlap
        # 14:30-15:30 US market açılış
        
        best_hours = [8, 9, 13, 14, 15, 16]
        return hour in best_hours
    
    def _get_time_recommendation(self, current_time):
        """Zaman bazlı öneri"""
        hour = int(current_time.split(':')[0])
        
        if 8 <= hour <= 9:
            return "🔥 MÜKEMMEL ZAMAN - London açılış volatilitesi"
        elif 13 <= hour <= 17:
            return "⚡ EN İYİ ZAMAN - London-NY overlap"
        elif 14 <= hour <= 15:
            return "🚀 SÜPER ZAMAN - US market açılış"
        elif 21 <= hour <= 23:
            return "📊 İYİ ZAMAN - NY kapanış volatilitesi"
        elif 0 <= hour <= 7:
            return "😴 SAKIN ZAMAN - Düşük volatilite"
        else:
            return "📈 NORMAL ZAMAN - Standart trading"
    
    def analyze_symbol_quality(self, symbol):
        """Sembol analizi ve sinyal kalitesi değerlendirmesi"""
        try:
            # Veri getir
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1mo', interval='1h')  # 1 saat bar
            
            if len(data) < 50:
                return None
            
            close = data['Close']
            current_price = close.iloc[-1]
            
            # EMA hesapla
            emas = {}
            for period in self.ema_periods:
                emas[f'EMA_{period}'] = close.ewm(span=period).mean()
            
            # Bias analizi
            above_emas = sum(1 for period in self.ema_periods 
                           if current_price > emas[f'EMA_{period}'].iloc[-1])
            bias_strength = (above_emas / len(self.ema_periods)) * 100
            
            # FVG tespiti
            fvgs = self._detect_fvgs(data)
            fvg_count = len(fvgs)
            
            # Confluence hesaplama
            confluence = self._calculate_confluence(bias_strength, fvg_count, data)
            
            # Sinyal kalitesi belirleme
            signal_quality = self._determine_signal_quality(bias_strength, fvg_count, confluence)
            
            # Direction
            if bias_strength >= 60:
                direction = "LONG"
                signal_emoji = "🟢"
            elif bias_strength <= 40:
                direction = "SHORT"
                signal_emoji = "🔴"
            else:
                direction = "WAIT"
                signal_emoji = "🟡"
            
            return {
                'symbol': symbol,
                'price': round(current_price, 4),
                'bias_strength': round(bias_strength, 1),
                'direction': direction,
                'signal_emoji': signal_emoji,
                'fvg_count': fvg_count,
                'confluence': confluence,
                'quality': signal_quality,
                'emas': {k: round(v.iloc[-1], 4) for k, v in emas.items()},
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            
        except Exception as e:
            print(f"❌ {symbol} analiz hatası: {e}")
            return None
    
    def _detect_fvgs(self, data, lookback=20):
        """Basitleştirilmiş FVG tespiti"""
        high = data['High'].iloc[-lookback:]
        low = data['Low'].iloc[-lookback:]
        close = data['Close'].iloc[-lookback:]
        
        fvgs = []
        current_price = close.iloc[-1]
        
        for i in range(2, len(high)):
            # Bullish FVG
            if (low.iloc[i] > high.iloc[i-2] and 
                low.iloc[i] > current_price):  # Unfilled
                fvgs.append('bullish')
            
            # Bearish FVG  
            if (high.iloc[i] < low.iloc[i-2] and 
                high.iloc[i] < current_price):  # Unfilled
                fvgs.append('bearish')
        
        return fvgs
    
    def _calculate_confluence(self, bias_strength, fvg_count, data):
        """Confluence seviyesi hesaplama"""
        score = 0
        
        # Bias gücü
        if bias_strength >= 80 or bias_strength <= 20:
            score += 3
        elif bias_strength >= 60 or bias_strength <= 40:
            score += 2
        else:
            score += 1
        
        # FVG sayısı
        if fvg_count >= 2:
            score += 2
        elif fvg_count >= 1:
            score += 1
        
        # Volatilite
        volatility = data['Close'].pct_change().std() * 100
        if volatility > 2:
            score += 1
        
        if score >= 5:
            return 'high'
        elif score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _determine_signal_quality(self, bias_strength, fvg_count, confluence):
        """Sinyal kalitesi belirleme"""
        if (bias_strength >= 80 or bias_strength <= 20) and fvg_count >= 2 and confluence == 'high':
            return 'cok_iyi'
        elif (bias_strength >= 60 or bias_strength <= 40) and fvg_count >= 1 and confluence in ['high', 'medium']:
            return 'iyi'
        else:
            return 'orta'
    
    def scan_all_symbols(self):
        """Tüm sembolleri tara"""
        time_info = self.get_current_time_info()
        results = []
        
        print(f"\n{'='*60}")
        print(f"🕐 {time_info['time']} - {time_info['date']}")
        print(f"📊 {time_info['forex_session']}")
        print(f"⭐ {time_info['recommendation']}")
        print(f"{'='*60}")
        
        for symbol in self.watched_symbols:
            result = self.analyze_symbol_quality(symbol)
            if result:
                results.append(result)
                self._print_signal(result)
        
        # En iyi sinyalleri filtrele
        best_signals = [r for r in results if r['quality'] in ['cok_iyi', 'iyi']]
        
        if best_signals:
            print(f"\n🎯 EN İYİ SİNYALLER ({len(best_signals)} adet):")
            for signal in best_signals:
                print(f"   {signal['signal_emoji']} {signal['symbol']}: {signal['direction']} - {signal['quality'].upper()}")
        
        return results, best_signals
    
    def _print_signal(self, result):
        """Sinyal sonucunu yazdır"""
        quality_colors = {
            'cok_iyi': '🔥',
            'iyi': '⭐',
            'orta': '📊'
        }
        
        quality_icon = quality_colors.get(result['quality'], '📊')
        
        print(f"{quality_icon} {result['symbol']:<10} | "
              f"{result['signal_emoji']} {result['direction']:<5} | "
              f"Bias: {result['bias_strength']:>5.1f}% | "
              f"FVG: {result['fvg_count']} | "
              f"Fiyat: {result['price']}")
    
    def start_auto_scanner(self, interval_minutes=15):
        """Otomatik tarama başlat"""
        print(f"🚀 Otomatik sinyal sistemi başlatıldı!")
        print(f"⏰ Her {interval_minutes} dakikada bir tarama yapılacak")
        print(f"📱 En iyi sinyaller için alarm verilecek")
        print(f"🛑 Durdurmak için Ctrl+C")
        print(f"📊 Takip edilen semboller: {', '.join(self.watched_symbols)}")
        print(f"🎯 Sinyal kaliteleri: ÇOK İYİ > İYİ > ORTA")
        
        try:
            while self.running:
                results, best_signals = self.scan_all_symbols()
                
                # En iyi sinyaller için alarm
                for signal in best_signals:
                    if signal['quality'] == 'cok_iyi':
                        self._send_alert(signal)
                
                # Sonraki tarama zamanı
                next_scan = datetime.now() + timedelta(minutes=interval_minutes)
                print(f"\n⏳ Sonraki tarama: {next_scan.strftime('%H:%M:%S')}")
                print("=" * 60)
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Otomatik tarama durduruldu.")
            self.running = False
    
    def _send_alert(self, signal):
        """Yüksek kaliteli sinyaller için alarm"""
        alert_message = (f"🔥 ÇOK İYİ SİNYAL ALARM!\n"
                        f"Sembol: {signal['symbol']}\n"
                        f"Yön: {signal['direction']}\n"
                        f"Bias: {signal['bias_strength']}%\n"
                        f"Fiyat: {signal['price']}\n"
                        f"Zaman: {signal['timestamp']}")
        
        print(f"\n{'!'*50}")
        print(alert_message)
        print(f"{'!'*50}")
        
        # Sistem bildirimi (Windows/Mac/Linux)
        try:
            if os.name == 'nt':  # Windows
                os.system(f'msg * "{alert_message}"')
            else:  # Linux/Mac
                os.system(f'notify-send "FinansLab Alert" "{alert_message}"')
        except:
            pass

def main():
    """Ana çalıştırma fonksiyonu"""
    sistem = OtomatikSinyalSistemi()
    
    print("🎯 FinansLab Otomatik Sinyal Sistemi")
    print("=" * 50)
    print()
    print("Seçenekler:")
    print("1. Şimdi tek tarama yap")
    print("2. Otomatik tarama başlat (15 dakikada bir)")
    print("3. Hızlı tarama (5 dakikada bir)")
    print("4. Özel tarama (10-20 dakika arası)")
    print("5. En iyi trading zamanlarını göster")
    print()
    
    try:
        choice = input("Seçiminizi yapın (1-5): ").strip()
        
        if choice == "1":
            print("\n🔍 Tek tarama yapılıyor...")
            sistem.scan_all_symbols()
            
        elif choice == "2":
            sistem.start_auto_scanner(interval_minutes=15)
            
        elif choice == "3":
            sistem.start_auto_scanner(interval_minutes=5)
            
        elif choice == "4":
            print("\nÖzel tarama süresi seçin:")
            print("a) 10 dakika")
            print("b) 15 dakika")  
            print("c) 20 dakika")
            interval_choice = input("Seçiminizi yapın (a/b/c): ").strip().lower()
            
            if interval_choice == "a":
                sistem.start_auto_scanner(interval_minutes=10)
            elif interval_choice == "b":
                sistem.start_auto_scanner(interval_minutes=15)
            elif interval_choice == "c":
                sistem.start_auto_scanner(interval_minutes=20)
            else:
                print("Geçersiz seçim, 15 dakika kullanılıyor...")
                sistem.start_auto_scanner(interval_minutes=15)
                
        elif choice == "5":
            time_info = sistem.get_current_time_info()
            print(f"\n📅 Şu anki durum:")
            print(f"🕐 Zaman: {time_info['time']} UTC")
            print(f"📊 Session: {time_info['forex_session']}")
            print(f"⭐ Durum: {time_info['recommendation']}")
            print(f"🎯 En iyi zaman: {'EVET' if time_info['is_best_time'] else 'HAYIR'}")
            
            print(f"\n⏰ EN İYİ TRADİNG SAATLERİ (UTC):")
            print("🔥 08:00-09:00: London açılış (MÜKEMMEL)")
            print("⚡ 13:00-17:00: London-NY overlap (EN İYİ)")  
            print("🚀 14:30-15:30: US market açılış (SÜPER)")
            print("📊 21:00-23:00: NY kapanış (İYİ)")
            print("😴 00:00-07:00: Sakin dönem (DÜŞÜK)")
            
        else:
            print("Geçersiz seçim, tek tarama yapılıyor...")
            sistem.scan_all_symbols()
            
    except KeyboardInterrupt:
        print("\n\n👋 Program kapatıldı.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")

if __name__ == "__main__":
    main()