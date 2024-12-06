# test_output.py

from market_data import MarketData  # Changed the import since we're in the same directory
import pandas as pd

def main():
    # Initialize
    print("\n🚀 Initializing Market Data System...")
    md = MarketData()
    
    # 1. Show Available Stocks
    print("\n📈 Available Top Stocks:")
    print("-" * 50)
    for symbol, name in md.get_available_stocks().items():
        print(f"{symbol:<6} | {name}")
    
    # 2. Get AAPL Data as Example
    print("\n🍎 Fetching Apple (AAPL) Stock Data...")
    print("-" * 50)
    data = md.fetch_data('AAPL', '1d', '1d')  # Daily data
    
    if data is not None:
        latest = data.iloc[-1]
        print(f"Latest Price: ${latest['Close']:.2f}")
        print(f"RSI: {latest['RSI']:.2f}")
        print(f"MACD: {latest['MACD']:.2f}")
        print(f"Volume: {latest['Volume']:,}")
    
    # 3. Show Market Overview
    print("\n🌍 Market Overview (Latest Data):")
    print("-" * 100)
    overview = md.get_market_overview('1d')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(overview[['Symbol', 'Name', 'Price', 'Change %', 'RSI', 'Volume']])

if __name__ == "__main__":
    main()