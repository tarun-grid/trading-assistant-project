from typing import Dict, Any, Optional
import pandas as pd
import json

class SophieAgent:
    def __init__(self, market_data, llm_handler):
        self.market_data = market_data
        self.llm_handler = llm_handler
        self._last_used = False
        
        # Define Sophie's boundaries
        self.boundaries = {
            "attributes": {
                "primary": [
                    "revenue_growth",
                    "earnings_growth",
                    "momentum_signals",
                    "market_position"
                ],
                "technical": [
                    "RSI",
                    "MACD",
                    "volume_profile"
                ]
            },
            "criteria": {
                "revenue_growth_min": 15,  # 15% minimum YoY
                "earnings_growth_min": 10,  # 10% minimum YoY
                "market_cap_min": 10_000_000_000,  # $10B minimum
                "volume_min": 1_000_000,  # 1M daily volume minimum
                "rsi_range": {"min": 40, "max": 70}
            },
            "specialization": {
                "focus": "growth",
                "style": "moderate-aggressive",
                "markets": ["US Stocks", "ADRs"],
                "sectors": {
                    "primary": ["Technology", "Healthcare", "Consumer"],
                    "secondary": ["Communications", "Industrials"],
                    "avoid": ["Utilities", "Basic Materials"]
                }
            }
        }
   
        

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

    def _handle_open_query(self, query: str, params: Dict) -> None:
        """Handle open-ended questions about Sophie's expertise"""
        query_lower = query.lower()
        
        # Investment style/expertise questions
        if any(word in query_lower for word in ['style', 'invest', 'approach', 'expertise']):
            print("\n👩‍💼 Investment Approach:")
            print("I focus on growth stocks with:")
            print("• Market cap > $10B")
            print("• Revenue growth > 15% YoY")
            print("• Strong momentum signals")
            print("\nKey sectors: Technology, Healthcare, Consumer, Communications")
            
        # Stock type questions
        elif 'stocks' in query_lower or 'analyze' in query_lower:
            print("\n👩‍💼 Focus Areas:")
            print("I analyze established growth companies with:")
            print("• Proven business models")
            print("• Market leadership position")
            print("• Technical strength (RSI 40-70)")
            print("• High trading volume (>1M daily)")
            
        # Default response
        else:
            print("\n👩‍💼 I'm a growth-focused strategist specializing in:")
            print("• High-growth stock analysis")
            print("• Growth momentum strategies")
            print("• Risk-managed portfolio construction")

    def execute(self, arg: str = '', structured_params: Dict = None) -> None:
        """Execute Sophie's commands with LLM integration"""
        try:
            if not arg:
                self._show_help()
                return

            # First check if request is within Sophie's boundaries
            is_valid, message = self._check_request_validity(arg)
            if not is_valid:
                print("\n👩‍💼 Growth Strategy Specialist:")
                print(message)
                print("\nI can help you with growth analysis of established companies. Would you like to:")
                print("• Analyze a growth stock")
                print("• Scan for growth opportunities")
                print("• Build a growth-focused strategy")
                return

            # Handle different types of queries
            if any(word in arg.lower() for word in ['what', 'think', 'how', 'should']):
                # Natural language query handling
                target_symbol = self._extract_symbol(arg)
                if target_symbol:
                    # Check if symbol meets growth criteria
                    if self._meets_growth_criteria(target_symbol):
                        return self._handle_analysis(target_symbol, structured_params)
                    else:
                        print(f"\n👩‍💼 {target_symbol} doesn't meet my growth criteria. I focus on companies with:")
                        print("• Minimum 15% revenue growth")
                        print("• Strong market position")
                        print("• Established market cap ($10B+)")
                        return
                else:
                    # Handle open-ended questions using all attributes
                    return self._handle_open_query(arg, structured_params)

            # Command processing
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
                return command_handlers[cmd_type](params, structured_params)
            else:
                print(f"❌ Unknown Sophie command: {cmd_type}")
                self._show_help()
                return None

        except Exception as e:
            print(f"🚫 Sophie execution error: {str(e)}")
            import traceback
            traceback.print_exc()

    def _validate_analyze_command(self, params: str) -> tuple[bool, str]:
        """Validate analyze command parameters"""
        if not params:
            return False, "Please provide a symbol to analyze"
            
        symbol = params.split()[0].upper()
        
        # Check if market data is available
        try:
            data = self.market_data.fetch_data(symbol, period="1mo")
            if data is None:
                return False, f"Unable to fetch data for {symbol}"
                
            latest = data.iloc[-1]
            
            # Check core criteria
            market_cap = latest.get('Market_Cap', 0)
            volume = latest.get('Volume', 0)
            price = latest.get('Close', 0)
            
            if market_cap < self.boundaries['criteria']['market_cap_min']:
                return False, f"{symbol} market cap below minimum threshold of ${self.boundaries['criteria']['market_cap_min']:,}"
                
            if volume < self.boundaries['criteria']['volume_min']:
                return False, f"{symbol} volume below minimum threshold of {self.boundaries['criteria']['volume_min']:,}"
                
            if price < 5:  # Hard minimum price threshold
                return False, f"{symbol} price below minimum threshold of $5"
                
            return True, ""
            
        except Exception as e:
            return False, f"Error validating {symbol}: {str(e)}"

    def _validate_scan_command(self, params: str) -> tuple[bool, str]:
        """Validate scan command parameters"""
        if any(term in params.lower() for term in ['penny', 'micro', 'small']):
            return False, "Sophie focuses on established growth companies with market caps above $10B"
            
        valid_sectors = set(self.boundaries['specialization']['sectors']['primary'] + 
                        self.boundaries['specialization']['sectors']['secondary'])
                        
        # Check if specified sector is valid
        if params and not any(sector.lower() in params.lower() for sector in valid_sectors):
            return False, f"Sophie specializes in the following sectors: {', '.join(valid_sectors)}"
            
        return True, ""


    def _check_request_validity(self, request: str) -> tuple[bool, str]:
        """
        Enhanced validation of requests against Sophie's boundaries
        
        Args:
            request: The incoming request string
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            request_lower = request.lower()
            parts = request_lower.split()
            cmd_type = parts[0] if parts else ""
            params = ' '.join(parts[1:]) if len(parts) > 1 else ""
            
            # Command type validation
            valid_commands = {'analyze', 'scan', 'build', 'backtest'}
            if cmd_type not in valid_commands:
                return False, f"Invalid command. Valid commands are: {', '.join(valid_commands)}"
            
            # Asset type validation
            excluded_terms = {
                'crypto': ['bitcoin', 'crypto', 'eth', 'btc', 'coin', 'token'],
                'options': ['option', 'call', 'put', 'strike', 'expiry'],
                'futures': ['future', 'contract', 'delivery'],
                'penny_stocks': ['penny', 'otc', 'micro-cap']
            }
            
            for category, terms in excluded_terms.items():
                if any(term in request_lower for term in terms):
                    return False, self._get_exclusion_message(category)
            
            # Command-specific validation
            if cmd_type == 'analyze':
                return self._validate_analyze_command(params)
            elif cmd_type == 'scan':
                return self._validate_scan_command(params)
            elif cmd_type == 'build':
                return self._validate_build_command(params)
            elif cmd_type == 'backtest':
                return self._validate_backtest_command(params)
                
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
            
    def _validate_build_command(self, params: str) -> tuple[bool, str]:
        """Validate build command parameters"""
        invalid_terms = ['day-trading', 'scalping', 'high-frequency', 'hft']
        if any(term in params.lower() for term in invalid_terms):
            return False, "Sophie specializes in growth-focused investment strategies, not short-term trading"
            
        return True, ""

    def _validate_backtest_command(self, params: str) -> tuple[bool, str]:
        """Validate backtest command parameters"""
        if not params:
            return False, "Please provide a symbol and strategy name for backtesting"
            
        parts = params.split()
        if len(parts) < 2:
            return False, "Backtest format: backtest <strategy_name> <symbol>"
            
        return True, ""

    def _get_exclusion_message(self, category: str) -> str:
        """Get appropriate message for excluded asset types"""
        messages = {
            'crypto': "I specialize in traditional growth stocks. For cryptocurrency analysis, please consult our crypto specialist.",
            'options': "My expertise is in equity growth analysis. For options strategies, please consult our options specialist.",
            'futures': "I focus on equity analysis. For futures trading, please consult our futures specialist.",
            'penny_stocks': "I analyze established growth companies with market caps above $10B to ensure liquidity and fundamental strength."
        }
        return messages.get(category, "This type of analysis is outside my specialization in growth stocks.")
        
    def _check_stock_boundaries(self, stock: pd.Series) -> bool:
        """Check if stock meets Sophie's basic boundaries"""
        try:
            # Market Cap Check (minimum $10B)
            if stock.get('Market_Cap', 0) < 10_000_000_000:
                return False

            # Sector Check
            allowed_sectors = ['Technology', 'Healthcare', 'Consumer', 'Communications']
            if stock.get('Sector') not in allowed_sectors:
                return False

            # Basic Technical Checks
            if stock.get('Price', 0) < 5:  # No penny stocks
                return False

            if stock.get('Volume', 0) < 100_000:  # Minimum liquidity
                return False

            return True

        except Exception as e:
            print(f"Warning: Error checking boundaries for {stock.get('Symbol')}: {str(e)}")
            return False

    def _meets_growth_criteria(self, stock: pd.Series, params: Dict) -> bool:
        """Check if stock meets Sophie's growth criteria"""
        try:
            # First check boundaries
            if not self._check_stock_boundaries(stock):
                return False

            # Then check growth criteria
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
        if cmd_type == "expertise":
            return """You are Sophie, a 32-year-old growth-focused portfolio strategist. 
            Return a JSON structure describing your expertise:
            {
                "specialization": {
                    "focus": "Growth investing in established markets",
                    "style": "Moderate-aggressive growth strategy",
                    "core_expertise": [
                        "High-growth stock analysis",
                        "Technical momentum signals",
                        "Market positioning analysis"
                    ]
                },
                "analysis_approach": {
                    "primary_metrics": [
                        "Revenue growth (minimum 15% YoY)",
                        "Earnings trajectory",
                        "Market leadership position"
                    ],
                    "technical_indicators": [
                        "RSI analysis",
                        "Momentum signals",
                        "Volume profiling"
                    ]
                },
                "market_focus": {
                    "market_cap": "Mid to large-cap ($10B+)",
                    "sectors": [
                        "Technology",
                        "Healthcare",
                        "Consumer Growth"
                    ],
                    "geography": "US Markets and major ADRs"
                }
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
    
    def _handle_expertise_query(self, params: Dict) -> None:
        """Handle queries about Sophie's expertise"""
        print("\n👩‍💼 Hi! I'm Sophie, The Growth Accelerator")
        print("=" * 50)

        if not params:
            params = self._get_default_expertise()

        print("\n🎯 My Specialization:")
        print("I'm a growth-focused portfolio strategist specializing in identifying")
        print("high-potential growth opportunities in established markets.")
        
        print("\n📊 Analysis Approach:")
        if 'analysis_approach' in params:
            metrics = params['analysis_approach']
            print("\nPrimary Growth Metrics:")
            for metric in metrics['primary_metrics']:
                print(f"• {metric}")
            
            print("\nTechnical Analysis:")
            for indicator in metrics['technical_indicators']:
                print(f"• {indicator}")

        print("\n🎯 Market Focus:")
        if 'market_focus' in params:
            focus = params['market_focus']
            print(f"• Market Cap: {focus['market_cap']}")
            print("\nKey Sectors:")
            for sector in focus['sectors']:
                print(f"• {sector}")
            print(f"\nGeographic Focus: {focus['geography']}")

        print("\n💡 Note: I focus on quality growth opportunities with:")
        print("• Minimum 15% YoY revenue growth")
        print("• Strong market position")
        print("• Proven business models")
        print("• Solid technical momentum")
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

    def _basic_growth_check(self, stock: pd.Series) -> bool:
        """Basic growth stock filtering"""
        try:
            return (
                stock.get('RSI', 0) > 40 and
                stock.get('MACD', 0) > 0 and
                stock['Volume'] > stock.get('Volume_SMA', 0) and
                stock.get('Revenue_Growth', 0) >= 15 and  # Minimum 15% revenue growth
                stock.get('Price', 0) > stock.get('SMA_200', 0)  # Above 200-day MA
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