# src/trading_assistant/commands/analyze.py

class AnalyzeCommand:
    def __init__(self, market_data):
        self.market_data = market_data
        
    def execute(self, arg=''):
        """Execute analyze command with symbol argument"""
        if not arg:
            print("❌ Please provide a symbol. Example: /analyze AAPL")
            return
            
        print(f"🔍 Analyzing {arg}...")
        try:
            data = self.market_data.fetch_data(arg, period='1mo', interval='1d')
            if data is not None:
                latest = data.iloc[-1]
                print(f"\nLatest Data for {arg}:")
                print(f"Price: ${latest['Close']:.2f}")
                print(f"RSI: {latest['RSI']:.2f}")
                print(f"Volume: {latest['Volume']:,}")
        except Exception as e:
            print(f"❌ Error analyzing {arg}: {str(e)}")