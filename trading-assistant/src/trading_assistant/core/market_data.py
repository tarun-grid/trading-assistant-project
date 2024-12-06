# src/trading_assistant/core/market_data.py

import yfinance as yf
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import ta

class MarketData:
    def __init__(self):
        """Initialize the market data handler"""
        self.current_symbol = None
        self.timeframes = {
            '5m': None,
            '30m': None,
            '1h': None,
            '1d': None
        }
        self.valid_periods = {
            '5m': '60d',    # yfinance limitation for 5m data
            '30m': '60d',   # yfinance limitation for 30m data
            '1h': '2y',     # yfinance limitation for 1h data
            '1d': '10y'     # daily data can go back further
        }
        # Top stocks by market cap (as of 2024)
        self.top_stocks = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'NVDA': 'NVIDIA Corporation',
            'META': 'Meta Platforms Inc.',
            'BRK-B': 'Berkshire Hathaway Inc.',
            'LLY': 'Eli Lilly and Company',
            'AVGO': 'Broadcom Inc.',
            'TSLA': 'Tesla, Inc.'
        }
        
    def get_available_stocks(self) -> Dict[str, str]:
        """Return available stock symbols and their names"""
        return self.top_stocks

    def fetch_top_stocks_data(self, timeframe: str = '1d') -> Dict[str, pd.DataFrame]:
        """
        Fetch data for all top stocks for a specific timeframe
        
        Args:
            timeframe: Data interval ('5m', '30m', '1h', '1d')
        
        Returns:
            Dictionary of DataFrames for each stock
        """
        results = {}
        period = self.valid_periods.get(timeframe, '1d')

        print(f"\n📈 Fetching {timeframe} data for top stocks...")
        for symbol in self.top_stocks.keys():
            data = self.fetch_data(symbol, period, timeframe)
            if data is not None:
                results[symbol] = data
                print(f"✅ {symbol} ({self.top_stocks[symbol]})")
                print(f"   Last Price: ${data['Close'].iloc[-1]:.2f}")
                print(f"   Volume: {data['Volume'].iloc[-1]:,}")
                print(f"   RSI: {data['RSI'].iloc[-1]:.2f}")
                print("-------------------")

        return results

    def fetch_all_timeframes(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for all timeframes for a given symbol
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
        
        Returns:
            Dictionary of DataFrames for each timeframe
        """
        self.current_symbol = symbol
        results = {}
        
        for timeframe in self.timeframes.keys():
            data = self.fetch_data(symbol, self.valid_periods[timeframe], timeframe)
            if data is not None:
                results[timeframe] = data
                self.timeframes[timeframe] = data
        
        return results

    def fetch_data(self, symbol: str, period: str = '1y', interval: str = '1d') -> Optional[pd.DataFrame]:
        """Fetch market data for a given symbol"""
        try:
            # Check if symbol is valid before fetching
            if not isinstance(symbol, str) or not symbol.isalpha():
                return None
                
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                print(f"❌ No data found for {symbol}")
                return None
                
            print(f"✅ Successfully fetched {interval} data for {symbol}")
            print(f"   Date range: {data.index[0]} to {data.index[-1]}")
            print(f"   Number of candles: {len(data)}")

            if len(data) > 50:  # Only add indicators if we have enough data
                data = self.add_indicators(data)
            
            return data
                
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {str(e)}")
            return None

    def add_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to the data
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added technical indicators
        """
        if data is None or data.empty:
            return data
        
        try:
            # Trend Indicators
            # Moving Averages
            data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
            data['SMA_50'] = ta.trend.sma_indicator(data['Close'], window=50)
            data['SMA_200'] = ta.trend.sma_indicator(data['Close'], window=200)
            data['EMA_12'] = ta.trend.ema_indicator(data['Close'], window=12)
            data['EMA_26'] = ta.trend.ema_indicator(data['Close'], window=26)
            
            # MACD
            macd = ta.trend.MACD(data['Close'])
            data['MACD'] = macd.macd()
            data['MACD_Signal'] = macd.macd_signal()
            data['MACD_Hist'] = macd.macd_diff()
            
            # Momentum Indicators
            # RSI
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            
            # Stochastic
            stoch = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close'])
            data['Stoch_k'] = stoch.stoch()
            data['Stoch_d'] = stoch.stoch_signal()
            
            # Volatility Indicators
            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(data['Close'])
            data['BB_Upper'] = bollinger.bollinger_hband()
            data['BB_Middle'] = bollinger.bollinger_mavg()
            data['BB_Lower'] = bollinger.bollinger_lband()
            
            # ATR
            data['ATR'] = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close']).average_true_range()
            
            # Volume Indicators
            data['Volume_SMA'] = ta.trend.sma_indicator(data['Volume'], window=20)
            data['OBV'] = ta.volume.OnBalanceVolumeIndicator(data['Close'], data['Volume']).on_balance_volume()
            
            return data
            
        except Exception as e:
            print(f"❌ Error adding indicators: {str(e)}")
            return data

    def get_latest_data(self, timeframe: str) -> Optional[pd.DataFrame]:
        """Get the latest data for a specific timeframe"""
        return self.timeframes.get(timeframe)
    
    def get_latest_price(self, timeframe: str = '1d') -> Optional[float]:
        """Get the latest closing price for a specific timeframe"""
        data = self.timeframes.get(timeframe)
        if data is not None and not data.empty:
            return data['Close'].iloc[-1]
        return None

    def get_market_overview(self, timeframe: str = '1d') -> pd.DataFrame:
        """
        Get a summary of all top stocks
        
        Args:
            timeframe: Data interval to analyze
            
        Returns:
            DataFrame with market overview
        """
        overview_data = []
        
        for symbol, name in self.top_stocks.items():
            data = self.fetch_data(symbol, self.valid_periods[timeframe], timeframe)
            if data is not None:
                latest = data.iloc[-1]
                prev_close = data['Close'].iloc[-2]
                
                overview_data.append({
                    'Symbol': symbol,
                    'Name': name,
                    'Price': round(latest['Close'], 2),
                    'Change %': round(((latest['Close'] - prev_close) / prev_close) * 100, 2),
                    'Volume': int(latest['Volume']),
                    'RSI': round(latest['RSI'], 2) if 'RSI' in data.columns else None,
                    'MACD': round(latest['MACD'], 2) if 'MACD' in data.columns else None,
                    'ATR': round(latest['ATR'], 2) if 'ATR' in data.columns else None,
                    'BB_Upper': round(latest['BB_Upper'], 2) if 'BB_Upper' in data.columns else None,
                    'BB_Lower': round(latest['BB_Lower'], 2) if 'BB_Lower' in data.columns else None,
                    'Stoch_k': round(latest['Stoch_k'], 2) if 'Stoch_k' in data.columns else None,
                    'OBV': int(latest['OBV']) if 'OBV' in data.columns else None
                })
        
        return pd.DataFrame(overview_data)

    def get_summary(self, timeframe: str = '1d') -> dict:
        """Get a summary of the current market data for a specific timeframe"""
        data = self.timeframes.get(timeframe)
        if data is None or data.empty:
            return {"error": f"No data available for {timeframe} timeframe"}
        
        latest = data.iloc[-1]
        prev_day = data.iloc[-2]
        
        return {
            "symbol": self.current_symbol,
            "timeframe": timeframe,
            "latest_close": round(latest['Close'], 2),
            "change_percent": round(((latest['Close'] - prev_day['Close']) / prev_day['Close']) * 100, 2),
            "volume": int(latest['Volume']),
            "volume_sma": int(latest['Volume_SMA']) if 'Volume_SMA' in data.columns else None,
            "rsi": round(latest['RSI'], 2) if 'RSI' in data.columns else None,
            "macd": round(latest['MACD'], 2) if 'MACD' in data.columns else None,
            "macd_signal": round(latest['MACD_Signal'], 2) if 'MACD_Signal' in data.columns else None,
            "stoch_k": round(latest['Stoch_k'], 2) if 'Stoch_k' in data.columns else None,
            "stoch_d": round(latest['Stoch_d'], 2) if 'Stoch_d' in data.columns else None,
            "bb_upper": round(latest['BB_Upper'], 2) if 'BB_Upper' in data.columns else None,
            "bb_middle": round(latest['BB_Middle'], 2) if 'BB_Middle' in data.columns else None,
            "bb_lower": round(latest['BB_Lower'], 2) if 'BB_Lower' in data.columns else None,
            "atr": round(latest['ATR'], 2) if 'ATR' in data.columns else None,
            "sma_20": round(latest['SMA_20'], 2) if 'SMA_20' in data.columns else None,
            "sma_50": round(latest['SMA_50'], 2) if 'SMA_50' in data.columns else None,
            "sma_200": round(latest['SMA_200'], 2) if 'SMA_200' in data.columns else None,
            "obv": int(latest['OBV']) if 'OBV' in data.columns else None,
            "data_points": len(data),
            "date_range": f"{data.index[0]} to {data.index[-1]}"
        }