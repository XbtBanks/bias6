"""
FinansLab Bias - Süper Kolay Versiyon
====================================

Hiçbir kurulum gerektirmeyen, direkt çalışan trading analiz sistemi.
Sadece bu dosyayı çalıştırın, analiz başlasın!
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class KolayFinansLab:
    """Süper basit FinansLab sistemi - kurulum yok, direkt çalışır"""
    
    def __init__(self):
        self.ema_periods = [45, 89, 144, 200, 276]
        self.forex_pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X']
        self.crypto_pairs = ['BTC-USD', 'ETH-USD', 'SOL-USD']
        self.indices = ['^GSPC', '^IXIC', '^DJI']
        self.gold = ['GC=F']
        
    def veri_getir(self, symbol, period='3mo'):
        """Yahoo Finance'dan veri getir - %100 güvenilir"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            if len(data) > 50:
                print(f"✅ {symbol}: {len(data)} veri noktası alındı")
                return data
            else:
                print(f"❌ {symbol}: Yetersiz veri")
                return None
        except Exception as e:
            print(f"❌ {symbol}: Veri hatası - {str(e)}")
            return None
    
    def ema_hesapla(self, prices, period):
        """EMA hesaplama"""
        return prices.ewm(span=period, adjust=False).mean()
    
    def bias_analiz(self, data):
        """EMA bias analizi - basit ve etkili"""
        close = data['Close']
        
        # EMA'ları hesapla
        emas = {}
        for period in self.ema_periods:
            emas[f'EMA_{period}'] = self.ema_hesapla(close, period)
        
        # Son değerler
        current_price = close.iloc[-1]
        ema_values = {k: v.iloc[-1] for k, v in emas.items()}
        
        # Bias hesaplama
        above_emas = sum(1 for ema in ema_values.values() if current_price > ema)
        bias_strength = (above_emas / len(self.ema_periods)) * 100
        
        if bias_strength >= 80:
            bias = "🟢 GÜÇLÜ YUKARI"
        elif bias_strength >= 60:
            bias = "🔵 YUKARI"
        elif bias_strength >= 40:
            bias = "🟡 NÖTR"
        elif bias_strength >= 20:
            bias = "🔴 AŞAĞI"
        else:
            bias = "🔴 GÜÇLÜ AŞAĞI"
        
        return {
            'bias': bias,
            'strength': bias_strength,
            'price': current_price,
            'emas': ema_values
        }
    
    def fvg_tespit(self, data, lookback=50):
        """Fair Value Gap tespiti"""
        high = data['High'].iloc[-lookback:]
        low = data['Low'].iloc[-lookback:]
        close = data['Close'].iloc[-lookback:]
        
        fvgs = []
        current_price = close.iloc[-1]
        
        for i in range(2, len(high)):
            # Bullish FVG
            if (low.iloc[i] > high.iloc[i-2] and 
                close.iloc[i] > close.iloc[i-1] and 
                low.iloc[i] > current_price):  # Unfilled
                
                fvgs.append({
                    'type': '🟢 Bullish FVG',
                    'level': low.iloc[i],
                    'strength': 'Güçlü' if close.iloc[i] > close.iloc[i-1] * 1.02 else 'Orta'
                })
            
            # Bearish FVG
            if (high.iloc[i] < low.iloc[i-2] and 
                close.iloc[i] < close.iloc[i-1] and 
                high.iloc[i] < current_price):  # Unfilled
                
                fvgs.append({
                    'type': '🔴 Bearish FVG',
                    'level': high.iloc[i],
                    'strength': 'Güçlü' if close.iloc[i] < close.iloc[i-1] * 0.98 else 'Orta'
                })
        
        return fvgs[-3:] if fvgs else []  # Son 3 FVG
    
    def risk_hesapla(self, current_price, bias_result):
        """Risk yönetimi hesaplama"""
        risk_percent = 1.0  # %1 risk
        reward_ratio = 1.5  # 1.5R
        
        # ATR benzeri volatilite
        volatility = current_price * 0.02  # %2 volatilite varsayımı
        
        if "YUKARI" in bias_result['bias']:
            entry = current_price
            stop_loss = entry - volatility
            take_profit = entry + (volatility * reward_ratio)
            direction = "LONG"
        else:
            entry = current_price
            stop_loss = entry + volatility
            take_profit = entry - (volatility * reward_ratio)
            direction = "SHORT"
        
        risk_amount = abs(entry - stop_loss)
        position_size = (1000 * risk_percent / 100) / risk_amount  # $1000 hesap varsayımı
        
        return {
            'direction': direction,
            'entry': round(entry, 4),
            'stop_loss': round(stop_loss, 4),
            'take_profit': round(take_profit, 4),
            'risk': f"{risk_percent}%",
            'reward': f"{risk_percent * reward_ratio}%",
            'position_size': round(position_size, 2)
        }
    
    def symbol_analiz(self, symbol):
        """Tek sembol için tam analiz"""
        print(f"\n{'='*50}")
        print(f"📊 {symbol} ANALİZİ")
        print(f"{'='*50}")
        
        # Veri getir
        data = self.veri_getir(symbol)
        if data is None:
            return None
        
        # Bias analizi
        bias_result = self.bias_analiz(data)
        
        # FVG tespiti
        fvgs = self.fvg_tespit(data)
        
        # Risk hesaplama
        risk_result = self.risk_hesapla(bias_result['price'], bias_result)
        
        # Sonuçları yazdır
        print(f"💰 Güncel Fiyat: {bias_result['price']:.4f}")
        print(f"📈 EMA Bias: {bias_result['bias']} ({bias_result['strength']:.1f}%)")
        print()
        
        print("🎯 TRADİNG PLANI:")
        print(f"   Yön: {risk_result['direction']}")
        print(f"   Giriş: {risk_result['entry']}")
        print(f"   Stop Loss: {risk_result['stop_loss']}")
        print(f"   Take Profit: {risk_result['take_profit']}")
        print(f"   Risk: {risk_result['risk']} | Hedef: {risk_result['reward']}")
        print()
        
        if fvgs:
            print("⚡ US FVG SEVİYELERİ:")
            for fvg in fvgs:
                print(f"   {fvg['type']}: {fvg['level']:.4f} ({fvg['strength']})")
        else:
            print("⚡ US FVG: Aktif seviye bulunamadı")
        
        print()
        print("📊 EMA SEVİYELERİ:")
        for ema_name, ema_value in bias_result['emas'].items():
            print(f"   {ema_name}: {ema_value:.4f}")
        
        return {
            'symbol': symbol,
            'bias': bias_result,
            'fvgs': fvgs,
            'risk': risk_result
        }
    
    def hizli_tarama(self):
        """Tüm piyasaları hızlı tara"""
        print("🚀 FinansLab Bias - Hızlı Piyasa Taraması")
        print("=" * 60)
        
        all_symbols = (self.forex_pairs + self.crypto_pairs + 
                      self.indices + self.gold)
        
        results = []
        
        for symbol in all_symbols:
            result = self.symbol_analiz(symbol)
            if result:
                results.append(result)
        
        # Özet
        print(f"\n🎯 ÖZET ANALİZ")
        print("=" * 60)
        
        bullish_count = sum(1 for r in results if "YUKARI" in r['bias']['bias'])
        bearish_count = sum(1 for r in results if "AŞAĞI" in r['bias']['bias'])
        
        print(f"📈 Bullish Sinyaller: {bullish_count}")
        print(f"📉 Bearish Sinyaller: {bearish_count}")
        print(f"🔍 Toplam Analiz: {len(results)}")
        
        return results

