# src/trading_assistant/commands/backtest.py

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
import json

class BacktestCommand:
    def __init__(self, market_data):
        self.market_data = market_data

    def execute(self, arg: str = ''):
        """Execute backtest command"""
        args = arg.split()
        
        if not args or len(args) < 2:
            print("❌ Usage: /backtest <strategy_name> <symbol> [timeframe]")
            print("Example: /backtest rsi_reversal AAPL 1d")
            return
            
        strategy_name = args[0]
        symbol = args[1]
        timeframe = args[2] if len(args) > 2 else '1d'
        
        try:
            # Load strategy configuration
            with open('strategies.json', 'r') as f:
                strategies = json.load(f)
                if strategy_name not in strategies:
                    print(f"❌ Strategy '{strategy_name}' not found")
                    return
                strategy_config = strategies[strategy_name]
            
            print(f"\n🔄 Running backtest for {strategy_name} on {symbol} ({timeframe})")
            print(f"Strategy Config: {json.dumps(strategy_config, indent=2)}")
            
            data = self.market_data.fetch_data(symbol, period='1y', interval=timeframe)
            if data is not None:
                results = self._run_backtest(data, strategy_config)
                self._show_results(results)
                self._plot_results(data, results)
            else:
                print("❌ Failed to fetch data for backtesting")
                
        except FileNotFoundError:
            print("❌ No saved strategies found. Create a strategy first using /build")
        except Exception as e:
            print(f"❌ Backtest error: {str(e)}")

    def _get_signal(self, row: pd.Series, strategy_type: str) -> str:
        """Get trading signal based on strategy type"""
        if strategy_type == 'macd_momentum':
            return self._get_macd_signal(row)
        elif strategy_type == 'rsi_reversal':
            return self._get_rsi_signal(row)
        return self._get_breakout_signal(row)

    def _get_macd_signal(self, row: pd.Series) -> str:
        """Generate MACD signals"""
        try:
            # Check if we have required MACD data
            if 'MACD' not in row or 'MACD_Signal' not in row:
                return 'hold'
                
            # Get histogram value
            macd_hist = row['MACD'] - row['MACD_Signal']
            
            # Buy conditions:
            # 1. MACD crosses above Signal
            # 2. MACD is positive (uptrend)
            if macd_hist > 0 and row['MACD'] > 0:
                print(f"\n🟢 MACD Buy Signal:")
                print(f"MACD: {row['MACD']:.2f}")
                print(f"Signal: {row['MACD_Signal']:.2f}")
                print(f"Histogram: {macd_hist:.2f}")
                return 'buy'
                
            # Sell conditions:
            # 1. MACD crosses below Signal
            # 2. MACD is negative (downtrend)
            elif macd_hist < 0 and row['MACD'] < 0:
                print(f"\n🔴 MACD Sell Signal:")
                print(f"MACD: {row['MACD']:.2f}")
                print(f"Signal: {row['MACD_Signal']:.2f}")
                print(f"Histogram: {macd_hist:.2f}")
                return 'sell'
                
            return 'hold'
            
        except Exception as e:
            print(f"Error in MACD signal: {e}")
        return 'hold'    

    def _get_rsi_signal(self, row: pd.Series) -> str:
        """Generate RSI signals"""
        try:
            if row['RSI'] < 30:
                print(f"RSI Buy Signal: RSI={row['RSI']:.2f}")
                return 'buy'
            elif row['RSI'] > 70:
                print(f"RSI Sell Signal: RSI={row['RSI']:.2f}")
                return 'sell'
            return 'hold'
        except Exception as e:
            print(f"Error in RSI signal: {e}")
            return 'hold'

    def _get_breakout_signal(self, row: pd.Series) -> str:
        """Generate breakout signals"""
        try:
            if row['Close'] > row['BB_Upper']:
                return 'buy'
            elif row['Close'] < row['BB_Lower']:
                return 'sell'
            return 'hold'
        except Exception as e:
            print(f"Error in breakout signal: {e}")
            return 'hold'

    def _should_exit(self, position: Dict, current_bar: pd.Series, price_diff: float) -> bool:
        """Determine if position should be closed"""
        try:
            # Load strategy configuration
            with open('strategies.json', 'r') as f:
                strategies = json.load(f)
                strategy = strategies.get(position['strategy_name'])
                if not strategy:
                    return False
                
                # Calculate percentage gain/loss
                pnl_pct = (price_diff / position['entry_price']) * 100
                
                # Check stop loss
                if 'stop_loss' in strategy['trade']:
                    stop_loss = float(strategy['trade']['stop_loss']['value'])
                    if pnl_pct <= -stop_loss:
                        print(f"Stop Loss Hit: {pnl_pct:.2f}%")
                        return True
                
                # Check take profit
                if 'take_profit' in strategy['trade']:
                    tp = strategy['trade']['take_profit']
                    if tp['type'] == 'levels':
                        for level in tp['values']:
                            if pnl_pct >= float(level):
                                print(f"Take Profit Hit: {pnl_pct:.2f}%")
                                return True
                    else:
                        if pnl_pct >= float(tp['value']):
                            print(f"Take Profit Hit: {pnl_pct:.2f}%")
                            return True
                
                return False
                
        except Exception as e:
            print(f"Error in exit check: {e}")
            return False

    def _run_backtest(self, data: pd.DataFrame, strategy_config: Dict) -> Dict:
        """Run backtest with strategy configuration"""
        try:
            trades = []
            position = None
            initial_capital = strategy_config['portfolio']['size']
            equity_curve = [initial_capital]
            
            print("\nStarting Backtest:")
            print(f"Initial Capital: ${initial_capital:,.2f}")
            
            for i in range(len(data)-1):
                current_bar = data.iloc[i]
                next_bar = data.iloc[i+1]
                
                # Get signal
                signal = self._get_signal(current_bar, 'macd_momentum')
                
                # Entry Logic
                if position is None and signal in ['buy', 'sell']:
                    # Calculate position size
                    risk_amount = initial_capital * (strategy_config['position_sizing']['max_risk_per_trade'] / 100)
                    stop_loss_pct = strategy_config['trade']['stop_loss']['value'] / 100
                    position_size = risk_amount / stop_loss_pct
                    shares = int(position_size / next_bar['Open'])
                    
                    position = {
                        'type': signal,
                        'entry_price': next_bar['Open'],
                        'entry_date': next_bar.name,
                        'shares': shares,
                        'stop_loss': next_bar['Open'] * (1 - stop_loss_pct) if signal == 'buy' else next_bar['Open'] * (1 + stop_loss_pct),
                        'take_profit_levels': strategy_config['trade']['take_profit']['values']
                    }
                    
                    print(f"\n🎯 Opening {signal.upper()} Position:")
                    print(f"Date: {position['entry_date']}")
                    print(f"Price: ${position['entry_price']:.2f}")
                    print(f"Shares: {shares}")
                    print(f"Stop Loss: ${position['stop_loss']:.2f}")
                    
                # Exit Logic
                elif position is not None:
                    # Calculate current P&L
                    price_diff = next_bar['Open'] - position['entry_price']
                    if position['type'] == 'sell':
                        price_diff = -price_diff
                        
                    pnl = price_diff * position['shares']
                    pnl_pct = (price_diff / position['entry_price']) * 100
                    
                    # Check exit conditions
                    should_exit = False
                    exit_reason = ""
                    
                    # 1. Stop Loss
                    if (position['type'] == 'buy' and next_bar['Low'] <= position['stop_loss']) or \
                    (position['type'] == 'sell' and next_bar['High'] >= position['stop_loss']):
                        should_exit = True
                        exit_reason = "Stop Loss"
                    
                    # 2. Take Profit
                    for tp_level in position['take_profit_levels']:
                        if pnl_pct >= float(tp_level):
                            should_exit = True
                            exit_reason = f"Take Profit {tp_level}%"
                            break
                    
                    # 3. Signal Reversal
                    if (position['type'] == 'buy' and signal == 'sell') or \
                    (position['type'] == 'sell' and signal == 'buy'):
                        should_exit = True
                        exit_reason = "Signal Reversal"
                    
                    if should_exit:
                        trades.append({
                            'entry_date': position['entry_date'],
                            'exit_date': next_bar.name,
                            'type': position['type'],
                            'entry': position['entry_price'],
                            'exit': next_bar['Open'],
                            'shares': position['shares'],
                            'pnl': pnl,
                            'pnl_pct': pnl_pct,
                            'exit_reason': exit_reason
                        })
                        
                        print(f"\n📊 Closing Position - {exit_reason}:")
                        print(f"Exit Date: {next_bar.name}")
                        print(f"Exit Price: ${next_bar['Open']:.2f}")
                        print(f"P&L: ${pnl:.2f} ({pnl_pct:.2f}%)")
                        
                        equity_curve.append(equity_curve[-1] + pnl)
                        position = None
                
                if len(equity_curve) <= i:
                    equity_curve.append(equity_curve[-1])
            
            # Force close any open position at the end of backtest
            if position is not None:
                final_bar = data.iloc[-1]
                price_diff = final_bar['Close'] - position['entry_price']
                if position['type'] == 'sell':
                    price_diff = -price_diff
                    
                pnl = price_diff * position['shares']
                pnl_pct = (price_diff / position['entry_price']) * 100
                
                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': final_bar.name,
                    'type': position['type'],
                    'entry': position['entry_price'],
                    'exit': final_bar['Close'],
                    'shares': position['shares'],
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'exit_reason': 'End of Period'
                })
                equity_curve.append(equity_curve[-1] + pnl)
            
            return self._calculate_statistics(trades, equity_curve)
            
        except Exception as e:
            print(f"❌ Backtest error: {str(e)}")
            # Return empty results
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'equity_curve': [initial_capital],
                'trades': []
            }

    def _calculate_statistics(self, trades: List[Dict], equity_curve: List[float]) -> Dict:
        """Calculate backtest statistics"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'total_return': ((equity_curve[-1] - equity_curve[0]) / equity_curve[0] * 100),
                'sharpe_ratio': 0,
                'equity_curve': equity_curve,
                'trades': []
            }
        
        win_trades = [t for t in trades if t['pnl'] > 0]
        loss_trades = [t for t in trades if t['pnl'] < 0]
        
        equity_series = pd.Series(equity_curve)
        drawdown = (equity_series - equity_series.cummax()) / equity_series.cummax() * 100
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(win_trades),
            'losing_trades': len(loss_trades),
            'win_rate': len(win_trades) / len(trades) * 100,
            'avg_win': np.mean([t['pnl'] for t in win_trades]) if win_trades else 0,
            'avg_loss': np.mean([t['pnl'] for t in loss_trades]) if loss_trades else 0,
            'largest_win': max([t['pnl'] for t in trades]),
            'largest_loss': min([t['pnl'] for t in trades]),
            'profit_factor': abs(sum(t['pnl'] for t in win_trades) / sum(t['pnl'] for t in loss_trades)) if loss_trades else float('inf'),
            'max_drawdown': abs(min(drawdown)),
            'total_return': ((equity_curve[-1] - equity_curve[0]) / equity_curve[0] * 100),
            'sharpe_ratio': self._calculate_sharpe_ratio(equity_curve),
            'equity_curve': equity_curve,
            'trades': trades
        }

    def _calculate_sharpe_ratio(self, equity_curve: List[float]) -> float:
        """Calculate Sharpe Ratio"""
        if len(equity_curve) < 2:
            return 0.0
        
        returns = pd.Series(equity_curve).pct_change().dropna()
        risk_free_rate = 0.02  # Assuming 2% risk-free rate
        excess_returns = returns - (risk_free_rate / 252)  # Daily adjustment
        
        if excess_returns.std() == 0:
            return 0.0
        
        return np.sqrt(252) * (excess_returns.mean() / excess_returns.std())

    def _show_results(self, results: Dict):
        """Display backtest results"""
        print("\n📊 Backtest Results Summary:")
        print("=" * 40)
        print(f"Total Trades: {results['total_trades']}")
        
        if results['total_trades'] == 0:
            print("\n❌ No trades executed with current strategy settings")
            print("Consider adjusting strategy parameters:")
            print("1. Check entry/exit conditions")
            print("2. Verify indicator settings")
            print("3. Review timeframe selection")
            return
        
        print(f"Win Rate: {results['win_rate']:.2f}%")
        print(f"Profit Factor: {results['profit_factor']:.2f}")
        print(f"Total Return: {results['total_return']:.2f}%")
        print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        
        print("\n📈 Trade Statistics:")
        print(f"Average Win: ${results['avg_win']:.2f}")
        print(f"Average Loss: ${results['avg_loss']:.2f}")
        print(f"Largest Win: ${results['largest_win']:.2f}")
        print(f"Largest Loss: ${results['largest_loss']:.2f}")

    def _plot_results(self, data: pd.DataFrame, results: Dict):
        """Plot backtest results"""
        if results['total_trades'] == 0:
            print("No trades to plot")
            return
            
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Price and Trades
        plt.subplot(2, 1, 1)
        plt.plot(data.index, data['Close'], label='Price', color='blue', alpha=0.6)
        
        # Plot trades
        for trade in results['trades']:
            if trade['type'] == 'buy':
                plt.plot(trade['entry_date'], trade['entry'], '^', color='green', markersize=10, label='Buy')
                plt.plot(trade['exit_date'], trade['exit'], 'v', color='red', markersize=10, label='Sell')
            else:
                plt.plot(trade['entry_date'], trade['entry'], 'v', color='red', markersize=10)
                plt.plot(trade['exit_date'], trade['exit'], '^', color='green', markersize=10)
        
        plt.title('Price and Trades')
        plt.grid(True)
        plt.legend()
        
        # Plot 2: Equity Curve and Drawdown
        plt.subplot(2, 1, 2)
        equity_curve = pd.Series(results['equity_curve'], index=data.index[:len(results['equity_curve'])])
        plt.plot(equity_curve.index, equity_curve.values, label='Equity', color='blue')
        
        # Calculate and plot drawdown
        drawdown = (equity_curve - equity_curve.cummax()) / equity_curve.cummax() * 100
        plt.fill_between(drawdown.index, drawdown.values, 0, color='red', alpha=0.3, label='Drawdown')
        
        plt.title('Equity Curve and Drawdown')
        plt.grid(True)
        plt.legend()
        
        # Adjust layout and display
        plt.tight_layout()
        plt.show()