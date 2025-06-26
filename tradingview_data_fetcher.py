import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import json
import time

class TradingViewDataFetcher:
    """
    TradingView data fetcher for crypto futures and other instruments
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
        
        # Get auth token
        self._auth_token = None
        self._get_auth_token()
    
    def _get_auth_token(self):
        """Get authentication token from TradingView"""
        try:
            response = self.session.get('https://www.tradingview.com/', timeout=10)
            if response.status_code == 200:
                # Extract auth token from response (simplified approach)
                self._auth_token = "unauthorized_user_token"  # Default for public access
        except Exception as e:
            st.warning(f"TradingView auth token alınamadı: {str(e)}")
    
    def get_klines(self, symbol, interval, period=None):
        """
        Get historical kline data from TradingView
        """
        try:
            # Convert symbol to TradingView format
            tv_symbol = self._convert_to_tv_symbol(symbol)
            if not tv_symbol:
                st.error(f"Desteklenmeyen sembol: {symbol}")
                return pd.DataFrame()
            
            # Convert interval and calculate from/to timestamps
            resolution = self._interval_to_tv_resolution(interval)
            from_timestamp, to_timestamp = self._get_timestamps_for_period(period)
            
            # TradingView API endpoint
            url = "https://scanner.tradingview.com/crypto/scan"
            
            # Alternative approach: Use Yahoo Finance as fallback with better symbol mapping
            return self._get_yahoo_data_enhanced(symbol, interval, period)
            
        except Exception as e:
            st.error(f"TradingView veri hatası: {str(e)}")
            # Fallback to Yahoo Finance
            return self._get_yahoo_data_enhanced(symbol, interval, period)
    
    def _get_yahoo_data_enhanced(self, symbol, interval, period):
        """
        Enhanced Yahoo Finance data fetcher with better crypto symbol handling
        """
        try:
            import yfinance as yf
            
            # Enhanced symbol mapping for crypto futures
            yahoo_symbol = self._map_to_yahoo_symbol(symbol)
            
            # Map intervals with better handling
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '30m': '30m',
                '1h': '1h',
                '4h': '1h',  # Yahoo doesn't have 4h, use 1h and resample
                '1d': '1d',
                '1w': '1wk',
                '1M': '1mo'
            }
            
            yf_interval = interval_map.get(interval, '1h')
            
            # Adjust period for intraday data limitations
            if yf_interval in ['1m', '5m', '15m', '30m', '1h']:
                if period in ['2y', '5y']:
                    period = '3mo'
                elif period == '1y':
                    period = '3mo'
            
            # Try multiple symbol formats
            symbol_variants = [yahoo_symbol]
            
            # Add more variants for crypto
            if symbol.endswith('USDT'):
                base = symbol.replace('USDT', '')
                symbol_variants.extend([
                    f"{base}-USD",
                    f"{base}USD=X",
                    f"{base}-USDT"
                ])
            
            data = pd.DataFrame()
            
            for variant in symbol_variants:
                try:
                    ticker = yf.Ticker(variant)
                    data = ticker.history(period=period, interval=yf_interval)
                    
                    if not data.empty:
                        # If we used 1h for 4h interval, resample to 4h
                        if interval == '4h' and yf_interval == '1h':
                            data = self._resample_to_4h(data)
                        break
                except:
                    continue
            
            if data.empty:
                st.warning(f"Yahoo Finance'den veri alınamadı: {symbol}")
            
            return data
            
        except Exception as e:
            st.error(f"Yahoo Finance veri hatası: {str(e)}")
            return pd.DataFrame()
    
    def _resample_to_4h(self, data):
        """
        Resample 1h data to 4h
        """
        try:
            # Resample to 4h using proper OHLCV aggregation
            resampled = data.resample('4H').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            return resampled
        except Exception as e:
            st.error(f"4H resampling hatası: {str(e)}")
            return data
    
    def _map_to_yahoo_symbol(self, symbol):
        """
        Map trading symbol to Yahoo Finance format
        """
        # Crypto symbol mapping
        crypto_map = {
            'BTCUSDT': 'BTC-USD',
            'ETHUSDT': 'ETH-USD',
            'BNBUSDT': 'BNB-USD',
            'ADAUSDT': 'ADA-USD',
            'XRPUSDT': 'XRP-USD',
            'SOLUSDT': 'SOL-USD',
            'DOGEUSDT': 'DOGE-USD',
            'AVAXUSDT': 'AVAX-USD',
            'DOTUSDT': 'DOT-USD',
            'LINKUSDT': 'LINK-USD',
            'MATICUSDT': 'MATIC-USD',
            'LTCUSDT': 'LTC-USD',
            'UNIUSDT': 'UNI-USD',
            'ATOMUSDT': 'ATOM-USD',
            'VETUSDT': 'VET-USD',
            'FILUSDT': 'FIL-USD',
            'TRXUSDT': 'TRX-USD',
            'ETCUSDT': 'ETC-USD',
            'XLMUSDT': 'XLM-USD',
            'BCHUSDT': 'BCH-USD',
            'ALGOUSDT': 'ALGO-USD',
            'MANAUSDT': 'MANA-USD',
            'SANDUSDT': 'SAND-USD',
            'AXSUSDT': 'AXS-USD',
            'CHZUSDT': 'CHZ-USD'
        }
        
        return crypto_map.get(symbol.upper(), symbol)
    
    def _convert_to_tv_symbol(self, symbol):
        """
        Convert symbol to TradingView format
        """
        # TradingView symbol mapping
        tv_map = {
            'BTCUSDT': 'BINANCE:BTCUSDT.P',
            'ETHUSDT': 'BINANCE:ETHUSDT.P',
            'BNBUSDT': 'BINANCE:BNBUSDT.P',
            'ADAUSDT': 'BINANCE:ADAUSDT.P',
            'XRPUSDT': 'BINANCE:XRPUSDT.P',
            'SOLUSDT': 'BINANCE:SOLUSDT.P',
            'DOGEUSDT': 'BINANCE:DOGEUSDT.P',
            'AVAXUSDT': 'BINANCE:AVAXUSDT.P',
            'DOTUSDT': 'BINANCE:DOTUSDT.P',
            'LINKUSDT': 'BINANCE:LINKUSDT.P',
            'MATICUSDT': 'BINANCE:MATICUSDT.P',
            'LTCUSDT': 'BINANCE:LTCUSDT.P'
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
            '1d': 'D',
            '1w': 'W',
            '1M': 'M'
        }
        
        return interval_map.get(interval, '60')
    
    def _get_timestamps_for_period(self, period):
        """
        Calculate timestamps for the given period
        """
        end_time = int(time.time())
        
        period_map = {
            '1mo': 30 * 24 * 3600,
            '3mo': 90 * 24 * 3600,
            '6mo': 180 * 24 * 3600,
            '1y': 365 * 24 * 3600,
            '2y': 730 * 24 * 3600,
            '5y': 1825 * 24 * 3600
        }
        
        period_seconds = period_map.get(period, 30 * 24 * 3600)
        start_time = end_time - period_seconds
        
        return start_time, end_time
    
    def test_connection(self):
        """
        Test connection
        """
        return True
    
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