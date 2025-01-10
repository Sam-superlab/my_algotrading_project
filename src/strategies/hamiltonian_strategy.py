import numpy as np
import pandas as pd
import yfinance as yf
from .base_strategy import BaseStrategy


class HamiltonianStrategy(BaseStrategy):
    def __init__(self, symbol: str, start_date: str, end_date: str,
                 damping=0.1, external_influence=0.5, friction=0.05,
                 price_threshold=0.02, allocation_threshold=50):
        """Initialize strategy parameters"""
        super().__init__(symbol, start_date, end_date)
        self.params = {
            'damping': damping,
            'external_influence': external_influence,
            'friction': friction,
            'price_threshold': price_threshold,
            'allocation_threshold': allocation_threshold
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

    def calculate_potential_energy(self, price, volume):
        """Calculate potential energy based on price and volume"""
        return price * volume

    def calculate_kinetic_energy(self, cash_flow):
        """Calculate kinetic energy based on cash flow"""
        return 0.5 * (cash_flow ** 2)

    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on Hamiltonian mechanics"""
        if self.data is None:
            raise ValueError("No data available. Call fetch_data() first.")

        # Calculate technical indicators first
        self.data['SMA20'] = self.data['Close'].rolling(window=20).mean()
        self.data['SMA50'] = self.data['Close'].rolling(window=50).mean()
        self.data['Momentum'] = self.data['Returns'].rolling(window=10).sum()
        self.data['Volatility'] = self.data['Returns'].rolling(window=20).std()

        # Calculate Hamiltonian components
        # Calculate price difference as Series
        price_diff = (self.data['Close'] - self.data['SMA20']).astype(float)
        potential_energy = price_diff * (1 - self.params['damping'])

        # Calculate momentum energy
        kinetic_energy = self.data['Momentum'].astype(
            float) * (1 - self.params['friction'])

        # Calculate trend
        trend = pd.Series(
            np.where(self.data['SMA20'] > self.data['SMA50'], 1, -1),
            index=self.data.index
        ).astype(float)
        external_force = trend * self.params['external_influence']

        # Total energy (Hamiltonian)
        total_energy = potential_energy + kinetic_energy + external_force

        # Dynamic threshold based on volatility
        threshold = (self.data['Volatility'].rolling(window=20).mean() *
                     self.params['price_threshold']).astype(float)

        # Generate trading signals using vectorized operations
        energy_change = total_energy.diff().fillna(0)

        # Create signals DataFrame with proper Series
        signals = pd.DataFrame(index=self.data.index)
        signals['Position'] = 0

        # Generate buy/sell signals based on energy threshold comparison
        signals.loc[energy_change > threshold, 'Position'] = 1
        signals.loc[energy_change < -threshold, 'Position'] = -1

        # Forward fill positions (maintain previous position when no new signal)
        signals['Position'] = signals['Position'].fillna(
            method='ffill').fillna(0)

        # Add position holding logic
        for i in range(1, len(signals)):
            prev_position = signals['Position'].iloc[i-1]
            curr_position = signals['Position'].iloc[i]

            # Only change position if signal is different from current position
            if curr_position == 0:  # No new signal
                signals['Position'].iloc[i] = prev_position
            elif (prev_position == 1 and curr_position == 1) or \
                 (prev_position == -1 and curr_position == -1):
                # Maintain current position
                signals['Position'].iloc[i] = prev_position

        return signals

    def backtest(self, initial_capital: float = 100000) -> pd.DataFrame:
        """Override backtest method to include transaction costs and position sizing"""
        signals = self.generate_signals()

        portfolio = pd.DataFrame(index=signals.index)
        portfolio['Position'] = signals['Position']
        portfolio['Close'] = self.data['Close']

        # Add transaction costs (0.1% per trade)
        portfolio['Trade'] = portfolio['Position'].diff().fillna(
            0).abs() * 0.001

        # Calculate returns with transaction costs
        portfolio['Holdings'] = portfolio['Position'] * portfolio['Close']
        portfolio['Returns'] = portfolio['Holdings'].pct_change().fillna(0)
        portfolio['Strategy_Returns'] = portfolio['Position'].shift(1).fillna(0) * \
            portfolio['Returns'] - portfolio['Trade']

        # Calculate portfolio value
        portfolio['Portfolio_Value'] = (
            1 + portfolio['Strategy_Returns']).cumprod() * initial_capital

        self.portfolio = portfolio
        return portfolio

    def calculate_metrics(self) -> dict:
        """Calculate strategy performance metrics"""
        returns = self.portfolio['Strategy_Returns'].fillna(0)

        total_return = (self.portfolio['Portfolio_Value'].iloc[-1] /
                        self.portfolio['Portfolio_Value'].iloc[0] - 1) * 100

        annual_return = returns.mean() * 252 * 100
        volatility = returns.std() * np.sqrt(252) * 100
        sharpe_ratio = (returns.mean() * 252) / \
            (returns.std() * np.sqrt(252)) if returns.std() != 0 else 0

        # Calculate maximum drawdown
        portfolio_value = self.portfolio['Portfolio_Value']
        rolling_max = portfolio_value.expanding().max()
        drawdowns = (portfolio_value - rolling_max) / rolling_max
        max_drawdown = drawdowns.min() * 100

        metrics = {
            'Total Return': float(total_return),
            'Annual Return': float(annual_return),
            'Volatility': float(volatility),
            'Sharpe Ratio': float(sharpe_ratio),
            'Max Drawdown': float(max_drawdown)
        }

        return metrics
