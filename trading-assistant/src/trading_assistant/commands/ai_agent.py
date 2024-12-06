# src/trading_assistant/commands/ai_agent.py

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import anthropic
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import yfinance as yf

from commands.scan import ScanCommand
from commands.analyze import AnalyzeCommand
from commands.strategy import StrategyCommand
from commands.backtest import BacktestCommand
from commands.build import BuildCommand
from commands.persona import PersonaCommand

class AnalysisType(Enum):
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    RISK = "risk"

@dataclass
class MarketContext:
    symbol: str
    timeframe: str
    price_data: Dict
    indicators: Dict
    market_cap: float
    sector: str
    news_sentiment: float

class AITradingAgent:
    def __init__(self, market_data):
        # Initialize market data and commands
        self.market_data = market_data
        self.scan_cmd = ScanCommand(market_data)
        self.analyze_cmd = AnalyzeCommand(market_data)
        self.strategy_cmd = StrategyCommand(market_data)
        self.backtest_cmd = BacktestCommand(market_data)
        self.build_cmd = BuildCommand(market_data)
        self.persona_cmd = PersonaCommand()  # Initialize PersonaCommand
        
        # Initialize Claude client
        load_dotenv()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.claude = anthropic.Client(api_key=self.api_key)
        else:
            print("⚠️ ANTHROPIC_API_KEY not found in .env file. AI features will be limited.")
            self.claude = None

    def _get_active_persona(self):
        """Helper method to get active persona"""
        if hasattr(self.persona_cmd, 'persona_manager'):
            return self.persona_cmd.persona_manager.active_persona  # Changed from get_active_persona()
        return None

    def execute(self, arg: str = '') -> None:
        """Execute AI agent workflow"""
        args = arg.split()
        
        if not args:
            self._show_help()
            return
            
        command = args[0].lower()
        
        if command == 'guide':
            self._start_guided_journey()
        elif command == 'analyze':
            self._analyze_opportunity(args[1] if len(args) > 1 else None)
        elif command == 'signal':
            self._generate_signals()
        else:
            self._show_help()

