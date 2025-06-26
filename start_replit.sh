#!/bin/bash

# Replit Başlatma Scripti
echo "🚀 FinansLab BiasDetector başlatılıyor..."

# Paketleri kontrol et ve yükle
echo "📦 Paketler kontrol ediliyor..."
uv sync

# Eksik paketleri yükle
echo "⬇️ Eksik paketler yükleniyor..."
uv add streamlit plotly yfinance pandas numpy requests python-binance websocket-client ta scipy

# Veritabanı oluştur (gerekirse)
echo "🗄️ Veritabanı hazırlanıyor..."
python -c "
import sqlite3
import os
if not os.path.exists('finanslab_signals.db'):
    conn = sqlite3.connect('finanslab_signals.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            signal_type TEXT NOT NULL,
            price REAL NOT NULL,
            confidence REAL NOT NULL,
            indicators TEXT,
            notes TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            total_signals INTEGER DEFAULT 0,
            successful_signals INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 0.0,
            total_pnl REAL DEFAULT 0.0,
            best_trade REAL DEFAULT 0.0,
            worst_trade REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()
    print('✅ Veritabanı oluşturuldu')
else:
    print('✅ Veritabanı mevcut')
"

# Uygulamayı başlat
echo "🌐 Streamlit uygulaması başlatılıyor..."
echo "📱 Tarayıcınızda otomatik olarak açılacak..."

# Ana uygulamayı çalıştır
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
