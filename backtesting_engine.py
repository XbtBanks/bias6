import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from reliable_data_fetcher import ReliableDataFetcher
from ema_calculator import EMACalculator
from bias_analyzer import BiasAnalyzer
from fvg_detector import FVGDetector
from scalp_analyzer import ScalpAnalyzer
from advanced_indicators import AdvancedIndicators

class BacktestingEngine:
    """
    Comprehensive backtesting engine for FinansLab Bias system
    Tests EMA bias, FVG signals, and scalp analysis for profitability
    """
    
    def __init__(self):
        self.initial_capital = 1000
        self.risk_per_trade = 0.01  # 1% risk per trade
        self.ema_periods = [45, 89, 144, 200, 276]
        self.scalp_emas = [8, 13, 21, 34, 55]
        
        # Initialize components
        self.data_fetcher = ReliableDataFetcher()
        self.ema_calculator = EMACalculator()
        self.bias_analyzer = BiasAnalyzer(self.ema_periods)
        self.fvg_detector = FVGDetector()
        self.scalp_analyzer = ScalpAnalyzer(self.scalp_emas)
        self.advanced_indicators = AdvancedIndicators()
        
    def backtest_symbol(self, symbol, timeframe='1h', period='3mo'):
        """
        Backtest a single symbol with the complete trading system
        """
        try:
            print(f"\n=== Backtesting {symbol} ===")
            
            # Fetch historical data
            data = self.data_fetcher.get_klines(symbol, timeframe, period)
            if data is None or len(data) < 100:
                return None
                
            print(f"Data points: {len(data)}")
            
            # Calculate EMAs
            ema_data = self.ema_calculator.calculate_multiple_emas(data['Close'], self.ema_periods)
            
            # Storage for trades
            trades = []
            current_capital = self.initial_capital
            
            # Simulate trading
            for i in range(100, len(data)):  # Start after sufficient data for indicators
                current_data = data.iloc[:i+1]
                current_price = current_data['Close'].iloc[-1]
                
                # Get analysis
                bias_result = self._get_bias_signal(current_data, ema_data, i)
                fvg_result = self._get_fvg_signal(current_data, i)
                scalp_result = self._get_scalp_signal(current_data, ema_data, i)
                
                # Trading logic
                trade_signal = self._combine_signals(bias_result, fvg_result, scalp_result)
                
                if trade_signal['signal'] in ['BUY', 'SELL']:
                    # Calculate position size
                    risk_amount = current_capital * self.risk_per_trade
                    
                    # Simulate trade execution
                    trade_result = self._simulate_trade(
                        current_data, i, trade_signal, risk_amount, current_price
                    )
                    
                    if trade_result:
                        trades.append(trade_result)
                        current_capital += trade_result['pnl']
                        
            # Calculate performance metrics
            performance = self._calculate_performance(trades, current_capital)
            if isinstance(performance, dict):
                performance['symbol'] = symbol
                performance['timeframe'] = timeframe
            
            return performance
            
        except Exception as e:
            print(f"Error backtesting {symbol}: {e}")
            return None
    
    def _get_bias_signal(self, data, ema_data, index):
        """Get EMA bias signal"""
        try:
            bias_analysis = self.bias_analyzer.analyze_bias(data['Close'])
            return {
                'bias': bias_analysis.get('overall_bias', 'neutral'),
                'strength': bias_analysis.get('bias_strength', 0)
            }
        except:
            return {'bias': 'neutral', 'strength': 0}
    
    def _get_fvg_signal(self, data, index):
        """Get FVG signal"""
        try:
            fvg_analysis = self.fvg_detector.detect_fvgs(data)
            
            # Get unfilled FVGs
            bullish_unfilled = [fvg for fvg in fvg_analysis.get('bullish_fvgs', []) 
                              if not fvg.get('filled', False)]
            bearish_unfilled = [fvg for fvg in fvg_analysis.get('bearish_fvgs', []) 
                              if not fvg.get('filled', False)]
            
            return {
                'bullish_fvgs': len(bullish_unfilled),
                'bearish_fvgs': len(bearish_unfilled),
                'total_unfilled': len(bullish_unfilled) + len(bearish_unfilled)
            }
        except:
            return {'bullish_fvgs': 0, 'bearish_fvgs': 0, 'total_unfilled': 0}
    
    def _get_scalp_signal(self, data, ema_data, index):
        """Get scalp signal"""
        try:
            scalp_analysis = self.scalp_analyzer.analyze_scalp_signals(data, ema_data)
            return {
                'direction': scalp_analysis.get('direction', 'neutral'),
                'confidence': scalp_analysis.get('confidence', 0)
            }
        except:
            return {'direction': 'neutral', 'confidence': 0}
    
    def _combine_signals(self, bias_result, fvg_result, scalp_result):
        """Combine all signals for trading decision"""
        score = 0
        
        # EMA Bias scoring
        if bias_result['bias'] == 'bullish':
            score += bias_result['strength'] * 0.4
        elif bias_result['bias'] == 'bearish':
            score -= bias_result['strength'] * 0.4
        
        # FVG scoring
        if fvg_result['bullish_fvgs'] > fvg_result['bearish_fvgs']:
            score += 0.3
        elif fvg_result['bearish_fvgs'] > fvg_result['bullish_fvgs']:
            score -= 0.3
        
        # Scalp scoring
        if scalp_result['direction'] == 'long':
            score += scalp_result['confidence'] * 0.3
        elif scalp_result['direction'] == 'short':
            score -= scalp_result['confidence'] * 0.3
        
        # Decision thresholds
        if score > 0.6:
            return {'signal': 'BUY', 'confidence': min(score, 1.0)}
        elif score < -0.6:
            return {'signal': 'SELL', 'confidence': min(abs(score), 1.0)}
        else:
            return {'signal': 'HOLD', 'confidence': 0}
    
    def _simulate_trade(self, data, index, signal, risk_amount, entry_price):
        """Simulate trade execution and outcome"""
        try:
            # Calculate stop loss and take profit levels
            atr = self._calculate_atr(data, index)
            
            if signal['signal'] == 'BUY':
                stop_loss = entry_price - (atr * 1.5)
                take_profit = entry_price + (atr * 3.0)  # 1:2 R:R ratio
                direction = 1
            else:  # SELL
                stop_loss = entry_price + (atr * 1.5)
                take_profit = entry_price - (atr * 3.0)
                direction = -1
            
            # Position size based on risk
            stop_distance = abs(entry_price - stop_loss)
            position_size = risk_amount / stop_distance
            
            # Look ahead to see trade outcome (max 48 hours for 1h timeframe)
            max_lookhead = min(48, len(data) - index - 1)
            
            for j in range(1, max_lookhead + 1):
                if index + j >= len(data):
                    break
                    
                future_high = data['High'].iloc[index + j]
                future_low = data['Low'].iloc[index + j]
                
                # Check for stop loss or take profit hit
                if direction == 1:  # Long trade
                    if future_low <= stop_loss:
                        # Stop loss hit
                        exit_price = stop_loss
                        pnl = (exit_price - entry_price) * position_size
                        return {
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'direction': 'LONG',
                            'pnl': pnl,
                            'outcome': 'LOSS',
                            'bars_held': j,
                            'risk_reward': -1
                        }
                    elif future_high >= take_profit:
                        # Take profit hit
                        exit_price = take_profit
                        pnl = (exit_price - entry_price) * position_size
                        return {
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'direction': 'LONG',
                            'pnl': pnl,
                            'outcome': 'WIN',
                            'bars_held': j,
                            'risk_reward': 2
                        }
                else:  # Short trade
                    if future_high >= stop_loss:
                        # Stop loss hit
                        exit_price = stop_loss
                        pnl = (entry_price - exit_price) * position_size
                        return {
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'direction': 'SHORT',
                            'pnl': pnl,
                            'outcome': 'LOSS',
                            'bars_held': j,
                            'risk_reward': -1
                        }
                    elif future_low <= take_profit:
                        # Take profit hit
                        exit_price = take_profit
                        pnl = (entry_price - exit_price) * position_size
                        return {
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'direction': 'SHORT',
                            'pnl': pnl,
                            'outcome': 'WIN',
                            'bars_held': j,
                            'risk_reward': 2
                        }
            
            # No exit triggered - close at current price (neutral outcome)
            exit_price = data['Close'].iloc[index + max_lookhead]
            if direction == 1:
                pnl = (exit_price - entry_price) * position_size
            else:
                pnl = (entry_price - exit_price) * position_size
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'direction': 'LONG' if direction == 1 else 'SHORT',
                'pnl': pnl,
                'outcome': 'NEUTRAL',
                'bars_held': max_lookhead,
                'risk_reward': pnl / risk_amount if risk_amount > 0 else 0
            }
            
        except Exception as e:
            return None
    
    def _calculate_atr(self, data, index, period=14):
        """Calculate Average True Range for stop loss/take profit levels"""
        try:
            start_idx = max(0, index - period)
            subset = data.iloc[start_idx:index+1]
            
            high_low = subset['High'] - subset['Low']
            high_close = abs(subset['High'] - subset['Close'].shift(1))
            low_close = abs(subset['Low'] - subset['Close'].shift(1))
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            return true_range.mean()
        except:
            return data['Close'].iloc[index] * 0.02  # 2% fallback
    
    def _calculate_performance(self, trades, final_capital):
        """Calculate comprehensive performance metrics"""
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'average_r': 0,
                'final_capital': self.initial_capital
            }
        
        wins = [t for t in trades if t['outcome'] == 'WIN']
        losses = [t for t in trades if t['outcome'] == 'LOSS']
        
        total_trades = len(trades)
        win_count = len(wins)
        loss_count = len(losses)
        
        win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0
        
        total_pnl = sum(t['pnl'] for t in trades)
        total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Calculate average R (risk-reward multiple)
        risk_rewards = [t['risk_reward'] for t in trades if t['risk_reward'] != 0]
        average_r = np.mean(risk_rewards) if risk_rewards else 0
        
        # Calculate expectancy
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
        expectancy = (win_rate/100 * avg_win) + ((100-win_rate)/100 * avg_loss)
        
        return {
            'total_trades': total_trades,
            'wins': win_count,
            'losses': loss_count,
            'win_rate': round(win_rate, 2),
            'total_return': round(total_return, 2),
            'total_pnl': round(total_pnl, 2),
            'average_r': round(average_r, 2),
            'expectancy': round(expectancy, 2),
            'final_capital': round(final_capital, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2)
        }
    
    def run_comprehensive_backtest(self):
        """Run backtest on multiple symbols and timeframes"""
        symbols = ['BTC.P', 'ETH.P', 'EURUSD', 'GBPUSD', 'XAUUSD']
        timeframes = ['1h', '4h']
        
        all_results = []
        
        for symbol in symbols:
            for timeframe in timeframes:
                print(f"\nTesting {symbol} on {timeframe}...")
                result = self.backtest_symbol(symbol, timeframe, '6mo')
                if result:
                    all_results.append(result)
        
        # Aggregate results
        if all_results:
            aggregate = self._aggregate_results(all_results)
            return aggregate, all_results
        else:
            return None, []
    
    def _aggregate_results(self, results):
        """Aggregate results from multiple tests"""
        total_trades = sum(r['total_trades'] for r in results)
        total_wins = sum(r['wins'] for r in results)
        
        if total_trades == 0:
            return {'error': 'No trades executed'}
        
        overall_win_rate = (total_wins / total_trades) * 100
        
        # Weighted average of returns
        avg_return = np.mean([r['total_return'] for r in results])
        avg_r = np.mean([r['average_r'] for r in results if r['average_r'] != 0])
        
        # Calculate yearly projection
        yearly_return = self._project_yearly_return(avg_return, overall_win_rate, avg_r)
        
        return {
            'total_trades': total_trades,
            'overall_win_rate': round(overall_win_rate, 2),
            'average_return_per_test': round(avg_return, 2),
            'average_r_multiple': round(avg_r, 2),
            'projected_yearly_return': round(yearly_return, 2),
            'projected_final_capital': round(self.initial_capital * (1 + yearly_return/100), 2),
            'number_of_tests': len(results)
        }
    
    def _project_yearly_return(self, avg_return_6mo, win_rate, avg_r):
        """Project yearly returns based on 6-month backtest data"""
        # Conservative projection accounting for market changes
        monthly_return = avg_return_6mo / 6
        yearly_return = monthly_return * 12
        
        # Apply conservative factor for longer timeframe
        conservative_factor = 0.7  # Reduce by 30% for realistic projection
        return yearly_return * conservative_factor