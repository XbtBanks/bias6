"""
FinansLab 15 Dakikalık Otomatik Sinyal Sistemi
Direkt başlar, hiçbir seçim gerektirmez
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

class Sinyal15Dk:
    def __init__(self):
        self.ema_periods = [45, 89, 144, 200, 276]
        self.symbols = ['BTC-USD', 'ETH-USD', 'EURUSD=X', 'GBPUSD=X', 'GC=F']
        self.cycle_count = 0
        
    def analyze_symbol(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1mo', interval='1h')
            
            if len(data) < 50:
                return None
                
            close = data['Close']
            current_price = close.iloc[-1]
            
            # EMA bias
            above_emas = 0
            for period in self.ema_periods:
                ema = close.ewm(span=period).mean().iloc[-1]
                if current_price > ema:
                    above_emas += 1
            
            bias_strength = (above_emas / len(self.ema_periods)) * 100
            
            # FVG detection
            fvg_count = self.detect_fvgs(data)
            
            # Signal quality
            if bias_strength >= 80 and fvg_count >= 2:
                quality = "🔥 ÇOK İYİ"
            elif bias_strength >= 60 and fvg_count >= 1:
                quality = "⭐ İYİ"
            else:
                quality = "📊 ORTA"
            
            direction = "🟢 LONG" if bias_strength >= 60 else "🔴 SHORT" if bias_strength <= 40 else "🟡 WAIT"
            
            return {
                'symbol': symbol,
                'price': round(current_price, 4),
                'bias': round(bias_strength, 1),
                'direction': direction,
                'fvg_count': fvg_count,
                'quality': quality
            }
            
        except Exception as e:
            return None
    
    def detect_fvgs(self, data):
        high = data['High'].iloc[-20:]
        low = data['Low'].iloc[-20:]
        current_price = data['Close'].iloc[-1]
        
        fvg_count = 0
        for i in range(2, len(high)):
            if (low.iloc[i] > high.iloc[i-2] and low.iloc[i] > current_price) or \
               (high.iloc[i] < low.iloc[i-2] and high.iloc[i] < current_price):
                fvg_count += 1
        
        return min(fvg_count, 5)
    
    def run_scan(self):
        self.cycle_count += 1
        now = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"🕐 TARAMA #{self.cycle_count} - {now.strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        results = []
        best_signals = []
        
        for symbol in self.symbols:
            result = self.analyze_symbol(symbol)
            if result:
                results.append(result)
                
                # Print result
                print(f"{result['quality']:<12} {result['symbol']:<10} | "
                      f"{result['direction']:<10} | "
                      f"Bias: {result['bias']:>5.1f}% | "
                      f"FVG: {result['fvg_count']} | "
                      f"Fiyat: {result['price']}")
                
                # Collect best signals
                if "ÇOK İYİ" in result['quality'] or "İYİ" in result['quality']:
                    best_signals.append(result)
        
        if best_signals:
            print(f"\n🎯 EN İYİ SİNYALLER ({len(best_signals)} adet):")
            for signal in best_signals:
                print(f"   {signal['direction']} {signal['symbol']}: {signal['quality']}")
            
            # Alert for very good signals
            super_signals = [s for s in best_signals if "ÇOK İYİ" in s['quality']]
            if super_signals:
                print(f"\n🚨 ALARM: {len(super_signals)} adet ÇOK İYİ sinyal!")
                for sig in super_signals:
                    print(f"   🔥 {sig['symbol']}: {sig['direction']} - {sig['bias']}%")
        
        return results, best_signals
    
    def start_monitoring(self, interval_minutes=15):
        print("🚀 FinansLab 15 Dakikalık Sinyal Sistemi Başlatıldı!")
        print(f"⏰ Her {interval_minutes} dakikada otomatik tarama")
        print(f"📊 Takip edilen: {', '.join(self.symbols)}")
        print(f"🛑 Durdurmak için Ctrl+C")
        
        try:
            while True:
                results, best_signals = self.run_scan()
                
                next_scan = datetime.now() + timedelta(minutes=interval_minutes)
                print(f"\n⏳ Sonraki tarama: {next_scan.strftime('%H:%M:%S')}")
                print(f"💤 {interval_minutes} dakika bekleniyor...")
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Sistem durduruldu. Toplam {self.cycle_count} tarama yapıldı.")

if __name__ == "__main__":
    sistem = Sinyal15Dk()
    sistem.start_monitoring(interval_minutes=15)  # 15 dakikada bir tarama