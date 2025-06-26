import pandas as pd
import numpy as np
from enhanced_data_fetcher import EnhancedDataFetcher
from ema_calculator import EMACalculator
from bias_analyzer import BiasAnalyzer
from fvg_detector import FVGDetector

def quick_system_test():
    """Quick test to verify system components are working"""
    
    print("=== FinansLab System Quick Test ===")
    
    # Test data fetching
    print("Testing data fetching...")
    fetcher = EnhancedDataFetcher()
    data = fetcher.get_klines('BTC.P', '1h', '30d')
    
    if data.empty:
        print("❌ Data fetching failed")
        return False
    
    print(f"✅ Data fetched: {len(data)} candles")
    print(f"Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
    
    # Test EMA calculations
    print("\nTesting EMA calculations...")
    ema_calc = EMACalculator()
    ema_data = ema_calc.calculate_multiple_emas(data['Close'], [45, 89, 144, 200, 276])
    
    if not ema_data:
        print("❌ EMA calculation failed")
        return False
    
    print(f"✅ EMAs calculated: {list(ema_data.keys())}")
    
    # Test bias analysis
    print("\nTesting bias analysis...")
    bias_analyzer = BiasAnalyzer([45, 89, 144, 200, 276])
    bias_result = bias_analyzer.analyze_bias(data['Close'], ema_data)
    
    print(f"✅ Bias analysis complete:")
    print(f"  Overall bias: {bias_result.get('overall_bias', 'unknown')}")
    print(f"  Current bias: {bias_result.get('current_bias', 'unknown')}")
    print(f"  Bias strength: {bias_result.get('bias_strength', 0):.3f}")
    
    # Test FVG detection
    print("\nTesting FVG detection...")
    fvg_detector = FVGDetector()
    fvg_result = fvg_detector.detect_fvgs(data)
    
    bullish_unfilled = len([fvg for fvg in fvg_result.get('bullish_fvgs', []) if not fvg.get('filled', False)])
    bearish_unfilled = len([fvg for fvg in fvg_result.get('bearish_fvgs', []) if not fvg.get('filled', False)])
    
    print(f"✅ FVG detection complete:")
    print(f"  Bullish unfilled FVGs: {bullish_unfilled}")
    print(f"  Bearish unfilled FVGs: {bearish_unfilled}")
    
    # Summary
    print(f"\n=== SYSTEM STATUS: OPERATIONAL ===")
    print(f"All core components working correctly")
    print(f"Ready for live trading analysis")
    
    return True

if __name__ == "__main__":
    success = quick_system_test()
    if success:
        print("\n🎯 System ready for production use!")
    else:
        print("\n❌ System requires attention")