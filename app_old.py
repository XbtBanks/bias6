import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from ema_calculator import EMACalculator
from bias_analyzer import BiasAnalyzer
from tradingview_websocket_fetcher import TradingViewWebSocketFetcher
from advanced_indicators import AdvancedIndicators
import os

# Page configuration
st.set_page_config(
    page_title="EMA Bias Analysis Tool",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("📈 EMA Bias Analysis Tool")
st.markdown("Technical analysis tool for determining market bias using multiple EMA periods")

# Sidebar for inputs
st.sidebar.header("Configuration")

# TradingView Authentication Section
st.sidebar.subheader("🔐 TradingView Hesabı")
with st.sidebar.expander("TradingView Bağlantısı", expanded=False):
    tv_username = st.text_input("Kullanıcı Adı", key="tv_user", help="TradingView kullanıcı adınız")
    tv_password = st.text_input("Şifre", type="password", key="tv_pass", help="TradingView şifreniz")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Bağlan", key="tv_connect"):
            if tv_username and tv_password:
                st.session_state['tv_authenticated'] = True
                st.session_state['tv_username'] = tv_username
                st.session_state['tv_password'] = tv_password
                st.success("Kaydedildi!")
            else:
                st.warning("Tüm alanları doldurun")
    
    with col2:
        if st.session_state.get('tv_authenticated', False):
            st.success("✅ Bağlı")
            if st.button("Çıkış", key="tv_disconnect"):
                for key in ['tv_authenticated', 'tv_username', 'tv_password']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

st.sidebar.markdown("---")

# Symbol input with TradingView categories
st.sidebar.subheader("Sembol Seçimi")

# TradingView symbol categories
tradingview_symbols = {
    "Kripto": ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:BNBUSDT", "BINANCE:ADAUSDT", "BINANCE:XRPUSDT", "BINANCE:SOLUSDT", "BINANCE:DOGEUSDT", "BINANCE:AVAXUSDT", "BINANCE:DOTUSDT", "BINANCE:LINKUSDT", "BINANCE:MATICUSDT", "BINANCE:LTCUSDT"],
    "Altın & Metal": ["OANDA:XAUUSD", "OANDA:XAGUSD", "COMEX:GC1!", "COMEX:SI1!", "COMEX:HG1!"],
    "Forex": ["OANDA:EURUSD", "OANDA:GBPUSD", "OANDA:USDJPY", "OANDA:USDCHF", "OANDA:AUDUSD", "OANDA:USDCAD"],
    "Endeksler": ["SP:SPX", "NASDAQ:NDX", "DJ:DJI", "TVC:DAX", "TVC:UKX", "TVC:NI225"],
    "Emtia": ["NYMEX:CL1!", "NYMEX:NG1!", "CBOT:ZW1!", "CBOT:ZC1!", "CBOT:ZS1!"],
    "Hisse Senetleri": ["NASDAQ:AAPL", "NASDAQ:TSLA", "NASDAQ:GOOGL", "NASDAQ:MSFT", "NASDAQ:AMZN", "NASDAQ:NVDA"]
}

# Category selection
selected_category = st.sidebar.selectbox("Kategori", list(tradingview_symbols.keys()))

# Symbol selection from category
if selected_category:
    symbol_from_preset = st.sidebar.selectbox("Sembol", tradingview_symbols[selected_category])
else:
    symbol_from_preset = "BINANCE:BTCUSDT"

# Manual symbol input
use_manual = st.sidebar.checkbox("Manuel TradingView sembolü gir")
if use_manual:
    symbol = st.sidebar.text_input("TradingView Sembol", value="BINANCE:BTCUSDT", help="TradingView formatında sembol (örn: BINANCE:BTCUSDT, OANDA:XAUUSD)")
else:
    symbol = symbol_from_preset

# Fixed EMA periods for consistency
ema_periods = [45, 89, 144, 200, 276]
st.sidebar.subheader("EMA Periods (Sabit)")
st.sidebar.info("EMA: 45, 89, 144, 200, 276")

# Fixed time period for optimal analysis
time_period = "6mo"
st.sidebar.subheader("Zaman Periyodu (Sabit)")
st.sidebar.info("6 ay - optimal analiz için")

# Interval selection
interval_options = {
    "1 dakika": "1m",
    "5 dakika": "5m",
    "15 dakika": "15m", 
    "30 dakika": "30m",
    "1 saat": "1h",
    "4 saat": "4h",
    "1 gün": "1d",
    "1 hafta": "1wk",
    "1 ay": "1mo"
}

selected_interval = st.sidebar.selectbox(
    "Zaman Aralığı",
    list(interval_options.keys()),
    index=5  # Default to "1 gün"
)

interval = interval_options[selected_interval]

# Analysis button
analyze_button = st.sidebar.button("🔍 Analiz Et", type="primary")

if analyze_button or st.session_state.get('auto_refresh', False):
    try:
        # Determine data source based on symbol
        is_crypto = symbol.startswith('BINANCE:') or 'USDT' in symbol
        
        with st.spinner(f"{symbol} için veri getiriliyor..."):
            # Use TradingView for all symbols
            try:
                tv_fetcher = TradingViewWebSocketFetcher()
                
                # Authenticate if credentials are available
                if st.session_state.get('tv_authenticated', False):
                    tv_fetcher.authenticate(
                        st.session_state.get('tv_username'),
                        st.session_state.get('tv_password')
                    )
                
                data = tv_fetcher.get_klines(symbol, interval, time_period)
                
                if data.empty:
                    st.error(f"TradingView'den veri alınamadı: {symbol}")
                    st.info("💡 Çözüm önerileri:")
                    st.info("1. TradingView hesabınızı bağlayın (yan panel - gerekli)")
                    st.info("2. Doğru TradingView sembol formatını kullanın")
                    st.info("3. TradingView hesabınızda bu sembole erişim olduğundan emin olun")
                    st.stop()
                    
            except Exception as e:
                st.error(f"TradingView veri hatası: {str(e)}")
                st.warning("TradingView hesabınızı bağlamanız gerekiyor (yan panel)")
                st.info("Hesap bilgilerinizi girdikten sonra tekrar deneyin.")
                st.stop()
                # Use multiple data sources for crypto data
                try:
                    tv_fetcher = TradingViewWebSocketFetcher()
                    
                    # Authenticate if credentials are available
                    if st.session_state.get('tv_authenticated', False):
                        tv_fetcher.authenticate(
                            st.session_state.get('tv_username'),
                            st.session_state.get('tv_password')
                        )
                    
                    data = tv_fetcher.get_klines(symbol, interval, time_period)
                    
                    if data.empty:
                        st.error(f"Kripto veri alınamadı: {symbol}")
                        st.info("💡 Çözüm önerileri:")
                        st.info("1. TradingView hesabınızı bağlayın (yan panel - gerekli)")
                        st.info("2. Doğru sembol formatını kullanın (BTCUSDT, ETHUSDT)")
                        st.info("3. TradingView hesabınızda bu sembole erişim olduğundan emin olun")
                        st.stop()
                        
                except Exception as e:
                    st.error(f"TradingView veri hatası: {str(e)}")
                    st.warning("TradingView hesabınızı bağlamanız gerekiyor (yan panel)")
                    st.info("Hesap bilgilerinizi girdikten sonra tekrar deneyin.")
                    st.stop()
            else:
                # Use Yahoo Finance for other symbols
                ticker = yf.Ticker(symbol)
                
                # For intraday intervals (minutes, hours), we need to adjust the period
                if interval in ['1m', '5m', '15m', '30m', '1h', '4h']:
                    # Yahoo Finance limits for intraday data
                    if time_period in ['2y', '5y']:
                        st.warning("Kısa zaman aralıkları için uzun periyot seçimi desteklenmiyor. 1 aya düşürülüyor.")
                        data = ticker.history(period="1mo", interval=interval)
                    elif time_period == '1y':
                        st.warning("Kısa zaman aralıkları için 1 yıl periyodu desteklenmiyor. 3 aya düşürülüyor.")
                        data = ticker.history(period="3mo", interval=interval)
                    else:
                        data = ticker.history(period=time_period, interval=interval)
                else:
                    data = ticker.history(period=time_period, interval=interval)
                
                if data.empty:
                    st.error(f"Yahoo Finance'den veri alınamadı: {symbol}")
                    st.info("Sembol doğru mu kontrol edin veya farklı bir sembol deneyin.")
                    st.stop()
        
        # Calculate EMAs
        with st.spinner("EMA'lar hesaplanıyor..."):
            ema_calc = EMACalculator()
            ema_data = {}
            
            for period in ema_periods:
                ema_data[f"EMA_{period}"] = ema_calc.calculate_ema(data['Close'], period)
        
        # Advanced technical analysis
        with st.spinner("Gelişmiş teknik analiz yapılıyor..."):
            advanced_indicators = AdvancedIndicators()
            
            # Calculate RSI
            rsi = advanced_indicators.calculate_rsi(data['Close'])
            
            # Calculate MACD
            macd = advanced_indicators.calculate_macd(data['Close'])
            
            # Volume analysis
            volume_analysis = advanced_indicators.analyze_volume(data['Volume'], data['Close'])
            
            # Price position analysis
            price_position = advanced_indicators.analyze_price_position(data['Close'], ema_data)
            
            # EMA sequence analysis
            ema_sequence = advanced_indicators.ema_sequence_analysis(ema_data)
            
            # Original bias analysis
            bias_analyzer = BiasAnalyzer(ema_periods)
            bias_results = bias_analyzer.analyze_bias(data['Close'], ema_data)
            
            # Calculate confluence score
            confluence = advanced_indicators.calculate_confluence_score(
                ema_sequence, rsi, macd, volume_analysis, price_position
            )
        
        # Enhanced Dashboard
        st.subheader("🎯 Gelişmiş Analiz Paneli")
        
        # Top level metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            confluence_score = confluence['confluence_score']
            confluence_color = "🟢" if confluence_score > 65 else "🔴" if confluence_score < 35 else "🟡"
            st.metric("Confluence Score", f"{confluence_color} {confluence_score:.0f}")
        
        with col2:
            signal_strength = confluence['signal_strength']
            st.metric("Sinyal Gücü", signal_strength)
        
        with col3:
            overall_bias = confluence['overall_bias']
            bias_color = "🟢" if overall_bias == "Bullish" else "🔴" if overall_bias == "Bearish" else "🟡"
            st.metric("Genel Bias", f"{bias_color} {overall_bias}")
        
        with col4:
            sequence_quality = ema_sequence.get('sequence_quality', 'Belirsiz')
            st.metric("EMA Kalitesi", sequence_quality)
        
        # Detailed analysis sections
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📊 EMA Sıralama Analizi")
            
            if ema_sequence.get('perfect_bullish'):
                st.success("✅ Mükemmel Yükseliş Sıralaması")
            elif ema_sequence.get('perfect_bearish'):
                st.error("❌ Mükemmel Düşüş Sıralaması")
            else:
                alignment_strength = ema_sequence.get('alignment_strength', 0)
                direction = ema_sequence.get('alignment_direction', 'Neutral')
                st.info(f"📈 {direction} Yönelim - %{alignment_strength:.1f} Güç")
            
            # EMA slopes
            st.write("**EMA Eğimleri:**")
            ema_slopes = ema_sequence.get('ema_slopes', {})
            for ema_key, slope in ema_slopes.items():
                period = ema_key.split('_')[1]
                color = "🟢" if slope > 0 else "🔴"
                st.write(f"EMA {period}: {color} %{slope:+.2f}")
        
        with col_right:
            st.subheader("🎯 Fiyat Pozisyon Analizi")
            
            position_strength = price_position.get('position_strength', 0)
            if position_strength > 50:
                st.success(f"✅ Fiyat EMA'ların üzerinde (%{position_strength:.1f})")
            elif position_strength < -50:
                st.error(f"❌ Fiyat EMA'ların altında (%{position_strength:.1f})")
            else:
                st.warning(f"⚠️ Karışık pozisyon (%{position_strength:.1f})")
            
            # EMA distances
            st.write("**EMA Mesafeleri:**")
            ema_distances = price_position.get('ema_distances', {})
            for ema_key, distance in ema_distances.items():
                period = ema_key.split('_')[1]
                color = "🟢" if distance > 0 else "🔴"
                st.write(f"EMA {period}: {color} %{distance:+.2f}")
        
        # Technical Indicators Section
        st.subheader("📈 Teknik Göstergeler")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**RSI (14)**")
            current_rsi = rsi[-1] if len(rsi) > 0 else 50
            rsi_status = "Aşırı Alım" if current_rsi > 70 else "Aşırı Satım" if current_rsi < 30 else "Normal"
            rsi_color = "🔴" if current_rsi > 70 else "🟢" if current_rsi < 30 else "🟡"
            st.metric("RSI", f"{rsi_color} {current_rsi:.1f}")
            st.write(f"Durum: {rsi_status}")
        
        with col2:
            st.write("**MACD**")
            if isinstance(macd, dict) and len(macd.get('macd', [])) > 0:
                macd_line = macd['macd'].iloc[-1]
                signal_line = macd['signal'].iloc[-1]
                histogram = macd['histogram'].iloc[-1]
                
                macd_signal = "Bullish" if macd_line > signal_line else "Bearish"
                macd_color = "🟢" if macd_line > signal_line else "🔴"
                st.metric("MACD Sinyal", f"{macd_color} {macd_signal}")
                st.write(f"Histogram: {histogram:+.4f}")
            else:
                st.metric("MACD Sinyal", "Hesaplanamadı")
        
        with col3:
            st.write("**Hacim Analizi**")
            volume_strength = volume_analysis.get('volume_strength', 1)
            volume_trend = volume_analysis.get('volume_trend', 'Normal')
            volume_color = "🟢" if volume_strength > 1.2 else "🔴" if volume_strength < 0.8 else "🟡"
            st.metric("Hacim Gücü", f"{volume_color} {volume_strength:.2f}x")
            st.write(f"Trend: {volume_trend}")
        
        # Create enhanced multi-indicator chart
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=('Fiyat ve EMA\'lar', 'RSI (14)', 'MACD', 'Hacim'),
            row_heights=[0.5, 0.15, 0.2, 0.15]
        )
        
        # Add price data
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Price",
                increasing_line_color='green',
                decreasing_line_color='red'
            ),
            row=1, col=1
        )
        
        # Add EMA lines
        ema_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for i, period in enumerate(ema_periods):
            ema_key = f"EMA_{period}"
            color = ema_colors[i % len(ema_colors)]
            
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=ema_data[ema_key],
                    mode='lines',
                    name=f"EMA {period}",
                    line=dict(color=color, width=2)
                ),
                row=1, col=1
            )
        
        # Add RSI
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=rsi,
                mode='lines',
                name="RSI",
                line=dict(color='purple', width=2)
            ),
            row=2, col=1
        )
        
        # Add RSI reference lines directly to the RSI subplot
        for i in range(len(rsi)):
            if i == 0:
                fig.add_trace(
                    go.Scatter(x=[data.index[0], data.index[-1]], y=[70, 70], mode='lines', 
                              line=dict(dash='dash', color='red', width=1), 
                              showlegend=False, name='RSI 70'),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=[data.index[0], data.index[-1]], y=[30, 30], mode='lines',
                              line=dict(dash='dash', color='green', width=1),
                              showlegend=False, name='RSI 30'),
                    row=2, col=1
                )
                break
        
        # Add MACD
        if isinstance(macd, dict):
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=macd['macd'],
                    mode='lines',
                    name="MACD",
                    line=dict(color='blue', width=2)
                ),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=macd['signal'],
                    mode='lines',
                    name="Signal",
                    line=dict(color='red', width=2)
                ),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=macd['histogram'],
                    name="Histogram",
                    marker_color=['green' if x > 0 else 'red' for x in macd['histogram']]
                ),
                row=3, col=1
            )
        
        # Add Volume
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name="Volume",
                marker_color='lightblue',
                opacity=0.7
            ),
            row=4, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=f"{symbol} - Gelişmiş Teknik Analiz",
            height=1000,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        # Update y-axis titles
        fig.update_yaxes(title_text="Fiyat", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="Hacim", row=4, col=1)
        
        # Display the enhanced chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Multi-timeframe analysis section
        st.subheader("⏰ Multi-Timeframe Analizi")
        
        if is_crypto_binance:
            timeframe_intervals = ['15m', '1h', '4h', '1d']
            timeframe_results = {}
            
            for tf_interval in timeframe_intervals:
                try:
                    tf_fetcher = TradingViewWebSocketFetcher()
                    tf_data = tf_fetcher.get_klines(symbol, tf_interval, "1mo")
                    
                    if not tf_data.empty:
                        # Quick EMA analysis for this timeframe
                        tf_ema_calc = EMACalculator()
                        tf_ema_data = {}
                        for period in ema_periods:
                            tf_ema_data[f"EMA_{period}"] = tf_ema_calc.calculate_ema(tf_data['Close'], period)
                        
                        tf_bias_analyzer = BiasAnalyzer(ema_periods)
                        tf_bias_results = tf_bias_analyzer.analyze_bias(tf_data['Close'], tf_ema_data)
                        
                        tf_ema_sequence = advanced_indicators.ema_sequence_analysis(tf_ema_data)
                        
                        timeframe_results[tf_interval] = {
                            'bias': tf_bias_results['current_bias'],
                            'strength': tf_bias_results['bias_strength'],
                            'quality': tf_ema_sequence.get('sequence_quality', 'Belirsiz')
                        }
                except:
                    timeframe_results[tf_interval] = {'bias': 'Hata', 'strength': 0, 'quality': 'Hata'}
            
            # Display timeframe analysis
            tf_cols = st.columns(len(timeframe_intervals))
            for i, (tf, result) in enumerate(timeframe_results.items()):
                with tf_cols[i]:
                    bias_color = "🟢" if result['bias'] == "Bullish" else "🔴" if result['bias'] == "Bearish" else "🟡"
                    st.metric(f"{tf} Timeframe", f"{bias_color} {result['bias']}")
                    st.write(f"Güç: {result['strength']:.1f}%")
                    st.write(f"Kalite: {result['quality']}")
        
        # Trading signals section
        st.subheader("🎯 Trading Sinyalleri")
        
        signal_col1, signal_col2 = st.columns(2)
        
        with signal_col1:
            st.write("**Entry Koşulları:**")
            
            entry_conditions = []
            if confluence['confluence_score'] > 65:
                entry_conditions.append("✅ Yüksek confluence score")
            if ema_sequence.get('perfect_bullish') or ema_sequence.get('perfect_bearish'):
                entry_conditions.append("✅ Mükemmel EMA sıralaması")
            if price_position.get('position_strength', 0) > 50:
                entry_conditions.append("✅ Güçlü fiyat pozisyonu")
            if volume_analysis.get('volume_strength', 1) > 1.2:
                entry_conditions.append("✅ Yüksek hacim")
            
            current_rsi = rsi[-1] if len(rsi) > 0 else 50
            if 30 < current_rsi < 70:
                entry_conditions.append("✅ RSI normal seviyede")
            
            if entry_conditions:
                for condition in entry_conditions:
                    st.write(condition)
            else:
                st.write("❌ Entry koşulları karşılanmıyor")
        
        with signal_col2:
            st.write("**Risk Yönetimi:**")
            
            current_price = data['Close'].iloc[-1]
            
            # Calculate potential stop loss based on EMA levels
            closest_ema = None
            closest_distance = float('inf')
            
            for period in ema_periods:
                ema_key = f"EMA_{period}"
                ema_value = ema_data[ema_key].iloc[-1]
                distance = abs(current_price - ema_value)
                
                if distance < closest_distance:
                    closest_distance = distance
                    closest_ema = ema_value
            
            if closest_ema:
                if overall_bias == "Bullish":
                    stop_loss = closest_ema * 0.995  # 0.5% below closest EMA
                    take_profit = current_price * 1.02  # 2% above current price
                elif overall_bias == "Bearish":
                    stop_loss = closest_ema * 1.005  # 0.5% above closest EMA  
                    take_profit = current_price * 0.98  # 2% below current price
                else:
                    stop_loss = current_price * 0.99
                    take_profit = current_price * 1.01
                
                st.write(f"💰 Güncel Fiyat: ${current_price:.4f}")
                st.write(f"🛑 Stop Loss: ${stop_loss:.4f}")
                st.write(f"🎯 Take Profit: ${take_profit:.4f}")
                
                risk_reward = abs(take_profit - current_price) / abs(current_price - stop_loss)
                st.write(f"📊 Risk/Reward: {risk_reward:.2f}")
        
        # Summary and recommendation
        st.subheader("📋 Özet ve Öneri")
        
        if confluence['confluence_score'] > 75:
            st.success(f"🚀 ÇOK GÜÇLÜ {overall_bias.upper()} SİNYALİ")
            st.write("Tüm göstergeler aynı yönde hizalı. Güçlü trading fırsatı.")
        elif confluence['confluence_score'] > 60:
            st.info(f"📈 GÜÇLÜ {overall_bias.upper()} SİNYALİ")
            st.write("Çoğu gösterge aynı yönde. Dikkatli trading yapılabilir.")
        elif confluence['confluence_score'] < 40:
            st.warning("⚠️ ZAYIF SİNYAL")
            st.write("Göstergeler karışık. Trading yapmak riskli.")
        else:
            st.info("📊 NÖTR DURUM")
            st.write("Net yön belli değil. Daha iyi setup beklemek mantıklı.")
        
        st.write(f"**Genel Değerlendirme:** {confluence['signal_strength']} sinyal gücü ile %{confluence['confluence_score']:.0f} confluence score.")
        
        # Auto-refresh option
        st.sidebar.checkbox("Otomatik yenileme (30s)", key='auto_refresh')
        
        if st.session_state.get('auto_refresh', False):
            import time
            time.sleep(30)
            st.rerun()
            
    except Exception as e:
        st.error(f"Bir hata oluştu: {str(e)}")
        st.info("Lütfen sembolu kontrol edip tekrar deneyin.")

# Information section
with st.expander("ℹ️ EMA Bias Analizi Nasıl Çalışır"):
    st.markdown("""
    **Exponential Moving Average (EMA) Bias Analizi**, piyasa yönünü ve gücünü belirlemek için çoklu EMA periyotları kullanan teknik bir analiz yöntemidir.
    
    **Temel Kavramlar:**
    - **Yükseliş Bias'ı:** Kısa vadeli EMA'lar uzun vadeli EMA'ların üzerinde, yukarı momentum gösterir
    - **Düşüş Bias'ı:** Kısa vadeli EMA'lar uzun vadeli EMA'ların altında, aşağı momentum gösterir
    - **Nötr Bias:** EMA'lar karışık veya birleşiyor, konsolidasyon gösterir
    
    **Kullanılan EMA Periyotları:**
    - EMA 45: Kısa vadeli trend
    - EMA 89: Orta vadeli trend
    - EMA 144: Uzun vadeli trend
    - EMA 200: Ana trend
    - EMA 276: Çok uzun vadeli trend
    
    **Bias Gücü Hesaplama:**
    Güç, bias yönüne göre doğru hizalanmış EMA sayısına göre hesaplanır.
    """)

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit • Data from Yahoo Finance*")
