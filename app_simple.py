import streamlit as st
import pandas as pd
from reliable_data_fetcher import ReliableDataFetcher
from simple_trading_engine import SimpleTradingEngine

# Page configuration
st.set_page_config(
    page_title="FinansLab - Simple Trading",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🎯 FinansLab - Basit Trading Sistemi</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Ayarlar")
        
        symbol = st.text_input("Sembol", value="BTCUSDT.P").upper()
        interval = st.selectbox("Zaman Dilimi", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
        time_period = st.selectbox("Dönem", ["1mo", "3mo", "6mo", "1y"], index=1)
        
        analyze_button = st.button("🔍 ANALİZ ET", type="primary")
    
    if analyze_button:
        analyze_symbol(symbol, interval, time_period)

def analyze_symbol(symbol, interval, time_period):
    try:
        with st.spinner(f"{symbol} analiz ediliyor..."):
            # Veri al
            data_fetcher = ReliableDataFetcher()
            data = data_fetcher.get_klines(symbol, interval, time_period)
            
            if data.empty:
                st.error("Veri alınamadı. Sembol veya ayarları kontrol edin.")
                return
            
            st.success(f"✅ {len(data)} veri noktası alındı")
            
            # Basit analiz
            engine = SimpleTradingEngine()
            analysis = engine.get_simple_signal(data, symbol)
            
            # 1. YÖN göster
            show_direction(analysis)
            
            # 2. İŞLEM SİNYALİ göster
            show_signal(analysis)
            
            # Özet bilgi
            show_summary(analysis)
            
    except Exception as e:
        st.error(f"Hata: {e}")

def show_direction(analysis):
    direction = analysis['direction']
    
    if 'Strong Bullish' in direction:
        color = "#27ae60"
        icon = "🟢🟢"
    elif 'Bullish' in direction:
        color = "#27ae60"
        icon = "🟢"
    elif 'Strong Bearish' in direction:
        color = "#e74c3c"
        icon = "🔴🔴"
    elif 'Bearish' in direction:
        color = "#e74c3c"
        icon = "🔴"
    else:
        color = "#f39c12"
        icon = "🟡"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color} 0%, #2c3e50 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        margin: 30px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5em;">YÖN</h1>
        <h1 style="color: white; margin: 20px 0; font-size: 4em;">{icon}</h1>
        <h1 style="color: white; margin: 10px 0; font-size: 2.8em;">{direction}</h1>
    </div>
    """, unsafe_allow_html=True)

def show_signal(analysis):
    signal = analysis['signal']
    confidence = analysis['confidence']
    
    if 'Strong Buy' in signal:
        color = "#27ae60"
        icon = "🚀"
        text = "GÜÇLÜ ALIM"
    elif 'Buy' in signal:
        color = "#27ae60"
        icon = "📈"
        text = "ALIM"
    elif 'Strong Sell' in signal:
        color = "#e74c3c"
        icon = "📉"
        text = "GÜÇLÜ SATIM"
    elif 'Sell' in signal:
        color = "#e74c3c"
        icon = "📉"
        text = "SATIM"
    else:
        color = "#f39c12"
        icon = "⏸️"
        text = "BEKLE"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color} 0%, #2c3e50 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        margin: 30px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5em;">İŞLEM SİNYALİ</h1>
        <h1 style="color: white; margin: 20px 0; font-size: 4em;">{icon}</h1>
        <h1 style="color: white; margin: 10px 0; font-size: 2.8em;">{text}</h1>
        <h2 style="color: #ecf0f1; margin: 20px 0; font-size: 1.8em;">Güven: %{confidence}</h2>
    </div>
    """, unsafe_allow_html=True)

def show_summary(analysis):
    st.markdown("### 📊 Özet")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Fiyat", f"${analysis['price']:.2f}")
    
    with col2:
        st.metric("🎯 Yön", analysis['direction'])
    
    with col3:
        st.metric("⚡ Sinyal", analysis['signal'])
    
    st.info(f"**Açıklama:** {analysis['reason']}")
    
    st.markdown("---")
    st.markdown("**🎯 Bu sistem sadece YÖN ve İŞLEM SİNYALİ gösterir. Başka analiz yoktur.**")

if __name__ == "__main__":
    main()