# src/trading_assistant/core/personas.py

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import random

class RiskTolerance(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class TimeHorizon(Enum):
    DAY_TRADER = "day_trader"
    SWING_TRADER = "swing_trader"
    POSITION_TRADER = "position_trader"
    LONG_TERM = "long_term"

@dataclass
class TradePreferences:
    min_position_size: float  # Minimum position size as % of portfolio
    max_position_size: float  # Maximum position size as % of portfolio
    max_trades_per_day: int
    preferred_timeframes: List[str]
    stop_loss_range: tuple  # (min%, max%)
    take_profit_range: tuple  # (min%, max%)
    preferred_indicators: List[str]
    
@dataclass
class PersonalityTraits:
    risk_tolerance: RiskTolerance
    time_horizon: TimeHorizon
    preferred_sectors: List[str]
    avoid_sectors: List[str]
    max_drawdown_tolerance: float
    prefers_diversification: bool
    loves_memes: bool  # Gen-Z specific trait

class TradingPersona:
    def __init__(
        self,
        name: str,
        traits: PersonalityTraits,
        preferences: TradePreferences,
        emoji: str
    ):
        self.name = name
        self.traits = traits
        self.preferences = preferences
        self.emoji = emoji
        
        # Persona-specific responses
        self.responses = self._initialize_responses()
        
    def _initialize_responses(self) -> Dict[str, List[str]]:
        """Initialize persona-specific response templates"""
        return {
            "greeting": self._get_greeting_templates(),
            "success": self._get_success_templates(),
            "warning": self._get_warning_templates(),
            "error": self._get_error_templates()
        }
    
    def _get_greeting_templates(self) -> List[str]:
        """Override in specific personas"""
        return ["Hey there!", "Hi!", "Hello!"]
        
    def _get_success_templates(self) -> List[str]:
        """Override in specific personas"""
        return ["Great!", "Awesome!", "Nice!"]
        
    def _get_warning_templates(self) -> List[str]:
        """Override in specific personas"""
        return ["Watch out!", "Be careful!", "Heads up!"]
        
    def _get_error_templates(self) -> List[str]:
        """Override in specific personas"""
        return ["Oops!", "That didn't work!", "Something went wrong!"]
    
    def get_response(self, category: str) -> str:
        """Get a random response from the specified category"""
        if category in self.responses:
            return random.choice(self.responses[category])
        return "..."

    def analyze_risk(self, position_size: float, stop_loss: float) -> bool:
        """Check if trade risk aligns with persona's risk tolerance"""
        max_risk = self.preferences.max_position_size * (stop_loss / 100)
        return position_size * (stop_loss / 100) <= max_risk
    
    def validate_timeframe(self, timeframe: str) -> bool:
        """Check if timeframe matches persona's preferences"""
        return timeframe in self.preferences.preferred_timeframes

class YoloTrader(TradingPersona):
    """The aggressive, meme-loving trader persona"""
    
    def _get_greeting_templates(self) -> List[str]:
        return [
            "yo fam, ready to send it? 🚀",
            "sup! let's get this bread 🍞",
            "ayy, time to make moves 💯",
            "what's good! market's looking juicy 🔥"
        ]
        
    def _get_success_templates(self) -> List[str]:
        return [
            "sheeeesh! we're mooning! 🌙",
            "no cap, that trade was bussin fr fr 💯",
            "ez gains, you love to see it 🔥",
            "W rizz on that trade fam! 🎯"
        ]
        
    def _get_warning_templates(self) -> List[str]:
        return [
            "ay fam, this looking kinda sus 👀",
            "ngl, might wanna chill on this one 💭",
            "respectfully, we might be down bad here ⚠️",
            "chief, this ain't it rn 🤔"
        ]
        
    def _get_error_templates(self) -> List[str]:
        return [
            "bruh moment fr fr 💀",
            "deadass just took an L 😭",
            "ain't no way fam 😩",
            "big yikes energy rn 😬"
        ]

class ValueInvestor(TradingPersona):
    """The conservative, long-term focused trader persona"""
    
    def _get_greeting_templates(self) -> List[str]:
        return [
            "Hello! Ready for some value hunting? 📊",
            "Welcome back! Let's find some hidden gems 💎",
            "Hi there! Time for some fundamental analysis 📈",
            "Greetings! Markets looking interesting today 🎯"
        ]
        
    def _get_success_templates(self) -> List[str]:
        return [
            "Excellent fundamentals! Looking promising 📈",
            "Strong value proposition here 💎",
            "This could be a solid long-term play 🎯",
            "Great margin of safety on this one 🛡️"
        ]
        
    def _get_warning_templates(self) -> List[str]:
        return [
            "Hmm, valuations seem a bit stretched 🤔",
            "We might want to dig deeper into the numbers 📊",
            "Let's review the risk factors carefully 🔍",
            "Fundamentals raising some concerns ⚠️"
        ]
        
    def _get_error_templates(self) -> List[str]:
        return [
            "This doesn't align with our value criteria ❌",
            "Risk metrics are outside our comfort zone ⚠️",
            "Let's pass on this opportunity 🚫",
            "Not seeing the value here 📉"
        ]

class SwingTrader(TradingPersona):
    """The technical analysis focused swing trader persona"""
    
    def _get_greeting_templates(self) -> List[str]:
        return [
            "hey! charts looking spicy today 📊",
            "what's up! found some nice setups 🎯",
            "ready to catch some moves? 🌊",
            "yo! market's giving signals 📈"
        ]
        
    def _get_success_templates(self) -> List[str]:
        return [
            "perfect setup, charts don't lie! 📈",
            "technicals looking clean af 🎯",
            "momentum's on our side! 🌊",
            "this pattern's about to pop off 🚀"
        ]
        
    def _get_warning_templates(self) -> List[str]:
        return [
            "divergence showing, stay alert 👀",
            "volume not confirming yet 📊",
            "resistance ahead, watch your size 🎯",
            "indicators showing mixed signals ⚠️"
        ]
        
    def _get_error_templates(self) -> List[str]:
        return [
            "setup invalidated, time to bounce 🚫",
            "nah fam, chart's looking rough 📉",
            "technicals broke down, we out 🏃‍♂️",
            "this ain't the move rn 🤚"
        ]

class PersonaManager:
    _instance = None  # Class variable to store singleton instance
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.personas = cls._instance._initialize_personas()
            cls._instance.active_persona = None
        return cls._instance

    def set_active_persona(self, name: str) -> bool:
        """Set the active trading persona"""
        persona = self.get_persona(name.lower())
        if persona:
            self.active_persona = persona
            return True
        return False
    
    def get_active_persona(self):
        """Get currently active persona"""
        return self.active_persona
        
    def _initialize_personas(self) -> Dict[str, TradingPersona]:
        """Initialize all trading personas"""
        return {
            "yolo": YoloTrader(
                name="YOLO Trader",
                traits=PersonalityTraits(
                    risk_tolerance=RiskTolerance.AGGRESSIVE,
                    time_horizon=TimeHorizon.DAY_TRADER,
                    preferred_sectors=["Technology", "Crypto", "Meme Stocks"],
                    avoid_sectors=["Utilities", "Consumer Staples"],
                    max_drawdown_tolerance=30.0,
                    prefers_diversification=False,
                    loves_memes=True
                ),
                preferences=TradePreferences(
                    min_position_size=5.0,
                    max_position_size=25.0,
                    max_trades_per_day=10,
                    preferred_timeframes=["1m", "5m", "15m"],
                    stop_loss_range=(5, 15),
                    take_profit_range=(10, 50),
                    preferred_indicators=["RSI", "MACD", "Volume"]
                ),
                emoji="🚀"
            ),
            "value": ValueInvestor(
                name="Value Investor",
                traits=PersonalityTraits(
                    risk_tolerance=RiskTolerance.CONSERVATIVE,
                    time_horizon=TimeHorizon.LONG_TERM,
                    preferred_sectors=["Financial", "Consumer Staples", "Healthcare"],
                    avoid_sectors=["Speculative Tech", "Meme Stocks"],
                    max_drawdown_tolerance=15.0,
                    prefers_diversification=True,
                    loves_memes=False
                ),
                preferences=TradePreferences(
                    min_position_size=2.0,
                    max_position_size=10.0,
                    max_trades_per_day=2,
                    preferred_timeframes=["1d", "1w", "1mo"],
                    stop_loss_range=(10, 20),
                    take_profit_range=(20, 100),
                    preferred_indicators=["PE_Ratio", "PB_Ratio", "Dividend_Yield"]
                ),
                emoji="💎"
            ),
            "swing": SwingTrader(
                name="Swing Trader",
                traits=PersonalityTraits(
                    risk_tolerance=RiskTolerance.MODERATE,
                    time_horizon=TimeHorizon.SWING_TRADER,
                    preferred_sectors=["All"],
                    avoid_sectors=[],
                    max_drawdown_tolerance=20.0,
                    prefers_diversification=True,
                    loves_memes=True
                ),
                preferences=TradePreferences(
                    min_position_size=3.0,
                    max_position_size=15.0,
                    max_trades_per_day=5,
                    preferred_timeframes=["1h", "4h", "1d"],
                    stop_loss_range=(5, 10),
                    take_profit_range=(15, 30),
                    preferred_indicators=["RSI", "MA_Cross", "Volume", "Bollinger"]
                ),
                emoji="🌊"
            )
        }
    
    def get_persona(self, name: str) -> Optional[TradingPersona]:
        """Get a specific persona by name"""
        return self.personas.get(name.lower())
    
    def set_active_persona(self, name: str) -> bool:
        """Set the active trading persona"""
        persona = self.get_persona(name.lower())
        if persona:
            self.active_persona = persona
            return True
        return False
    
    def get_active_persona(self) -> Optional[TradingPersona]:
        """Get currently active persona"""
        return self.active_persona
    
    def list_personas(self) -> List[Dict]:
        """Get list of available personas with their basic info"""
        return [
            {
                "name": p.name,
                "emoji": p.emoji,
                "risk_tolerance": p.traits.risk_tolerance.value,
                "time_horizon": p.traits.time_horizon.value
            }
            for p in self.personas.values()
        ]