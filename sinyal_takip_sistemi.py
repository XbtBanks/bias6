"""
FinansLab Otomatik Sinyal Takip ve Performans Sistemi
====================================================

Bu sistem:
1. Attığı sinyalleri otomatik olarak kaydeder
2. Günlük performansı (kazanç/kayıp) hesaplar
3. Günlük bias (yön) önerisi verir
4. Performance raporları oluşturur
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import sqlite3
import streamlit as st
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SinyalTakipSistemi:
    """Otomatik sinyal takip ve performans analiz sistemi"""
    
    def __init__(self, db_path="finanslab_signals.db"):
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Veritabanı kurulumu"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sinyaller tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit1 REAL NOT NULL,
                    take_profit2 REAL NOT NULL,
                    bias_strength REAL NOT NULL,
                    confluence_score REAL NOT NULL,
                    signal_quality TEXT NOT NULL,
                    status TEXT DEFAULT 'ACTIVE',
                    entry_time TEXT,
                    exit_time TEXT,
                    exit_price REAL,
                    pnl_percentage REAL,
                    r_multiple REAL,
                    notes TEXT
                )
            ''')
            
            # Günlük performans tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_performance (
                    date TEXT PRIMARY KEY,
                    total_signals INTEGER DEFAULT 0,
                    winning_signals INTEGER DEFAULT 0,
                    losing_signals INTEGER DEFAULT 0,
                    win_rate REAL DEFAULT 0,
                    total_r REAL DEFAULT 0,
                    best_trade_r REAL DEFAULT 0,
                    worst_trade_r REAL DEFAULT 0,
                    daily_bias TEXT DEFAULT 'NEUTRAL',
                    market_sentiment TEXT DEFAULT 'NEUTRAL'
                )
            ''')
            
            # Günlük bias önerileri tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_bias (
                    date TEXT PRIMARY KEY,
                    recommended_bias TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    reasoning TEXT NOT NULL,
                    market_conditions TEXT NOT NULL,
                    active_pairs TEXT NOT NULL,
                    expected_volatility TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Veritabanı başarıyla kuruldu")
            
        except Exception as e:
            logger.error(f"❌ Veritabanı kurulum hatası: {str(e)}")
    
    def kaydet_sinyal(self, symbol: str, direction: str, entry_price: float, 
                     stop_loss: float, take_profit1: float, take_profit2: float,
                     bias_strength: float, confluence_score: float, signal_quality: str,
                     notes: str = ""):
        """Yeni sinyal kaydı"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO signals (
                    timestamp, symbol, direction, entry_price, stop_loss,
                    take_profit1, take_profit2, bias_strength, confluence_score,
                    signal_quality, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, symbol, direction, entry_price, stop_loss,
                  take_profit1, take_profit2, bias_strength, confluence_score,
                  signal_quality, notes))
            
            signal_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Sinyal kaydedildi: {symbol} {direction} - ID: {signal_id}")
            return signal_id
            
        except Exception as e:
            logger.error(f"❌ Sinyal kaydetme hatası: {str(e)}")
            return None
    
    def guncelle_sinyal_sonuc(self, signal_id: int, exit_price: float, 
                             exit_time: Optional[str] = None):
        """Sinyal sonucunu güncelle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sinyal bilgilerini al
            cursor.execute('SELECT * FROM signals WHERE id = ?', (signal_id,))
            signal = cursor.fetchone()
            
            if not signal:
                logger.error(f"❌ Sinyal bulunamadı: {signal_id}")
                return False
            
            # Unpack signal data
            (id, timestamp, symbol, direction, entry_price, stop_loss,
             take_profit1, take_profit2, bias_strength, confluence_score,
             signal_quality, status, entry_time, old_exit_time, old_exit_price,
             old_pnl, old_r_multiple, notes) = signal
            
            # PnL hesaplama
            if direction.upper() in ['LONG', 'BUY', 'ALIM']:
                pnl_percentage = ((exit_price - entry_price) / entry_price) * 100
            else:  # SHORT
                pnl_percentage = ((entry_price - exit_price) / entry_price) * 100
            
            # R Multiple hesaplama
            risk = abs(entry_price - stop_loss)
            if risk > 0:
                if direction.upper() in ['LONG', 'BUY', 'ALIM']:
                    r_multiple = (exit_price - entry_price) / risk
                else:
                    r_multiple = (entry_price - exit_price) / risk
            else:
                r_multiple = 0
            
            # Durumu belirle
            new_status = 'WIN' if pnl_percentage > 0 else 'LOSS'
            
            # Güncelle
            exit_time = exit_time or datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE signals SET
                    status = ?, exit_time = ?, exit_price = ?,
                    pnl_percentage = ?, r_multiple = ?
                WHERE id = ?
            ''', (new_status, exit_time, exit_price, pnl_percentage, r_multiple, signal_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Sinyal güncellendi: {symbol} {new_status} - PnL: {pnl_percentage:.2f}% - R: {r_multiple:.2f}")
            
            # Günlük performansı güncelle
            self.guncelle_gunluk_performans()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Sinyal güncelleme hatası: {str(e)}")
            return False
    
    def guncelle_gunluk_performans(self, target_date: Optional[str] = None):
        """Günlük performans istatistiklerini güncelle"""
        try:
            if not target_date:
                target_date = datetime.now().strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # O gün kapanan sinyalleri al
            cursor.execute('''
                SELECT * FROM signals 
                WHERE date(exit_time) = ? AND status IN ('WIN', 'LOSS')
            ''', (target_date,))
            
            signals = cursor.fetchall()
            
            if not signals:
                logger.info(f"📊 {target_date} için kapanan sinyal bulunamadı")
                return
            
            # İstatistikleri hesapla
            total_signals = len(signals)
            winning_signals = len([s for s in signals if s[14] > 0])  # pnl_percentage > 0
            losing_signals = total_signals - winning_signals
            win_rate = (winning_signals / total_signals) * 100 if total_signals > 0 else 0
            
            # R multiple'ları al
            r_multiples = [s[15] for s in signals if s[15] is not None]  # r_multiple
            total_r = sum(r_multiples) if r_multiples else 0
            best_trade_r = max(r_multiples) if r_multiples else 0
            worst_trade_r = min(r_multiples) if r_multiples else 0
            
            # Günlük bias hesapla (aktif sinyallerin çoğunluğu)
            cursor.execute('''
                SELECT direction FROM signals 
                WHERE date(timestamp) = ? AND status = 'ACTIVE'
            ''', (target_date,))
            
            active_directions = [row[0] for row in cursor.fetchall()]
            
            if active_directions:
                long_count = len([d for d in active_directions if d.upper() in ['LONG', 'BUY', 'ALIM']])
                short_count = len([d for d in active_directions if d.upper() in ['SHORT', 'SELL', 'SATIM']])
                
                if long_count > short_count:
                    daily_bias = 'BULLISH'
                elif short_count > long_count:
                    daily_bias = 'BEARISH'
                else:
                    daily_bias = 'NEUTRAL'
            else:
                daily_bias = 'NEUTRAL'
            
            # Market sentiment (win rate'e göre)
            if win_rate >= 70:
                market_sentiment = 'STRONG'
            elif win_rate >= 50:
                market_sentiment = 'POSITIVE'
            elif win_rate >= 30:
                market_sentiment = 'NEUTRAL'
            else:
                market_sentiment = 'NEGATIVE'
            
            # Güncelle veya ekle
            cursor.execute('''
                INSERT OR REPLACE INTO daily_performance (
                    date, total_signals, winning_signals, losing_signals,
                    win_rate, total_r, best_trade_r, worst_trade_r,
                    daily_bias, market_sentiment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (target_date, total_signals, winning_signals, losing_signals,
                  win_rate, total_r, best_trade_r, worst_trade_r,
                  daily_bias, market_sentiment))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Günlük performans güncellendi: {target_date}")
            logger.info(f"   📊 Sinyaller: {total_signals}, Win Rate: {win_rate:.1f}%, Total R: {total_r:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Günlük performans güncelleme hatası: {str(e)}")
    
    def hesapla_gunluk_bias(self, market_data: Dict = None):
        """Günlük bias önerisi hesapla"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Market verilerini analiz et
            if not market_data:
                market_data = self.analyze_market_conditions()
            
            # Bias hesaplama
            bias_factors = []
            confidence_score = 0
            
            # 1. Genel market trend
            if market_data.get('overall_trend') == 'bullish':
                bias_factors.append("Genel market yükseliş trendinde")
                confidence_score += 20
                recommended_bias = 'BULLISH'
            elif market_data.get('overall_trend') == 'bearish':
                bias_factors.append("Genel market düşüş trendinde")
                confidence_score += 20
                recommended_bias = 'BEARISH'
            else:
                bias_factors.append("Market kararsız durumda")
                confidence_score += 10
                recommended_bias = 'NEUTRAL'
            
            # 2. Volatilite analizi
            volatility = market_data.get('volatility', 'normal')
            if volatility == 'high':
                bias_factors.append("Yüksek volatilite - dikkatli pozisyon")
                confidence_score += 15
            elif volatility == 'low':
                bias_factors.append("Düşük volatilite - breakout bekleyin")
                confidence_score += 10
            else:
                bias_factors.append("Normal volatilite seviyesi")
                confidence_score += 12
            
            # 3. En güçlü semboller
            strong_symbols = market_data.get('strong_symbols', [])
            if strong_symbols:
                bias_factors.append(f"Güçlü sinyaller: {', '.join(strong_symbols[:3])}")
                confidence_score += 15
            
            # 4. Market session
            current_hour = datetime.now().hour
            if 12 <= current_hour <= 16:  # London-NY overlap
                bias_factors.append("London-NY overlap - yüksek aktivite")
                confidence_score += 10
            elif 7 <= current_hour <= 11:  # London session
                bias_factors.append("London session - trend takibi")
                confidence_score += 8
            else:
                bias_factors.append("Düşük aktivite session")
                confidence_score += 5
            
            # 5. Geçmiş performans
            recent_performance = self.get_recent_performance()
            if recent_performance.get('win_rate', 0) >= 70:
                bias_factors.append("Son performans mükemmel - devam edin")
                confidence_score += 10
            elif recent_performance.get('win_rate', 0) >= 50:
                bias_factors.append("Son performans iyi")
                confidence_score += 5
            else:
                bias_factors.append("Son performans zayıf - dikkatli olun")
                confidence_score -= 5
            
            # Confidence normalize et
            confidence_score = min(100, max(0, confidence_score))
            
            # Reasoning oluştur
            reasoning = "; ".join(bias_factors)
            
            # Market conditions özeti
            market_conditions = f"Trend: {market_data.get('overall_trend', 'unknown')}, " \
                              f"Volatilite: {volatility}, " \
                              f"Session: {'Aktif' if 7 <= current_hour <= 21 else 'Düşük'}"
            
            # Aktif semboller
            active_pairs = ", ".join(strong_symbols[:5]) if strong_symbols else "Güçlü sinyal yok"
            
            # Beklenen volatilite
            if volatility == 'high':
                expected_volatility = "Yüksek - Büyük hareketler beklenebilir"
            elif volatility == 'low':
                expected_volatility = "Düşük - Sabırlı bekleyin"
            else:
                expected_volatility = "Normal - Standart pozisyon büyüklüğü"
            
            # Veritabanına kaydet
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO daily_bias (
                    date, recommended_bias, confidence, reasoning,
                    market_conditions, active_pairs, expected_volatility
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (today, recommended_bias, confidence_score, reasoning,
                  market_conditions, active_pairs, expected_volatility))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Günlük bias hesaplandı: {recommended_bias} (%{confidence_score:.0f} güven)")
            
            return {
                'date': today,
                'recommended_bias': recommended_bias,
                'confidence': confidence_score,
                'reasoning': reasoning,
                'market_conditions': market_conditions,
                'active_pairs': active_pairs,
                'expected_volatility': expected_volatility
            }
            
        except Exception as e:
            logger.error(f"❌ Günlük bias hesaplama hatası: {str(e)}")
            return None
    
    def analyze_market_conditions(self):
        """Market koşullarını analiz et"""
        try:
            # Major pairs için hızlı analiz
            import yfinance as yf
            
            major_symbols = ['BTC-USD', 'ETH-USD', 'EURUSD=X', 'GC=F']
            results = {
                'overall_trend': 'neutral',
                'volatility': 'normal',
                'strong_symbols': []
            }
            
            bullish_count = 0
            bearish_count = 0
            volatilities = []
            
            for symbol in major_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period='5d', interval='1h')
                    
                    if len(data) < 20:
                        continue
                    
                    # Trend analizi
                    close = data['Close']
                    ema_short = close.ewm(span=8).mean().iloc[-1]
                    ema_long = close.ewm(span=21).mean().iloc[-1]
                    
                    if ema_short > ema_long * 1.01:
                        bullish_count += 1
                        results['strong_symbols'].append(symbol)
                    elif ema_short < ema_long * 0.99:
                        bearish_count += 1
                    
                    # Volatilite
                    volatility = close.pct_change().std() * 100
                    volatilities.append(volatility)
                    
                except:
                    continue
            
            # Genel trend
            if bullish_count > bearish_count:
                results['overall_trend'] = 'bullish'
            elif bearish_count > bullish_count:
                results['overall_trend'] = 'bearish'
            
            # Volatilite
            if volatilities:
                avg_vol = np.mean(volatilities)
                if avg_vol > 3:
                    results['volatility'] = 'high'
                elif avg_vol < 1:
                    results['volatility'] = 'low'
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Market analizi hatası: {str(e)}")
            return {'overall_trend': 'neutral', 'volatility': 'normal', 'strong_symbols': []}
    
    def get_recent_performance(self, days: int = 7):
        """Son günlerin performansını al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            cursor.execute('''
                SELECT * FROM daily_performance 
                WHERE date >= ? AND date <= ?
                ORDER BY date DESC
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            performances = cursor.fetchall()
            conn.close()
            
            if not performances:
                return {'win_rate': 0, 'total_r': 0, 'total_signals': 0}
            
            # Toplam istatistikler
            total_signals = sum([p[1] for p in performances])  # total_signals
            winning_signals = sum([p[2] for p in performances])  # winning_signals
            total_r = sum([p[5] for p in performances])  # total_r
            
            win_rate = (winning_signals / total_signals * 100) if total_signals > 0 else 0
            
            return {
                'win_rate': win_rate,
                'total_r': total_r,
                'total_signals': total_signals,
                'days_analyzed': len(performances)
            }
            
        except Exception as e:
            logger.error(f"❌ Son performans alma hatası: {str(e)}")
            return {'win_rate': 0, 'total_r': 0, 'total_signals': 0}
    
    def get_gunluk_rapor(self, target_date: Optional[str] = None):
        """Günlük rapor oluştur"""
        try:
            if not target_date:
                target_date = datetime.now().strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Günlük performans
            cursor.execute('SELECT * FROM daily_performance WHERE date = ?', (target_date,))
            performance = cursor.fetchone()
            
            # Günlük bias
            cursor.execute('SELECT * FROM daily_bias WHERE date = ?', (target_date,))
            bias_data = cursor.fetchone()
            
            # Aktif sinyaller
            cursor.execute('SELECT * FROM signals WHERE status = "ACTIVE" ORDER BY timestamp DESC')
            active_signals = cursor.fetchall()
            
            # Kapanan sinyaller
            cursor.execute('''
                SELECT * FROM signals 
                WHERE date(exit_time) = ? AND status IN ("WIN", "LOSS")
                ORDER BY exit_time DESC
            ''', (target_date,))
            closed_signals = cursor.fetchall()
            
            conn.close()
            
            return {
                'date': target_date,
                'performance': performance,
                'bias_recommendation': bias_data,
                'active_signals': active_signals,
                'closed_signals': closed_signals
            }
            
        except Exception as e:
            logger.error(f"❌ Günlük rapor oluşturma hatası: {str(e)}")
            return None
    
    def display_streamlit_dashboard(self):
        """Streamlit dashboard gösterimi"""
        try:
            st.header("📊 FinansLab Sinyal Takip Sistemi")
            
            # Günlük bias önerisi
            today = datetime.now().strftime('%Y-%m-%d')
            bias_data = self.hesapla_gunluk_bias()
            
            if bias_data:
                st.subheader("🎯 Günlük Bias Önerisi")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    bias_color = "🟢" if bias_data['recommended_bias'] == 'BULLISH' else "🔴" if bias_data['recommended_bias'] == 'BEARISH' else "🟡"
                    st.metric("Önerilen Yön", f"{bias_color} {bias_data['recommended_bias']}")
                
                with col2:
                    st.metric("Güven Seviyesi", f"{bias_data['confidence']:.0f}%")
                
                with col3:
                    st.metric("Market Durumu", bias_data['expected_volatility'].split('-')[0].strip())
                
                st.info(f"**Analiz:** {bias_data['reasoning']}")
                st.warning(f"**Market Koşulları:** {bias_data['market_conditions']}")
                
                if bias_data['active_pairs'] != "Güçlü sinyal yok":
                    st.success(f"**Öncelikli Semboller:** {bias_data['active_pairs']}")
            
            # Son performans
            st.subheader("📈 Son 7 Gün Performansı")
            recent_perf = self.get_recent_performance()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Toplam Sinyal", recent_perf['total_signals'])
            
            with col2:
                win_rate = recent_perf['win_rate']
                st.metric("Başarı Oranı", f"{win_rate:.1f}%", 
                         delta=f"{win_rate-65:.1f}%" if win_rate >= 65 else None)
            
            with col3:
                st.metric("Toplam R", f"{recent_perf['total_r']:.2f}R")
            
            with col4:
                avg_r = recent_perf['total_r'] / recent_perf['total_signals'] if recent_perf['total_signals'] > 0 else 0
                st.metric("Ortalama R", f"{avg_r:.2f}R")
            
            # Aktif sinyaller
            rapor = self.get_gunluk_rapor()
            if rapor and rapor['active_signals']:
                st.subheader("⚡ Aktif Sinyaller")
                
                for signal in rapor['active_signals'][:5]:  # Son 5 aktif sinyal
                    (id, timestamp, symbol, direction, entry_price, stop_loss,
                     take_profit1, take_profit2, bias_strength, confluence_score,
                     signal_quality, status, entry_time, exit_time, exit_price,
                     pnl_percentage, r_multiple, notes) = signal
                    
                    with st.expander(f"{symbol} - {direction} ({signal_quality})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Giriş Fiyatı:** ${entry_price:.4f}")
                            st.write(f"**Stop Loss:** ${stop_loss:.4f}")
                            st.write(f"**Take Profit 1:** ${take_profit1:.4f}")
                        
                        with col2:
                            st.write(f"**Bias Gücü:** {bias_strength:.1f}%")
                            st.write(f"**Confluence:** {confluence_score:.1f}")
                            st.write(f"**Tarih:** {timestamp[:19]}")
                        
                        if notes:
                            st.write(f"**Notlar:** {notes}")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Dashboard gösterim hatası: {str(e)}")
            return False

# Test ve kullanım fonksiyonları
def test_sistem():
    """Sistem test fonksiyonu"""
    takip = SinyalTakipSistemi()
    
    # Test sinyali kaydet
    signal_id = takip.kaydet_sinyal(
        symbol="BTCUSDT",
        direction="LONG",
        entry_price=45000.0,
        stop_loss=44000.0,
        take_profit1=46500.0,
        take_profit2=48000.0,
        bias_strength=75.5,
        confluence_score=8.2,
        signal_quality="MÜKEMMEL",
        notes="Güçlü bullish bias + 3 FVG confluence"
    )
    
    # Test sinyal sonucu
    if signal_id:
        takip.guncelle_sinyal_sonuc(signal_id, 46200.0)
    
    # Günlük bias hesapla
    bias_data = takip.hesapla_gunluk_bias()
    print("Günlük Bias:", bias_data)
    
    # Rapor al
    rapor = takip.get_gunluk_rapor()
    print("Günlük Rapor:", rapor)

if __name__ == "__main__":
    test_sistem()
