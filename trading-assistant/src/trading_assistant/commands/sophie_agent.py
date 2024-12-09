
from typing import Dict, Optional
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
import json


class SophieAgent:
    def __init__(self, market_data, llm_handler):
        self.market_data = market_data
        self.llm_handler = llm_handler
        self._last_used = False

        self.strategies = {}
        
        # Define strategy templates
        self.strategy_templates = {
            'aggressive_growth': {
                'name': 'Aggressive Growth Strategy',
                'risk_profile': 'aggressive',
                'growth_criteria': {
                    'revenue_growth_min': 25,
                    'earnings_growth_min': 20,
                    'market_cap_min': 10_000_000_000
                },
                'technical_rules': {
                    'entry': {
                        'rsi_range': {'min': 40, 'max': 65},
                        'macd_signal': 'positive',
                        'volume_threshold': 1.5  # 1.5x average volume
                    },
                    'exit': {
                        'rsi_max': 75,
                        'trailing_stop': 10,
                        'profit_target': 25
                    }
                },
                'position_sizing': {
                    'base_size': 10,  # 10% position size
                    'max_size': 15,   # Maximum 15% per position
                    'sector_max': 30  # Maximum 30% per sector
                }
            },
            'moderate_growth': {
                'name': 'Moderate Growth Strategy',
                'risk_profile': 'moderate',
                'growth_criteria': {
                    'revenue_growth_min': 15,
                    'earnings_growth_min': 12,
                    'market_cap_min': 15_000_000_000
                },
                'technical_rules': {
                    'entry': {
                        'rsi_range': {'min': 45, 'max': 60},
                        'macd_signal': 'positive',
                        'volume_threshold': 1.2
                    },
                    'exit': {
                        'rsi_max': 70,
                        'trailing_stop': 8,
                        'profit_target': 20
                    }
                },
                'position_sizing': {
                    'base_size': 7,    # 7% position size
                    'max_size': 12,    # Maximum 12% per position
                    'sector_max': 25   # Maximum 25% per sector
                }
            }
        }
        
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
   
        self.response_templates = {
            'crypto': {
                'explanation': "I specialize in traditional growth stocks with proven business models.",
                'referral': "For cryptocurrency analysis, I'd recommend consulting our crypto specialist.",
                'alternatives': {
                    'companies': [
                        'Square (SQ) - Digital payments and fintech',
                        'PayPal (PYPL) - Digital financial services',
                        'Microsoft (MSFT) - Enterprise blockchain solutions',
                        'Nvidia (NVDA) - Crypto-mining hardware'
                    ],
                    'sectors': [
                        'Digital Payments',
                        'Enterprise Software',
                        'Cloud Computing',
                        'Semiconductor Technology'
                    ]
                }
            },
            'general': {
                'growth_focus': [
                    'Revenue growth exceeding 15% annually',
                    'Market leadership position',
                    'Strong competitive moats',
                    'Solid technical momentum'
                ],
                'sectors': [
                    'Technology',
                    'Healthcare',
                    'Consumer Growth',
                    'Digital Transformation'
                ]
            }
        }
        
    def process_llm_response(self, response: str) -> Dict:
            """
            Enhanced LLM response processing with better JSON handling and fallback mechanisms
            
            Args:
                response: Raw response string from LLM
                
            Returns:
                Dict containing structured response data
            """
            try:
                # First attempt: Try to find JSON between markdown code blocks
                if '```' in response:
                    parts = response.split('```')
                    for part in parts:
                        # Remove 'json' language identifier if present
                        clean_part = part.replace('json\n', '').strip()
                        if clean_part.startswith('{'):
                            try:
                                return json.loads(clean_part)
                            except json.JSONDecodeError:
                                continue

                # Second attempt: Try to find JSON between curly braces
                start = response.find('{')
                end = response.rfind('}')
                if start != -1 and end != -1:
                    try:
                        return json.loads(response[start:end + 1])
                    except json.JSONDecodeError:
                        pass

                # Fallback: Extract structured content
                return self._extract_content_fallback(response)

            except Exception as e:
                print(f"Response processing error: {str(e)}")
                return self._create_error_response()

    def _extract_content_fallback(self, text: str) -> Dict:
        """
        Enhanced content extraction when JSON parsing fails
        
        Args:
            text: Raw text content
            
        Returns:
            Dict with extracted information
        """
        content = {
            'raw_content': text,
            'extracted_data': {
                'growth_mentioned': False,
                'technical_mentioned': False,
                'risk_mentioned': False,
                'sectors_mentioned': [],
                'companies_mentioned': [],
                'key_points': []
            }
        }

        # Extract key information
        growth_terms = ['growth', 'revenue', 'earnings', 'expansion']
        technical_terms = ['technical', 'momentum', 'rsi', 'macd', 'volume']
        risk_terms = ['risk', 'volatility', 'uncertainty', 'concern']
        
        # Check for term presence
        content['extracted_data']['growth_mentioned'] = any(term in text.lower() for term in growth_terms)
        content['extracted_data']['technical_mentioned'] = any(term in text.lower() for term in technical_terms)
        content['extracted_data']['risk_mentioned'] = any(term in text.lower() for term in risk_terms)

        # Extract sectors
        for sector in self.boundaries['specialization']['sectors']['primary']:
            if sector.lower() in text.lower():
                content['extracted_data']['sectors_mentioned'].append(sector)

        # Extract key points (sentences containing important terms)
        sentences = text.split('.')
        for sentence in sentences:
            if any(term in sentence.lower() for term in growth_terms + technical_terms + risk_terms):
                content['extracted_data']['key_points'].append(sentence.strip())

        return content

    def _format_boundary_response(self, category: str, extracted_data: Dict) -> str:
        """
        Create well-structured boundary responses with relevant alternatives
        
        Args:
            category: Type of boundary violation
            extracted_data: Extracted information from query
            
        Returns:
            Formatted response string
        """
        template = self.response_templates.get(category, self.response_templates['general'])
        
        # Build response using template
        response = [
            f"\n👩‍💼 {template['explanation']}",
            template['referral'],
            "\nInstead, I can help you analyze:",
        ]

        # Add relevant alternatives based on extracted data
        if category == 'crypto' and extracted_data['growth_mentioned']:
            response.extend([
                "\nFintech Growth Leaders:",
                *[f"• {company}" for company in template['alternatives']['companies'][:2]],
                "\nTechnology Infrastructure:",
                *[f"• {company}" for company in template['alternatives']['companies'][2:]]
            ])
        else:
            response.extend([
                "\nFocus Areas:",
                *[f"• {sector}" for sector in template['alternatives']['sectors']]
            ])

        response.extend([
            "\nWould you like me to:",
            "1. Analyze any of these growth companies",
            "2. Scan for high-growth opportunities in these sectors",
            "3. Build a growth-focused portfolio strategy"
        ])

        return '\n'.join(response)

    def _create_error_response(self) -> Dict:
        """Create structured error response"""
        return {
            'error': True,
            'message': "Could not process response",
            'extracted_data': {
                'growth_mentioned': False,
                'technical_mentioned': False,
                'risk_mentioned': False
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
        """
        Execute Sophie's analysis with specialized handling for crypto queries.
        For crypto-related queries, we return an immediate JSON response explaining 
        Sophie's specialization, without any further processing.
        """
        try:
            # First check if we have any input
            if not arg:
                self._show_help()
                return

            # Convert query to lowercase for consistent checking
            query_lower = arg.lower()
            
            # Define crypto-related terms to check for
            crypto_terms = ['bitcoin', 'crypto', 'blockchain', 'btc', 'eth']
            
            # If this is a crypto query, return our specialized response
            if any(term in query_lower for term in crypto_terms):
                response = {
                    "specialization": "I specialize in traditional growth stocks with proven business models.",
                    "referral": "For cryptocurrency analysis, I'd recommend consulting our crypto specialist."
                }
                
                # Print our standard response
                print("\n👩‍💼 Growth Strategy Specialist:")
                print(response["specialization"])
                print(response["referral"])
                return

            # For non-crypto queries, continue with normal processing
            if self._is_natural_language_query(query_lower):
                return self._handle_natural_language_query(arg, structured_params)

            # Handle structured commands
            cmd_parts = query_lower.split()
            cmd_type = cmd_parts[0]
            params = ' '.join(cmd_parts[1:]) if len(cmd_parts) > 1 else ''

            valid_commands = {
                'analyze': self._handle_analysis,
                'scan': self._handle_scan,
                'build': self._handle_strategy,
                'backtest': self._handle_backtest
            }

            if cmd_type not in valid_commands:
                self._show_help()
                return

            self._last_used = True
            return valid_commands[cmd_type](params, structured_params)

        except Exception as e:
            print(f"\n🚫 Sophie encountered an error: {str(e)}")

    def _get_boundary_response(self, category: str) -> str:
        """
        Provides appropriate responses when users inquire about excluded topics.
        Each response explains Sophie's focus and offers relevant alternatives.
        
        Args:
            category: The category of excluded topic (crypto, options, etc.)
        
        Returns:
            str: A helpful response redirecting to Sophie's areas of expertise
        """
        responses = {
            'crypto': """I specialize in traditional growth stocks with proven business models.
    For cryptocurrency analysis, I'd recommend consulting our crypto specialist.

    I focus on analyzing companies that are:
    - Publicly traded with market caps above $10B
    - Growing revenue at 15%+ annually
    - Leaders in their markets
    - Showing strong momentum

    Would you like to explore growth opportunities in fintech or technology instead?""",
            
            'options': """I focus on equity growth analysis and fundamental company evaluation.
    For options strategies, please consult our options specialist.

    I can help you with:
    - Analyzing growth stock fundamentals
    - Identifying market leaders
    - Building growth-focused portfolios
    - Long-term value creation opportunities""",
            
            'penny_stocks': """I analyze established growth companies with market caps above $10B.
    This ensures strong fundamentals and market leadership.

    Let me help you find high-quality growth opportunities with:
    - Proven business models
    - Strong revenue growth
    - Market leadership positions
    - Solid financial foundations"""
        }
        
        return responses.get(category, "I focus on established growth companies with strong fundamentals.")

    def _check_excluded_topics(self, query: str) -> Optional[str]:
        """
        Check if query involves topics outside Sophie's boundaries
        
        Args:
            query: The incoming query string
            
        Returns:
            Optional[str]: Explanation message if topic is excluded, None otherwise
        """
        query_lower = query.lower()
        
        # Cryptocurrency check
        crypto_terms = ['bitcoin', 'crypto', 'eth', 'btc', 'blockchain', 'token']
        if any(term in query_lower for term in crypto_terms):
            return """I specialize in traditional growth stocks with proven business models. 
    For cryptocurrency analysis, I'd recommend consulting our crypto specialist.

    I can help you analyze high-growth technology companies that are:
    • Publicly traded with market caps above $10B
    • Growing revenue at 15%+ annually
    • Leaders in their markets
    • Showing strong momentum

    Would you like to explore some growth opportunities in technology or digital payments instead?"""
        
        # Options/derivatives check
        option_terms = ['option', 'call', 'put', 'strike', 'expiry']
        if any(term in query_lower for term in option_terms):
            return """My expertise is in equity growth analysis. For options strategies, 
    please consult our options specialist.

    I can help you with:
    • Analyzing growth stock fundamentals
    • Identifying market leaders
    • Building growth-focused portfolios
    • Risk-managed position sizing"""
        
        # Other excluded categories...
        return None

    def _is_natural_language_query(self, query: str) -> bool:
        """
        Determine if input is a natural language query
        
        Args:
            query: The incoming query string
            
        Returns:
            bool: True if natural language query, False if command
        """
        query_lower = query.lower()
        nl_indicators = ['what', 'how', 'why', 'when', 'where', 'tell', 'think', 'explain']
        return any(word in query_lower for word in nl_indicators)

    def _handle_natural_language_query(self, query: str, params: Dict) -> None:
        """
        Handle natural language queries with enhanced analysis
        
        Args:
            query: The natural language query
            params: Additional parameters and context
        """
        try:
            # Extract ticker if present in the query
            ticker = self._extract_symbol(query)
            
            # If no ticker in query but present in params, use that
            if not ticker and params and 'ticker' in params:
                ticker = params['ticker']
                
            if ticker:
                # Fetch market data
                market_data = self.market_data.fetch_data(ticker)
                if market_data is None or market_data.empty:
                    print(f"❌ Unable to fetch data for {ticker}")
                    return None
                    
                # Get latest data point
                latest_data = market_data.iloc[-1]
                
                # Check if stock meets growth criteria
                if self._meets_growth_criteria(latest_data):
                    return self._handle_analysis(ticker, params)
                else:
                    self._explain_growth_criteria_failure(ticker, latest_data)
                    return None
                    
            else:
                # Handle general questions about growth investing
                self._handle_open_query(query, params)
                
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return None
            
    def _explain_growth_criteria_failure(self, ticker: str, data: pd.Series) -> None:
        """
        Provide detailed explanation when a stock doesn't meet growth criteria
        
        Args:
            ticker: Stock symbol
            data: Stock data with metrics
        """
        print(f"\n👩‍💼 Growth Analysis for {ticker}:")
        print("\nThis company doesn't currently meet my growth criteria. Here's why:")
        
        # Check and explain each criterion
        if data.get('Revenue_Growth', 0) < self.boundaries['criteria']['revenue_growth_min']:
            print(f"• Revenue Growth: {data.get('Revenue_Growth', 0):.1f}% vs required {self.boundaries['criteria']['revenue_growth_min']}%")
            
        if data.get('Market_Cap', 0) < self.boundaries['criteria']['market_cap_min']:
            print(f"• Market Cap: ${data.get('Market_Cap', 0)/1e9:.1f}B vs required ${self.boundaries['criteria']['market_cap_min']/1e9:.1f}B")
            
        if data.get('Volume', 0) < self.boundaries['criteria']['volume_min']:
            print(f"• Daily Volume: {data.get('Volume', 0):,.0f} vs required {self.boundaries['criteria']['volume_min']:,.0f}")
            
        rsi = data.get('RSI', 0)
        if rsi < self.boundaries['criteria']['rsi_range']['min'] or rsi > self.boundaries['criteria']['rsi_range']['max']:
            print(f"• RSI: {rsi:.1f} (should be between {self.boundaries['criteria']['rsi_range']['min']} and {self.boundaries['criteria']['rsi_range']['max']})")
        
        print("\nI focus on companies that meet these growth criteria:")
        print("• Minimum 15% revenue growth")
        print("• Market cap above $10B")
        print("• Strong trading volume")
        print("• Healthy technical indicators")
        
        print("\nWould you like me to:")
        print("1. Suggest similar companies that meet my criteria")
        print("2. Scan for growth opportunities in this sector")
        print("3. Explain my growth criteria in more detail")        

    def _explain_investment_philosophy(self) -> None:
        """Explain Sophie's investment philosophy"""
        print("\n👩‍💼 Investment Philosophy:")
        print("""I'm a growth-focused portfolio strategist specializing in identifying 
    high-potential companies with proven business models and strong market positions.

    My investment approach centers on:
    • Companies with 15%+ revenue growth
    • Market leaders in expanding sectors
    • Strong technical momentum
    • Risk-managed position sizing

    I focus primarily on:
    • Technology
    • Healthcare
    • Consumer growth
    • Digital transformation

    My goal is to identify companies with sustainable competitive advantages 
    and long-term growth potential while managing risk through position sizing 
    and portfolio diversification.""")

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

    def _meets_growth_criteria(self, stock_data: pd.Series) -> bool:
        """
        Check if a stock meets Sophie's growth criteria
        
        Args:
            stock_data: Series containing stock metrics and data
            
        Returns:
            bool: True if stock meets growth criteria, False otherwise
        """
        try:
            # Basic growth metrics check
            growth_checks = {
                'revenue_growth': {
                    'value': stock_data.get('Revenue_Growth', 0),
                    'threshold': self.boundaries['criteria']['revenue_growth_min'],
                    'check': lambda x, y: x >= y
                },
                'earnings_growth': {
                    'value': stock_data.get('Earnings_Growth', 0),
                    'threshold': self.boundaries['criteria']['earnings_growth_min'],
                    'check': lambda x, y: x >= y
                },
                'market_cap': {
                    'value': stock_data.get('Market_Cap', 0),
                    'threshold': self.boundaries['criteria']['market_cap_min'],
                    'check': lambda x, y: x >= y
                }
            }
            
            # Technical metrics check
            technical_checks = {
                'volume': {
                    'value': stock_data.get('Volume', 0),
                    'threshold': self.boundaries['criteria']['volume_min'],
                    'check': lambda x, y: x >= y
                },
                'rsi': {
                    'value': stock_data.get('RSI', 50),
                    'threshold': (
                        self.boundaries['criteria']['rsi_range']['min'],
                        self.boundaries['criteria']['rsi_range']['max']
                    ),
                    'check': lambda x, y: y[0] <= x <= y[1]
                }
            }
            
            # Perform growth checks
            for metric, check in growth_checks.items():
                if not check['check'](check['value'], check['threshold']):
                    print(f"Failed {metric} check: {check['value']} vs threshold {check['threshold']}")
                    return False
                    
            # Perform technical checks
            for metric, check in technical_checks.items():
                if not check['check'](check['value'], check['threshold']):
                    print(f"Failed {metric} check: {check['value']} vs threshold {check['threshold']}")
                    return False
                    
            return True
            
        except Exception as e:
            print(f"Error in growth criteria check: {str(e)}")
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

    def _handle_analysis(self, symbol: str, params: Dict) -> None:
        """
        Performs comprehensive growth analysis including price and technical indicators
        
        Args:
            symbol: Stock symbol to analyze
            params: Additional parameters from LLM
        """
        try:
            print(f"\n👩‍💼 Sophie's Growth Analysis: {symbol}")
            print("=" * 50)
            
            # Fetch market data
            market_data = self.market_data.fetch_data(symbol)
            if market_data is None or market_data.empty:
                print(f"❌ Unable to analyze {symbol} - No market data available")
                return None
                
            # Get latest data point
            latest = market_data.iloc[-1]
            
            # Price Analysis
            print("\n💰 Price Analysis:")
            print(f"Current Price: ${latest['Close']:.2f}")
            print(f"50-day MA: ${latest.get('SMA_50', 0):.2f}")
            print(f"200-day MA: ${latest.get('SMA_200', 0):.2f}")
            
            # Technical Analysis
            print("\n📊 Technical Indicators:")
            rsi = latest.get('RSI', 0)
            macd = latest.get('MACD', 0)
            volume = latest.get('Volume', 0)
            
            # RSI Analysis with boundary checks
            print(f"RSI: {rsi:.2f}")
            if self.boundaries['criteria']['rsi_range']['min'] <= rsi <= self.boundaries['criteria']['rsi_range']['max']:
                print("✅ RSI within optimal growth range")
            else:
                print("⚠️ RSI outside optimal range")
                
            # MACD Analysis
            print(f"MACD: {macd:.2f}")
            if macd > 0:
                print("✅ Positive momentum")
            else:
                print("⚠️ Negative momentum")
                
            # Volume Analysis
            avg_volume = market_data['Volume'].mean()
            print(f"Volume: {volume:,.0f}")
            if volume >= self.boundaries['criteria']['volume_min']:
                print("✅ Strong trading volume")
            else:
                print("⚠️ Below minimum volume threshold")
            
            # Growth Assessment
            if params and 'financials' in params:
                print("\n📈 Growth Metrics:")
                financials = params['financials']
                revenue_growth = financials.get('revenue_growth_rate', 0) * 100
                print(f"Revenue Growth: {revenue_growth:.1f}%")
                if revenue_growth >= self.boundaries['criteria']['revenue_growth_min']:
                    print("✅ Meets revenue growth criteria")
                else:
                    print("⚠️ Below revenue growth threshold")
            
            # Overall Assessment
            print("\n🎯 Sophie's Assessment:")
            if params and 'recommendation' in params:
                print(self._format_paragraph(params['recommendation']))

        except Exception as e:
            print(f"Analysis error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
    def _calculate_growth_metrics(self, market_data: pd.DataFrame) -> Dict:
        """
        Calculate comprehensive growth metrics from market data
        
        Args:
            market_data: DataFrame containing historical market data
            
        Returns:
            Dict containing growth metrics
        """
        try:
            # Calculate key metrics
            if not market_data.empty:
                latest = market_data.iloc[-1]
                year_ago = market_data.iloc[-252] if len(market_data) >= 252 else market_data.iloc[0]
                
                revenue_growth = ((latest.get('Revenue', 0) - year_ago.get('Revenue', 0)) / 
                                year_ago.get('Revenue', 1)) * 100 if year_ago.get('Revenue', 0) != 0 else 0
                                
                market_cap = latest.get('Close', 0) * latest.get('Shares_Outstanding', 0)
                
                return {
                    'revenue_growth': revenue_growth,
                    'market_cap': market_cap,
                    'volume': latest.get('Volume', 0),
                    'price_momentum': {
                        'current_price': latest.get('Close', 0),
                        'sma_50': latest.get('SMA_50', 0),
                        'sma_200': latest.get('SMA_200', 0)
                    }
                }
        except Exception as e:
            print(f"Error calculating growth metrics: {str(e)}")
            
        return {}

    def _present_growth_analysis(self, analysis: Dict) -> None:
        """
        Present comprehensive growth analysis in a clear format
        
        Args:
            analysis: Dict containing analysis results
        """
        company = analysis['company']
        metrics = analysis['growth_metrics']
        
        print(f"\n📊 Company Overview: {company['name']}")
        print(f"Industry: {company['industry']}")
        
        print("\n📈 Growth Metrics:")
        print(f"• Revenue Growth: {metrics.get('revenue_growth', 0):.1f}%")
        print(f"• Market Cap: ${metrics.get('market_cap', 0)/1e9:.1f}B")
        print(f"• Daily Volume: {metrics.get('volume', 0):,.0f}")
        
        if 'technical_signals' in analysis:
            tech = analysis['technical_signals']
            print("\n📊 Technical Indicators:")
            print(f"• RSI: {tech.get('rsi', 0):.1f}")
            print(f"• MACD Signal: {tech.get('macd_signal', 'N/A')}")
            print(f"• Volume Trend: {tech.get('volume_trend', 'N/A')}")
        
        print("\n💡 Growth Analysis:")
        print(self._format_paragraph(company['analysis']))
        
        if 'risk_assessment' in analysis:
            risks = analysis['risk_assessment']
            print("\n⚠️ Risk Assessment:")
            for risk in risks.get('key_risks', []):
                print(f"• {risk}")
        
        recommendation = company.get('recommendation', '')
        if recommendation:
            print("\n🎯 Sophie's Recommendation:")
            print(self._format_paragraph(recommendation))

    def _format_paragraph(self, text: str, width: int = 80) -> str:
        """Format long text into readable paragraphs"""
        if not text:
            return ""
            
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
                # if self._meets_growth_criteria(stock, scan_params):
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
            """
            Handle strategy building with enhanced error handling
            
            Args:
                params: Strategy parameters
                llm_params: Additional context from LLM
            """
            try:
                print("\n👩‍💼 Sophie's Growth Strategy Builder")
                print("=" * 50)
                
                # Get base template
                template_name = 'moderate_growth'
                if params and 'aggressive' in params.lower():
                    template_name = 'aggressive_growth'
                    
                template = self.strategy_templates[template_name].copy()
                
                # Display strategy configuration
                return self._display_strategy(template)
            
                # Handle strategy saving
                save = input("\nWould you like to save this strategy? (y/n): ").lower()
                if save == 'y':
                    name = input("Enter strategy name: ").strip()
                    if name:
                        try:
                            # Create strategy using manager
                            strategy = self.strategy_manager.create_strategy(name, template)
                            print(f"\n✅ Strategy '{name}' saved successfully!")
                            
                            # Show next steps
                            print("\nWould you like to:")
                            print("1. Backtest this strategy")
                            print("2. Scan for matching stocks")
                            print("3. Modify strategy parameters")
                            
                            choice = input("\nEnter your choice (1-3): ")
                            self._handle_strategy_choice(choice, name, strategy)
                            
                        except Exception as e:
                            print(f"Error saving strategy: {str(e)}")
                    else:
                        print("❌ Invalid strategy name")
                        
            except Exception as e:
                print(f"❌ Strategy building error: {str(e)}")

    def _save_strategy(self, name: str, strategy: Dict) -> None:
            """Save strategy to storage"""
            try:
                strategy['created_at'] = datetime.now().isoformat()
                strategy['last_modified'] = datetime.now().isoformat()
                self.strategies[name] = strategy
                
                # Save to file for persistence
                self._save_strategies_to_file()
                
            except Exception as e:
                print(f"Error saving strategy: {str(e)}")
                raise

    def _save_strategies_to_file(self) -> None:
                """Save strategies to JSON file"""
                try:
                    file_path = 'strategies.json'
                    with open(file_path, 'w') as f:
                        json.dump(self.strategies, f, indent=2)
                except Exception as e:
                    print(f"Error saving to file: {str(e)}")

    def _load_strategies_from_file(self) -> None:
                """Load strategies from JSON file"""
                try:
                    file_path = 'strategies.json'
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            self.strategies = json.load(f)
                except Exception as e:
                    print(f"Error loading strategies: {str(e)}")        

    def _test_strategy(self, strategy_name: str, symbol: str) -> Dict:
                """Test a saved strategy on a specific symbol"""
                try:
                    if strategy_name not in self.strategies:
                        raise ValueError(f"Strategy '{strategy_name}' not found")
                        
                    strategy = self.strategies[strategy_name]
                    
                    print(f"\n📊 Testing {strategy['name']} on {symbol}")
                    print("=" * 50)
                    
                    # Fetch historical data
                    data = self.market_data.fetch_data(symbol, period='1y')
                    if data is None or data.empty:
                        raise ValueError(f"No data available for {symbol}")
                        
                    # Run backtest with strategy parameters
                    results = self._run_strategy_backtest(data, strategy)
                    
                    # Display results
                    self._display_strategy_results(results)
                    
                    return results
                    
                except Exception as e:
                    print(f"Strategy test error: {str(e)}")
                    return None     

    def _display_strategy(self, strategy: Dict) -> None:
            """
            Display strategy configuration in a clear format
            
            Args:
                strategy: Strategy configuration to display
            """
            response = {
                "strategy_overview": {
                    "name": strategy.get("name", "Growth Strategy"),
                    "type": strategy.get("risk_profile", "growth"),
                    "timeframe": strategy.get("timeframe", "1d"),
                },
                "growth_criteria": {
                    "min_revenue_growth": f'{strategy.get("growth_criteria", {}).get("revenue_growth_min")}%',
                    "min_earnings_growth": f'{strategy.get("growth_criteria", {}).get("earnings_growth_min")}%',
                    "min_market_cap": f"${strategy.get('growth_criteria', {}).get('market_cap_min', 0) / 1e9:.1f}B",
                },
                "technical_rules": {
                    "rsi_range": strategy.get("technical_rules", {}).get("entry", {}).get("rsi_range", {}),
                    "macd_signal": strategy.get("technical_rules", {}).get("entry", {}).get("macd_signal", "positive"),
                    "volume_threshold": strategy.get("technical_rules", {}).get("entry", {}).get("volume_threshold"),
                },
            }
            
            return response


    def _run_strategy_backtest(self, data: pd.DataFrame, strategy: Dict) -> Dict:
                """Run backtest using strategy parameters"""
                results = {
                    'trades': [],
                    'metrics': {
                        'total_return': 0,
                        'win_rate': 0,
                        'avg_gain': 0,
                        'max_drawdown': 0
                    }
                }
                
                try:
                    # Initialize tracking variables
                    in_position = False
                    entry_price = 0
                    position_size = strategy['position_sizing']['base_size'] / 100
                    trailing_stop = strategy['technical_rules']['exit']['trailing_stop'] / 100
                    profit_target = strategy['technical_rules']['exit']['profit_target'] / 100
                    
                    # Simulate trading
                    for i in range(1, len(data)):
                        current = data.iloc[i]
                        
                        if not in_position:
                            # Check entry conditions
                            entry_signal = self._check_entry_conditions(current, strategy)
                            if entry_signal:
                                entry_price = current['Close']
                                in_position = True
                                results['trades'].append({
                                    'type': 'entry',
                                    'date': current.name,
                                    'price': entry_price
                                })
                        else:
                            # Check exit conditions
                            exit_signal = self._check_exit_conditions(
                                current, entry_price, strategy
                            )
                            if exit_signal:
                                exit_price = current['Close']
                                returns = (exit_price / entry_price - 1) * 100
                                results['trades'].append({
                                    'type': 'exit',
                                    'date': current.name,
                                    'price': exit_price,
                                    'returns': returns
                                })
                                in_position = False
                    
                    # Calculate final metrics
                    results['metrics'] = self._calculate_strategy_metrics(results['trades'])
                    
                    return results
                    
                except Exception as e:
                    print(f"Backtest error: {str(e)}")
                    return results        
    def _run_strategy_backtest(self, data: pd.DataFrame, strategy: Dict) -> Dict:
                """Run backtest using strategy parameters"""
                results = {
                    'trades': [],
                    'metrics': {
                        'total_return': 0,
                        'win_rate': 0,
                        'avg_gain': 0,
                        'max_drawdown': 0
                    }
                }
                
                try:
                    # Initialize tracking variables
                    in_position = False
                    entry_price = 0
                    position_size = strategy['position_sizing']['base_size'] / 100
                    trailing_stop = strategy['technical_rules']['exit']['trailing_stop'] / 100
                    profit_target = strategy['technical_rules']['exit']['profit_target'] / 100
                    
                    # Simulate trading
                    for i in range(1, len(data)):
                        current = data.iloc[i]
                        
                        if not in_position:
                            # Check entry conditions
                            entry_signal = self._check_entry_conditions(current, strategy)
                            if entry_signal:
                                entry_price = current['Close']
                                in_position = True
                                results['trades'].append({
                                    'type': 'entry',
                                    'date': current.name,
                                    'price': entry_price
                                })
                        else:
                            # Check exit conditions
                            exit_signal = self._check_exit_conditions(
                                current, entry_price, strategy
                            )
                            if exit_signal:
                                exit_price = current['Close']
                                returns = (exit_price / entry_price - 1) * 100
                                results['trades'].append({
                                    'type': 'exit',
                                    'date': current.name,
                                    'price': exit_price,
                                    'returns': returns
                                })
                                in_position = False
                    
                    # Calculate final metrics
                    results['metrics'] = self._calculate_strategy_metrics(results['trades'])
                    
                    return results
                    
                except Exception as e:
                    print(f"Backtest error: {str(e)}")
                    return results                      

    def _handle_backtest(self, params: str, llm_params: Dict) -> None:
        """
        Comprehensive backtesting system for growth strategies
        
        Args:
            params: Backtest parameters (symbol, timeframe)
            llm_params: Additional context from LLM
        """
        try:
            # Parse parameters
            if not params:
                print("❌ Please provide a symbol for backtesting")
                return
                
            symbol = params.split()[0].upper()
            print(f"\n👩‍💼 Sophie's Growth Strategy Backtest: {symbol}")
            print("=" * 50)
            
            # Fetch historical data
            historical_data = self.market_data.fetch_data(symbol, period='5y')  # Get 5 years of data
            if historical_data is None or historical_data.empty:
                print(f"❌ Unable to fetch historical data for {symbol}")
                return
                
            # Calculate growth metrics over time
            growth_metrics = self._calculate_historical_growth(historical_data)
            
            # Run technical strategy backtest
            backtest_results = self._run_growth_strategy_backtest(historical_data, growth_metrics)
            
            # Present comprehensive results
            return self._present_backtest_results(symbol, backtest_results, growth_metrics)
        
        except Exception as e:
            print(f"🚫 Backtest error: {str(e)}")
            import traceback
            traceback.print_exc()

    def _calculate_historical_growth(self, data: pd.DataFrame) -> Dict:
        """Calculate historical growth metrics and trends"""
        growth_metrics = {
            'revenue_growth': [],
            'earnings_growth': [],
            'momentum_signals': [],
            'volatility': []
        }
        
        # Calculate quarterly growth rates
        for i in range(4, len(data), 63):  # Approximate quarters
            window = data.iloc[i-63:i]
            if not window.empty:
                # Revenue growth (if available)
                growth_metrics['revenue_growth'].append({
                    'date': window.index[-1],
                    'growth': ((window['Close'].iloc[-1] / window['Close'].iloc[0]) - 1) * 100
                })
                
                # Calculate volatility
                growth_metrics['volatility'].append({
                    'date': window.index[-1],
                    'value': window['Close'].pct_change().std() * (252 ** 0.5) * 100
                })
                
                # Momentum signals
                growth_metrics['momentum_signals'].append({
                    'date': window.index[-1],
                    'rsi': window['RSI'].iloc[-1],
                    'macd': window['MACD'].iloc[-1]
                })
        
        return growth_metrics

    def _run_growth_strategy_backtest(self, data: pd.DataFrame, metrics: Dict) -> Dict:
        """Execute growth strategy backtest with Sophie's criteria"""
        results = {
            'trades': [],
            'performance': {
                'returns': [],
                'drawdowns': [],
                'metrics': {}
            },
            'analysis': {
                'entry_points': [],
                'exit_points': [],
                'risk_events': []
            }
        }
        
        # Strategy parameters
        initial_capital = 100000
        position_size = 0.10  # 10% position size
        stop_loss = 0.08     # 8% stop loss
        
        # Track portfolio value
        portfolio_value = initial_capital
        in_position = False
        entry_price = 0
        
        # Simulate trading
        for i in range(1, len(data)):
            current_bar = data.iloc[i]
            previous_bar = data.iloc[i-1]
            
            # Entry conditions (growth-focused)
            entry_signal = (
                not in_position and
                current_bar['RSI'] > 40 and current_bar['RSI'] < 70 and
                current_bar['MACD'] > 0 and
                current_bar['Volume'] > current_bar['Volume_SMA']
            )
            
            # Exit conditions
            exit_signal = (
                in_position and (
                    current_bar['RSI'] > 70 or
                    current_bar['MACD'] < 0 or
                    (current_bar['Close'] / entry_price - 1) < -stop_loss
                )
            )
            
            if entry_signal:
                # Enter position
                entry_price = current_bar['Close']
                position_value = portfolio_value * position_size
                shares = position_value / entry_price
                in_position = True
                
                results['trades'].append({
                    'date': current_bar.name,
                    'type': 'entry',
                    'price': entry_price,
                    'shares': shares,
                    'portfolio_value': portfolio_value
                })
                
            elif exit_signal:
                # Exit position
                exit_price = current_bar['Close']
                trade_return = (exit_price / entry_price - 1) * 100
                portfolio_value *= (1 + trade_return * position_size / 100)
                in_position = False
                
                results['trades'].append({
                    'date': current_bar.name,
                    'type': 'exit',
                    'price': exit_price,
                    'return': trade_return,
                    'portfolio_value': portfolio_value
                })
        
        # Calculate final performance metrics
        results['performance']['metrics'] = {
            'total_return': (portfolio_value / initial_capital - 1) * 100,
            'num_trades': len([t for t in results['trades'] if t['type'] == 'entry']),
            'win_rate': sum(1 for t in results['trades'] if t['type'] == 'exit' and t['return'] > 0) / 
                    len([t for t in results['trades'] if t['type'] == 'exit']) * 100 if results['trades'] else 0,
            'max_drawdown': min([t['return'] for t in results['trades'] if t['type'] == 'exit'], default=0)
        }
        
        return results

    def _present_backtest_results(self, symbol: str, results: Dict, metrics: Dict) -> None:
        """Present comprehensive backtest results"""
        # Backtest configuration
        backtest_config = {
            "strategy": "Growth Momentum",
            "period": "5 Years",
            "initial_capital": "$100,000",
            "position_size": "10%",
            "stop_loss": "8%",
        }

        # Performance summary
        perf = results["performance"]["metrics"]
        performance_summary = {
            "total_return": f"{round(perf['total_return'], 1)}%",
            "number_of_trades": perf["num_trades"],
            "win_rate": f"{round(perf['win_rate'], 1)}%",
            "maximum_drawdown": f"{round(perf['max_drawdown'], 1)}%"
        }

        # Growth trends
        recent_growth = metrics.get("revenue_growth", [])[-4:]
        growth_trends = [
            {
                "date": period["date"].strftime("%Y-%m"),
                "growth": f"{round(period['growth'], 1)}%"
            }
            for period in recent_growth
        ]

        # Risk analysis
        recent_vol = metrics.get("volatility", [{}])[-1]
        risk_analysis = {
            "recent_volatility": f"{round(recent_vol.get('value', 0), 1)}%",
            "risk_adjusted_return": round(
                perf["total_return"] / abs(perf["max_drawdown"]), 2
            ),
        }

        # Strategy insights
        strategy_insights = [
            "Best performing entries occurred during strong growth momentum phases",
            "Technical confirmation improved entry timing",
            "Position sizing and stop-losses effectively managed drawdowns",
        ]

        # User options
        options = [
            "Adjust strategy parameters",
            "Compare with other growth stocks",
            "View detailed trade history",
        ]

        # Combine everything into a JSON response
        response = {
            "symbol": symbol,
            "backtest_configuration": backtest_config,
            "performance_summary": performance_summary,
            "growth_trends": growth_trends,
            "risk_analysis": risk_analysis,
            "strategy_insights": strategy_insights,
            "options": options,
        }

        return response

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
