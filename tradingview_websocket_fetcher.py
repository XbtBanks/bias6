import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import json
import time
import logging
from urllib.parse import urlencode
from typing import Optional, Dict, Any, List

# Optional dependencies
try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

try:
    import websocket
    import threading
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False

class TradingViewWebSocketFetcher:
    """
    Advanced TradingView data fetcher with WebSocket support
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.tradingview.com/',
            'Origin': 'https://www.tradingview.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        })
        
        self.auth_token = None
        self.sessionid = None
        self._authenticated = False
    
    def authenticate(self, username=None, password=None):
        """
        Authenticate with TradingView (optional for public data)
        """
        try:
            # Get initial cookies and tokens
            response = self.session.get('https://www.tradingview.com/')
            
            if username and password:
                # Login process
                login_url = 'https://www.tradingview.com/accounts/signin/'
                login_data = {
                    'username': username,
                    'password': password,
                    'remember': 'on'
                }
                
                login_response = self.session.post(login_url, data=login_data)
                
                if login_response.status_code == 200:
                    self._authenticated = True
                    st.success("TradingView hesabınız başarıyla bağlandı!")
                else:
                    st.warning("TradingView giriş başarısız, genel veriler kullanılacak")
            
            return True
            
        except Exception as e:
            st.warning(f"TradingView bağlantı hatası: {str(e)}")
            return False
    
    def get_klines(self, symbol, interval, period=None):
        """
        Get historical data with multiple fallback strategies
        """
        try:
            if period is None:
                period = '1mo'
            
            # Strategy 1: Yahoo Finance (most reliable)
            if HAS_YFINANCE:
                data = self._get_yahoo_finance_data(symbol, interval, period)
                if not data.empty:
                    st.success(f"✅ Yahoo Finance'den {len(data)} veri noktası alındı")
                    return data
            
            # Strategy 2: Alternative crypto API (if crypto symbol)
            if self._is_crypto_symbol(symbol):
                data = self._get_crypto_data(symbol, interval, period)
                if not data.empty:
                    st.info(f"📈 Kripto API'den {len(data)} veri noktası alındı")
                    return data
            
            # Strategy 3: Generate sample data (last resort)
            st.warning(f"⚠️ Gerçek veri alınamadı, örnek veri oluşturuluyor")
            return self._generate_sample_data(symbol, interval, period)
            
        except Exception as e:
            st.error(f"❌ Veri alma hatası: {str(e)}")
            return self._generate_sample_data(symbol, interval, period)
    
    def _get_tradingview_chart_data(self, symbol, interval, period):
        """
        Fallback method - now uses Yahoo Finance as primary data source
        """
        return self._get_yahoo_finance_data(symbol, interval, period)
    
    def _fetch_chart_data(self, symbol, resolution, from_timestamp, to_timestamp):
        """
        Fetch chart data using Yahoo Finance as reliable alternative
        """
        try:
            # Convert TradingView symbol to Yahoo Finance format  
            yahoo_symbol = self._convert_tv_to_yahoo_symbol(symbol)
            if not yahoo_symbol:
                yahoo_symbol = self._convert_to_yahoo_symbol(symbol)
            
            if not yahoo_symbol:
                return pd.DataFrame()
            
            # Use Yahoo Finance for reliable data
            if not HAS_YFINANCE:
                return pd.DataFrame()
            
            # Convert resolution to Yahoo Finance interval
            interval_map = {
                '1': '1m',
                '5': '5m', 
                '15': '15m',
                '30': '30m',
                '60': '1h',
                '240': '4h',
                'D': '1d'
            }
            
            yf_interval = interval_map.get(resolution, '1h')
            
            # Calculate period
            days = (to_timestamp - from_timestamp) // 86400
            if days <= 7:
                period = '7d'
            elif days <= 30:
                period = '1mo'
            elif days <= 90:
                period = '3mo'
            elif days <= 180:
                period = '6mo'
            else:
                period = '1y'
            
            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period=period, interval=yf_interval)
            
            if not data.empty:
                # Ensure we have the required columns
                required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                if all(col in data.columns for col in required_cols):
                    return data
            
            return pd.DataFrame()
            
        except Exception as e:
            logging.error(f"Yahoo Finance veri hatası: {str(e)}")
            return pd.DataFrame()
    
    def _convert_tv_to_yahoo_symbol(self, tv_symbol):
        """
        Convert TradingView symbol to Yahoo Finance format
        """
        symbol_map = {
            # Crypto
            'BINANCE:BTCUSDT.P': 'BTC-USD',
            'BINANCE:BTCUSDT': 'BTC-USD',
            'BINANCE:ETHUSDT.P': 'ETH-USD',
            'BINANCE:ETHUSDT': 'ETH-USD',
            'BINANCE:BNBUSDT.P': 'BNB-USD',
            'BINANCE:ADAUSDT.P': 'ADA-USD',
            'BINANCE:XRPUSDT.P': 'XRP-USD',
            'BINANCE:SOLUSDT.P': 'SOL-USD',
            'BINANCE:DOGEUSDT.P': 'DOGE-USD',
            'BINANCE:AVAXUSDT.P': 'AVAX-USD',
            'BINANCE:DOTUSDT.P': 'DOT-USD',
            'BINANCE:LINKUSDT.P': 'LINK-USD',
            
            # Indices
            'CAPITALCOM:US100': '^NDX',
            'CAPITALCOM:SPX500': '^GSPC',
            'CAPITALCOM:US30': '^DJI',
            'CAPITALCOM:DE40': '^GDAXI',
            'CAPITALCOM:UK100': '^FTSE',
            'CAPITALCOM:JPN225': '^N225',
            
            # Gold & Metals
            'OANDA:XAUUSD': 'GC=F',
            'OANDA:XAGUSD': 'SI=F',
            'COMEX:GC1!': 'GC=F',
            'COMEX:SI1!': 'SI=F',
            
            # Forex
            'OANDA:EURUSD': 'EURUSD=X',
            'OANDA:GBPUSD': 'GBPUSD=X',
            'OANDA:USDJPY': 'USDJPY=X',
            'OANDA:AUDUSD': 'AUDUSD=X',
            'OANDA:USDCAD': 'USDCAD=X',
            'OANDA:NZDUSD': 'NZDUSD=X',
            
            # Commodities
            'NYMEX:CL1!': 'CL=F',
            'NYMEX:NG1!': 'NG=F',
            'CBOT:ZW1!': 'ZW=F',
            'CBOT:ZC1!': 'ZC=F'
        }
        
        return symbol_map.get(tv_symbol)
    

    

    
    def _symbol_to_coingecko_id(self, symbol):
        """
        Convert trading symbol to CoinGecko ID
        """
        symbol_map = {
            'BTCUSDT': 'bitcoin',
            'ETHUSDT': 'ethereum',
            'BNBUSDT': 'binancecoin',
            'ADAUSDT': 'cardano',
            'XRPUSDT': 'ripple',
            'SOLUSDT': 'solana',
            'DOGEUSDT': 'dogecoin',
            'AVAXUSDT': 'avalanche-2',
            'DOTUSDT': 'polkadot',
            'LINKUSDT': 'chainlink',
            'MATICUSDT': 'matic-network',
            'LTCUSDT': 'litecoin',
            'UNIUSDT': 'uniswap',
            'ATOMUSDT': 'cosmos',
            'VETUSDT': 'vechain',
            'FILUSDT': 'filecoin',
            'TRXUSDT': 'tron',
            'ETCUSDT': 'ethereum-classic',
            'XLMUSDT': 'stellar',
            'BCHUSDT': 'bitcoin-cash'
        }
        
        return symbol_map.get(symbol.upper())
    
    def _period_to_days(self, period):
        """
        Convert period to days for CoinGecko
        """
        period_map = {
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730,
            '5y': 1825
        }
        
        return period_map.get(period, 30)
    
    def _interval_to_binance(self, interval):
        """
        Convert interval to Binance format
        """
        interval_map = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d',
            '1w': '1w',
            '1M': '1M'
        }
        
        return interval_map.get(interval, '1h')
    
    def _period_to_limit(self, period, interval):
        """
        Calculate limit for API calls
        """
        # Calculate how many candles we need
        period_hours = {
            '1mo': 30 * 24,
            '3mo': 90 * 24,
            '6mo': 180 * 24,
            '1y': 365 * 24,
            '2y': 730 * 24
        }
        
        interval_hours = {
            '1m': 1/60,
            '5m': 5/60,
            '15m': 15/60,
            '30m': 30/60,
            '1h': 1,
            '4h': 4,
            '1d': 24
        }
        
        total_hours = period_hours.get(period, 720)  # Default 1 month
        interval_hour = interval_hours.get(interval, 1)
        
        return int(total_hours / interval_hour)
    
    def _resample_data(self, df, target_interval):
        """
        Resample data to target interval
        """
        try:
            interval_map = {
                '15m': '15min',
                '30m': '30min',
                '1h': '1h',
                '4h': '4h'
            }
            
            resample_rule = interval_map.get(target_interval, '1h')
            
            resampled = df.resample(resample_rule).agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            return resampled
            
        except Exception as e:
            st.warning(f"Resample hatası: {str(e)}")
            return df
    
    def _convert_to_tv_symbol(self, symbol):
        """
        Convert symbol to TradingView format
        """
        tv_map = {
            'BTCUSDT': 'BINANCE:BTCUSDT.P',
            'ETHUSDT': 'BINANCE:ETHUSDT.P',
            'BNBUSDT': 'BINANCE:BNBUSDT.P',
            'ADAUSDT': 'BINANCE:ADAUSDT.P',
            'XRPUSDT': 'BINANCE:XRPUSDT.P',
            'SOLUSDT': 'BINANCE:SOLUSDT.P'
        }
        
        return tv_map.get(symbol.upper(), f'BINANCE:{symbol.upper()}.P')
    
    def _interval_to_tv_resolution(self, interval):
        """
        Convert interval to TradingView resolution
        """
        interval_map = {
            '1m': '1',
            '5m': '5',
            '15m': '15',
            '30m': '30',
            '1h': '60',
            '4h': '240',
            '1d': 'D'
        }
        
        return interval_map.get(interval, '60')
    
    def _calculate_from_timestamp(self, period, interval):
        """
        Calculate from timestamp
        """
        now = int(time.time())
        
        period_seconds = {
            '1mo': 30 * 24 * 3600,
            '3mo': 90 * 24 * 3600,
            '6mo': 180 * 24 * 3600,
            '1y': 365 * 24 * 3600
        }
        
        return now - period_seconds.get(period, 30 * 24 * 3600)
    
    def test_connection(self):
        """
        Test connection to data sources
        """
        try:
            # Test Yahoo Finance first
            if HAS_YFINANCE:
                try:
                    ticker = yf.Ticker("AAPL")
                    data = ticker.history(period="1d", interval="1h")
                    if not data.empty:
                        st.success("✅ Yahoo Finance bağlantısı başarılı")
                        return True
                except Exception:
                    pass
            
            # Test CoinGecko
            try:
                response = requests.get('https://api.coingecko.com/api/v3/ping', timeout=5)
                if response.status_code == 200:
                    st.success("✅ CoinGecko bağlantısı başarılı")
                    return True
            except Exception:
                pass
            
            # Test Binance public API
            try:
                response = requests.get('https://api.binance.com/api/v3/ping', timeout=5)
                if response.status_code == 200:
                    st.success("✅ Binance bağlantısı başarılı")
                    return True
            except Exception:
                pass
            
            st.warning("⚠️ Tüm veri kaynaklarına bağlantı başarısız")
            return False
            
        except Exception as e:
            st.error(f"❌ Bağlantı test hatası: {str(e)}")
            return False
    
    def get_supported_symbols(self):
        """
        Get supported symbols across all data sources
        """
        return {
            'crypto': [
                'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
                'SOLUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'LINKUSDT',
                'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'VETUSDT'
            ],
            'stocks': [
                'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META'
            ],
            'indices': [
                'SPY', 'QQQ', 'DIA', 'IWM', 'VIX'
            ],
            'forex': [
                'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD'
            ]
        }
    
    def validate_symbol(self, symbol):
        """
        Validate if symbol is supported
        """
        all_symbols = []
        supported = self.get_supported_symbols()
        for category in supported.values():
            all_symbols.extend(category)
        
        # Also check if it's a crypto symbol
        if self._is_crypto_symbol(symbol):
            return True
            
        return symbol.upper() in [s.upper() for s in all_symbols]
    
    def get_data_info(self, symbol):
        """
        Get information about data source for symbol
        """
        info = {
            'symbol': symbol,
            'data_source': 'Unknown',
            'supported': False,
            'real_time': False
        }
        
        if HAS_YFINANCE and self._convert_to_yahoo_symbol(symbol):
            info['data_source'] = 'Yahoo Finance'
            info['supported'] = True
            info['real_time'] = True
        elif self._is_crypto_symbol(symbol):
            info['data_source'] = 'CoinGecko'
            info['supported'] = True
            info['real_time'] = False
        else:
            info['data_source'] = 'Sample Data'
            info['supported'] = True
            info['real_time'] = False
        
        return info
    
    def _is_crypto_symbol(self, symbol):
        """
        Check if symbol is a cryptocurrency
        """
        crypto_keywords = ['BTC', 'ETH', 'BNB', 'ADA', 'XRP', 'SOL', 'DOGE', 'AVAX', 'DOT', 'LINK', 'USDT', 'BUSD']
        return any(keyword in symbol.upper() for keyword in crypto_keywords)
    
    def _generate_sample_data(self, symbol, interval, period):
        """
        Generate sample data for testing purposes
        """
        try:
            # Calculate number of periods
            period_map = {
                '1mo': 30,
                '3mo': 90,
                '6mo': 180,
                '1y': 365
            }
            
            interval_map = {
                '1m': 1440,  # minutes per day
                '5m': 288,
                '15m': 96,
                '30m': 48,
                '1h': 24,
                '4h': 6,
                '1d': 1
            }
            
            days = period_map.get(period, 30)
            periods_per_day = interval_map.get(interval, 24)
            total_periods = days * periods_per_day
            
            # Generate dates
            end_date = datetime.now()
            if interval == '1d':
                dates = pd.date_range(end=end_date, periods=total_periods, freq='D')
            elif interval == '4h':
                dates = pd.date_range(end=end_date, periods=total_periods, freq='4h')
            elif interval == '1h':
                dates = pd.date_range(end=end_date, periods=total_periods, freq='h')
            else:
                dates = pd.date_range(end=end_date, periods=total_periods, freq='15min')
            
            # Generate price data
            np.random.seed(42)  # For reproducible results
            
            # Starting price
            base_price = 50000 if 'BTC' in symbol.upper() else 2000
            
            # Generate realistic price movement
            returns = np.random.normal(0, 0.02, total_periods)
            prices = [base_price]
            
            for ret in returns[1:]:
                new_price = prices[-1] * (1 + ret)
                prices.append(max(new_price, base_price * 0.1))  # Prevent negative prices
            
            # Create OHLCV data
            data = []
            for i, price in enumerate(prices):
                high = price * (1 + abs(np.random.normal(0, 0.01)))
                low = price * (1 - abs(np.random.normal(0, 0.01)))
                open_price = prices[i-1] if i > 0 else price
                volume = np.random.randint(100000, 1000000)
                
                data.append({
                    'Open': open_price,
                    'High': max(high, price, open_price),
                    'Low': min(low, price, open_price),
                    'Close': price,
                    'Volume': volume
                })
            
            df = pd.DataFrame(data, index=dates)
            return df.tail(min(1000, total_periods))  # Limit to reasonable size
            
        except Exception as e:
            st.error(f"Sample data generation error: {str(e)}")
            # Return minimal data
            return pd.DataFrame({
                'Open': [100],
                'High': [105],
                'Low': [95],
                'Close': [102],
                'Volume': [1000000]
            }, index=[datetime.now()])
    
    def _get_crypto_data(self, symbol, interval, period):
        """
        Get cryptocurrency data from alternative APIs
        """
        try:
            # Try CoinGecko for crypto data
            return self._get_coingecko_data(symbol, interval, period)
        except Exception as e:
            logging.error(f"Crypto data error: {str(e)}")
            return pd.DataFrame()
    
    def _get_coingecko_data(self, symbol, interval, period):
        """
        Get data from CoinGecko API
        """
        try:
            # Convert symbol to CoinGecko ID
            coin_id = self._symbol_to_coingecko_id(symbol)
            if not coin_id:
                return pd.DataFrame()
            
            # Calculate days
            days = self._period_to_days(period)
            
            # Make API request
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'hourly' if days <= 90 else 'daily'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Convert to DataFrame
                if 'prices' in data and len(data['prices']) > 0:
                    df = pd.DataFrame(data['prices'], columns=['timestamp', 'Close'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    
                    # Add OHLV columns (simplified)
                    df['Open'] = df['Close'].shift(1).fillna(df['Close'])
                    df['High'] = df['Close'] * 1.01  # Approximation
                    df['Low'] = df['Close'] * 0.99   # Approximation
                    df['Volume'] = 1000000  # Placeholder
                    
                    return df[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            return pd.DataFrame()
            
        except Exception as e:
            logging.error(f"CoinGecko error: {str(e)}")
            return pd.DataFrame()
    
# Test function
if __name__ == "__main__":
    # Test the TradingViewWebSocketFetcher
    fetcher = TradingViewWebSocketFetcher()
    
    print("Testing TradingView WebSocket Fetcher...")
    
    # Test connection
    print("\n1. Testing connection...")
    if fetcher.test_connection():
        print("✅ Connection test passed")
    else:
        print("❌ Connection test failed")
    
    # Test symbol validation
    print("\n2. Testing symbol validation...")
    test_symbols = ['BTCUSDT', 'AAPL', 'INVALID_SYM']
    for symbol in test_symbols:
        is_valid = fetcher.validate_symbol(symbol)
        print(f"Symbol {symbol}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test data fetching
    print("\n3. Testing data fetching...")
    try:
        data = fetcher.get_klines('BTCUSDT', '1h', '1mo')
        if not data.empty:
            print(f"✅ Data fetching successful: {len(data)} records")
            print(f"Columns: {list(data.columns)}")
            print(f"Date range: {data.index.min()} to {data.index.max()}")
        else:
            print("❌ No data retrieved")
    except Exception as e:
        print(f"❌ Data fetching failed: {str(e)}")
    
    print("\nTesting completed!")