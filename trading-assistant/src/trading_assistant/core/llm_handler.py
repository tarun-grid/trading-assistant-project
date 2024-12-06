from typing import Dict, Any, Optional, Tuple
import json
from anthropic import Anthropic
from dotenv import load_dotenv
import os

class LLMHandler:
    """
    Handles all interactions with the Language Model (Claude), specifically for trading analysis.
    Manages different personas (including Sophie) and maintains consistent response formats.
    """
    def __init__(self, market_data):
        """Initialize the LLM handler with market data and Sophie's personality."""
        load_dotenv()
        self.market_data = market_data
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Define Sophie's complete persona and boundaries
        self.sophie_persona = {
            "name": "Sophie",
            "style": "Growth Accelerator",
            "traits": {
                "analysis": "hybrid_growth",
                "risk_profile": "moderate_aggressive",
                "expertise": ["growth_stocks", "momentum", "emerging_sectors"]
            },
            "boundaries": {
                "focus": {
                    "min_market_cap": 10_000_000_000,  # $10B minimum
                    "min_revenue_growth": 15,  # 15% minimum
                    "sectors": ["Technology", "Healthcare", "Consumer"]
                },
                "excludes": {
                    "assets": ["crypto", "forex", "commodities"],
                    "instruments": ["options", "futures", "derivatives"],
                    "categories": ["penny_stocks", "micro_caps", "pre_revenue"]
                }
            }
        }

    def process_command(self, command: str, persona: str = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process commands through Claude and return structured responses.
        Returns tuple of (raw_response, structured_parameters).
        """
        try:
            # Parse command components
            cmd_parts = command.split()
            cmd_type = cmd_parts[0].strip('/')
            content = ' '.join(cmd_parts[1:])
            
            print(f"\n🤖 Processing: {cmd_type} command")
            print(f"Content: {content}")

            # Get appropriate system prompt based on persona
            system_prompt = self._get_sophie_prompt(cmd_type) if persona == "sophie" else self._get_system_prompt(cmd_type)
            
            # Get LLM response with error handling
            try:
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    temperature=0.7 if persona == "sophie" else 0,
                    system=system_prompt,
                    messages=[{"role": "user", "content": content}]
                )
                
                # Process and structure the response
                raw_text = response.content[0].text
                print("\n🔍 Raw LLM Response:")
                print(raw_text)
                
                # Parse response with enhanced error handling
                raw_response = self._parse_llm_response(raw_text)
                structured_params = self._structure_response(raw_response, cmd_type)
                
                print("\n📊 Structured Parameters:")
                print(json.dumps(structured_params, indent=2))
                
                return raw_response, structured_params
                
            except Exception as e:
                print(f"LLM Response Error: {str(e)}")
                return self._get_fallback_response(cmd_type)
                
        except Exception as e:
            print(f"🚫 Command Processing Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response text into structured format, handling various response formats.
        """
        try:
            # Handle markdown-wrapped JSON
            if response_text.startswith('```'):
                parts = response_text.split('```')
                for part in parts:
                    # Find the JSON content
                    if part.strip().startswith('{'):
                        response_text = part.strip()
                        break
            
            # Clean the response text
            response_text = response_text.replace('json\n', '').strip()
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {str(e)}")
                return self._extract_content_fallback(response_text)
                
        except Exception as e:
            print(f"Response Parse Error: {str(e)}")
            return {}

    def _extract_content_fallback(self, text: str) -> Dict[str, Any]:
        """
        Extract meaningful content when JSON parsing fails.
        Creates a structured format from unstructured text.
        """
        result = {
            "raw_content": text,
            "extracted_data": {}
        }
        
        try:
            # Extract key patterns
            patterns = {
                "growth_mentioned": ["growth", "revenue", "earnings"],
                "technical_mentioned": ["rsi", "macd", "momentum"],
                "risk_mentioned": ["risk", "volatility", "downside"]
            }
            
            for key, terms in patterns.items():
                result["extracted_data"][key] = any(term in text.lower() for term in terms)
                
        except Exception as e:
            print(f"Content Extraction Error: {str(e)}")
            
        return result

    def _structure_response(self, raw_response: Dict[str, Any], cmd_type: str) -> Dict[str, Any]:
        """
        Structure raw response into consistent format based on command type.
        Ensures response maintains expected structure regardless of LLM output variations.
        """
        try:
            if not raw_response:
                return self._get_fallback_response(cmd_type)[1]
                
            structured = {}
            
            # Structure based on command type
            if cmd_type == "analyze":
                structured = {
                    "analysis": raw_response.get("analysis", {}),
                    "risk_assessment": raw_response.get("risk_assessment", {}),
                    "recommendation": raw_response.get("recommendation", {})
                }
            elif cmd_type == "scan":
                structured = {
                    "scan_criteria": raw_response.get("scan_criteria", {}),
                    "filters": raw_response.get("filters", {})
                }
            elif cmd_type == "build":
                structured = {
                    "strategy": raw_response.get("strategy", {}),
                    "rules": raw_response.get("entry_rules", {})
                }
            else:
                structured = raw_response
                
            return structured
            
        except Exception as e:
            print(f"Response Structuring Error: {str(e)}")
            return self._get_fallback_response(cmd_type)[1]

    def _get_fallback_response(self, cmd_type: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Provide fallback responses when normal processing fails.
        Ensures consistent response structure even in error cases.
        """
        fallback = {
            "error": True,
            "cmd_type": cmd_type,
            "message": "Could not process request normally"
        }
        
        structured = {
            "analysis": {
                "status": "error",
                "message": "Analysis unavailable",
                "fallback": True
            }
        }
        
        return fallback, structured

    def _get_technical_rating(self, symbol: str) -> str:
        """Get technical rating based on market data."""
        try:
            data = self.market_data.fetch_data(symbol)
            if data is not None and not data.empty:
                latest = data.iloc[-1]
                if latest['RSI'] > 70:
                    return "overbought"
                elif latest['RSI'] < 30:
                    return "oversold"
                return "neutral"
        except Exception as e:
            print(f"Technical Rating Error: {str(e)}")
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