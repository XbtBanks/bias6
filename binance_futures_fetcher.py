import os
import pandas as pd
import numpy as np
import requests
import hmac
import hashlib
import time
from datetime import datetime, timedelta
import streamlit as st

class BinanceFuturesFetcher:
    """
    Binance Futures data fetcher using authenticated API
    """
    
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_SECRET_KEY')
        
        if not self.api_key or not self.api_secret:
            raise ValueError("Binance API anahtarları bulunamadı.")
        
        self.base_url = "https://fapi.binance.com"  # Futures API endpoint
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key
        })
    
    def _generate_signature(self, params):
        """
        Generate signature for authenticated requests
        """
        if not self.api_secret:
            return ""
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def get_klines(self, symbol, interval, period=None):
        """
        Get historical kline data from Binance Futures
        """
        try:
            # Calculate limit based on period
            limit = self._period_to_limit(period, interval)
            
            # Prepare parameters
            params = {
                'symbol': symbol.upper(),
                'interval': interval,
                'limit': limit
            }
            
            # For futures, we can use public endpoint first (no signature needed)
            url = f"{self.base_url}/fapi/v1/klines"
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 451:
                # If blocked, try with authentication
                params['timestamp'] = int(time.time() * 1000)
                params['signature'] = self._generate_signature(params)
                response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                st.error(f"Binance Futures API hatası: {response.status_code} - {response.text}")
                return pd.DataFrame()
            
            data = response.json()
            
            if not data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
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
            
        except Exception as e:
            st.error(f"Binance Futures veri hatası: {str(e)}")
            return pd.DataFrame()
    
    def _period_to_limit(self, period, interval):
        """
        Convert period to limit for API call
        """
        interval_minutes = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '4h': 240,
            '1d': 1440,
            '1w': 10080
        }
        
        period_days = {
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730,
            '5y': 1825
        }
        
        minutes_per_interval = interval_minutes.get(interval, 60)
        days = period_days.get(period, 30)
        
        total_minutes = days * 24 * 60
        limit = min(total_minutes // minutes_per_interval, 1500)  # Max 1500 for futures
        
        return max(limit, 100)
    
    def get_futures_symbols(self):
        """
        Get all futures trading symbols
        """
        try:
            url = f"{self.base_url}/fapi/v1/exchangeInfo"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING']
                return sorted(symbols)
            else:
                return []
                
        except Exception as e:
            st.error(f"Futures sembolleri alınamadı: {str(e)}")
            return []
    
    def get_popular_futures(self):
        """
        Get popular futures symbols
        """
        return [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'LINKUSDT',
            'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'VETUSDT',
            'FILUSDT', 'TRXUSDT', 'ETCUSDT', 'XLMUSDT', 'BCHUSDT',
            'ALGOUSDT', 'MANAUSDT', 'SANDUSDT', 'AXSUSDT', 'CHZUSDT',
            'GMTUSDT', 'AAVEUSDT', 'SUSHIUSDT', 'COMPUSDT', 'YFIUSDT'
        ]
    
    def test_connection(self):
        """
        Test Binance Futures API connection
        """
        try:
            url = f"{self.base_url}/fapi/v1/ping"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                return True
            else:
                st.error(f"Binance Futures bağlantı testi başarısız: {response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"Bağlantı testi başarısız: {str(e)}")
            return False
    
    def get_symbol_info(self, symbol):
        """
        Get symbol information
        """
        try:
            url = f"{self.base_url}/fapi/v1/exchangeInfo"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for s in data['symbols']:
                    if s['symbol'] == symbol.upper():
                        return s
                return None
            else:
                return None
                
        except Exception as e:
            st.error(f"Sembol bilgisi alınamadı: {str(e)}")
            return None