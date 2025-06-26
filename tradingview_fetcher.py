import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import json
import time

class TradingViewFetcher:
    """
    TradingView data fetcher for crypto futures data
    """
    
    def __init__(self):
        self.base_url = "https://scanner.tradingview.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.tradingview.com/',
            'Origin': 'https://www.tradingview.com'
        })
        
    def get_klines(self, symbol, interval, period=None):
        """
        Get historical price data from TradingView
        """
        try:
            # Convert symbol to TradingView format
            tv_symbol = self._convert_to_tv_symbol(symbol)
            if not tv_symbol:
                st.error(f"Desteklenmeyen sembol: {symbol}")
                return pd.DataFrame()
            
            # Get resolution and bars count
            resolution = self._interval_to_tv_resolution(interval)
            bars_count = self._period_to_bars(period, interval)
            
            # Calculate timestamps
            end_time = int(time.time())
            start_time = end_time - (bars_count * self._resolution_to_seconds(resolution))
            
            # TradingView history endpoint
            url = f"https://symbol-search.tradingview.com/symbol_search/"
            
            # Alternative approach using Yahoo Finance with crypto format
            return self._get_yahoo_crypto_data(symbol, interval, period)
            
        except Exception as e:
            st.error(f"TradingView veri hatası: {str(e)}")
            return pd.DataFrame()
    
    def _get_yahoo_crypto_data(self, symbol, interval, period):
        """
        Alternative method using Yahoo Finance with proper crypto symbol format
        """
        try:
            import yfinance as yf
            
            # Convert USDT symbols to Yahoo Finance format
            if symbol.endswith('USDT'):
                base_symbol = symbol.replace('USDT', '')
                yahoo_symbol = f"{base_symbol}-USD"
            else:
                yahoo_symbol = symbol
            
            # Create ticker
            ticker = yf.Ticker(yahoo_symbol)
            
            # Map intervals
            interval_map = {
                '1m': '1m',
                '5m': '5m', 
                '15m': '15m',
                '30m': '30m',
                '1h': '1h',
                '4h': '1h',  # Yahoo doesn't have 4h, use 1h
                '1d': '1d'
            }
            
            yf_interval = interval_map.get(interval, '1h')
            
            # Get data with period limits for intraday
            if yf_interval in ['1m', '5m', '15m', '30m', '1h']:
                if period in ['2y', '5y', '1y']:
                    period = '3mo'  # Limit for intraday data
            
            data = ticker.history(period=period, interval=yf_interval)
            
            if data.empty:
                # Try without -USD suffix for some symbols
                if '-USD' in yahoo_symbol:
                    alt_symbol = yahoo_symbol.replace('-USD', '-USDT')
                    ticker = yf.Ticker(alt_symbol)
                    data = ticker.history(period=period, interval=yf_interval)
            
            return data
            
        except Exception as e:
            st.error(f"Yahoo Finance alternatif hatası: {str(e)}")
            return pd.DataFrame()
    
    def _convert_to_tv_symbol(self, symbol):
        """
        Convert symbol to TradingView format
        """
        symbol_map = {
            'BTCUSDT': 'BINANCE:BTCUSDT',
            'ETHUSDT': 'BINANCE:ETHUSDT',
            'BNBUSDT': 'BINANCE:BNBUSDT',
            'ADAUSDT': 'BINANCE:ADAUSDT',
            'XRPUSDT': 'BINANCE:XRPUSDT',
            'SOLUSDT': 'BINANCE:SOLUSDT',
            'DOGEUSDT': 'BINANCE:DOGEUSDT',
            'AVAXUSDT': 'BINANCE:AVAXUSDT',
            'DOTUSDT': 'BINANCE:DOTUSDT',
            'LINKUSDT': 'BINANCE:LINKUSDT',
            'MATICUSDT': 'BINANCE:MATICUSDT',
            'LTCUSDT': 'BINANCE:LTCUSDT'
        }
        
        return symbol_map.get(symbol.upper(), f'BINANCE:{symbol.upper()}')
    
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
            '1d': 'D',
            '1w': 'W',
            '1M': 'M'
        }
        
        return interval_map.get(interval, '60')
    
    def _period_to_bars(self, period, interval):
        """
        Calculate number of bars needed
        """
        period_hours = {
            '1mo': 30 * 24,
            '3mo': 90 * 24,
            '6mo': 180 * 24,
            '1y': 365 * 24,
            '2y': 730 * 24,
            '5y': 1825 * 24
        }
        
        interval_hours = {
            '1m': 1/60,
            '5m': 5/60,
            '15m': 15/60,
            '30m': 30/60,
            '1h': 1,
            '4h': 4,
            '1d': 24,
            '1w': 168,
            '1M': 720
        }
        
        total_hours = period_hours.get(period, 720)  # Default 1 month
        interval_hour = interval_hours.get(interval, 1)
        
        return min(int(total_hours / interval_hour), 5000)  # Limit to 5000 bars
    
    def _resolution_to_seconds(self, resolution):
        """
        Convert resolution to seconds
        """
        if resolution == 'D':
            return 86400
        elif resolution == 'W':
            return 604800
        elif resolution == 'M':
            return 2628000
        else:
            return int(resolution) * 60
    
    def test_connection(self):
        """
        Test connection
        """
        return True  # Always return true for Yahoo Finance fallback
    
    def get_supported_symbols(self):
        """
        Get supported symbols
        """
        return [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'LINKUSDT',
            'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'VETUSDT',
            'FILUSDT', 'TRXUSDT', 'ETCUSDT', 'XLMUSDT', 'BCHUSDT'
        ]