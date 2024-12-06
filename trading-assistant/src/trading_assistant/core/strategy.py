# src/trading_assistant/commands/strategy.py

class StrategyCommand:
    def __init__(self, market_data):
        self.market_data = market_data
        self.strategies = {
            'rsi_reversal': {
                'name': 'RSI Reversal Strategy',
                'description': 'Trade RSI oversold and overbought conditions',
                'parameters': {
                    'rsi_period': 14,
                    'overbought_level': 70,
                    'oversold_level': 30
                }
            },
            'ma_crossover': {
                'name': 'Moving Average Crossover',
                'description': 'Trade when fast MA crosses slow MA',
                'parameters': {
                    'fast_ma': 20,
                    'slow_ma': 50
                }
            },
            'breakout': {
                'name': 'Breakout Strategy',
                'description': 'Trade breakouts from price ranges',
                'parameters': {
                    'lookback_period': 20,
                    'volatility_factor': 2.0
                }
            }
        }
        
    def execute(self, arg=''):
        """Execute strategy command with arguments"""
        args = arg.split()
        
        if not args:
            self._list_strategies()
            return
            
        command = args[0]
        if command == 'list':
            self._list_strategies()
        elif command == 'info' and len(args) > 1:
            self._show_strategy_info(args[1])
        elif command == 'customize' and len(args) > 1:
            self._customize_strategy(args[1])
        else:
            self._show_help()
    
    def _list_strategies(self):
        """Show available strategy templates"""
        print("\n📊 Available Strategy Templates:")
        print("--------------------------------")
        for key, strategy in self.strategies.items():
            print(f"\n{strategy['name']} (/strategy info {key})")
            print(f"Description: {strategy['description']}")
    
    def _show_strategy_info(self, strategy_key):
        """Show detailed information about a strategy"""
        if strategy_key not in self.strategies:
            print(f"❌ Strategy '{strategy_key}' not found")
            return
            
        strategy = self.strategies[strategy_key]
        print(f"\n📈 {strategy['name']}")
        print("-" * 40)
        print(f"Description: {strategy['description']}")
        print("\nParameters:")
        for param, value in strategy['parameters'].items():
            print(f"- {param}: {value}")
        print("\nUsage:")
        print(f"/strategy customize {strategy_key}")
    
    def _customize_strategy(self, strategy_key):
        """Customize strategy parameters"""
        if strategy_key not in self.strategies:
            print(f"❌ Strategy '{strategy_key}' not found")
            return
            
        strategy = self.strategies[strategy_key]
        print(f"\n⚙️ Customizing {strategy['name']}")
        print("Enter new values or press enter to keep default")
        
        new_params = {}
        for param, value in strategy['parameters'].items():
            user_input = input(f"{param} ({value}): ").strip()
            new_params[param] = float(user_input) if user_input else value
        
        # Update strategy parameters
        self.strategies[strategy_key]['parameters'] = new_params
        print("\n✅ Strategy parameters updated!")
        self._show_strategy_info(strategy_key)
    
    def _show_help(self):
        """Show strategy command help"""
        print("""
📊 Strategy Command Usage:
------------------------
/strategy           : List all available strategies
/strategy list     : List all available strategies
/strategy info <name> : Show detailed information about a strategy
/strategy customize <name> : Customize strategy parameters
        """)