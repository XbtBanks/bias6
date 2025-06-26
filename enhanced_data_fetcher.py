import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class EnhancedDataFetcher:
    """
    Enhanced data fetcher with multiple sources and improved reliability
    """
    
    def __init__(self):
        self.primary_sources = ['yahoo', 'binance_public']
        self.symbol_mapping = self._build_symbol_mapping()
    
    def _build_symbol_mapping(self):
        """Build comprehensive symbol mapping for different data sources"""
        return {
            # Crypto futures mapping
            'BTC.P': {
                'yahoo': 'BTC-USD',
                'binance': 'BTCUSDT',
                'display': 'Bitcoin'
            },
            'ETH.P': {
                'yahoo': 'ETH-USD',
                'binance': 'ETHUSDT',
                'display': 'Ethereum'
            },
            'SOL.P': {
                'yahoo': 'SOL-USD',
                'binance': 'SOLUSDT',
                'display': 'Solana'
            },
            'BNB.P': {
                'yahoo': 'BNB-USD',
                'binance': 'BNBUSDT',
                'display': 'Binance Coin'
            },
            'ADA.P': {
                'yahoo': 'ADA-USD',
                'binance': 'ADAUSDT',
                'display': 'Cardano'
            },
            'XRP.P': {
                'yahoo': 'XRP-USD',
                'binance': 'XRPUSDT',
                'display': 'Ripple'
            },
            
            # Forex pairs
            'EURUSD': {
                'yahoo': 'EURUSD=X',
                'display': 'EUR/USD'
            },
            'GBPUSD': {
                'yahoo': 'GBPUSD=X',
                'display': 'GBP/USD'
            },
            'JPYUSD': {
                'yahoo': 'USDJPY=X',
                'display': 'USD/JPY',
                'invert': True
            },
            'AUDUSD': {
                'yahoo': 'AUDUSD=X',
                'display': 'AUD/USD'
            },
            'USDCAD': {
                'yahoo': 'USDCAD=X',
                'display': 'USD/CAD'
            },
            
            # Commodities
            'XAUUSD': {
                'yahoo': 'GC=F',
                'display': 'Gold'
            },
            'XAGUSD': {
                'yahoo': 'SI=F',
                'display': 'Silver'
            },
            
            # Indices
            'US100': {
                'yahoo': '^NDX',
                'display': 'NASDAQ 100'
            },
            'SP500': {
                'yahoo': '^GSPC',
                'display': 'S&P 500'
            },
            'DJI': {
                'yahoo': '^DJI',
                'display': 'Dow Jones'
            }
        }
    
    def get_klines(self, symbol, interval, period=None):
        """
        Get historical data with multiple fallback sources
        """
        if not period:
            period = '30d'
        
        # Try Yahoo Finance first (most reliable for most symbols)
        data = self._fetch_from_yahoo(symbol, interval, period)
        if data is not None and not data.empty:
            return data
        
        # Fallback to Binance public API for crypto
        if any(symbol.upper().endswith(suffix) for suffix in ['.P', 'USDT', 'USDC']):
            data = self._fetch_from_binance_public(symbol, interval, period)
            if data is not None and not data.empty:
                return data
        
        # If all sources fail, return empty DataFrame
        return pd.DataFrame()
    
    def _fetch_from_yahoo(self, symbol, interval, period):
        """Fetch data from Yahoo Finance"""
        try:
            # Convert symbol to Yahoo format
            yahoo_symbol = self._convert_to_yahoo_symbol(symbol)
            if not yahoo_symbol:
                return None
            
            # Convert interval and period to Yahoo format
            yf_interval = self._convert_interval_to_yahoo(interval)
            yf_period = self._convert_period_to_yahoo(period)
            
            # Fetch data
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period=yf_period, interval=yf_interval, auto_adjust=True, prepost=False)
            
            if data.empty:
                return None
            
            # Standardize column names
            data = data.rename(columns={
                'Open': 'Open',
                'High': 'High', 
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume'
            })
            
            # Handle inverted pairs (like JPYUSD)
            if symbol in self.symbol_mapping and self.symbol_mapping[symbol].get('invert', False):
                for col in ['Open', 'High', 'Low', 'Close']:
                    data[col] = 1 / data[col]
                # Swap high and low for inverted pairs
                data['High'], data['Low'] = data['Low'].copy(), data['High'].copy()
            
            return data
            
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
            return None
    
    def _fetch_from_binance_public(self, symbol, interval, period):
        """Fetch data from Binance public API"""
        try:
            import requests
            
            # Convert symbol to Binance format
            binance_symbol = self._convert_to_binance_symbol(symbol)
            if not binance_symbol:
                return None
            
            # Convert interval to Binance format
            binance_interval = self._convert_interval_to_binance(interval)
            
            # Calculate limit based on period
            limit = self._calculate_binance_limit(period, interval)
            
            # Binance API endpoint
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': binance_symbol,
                'interval': binance_interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert timestamp and set as index
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Convert price columns to float
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Keep only OHLCV columns
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            return df
            
        except Exception as e:
            print(f"Binance public API error for {symbol}: {e}")
            return None
    
    def _convert_to_yahoo_symbol(self, symbol):
        """Convert symbol to Yahoo Finance format"""
        if symbol in self.symbol_mapping:
            return self.symbol_mapping[symbol].get('yahoo')
        
        # Direct mapping attempts
        if symbol.upper().endswith('.P'):
            base = symbol.replace('.P', '').upper()
            return f"{base}-USD"
        elif 'USD' in symbol.upper() and len(symbol) == 6:
            return f"{symbol}=X"
        
        return symbol
    
    def _convert_to_binance_symbol(self, symbol):
        """Convert symbol to Binance format"""
        if symbol in self.symbol_mapping:
            return self.symbol_mapping[symbol].get('binance')
        
        if symbol.upper().endswith('.P'):
            return symbol.replace('.P', 'USDT').upper()
        elif 'USDT' in symbol.upper():
            return symbol.upper()
        
        return None
    
    def _convert_interval_to_yahoo(self, interval):
        """Convert interval to Yahoo Finance format"""
        mapping = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d',
            '1w': '1wk',
            '1M': '1mo'
        }
        return mapping.get(interval, '1h')
    
    def _convert_interval_to_binance(self, interval):
        """Convert interval to Binance format"""
        mapping = {
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
        return mapping.get(interval, '1h')
    
    def _convert_period_to_yahoo(self, period):
        """Convert period to Yahoo Finance format"""
        mapping = {
            '1d': '1d',
            '7d': '7d',
            '1mo': '1mo',
            '30d': '1mo',
            '60d': '2mo',
            '3mo': '3mo',
            '6mo': '6mo',
            '1y': '1y',
            '2y': '2y'
        }
        return mapping.get(period, '1mo')
    
    def _calculate_binance_limit(self, period, interval):
        """Calculate limit for Binance API based on period and interval"""
        period_days = {
            '1d': 1,
            '7d': 7,
            '1mo': 30,
            '30d': 30,
            '60d': 60,
            '3mo': 90,
            '6mo': 180,
            '1y': 365
        }
        
        interval_minutes = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '4h': 240,
            '1d': 1440
        }
        
        days = period_days.get(period, 30)
        minutes = interval_minutes.get(interval, 60)
        
        limit = min(1000, (days * 24 * 60) // minutes)
        return max(100, limit)
    
    def test_connection(self):
        """Test connection to data sources"""
        test_results = {}
        
        # Test Yahoo Finance
        try:
            test_data = self._fetch_from_yahoo('BTC.P', '1h', '7d')
            test_results['yahoo'] = 'Working' if test_data is not None and not test_data.empty else 'Failed'
        except:
            test_results['yahoo'] = 'Failed'
        
        # Test Binance Public API
        try:
            test_data = self._fetch_from_binance_public('BTC.P', '1h', '7d')
            test_results['binance_public'] = 'Working' if test_data is not None and not test_data.empty else 'Failed'
        except:
            test_results['binance_public'] = 'Failed'
        
        return test_results

def test_enhanced_fetcher():
    """Test the enhanced data fetcher"""
    print("Testing Enhanced Data Fetcher...")
    
    fetcher = EnhancedDataFetcher()
    
    # Test connection
    connection_status = fetcher.test_connection()
    print(f"Connection Status: {connection_status}")
    
    # Test various symbols
    test_symbols = ['BTC.P', 'EURUSD', 'XAUUSD', 'US100']
    
    for symbol in test_symbols:
        print(f"\nTesting {symbol}...")
        data = fetcher.get_klines(symbol, '1h', '7d')
        
        if data is not None and not data.empty:
            print(f"✅ {symbol}: {len(data)} candles, ${data['Close'].min():.2f}-${data['Close'].max():.2f}")
        else:
            print(f"❌ {symbol}: No data retrieved")
    
    return fetcher

if __name__ == "__main__":
    test_enhanced_fetcher()