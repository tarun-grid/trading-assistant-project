# test_timeframes.py

from market_data import MarketData
import pandas as pd

def test_timeframes():
    md = MarketData()
    symbol = 'AAPL'
    
    # Updated timeframes with correct periods
    timeframes = {
        '5m': '1d',     # Last day of 5-min data
        '30m': '5d',    # Last 5 days of 30-min data
        '1h': '5d',     # Last 5 days of hourly data
        '1d': '1mo'     # Last month of daily data
    }
    
    for interval, period in timeframes.items():
        print(f"\n{'='*50}")
        print(f"Testing {interval} timeframe (Period: {period})")
        print(f"{'='*50}")
        
        data = md.fetch_data(symbol, period=period, interval=interval)
        
        if data is not None:
            print(f"\nData Summary:")
            print(f"Start: {data.index[0]}")
            print(f"End: {data.index[-1]}")
            print(f"Number of candles: {len(data)}")
            
            # Get latest complete data point
            latest = data.iloc[-1]
            print(f"\nLatest Data Point:")
            print(f"Time: {data.index[-1]}")
            print(f"Price: ${latest['Close']:.2f}")
            print(f"Volume: {latest['Volume']:,}")
            
            if 'RSI' in data.columns:
                print(f"RSI: {latest['RSI']:.2f}")
            if 'MACD' in data.columns:
                print(f"MACD: {latest['MACD']:.2f}")
            if 'BB_Upper' in data.columns:
                print(f"BB Upper: {latest['BB_Upper']:.2f}")
                print(f"BB Lower: {latest['BB_Lower']:.2f}")

def print_available_indicators(data):
    print("\nAvailable Indicators:")
    indicators = [col for col in data.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']]
    for ind in indicators:
        print(f"- {ind}")

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    test_timeframes()