from typing import Dict, Any, Optional
import pandas as pd
import json

class SophieAgent:
    def __init__(self, market_data, llm_handler):
        self.market_data = market_data
        self.llm_handler = llm_handler
        self._last_used = False

    # Add this method right after __init__
    def _show_help(self) -> None:
        """Show Sophie's help message"""
        print("""
👩‍💼 Sophie - The Growth Accelerator
================================
Dynamic portfolio strategist focusing on high-growth opportunities.

Available Commands:
-----------------
analyze <symbol>  : Get growth-focused analysis
scan             : Find growth opportunities
build <strategy> : Create growth-oriented strategy
backtest <params>: Test strategy performance

Examples:
--------
/sophie analyze AAPL     : Analyze Apple's growth potential
/sophie scan tech        : Find high-growth tech stocks
/sophie build aggressive : Create aggressive growth strategy
/sophie backtest TSLA    : Test growth strategy
        """)

    def execute(self, arg: str = '', structured_params: Dict = None) -> None:
        """Execute Sophie's commands with LLM integration"""
        try:
            if not arg:
                self._show_help()
                return

            # Parse intent from natural language
            target_symbol = self._extract_symbol(arg)  # Extract stock symbol first
            
            # Handle natural language
            if 'what' in arg.lower() or 'think' in arg.lower():
                if target_symbol:
                    self._handle_analysis(target_symbol, structured_params)
                    return
                    
            # Fallback to command processing
            cmd_parts = arg.split()
            cmd_type = cmd_parts[0]
            params = ' '.join(cmd_parts[1:]) if len(cmd_parts) > 1 else ''

            command_handlers = {
                'analyze': self._handle_analysis,
                'scan': self._handle_scan,
                'build': self._handle_strategy,
                'backtest': self._handle_backtest
            }
            
            if cmd_type in command_handlers:
                self._last_used = True
                response = command_handlers[cmd_type](params, structured_params)
                return response  

            else:
                print(f"❌ Unknown Sophie command: {cmd_type}")
                self._show_help()
                return None

        except Exception as e:
            print(f"🚫 Sophie execution error: {str(e)}")

    def _extract_symbol(self, text: str) -> str:
        """Extract stock symbol from text"""
        import re
        # Look for 1-5 letter stock symbols
        symbols = re.findall(r'\b[A-Z]{1,5}\b', text)
        return symbols[0] if symbols else None    

    def _is_crypto_request(self, text: str) -> bool:
        """Check if request is crypto-related"""
        crypto_terms = [
            'crypto', 'bitcoin', 'btc', 'eth', 'ethereum', 'blockchain', 
            'defi', 'nft', 'token', 'binance', 'coinbase', 'altcoin'
        ]
        return any(term in text.lower() for term in crypto_terms)
    


    def _get_sophie_prompt(self, cmd_type: str) -> str:
        """Get Sophie-specific system prompts"""
        if cmd_type == "analyze":
            return """You are Sophie, a growth-focused portfolio strategist specializing in stock analysis. 
            Return analysis in this exact JSON structure:
            {
                "company": "<company name>",
                "ticker": "<ticker symbol>",
                "sector": "<sector>",
                "analysis": "<core growth analysis>",
                "metrics": {
                    "growth_rate": "<YoY growth>",
                    "market_position": "<market position>",
                    "competitive_advantages": ["<list of advantages>"]
                },
                "risks": "<key risks>",
                "catalysts": ["<list of growth catalysts>"],
                "recommendation": "<your recommendation>",
                "target_allocation": "<suggested portfolio allocation>",
                "entry_strategy": "<entry approach>"
                }"""    

    def _handle_analysis(self, symbol: str, response: Dict) -> None:
        """Handle stock analysis with LLM insights"""
        try:
            print(f"\n👩‍💼 Sophie's Growth Analysis for {symbol}")
            print("=" * 50)

            # Market Data
            data = self.market_data.fetch_data(symbol)
            if data is None:
                print(f"❌ Could not fetch data for {symbol}")
                return

            latest = data.iloc[-1]
            print("\n📈 Technical Overview:")
            print(f"• Current Price: ${latest['Close']:.2f}")
            print(f"• RSI: {latest['RSI']:.2f} ({'Overbought' if latest['RSI'] > 70 else 'Oversold' if latest['RSI'] < 30 else 'Neutral'})")
            print(f"• Momentum: {latest['MACD']:.2f} ({'Positive' if latest['MACD'] > 0 else 'Negative'})")
            print(f"• Volume: {latest['Volume']:,.0f}")

            # Growth Analysis
            if 'analysis' in response:
                print("\n🔍 Growth Perspective:")
                analysis_text = response['analysis']
                if isinstance(analysis_text, dict):
                    # Handle nested analysis structure
                    for key, value in analysis_text.items():
                        if isinstance(value, str):
                            print(self._format_paragraph(value))
                elif isinstance(analysis_text, str):
                    # Handle direct string analysis
                    print(self._format_paragraph(analysis_text))

            # Rationale (if present)
            if 'rationale' in response:
                print("\n💡 Investment Rationale:")
                print(self._format_paragraph(response['rationale']))

            # Recommendation
            if 'rating' in response or 'recommendation' in response:
                print("\n🎯 Sophie's Recommendation:")
                rating = response.get('rating') or response.get('recommendation')
                print(f"• Action: {rating}")
                
                # Handle different price target formats
                if 'target_price' in response:
                    print(f"• Target Price: ${response['target_price']}")
                elif 'target_price_range' in response:
                    print(f"• Target Price Range: {response['target_price_range']}")

        except Exception as e:
            print(f"❌ Analysis error: {str(e)}")
            import traceback
            traceback.print_exc()

    def _format_paragraph(self, text: str) -> str:
        """Format long text into readable paragraphs"""
        width = 80
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                
        if current_line:
            lines.append(' '.join(current_line))
            
        return '\n'.join(lines)
   

    def _handle_scan(self, criteria: str, structured_params: Dict) -> None:
        """Handle market scanning with Sophie's growth focus"""
        try:
            print("\n👩‍💼 Sophie's Growth Scan")
            print("=" * 50)
            print("🔍 Scanning market for growth opportunities...")

            # Get market overview - avoiding fetching for the word "scan"
            overview = self.market_data.get_market_overview()
            
            if not isinstance(overview, pd.DataFrame) or overview.empty:
                print("❌ No market data available")
                return

            # Extract scan criteria
            scan_params = structured_params.get('scan_criteria', {})
            
            # Show scan criteria
            if scan_params:
                print("\n📊 Scan Parameters:")
                if 'growth_metrics' in scan_params:
                    metrics = scan_params['growth_metrics']
                    print("\nGrowth Requirements:")
                    print(f"• Revenue Growth > {metrics.get('min_revenue_growth', 'N/A')}%")
                    print(f"• Earnings Growth > {metrics.get('min_earnings_growth', 'N/A')}%")
                    print(f"• Margin Threshold > {metrics.get('margin_threshold', 'N/A')}%")

                if 'momentum_filters' in scan_params:
                    filters = scan_params['momentum_filters']
                    print("\nTechnical Filters:")
                    print(f"• RSI Range: {filters['rsi_range']['min']} - {filters['rsi_range']['max']}")
                    print(f"• Volume Threshold: {filters['volume_threshold']}")
                    print(f"• Trend: {filters['trend_strength']}")

            # Find matches
            matches = []
            print("\n🔍 Analyzing stocks...")
            for _, stock in overview.iterrows():
                if self._meets_growth_criteria(stock, scan_params):
                    matches.append(stock)
            
            response = {"message": "", "data": []}
            
            if matches:
                response["message"] = f"Found {len(matches)} growth opportunities"
                for stock in matches:
                    stock_info = {
                        "Symbol": stock["Symbol"],
                        "Price": round(stock["Price"], 2),
                        "RSI": round(stock["RSI"], 2),
                        "Volume": f"{stock['Volume']:,}"
                    }
                    response["data"].append(stock_info)
            else:
                response["message"] = "❌ No stocks currently meet the growth criteria"

            return response 
        
        except Exception as e:
            print(f"❌ Scan error: {str(e)}")

    def _meets_growth_criteria(self, stock: pd.Series, params: Dict) -> bool:
        """Check if stock meets Sophie's growth criteria"""
        try:
            if not params or 'scan_criteria' not in params:
                return self._basic_growth_check(stock)

            criteria = params['scan_criteria']
            
            # Technical Checks
            if 'momentum_filters' in criteria:
                filters = criteria['momentum_filters']
                
                # RSI Check
                if 'rsi_range' in filters:
                    rsi_range = filters['rsi_range']
                    if not (rsi_range['min'] <= stock['RSI'] <= rsi_range['max']):
                        return False

                # Volume Check
                if 'volume_threshold' in filters:
                    min_volume = float(filters['volume_threshold'].replace('M', '000000'))
                    if stock['Volume'] < min_volume:
                        return False

            # Growth Metrics
            if 'growth_metrics' in criteria:
                metrics = criteria['growth_metrics']
                
                if 'min_revenue_growth' in metrics:
                    min_growth = float(metrics['min_revenue_growth'])
                    if stock.get('Revenue_Growth', 0) < min_growth:
                        return False

            return True

        except Exception as e:
            print(f"Warning: Error checking criteria for {stock.get('Symbol')}: {str(e)}")
            return False

    def _basic_growth_check(self, stock: pd.Series) -> bool:
        """Basic growth stock filtering"""
        try:
            # Basic technical conditions
            return (
                stock.get('RSI', 0) > 50 and  # Showing strength
                stock.get('MACD', 0) > 0 and  # Positive momentum
                stock['Volume'] > stock.get('Volume_SMA', 0)  # Above average volume
            )
        except:
            return False

    def _get_quick_analysis(self, symbol: str) -> str:
        """Get quick growth thesis from LLM"""
        try:
            response = self.llm_handler.process_command(
                f"Give a one-sentence growth thesis for {symbol}",
                persona="sophie"
            )
            return response.get('analysis', '')
        except:
            return ""

    def _handle_strategy(self, params: str, llm_params: Dict) -> None:
        """Handle strategy building with Sophie's growth focus"""
        try:
            print("\n👩‍💼 Sophie's Growth Strategy Builder")
            print("=" * 50)

            if not llm_params:
                print("❌ No strategy parameters provided")
                return

            # Extract strategy components
            strategy = llm_params.get('strategy', {})
            entry = llm_params.get('entry_rules', {})
            position = llm_params.get('position_sizing', {})
            risk = llm_params.get('risk_management', {})

            # Display Strategy Overview
            print("\n📈 Growth Strategy Overview:")
            print(f"Strategy Name: {strategy.get('name', 'Growth Strategy')}")
            print(f"Type: {strategy.get('type', 'growth')}")
            print(f"Timeframe: {strategy.get('timeframe', '1d')}")
            print(f"Risk Profile: {strategy.get('risk_profile', 'moderate-aggressive')}")

            # Entry Rules
            if entry:
                print("\n📊 Entry Criteria:")
                print("\nGrowth Requirements:")
                for criterion in entry.get('growth_criteria', []):
                    print(f"• {criterion}")
                
                print("\nTechnical Triggers:")
                for trigger in entry.get('technical_triggers', []):
                    print(f"• {trigger}")

            # Position Sizing
            if position:
                print("\n💰 Position Sizing:")
                print(f"• Base Position: {position.get('base_position', '5')}%")
                print(f"• Maximum Position: {position.get('max_position', '15')}%")
                for rule in position.get('scaling_rules', []):
                    print(f"• {rule}")

            # Risk Management
            if risk:
                print("\n⚠️ Risk Management:")
                stop_loss = risk.get('stop_loss', {})
                print(f"• Initial Stop Loss: {stop_loss.get('initial', '7')}%")
                print(f"• Trailing Stop: {stop_loss.get('trailing', '5')}%")
                
                print("\nProfit Targets:")
                for target in risk.get('profit_targets', []):
                    print(f"• {target}%")
                
                print(f"\nMax Portfolio Risk: {risk.get('max_portfolio_risk', '25')}%")

            # Save strategy option
            save = input("\nWould you like to save this strategy? (y/n): ").lower()
            if save == 'y':
                name = input("Enter strategy name: ").strip()
                if name:
                    self._save_strategy(name, llm_params)
                    print(f"\n✅ Strategy '{name}' saved successfully!")
                    print(f"Use '/sophie backtest {name} SYMBOL' to test this strategy")

        except Exception as e:
            print(f"❌ Strategy building error: {str(e)}")    

    def _handle_backtest(self, params: str, llm_params: Dict) -> None:
        """Handle backtesting with LLM insights"""
        print("\n👩‍💼 Sophie's Backtest Analysis")
        print("=" * 50)

        try:
            if llm_params and 'backtest_config' in llm_params:
                config = llm_params['backtest_config']
                strategy = llm_params['strategy_params']
                
                print("\n📊 Backtest Configuration:")
                print(f"• Timeframe: {config['timeframe']}")
                print(f"• Initial Capital: ${config['initial_capital']:,}")
                print(f"• Position Sizing: {config['position_sizing']['type']}")
                print(f"• Risk per Trade: {config['position_sizing']['risk_per_trade']}%")

                print("\n📈 Strategy Parameters:")
                print(f"• Entry Threshold: {strategy['entry_threshold']}")
                print(f"• Stop Loss: {strategy['stop_loss']}%")
                print("• Take Profit Levels:")
                for level in strategy['take_profit']:
                    print(f"  - {level}%")

            else:
                # Fallback to basic backtest parameters
                self._show_basic_backtest()

        except Exception as e:
            print(f"❌ Backtest error: {str(e)}")

    def _filter_growth_opportunities(self, overview: pd.DataFrame, params: Dict) -> list:
        """Filter for growth opportunities using LLM parameters"""
        opportunities = []
        try:
            if params and 'scan_criteria' in params:
                criteria = params['scan_criteria']
                momentum = criteria['momentum_filters']
                
                for _, stock in overview.iterrows():
                    if (
                        stock.get('RSI', 0) > momentum['rsi_range']['min'] and
                        stock.get('RSI', 0) < momentum['rsi_range']['max'] and
                        stock.get('Volume', 0) > float(momentum['volume_threshold'])
                    ):
                        opportunities.append(stock)
            else:
                # Fallback to basic filtering
                for _, stock in overview.iterrows():
                    if (
                        stock.get('RSI', 0) > 50 and
                        stock.get('MACD', 0) > 0
                    ):
                        opportunities.append(stock)
                        
        except Exception as e:
            print(f"Warning: Using basic filtering due to error: {str(e)}")
            # Fallback to basic filtering on error
            return self._basic_filter_opportunities(overview)
            
        return opportunities

    def was_last_used(self) -> bool:
        return self._last_used

    # Helper methods with basic implementations as fallback
    def _show_basic_strategy(self):
        print("\n📊 Basic Growth Strategy:")
        print("• Entry: RSI < 30, Positive MACD")
        print("• Exit: RSI > 70, Negative MACD")
        print("• Stop Loss: 8%")
        print("• Take Profit: 15%")

    def _show_basic_backtest(self):
        print("\n📊 Basic Backtest Parameters:")
        print("• Timeframe: 1 year")
        print("• Initial Capital: $100,000")
        print("• Position Size: 10%")
        print("• Stop Loss: 8%")

    def _basic_filter_opportunities(self, overview: pd.DataFrame) -> list:
        return [stock for _, stock in overview.iterrows() 
                if stock.get('RSI', 0) > 50 and stock.get('MACD', 0) > 0]