def main():
    """Ana çalıştırma fonksiyonu"""
    print("🎯 FinansLab Bias - Kolay Sistem Başlatılıyor...")
    print("⚡ Kurulum yok, direkt çalışır!")
    print()
    
    sistem = KolayFinansLab()
    
    # Kullanıcı seçimi
    print("Hangi analizi yapmak istiyorsunuz?")
    print("1. Hızlı tarama (tüm piyasalar)")
    print("2. Tekli analiz (bir sembol)")
    print()
    
    try:
        secim = input("Seçiminizi yapın (1 veya 2): ").strip()
        
        if secim == "1":
            sistem.hizli_tarama()
        elif secim == "2":
            print("\nMevcut semboller:")
            print("Forex: EURUSD=X, GBPUSD=X, USDJPY=X")
            print("Crypto: BTC-USD, ETH-USD, SOL-USD")
            print("Indices: ^GSPC, ^IXIC, ^DJI")
            print("Gold: GC=F")
            print()
            
            symbol = input("Sembol girin: ").strip().upper()
            if not symbol.endswith(('=X', '-USD', '^', '=F')):
                # Otomatik düzeltme
                if symbol in ['BTC', 'BITCOIN']:
                    symbol = 'BTC-USD'
                elif symbol in ['ETH', 'ETHEREUM']:
                    symbol = 'ETH-USD'
                elif symbol in ['EURUSD', 'EUR']:
                    symbol = 'EURUSD=X'
                elif symbol in ['GBPUSD', 'GBP']:
                    symbol = 'GBPUSD=X'
                elif symbol in ['SPX', 'SP500']:
                    symbol = '^GSPC'
                elif symbol in ['GOLD', 'XAUUSD']:
                    symbol = 'GC=F'
            
            sistem.symbol_analiz(symbol)
        else:
            print("Geçersiz seçim, hızlı tarama başlatılıyor...")
            sistem.hizli_tarama()
            
    except KeyboardInterrupt:
        print("\n\n👋 Sistem kapatıldı.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        print("Hızlı tarama başlatılıyor...")
        sistem.hizli_tarama()

if __name__ == "__main__":
    main()