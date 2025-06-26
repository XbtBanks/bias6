import os
import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime, timedelta
import streamlit as st

class BinanceDataFetcher:
    """
    Binance data fetcher for crypto market data
    """
    
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_SECRET_KEY')
        
        if not self.api_key or not self.api_secret:
            raise ValueError("Binance API anahtarları bulunamadı. Lütfen BINANCE_API_KEY ve BINANCE_SECRET_KEY'i ayarlayın.")
        
        try:
            self.client = Client(self.api_key, self.api_secret)
            # Test connection
            self.client.ping()
        except Exception as e:
            raise ConnectionError(f"Binance API'ye bağlanılamadı: {str(e)}")
    
    def get_klines(self, symbol, interval, period=None, start_time=None, end_time=None):
        """
        Get historical kline data from Binance
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            interval (str): Kline interval (e.g., '1m', '5m', '1h', '1d')
            period (str): Time period (e.g., '1mo', '3mo', '1y') - optional
            start_time (datetime): Start time - optional
            end_time (datetime): End time - optional
            
        Returns:
            pd.DataFrame: OHLCV data
        """
        try:
            # Convert period to start_time if provided
            if period and not start_time:
                end_time = datetime.now()
                if period == '1mo':
                    start_time = end_time - timedelta(days=30)
                elif period == '3mo':
                    start_time = end_time - timedelta(days=90)
                elif period == '6mo':
                    start_time = end_time - timedelta(days=180)
                elif period == '1y':
                    start_time = end_time - timedelta(days=365)
                elif period == '2y':
                    start_time = end_time - timedelta(days=730)
                elif period == '5y':
                    start_time = end_time - timedelta(days=1825)
                else:
                    start_time = end_time - timedelta(days=30)  # Default to 1 month
            
            # Get klines from Binance
            klines = self.client.get_historical_klines(
                symbol,
                interval,
                start_str=start_time.strftime('%d %b %Y %H:%M:%S') if start_time else None,
                end_str=end_time.strftime('%d %b %Y %H:%M:%S') if end_time else None
            )
            
            if not klines:
                return pd.DataFrame()
            
            # Convert to DataFrame with proper column assignment
            column_names = [
                'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ]
            
            # Create DataFrame and assign columns properly
            df = pd.DataFrame(data=klines)
            if len(df.columns) >= len(column_names):
                df = df.iloc[:, :len(column_names)]
                df.columns = column_names
            else:
                # Fallback if fewer columns than expected
                for i, col in enumerate(column_names[:len(df.columns)]):
                    df.columns.values[i] = col
            
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
            st.error(f"Binance'den veri alırken hata: {str(e)}")
            return pd.DataFrame()
    
    def get_symbol_info(self, symbol):
        """
        Get symbol information
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            dict: Symbol information
        """
        try:
            info = self.client.get_symbol_info(symbol)
            return info
        except Exception as e:
            st.error(f"Sembol bilgisi alınırken hata: {str(e)}")
            return None
    
    def get_all_symbols(self):
        """
        Get all available trading symbols
        
        Returns:
            list: List of all symbols
        """
        try:
            exchange_info = self.client.get_exchange_info()
            symbols = [s['symbol'] for s in exchange_info['symbols'] if s['status'] == 'TRADING']
            return symbols
        except Exception as e:
            st.error(f"Sembol listesi alınırken hata: {str(e)}")
            return []
    
    def get_usdt_pairs(self):
        """
        Get all USDT trading pairs
        
        Returns:
            list: List of USDT pairs
        """
        try:
            all_symbols = self.get_all_symbols()
            usdt_pairs = [s for s in all_symbols if s.endswith('USDT')]
            return sorted(usdt_pairs)
        except Exception as e:
            st.error(f"USDT çiftleri alınırken hata: {str(e)}")
            return []
    
    def test_connection(self):
        """
        Test Binance API connection
        
        Returns:
            bool: True if connection successful
        """
        try:
            self.client.ping()
            return True
        except Exception as e:
            st.error(f"Binance bağlantı testi başarısız: {str(e)}")
            return False