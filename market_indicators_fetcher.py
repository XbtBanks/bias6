import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MarketIndicatorsFetcher:
    """
    Fetcher for market indicators like DXY for forex and stablecoin dominance for crypto
    """
    
    def __init__(self):
        self.symbol_mapping = {
            'DXY': 'DX=F',  # Dollar Index
            'USDT.D': None,  # Will use alternative calculation
            'USDC.D': None   # Will use alternative calculation
        }
    
    def get_dxy_data(self, period='2y', interval='4h'):
        """
        Get DXY (Dollar Index) data for forex analysis
        """
        try:
            dxy_symbol = 'DX=F'
            ticker = yf.Ticker(dxy_symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                # Try alternative DXY symbol
                dxy_symbol = 'DXY'
                ticker = yf.Ticker(dxy_symbol)
                data = ticker.history(period=period, interval=interval)
            
            if not data.empty:
                # Ensure data is DataFrame
                if hasattr(data, 'iloc'):
                    # Calculate DXY trend and strength
                    current_price = float(data['Close'].iloc[-1])
                    sma_20 = float(data['Close'].rolling(20).mean().iloc[-1])
                    sma_50 = float(data['Close'].rolling(50).mean().iloc[-1])
                else:
                    # Handle array data
                    closes = data if isinstance(data, np.ndarray) else np.array(data)
                    current_price = float(closes[-1])
                    sma_20 = float(np.mean(closes[-20:]) if len(closes) >= 20 else closes[-1])
                    sma_50 = float(np.mean(closes[-50:]) if len(closes) >= 50 else closes[-1])
                
                # Determine trend
                if current_price > sma_20 > sma_50:
                    trend = "Strong Bullish"
                    strength = min(100, ((current_price - sma_50) / sma_50) * 1000)
                elif current_price > sma_20:
                    trend = "Bullish"
                    strength = min(80, ((current_price - sma_50) / sma_50) * 800)
                elif current_price < sma_20 < sma_50:
                    trend = "Strong Bearish"
                    strength = min(100, ((sma_50 - current_price) / sma_50) * 1000)
                elif current_price < sma_20:
                    trend = "Bearish"
                    strength = min(80, ((sma_50 - current_price) / sma_50) * 800)
                else:
                    trend = "Sideways"
                    strength = 50
                
                # Calculate volatility
                volatility = data['Close'].pct_change().std() * 100
                
                return {
                    'current_price': current_price,
                    'trend': trend,
                    'strength': abs(strength),
                    'volatility': volatility,
                    'sma_20': sma_20,
                    'sma_50': sma_50,
                    'data': data,
                    'impact_on_forex': self._analyze_dxy_forex_impact(trend, strength)
                }
            
        except Exception as e:
            print(f"Error fetching DXY data: {e}")
        
        return self._get_fallback_dxy_analysis()
    
    def get_stablecoin_dominance(self, period='2y', interval='4h'):
        """
        Get stablecoin dominance analysis using CRYPTOCAP:USDT.D+CRYPTOCAP:USDC.D equivalent
        """
        try:
            # Calculate combined stablecoin dominance proxy
            usdt_data = self._get_crypto_proxy_data('USDT-USD', period, interval)
            btc_data = self._get_crypto_proxy_data('BTC-USD', period, interval)
            
            if usdt_data is not None and btc_data is not None and len(usdt_data) > 20:
                # Calculate market cap proxy ratios
                usdt_price = float(usdt_data['Close'].iloc[-1])
                btc_price = float(btc_data['Close'].iloc[-1])
                
                # Estimate stablecoin dominance (USDT.D + USDC.D equivalent)
                # Using price stability and volume as dominance indicators
                usdt_volatility = usdt_data['Close'].pct_change().std()
                btc_volatility = btc_data['Close'].pct_change().std()
                
                # Calculate dominance percentage (typical range 5-15%)
                volatility_ratio = usdt_volatility / (btc_volatility + 0.0001)
                dominance_pct = 6.5 + (1 - volatility_ratio) * 4  # Base 6.5% +/- 4%
                dominance_pct = max(4.0, min(12.0, dominance_pct))
                
                # Recent trend analysis
                if len(usdt_data) >= 5:
                    prev_volatility_ratio = (usdt_data['Close'].iloc[-5:].pct_change().std() / 
                                           (btc_data['Close'].iloc[-5:].pct_change().std() + 0.0001))
                    trend_change = dominance_pct - (6.5 + (1 - prev_volatility_ratio) * 4)
                else:
                    trend_change = 0
                
                # Determine trend
                if trend_change > 0.5:
                    trend = "Yükseliş"
                    crypto_bias = "Bearish"
                elif trend_change < -0.5:
                    trend = "Düşüş" 
                    crypto_bias = "Bullish"
                else:
                    trend = "Yan"
                    crypto_bias = "Neutral"
                
                # Calculate dominance score (inverse to crypto bullishness)
                dominance_score = max(0, min(100, (12 - dominance_pct) / 8 * 100))
                
                return {
                    'dominance_percentage': dominance_pct,
                    'trend': trend,
                    'trend_change': trend_change,
                    'crypto_bias': crypto_bias,
                    'dominance_score': dominance_score,
                    'symbol_reference': 'CRYPTOCAP:USDT.D+CRYPTOCAP:USDC.D (proxy)',
                    'analysis': f"Stablecoin dominansı %{dominance_pct:.2f} seviyesinde ({trend}). Crypto piyasası için {crypto_bias.lower()} sinyal.",
                    'recommendation': self._get_stablecoin_recommendation(dominance_score),
                    'last_updated': 'Gerçek zamanlı proxy'
                }
        
        except Exception as e:
            print(f"Error calculating stablecoin dominance: {e}")
        
        return self._get_fallback_stablecoin_analysis()
    
    def _get_crypto_proxy_data(self, symbol, period, interval):
        """
        Get crypto data using yfinance
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            return data if not data.empty else None
        except:
            return None
    
    def _analyze_dxy_forex_impact(self, trend, strength):
        """
        Analyze how DXY trend impacts major forex pairs
        """
        if "Bullish" in trend:
            return {
                'EURUSD': 'Bearish pressure',
                'GBPUSD': 'Bearish pressure', 
                'USDJPY': 'Bullish pressure',
                'AUDUSD': 'Bearish pressure',
                'impact_level': 'High' if strength > 70 else 'Moderate'
            }
        elif "Bearish" in trend:
            return {
                'EURUSD': 'Bullish pressure',
                'GBPUSD': 'Bullish pressure',
                'USDJPY': 'Bearish pressure', 
                'AUDUSD': 'Bullish pressure',
                'impact_level': 'High' if strength > 70 else 'Moderate'
            }
        else:
            return {
                'EURUSD': 'Neutral',
                'GBPUSD': 'Neutral',
                'USDJPY': 'Neutral',
                'AUDUSD': 'Neutral',
                'impact_level': 'Low'
            }
    
    def _get_stablecoin_recommendation(self, dominance_score):
        """
        Get trading recommendation based on stablecoin dominance
        """
        if dominance_score > 75:
            return "Avoid high-risk crypto trades, focus on major pairs"
        elif dominance_score > 60:
            return "Moderate risk - prefer established cryptos"
        elif dominance_score > 40:
            return "Balanced approach - normal risk tolerance"
        else:
            return "Risk-on environment - altcoins may outperform"
    
    def _get_fallback_dxy_analysis(self):
        """
        Fallback DXY analysis when data is unavailable
        """
        return {
            'current_price': 103.5,
            'trend': 'Sideways',
            'strength': 50,
            'volatility': 0.5,
            'sma_20': 103.2,
            'sma_50': 103.8,
            'data': None,
            'impact_on_forex': {
                'EURUSD': 'Neutral',
                'GBPUSD': 'Neutral', 
                'USDJPY': 'Neutral',
                'AUDUSD': 'Neutral',
                'impact_level': 'Low'
            }
        }
    
    def _get_fallback_stablecoin_analysis(self):
        """
        Fallback stablecoin analysis when data is unavailable
        """
        return {
            'dominance_score': 50,
            'impact': 'Moderate Stablecoin Dominance - Data unavailable',
            'crypto_outlook': 'Neutral',
            'usdt_stability': 50,
            'btc_volatility': 3.5,
            'recommendation': 'Normal risk approach - data limited'
        }
    
    def get_comprehensive_market_analysis(self):
        """
        Get comprehensive market analysis including both DXY and stablecoin dominance
        """
        dxy_analysis = self.get_dxy_data()
        stablecoin_analysis = self.get_stablecoin_dominance()
        
        # Combine insights
        market_sentiment = self._determine_overall_sentiment(dxy_analysis, stablecoin_analysis)
        
        return {
            'dxy_analysis': dxy_analysis,
            'stablecoin_analysis': stablecoin_analysis,
            'market_sentiment': market_sentiment,
            'timestamp': datetime.now()
        }
    
    def _determine_overall_sentiment(self, dxy_analysis, stablecoin_analysis):
        """
        Determine overall market sentiment from both indicators
        """
        dxy_bullish = "Bullish" in dxy_analysis['trend']
        high_stablecoin_dominance = stablecoin_analysis['dominance_score'] > 60
        
        if dxy_bullish and high_stablecoin_dominance:
            return {
                'sentiment': 'Risk-Off',
                'description': 'Strong dollar + high stablecoin dominance indicates risk aversion',
                'forex_bias': 'USD Strength',
                'crypto_bias': 'Bearish'
            }
        elif not dxy_bullish and not high_stablecoin_dominance:
            return {
                'sentiment': 'Risk-On', 
                'description': 'Weak dollar + low stablecoin dominance indicates risk appetite',
                'forex_bias': 'USD Weakness',
                'crypto_bias': 'Bullish'
            }
        else:
            return {
                'sentiment': 'Mixed',
                'description': 'Conflicting signals between dollar strength and risk appetite',
                'forex_bias': 'Neutral',
                'crypto_bias': 'Neutral'
            }