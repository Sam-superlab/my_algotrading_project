import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class TradeResult:
    """Container for individual trade results"""
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_price: float
    exit_price: float
    position_size: float
    pnl: float
    return_pct: float


class Backtester:
    """Backtesting engine for trading strategies"""

    def __init__(self, config: Dict):
        self.initial_capital = config.get(
            'backtest', {}).get('initial_capital', 100000)
        self.position_size = config.get(
            'backtest', {}).get('position_size', 0.1)
        self.stop_loss = config.get('backtest', {}).get('stop_loss', 0.02)
        self.take_profit = config.get('backtest', {}).get('take_profit', 0.05)

        self.trades: List[TradeResult] = []
        self.equity_curve = []
        self.current_capital = self.initial_capital

    def run(self, df: pd.DataFrame, predictions: np.ndarray) -> Dict:
        """Run backtest on historical data with model predictions"""
        df = df.copy()
        df['prediction'] = predictions

        for i in range(1, len(df)):
            if self._should_enter_trade(df, i):
                trade = self._execute_trade(df, i)
                if trade:
                    self.trades.append(trade)
                    self.current_capital += trade.pnl

            self.equity_curve.append(self.current_capital)

        return self._generate_results()

    def _should_enter_trade(self, df: pd.DataFrame, index: int) -> bool:
        """Determine if we should enter a trade based on prediction"""
        return df['prediction'].iloc[index] == 1 and not self._has_open_position()

    def _execute_trade(self, df: pd.DataFrame, entry_index: int) -> Optional[TradeResult]:
        """Execute a trade and track its performance"""
        entry_price = df['close'].iloc[entry_index]
        position_size = self.current_capital * self.position_size
        shares = position_size / entry_price

        # Find exit point based on stop loss and take profit
        exit_index = self._find_exit_point(df, entry_index, entry_price)
        if exit_index is None:
            return None

        exit_price = df['close'].iloc[exit_index]
        pnl = (exit_price - entry_price) * shares
        return_pct = (exit_price - entry_price) / entry_price

        return TradeResult(
            entry_date=df.index[entry_index],
            exit_date=df.index[exit_index],
            entry_price=entry_price,
            exit_price=exit_price,
            position_size=position_size,
            pnl=pnl,
            return_pct=return_pct
        )

    def _find_exit_point(self, df: pd.DataFrame, entry_index: int, entry_price: float) -> Optional[int]:
        """Find the index where we should exit the trade"""
        for i in range(entry_index + 1, len(df)):
            current_price = df['close'].iloc[i]
            return_pct = (current_price - entry_price) / entry_price

            if return_pct <= -self.stop_loss or return_pct >= self.take_profit:
                return i
        return None

    def _has_open_position(self) -> bool:
        """Check if we currently have an open position"""
        return len(self.trades) > 0 and self.trades[-1].exit_date is None

    def _generate_results(self) -> Dict:
        """Generate backtest summary statistics"""
        returns = [trade.return_pct for trade in self.trades]

        return {
            'total_trades': len(self.trades),
            'profitable_trades': sum(1 for r in returns if r > 0),
            'win_rate': sum(1 for r in returns if r > 0) / len(returns) if returns else 0,
            'avg_return': np.mean(returns) if returns else 0,
            'max_drawdown': self._calculate_max_drawdown(),
            'final_capital': self.current_capital,
            'total_return': (self.current_capital - self.initial_capital) / self.initial_capital
        }

    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from equity curve"""
        peak = self.equity_curve[0]
        max_drawdown = 0

        for value in self.equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)

        return max_drawdown
