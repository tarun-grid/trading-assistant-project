from typing import Dict, Any, Optional
import json
from anthropic import Anthropic
from dotenv import load_dotenv
import os

class LLMHandler:
    def __init__(self, market_data):
        load_dotenv()
        self.market_data = market_data
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Sophie's personality traits
        self.sophie_persona = {
            "name": "Sophie",
            "style": "Growth Accelerator",
            "traits": {
                "analysis": "hybrid_growth",
                "risk_profile": "moderate_aggressive",
                "expertise": ["growth_stocks", "momentum", "emerging_sectors"]
            }
        }
            
    def process_command(self, command: str, persona: str = None) -> Dict[str, Any]:
        """Process natural language command through Claude"""
        try:
            # Extract command type and content
            cmd_type = command.split()[0].strip('/')
            content = ' '.join(command.split()[1:])
            
            print(f"\n🤖 Processing: {cmd_type} command")
            print(f"Content: {content}")
            
            # Determine which system prompt to use
            if persona == "sophie":
                system_prompt = self._get_sophie_prompt(cmd_type)
            else:
                system_prompt = self._get_system_prompt(cmd_type)
            
            # Get response from Claude
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.7 if persona == "sophie" else 0,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )
            
            # Debug print to see raw response
            print("\n🔍 Raw LLM Response:")
            print(response.content[0].text)
            
            raw_llm_response = parse_to_json(response.content[0].text)
            
            try:
                # Try to parse as JSON
                result = json.loads(response.content[0].text)
                print("\n📊 Structured Parameters:")
                print(json.dumps(result, indent=2))
                return (raw_llm_response, result)
            except json.JSONDecodeError:
                # If not valid JSON, create structured response
                return (raw_llm_response, {
                    "analysis": {
                        "growth_metrics": {
                            "revenue_growth": "Unknown",
                            "earnings_growth": "Unknown",
                            "margin_trends": "Unknown"
                        },
                        "momentum_signals": {
                            "technical_rating": self._get_technical_rating(content),
                            "price_trend": "Analyzing recent price action",
                            "volume_analysis": "Analyzing volume patterns"
                        },
                        "market_position": {
                            "sector_strength": "Unknown",
                            "competitive_advantage": "Analyzing competitive position",
                            "growth_catalysts": ["Analyzing potential catalysts"]
                        }
                    },
                    "risk_assessment": {
                        "risk_level": "moderate",
                        "key_risks": ["Market volatility", "Sector-specific risks"],
                        "risk_mitigants": ["Diversification", "Position sizing"]
                    },
                    "recommendation": {
                        "action": "analyzing",
                        "target_allocation": "0%",
                        "entry_strategy": "Pending full analysis",
                        "exit_conditions": ["Stop loss hit", "Target reached"]
                    }
                })
                
        except Exception as e:
            print(f"🚫 LLM Processing Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _get_technical_rating(self, symbol: str) -> str:
        """Get technical rating based on market data"""
        try:
            data = self.market_data.fetch_data(symbol)
            if data is not None and not data.empty:
                latest = data.iloc[-1]
                if latest['RSI'] > 70:
                    return "overbought"
                elif latest['RSI'] < 30:
                    return "oversold"
                else:
                    return "neutral"
        except:
            pass
        return "neutral"
            
    def _get_system_prompt(self, cmd_type: str) -> str:
        """Get standard system prompts"""
        if cmd_type == "scan":
            return """You are a trading assistant. Parse the scan command and return only a JSON object with this exact structure:
            {
                "indicators": ["RSI", "Volume"],
                "conditions": {
                    "RSI": {"operator": "<", "value": 40},
                    "volume": {"operator": ">", "value": "1M"}
                },
                "filters": {
                    "price_min": 50,
                    "price_max": 200,
                    "market_cap": "any"
                },
                "timeframe": "1d"
            }
            Do not include any explanation or additional text, just return the JSON object."""
            
        elif cmd_type == "build":
            return """You are a trading assistant that converts natural language commands into structured JSON parameters.
            Parse the build command and return JSON only, matching this structure:
            {
                "strategy_type": "trend/reversal/breakout",
                "target": {
                    "roi": "percentage",
                    "timeframe": "period"
                },
                "indicators": ["list of indicators"],
                "risk_params": {
                    "stop_loss": "percentage",
                    "position_size": "percentage"
                }
            }
            Only respond with the JSON, no other text."""
            
        elif cmd_type == "analyze":
            return """You are a trading assistant that converts natural language commands into structured JSON parameters.
            Parse the analyze command and return JSON only, matching this structure:
            {
                "asset": "symbol",
                "aspects": ["technical", "sentiment", "volume"],
                "timeframe": "period",
                "indicators": ["requested indicators"]
            }
            Only respond with the JSON, no other text."""
            
        return "Convert the command into appropriate JSON parameters. Respond with JSON only, no other text."

    def _get_sophie_prompt(self, cmd_type: str) -> str:
        """Get Sophie-specific system prompts"""
        base_prompt = """You are Sophie, a dynamic 32-year-old portfolio strategist specializing in growth opportunities.
        Your analysis combines growth metrics with technical momentum and you maintain a moderate-aggressive risk profile.
        Your expertise includes identifying emerging sector opportunities and high-growth potential stocks.
        Respond in a confident, professional tone while maintaining your growth-focused perspective."""

        if cmd_type == "analyze":
            return base_prompt + """
            Analyze the given asset and return a JSON with this structure:
            {
                "analysis": {
                    "growth_metrics": {
                        "revenue_growth": "value",
                        "earnings_growth": "value",
                        "margin_trends": "description"
                    },
                    "momentum_signals": {
                        "technical_rating": "strong/neutral/weak",
                        "price_trend": "description",
                        "volume_analysis": "description"
                    },
                    "market_position": {
                        "sector_strength": "rating",
                        "competitive_advantage": "description",
                        "growth_catalysts": ["list"]
                    }
                },
                "risk_assessment": {
                    "risk_level": "low/moderate/high",
                    "key_risks": ["list"],
                    "risk_mitigants": ["list"]
                },
                "recommendation": {
                    "action": "buy/hold/sell",
                    "target_allocation": "percentage",
                    "entry_strategy": "description",
                    "exit_conditions": ["list"]
                }
            }"""

        elif cmd_type == "scan":
            return base_prompt + """
        Return only a JSON matching this exact structure for scan commands:
        {
            "scan_criteria": {
                "growth_metrics": {
                    "min_revenue_growth": 20,
                    "min_earnings_growth": 15,
                    "margin_threshold": 10
                },
                "momentum_filters": {
                    "rsi_range": {"min": 40, "max": 70},
                    "volume_threshold": 1000000,
                    "trend_strength": "positive"
                },
                "sectors": ["Technology", "Healthcare", "Consumer"],
                "price_range": {"min": 10, "max": 500}
            }
        }
        Note: Provide actual numbers, not strings, for numerical values."""

        elif cmd_type == "build":
            return base_prompt + """
            Return only a JSON matching this exact structure for build commands:
        {
            "strategy": {
                "name": "High Growth Momentum Strategy",
                "type": "growth",
                "timeframe": "1d",
                "risk_profile": "moderate-aggressive"
            },
            "entry_rules": {
                "growth_criteria": [
                    "Revenue growth > 20%",
                    "Earnings growth > 15%",
                    "Positive margin trend"
                ],
                "technical_triggers": [
                    "RSI > 50",
                    "Positive MACD crossover",
                    "Volume above 20-day average"
                ]
            },
            "position_sizing": {
                "base_position": 5,
                "max_position": 15,
                "scaling_rules": [
                    "Enter 1/3 at initial signal",
                    "Add 1/3 on momentum confirmation",
                    "Add final 1/3 on trend confirmation"
                ]
            },
            "risk_management": {
                "stop_loss": {
                    "initial": 7,
                    "trailing": 5
                },
                "profit_targets": [8, 12, 15],
                "position_limits": {
                    "single_stock": 15,
                    "sector": 30
                }
            }
        }
        Note: Use actual numbers, not strings, for all numerical values."""

        elif cmd_type == "backtest":
            return base_prompt + """
            Configure backtest parameters and return a JSON with this structure:
            {
                "backtest_config": {
                    "timeframe": "period",
                    "initial_capital": "amount",
                    "position_sizing": {
                        "type": "risk_based/fixed",
                        "risk_per_trade": "percentage",
                        "max_position": "percentage"
                    }
                },
                "strategy_params": {
                    "entry_threshold": "value",
                    "exit_rules": ["list"],
                    "stop_loss": "percentage",
                    "take_profit": ["list of levels"]
                },
                "market_conditions": {
                    "volatility_regime": "low/normal/high",
                    "trend_filter": "value",
                    "volume_filter": "value"
                }
            }"""

        return base_prompt + " Return a JSON structure appropriate for the command context."
    
def parse_to_json(raw_json: str):
    # Remove "```json\n"
    if raw_json.startswith("```json"):
        raw_json = raw_json[7:] 
    
    if raw_json.endswith("```"):
        raw_json = raw_json[:-3]  # Remove trailing backticks

    # Parse the JSON
    try:
        parsed_json = json.loads(raw_json)
        return parsed_json
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)