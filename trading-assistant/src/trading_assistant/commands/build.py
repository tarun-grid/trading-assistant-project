# src/trading_assistant/commands/build.py

from typing import Dict, Optional
import json

class BuildCommand:
    def __init__(self, market_data):
        self.market_data = market_data
        
        # Portfolio size tiers
        self.portfolio_tiers = {
            'micro': {
                'size': 10000,
                'max_position_pct': 20,  # Max 20% of portfolio per trade
                'risk_per_trade_pct': 1  # Risk 1% of portfolio per trade
            },
            'small': {
                'size': 50000,
                'max_position_pct': 15,
                'risk_per_trade_pct': 1.5
            },
            'medium': {
                'size': 100000,
                'max_position_pct': 10,
                'risk_per_trade_pct': 2
            },
            'large': {
                'size': 500000,
                'max_position_pct': 5,
                'risk_per_trade_pct': 2
            },
            'institutional': {
                'size': 1000000,
                'max_position_pct': 3,
                'risk_per_trade_pct': 2.5
            }
        }
        
        # Pre-built strategy templates
        self.templates = {
            'macd_momentum': {
                'name': 'MACD Momentum Strategy',
                'timeframe': '4H',
                'market_type': 'Uptrend',
                'portfolio': self.portfolio_tiers['small'],  # Default to small tier
                'position_sizing': {
                    'type': 'risk_based',
                    'max_risk_per_trade': 1.5,  # % of portfolio
                    'max_position_size': 15     # % of portfolio
                },
                'validation': {
                    'macd': '5%_max_portfolio',
                    'histogram': 'Positive'
                },
                'trade': {
                    'take_profit': {
                        'type': 'levels',
                        'values': [8, 12]
                    },
                    'stop_loss': {
                        'type': 'entry_price',
                        'value': 5
                    }
                }
            },
            'rsi_reversal': {
                'name': 'RSI Reversal Strategy',
                'timeframe': '1h',
                'market_type': 'Any',
                'portfolio': self.portfolio_tiers['medium'],  # Default to medium tier
                'position_sizing': {
                    'type': 'risk_based',
                    'max_risk_per_trade': 2,    # % of portfolio
                    'max_position_size': 10     # % of portfolio
                },
                'validation': {
                    'rsi': {
                        'oversold': 30,
                        'overbought': 70
                    },
                    'volume': '1.5x_average'
                },
                'trade': {
                    'take_profit': {
                        'type': 'fixed',
                        'value': 10
                    },
                    'stop_loss': {
                        'type': 'atr',
                        'value': 2,     # Added this line
                        'multiplier': 2
                    }
                }
            }
        }

    def _configure_portfolio(self) -> Dict:
        """Configure portfolio settings"""
        print("\n💰 Portfolio Configuration")
        print("=" * 40)
        
        print("\nAvailable Portfolio Tiers:")
        print("1. Micro    ($10,000)  - Max Position: 20%, Risk/Trade: 1%")
        print("2. Small    ($50,000)  - Max Position: 15%, Risk/Trade: 1.5%")
        print("3. Medium   ($100,000) - Max Position: 10%, Risk/Trade: 2%")
        print("4. Large    ($500,000) - Max Position: 5%, Risk/Trade: 2%")
        print("5. Institutional ($1M) - Max Position: 3%, Risk/Trade: 2.5%")
        print("6. Custom")
        
        choice = input("\nSelect portfolio tier (1-6): ").strip()
        
        if choice == '6':
            # Custom portfolio configuration
            size = float(input("Enter portfolio size ($): ").strip())
            max_position = float(input("Maximum position size (%): ").strip())
            risk_per_trade = float(input("Risk per trade (%): ").strip())
            
            return {
                'size': size,
                'max_position_pct': max_position,
                'risk_per_trade_pct': risk_per_trade
            }
        else:
            # Pre-defined tier
            tier_map = {
                '1': 'micro',
                '2': 'small',
                '3': 'medium',
                '4': 'large',
                '5': 'institutional'
            }
            return self.portfolio_tiers[tier_map.get(choice, 'small')]

    def _calculate_position_size(self, portfolio: Dict, price: float, stop_loss_pct: float) -> Dict:
        """Calculate position size based on risk parameters"""
        risk_amount = portfolio['size'] * (portfolio['risk_per_trade_pct'] / 100)
        position_value = risk_amount / (stop_loss_pct / 100)
        max_position_value = portfolio['size'] * (portfolio['max_position_pct'] / 100)
        
        # Ensure position doesn't exceed maximum allowed
        position_value = min(position_value, max_position_value)
        shares = int(position_value / price)
        
        return {
            'shares': shares,
            'value': shares * price,
            'risk_amount': risk_amount,
            'pct_of_portfolio': (shares * price / portfolio['size']) * 100
        }
    
    def execute(self, arg: str = '') -> None:
        """Execute build command"""
        args = arg.split()
        
        if not args:
            self._show_help()
            return
            
        subcommand = args[0]
        
        if subcommand == 'new':
            self._create_strategy()
        elif subcommand == 'template':
            self._use_template(args[1] if len(args) > 1 else None)
        elif subcommand == 'list':
            self._list_templates()
        else:
            self._show_help()
    
    def _list_templates(self) -> None:
        """Display available strategy templates"""
        print("\n📋 Available Strategy Templates:")
        print("=" * 40)
        
        for key, template in self.templates.items():
            print(f"\n🔹 {template['name']} ({key})")
            print(f"   Timeframe: {template['timeframe']}")
            print(f"   Market Type: {template['market_type']}")
            print(f"   Portfolio Size: ${template['portfolio']['size']:,}")
            print(f"   Position Sizing:")
            print(f"     - Max Risk per Trade: {template['position_sizing']['max_risk_per_trade']}%")
            print(f"     - Max Position Size: {template['position_sizing']['max_position_size']}%")
            
            if key == 'macd_momentum':
                print(f"   MACD Settings:")
                print(f"     - Threshold: {template['validation']['macd']}")
                print(f"     - Histogram: {template['validation']['histogram']}")
            elif key == 'rsi_reversal':
                print(f"   RSI Settings:")
                print(f"     - Oversold: {template['validation']['rsi']['oversold']}")
                print(f"     - Overbought: {template['validation']['rsi']['overbought']}")
                print(f"     - Volume Requirement: {template['validation']['volume']}")
            
            print(f"   Trade Rules:")
            tp = template['trade']['take_profit']
            sl = template['trade']['stop_loss']
            
            # Handle different take profit types
            if tp['type'] == 'levels':
                print(f"     - Take Profit: {tp['values']}%")
            else:
                print(f"     - Take Profit: {tp['value']}%")
            
            # Handle different stop loss types
            if sl['type'] == 'entry_price':
                print(f"     - Stop Loss: {sl['value']}% (from entry)")
            elif sl['type'] == 'atr':
                print(f"     - Stop Loss: {sl['multiplier']}x ATR")

                
    def _use_template(self, template_name: str = None) -> None:
        """Use or customize a strategy template"""
        if not template_name:
            print("❌ Please specify a template name")
            self._list_templates()
            return
            
        if template_name not in self.templates:
            print(f"❌ Template '{template_name}' not found")
            self._list_templates()
            return
            
        template = self.templates[template_name]
        print(f"\n📝 Using template: {template['name']}")
        
        customize = input("\nWould you like to customize this template? (y/n): ").strip().lower()
        
        if customize == 'y':
            self._create_strategy(template)  # Pass template as base
        else:
            # Use template as-is
            strategy_name = input("\nEnter name for this strategy (default: template name): ").strip()
            if not strategy_name:
                strategy_name = template_name
            
            self._save_strategy(strategy_name, template)
            self._show_strategy_summary(strategy_name, template)
        
    def _create_strategy(self, base_template: Dict = None) -> None:
        """Create new trading strategy or customize template"""
        print("\n🔨 Strategy Builder")
        print("=" * 40)
        
        if base_template:
            print("Customizing template: Press Enter to keep default values")
            template = base_template
        else:
            template = self.templates['macd_momentum'].copy()  # Use as default
            
        config = {}
        
        # 1. Timeframe
        print("\n⏰ Timeframe Selection:")
        timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        for i, tf in enumerate(timeframes, 1):
            print(f"{i}. {tf}")
        choice = input(f"Select timeframe (default {template['timeframe']}): ").strip()
        config['timeframe'] = choice if choice in timeframes else template['timeframe']
        
        # 2. Market Type
        print("\n📈 Market Type Selection:")
        market_types = ['Uptrend', 'Downtrend', 'Sideways', 'Any']
        for i, mt in enumerate(market_types, 1):
            print(f"{i}. {mt}")
        choice = input(f"Select market type (default {template['market_type']}): ").strip()
        config['market_type'] = market_types[int(choice)-1] if choice.isdigit() and 1 <= int(choice) <= len(market_types) else template['market_type']
        
        # 3. Portfolio Configuration
        print("\n💰 Portfolio Configuration")
        config['portfolio'] = self._configure_portfolio()
        
        # 4. Strategy Type Selection
        print("\n📊 Strategy Type Selection:")
        print("1. MACD Momentum")
        print("2. RSI Reversal")
        print("3. Custom")
        strategy_type = input("Select strategy type (1-3): ").strip()
        
        # 5. Configure Strategy Parameters
        if strategy_type == '1':
            config.update(self._configure_macd_strategy())
        elif strategy_type == '2':
            config.update(self._configure_rsi_strategy())
        else:
            config.update(self._configure_custom_strategy())
        
        # 6. Name and Save Strategy
        strategy_name = input("\nEnter strategy name: ").strip()
        if strategy_name:
            self._save_strategy(strategy_name, config)
            self._show_strategy_summary(strategy_name, config)
        else:
            print("❌ Strategy name required")

    def _save_strategy(self, strategy_name: str, config: Dict) -> None:
        """Save strategy configuration to file"""
        try:
            # Try to load existing strategies
            try:
                with open('strategies.json', 'r') as f:
                    strategies = json.load(f)
            except FileNotFoundError:
                strategies = {}
            
            # Add or update strategy
            strategies[strategy_name] = config
            
            # Save back to file
            with open('strategies.json', 'w') as f:
                json.dump(strategies, f, indent=4)
                
            print(f"\n✅ Strategy '{strategy_name}' saved successfully!")
            
        except Exception as e:
            print(f"❌ Error saving strategy: {str(e)}")

    def _show_strategy_summary(self, strategy_name: str, config: Dict) -> None:
        """Display strategy configuration summary"""
        print(f"\n📊 Strategy Summary: {strategy_name}")
        print("=" * 40)
        
        # Basic Settings
        print(f"Timeframe: {config['timeframe']}")
        print(f"Market Type: {config['market_type']}")
        
        # Portfolio Settings
        print(f"\nPortfolio Configuration:")
        print(f"Size: ${config['portfolio']['size']:,}")
        print(f"Max Position: {config['portfolio']['max_position_pct']}%")
        print(f"Risk per Trade: {config['portfolio']['risk_per_trade_pct']}%")
        
        # Strategy-specific validation
        print("\nValidation Rules:")
        if 'macd' in config['validation']:
            print(f"MACD Threshold: {config['validation']['macd']}")
            print(f"Histogram: {config['validation']['histogram']}")
        elif 'rsi' in config['validation']:
            print(f"RSI Oversold: {config['validation']['rsi']['oversold']}")
            print(f"RSI Overbought: {config['validation']['rsi']['overbought']}")
            print(f"Volume Requirement: {config['validation']['volume']}")
        
        # Trade Rules
        print("\nTrade Rules:")
        tp = config['trade']['take_profit']
        sl = config['trade']['stop_loss']
        
        if tp['type'] == 'levels':
            print(f"Take Profit Levels: {tp['values']}%")
        else:
            print(f"Take Profit: {tp['value']}%")
            
        print(f"Stop Loss: {sl['value']}% ({sl['type']})")
        
        print("\nUsage:")
        print(f"/backtest {strategy_name} SYMBOL")            

    def _configure_macd_strategy(self) -> Dict:
        """Configure MACD strategy parameters"""
        config = {
            'validation': {
                'macd': input("\nMACD threshold (default 5%_max_portfolio): ").strip() or '5%_max_portfolio',
                'histogram': input("Histogram (Positive/Negative, default Positive): ").strip() or 'Positive'
            },
            'trade': {
                'take_profit': {
                    'type': 'levels',
                    'values': []
                },
                'stop_loss': {
                    'type': 'entry_price',
                    'value': 0
                }
            }
        }
        
        # Configure Take Profit Levels
        print("\n📈 Take Profit Configuration:")
        tp1 = float(input("Take Profit Level 1 % (default 8): ").strip() or 8)
        tp2 = float(input("Take Profit Level 2 % (default 12): ").strip() or 12)
        config['trade']['take_profit']['values'] = [tp1, tp2]
        
        # Configure Stop Loss
        print("\n🛑 Stop Loss Configuration:")
        sl = float(input("Stop Loss % below entry (default 5): ").strip() or 5)
        config['trade']['stop_loss']['value'] = sl
        
        return config

    def _configure_rsi_strategy(self) -> Dict:
        """Configure RSI strategy parameters"""
        config = {
            'validation': {
                'rsi': {
                    'oversold': int(input("\nRSI Oversold Level (default 30): ").strip() or 30),
                    'overbought': int(input("RSI Overbought Level (default 70): ").strip() or 70)
                },
                'volume': input("Volume requirement (default 1.5x_average): ").strip() or '1.5x_average'
            },
            'trade': {
                'take_profit': {
                    'type': 'fixed',
                    'value': float(input("\nTake Profit % (default 10): ").strip() or 10)
                },
                'stop_loss': {
                    'type': 'atr',
                    'multiplier': float(input("Stop Loss ATR Multiplier (default 2): ").strip() or 2)
                }
            }
        }
        
        return config
    
    def _show_help(self) -> None:
        """Show build command help"""
        print("""
🔨 Strategy Builder Commands:
---------------------------
/build new                 : Create new strategy
/build template <name>     : Use or customize template
/build list               : List available templates

Examples:
/build template macd_momentum
/build template rsi_reversal
        """)