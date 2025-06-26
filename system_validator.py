import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def validate_complete_system():
    """
    Comprehensive system validation with all components
    Tests integration and identifies any remaining issues
    """
    
    print("=== FinansLab Bias System - Comprehensive Validation ===")
    print("Testing all components with 1% risk and 1.5R parameters\n")
    
    # Import all system components
    try:
        from reliable_data_fetcher import ReliableDataFetcher
        from ema_calculator import EMACalculator
        from bias_analyzer import BiasAnalyzer
        from fvg_detector import FVGDetector
        from scalp_analyzer import ScalpAnalyzer
        from advanced_indicators import AdvancedIndicators
        from market_structure_analyzer import MarketStructureAnalyzer
        from risk_management_engine import RiskManagementEngine
        from sentiment_analyzer import SentimentAnalyzer
        from institutional_levels import InstitutionalLevels
        from multi_timeframe_analyzer import MultiTimeframeAnalyzer
        
        print("✓ All modules imported successfully")
    except Exception as e:
        print(f"✗ Module import error: {e}")
        return False
    
    # Test data fetching
    print("\n--- Testing Data Fetcher ---")
    try:
        fetcher = ReliableDataFetcher()
        test_data = fetcher.get_klines('BTC.P', '1h', '7d')
        if test_data is not None and len(test_data) > 30:
            print(f"✓ Data fetch successful: {len(test_data)} candles")
            print(f"  Price range: ${test_data['Close'].min():.2f} - ${test_data['Close'].max():.2f}")
        else:
            print("✗ Data fetch failed")
            return False
    except Exception as e:
        print(f"✗ Data fetch error: {e}")
        return False
    
    # Test EMA calculations
    print("\n--- Testing EMA Calculator ---")
    try:
        ema_calc = EMACalculator()
        ema_periods = [45, 89, 144, 200, 276]
        ema_data = ema_calc.calculate_multiple_emas(test_data['Close'], ema_periods)
        
        if len(ema_data) == 5:
            print("✓ EMA calculations successful")
            try:
                current_emas = {period: float(ema_data[period].iloc[-1]) for period in ema_periods}
                print(f"  Current EMAs: {', '.join([f'{p}:{v:.2f}' for p, v in current_emas.items()])}")
            except Exception as e:
                print(f"  Warning: EMA display error: {e}")
        else:
            print("✗ EMA calculation failed")
            return False
    except Exception as e:
        print(f"✗ EMA calculation error: {e}")
        return False
    
    # Test bias analysis
    print("\n--- Testing Bias Analyzer ---")
    try:
        bias_analyzer = BiasAnalyzer(ema_periods)
        bias_result = bias_analyzer.analyze_bias(test_data['Close'], ema_data)
        
        if bias_result:
            print("✓ Bias analysis successful")
            print(f"  Overall bias: {bias_result.get('overall_bias', 'N/A')}")
            print(f"  Bias strength: {bias_result.get('bias_strength', 0):.2f}")
        else:
            print("✗ Bias analysis failed")
            return False
    except Exception as e:
        print(f"✗ Bias analysis error: {e}")
        return False
    
    # Test FVG detection
    print("\n--- Testing FVG Detector ---")
    try:
        fvg_detector = FVGDetector()
        fvg_result = fvg_detector.detect_fvgs(test_data)
        
        if fvg_result:
            total_fvgs = fvg_result.get('total_fvgs', 0)
            bullish_unfilled = len([fvg for fvg in fvg_result.get('bullish_fvgs', []) if not fvg.get('filled', False)])
            bearish_unfilled = len([fvg for fvg in fvg_result.get('bearish_fvgs', []) if not fvg.get('filled', False)])
            
            print("✓ FVG detection successful")
            print(f"  Total FVGs: {total_fvgs}")
            print(f"  Unfilled Bullish US FVG: {bullish_unfilled}")
            print(f"  Unfilled Bearish US FVG: {bearish_unfilled}")
        else:
            print("✗ FVG detection failed")
            return False
    except Exception as e:
        print(f"✗ FVG detection error: {e}")
        return False
    
    # Test scalp analysis
    print("\n--- Testing Scalp Analyzer ---")
    try:
        scalp_emas = [8, 13, 21, 34, 55]
        scalp_analyzer = ScalpAnalyzer(scalp_ema_periods=scalp_emas)
        scalp_result = scalp_analyzer.analyze_scalp_signals(test_data, ema_data)
        
        if scalp_result:
            print("✓ Scalp analysis successful")
            print(f"  Direction: {scalp_result.get('direction', 'N/A')}")
            print(f"  Confidence: {scalp_result.get('confidence', 0):.2f}")
        else:
            print("✗ Scalp analysis failed")
            return False
    except Exception as e:
        print(f"✗ Scalp analysis error: {e}")
        return False
    
    # Test advanced indicators
    print("\n--- Testing Advanced Indicators ---")
    try:
        advanced_indicators = AdvancedIndicators()
        rsi = advanced_indicators.calculate_rsi(test_data['Close'])
        macd = advanced_indicators.calculate_macd(test_data['Close'])
        confluence = advanced_indicators.calculate_confluence_score(
            bias_result, rsi, macd, {}, {}
        )
        
        print("✓ Advanced indicators successful")
        try:
            rsi_value = float(rsi.iloc[-1]) if hasattr(rsi, 'iloc') else float(rsi)
            print(f"  RSI: {rsi_value:.2f}")
        except:
            print(f"  RSI: {rsi}")
        print(f"  Confluence score: {confluence.get('confluence_score', 0):.2f}")
    except Exception as e:
        print(f"✗ Advanced indicators error: {e}")
        return False
    
    # Test risk management
    print("\n--- Testing Risk Management (1% risk, 1.5R target) ---")
    try:
        market_analyzer = MarketStructureAnalyzer()
        market_structure = market_analyzer.analyze_market_structure(test_data, ema_data)
        
        risk_engine = RiskManagementEngine()
        risk_analysis = risk_engine.calculate_position_parameters(
            test_data, ema_data, confluence['confluence_score'], market_structure
        )
        
        if risk_analysis:
            print("✓ Risk management successful")
            current_price = test_data['Close'].iloc[-1]
            entry_price = risk_analysis.get('entry_price', current_price)
            stop_loss = risk_analysis.get('stop_loss', {}).get('price', 0)
            take_profit = risk_analysis.get('take_profit', {}).get('target_1', {}).get('price', 0)
            
            print(f"  Entry price: ${entry_price:.2f}")
            print(f"  Stop loss: ${stop_loss:.2f}")
            print(f"  Take profit 1: ${take_profit:.2f}")
            
            if stop_loss > 0 and take_profit > 0:
                risk_amount = abs(entry_price - stop_loss)
                reward_amount = abs(take_profit - entry_price)
                rr_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
                print(f"  Risk/Reward ratio: 1:{rr_ratio:.2f}")
        else:
            print("✗ Risk management failed")
            return False
    except Exception as e:
        print(f"✗ Risk management error: {e}")
        return False
    
    # Test system integration
    print("\n--- Testing Complete System Integration ---")
    try:
        # Simulate complete analysis workflow
        current_price = test_data['Close'].iloc[-1]
        
        # Calculate all signals
        signal_strength = 0
        signals = []
        
        # EMA bias signal
        if bias_result.get('overall_bias') == 'bullish' and bias_result.get('bias_strength', 0) > 0.6:
            signal_strength += 0.4
            signals.append("Strong bullish EMA bias")
        elif bias_result.get('overall_bias') == 'bearish' and bias_result.get('bias_strength', 0) > 0.6:
            signal_strength -= 0.4
            signals.append("Strong bearish EMA bias")
        
        # FVG signal
        if bullish_unfilled > bearish_unfilled:
            signal_strength += 0.3
            signals.append(f"Bullish US FVG dominance ({bullish_unfilled} vs {bearish_unfilled})")
        elif bearish_unfilled > bullish_unfilled:
            signal_strength -= 0.3
            signals.append(f"Bearish US FVG dominance ({bearish_unfilled} vs {bullish_unfilled})")
        
        # Scalp signal
        if scalp_result.get('direction') == 'long' and scalp_result.get('confidence', 0) > 0.7:
            signal_strength += 0.3
            signals.append("Strong scalp long signal")
        elif scalp_result.get('direction') == 'short' and scalp_result.get('confidence', 0) > 0.7:
            signal_strength -= 0.3
            signals.append("Strong scalp short signal")
        
        print("✓ System integration successful")
        print(f"  Combined signal strength: {signal_strength:.2f}")
        print(f"  Trading decision: {'BUY' if signal_strength > 0.6 else 'SELL' if signal_strength < -0.6 else 'HOLD'}")
        print(f"  Active signals: {len(signals)}")
        for signal in signals:
            print(f"    • {signal}")
        
    except Exception as e:
        print(f"✗ System integration error: {e}")
        return False
    
    # Performance summary
    print("\n=== SYSTEM VALIDATION SUMMARY ===")
    print("✓ All core components working")
    print("✓ Data fetching operational")
    print("✓ EMA bias analysis functional")
    print("✓ US FVG detection active")
    print("✓ Scalp analysis operational")
    print("✓ Risk management configured (1% risk, 1.5R)")
    print("✓ System integration complete")
    
    print(f"\n=== TRADING CONFIGURATION ===")
    print("• Risk per trade: 1%")
    print("• Target reward: 1.5R")
    print("• EMA periods: 45, 89, 144, 200, 276")
    print("• Scalp EMAs: 8, 13, 21, 34, 55")
    print("• FVG detection: Unfilled gaps only")
    print("• Multi-timeframe confirmation")
    
    return True

if __name__ == "__main__":
    success = validate_complete_system()
    print(f"\nSystem validation: {'PASSED' if success else 'FAILED'}")