# In ai_agent.py

    def _analyze_opportunity(self, symbol: str = None):
        """Analyze a specific trading opportunity"""
        if not symbol:
            print("⚠️ Please specify a symbol to analyze (e.g., /agent analyze AAPL)")
            return

        # Get active persona using new helper method
        persona = self._get_active_persona()
        if not persona:
            print("\n⚠️ Please set a trading persona first using /persona set <name>")
            return

        print(f"\n{persona.emoji} Analyzing {symbol}...")
        
        try:
            # Get market data
            data = self.market_data.fetch_data(symbol)
            if not data:
                print(f"❌ Unable to fetch data for {symbol}")
                return

            # Create context
            context = MarketContext(
                symbol=symbol,
                timeframe=persona.preferences.preferred_timeframes[0],
                price_data=data,
                indicators=self._calculate_indicators(data),
                market_cap=self._get_market_cap(symbol),
                sector=self._get_sector(symbol),
                news_sentiment=self._get_sentiment(symbol)
            )
            
            # Get AI analysis if Claude is available
            if self.claude:
                # Technical Analysis
                tech_prompt = f"""Analyze {symbol} from a technical perspective:
                - Current price: ${context.price_data.get('close', 0)}
                - Recent price action
                - Key support/resistance levels
                - Technical indicators
                - Volume analysis
                Respond in {persona.name}'s style."""
                
                tech_analysis = self._get_claude_response(tech_prompt, persona.name.lower())
                
                # Trade Setup
                setup_prompt = f"""Based on the analysis of {symbol}, provide:
                1. Trade setup details
                2. Entry points
                3. Stop loss levels
                4. Take profit targets
                5. Position sizing (considering {persona.preferences.max_position_size}% max position)
                6. Key risks to watch
                Respond in {persona.name}'s style."""
                
                trade_setup = self._get_claude_response(setup_prompt, persona.name.lower())
                
                print("\n🔍 Technical Analysis:")
                print("=" * 40)
                print(tech_analysis)
                
                print("\n💡 Trade Setup:")
                print("=" * 40)
                print(trade_setup)
                
            else:
                # Fallback to basic analysis
                print("\n📊 Basic Analysis:")
                print("=" * 40)
                
                # Get basic price data
                close_price = data.get('close', 0)
                change_pct = data.get('change_percent', 0)
                volume = data.get('volume', 'N/A')
                
                print(f"Symbol: {symbol}")
                print(f"Price: ${close_price:.2f} ({change_pct:+.2f}%)")
                print(f"Volume: {volume}")
                
                # Show indicators
                indicators = self._calculate_indicators(data)
                if indicators:
                    print("\n📈 Technical Indicators:")
                    for indicator, value in indicators.items():
                        print(f"{indicator}: {value}")
        
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {str(e)}")

    def _start_guided_journey(self):
        """Start an end-to-end guided trading journey"""
        persona = self.persona_cmd.persona_manager.get_active_persona()
        if not persona:
            print("\n⚠️ Please set a trading persona first using /persona set <name>")
            return

        print(f"\n{persona.emoji} {persona.get_response('greeting')}")
        
        # Use Claude for personalized introduction
        if self.claude:
            intro_prompt = f"You are a {persona.name}. Give a brief, engaging introduction to start a trading session."
            intro = self._get_claude_response(intro_prompt, persona.name.lower())
            print(intro)

        # 1. Market Scanning
        print("\n1️⃣ Scanning markets based on your style...")
        matches = self._scan_based_on_persona(persona)
        
        if not matches:
            if self.claude:
                alt_prompt = f"As a {persona.name}, suggest alternative market scanning approaches when no immediate opportunities are found."
                suggestion = self._get_claude_response(alt_prompt, persona.name.lower())
                print(suggestion)
            return

        # 2. Analysis & Ideas
        print("\n2️⃣ Analyzing top opportunities...")
        for symbol in matches[:3]:
            self._analyze_and_present(symbol, persona)

    def _analyze_and_present(self, symbol: str, persona) -> None:
        """Analyze and present trading opportunity"""
        # Gather market context
        context = self._gather_market_context(symbol, persona)
        
        # Get Claude's analysis if available
        if self.claude:
            analysis_prompt = self._construct_analysis_prompt(context, persona)
            analysis = self._get_claude_response(analysis_prompt, persona.name.lower())
            
            trade_prompt = self._construct_trade_idea_prompt(context, persona)
            trade_idea = self._get_claude_response(trade_prompt, persona.name.lower())
            
            print(f"\n{persona.emoji} Analysis for {symbol}:")
            print(analysis)
            print("\n💡 Trade Idea:")
            print(trade_idea)
        else:
            # Fallback to basic analysis
            self.analyze_cmd.execute(f"analyze {symbol}")

    def _generate_signals(self):
        """Generate real-time trading signals"""
        persona = self.persona_cmd.persona_manager.get_active_persona()
        if not persona:
            print("\n⚠️ Please set a trading persona first")
            return

        print(f"\n{persona.emoji} Generating Trading Signals")
        print("=" * 40)

        try:
            # Get market data for common indices
            indices = ['SPY', 'QQQ', 'IWM']
            market_context = {}
            for index in indices:
                context = self._gather_market_context(index, persona)
                if context:
                    market_context[index] = context

            if self.claude:
                # Generate market overview
                overview_prompt = f"""As a {persona.name}, provide a brief market overview based on:
                SPY: ${market_context.get('SPY', {}).get('price_data', {}).get('close', 0)}
                QQQ: ${market_context.get('QQQ', {}).get('price_data', {}).get('close', 0)}
                IWM: ${market_context.get('IWM', {}).get('price_data', {}).get('close', 0)}
                Include market sentiment and key levels to watch."""
                
                overview = self._get_claude_response(overview_prompt, persona.name.lower())
                print("\n📊 Market Overview:")
                print(overview)

                # Generate trading signals
                signals_prompt = """Based on the market context, provide:
                1. Top 3 bullish setups
                2. Top 3 bearish setups
                3. Key risks to watch
                4. Sector rotation analysis"""
                
                signals = self._get_claude_response(signals_prompt, persona.name.lower())
                print("\n🎯 Trading Signals:")
                print(signals)
            else:
                # Basic signal generation without Claude
                print("\n📈 Basic Market Overview:")
                for index, context in market_context.items():
                    if context and context.price_data:
                        close = context.price_data.get('close', 0)
                        change = context.price_data.get('change_percent', 0)
                        print(f"{index}: ${close:.2f} ({change:+.2f}%)")

        except Exception as e:
            print(f"❌ Error generating signals: {str(e)}")

    def _gather_market_context(self, symbol: str, persona) -> Optional[MarketContext]:
        """Gather all relevant market data for analysis"""
        try:
            # Fetch market data
            data = self.market_data.fetch_data(
                symbol, 
                timeframe=persona.preferences.preferred_timeframes[0]
            )
            
            if not data:
                return None

            # Calculate additional metrics
            indicators = self._calculate_indicators(data)
            market_cap = self._get_market_cap(symbol)
            sector = self._get_sector(symbol)
            sentiment = self._get_sentiment(symbol)
            
            return MarketContext(
                symbol=symbol,
                timeframe=persona.preferences.preferred_timeframes[0],
                price_data=data,
                indicators=indicators,
                market_cap=market_cap,
                sector=sector,
                news_sentiment=sentiment
            )
            
        except Exception as e:
            print(f"❌ Error gathering market context: {str(e)}")
            return None

    def _calculate_indicators(self, data: Dict) -> Dict:
        """Calculate technical indicators"""
        indicators = {}
        try:
            if isinstance(data, dict) and 'close' in data:
                prices = pd.Series(data['close'])
                
                # RSI
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                indicators['RSI'] = 100 - (100 / (1 + rs)).iloc[-1]
                
                # Moving Averages
                indicators['MA20'] = prices.rolling(window=20).mean().iloc[-1]
                indicators['MA50'] = prices.rolling(window=50).mean().iloc[-1]
                
                # Volume Analysis
                if 'volume' in data:
                    volume = pd.Series(data['volume'])
                    indicators['Volume_MA20'] = volume.rolling(window=20).mean().iloc[-1]
                    indicators['Volume_Ratio'] = volume.iloc[-1] / indicators['Volume_MA20']
                
                # MACD
                exp1 = prices.ewm(span=12, adjust=False).mean()
                exp2 = prices.ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                indicators['MACD'] = macd.iloc[-1]
                indicators['MACD_Signal'] = signal.iloc[-1]
                
            return indicators
            
        except Exception as e:
            print(f"Error calculating indicators: {str(e)}")
            return {}

    def _get_market_cap(self, symbol: str) -> float:
        """Get market cap for symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('marketCap', 0)
        except:
            return 0

    def _get_sector(self, symbol: str) -> str:
        """Get sector for symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('sector', 'Unknown')
        except:
            return 'Unknown'

    def _get_sentiment(self, symbol: str) -> float:
        """Get sentiment score for symbol"""
        # This is a placeholder. In a real implementation,
        # you would integrate with news API or sentiment analysis service
        return 0.0  # Neutral sentiment

    def _construct_analysis_prompt(self, context: MarketContext, persona) -> str:
        """Construct analysis prompt based on persona and context"""
        return f"""As a {persona.name}, analyze {context.symbol} with these details:
        - Timeframe: {context.timeframe}
        - Current Price: ${context.price_data.get('close', 0)}
        - Sector: {context.sector}
        - Market Cap: ${context.market_cap}
        
        Focus on:
        1. Key technical levels
        2. Risk assessment
        3. Market sentiment
        4. Trade potential
        
        Respond in {persona.name}'s characteristic style."""

    def _construct_trade_idea_prompt(self, context: MarketContext, persona) -> str:
        """Construct trade idea prompt"""
        return f"""As a {persona.name}, generate a specific trade idea for {context.symbol}.
        Include:
        1. Entry strategy
        2. Stop loss level
        3. Take profit targets
        4. Position sizing
        5. Key risks
        
        Consider the persona's risk tolerance: {persona.traits.risk_tolerance.value}
        Max position size: {persona.preferences.max_position_size}%
        Preferred timeframe: {context.timeframe}"""

    def _get_claude_response(self, prompt: str, persona_style: str) -> str:
        """Get response from Claude"""
        try:
            message = self.claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system=self._get_persona_system_prompt(persona_style),
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content
        except Exception as e:
            print(f"⚠️ AI Error: {str(e)}")
            return None

    def _get_persona_system_prompt(self, persona: str) -> str:
        """Get persona-specific system prompt"""
        prompts = {
            "yolo": """You are a Gen-Z trading expert. Use modern slang and emojis while keeping advice professional.
                      Risk tolerance: High, Style: Aggressive, Timeframe: Short-term""",
            "value": """You are a conservative value investor. Use professional language and emphasize risk management.
                       Risk tolerance: Low, Style: Conservative, Timeframe: Long-term""",
            "swing": """You are a technical analysis expert. Balance technical jargon with clear explanations.
                       Risk tolerance: Medium, Style: Balanced, Timeframe: Medium-term"""
        }
        return prompts.get(persona, prompts["swing"])

    def _show_help(self):
        """Show AI agent help message"""
        print("""
🤖 AI Trading Agent Commands:
---------------------------
/agent guide              : Start guided trading journey
/agent analyze <symbol>   : Get AI analysis for symbol
/agent signal            : Generate trading signals

Examples:
/agent guide             : Start personalized trading journey
/agent analyze AAPL      : Get AI analysis for Apple
/agent signal           : Get current trading signals
        """)

    def _scan_based_on_persona(self, persona) -> List[str]:
        """Scan market based on persona preferences"""
        scan_params = {
            'min_volume': 100000,  # Base minimum volume
            'timeframe': persona.preferences.preferred_timeframes[0]
        }
        
        # Adjust scan parameters based on persona
        if persona.name == "YOLO Trader":
            scan_params.update({
                'min_volatility': 3.0,
                'min_volume': 1000000,
                'sectors': persona.traits.preferred_sectors
            })
        elif persona.name == "Value Investor":
            scan_params.update({
                'min_market_cap': 1000000000,
                'max_pe': 20,
                'min_dividend_yield': 2.0
            })
        
        # Execute scan with persona-specific parameters
        try:
            scan_results = self.scan_cmd.scan_markets(scan_params)
            return scan_results
        except Exception as e:
            print(f"❌ Error during market scan: {str(e)}")
            return []