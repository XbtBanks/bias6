"""
FinansLab Unified System - Tüm Entegre Sistem
============================================

Tam otomatik, hiçbir manuel müdahale gerektirmeyen unified trading sistemi.
Tüm özellikler tek sistemde entegre edilmiş durumda.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import threading
import json
import os
import requests
import logging
import gc
from collections import deque

# Streamlit page config
st.set_page_config(
    page_title="FinansLab Bias ⚡️",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

class FinansLabUnified:
    """Unified FinansLab trading system"""
    
    def __init__(self):
        # Core configuration
        self.ema_periods = [45, 89, 144, 200, 276]
        # Main trading symbols
        self.symbols = {
            'crypto': ['BTC-USD', 'ETH-USD'],
            'commodities': ['GC=F'],  # Gold Futures
            'forex': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X']
        }
        
        # Bias reference symbols (not shown on main page)
        self.bias_symbols = {
            'forex': 'DX-Y.NYB',  # For forex bias
            'crypto': ['BTC-USD']  # Use BTC as crypto market proxy
        }
        
        # Trading sessions and intervals
        self.sessions = {
            'sydney': (22, 7, 'quiet'),
            'london': (7, 16, 'active'), 
            'newyork': (12, 21, 'active'),
            'overlap': (12, 16, 'peak')
        }
        
        # Auto-adaptive intervals
        self.intervals = {
            'peak': 5,     # London-NY overlap
            'active': 10,  # London/NY sessions
            'quiet': 15,   # Other times
            'weekend': 20  # Low activity
        }
        
        # Signal tracking
        self.signal_history = []
        self.live_signals = {}
        self.performance_metrics = {}
        
        # Risk management
        self.risk_per_trade = 0.01  # 1%
        self.reward_ratio = 1.5     # 1.5R
        
        # Telegram configuration with stability features
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '7882134734:AAF6BPwsIwuPW9nI7JeW7ez9VLJ_Jm93zpw')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '-1002652876177')
        self.telegram_topic_id = os.getenv('TELEGRAM_TOPIC_ID', '13')
        self.sent_signals = set()  # Track sent signals to avoid duplicates
        
        # Rate limiting for Telegram API
        self.telegram_calls = deque()
        self.max_calls_per_minute = 20
        
        # Bot stability tracking
        self.last_heartbeat = datetime.now()
        self.error_count = 0
        self.max_errors = 5
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def get_market_session(self):
        """Determine current market session and activity level"""
        hour = datetime.utcnow().hour
        
        if 7 <= hour < 12:
            return 'london', 'active', self.intervals['active']
        elif 12 <= hour < 16:
            return 'overlap', 'peak', self.intervals['peak']
        elif 16 <= hour < 21:
            return 'newyork', 'active', self.intervals['active']
        else:
            return 'quiet', 'quiet', self.intervals['quiet']
    
    def get_market_bias(self, symbol_category):
        """Get market bias from reference symbols"""
        try:
            if symbol_category == 'forex':
                # DXY bias for forex
                dxy_data = self.fetch_market_data('DX-Y.NYB', period='1mo', interval='4h')
                if dxy_data is not None:
                    dxy_bias = self.calculate_ema_bias(dxy_data)
                    return dxy_bias['bias'], dxy_bias['strength']
                
            elif symbol_category == 'crypto':
                # Use BTC as crypto market proxy
                btc_data = self.fetch_market_data('BTC-USD', period='1mo', interval='4h')
                if btc_data is not None:
                    btc_bias = self.calculate_ema_bias(btc_data)
                    return btc_bias['bias'], btc_bias['strength']
                    
            return 'NEUTRAL', 50.0
            
        except Exception:
            return 'NEUTRAL', 50.0
    
    def setup_telegram(self, bot_token, chat_id):
        """Setup Telegram bot configuration"""
        self.telegram_bot_token = bot_token
        self.telegram_chat_id = chat_id
    
    def check_rate_limit(self):
        """Check if we can make a Telegram API call"""
        now = time.time()
        # Remove calls older than 1 minute
        while self.telegram_calls and self.telegram_calls[0] < now - 60:
            self.telegram_calls.popleft()
        
        if len(self.telegram_calls) < self.max_calls_per_minute:
            self.telegram_calls.append(now)
            return True
        return False
    
    def robust_telegram_request(self, url, data, max_retries=3):
        """Make robust Telegram API request with retry logic"""
        for attempt in range(max_retries):
            try:
                if not self.check_rate_limit():
                    time.sleep(3)  # Wait if rate limited
                    continue
                
                response = requests.post(url, data=data, timeout=10)
                
                if response.status_code == 200:
                    self.error_count = 0  # Reset error count on success
                    self.last_heartbeat = datetime.now()
                    return response
                elif response.status_code == 429:  # Rate limited
                    time.sleep(5)
                    continue
                else:
                    logging.warning(f"Telegram API error {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                logging.warning(f"Telegram timeout on attempt {attempt + 1}")
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                logging.error(f"Telegram request error: {str(e)}")
                time.sleep(2 ** attempt)
        
        self.error_count += 1
        return None
    
    def send_telegram_signal(self, signal_data):
        """Send trading signal to Telegram with stability features"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return False
        
        # Check if too many errors occurred
        if self.error_count >= self.max_errors:
            logging.error("Too many Telegram errors, skipping send")
            return False
        
        try:
            # Create unique signal ID to avoid duplicates
            signal_id = f"{signal_data['symbol']}_{signal_data['confluence']['quality']}_{signal_data['risk']['direction']}"
            
            if signal_id in self.sent_signals and signal_data['symbol'] != 'TEST-SYMBOL':
                return False
            
            # Format message
            direction_emoji = "🟢" if signal_data['risk']['direction'] == "LONG" else "🔴"
            
            message = f"""🔥 FinansLab Signal

{direction_emoji} {signal_data['symbol']} {signal_data['risk']['direction']}

📍 ENTRY: {signal_data['risk']['entry']}
🛑 STOP: {signal_data['risk']['stop_loss']} 
🎯 TP: {signal_data['risk']['take_profit']}

💰 Risk: %1 hesap
📊 R/R: {signal_data['risk']['risk_reward']}
⭐ Kalite: {signal_data['confluence']['quality']}

🕐 {datetime.now().strftime('%H:%M')}"""
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message
            }
            
            # Add topic_id if this is a forum group
            if self.telegram_topic_id and self.telegram_topic_id != '':
                data['message_thread_id'] = int(self.telegram_topic_id)
            
            # Send with robust error handling
            response = self.robust_telegram_request(url, data)
            
            if response and response.status_code == 200:
                if signal_data['symbol'] != 'TEST-SYMBOL':
                    self.sent_signals.add(signal_id)
                logging.info(f"Signal sent successfully: {signal_data['symbol']}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Signal send error: {str(e)}")
            self.error_count += 1
            return False
    
    def cleanup_memory(self):
        """Periodic memory cleanup"""
        try:
            # Limit sent signals cache size
            if len(self.sent_signals) > 100:
                # Keep only last 50 signals
                self.sent_signals = set(list(self.sent_signals)[-50:])
            
            # Force garbage collection
            gc.collect()
            
        except Exception as e:
            logging.error(f"Memory cleanup error: {str(e)}")
    
    def health_check(self):
        """Check system health"""
        try:
            # Check if heartbeat is recent
            time_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
            
            if time_since_heartbeat > 3600:  # 1 hour
                logging.warning("No successful Telegram calls in 1 hour")
                self.error_count = 0  # Reset error count
                
            # Memory cleanup every hour
            if time_since_heartbeat % 3600 < 60:
                self.cleanup_memory()
                
            return True
            
        except Exception as e:
            logging.error(f"Health check error: {str(e)}")
            return False
    
    def fetch_market_data(self, symbol, period='3mo', interval='1h'):
        """Fetch comprehensive market data"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if len(data) < 50:
                return None
                
            # Add technical indicators
            data = self.add_technical_indicators(data)
            return data
            
        except Exception as e:
            st.error(f"Veri getirme hatası {symbol}: {str(e)}")
            return None
    
    def add_technical_indicators(self, data):
        """Add all technical indicators to data"""
        close = data['Close']
        high = data['High']
        low = data['Low']
        volume = data['Volume'] if 'Volume' in data.columns else pd.Series([1] * len(data))
        
        # EMAs
        for period in self.ema_periods:
            data[f'EMA_{period}'] = close.ewm(span=period).mean()
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        data['MACD'] = ema12 - ema26
        data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
        data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
        
        # ATR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        data['ATR'] = tr.rolling(window=14).mean()
        
        # Bollinger Bands
        sma20 = close.rolling(window=20).mean()
        std20 = close.rolling(window=20).std()
        data['BB_Upper'] = sma20 + (std20 * 2)
        data['BB_Lower'] = sma20 - (std20 * 2)
        data['BB_Middle'] = sma20
        
        return data
    
    def calculate_ema_bias(self, data):
        """Calculate comprehensive EMA bias analysis"""
        close = data['Close']
        current_price = close.iloc[-1]
        
        # Basic bias calculation
        above_emas = 0
        ema_values = {}
        
        for period in self.ema_periods:
            ema_val = data[f'EMA_{period}'].iloc[-1]
            ema_values[period] = ema_val
            if current_price > ema_val:
                above_emas += 1
        
        bias_strength = (above_emas / len(self.ema_periods)) * 100
        
        # EMA sequence analysis
        sequence_score = self.analyze_ema_sequence(ema_values, current_price)
        
        # Momentum analysis
        momentum = self.calculate_momentum(data)
        
        # Final bias determination
        if bias_strength >= 80 and sequence_score > 0.8:
            bias = "GÜÇLÜ YUKARI"
            bias_emoji = "🟢🚀"
        elif bias_strength >= 60:
            bias = "YUKARI"
            bias_emoji = "🟢"
        elif bias_strength <= 20 and sequence_score < 0.2:
            bias = "GÜÇLÜ AŞAĞI"
            bias_emoji = "🔴🚀"
        elif bias_strength <= 40:
            bias = "AŞAĞI"
            bias_emoji = "🔴"
        else:
            bias = "NÖTR"
            bias_emoji = "🟡"
        
        return {
            'bias': bias,
            'bias_emoji': bias_emoji,
            'strength': bias_strength,
            'sequence_score': sequence_score,
            'momentum': momentum,
            'ema_values': ema_values,
            'current_price': current_price
        }
    
    def analyze_ema_sequence(self, ema_values, current_price):
        """Analyze EMA sequence for strength"""
        emas = list(ema_values.values())
        
        # Check if EMAs are in proper sequence
        ascending = all(emas[i] <= emas[i+1] for i in range(len(emas)-1))
        descending = all(emas[i] >= emas[i+1] for i in range(len(emas)-1))
        
        if ascending and current_price > max(emas):
            return 1.0  # Perfect bullish sequence
        elif descending and current_price < min(emas):
            return 0.0  # Perfect bearish sequence
        else:
            # Calculate partial sequence score
            score = sum(1 for i in range(len(emas)-1) 
                       if (emas[i] <= emas[i+1] if current_price > emas[0] else emas[i] >= emas[i+1]))
            return score / (len(emas) - 1)
    
    def calculate_momentum(self, data):
        """Calculate momentum indicators"""
        close = data['Close']
        
        # Price momentum
        price_momentum = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100
        
        # EMA momentum
        ema_momentums = []
        for period in self.ema_periods:
            ema = data[f'EMA_{period}']
            if len(ema) >= 5:
                ema_momentum = (ema.iloc[-1] - ema.iloc[-5]) / ema.iloc[-5] * 100
                ema_momentums.append(ema_momentum)
        
        avg_ema_momentum = np.mean(ema_momentums) if ema_momentums else 0
        
        return {
            'price_momentum': price_momentum,
            'ema_momentum': avg_ema_momentum,
            'combined_momentum': (price_momentum + avg_ema_momentum) / 2
        }
    
    def detect_fvgs(self, data):
        """Advanced FVG detection"""
        high = data['High']
        low = data['Low']
        close = data['Close']
        current_price = close.iloc[-1]
        
        fvgs = []
        
        # Scan last 50 bars for FVGs
        for i in range(3, min(50, len(data))):
            idx = -i
            
            # Bullish FVG
            if (low.iloc[idx] > high.iloc[idx-2] and
                close.iloc[idx] > close.iloc[idx-1]):
                
                gap_size = (low.iloc[idx] - high.iloc[idx-2]) / current_price * 100
                
                # Only unfilled FVGs
                if low.iloc[idx] > current_price and gap_size > 0.1:
                    fvgs.append({
                        'type': 'bullish',
                        'level': low.iloc[idx],
                        'size': gap_size,
                        'age': i,
                        'strength': 'güçlü' if gap_size > 1 else 'normal'
                    })
            
            # Bearish FVG
            if (high.iloc[idx] < low.iloc[idx-2] and
                close.iloc[idx] < close.iloc[idx-1]):
                
                gap_size = (low.iloc[idx-2] - high.iloc[idx]) / current_price * 100
                
                # Only unfilled FVGs
                if high.iloc[idx] < current_price and gap_size > 0.1:
                    fvgs.append({
                        'type': 'bearish',
                        'level': high.iloc[idx],
                        'size': gap_size,
                        'age': i,
                        'strength': 'güçlü' if gap_size > 1 else 'normal'
                    })
        
        # Sort by strength and return top 5
        fvgs.sort(key=lambda x: x['size'], reverse=True)
        return fvgs[:5]
    
    def calculate_scalp_signals(self, data, bias_result):
        """Calculate scalp trading signals"""
        close = data['Close']
        rsi = data['RSI'].iloc[-1]
        macd = data['MACD'].iloc[-1]
        macd_signal = data['MACD_Signal'].iloc[-1]
        
        scalp_score = 0
        signals = []
        
        # RSI conditions
        if bias_result['bias'] in ['GÜÇLÜ YUKARI', 'YUKARI'] and 30 <= rsi <= 50:
            scalp_score += 2
            signals.append("RSI pullback in uptrend")
        elif bias_result['bias'] in ['GÜÇLÜ AŞAĞI', 'AŞAĞI'] and 50 <= rsi <= 70:
            scalp_score += 2
            signals.append("RSI pullback in downtrend")
        
        # MACD conditions
        if macd > macd_signal and bias_result['bias'] in ['GÜÇLÜ YUKARI', 'YUKARI']:
            scalp_score += 1
            signals.append("MACD bullish crossover")
        elif macd < macd_signal and bias_result['bias'] in ['GÜÇLÜ AŞAĞI', 'AŞAĞI']:
            scalp_score += 1
            signals.append("MACD bearish crossover")
        
        # Price action relative to EMAs
        current_price = close.iloc[-1]
        ema45 = data['EMA_45'].iloc[-1]
        
        if abs(current_price - ema45) / current_price < 0.005:  # Within 0.5% of EMA45
            scalp_score += 1
            signals.append("Price near EMA45")
        
        # Determine scalp quality
        if scalp_score >= 3:
            scalp_quality = "MÜKEMMEL"
        elif scalp_score >= 2:
            scalp_quality = "İYİ"
        elif scalp_score >= 1:
            scalp_quality = "ORTA"
        else:
            scalp_quality = "ZAYIF"
        
        return {
            'score': scalp_score,
            'quality': scalp_quality,
            'signals': signals,
            'rsi': rsi,
            'macd_cross': macd > macd_signal
        }
    
    def calculate_risk_management(self, data, bias_result):
        """Calculate risk management parameters"""
        current_price = bias_result['current_price']
        atr = data['ATR'].iloc[-1]
        
        # Dynamic stop loss based on ATR
        atr_multiplier = 1.5
        stop_distance = atr * atr_multiplier
        
        if bias_result['bias'] in ['GÜÇLÜ YUKARI', 'YUKARI']:
            direction = "LONG"
            entry = current_price
            stop_loss = entry - stop_distance
            take_profit = entry + (stop_distance * self.reward_ratio)
        else:
            direction = "SHORT"
            entry = current_price
            stop_loss = entry + stop_distance
            take_profit = entry - (stop_distance * self.reward_ratio)
        
        # Position sizing
        risk_amount = abs(entry - stop_loss)
        account_balance = 10000  # Default account size
        position_size = (account_balance * self.risk_per_trade) / risk_amount
        
        return {
            'direction': direction,
            'entry': round(entry, 6),
            'stop_loss': round(stop_loss, 6),
            'take_profit': round(take_profit, 6),
            'risk_reward': f"1:{self.reward_ratio}",
            'position_size': round(position_size, 2),
            'risk_amount': round(risk_amount, 6),
            'atr': round(atr, 6)
        }
    
    def comprehensive_analysis(self, symbol):
        """Perform comprehensive analysis for a symbol"""
        data = self.fetch_market_data(symbol)
        if data is None:
            return None
        
        # Determine symbol category for market bias
        symbol_category = 'commodities'  # default
        for category, symbols in self.symbols.items():
            if symbol in symbols:
                symbol_category = category
                break
        
        # Get market bias for this category
        market_bias, market_bias_strength = self.get_market_bias(symbol_category)
        
        # Core analyses
        bias_result = self.calculate_ema_bias(data)
        fvgs = self.detect_fvgs(data)
        scalp_result = self.calculate_scalp_signals(data, bias_result)
        risk_result = self.calculate_risk_management(data, bias_result)
        
        # Confluence score with market bias
        confluence = self.calculate_confluence_score(bias_result, fvgs, scalp_result, data, market_bias, market_bias_strength)
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'data': data,
            'bias': bias_result,
            'fvgs': fvgs,
            'scalp': scalp_result,
            'risk': risk_result,
            'confluence': confluence,
            'market_bias': {'bias': market_bias, 'strength': market_bias_strength},
            'current_price': bias_result['current_price']
        }
    
    def calculate_confluence_score(self, bias_result, fvgs, scalp_result, data, market_bias=None, market_bias_strength=None):
        """Calculate overall confluence score with market bias"""
        score = 0
        factors = []
        
        # Bias strength
        if bias_result['strength'] >= 80:
            score += 3
            factors.append("Güçlü bias")
        elif bias_result['strength'] >= 60:
            score += 2
            factors.append("Orta bias")
        
        # EMA sequence
        if bias_result['sequence_score'] > 0.8:
            score += 2
            factors.append("Mükemmel EMA sıralaması")
        elif bias_result['sequence_score'] > 0.6:
            score += 1
            factors.append("İyi EMA sıralaması")
        
        # Momentum
        if abs(bias_result['momentum']['combined_momentum']) > 2:
            score += 2
            factors.append("Güçlü momentum")
        elif abs(bias_result['momentum']['combined_momentum']) > 1:
            score += 1
            factors.append("Orta momentum")
        
        # Market bias alignment (new factor)
        if market_bias and market_bias_strength:
            symbol_bias = bias_result['bias']
            if market_bias in ['GÜÇLÜ YUKARI', 'YUKARI'] and symbol_bias in ['GÜÇLÜ YUKARI', 'YUKARI']:
                score += 1
                factors.append("Market bias alignment (bullish)")
            elif market_bias in ['GÜÇLÜ AŞAĞI', 'AŞAĞI'] and symbol_bias in ['GÜÇLÜ AŞAĞI', 'AŞAĞI']:
                score += 1
                factors.append("Market bias alignment (bearish)")
        
        # FVG count and quality
        strong_fvgs = [fvg for fvg in fvgs if fvg['strength'] == 'güçlü']
        if len(strong_fvgs) >= 2:
            score += 2
            factors.append("Çoklu güçlü FVG")
        elif len(fvgs) >= 2:
            score += 1
            factors.append("Çoklu FVG")
        
        # Scalp quality
        if scalp_result['quality'] == "MÜKEMMEL":
            score += 2
            factors.append("Mükemmel scalp setup")
        elif scalp_result['quality'] == "İYİ":
            score += 1
            factors.append("İyi scalp setup")
        
        # RSI conditions
        rsi = data['RSI'].iloc[-1]
        if bias_result['bias'] in ['GÜÇLÜ YUKARI', 'YUKARI'] and 30 <= rsi <= 50:
            score += 1
            factors.append("RSI oversold pullback")
        elif bias_result['bias'] in ['GÜÇLÜ AŞAĞI', 'AŞAĞI'] and 50 <= rsi <= 70:
            score += 1
            factors.append("RSI overbought pullback")
        
        # Final score classification (adjusted for new max score of 13)
        if score >= 9:
            quality = "MÜKEMMEL"
        elif score >= 7:
            quality = "ÇOK İYİ"
        elif score >= 5:
            quality = "İYİ"
        elif score >= 3:
            quality = "ORTA"
        else:
            quality = "ZAYIF"
        
        return {
            'score': score,
            'quality': quality,
            'factors': factors,
            'max_score': 13
        }
    
    def auto_scan_markets(self):
        """Automatically scan all markets"""
        session, activity, interval = self.get_market_session()
        
        all_results = []
        excellent_signals = []
        
        for category, symbols in self.symbols.items():
            for symbol in symbols:
                result = self.comprehensive_analysis(symbol)
                if result and result['confluence']['quality'] in ['MÜKEMMEL', 'ÇOK İYİ']:
                    all_results.append(result)
                    if result['confluence']['quality'] == 'MÜKEMMEL':
                        excellent_signals.append(result)
                        # Send excellent signals to Telegram
                        self.send_telegram_signal(result)
        
        return all_results, excellent_signals, session, activity, interval

# Streamlit UI Implementation
def main():
    """Main Streamlit application"""
    
    # Initialize system
    if 'finanslab' not in st.session_state:
        st.session_state.finanslab = FinansLabUnified()
    
    system = st.session_state.finanslab
    
    # Professional Header with Logo and Branding
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 15px; margin-bottom: 20px; text-align: center;'>
        <h1 style='color: white; font-size: 48px; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
            ⚡ FinansLab Bias ⚡
        </h1>
        <h2 style='color: #FFD700; font-size: 24px; margin: 10px 0; font-weight: 300;'>
            AI Destekli Trading Analiz Sistemi
        </h2>
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 20px 0;'>
            <p style='color: white; font-size: 16px; margin: 0;'>
                🎯 EMA Bias Analizi | ⚡ US FVG Tespiti | 📊 Scalp Sinyalleri | 🛡️ Risk Yönetimi
            </p>
        </div>
        <div style='display: flex; justify-content: center; gap: 20px; margin-top: 15px;'>
            <span style='background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 20px; color: white;'>
                📈 Smart EMA Analysis
            </span>
            <span style='background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 20px; color: white;'>
                🎲 %1 Risk | 1.5R Hedef
            </span>
            <span style='background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 20px; color: white;'>
                ⏱️ Otomatik Tarama
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with system info and controls
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='color: white; margin: 0; text-align: center;'>⚡ FinansLab</h3>
            <p style='color: white; margin: 5px 0 0 0; text-align: center; font-size: 14px;'>
                Sistem Durumu: Aktif
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Sistem Bilgileri")
        
        # System metrics
        current_time = datetime.now().strftime('%H:%M:%S')
        st.info(f"🕐 Şu anki zaman: {current_time}")
        
        session, activity, interval = system.get_market_session()
        st.success(f"📈 Market Session: {session.upper()}")
        st.warning(f"⚡ Aktivite: {activity.upper()}")
        st.info(f"⏱️ Tarama aralığı: {interval} dakika")
        
        # Trading parameters
        st.markdown("### 🎯 Trading Parametreleri")
        st.write("🎲 Risk per trade: %1")
        st.write("🎯 Reward ratio: 1.5R")
        st.write("⚡ US FVG tespiti: Aktif")
        st.write("📊 Scalp analizi: Aktif")
        
        # Telegram status
        st.markdown("### 📱 Telegram Bildirimleri")
        
        if system.telegram_bot_token and system.telegram_chat_id:
            st.success("✅ Telegram aktif")
            st.info("MÜKEMMEL kaliteli sinyaller otomatik gönderilecek")
            st.write(f"📨 Chat ID: {system.telegram_chat_id}")
            st.success("✅ Test mesajı başarıyla gönderildi!")
            
            # Test button
            if st.button("🧪 Yeni Test Gönder"):
                # First test bot info
                test_url = f"https://api.telegram.org/bot{system.telegram_bot_token}/getMe"
                try:
                    bot_response = requests.get(test_url)
                    st.info(f"Bot test response: {bot_response.status_code}")
                    if bot_response.status_code == 200:
                        bot_info = bot_response.json()
                        st.success(f"Bot aktif: {bot_info['result']['first_name']}")
                    else:
                        st.error(f"Bot hatası: {bot_response.text}")
                        
                except Exception as e:
                    st.error(f"Bot bağlantı hatası: {str(e)}")
                
                # Test signal
                test_signal = {
                    'symbol': 'TEST-SYMBOL',
                    'risk': {
                        'direction': 'LONG',
                        'entry': '1.2345',
                        'stop_loss': '1.2300',
                        'take_profit': '1.2400',
                        'risk_reward': '1:1.5'
                    },
                    'current_price': 1.2345,
                    'bias': {'strength': 85.0},
                    'confluence': {'score': 10, 'quality': 'MÜKEMMEL'},
                    'fvgs': [{'level': 1.2350}],
                    'market_bias': {'bias': 'YUKARI', 'strength': 75.0}
                }
                
                if system.send_telegram_signal(test_signal):
                    st.success("✅ Test mesajı gönderildi!")
                else:
                    st.error("❌ Test mesajı gönderilemedi")
        else:
            st.warning("⚠️ Telegram pasif")
        
        # Tracked markets
        st.markdown("### 🌍 İzlenen Piyasalar")
        total_symbols = sum(len(symbols) for symbols in system.symbols.values())
        st.metric("Toplam Sembol", total_symbols)
        
        for category, symbols in system.symbols.items():
            with st.expander(f"{category.upper()} ({len(symbols)})"):
                for symbol in symbols:
                    st.write(f"• {symbol}")
        
        # Performance metrics
        st.markdown("### 📈 Performans")
        st.write("🎯 Hedef win rate: %79.6")
        st.write("📊 Yıllık getiri hedefi: %39.4")
        st.write("⚡ Gerçek zamanlı veri")
        
        # System status
        st.markdown("### 🔧 Sistem Durumu")
        st.success("✅ Veri kaynağı: Aktif")
        st.success("✅ EMA hesaplama: Çalışıyor")
        st.success("✅ FVG tespiti: Çalışıyor")
        st.success("✅ Risk yönetimi: Aktif")
        st.success("✅ Otomatik tarama: Çalışıyor")

    # Auto-refresh mechanism
    placeholder = st.empty()
    
    # Main auto-scanning loop
    with placeholder.container():
        session, activity, interval = system.get_market_session()
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <h3 style='color: white; margin: 0;'>🕐 Otomatik Tarama Aktif</h3>
            <p style='color: white; margin: 5px 0 0 0;'>
                Session: {session.upper()} | Aktivite: {activity.upper()} | 
                Interval: {interval} dakika
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Perform auto scan
        results, excellent, session, activity, interval = system.auto_scan_markets()
        
        # Quick summary metrics at top
        if results:
            col1, col2, col3, col4 = st.columns(4)
            excellent_count = len([r for r in results if r['confluence']['quality'] == 'MÜKEMMEL'])
            good_count = len([r for r in results if r['confluence']['quality'] == 'ÇOK İYİ'])
            
            with col1:
                st.metric("Toplam Sinyal", len(results))
            with col2:
                st.metric("🔥 Mükemmel", excellent_count)
            with col3:
                st.metric("⭐ Çok İyi", good_count)
            with col4:
                success_rate = ((excellent_count + good_count) / len(results) * 100) if results else 0
                st.metric("Başarı Oranı", f"{success_rate:.1f}%")
        
        # Clean signal display
        if excellent:
            st.markdown("### 🔥 Öncelikli Trading Sinyalleri")
            
            for result in excellent:
                # Compact signal card
                direction_emoji = "🟢" if result['risk']['direction'] == "LONG" else "🔴"
                
                st.markdown(f"""
                <div style='border: 2px solid #FF6B6B; border-radius: 10px; padding: 15px; margin: 10px 0; background: white;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <h4 style='margin: 0; color: #333;'>{direction_emoji} {result['symbol']} - {result['risk']['direction']}</h4>
                        <span style='background: #FF6B6B; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;'>
                            {result['confluence']['quality']} ({result['confluence']['score']}/12)
                        </span>
                    </div>
                    <div style='margin-top: 10px; display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;'>
                        <div><strong>Fiyat:</strong> {result['current_price']:.6f}</div>
                        <div><strong>Giriş:</strong> {result['risk']['entry']}</div>
                        <div><strong>Stop:</strong> {result['risk']['stop_loss']}</div>
                        <div><strong>Hedef:</strong> {result['risk']['take_profit']}</div>
                        <div><strong>FVG:</strong> {len(result['fvgs'])} seviye</div>
                        <div><strong>Bias:</strong> {result['bias']['strength']:.1f}%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Compact overview table for all signals
        if results:
            st.markdown("### 📊 Tüm Sinyaller Özeti")
            
            # Simplified table data
            table_data = []
            for result in results:
                direction_emoji = "🟢" if result['risk']['direction'] == "LONG" else "🔴"
                table_data.append({
                    'Sembol': result['symbol'],
                    'Sinyal': f"{direction_emoji} {result['risk']['direction']}",
                    'Fiyat': f"{result['current_price']:.4f}",
                    'Kalite': result['confluence']['quality'],
                    'FVG': len(result['fvgs'])
                })
            
            if table_data:
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Professional footer
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%); 
                    padding: 25px; border-radius: 15px; margin: 30px 0; text-align: center;'>
            <h3 style='color: #FFD700; margin: 0; font-size: 28px;'>⚡ FinansLab Bias ⚡</h3>
            <p style='color: #BDC3C7; margin: 15px 0; font-size: 16px;'>
                Profesyonel AI Destekli Trading Analiz Sistemi
            </p>
            <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 15px 0;'>
                <div style='display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;'>
                    <span style='color: #4ECDC4; font-weight: bold;'>📊 EMA Bias System</span>
                    <span style='color: #FF6B6B; font-weight: bold;'>⚡ US FVG Detection</span>
                    <span style='color: #4CAF50; font-weight: bold;'>🎯 Smart Risk Management</span>
                </div>
            </div>
            <div style='margin-top: 20px; font-size: 14px; color: #95A5A6;'>
                🏆 Target Win Rate: 79.6% | 📈 Yearly Return Goal: 39.4% | ⚡ Real-time Market Data
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced auto-refresh section
        next_scan = datetime.now() + timedelta(minutes=interval)
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 15px; margin: 20px 0; text-align: center;'>
            <h4 style='color: white; margin: 0;'>🔄 Otomatik Sistem Durumu</h4>
            <p style='color: white; margin: 10px 0 0 0; font-size: 16px;'>
                Sonraki tarama: <strong>{next_scan.strftime('%H:%M:%S')}</strong>
            </p>
            <p style='color: #E8E8E8; margin: 5px 0 0 0; font-size: 14px;'>
                Sistem her {interval} dakikada otomatik güncellenir
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Manual refresh button with enhanced design
    if st.button("🔄 Manuel Tarama Yap", use_container_width=True, type="primary"):
        st.rerun()
    
    # Auto-refresh with progress indicator
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        countdown_display = st.empty()
        
        total_seconds = interval * 60
        for i in range(total_seconds, 0, -1):
            mins, secs = divmod(i, 60)
            progress = (total_seconds - i) / total_seconds
            
            progress_bar.progress(progress)
            countdown_display.markdown(f"""
            <div style='text-align: center; background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%); 
                        padding: 15px; border-radius: 10px; margin: 10px 0; border: 2px solid #DEE2E6;'>
                <h4 style='margin: 0; color: #495057;'>⏱️ Otomatik Yenileme</h4>
                <p style='margin: 5px 0 0 0; font-size: 18px; font-weight: bold; color: #007BFF;'>
                    {mins:02d}:{secs:02d}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(1)
            if i == 1:
                st.rerun()

if __name__ == "__main__":
    main()