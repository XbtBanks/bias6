# 🚀 FinansLab BiasDetector - Replit Kurulum Rehberi

## 📋 Adım 1: Replit'te Proje Açma

1. **Replit.com**'da oturum açın
2. **"Create Repl"** butonuna tıklayın
3. **"Import from GitHub"** veya **"Upload folder"** seçeneğini kullanın
4. Zip dosyasını yükleyin veya GitHub'dan import edin

## 🔧 Adım 2: Otomatik Kurulum

Replit projesi otomatik olarak gerekli ayarları yapar:

```bash
# Paketler otomatik yüklenecek (pyproject.toml'dan)
uv sync
```

## ▶️ Adım 3: Uygulamayı Çalıştırma

### Ana Uygulama (Önerilen):
```bash
streamlit run app.py --server.port 5000
```

### Alternatif Uygulamalar:
```bash
# Basit versiyon
streamlit run app_simple.py --server.port 5000

# FinansLab Unified
streamlit run finanslab_unified.py --server.port 5000

# Türkçe kurulum rehberi
streamlit run turkce_kurulum_rehberi.py --server.port 5000
```

## 🛠️ Adım 4: Manuel Paket Kurulumu (Gerekirse)

Eğer otomatik kurulum çalışmazsa:

```bash
# Temel paketler
uv add streamlit plotly pandas numpy yfinance requests

# Trading paketleri
uv add python-binance websocket-client

# Ek paketler
uv add trafilatura binance sqlite3
```

## 🌐 Adım 5: Port Ayarları

Replit otomatik olarak doğru portu kullanır:
- **Port:** 5000
- **External Port:** 80 (otomatik)

## 📊 Adım 6: Uygulama Özellikleri

### Ana App.py Özellikleri:
- ✅ TradingView WebSocket veri çekici
- ✅ Otomatik sinyal takip sistemi
- ✅ Günlük performans dashboard'ı
- ✅ Bias (yön) önerisi
- ✅ Gerçek zamanlı analiz

### Kullanabileceğiniz Uygulamalar:
1. **app.py** - Tam özellikli ana uygulama
2. **app_simple.py** - Basit versiyon
3. **finanslab_unified.py** - FinansLab unified sistemi
4. **sinyal_takip_sistemi.py** - Sadece sinyal takibi
5. **turkce_kurulum_rehberi.py** - Kurulum rehberi

## 🚨 Sorun Giderme

### Paket Kurulum Hatası:
```bash
# Cache temizle
uv cache clean

# Paketleri yeniden yükle
uv sync --refresh
```

### Port Hatası:
```bash
# Farklı port dene
streamlit run app.py --server.port 8080
```

### Veri Çekme Hatası:
- Yahoo Finance otomatik fallback kullanır
- CoinGecko API ücretsiz limit var
- Örnek veri her zaman çalışır

## 🎯 Hızlı Başlangıç

1. **Replit'te "Run" butonuna bas**
2. Otomatik olarak `app.py` çalışacak
3. Web arayüzü açılacak
4. Sol menüden analiz yapmaya başla!

## 📱 Mobil Erişim

Replit uygulaması telefonda da çalışır:
- Replit app'ı indir
- Projeyi açık bırak
- Mobil tarayıcıdan eriş

## 🔗 Yararlı Linkler

- **Replit Docs:** https://docs.replit.com/
- **Streamlit Docs:** https://docs.streamlit.io/
- **Proje GitHub:** (varsa link ekle)

## 📞 Destek

Sorun yaşarsanız:
1. Replit console'u kontrol edin
2. Error mesajlarını okuyun
3. Paketleri yeniden yükleyin
4. Farklı uygulama dosyası deneyin

---

🎉 **Başarılı kurulum sonrası app.py'ı çalıştırın ve trading analizi yapmaya başlayın!**
