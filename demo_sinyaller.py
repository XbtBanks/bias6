"""
FinansLab Sinyal Takip Sistemi - Demo
====================================

Bu demo sistemi test etmek için örnek sinyaller oluşturur.
"""

from sinyal_takip_sistemi import SinyalTakipSistemi
import random
from datetime import datetime, timedelta

def create_demo_signals():
    """Demo sinyaller oluştur"""
    
    takip = SinyalTakipSistemi()
    
    print("🚀 FinansLab Demo Sinyaller Oluşturuluyor...")
    print()
    
    # Demo semboller ve fiyatları
    demo_data = [
        {"symbol": "BTCUSDT", "price": 45000, "direction": "LONG", "bias": 75.5, "quality": "MÜKEMMEL"},
        {"symbol": "ETHUSDT", "price": 2800, "direction": "LONG", "bias": 68.2, "quality": "ÇOK İYİ"},
        {"symbol": "EURUSD", "price": 1.0850, "direction": "SHORT", "bias": 72.8, "quality": "ÇOK İYİ"},
        {"symbol": "XAUUSD", "price": 1950.50, "direction": "LONG", "bias": 81.3, "quality": "MÜKEMMEL"},
        {"symbol": "GBPUSD", "price": 1.2650, "direction": "SHORT", "bias": 69.7, "quality": "İYİ"},
    ]
    
    created_signals = []
    
    for i, data in enumerate(demo_data):
        # Sinyal verileri
        symbol = data["symbol"]
        direction = data["direction"]
        entry_price = data["price"]
        bias_strength = data["bias"]
        signal_quality = data["quality"]
        
        # SL/TP hesapla
        if direction == "LONG":
            stop_loss = entry_price * 0.985
            take_profit1 = entry_price * 1.025
            take_profit2 = entry_price * 1.04
        else:
            stop_loss = entry_price * 1.015
            take_profit1 = entry_price * 0.975
            take_profit2 = entry_price * 0.96
        
        # Confluence score
        confluence_score = random.uniform(7.5, 9.2)
        
        # Notlar
        notes = f"Demo sinyal #{i+1} - Bias: {bias_strength}%, Multi-timeframe onayı"
        
        # Sinyali kaydet
        signal_id = takip.kaydet_sinyal(
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit1=take_profit1,
            take_profit2=take_profit2,
            bias_strength=bias_strength,
            confluence_score=confluence_score,
            signal_quality=signal_quality,
            notes=notes
        )
        
        if signal_id:
            created_signals.append(signal_id)
            print(f"✅ {symbol} {direction} sinyali kaydedildi (ID: {signal_id})")
            
            # Bazı sinyalleri kapatılmış olarak işaretle (demo için)
            if i < 3:  # İlk 3 sinyali kapat
                # Random exit price (kazanan veya kaybeden)
                if random.random() > 0.3:  # %70 kazanma oranı
                    if direction == "LONG":
                        exit_price = entry_price * random.uniform(1.015, 1.035)
                    else:
                        exit_price = entry_price * random.uniform(0.965, 0.985)
                else:  # Kaybeden
                    if direction == "LONG":
                        exit_price = entry_price * random.uniform(0.985, 0.995)
                    else:
                        exit_price = entry_price * random.uniform(1.005, 1.015)
                
                # Sinyali kapat
                takip.guncelle_sinyal_sonuc(signal_id, exit_price)
                print(f"  📊 Sinyal kapatıldı: ${exit_price:.2f}")
    
    print()
    print(f"🎯 {len(created_signals)} demo sinyal oluşturuldu")
    print(f"📊 3 sinyal kapatıldı, 2 sinyal aktif")
    
    # Günlük bias hesapla
    print()
    print("🤖 Günlük bias hesaplanıyor...")
    bias_data = takip.hesapla_gunluk_bias()
    
    if bias_data:
        print(f"📈 Günlük Bias: {bias_data['recommended_bias']} (%{bias_data['confidence']:.0f} güven)")
        print(f"💡 Analiz: {bias_data['reasoning']}")
    
    # Rapor göster
    print()
    print("📋 Günlük Rapor:")
    rapor = takip.get_gunluk_rapor()
    
    if rapor and rapor['performance']:
        perf = rapor['performance']
        print(f"  💰 Toplam İşlem: {perf[1]}")
        print(f"  ✅ Kazanan: {perf[2]}")
        print(f"  📈 Win Rate: {perf[4]:.1f}%")
        print(f"  💎 Toplam R: {perf[5]:.2f}R")
    
    print()
    print("🚀 Demo tamamlandı! Artık uygulamayı başlatabilirsiniz:")
    print("   streamlit run app.py")
    print()
    print("📊 Sinyal Takip tab'ında demo verilerini görebilirsiniz")

if __name__ == "__main__":
    create_demo_signals()
