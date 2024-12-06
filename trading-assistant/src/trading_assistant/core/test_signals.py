# test_signals.py

from market_data import MarketData
from trading_signals import TradingSignals, generate_alerts
import pandas as pd

def analyze_timeframe(symbol: str, period: str, interval: str):
    md = MarketData()
    data = md.fetch_data(symbol, period=period, interval=interval)
    
    if data is not None:
        signals = TradingSignals(data)
        all_signals = signals.analyze_all_signals()
        alerts = generate_alerts(all_signals)
        
        print(f"\n=== Analysis for {symbol} ({interval} timeframe) ===")
        
        print("\nPrice Signals:")
        for key, value in all_signals['price_signals'].items():
            print(f"{key}: {value}")
            
        print("\nMomentum Signals:")
        for key, value in all_signals['momentum_signals'].items():
            print(f"{key}: {value}")
            
        print("\nVolume Signals:")
        for key, value in all_signals['volume_signals'].items():
            print(f"{key}: {value}")
            
        print("\nTrend Analysis:")
        for key, value in all_signals['trend_signals'].items():
            print(f"{key}: {value}")
            
        print("\nAlerts:")
        for alert in alerts:
            print(f"🚨 {alert}")

def main():
    timeframes = {
        '5m': '1d',
        '1h': '5d',
        '1d': '1mo'
    }
    
    for interval, period in timeframes.items():
        analyze_timeframe('AAPL', period, interval)

if __name__ == "__main__":
    main()