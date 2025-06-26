# 🚀 FinansLab Otomatik Sinyal Takip Sistemi

## 🎯 Yeni Özellikler

### ⚡ Otomatik Sinyal Takip
- **Sinyal Kaydı**: Her analiz sonrası "Sinyali Kaydet" butonu ile otomatik kayıt
- **Performance Takibi**: Win rate, R multiple, PnL hesaplama
- **SQLite Veritabanı**: Tüm sinyaller kalıcı olarak saklanır
- **Otomatik SL/TP**: Bias ve volatiliteye göre stop/target hesaplama

### 📊 Günlük Bias Sistemi
- **Trend Önerisi**: Her gün için BULLISH/BEARISH/NEUTRAL önerisi
- **Güven Skoru**: %0-100 arası güvenilirlik puanı  
- **Market Analizi**: Volatilite, session ve sembol analizi
- **Akıllı Hesaplama**: Major pairs'lere göre otomatik bias hesaplama

### 📈 Performance Dashboard
- **Detaylı İstatistikler**: Win rate, R multiple, toplam kar
- **Periyodik Analiz**: 7 gün, 30 gün, 3 ay, tüm zamanlar
- **Risk Analizi**: Position sizing ve risk yönetimi önerileri
- **Gelişim Tavsiyeleri**: Performansa göre otomatik öneriler

## 🎮 Kullanım

### 1. Sistem Başlatma
```bash
cd "BiasDetector 3"
streamlit run app.py
```

### 2. Demo Verileri (İsteğe Bağlı)
```bash
python3 demo_sinyaller.py
```

### 3. Sinyal Kaydetme
1. Normal analiz yapın (sembol seçin, analiz et)
2. Sonuçta "💾 Sinyali Kaydet" butonuna basın
3. Sistem otomatik olarak:
   - Bias yönünü belirler (LONG/SHORT)
   - SL/TP seviyelerini hesaplar
   - Confluence scorunu kaydeder
   - Kaliteyi değerlendirir

### 4. Dashboard Kullanımı
Ana sayfada 3 tab bulunur:
- **📊 Piyasa Durumu**: Genel market özeti
- **⚡ Sinyal Takip**: Günlük bias + aktif sinyaller
- **📈 Performans**: Detaylı performans analizi

## 📋 Özellik Detayları

### Günlük Bias Hesaplama
```python
# Faktörler:
- Genel market trend (BTC, ETH, EURUSD, Gold)
- Volatilite analizi (yüksek/normal/düşük)
- Trading session (London-NY overlap vs diğer)
- Geçmiş performans (son 7 gün)
- Güçlü semboller (EMA 8/21 crossover)

# Çıktı:
{
    'recommended_bias': 'BULLISH',
    'confidence': 85,
    'reasoning': 'Genel market yükseliş trendinde; Normal volatilite; London-NY overlap aktif',
    'active_pairs': 'BTCUSDT, ETHUSDT, XAUUSD',
    'expected_volatility': 'Normal - Standart pozisyon büyüklüğü'
}
```

### Sinyal Kalite Kriterleri
- **MÜKEMMEL**: 80+ final score, güçlü confluence
- **ÇOK İYİ**: 70-79 final score, iyi confluence  
- **İYİ**: 60-69 final score, orta confluence

### Risk Yönetimi
- **Stop Loss**: Trend yönüne göre %1.5 risk
- **Take Profit 1**: %2.5 hedef (ana çıkış)
- **Take Profit 2**: %4.0 hedef (trend devamı)
- **Position Size**: Otomatik hesaplama (%1 hesap riski)

## 📊 Veritabanı Yapısı

### `signals` Tablosu
- Tüm sinyal detayları (entry, exit, SL, TP)
- Bias strength, confluence score
- PnL hesaplama ve R multiple
- Signal quality ve notlar

### `daily_performance` Tablosu  
- Günlük win rate ve toplam R
- Best/worst trade tracking
- Market sentiment analizi

### `daily_bias` Tablosu
- Günlük bias önerileri
- Confidence skorları
- Market conditions logging

## ⚡ Hızlı Başlangıç

1. **Demo çalıştır**: `python3 demo_sinyaller.py`
2. **Uygulamayı başlat**: `streamlit run app.py`
3. **Sinyal Takip tab'ına** git
4. **Günlük bias** önerisini gör
5. **Normal analiz** yap (BTC, ETH, vs.)
6. **Sinyali kaydet** ve takip et

## 🔮 Gelecek Özellikler

- **Telegram Entegrasyonu**: Otomatik sinyal bildirimleri
- **Portfolio Tracking**: Çoklu hesap takibi
- **Advanced Analytics**: ML bazlı bias prediction
- **Mobile App**: iOS/Android uygulaması
- **Social Trading**: Sinyal paylaşımı

---

**🎯 FinansLab Bias - Artık sadece analiz değil, tam otomatik sinyal yönetimi!**
