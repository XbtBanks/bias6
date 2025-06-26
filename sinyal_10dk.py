"""
FinansLab 10 Dakikalık Otomatik Sinyal - Direkt Başlar
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

class SinyalSistemi:
    def __init__(self):
        self.symbols = ['BTC-USD', 'ETH-USD', 'EURUSD=X', 'GBPUSD=X', 'GC=F']
        self.ema_periods = [45, 89, 144, 200, 276]
        
    def analyze(self, symbol):
        try:
            data = yf.Ticker(symbol).history(period='1mo', interval='1h')
            if len(data) < 50:
                return None
                
            close = data['Close']
            price = close.iloc[-1]
            
            # EMA bias calculation
            above_count = 0
            for period in self.ema_periods:
                ema = close.ewm(span=period).mean().iloc[-1]
                if price > ema:
                    above_count += 1
            
            bias = (above_count / 5) * 100
            
            # Direction and quality
            if bias >= 80:
                direction, quality = "LONG", "COK_IYI"
            elif bias >= 60:
                direction, quality = "LONG", "IYI"
            elif bias <= 20:
                direction, quality = "SHORT", "COK_IYI"
            elif bias <= 40:
                direction, quality = "SHORT", "IYI"
            else:
                direction, quality = "WAIT", "ORTA"
            
            return {
                'symbol': symbol,
                'price': round(price, 4),
                'bias': round(bias, 1),
                'direction': direction,
                'quality': quality
            }
        except:
            return None
    
    def scan(self):
        now = datetime.now()
        print(f"\n{now.strftime('%H:%M:%S')} - FINANSLAB TARAMA")
        print("=" * 50)
        
        signals = []
        for symbol in self.symbols:
            result = self.analyze(symbol)
            if result:
                signals.append(result)
                emoji = "🟢" if "LONG" in result['direction'] else "🔴" if "SHORT" in result['direction'] else "🟡"
                print(f"{emoji} {result['symbol']:<10} {result['direction']:<6} {result['bias']:>5.1f}% {result['quality']}")
        
        # Best signals alert
        best = [s for s in signals if s['quality'] in ['COK_IYI', 'IYI']]
        if best:
            print(f"\nALARM: {len(best)} iyi sinyal tespit edildi!")
            for s in best:
                print(f"  {s['symbol']}: {s['direction']} ({s['quality']})")
        
        return signals
    
    def start(self, minutes=10):
        print(f"FINANSLAB {minutes} DAKIKA OTOMATIK SINYAL SISTEMI")
        print(f"Takip: {', '.join(self.symbols)}")
        print("Durdurmak icin Ctrl+C\n")
        
        cycle = 0
        try:
            while True:
                cycle += 1
                print(f"\n--- TARAMA #{cycle} ---")
                self.scan()
                
                next_time = datetime.now() + timedelta(minutes=minutes)
                print(f"\nSonraki tarama: {next_time.strftime('%H:%M')}")
                time.sleep(minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\nSistem durduruldu. {cycle} tarama tamamlandi.")

if __name__ == "__main__":
    SinyalSistemi().start(minutes=10)