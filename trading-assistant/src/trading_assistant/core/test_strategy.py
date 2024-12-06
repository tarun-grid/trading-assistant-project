# test_strategy.py

from trading_strategy import TradingStrategy

def main():
    # Create strategy instance
    strategy = TradingStrategy()
    
    print("\n=== 5 Minute Timeframe (Last day) ===")
    strategy.analyze_stock('AAPL', timeframe='5m', period='1d')
    
    print("\n=== 1 Hour Timeframe (Last 5 days) ===")
    strategy.analyze_stock('AAPL', timeframe='1h', period='5d')
    
    print("\n=== Daily Timeframe (Last month) ===")
    strategy.analyze_stock('AAPL', timeframe='1d', period='1mo')
    
    # Test other stocks with daily timeframe
    print("\n=== Other Major Stocks (Daily Timeframe) ===")
    other_stocks = ['MSFT', 'GOOGL', 'NVDA']
    for symbol in other_stocks:
        strategy.analyze_stock(symbol, timeframe='1d', period='1mo')

if __name__ == "__main__":
    main()