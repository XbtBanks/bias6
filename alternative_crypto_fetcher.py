import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import time

class AlternativeCryptoFetcher:
    """
    Alternative crypto data fetcher using CoinGecko and other public APIs
    """
    
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        
    def get_klines(self, symbol, interval, period=None):
        """
        Get historical price data for crypto symbols
        """
        try:
            # Convert symbol to CoinGecko format
            coin_id = self._symbol_to_coingecko_id(symbol)
            if not coin_id:
                st.error(f"Desteklenmeyen sembol: {symbol}")
                return pd.DataFrame()
            
            # Get days for the period
            days = self._period_to_days(period)
            
            # CoinGecko API endpoint
            url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
            
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': self._interval_to_coingecko(interval)
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 429:
                st.warning("API rate limit aşıldı, 60 saniye bekleyin...")
                time.sleep(60)
                response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                st.error(f"CoinGecko API hatası: {response.status_code}")
                return pd.DataFrame()
            
            data = response.json()
            
            if 'prices' not in data:
                st.error("Fiyat verisi bulunamadı")
                return pd.DataFrame()
            
            # Convert to DataFrame
            prices = data['prices']
            volumes = data.get('total_volumes', [])
            
            # Create OHLCV-like data (CoinGecko only provides price points)
            df_data = []
            
            for i, (timestamp, price) in enumerate(prices):
                volume = volumes[i][1] if i < len(volumes) else 0
                
                # Create OHLC from price (simplified approach)
                df_data.append({
                    'timestamp': timestamp,
                    'Open': price,
                    'High': price * 1.001,  # Small variation for visualization
                    'Low': price * 0.999,
                    'Close': price,
                    'Volume': volume
                })
            
            df = pd.DataFrame(df_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Ensure numeric types
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            st.error(f"Veri alırken hata: {str(e)}")
            return pd.DataFrame()
    
    def _symbol_to_coingecko_id(self, symbol):
        """
        Convert trading symbol to CoinGecko coin ID
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
            'BCHUSDT': 'bitcoin-cash',
            'ALGOUSDT': 'algorand',
            'MANAUSDT': 'decentraland',
            'SANDUSDT': 'the-sandbox',
            'AXSUSDT': 'axie-infinity',
            'CHZUSDT': 'chiliz'
        }
        
        return symbol_map.get(symbol.upper())
    
    def _period_to_days(self, period):
        """
        Convert period to days
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
    
    def _interval_to_coingecko(self, interval):
        """
        Convert interval to CoinGecko format
        """
        # CoinGecko has limited interval options
        interval_map = {
            '1m': 'minutely',
            '5m': 'minutely',
            '15m': 'minutely',
            '30m': 'minutely',
            '1h': 'hourly',
            '4h': 'hourly',
            '1d': 'daily',
            '1w': 'daily',
            '1M': 'daily'
        }
        
        return interval_map.get(interval, 'daily')
    
    def test_connection(self):
        """
        Test connection to CoinGecko API
        """
        try:
            url = f"{self.coingecko_base}/ping"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                return True
            else:
                st.error(f"CoinGecko API test başarısız: {response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"Bağlantı testi başarısız: {str(e)}")
            return False
    
    def get_supported_symbols(self):
        """
        Get supported crypto symbols
        """
        return [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'LINKUSDT',
            'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'VETUSDT',
            'FILUSDT', 'TRXUSDT', 'ETCUSDT', 'XLMUSDT', 'BCHUSDT',
            'ALGOUSDT', 'MANAUSDT', 'SANDUSDT', 'AXSUSDT', 'CHZUSDT'
        ]