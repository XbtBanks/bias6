import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import time

class CryptoDataFetcher:
    """
    Alternative crypto data fetcher using public APIs
    """
    
    def __init__(self):
        self.base_url = "https://api.binance.com"
        
    def get_klines(self, symbol, interval, period=None):
        """
        Get historical kline data from Binance public API
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            interval (str): Kline interval (e.g., '1m', '5m', '1h', '1d')
            period (str): Time period (e.g., '1mo', '3mo', '1y')
            
        Returns:
            pd.DataFrame: OHLCV data
        """
        try:
            # Convert period to limit
            limit = self._period_to_limit(period, interval)
            
            # Binance public API endpoint
            url = f"{self.base_url}/api/v3/klines"
            
            params = {
                'symbol': symbol.upper(),
                'interval': interval,
                'limit': limit
            }
            
            # Make request
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                st.error(f"API hatası: {response.status_code} - {response.text}")
                return pd.DataFrame()
            
            data = response.json()
            
            if not data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Assign column names
            df.columns = [
                'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ]
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Convert OHLCV to float
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                df[col] = df[col].astype(float)
            
            # Keep only OHLCV columns
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            return df
            
        except requests.exceptions.RequestException as e:
            st.error(f"Ağ hatası: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Veri işleme hatası: {str(e)}")
            return pd.DataFrame()
    
    def _period_to_limit(self, period, interval):
        """
        Convert period string to limit number
        """
        # Define multipliers for different intervals
        interval_minutes = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '4h': 240,
            '1d': 1440,
            '1w': 10080,
            '1M': 43200
        }
        
        # Get minutes per interval
        minutes_per_interval = interval_minutes.get(interval, 60)
        
        # Convert period to days
        period_days = {
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730,
            '5y': 1825
        }
        
        days = period_days.get(period, 30)
        
        # Calculate limit (max 1000 for Binance API)
        total_minutes = days * 24 * 60
        limit = min(total_minutes // minutes_per_interval, 1000)
        
        return max(limit, 100)  # Minimum 100 data points
    
    def test_connection(self, symbol="BTCUSDT"):
        """
        Test connection to Binance public API
        """
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {'symbol': symbol}
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                return True
            else:
                st.error(f"API test başarısız: {response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"Bağlantı testi başarısız: {str(e)}")
            return False
    
    def get_all_symbols(self):
        """
        Get all available trading symbols from Binance
        """
        try:
            url = f"{self.base_url}/api/v3/exchangeInfo"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING']
                return symbols
            else:
                return []
                
        except Exception as e:
            st.error(f"Sembol listesi alınamadı: {str(e)}")
            return []
    
    def get_usdt_pairs(self):
        """
        Get popular USDT trading pairs
        """
        # Return a curated list of popular USDT pairs
        popular_pairs = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'LINKUSDT',
            'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'VETUSDT',
            'FILUSDT', 'TRXUSDT', 'ETCUSDT', 'XLMUSDT', 'BCHUSDT',
            'ALGOUSDT', 'MANAUSDT', 'SANDUSDT', 'AXSUSDT', 'CHZUSDT'
        ]
        
        return popular_pairs