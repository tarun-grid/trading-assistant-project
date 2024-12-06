# trading_strategy.py

from market_data import MarketData

class TradingStrategy:
    def __init__(self):
        self.market_data = MarketData()
    
    def analyze_stock(self, symbol, timeframe='1d', period='1mo'):
        """
        Analyze a stock with specified timeframe and period
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            timeframe: Data interval ('5m', '1h', '1d')
            period: Time period ('1d', '5d', '1mo', etc.)
        """
        data = self.market_data.fetch_data(symbol, period=period, interval=timeframe)
        
        if data is not None and len(data) > 0:
            latest = data.iloc[-1]
            
            print(f"\n=== Analysis for {symbol} ({timeframe}) ===")
            print(f"Current Price: ${latest['Close']:.2f}")
            
            # Technical Indicators
            if 'RSI' in data.columns:
                print(f"RSI: {latest['RSI']:.2f}")
                if latest['RSI'] > 70:
                    print("⚠️ RSI shows overbought")
                elif latest['RSI'] < 30:
                    print("⚠️ RSI shows oversold")
                else:
                    print("✅ RSI in normal range")
            
            # MACD Analysis
            if all(x in data.columns for x in ['MACD', 'MACD_Signal']):
                macd_cross = latest['MACD'] - latest['MACD_Signal']
                print(f"MACD: {latest['MACD']:.2f}")
                if macd_cross > 0:
                    print("📈 MACD shows bullish signal")
                else:
                    print("📉 MACD shows bearish signal")
            
            # Moving Averages
            if all(x in data.columns for x in ['SMA_20', 'SMA_50']):
                print(f"\nMoving Averages:")
                print(f"SMA 20: ${latest['SMA_20']:.2f}")
                print(f"SMA 50: ${latest['SMA_50']:.2f}")
                
                if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
                    print("🟢 Strong uptrend")
                elif latest['Close'] < latest['SMA_20'] < latest['SMA_50']:
                    print("🔴 Strong downtrend")
                else:
                    print("🟡 Mixed trend")
            
            # Volume Analysis
            if 'Volume_SMA' in data.columns:
                vol_ratio = latest['Volume'] / latest['Volume_SMA']
                print(f"\nVolume Analysis:")
                print(f"Current Volume: {int(latest['Volume']):,}")
                print(f"Volume Ratio to 20-day avg: {vol_ratio:.2f}x")
                if vol_ratio > 1.5:
                    print("📊 High volume alert!")
                elif vol_ratio < 0.5:
                    print("📉 Low volume warning")