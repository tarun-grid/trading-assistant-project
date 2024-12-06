# trading_signals.py

import pandas as pd
import numpy as np

class TradingSignals:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        
    def analyze_all_signals(self) -> dict:
        """Generate all trading signals"""
        signals = {
            'price_signals': self.get_price_signals(),
            'momentum_signals': self.get_momentum_signals(),
            'volume_signals': self.get_volume_signals(),
            'trend_signals': self.get_trend_signals()
        }
        return signals
    
    def get_price_signals(self) -> dict:
        """Analyze price action signals"""
        latest = self.data.iloc[-1]
        prev = self.data.iloc[-2]
        
        return {
            'bb_position': self._analyze_bb_position(latest),
            'price_change': (latest['Close'] - prev['Close']) / prev['Close'] * 100,
            'above_sma_20': latest['Close'] > latest['SMA_20'],
            'above_sma_50': latest['Close'] > latest['SMA_50'],
            'above_sma_200': latest['Close'] > latest['SMA_200']
        }
    
    def get_momentum_signals(self) -> dict:
        """Analyze momentum signals"""
        latest = self.data.iloc[-1]
        
        return {
            'rsi_signal': self._analyze_rsi(latest['RSI']),
            'macd_signal': self._analyze_macd(latest),
            'stoch_signal': self._analyze_stochastic(latest)
        }
    
    def get_volume_signals(self) -> dict:
        """Analyze volume signals"""
        latest = self.data.iloc[-1]
        
        return {
            'volume_surge': latest['Volume'] > latest['Volume_SMA'] * 1.5,
            'obv_trend': self._analyze_obv_trend(),
            'volume_price_trend': self._analyze_volume_price_trend()
        }
    
    def get_trend_signals(self) -> dict:
        """Analyze trend signals"""
        latest = self.data.iloc[-1]
        
        return {
            'trend_strength': self._calculate_trend_strength(),
            'trend_direction': self._determine_trend_direction(),
            'support_resistance': self._find_support_resistance()
        }
    
    def _analyze_bb_position(self, latest) -> str:
        """Analyze position relative to Bollinger Bands"""
        if latest['Close'] > latest['BB_Upper']:
            return "Overbought"
        elif latest['Close'] < latest['BB_Lower']:
            return "Oversold"
        else:
            return "Normal"
    
    def _analyze_rsi(self, rsi) -> str:
        """Analyze RSI signals"""
        if rsi > 70:
            return "Overbought"
        elif rsi < 30:
            return "Oversold"
        return "Neutral"
    
    def _analyze_macd(self, latest) -> str:
        """Analyze MACD signals"""
        if latest['MACD'] > latest['MACD_Signal']:
            return "Bullish"
        return "Bearish"
    
    def _analyze_stochastic(self, latest) -> str:
        """Analyze Stochastic signals"""
        if latest['Stoch_k'] > 80:
            return "Overbought"
        elif latest['Stoch_k'] < 20:
            return "Oversold"
        return "Neutral"
    
    def _analyze_obv_trend(self) -> str:
        """Analyze On Balance Volume trend"""
        recent_obv = self.data['OBV'].tail(20)
        obv_sma = recent_obv.mean()
        if recent_obv.iloc[-1] > obv_sma:
            return "Bullish"
        return "Bearish"
    
    def _analyze_volume_price_trend(self) -> str:
        """Analyze volume and price relationship"""
        latest = self.data.iloc[-1]
        prev = self.data.iloc[-2]
        
        price_up = latest['Close'] > prev['Close']
        volume_up = latest['Volume'] > prev['Volume']
        
        if price_up and volume_up:
            return "Strong Bullish"
        elif not price_up and volume_up:
            return "Strong Bearish"
        return "Neutral"
    
    def _calculate_trend_strength(self) -> float:
        """Calculate trend strength using ADX-like method"""
        latest = self.data.iloc[-1]
        return abs(latest['SMA_20'] - latest['SMA_50']) / latest['ATR']
    
    def _determine_trend_direction(self) -> str:
        """Determine overall trend direction"""
        latest = self.data.iloc[-1]
        if latest['SMA_20'] > latest['SMA_50'] > latest['SMA_200']:
            return "Strong Uptrend"
        elif latest['SMA_20'] < latest['SMA_50'] < latest['SMA_200']:
            return "Strong Downtrend"
        return "Mixed"
    
    def _find_support_resistance(self) -> dict:
        """Find potential support and resistance levels"""
        recent_high = self.data['High'].tail(20).max()
        recent_low = self.data['Low'].tail(20).min()
        
        return {
            'resistance': recent_high,
            'support': recent_low,
            'mid_point': (recent_high + recent_low) / 2
        }

def generate_alerts(signals: dict) -> list:
    """Generate trading alerts based on signals"""
    alerts = []
    
    # Price alerts
    if signals['price_signals']['bb_position'] in ['Overbought', 'Oversold']:
        alerts.append(f"Price is {signals['price_signals']['bb_position']} on Bollinger Bands")
    
    # Momentum alerts
    if signals['momentum_signals']['rsi_signal'] != "Neutral":
        alerts.append(f"RSI shows {signals['momentum_signals']['rsi_signal']} conditions")
    
    # Volume alerts
    if signals['volume_signals']['volume_surge']:
        alerts.append("Unusual volume detected")
    
    # Trend alerts
    trend = signals['trend_signals']['trend_direction']
    if trend in ['Strong Uptrend', 'Strong Downtrend']:
        alerts.append(f"Market in {trend}")
    
    return alerts