# src/trading_assistant/commands/strategy.py

from typing import Dict, Any
import json
from dataclasses import dataclass

@dataclass
class StrategyParameters:
    entry: Dict
    filters: Dict
    risk_management: Dict
    timeframes: Dict = None

class StrategyCommand:
    def __init__(self, market_data):
        self.market_data = market_data
        self.strategies = {
            'rsi_reversal': {
                'name': 'RSI Reversal Strategy',
                'description': 'Advanced RSI strategy with multi-timeframe confirmation',
                'parameters': {
                    'entry': {
                        'rsi_period': 14,
                        'rsi_overbought': 70,
                        'rsi_oversold': 30,
                        'confirmation_timeframe': '1h',
                        'min_volume_multiplier': 1.5
                    },
                    'filters': {
                        'trend_filter': True,   # Use higher timeframe trend
                        'volume_filter': True,  # Check volume confirmation
                        'volatility_filter': True,  # Use ATR filter
                        'minimum_atr': 1.0,
                        'maximum_spread': 0.1   # Maximum allowed spread
                    },
                    'risk_management': {
                        'position_size_pct': 2.0,  # % of portfolio per trade
                        'stop_loss_atr_multiplier': 2.0,  # ATR multiplier for stop loss
                        'take_profit_atr_multiplier': 4.0,  # ATR multiplier for take profit
                        'trailing_stop': True,
                        'trailing_stop_activation': 1.5,  # ATR multiplier for trailing
                        'max_trades_per_day': 3
                    },
                    'timeframes': {
                        'primary': '1d',
                        'secondary': '1h',
                        'confirmation': '15m'
                    }
                },
                'rules': [
                    "1. Entry Rules:",
                    "   • Buy when RSI < oversold level (30) on primary timeframe",
                    "   • Sell when RSI > overbought level (70) on primary timeframe",
                    "   • Confirm with RSI direction on secondary timeframe",
                    "2. Filter Rules:",
                    "   • Trend must align on higher timeframe",
                    "   • Volume must be above average * multiplier",
                    "   • ATR must be above minimum threshold",
                    "3. Risk Management:",
                    "   • Position size: 2% of portfolio",
                    "   • Stop loss: 2 * ATR from entry",
                    "   • Take profit: 4 * ATR from entry",
                    "   • Enable trailing stop after 1.5 * ATR profit"
                ]
            },
            'ma_crossover': {
                'name': 'Advanced MA Crossover',
                'description': 'Multi-timeframe MA strategy with volume and trend confirmation',
                'parameters': {
                    'entry': {
                        'fast_ma_type': 'EMA',
                        'fast_ma_period': 20,
                        'slow_ma_type': 'SMA',
                        'slow_ma_period': 50,
                        'signal_ma_period': 200,
                        'min_crossover_angle': 15
                    },
                    'filters': {
                        'volume_confirmation': True,
                        'min_volume_increase': 1.5,
                        'trend_alignment': True,
                        'volatility_check': True
                    },
                    'risk_management': {
                        'position_size_pct': 2.0,
                        'fixed_stop_loss_pct': 2.5,
                        'trailing_stop': True,
                        'trailing_stop_step': 0.5,
                        'max_loss_per_day_pct': 5.0
                    }
                },
                'rules': [
                    "1. Entry Rules:",
                    "   • Buy when fast MA crosses above slow MA",
                    "   • Sell when fast MA crosses below slow MA",
                    "   • Minimum crossing angle must be 15 degrees",
                    "2. Filter Rules:",
                    "   • Price must be above 200 MA for longs",
                    "   • Volume must increase on crossover",
                    "   • Trend must align on higher timeframe",
                    "3. Risk Management:",
                    "   • Fixed 2.5% stop loss",
                    "   • Trailing stop with 0.5% step",
                    "   • Maximum 5% loss per day"
                ]
            },
            'breakout': {
                'name': 'Advanced Breakout Strategy',
                'description': 'Volatility adjusted breakout with multiple confirmations',
                'parameters': {
                    'entry': {
                        'lookback_period': 20,
                        'breakout_atr_multiplier': 2.0,
                        'volume_breakout_factor': 2.0,
                        'minimum_range_days': 5
                    },
                    'filters': {
                        'false_breakout_filter': True,
                        'wait_for_candle_close': True,
                        'min_range_atr_multiplier': 1.5,
                        'trend_alignment': True
                    },
                    'risk_management': {
                        'position_size_pct': 2.0,
                        'stop_loss_atr_multiplier': 2.0,
                        'take_profit_atr_multiplier': 6.0,
                        'scale_out_levels': [0.33, 0.66, 1.0],
                        'max_trades_per_week': 5
                    }
                },
                'rules': [
                    "1. Entry Rules:",
                    "   • Identify range over lookback period",
                    "   • Buy on breakout above range + (2 * ATR)",
                    "   • Sell on breakout below range - (2 * ATR)",
                    "2. Filter Rules:",
                    "   • Wait for candle close beyond breakout level",
                    "   • Volume must be 2x average on breakout",
                    "   • Range must be at least 1.5 * ATR",
                    "3. Risk Management:",
                    "   • Stop loss: 2 * ATR from entry",
                    "   • Scale out at 33%, 66%, and 100% targets",
                    "   • Maximum 5 trades per week"
                ]
            }
        }

    def execute(self, arg: str = '') -> None:
        """Execute strategy command"""
        args = arg.split()
        
        if not args:
            self._show_help()
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

    def _list_strategies(self) -> None:
        """Display available strategy templates"""
        print("\n📋 Available Strategy Templates:")
        print("=" * 40)
        
        for key, strategy in self.strategies.items():
            print(f"\n🔹 {strategy['name']} (/strategy info {key})")
            print(f"Description: {strategy['description']}")

    def _show_strategy_info(self, strategy_key: str) -> None:
        """Show detailed strategy information"""
        if strategy_key not in self.strategies:
            print(f"❌ Strategy '{strategy_key}' not found")
            return
            
        strategy = self.strategies[strategy_key]
        print(f"\n📈 {strategy['name']}")
        print("=" * 40)
        print(f"Description: {strategy['description']}")
        
        # Parameters
        print("\n📊 Parameters:")
        for section in ['entry', 'filters', 'risk_management']:
            if section in strategy['parameters']:
                print(f"\n{section.replace('_', ' ').title()}:")
                for param, value in strategy['parameters'][section].items():
                    print(f"• {param}: {value}")
        
        # Rules
        print("\n📋 Trading Rules:")
        print("-" * 20)
        for rule in strategy['rules']:
            print(rule)
        
        print("\n💡 Usage:")
        print(f"/strategy customize {strategy_key}")
        print(f"/backtest {strategy_key} SYMBOL")

    def _customize_strategy(self, strategy_key: str) -> None:
        """Customize strategy parameters"""
        if strategy_key not in self.strategies:
            print(f"❌ Strategy '{strategy_key}' not found")
            return
            
        strategy = self.strategies[strategy_key].copy()
        print(f"\n⚙️ Customizing {strategy['name']}")
        
        # Customize parameters by section
        for section in ['entry', 'filters', 'risk_management']:
            if section in strategy['parameters']:
                print(f"\n📝 {section.replace('_', ' ').title()} Parameters:")
                print("-" * 40)
                
                for param, default_value in strategy['parameters'][section].items():
                    while True:
                        try:
                            user_input = input(f"{param} (current: {default_value}): ").strip()
                            if not user_input:  # Keep default
                                break
                                
                            # Convert to appropriate type
                            if isinstance(default_value, bool):
                                new_value = user_input.lower() in ['true', 'yes', 'y', '1']
                            elif isinstance(default_value, float):
                                new_value = float(user_input)
                            elif isinstance(default_value, int):
                                new_value = int(user_input)
                            else:
                                new_value = user_input
                                
                            strategy['parameters'][section][param] = new_value
                            break
                        except ValueError:
                            print("❌ Invalid input. Please try again.")
        
        # Save customized strategy
        self._save_strategy(strategy_key, strategy)
        print("\n✅ Strategy updated successfully!")
        self._show_strategy_info(strategy_key)

    def _save_strategy(self, strategy_key: str, strategy: Dict) -> None:
        """Save strategy to file"""
        try:
            # Load existing strategies
            try:
                with open('strategies.json', 'r') as f:
                    strategies = json.load(f)
            except FileNotFoundError:
                strategies = {}
            
            # Update strategy
            strategies[strategy_key] = strategy
            
            # Save back to file
            with open('strategies.json', 'w') as f:
                json.dump(strategies, f, indent=4)
                
            print(f"\n✅ Strategy saved to strategies.json")
            
        except Exception as e:
            print(f"❌ Error saving strategy: {str(e)}")

    def _show_help(self) -> None:
        """Show help message"""
        print("""
📈 Strategy Command Usage:
------------------------
/strategy list              : List all available strategies
/strategy info <name>       : Show detailed strategy information
/strategy customize <name>  : Customize strategy parameters
        """)

    def validate_parameters(self, parameters: Dict) -> bool:
        """Validate strategy parameters"""
        required_sections = ['entry', 'filters', 'risk_management']
        
        for section in required_sections:
            if section not in parameters:
                print(f"❌ Missing required section: {section}")
                return False
                
        return True