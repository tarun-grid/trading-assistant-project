# src/trading_assistant/config.py

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_KEYS = {
    "ANTHROPIC": os.getenv("ANTHROPIC_API_KEY"),
    # Add other API keys here
}

# Check if required keys are present
if not API_KEYS["ANTHROPIC"]:
    print("⚠️ Warning: ANTHROPIC_API_KEY not found in environment variables")

# Other configuration settings
MARKET_DATA_SETTINGS = {
    "default_timeframe": "1d",
    "max_history_days": 365,
    "cache_duration": 3600  # 1 hour
}

STRATEGY_SETTINGS = {
    "max_position_size": 0.25,  # 25% of portfolio
    "default_stop_loss": 0.02,  # 2%
    "default_take_profit": 0.06  # 6%
}

# Then update ai_agent.py to use config
from trading_assistant.config import API_KEYS

class AITradingAgent:
    def __init__(self, market_data):
        # Initialize market data and commands
        self.market_data = market_data
        self.scan_cmd = ScanCommand(market_data)
        self.analyze_cmd = AnalyzeCommand(market_data)
        self.strategy_cmd = StrategyCommand(market_data)
        self.backtest_cmd = BacktestCommand(market_data)
        self.build_cmd = BuildCommand(market_data)
        self.persona_cmd = PersonaCommand()
        
        # Initialize Claude client
        self.api_key = API_KEYS["ANTHROPIC"]
        if self.api_key:
            self.claude = anthropic.Client(api_key=self.api_key)
        else:
            print("⚠️ ANTHROPIC_API_KEY not found in config. AI features will be limited.")
            self.claude = None