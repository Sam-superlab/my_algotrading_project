from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import yfinance as yf


class BaseStrategy(ABC):
    def __init__(self, symbol: str, start_date: str, end_date: str):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.portfolio = None

    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals specific to the strategy"""
        pass

    def backtest(self, initial_capital: float = 100000) -> pd.DataFrame:
        """Common backtesting logic for all strategies"""
        signals = self.generate_signals()

        portfolio = pd.DataFrame(index=signals.index)
        portfolio['Position'] = signals['Position']
        portfolio['Close'] = self.data['Close']
        portfolio['Holdings'] = portfolio['Position'] * portfolio['Close']
        portfolio['Returns'] = portfolio['Holdings'].pct_change().fillna(0)
        portfolio['Strategy_Returns'] = portfolio['Position'].shift(
            1).fillna(0) * portfolio['Returns']
        portfolio['Portfolio_Value'] = (
            1 + portfolio['Strategy_Returns']).cumprod() * initial_capital

        self.portfolio = portfolio
        return portfolio

    def calculate_metrics(self) -> dict:
        """Calculate performance metrics"""
        try:
            returns = self.portfolio['Strategy_Returns'].fillna(
                0)  # Handle NaN values
            total_return = ((self.portfolio['Portfolio_Value'].iloc[-1] /
                            self.portfolio['Portfolio_Value'].iloc[0]) - 1) * 100
            annual_return = returns.mean() * 252 * 100
            volatility = returns.std() * np.sqrt(252) * 100
            sharpe_ratio = (returns.mean() * 252) / \
                (returns.std() * np.sqrt(252)) if returns.std() != 0 else 0
            max_drawdown = (self.portfolio['Portfolio_Value'] /
                            self.portfolio['Portfolio_Value'].cummax() - 1).min() * 100

            metrics = {
                'Total Return': float(total_return),
                'Annual Return': float(annual_return),
                'Volatility': float(volatility),
                'Sharpe Ratio': float(sharpe_ratio),
                'Max Drawdown': float(max_drawdown)
            }

            # Ensure no NaN values in metrics
            for key in metrics:
                if np.isnan(metrics[key]):
                    metrics[key] = 0.0

            return metrics
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            return {
                'Total Return': 0.0,
                'Annual Return': 0.0,
                'Volatility': 0.0,
                'Sharpe Ratio': 0.0,
                'Max Drawdown': 0.0
            }

    def fetch_data(self):
        """Fetch historical data from Yahoo Finance"""
        print(f"Fetching data for {self.symbol}...")
        self.data = yf.download(
            self.symbol, start=self.start_date, end=self.end_date)
        if self.data.empty:
            raise ValueError("No data fetched. Please check symbol and dates.")

        # Calculate basic features without method='ffill'
        self.data['Returns'] = self.data['Close'].pct_change().fillna(0)
        self.data['Volume_Change'] = self.data['Volume'].pct_change().fillna(0)
        self.data['Cash_Flow'] = self.data['Close'] * self.data['Volume']

        print(f"Fetched {len(self.data)} days of data")
        return self.data
