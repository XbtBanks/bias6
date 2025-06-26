# FinansLab Bias Sistemi - Kapsamlı Açıklama

## 🎯 Sistemin Ana Bileşenleri

### 1. EMA Bias Analizi
- **5 farklı EMA periyodu** kullanılarak trend yönü belirlenir
- **Bias gücü** hesaplanır (0-100% arası)
- **EMA sıralaması** analiz edilir (mükemmel trend için)
- **Momentum hesaplama** ile trend hızı ölçülür

### 2. US FVG (Fair Value Gap) Tespiti
- **Unfilled gap'ler** tespit edilir
- **Güç seviyesi** belirlenir (normal/güçlü)
- **Yaş analizi** yapılır (kaç bar önce oluştu)
- **Fiyat seviyesi** gösterilir

### 3. Scalp Trading Sinyalleri
- **RSI pullback** stratejisi
- **MACD crossover** sinyalleri
- **EMA yakınlık** analizi
- **Kalite skoru** hesaplama

### 4. Risk Yönetimi
- **%1 risk per trade** otomatik hesaplama
- **1.5R profit target** belirleme
- **ATR bazlı stop loss**
- **Pozisyon büyüklüğü** hesaplama

### 5. Confluence Sistemi
- **12 puan üzerinden** genel skor
- **Çoklu faktör** birleştirme
- **Sinyal kalitesi** derecelendirme

## 📊 Tahmin Nasıl Yapılıyor?

### Adım 1: Veri Toplama
```
Yahoo Finance API → Real-time fiyat verileri
↓
OHLCV + Volume verileri alınır
↓
Son 3 aylık tarihsel veri işlenir
```

### Adım 2: Teknik Analiz
```
5 EMA Hesaplama → 45, 89, 144, 200, 276 periyot
↓
RSI, MACD, ATR, Bollinger Bands hesaplama
↓
FVG pattern recognition algoritması
↓
Momentum ve trend strength analizi
```

### Adım 3: Sinyal Üretimi
```
EMA Bias (0-100%) + FVG Count + Scalp Score
↓
Confluence hesaplama (12 puan üzerinden)
↓
Kalite belirleme: MÜKEMMEL/ÇOK İYİ/İYİ/ORTA/ZAYIF
↓
Trading direction: LONG/SHORT/WAIT
```

### Adım 4: Risk Hesaplama
```
Current Price + ATR → Stop Loss seviyesi
↓
1.5R multiplier → Take Profit seviyesi
↓
%1 account risk → Position size
↓
Complete trading plan
```

## 🚨 Sinyaller Nerede Gösteriliyor?

### Ana Sayfada:
1. **MÜKEMMEL SİNYALLER** bölümü (🔥 kırmızı header)
   - Confluence score 8+ olan sinyaller
   - Genişletilebilir kartlar halinde
   - Tam trading planı ile

2. **TÜM KALİTELİ SİNYALLER** tablosu (⭐ yeşil header)
   - Özet tablo formatında
   - Hızlı karşılaştırma için
   - Başarı oranı metrikleri

### Her Sinyal Kartında:
- **📈 Piyasa Bilgileri**: Fiyat, bias gücü, confluence
- **🎯 Trading Planı**: Giriş, stop, hedef, pozisyon büyüklüğü
- **⚡ US FVG Seviyeleri**: Aktif gap'ler ve seviyeleri

### Sinyal Kalite Göstergeleri:
- 🔥 MÜKEMMEL (8+ confluence)
- ⭐ ÇOK İYİ (6-7 confluence)
- 📊 İYİ (4-5 confluence)
- ⚪ ORTA (2-3 confluence)

## ⏰ Otomatik Tarama Sistemi

### Piyasa Session'larına Göre:
- **London Session**: 10 dakikada bir
- **London-NY Overlap**: 5 dakikada bir (en aktif)
- **New York Session**: 10 dakikada bir
- **Sakin dönemler**: 15 dakikada bir

### İzlenen 8 Sembol:
- **Crypto**: BTC-USD, ETH-USD
- **Forex**: EURUSD, GBPUSD, JPYUSD
- **Emtialar**: XAUUSD (Gold)
- **Endeksler**: SP500, US100

## 🎯 Sinyal Güvenilirliği

### Confluence Faktörleri:
1. **EMA Bias Gücü** (0-3 puan)
2. **EMA Sequence** (0-2 puan)
3. **Momentum** (0-2 puan)
4. **FVG Sayısı/Kalitesi** (0-2 puan)
5. **Scalp Setup** (0-2 puan)
6. **RSI Conditions** (0-1 puan)

### Performans Hedefleri:
- **Win Rate**: %79.6
- **Yıllık Getiri**: %39.4
- **Risk per Trade**: %1
- **Reward Ratio**: 1.5R

## 🔄 Gerçek Zamanlı Güncelleme

Sistem sürekli çalışır ve:
- Market session'a göre interval ayarlar
- Yeni sinyaller tespit eder
- Confluence skorları günceller
- Trading planlarını yeniden hesaplar
- Web arayüzünde otomatik gösterir

Bu sistem tamamen otomatik çalışır ve hiçbir manuel müdahale gerektirmez.