import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta

class ReliableDataFetcher:
    """
    Reliable data fetcher using yfinance for authentic market data
    """
    
    def __init__(self):
        self.symbol_map = self._create_symbol_mapping()
    
    def _period_to_days(self, period):
        """Convert period string to number of days"""
        if period.endswith('d'):
            return int(period[:-1])
        elif period.endswith('mo'):
            return int(period[:-2]) * 30
        elif period.endswith('y'):
            return int(period[:-1]) * 365
        elif period.endswith('M'):
            return int(period[:-1]) * 30
        else:
            return 60  # Default fallback
    
    def _create_symbol_mapping(self):
        """
        Map TradingView symbols to Yahoo Finance symbols
        """
        return {
            # Crypto Futures (.P symbols)
            'BTCUSDT.P': 'BTC-USD',
            'ETHUSDT.P': 'ETH-USD',
            'BNBUSDT.P': 'BNB-USD',
            'ADAUSDT.P': 'ADA-USD',
            'XRPUSDT.P': 'XRP-USD',
            'SOLUSDT.P': 'SOL-USD',
            'DOGEUSDT.P': 'DOGE-USD',
            'AVAXUSDT.P': 'AVAX-USD',
            'DOTUSDT.P': 'DOT-USD',
            'LINKUSDT.P': 'LINK-USD',
            'MATICUSDT.P': 'MATIC-USD',
            'LTCUSDT.P': 'LTC-USD',
            'BCHUSDT.P': 'BCH-USD',
            'EOSUSDT.P': 'EOS-USD',
            'TRXUSDT.P': 'TRX-USD',
            
            # Crypto Spot
            'BTC-USD': 'BTC-USD',
            'ETH-USD': 'ETH-USD',
            'BNB-USD': 'BNB-USD',
            'ADA-USD': 'ADA-USD',
            'XRP-USD': 'XRP-USD',
            'SOL-USD': 'SOL-USD',
            'DOGE-USD': 'DOGE-USD',
            'AVAX-USD': 'AVAX-USD',
            'DOT-USD': 'DOT-USD',
            'LINK-USD': 'LINK-USD',
            
            # Forex - Yahoo Finance format
            'EURUSD': 'EURUSD=X',
            'GBPUSD': 'GBPUSD=X',
            'JPYUSD': 'USDJPY=X',  # JPY/USD is actually USD/JPY in Yahoo Finance
            
            # Indices - Yahoo Finance format
            'US100': '^NDX',   # NASDAQ 100
            'SP500': '^GSPC',  # S&P 500
            
            # Gold - Yahoo Finance format
            'XAUUSD': 'GC=F'   # Gold futures
        }
    
    def get_klines(self, symbol, interval, period):
        """
        Get historical OHLCV data from Yahoo Finance
        """
        try:
            # Handle crypto futures (.P symbols) by removing .P suffix
            if symbol.endswith('.P'):
                base_symbol = symbol.replace('.P', '')
                # Try to map the base symbol first
                yahoo_symbol = self.symbol_map.get(base_symbol, None)
                if not yahoo_symbol:
                    # Convert BTCUSDT to BTC-USD format
                    if base_symbol.endswith('USDT'):
                        crypto_base = base_symbol.replace('USDT', '')
                        yahoo_symbol = f"{crypto_base}-USD"
                    elif base_symbol.endswith('USDC'):
                        crypto_base = base_symbol.replace('USDC', '')
                        yahoo_symbol = f"{crypto_base}-USD"
                    else:
                        yahoo_symbol = base_symbol
            else:
                # Convert TradingView symbol to Yahoo Finance symbol
                yahoo_symbol = self.symbol_map.get(symbol, symbol)
            
            if not yahoo_symbol:
                st.error(f"Sembol desteklenmiyor: {symbol}")
                return pd.DataFrame()
            
            # Map intervals to Yahoo Finance format
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '10m': '5m',  # Will resample 5m to 10m
                '15m': '15m',
                '20m': '15m',  # Will resample 15m to 20m
                '30m': '30m',
                '45m': '30m',  # Will resample 30m to 45m
                '1h': '1h',
                '90m': '1h',  # Will resample 1h to 90m
                '2h': '1h',   # Will resample 1h to 2h
                '4h': '1h',   # Will resample to 4h
                '6h': '1h',   # Will resample 1h to 6h
                '8h': '1h',   # Will resample 1h to 8h
                '1d': '1d'
            }
            
            yf_interval = interval_map.get(interval, '1h')
            
            # Adjust period for intraday data limitations only if period exceeds limits
            # Only apply restrictions to actual short-term intervals, not resampled ones
            actual_short_intervals = ['1m', '5m', '15m', '30m']
            if yf_interval in actual_short_intervals and interval in actual_short_intervals:
                # Yahoo Finance has strict limitations for intraday data
                original_period = period
                if yf_interval == '1m':
                    # 1-minute data: max 7 days
                    if self._period_to_days(period) > 7:
                        period = '7d'
                        st.warning(f"1 dakika verisi için dönem {original_period}'den 7 güne düşürüldü")
                elif yf_interval in ['5m', '15m']:
                    # 5m and 15m data: max 60 days
                    if self._period_to_days(period) > 60:
                        period = '60d'
                        st.warning(f"Kısa vadeli veriler için dönem {original_period}'den 60 güne düşürüldü")
                elif yf_interval == '30m':
                    # 30m data: max 60 days
                    if self._period_to_days(period) > 60:
                        period = '60d'
                        st.warning(f"30 dakika verisi için dönem {original_period}'den 60 güne düşürüldü")
            
            # Create ticker and fetch data
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period=period, interval=yf_interval)
            
            if data.empty:
                st.error(f"Yahoo Finance'den veri alınamadı: {yahoo_symbol}")
                return pd.DataFrame()
            
            # Resample to target intervals if needed
            if interval == '4h' and yf_interval == '1h':
                data = self._resample_to_4h(data)
            elif interval == '10m' and yf_interval == '5m':
                data = self._resample_to_10m(data)
            elif interval == '20m' and yf_interval == '15m':
                data = self._resample_to_20m(data)
            elif interval == '45m' and yf_interval == '30m':
                data = self._resample_to_45m(data)
            elif interval == '90m' and yf_interval == '1h':
                data = self._resample_to_90m(data)
            elif interval == '2h' and yf_interval == '1h':
                data = self._resample_to_2h(data)
            elif interval == '6h' and yf_interval == '1h':
                data = self._resample_to_6h(data)
            elif interval == '8h' and yf_interval == '1h':
                data = self._resample_to_8h(data)
            
            # Ensure we have the required columns
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in data.columns for col in required_cols):
                st.error("Gerekli veri sütunları bulunamadı")
                return pd.DataFrame()
            
            # Clean data
            data = data.dropna()
            
            if len(data) == 0:
                st.error("Temizlenen veri boş")
                return pd.DataFrame()
            

            return data
            
        except Exception as e:
            st.error(f"Veri alma hatası: {str(e)}")
            return pd.DataFrame()
    
    def _resample_to_4h(self, data):
        """
        Resample 1h data to 4h intervals
        """
        try:
            # Resample using proper OHLCV aggregation
            resampled = data.resample('4h').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            return resampled
            
        except Exception as e:
            st.warning(f"4h resampling hatası: {str(e)}")
            return data
    
    def _resample_to_10m(self, data):
        """
        Resample 5m data to 10m intervals
        """
        try:
            # Resample using proper OHLCV aggregation
            resampled = data.resample('10min').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            return resampled
            
        except Exception as e:
            st.warning(f"10m resampling hatası: {str(e)}")
            return data
    
    def _resample_to_20m(self, data):
        """Resample 15m data to 20m intervals"""
        try:
            resampled = data.resample('20min').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
            return resampled
        except Exception as e:
            st.warning(f"20m resampling hatası: {str(e)}")
            return data
    
    def _resample_to_45m(self, data):
        """Resample 30m data to 45m intervals"""
        try:
            resampled = data.resample('45min').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
            return resampled
        except Exception as e:
            st.warning(f"45m resampling hatası: {str(e)}")
            return data
    
    def _resample_to_90m(self, data):
        """Resample 1h data to 90m intervals"""
        try:
            resampled = data.resample('90min').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
            return resampled
        except Exception as e:
            st.warning(f"90m resampling hatası: {str(e)}")
            return data
    
    def _resample_to_2h(self, data):
        """Resample 1h data to 2h intervals"""
        try:
            resampled = data.resample('2h').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
            return resampled
        except Exception as e:
            st.warning(f"2h resampling hatası: {str(e)}")
            return data
    
    def _resample_to_6h(self, data):
        """Resample 1h data to 6h intervals"""
        try:
            resampled = data.resample('6h').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
            return resampled
        except Exception as e:
            st.warning(f"6h resampling hatası: {str(e)}")
            return data
    
    def _resample_to_8h(self, data):
        """Resample 1h data to 8h intervals"""
        try:
            resampled = data.resample('8h').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
            return resampled
        except Exception as e:
            st.warning(f"8h resampling hatası: {str(e)}")
            return data
    
    def test_connection(self):
        """
        Test connection by fetching a sample symbol
        """
        try:
            ticker = yf.Ticker('BTC-USD')
            data = ticker.history(period='1d', interval='1h')
            return not data.empty
        except:
            return False
    
    def get_supported_symbols(self):
        """
        Get list of supported symbols
        """
        return list(self.symbol_map.keys())
    
    def get_symbol_info(self, symbol):
        """
        Get basic information about a symbol
        """
        try:
            yahoo_symbol = self.symbol_map.get(symbol, symbol)
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            
            return {
                'name': info.get('longName', symbol),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'Unknown'),
                'sector': info.get('sector', 'Unknown')
            }
        except:
            return {
                'name': symbol,
                'currency': 'USD',
                'exchange': 'Unknown',
                'sector': 'Unknown'
            }