import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import os
import streamlit as st

class TradingViewAuthenticatedFetcher:
    """
    Authenticated TradingView data fetcher using your personal account
    Provides access to premium data feeds and better rate limits
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.username = os.getenv('TRADINGVIEW_USERNAME')
        self.password = os.getenv('TRADINGVIEW_PASSWORD')
        self.auth_token = None
        self.session_id = None
        
        # Standard headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.tradingview.com/',
            'Origin': 'https://www.tradingview.com'
        })
        
        # Authenticate on initialization
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with TradingView using your credentials"""
        try:
            if not self.username or not self.password:
                st.warning("TradingView credentials not found. Using public access.")
                return False
            
            # Step 1: Get initial session
            response = self.session.get('https://www.tradingview.com/', timeout=10)
            
            # Step 2: Login with credentials
            login_data = {
                'username': self.username,
                'password': self.password,
                'remember': 'on'
            }
            
            login_response = self.session.post(
                'https://www.tradingview.com/accounts/signin/',
                data=login_data,
                timeout=10
            )
            
            if login_response.status_code == 200:
                # Extract session info
                self._extract_session_info(login_response)
                st.success("TradingView authenticated successfully!")
                return True
            else:
                st.warning("TradingView authentication failed. Using public access.")
                return False
                
        except Exception as e:
            st.warning(f"TradingView authentication error: {str(e)}")
            return False
    
    def _extract_session_info(self, response):
        """Extract session information from login response"""
        try:
            # Look for auth token in cookies or response
            for cookie in self.session.cookies:
                if 'sessionid' in cookie.name.lower():
                    self.session_id = cookie.value
                elif 'auth' in cookie.name.lower():
                    self.auth_token = cookie.value
                    
            # Update headers with auth info
            if self.auth_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
        except Exception as e:
            print(f"Session extraction error: {e}")
    
    def get_klines(self, symbol, interval, period=None):
        """
        Get historical data using authenticated TradingView access
        
        Args:
            symbol (str): Trading symbol (e.g., 'BTCUSDT', 'EURUSD', 'XAUUSD')
            interval (str): Timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
            period (str): Time period ('1mo', '3mo', '6mo', '1y')
        
        Returns:
            pd.DataFrame: OHLCV data
        """
        try:
            # Convert symbol to TradingView format
            tv_symbol = self._convert_symbol(symbol)
            tv_interval = self._convert_interval(interval)
            
            # Calculate time range
            end_time = int(datetime.now().timestamp())
            start_time = self._calculate_start_time(period, end_time)
            
            # Prepare request
            url = "https://scanner.tradingview.com/symbol"
            params = {
                'symbol': tv_symbol,
                'fields': 'base_name,logoid,update_mode,type,typespecs',
                'no_404': 'true'
            }
            
            # Get symbol info first
            symbol_response = self.session.get(url, params=params, timeout=10)
            
            if symbol_response.status_code != 200:
                return self._fallback_to_public_api(symbol, interval, period)
            
            # Get historical data
            history_url = "https://api.tradingview.com/v1/history"
            history_params = {
                'symbol': tv_symbol,
                'resolution': tv_interval,
                'from': start_time,
                'to': end_time,
                'countback': 5000
            }
            
            history_response = self.session.get(history_url, params=history_params, timeout=15)
            
            if history_response.status_code == 200:
                data = history_response.json()
                return self._parse_tradingview_data(data)
            else:
                return self._fallback_to_public_api(symbol, interval, period)
                
        except Exception as e:
            print(f"TradingView authenticated fetch error: {e}")
            return self._fallback_to_public_api(symbol, interval, period)
    
    def _convert_symbol(self, symbol):
        """Convert symbol to TradingView format"""
        symbol_mapping = {
            # Crypto futures
            'BTC.P': 'BINANCE:BTCUSDT.P',
            'ETH.P': 'BINANCE:ETHUSDT.P',
            'SOL.P': 'BINANCE:SOLUSDT.P',
            'BNB.P': 'BINANCE:BNBUSDT.P',
            'XRP.P': 'BINANCE:XRPUSDT.P',
            'ADA.P': 'BINANCE:ADAUSDT.P',
            
            # Forex
            'EURUSD': 'FX_IDC:EURUSD',
            'GBPUSD': 'FX_IDC:GBPUSD',
            'USDJPY': 'FX_IDC:USDJPY',
            'JPYUSD': 'FX_IDC:USDJPY',
            'AUDUSD': 'FX_IDC:AUDUSD',
            'USDCAD': 'FX_IDC:USDCAD',
            
            # Commodities
            'XAUUSD': 'TVC:GOLD',
            'XAGUSD': 'TVC:SILVER',
            'CRUDE': 'TVC:USOIL',
            
            # Indices
            'US100': 'TVC:NDX',
            'SP500': 'TVC:SPX',
            'DJI': 'TVC:DJI',
            'DAX': 'TVC:DAX'
        }
        
        return symbol_mapping.get(symbol, f'BINANCE:{symbol}')
    
    def _convert_interval(self, interval):
        """Convert interval to TradingView format"""
        interval_mapping = {
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
        
        return interval_mapping.get(interval, '60')
    
    def _calculate_start_time(self, period, end_time):
        """Calculate start time based on period"""
        if not period:
            period = '3mo'
            
        period_mapping = {
            '1d': 1,
            '7d': 7,
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730
        }
        
        days = period_mapping.get(period, 90)
        return end_time - (days * 24 * 60 * 60)
    
    def _parse_tradingview_data(self, data):
        """Parse TradingView API response to DataFrame"""
        try:
            if data.get('s') != 'ok':
                return None
            
            timestamps = data.get('t', [])
            opens = data.get('o', [])
            highs = data.get('h', [])
            lows = data.get('l', [])
            closes = data.get('c', [])
            volumes = data.get('v', [])
            
            if not timestamps:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame({
                'timestamp': [datetime.fromtimestamp(ts) for ts in timestamps],
                'Open': opens,
                'High': highs,
                'Low': lows,
                'Close': closes,
                'Volume': volumes if volumes else [0] * len(timestamps)
            })
            
            df.set_index('timestamp', inplace=True)
            return df
            
        except Exception as e:
            print(f"Data parsing error: {e}")
            return None
    
    def _fallback_to_public_api(self, symbol, interval, period):
        """Fallback to public API if authenticated access fails"""
        from reliable_data_fetcher import ReliableDataFetcher
        
        fallback_fetcher = ReliableDataFetcher()
        return fallback_fetcher.get_klines(symbol, interval, period)
    
    def get_symbol_info(self, symbol):
        """Get detailed symbol information"""
        try:
            tv_symbol = self._convert_symbol(symbol)
            
            url = "https://scanner.tradingview.com/symbol"
            params = {
                'symbol': tv_symbol,
                'fields': 'name,description,type,typespecs,exchange,currency,base_name'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Symbol info error: {e}")
            return None
    
    def test_connection(self):
        """Test TradingView connection and authentication"""
        try:
            # Test with a simple symbol request
            test_symbol = 'BINANCE:BTCUSDT'
            
            url = "https://scanner.tradingview.com/symbol"
            params = {
                'symbol': test_symbol,
                'fields': 'base_name'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                auth_status = "Authenticated" if self.auth_token else "Public Access"
                return {
                    'status': 'Connected',
                    'auth_status': auth_status,
                    'username': self.username if self.username else 'Anonymous',
                    'response_code': response.status_code
                }
            else:
                return {
                    'status': 'Failed',
                    'auth_status': 'No Connection',
                    'response_code': response.status_code
                }
                
        except Exception as e:
            return {
                'status': 'Error',
                'auth_status': 'Connection Failed',
                'error': str(e)
            }
    
    def get_premium_symbols(self):
        """Get list of premium symbols available with your account"""
        premium_symbols = {
            'Crypto Futures': ['BTC.P', 'ETH.P', 'SOL.P', 'BNB.P', 'XRP.P', 'ADA.P'],
            'Forex Major': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF'],
            'Forex Minor': ['EURGBP', 'EURJPY', 'GBPJPY', 'EURCHF', 'GBPCHF', 'AUDJPY'],
            'Commodities': ['XAUUSD', 'XAGUSD', 'CRUDE', 'NATGAS', 'COPPER'],
            'Indices': ['US100', 'SP500', 'DJI', 'DAX', 'FTSE', 'NIKKEI'],
            'Crypto Spot': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'DOTUSDT']
        }
        
        return premium_symbols

def test_tradingview_connection():
    """Test function to verify TradingView connection"""
    print("Testing TradingView Authenticated Connection...")
    
    fetcher = TradingViewAuthenticatedFetcher()
    
    # Test connection
    connection_test = fetcher.test_connection()
    print(f"Connection Status: {connection_test}")
    
    # Test data fetch
    print("\nTesting data fetch for BTCUSDT...")
    data = fetcher.get_klines('BTC.P', '1h', '7d')
    
    if data is not None and not data.empty:
        print(f"✅ Data retrieved successfully: {len(data)} candles")
        print(f"Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
        print(f"Latest price: ${data['Close'].iloc[-1]:.2f}")
    else:
        print("❌ Data retrieval failed")
    
    return fetcher

if __name__ == "__main__":
    test_tradingview_connection()