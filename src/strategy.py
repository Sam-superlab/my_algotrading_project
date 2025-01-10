import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class HamiltonianStrategy:
    def __init__(self, symbol, start_date, end_date,
                 damping=0.1, external_influence=0.5, friction=0.05,
                 price_threshold=0.02, allocation_threshold=50):
        """Initialize strategy parameters"""
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.params = {
            'damping': damping,
            'external_influence': external_influence,
            'friction': friction,
            'price_threshold': price_threshold,
            'allocation_threshold': allocation_threshold
        }

        # Will store results
        self.positions = []
        self.portfolio_value = []
        self.returns = []

    def fetch_data(self):
        """Fetch historical data from Yahoo Finance"""
        print(f"Fetching data for {self.symbol}...")
        self.data = yf.download(
            self.symbol, start=self.start_date, end=self.end_date)
        if self.data.empty:
            raise ValueError("No data fetched. Please check symbol and dates.")

        # Calculate basic features
        self.data['Returns'] = self.data['Close'].pct_change()
        self.data['Volume_Change'] = self.data['Volume'].pct_change()
        self.data['Cash_Flow'] = self.data['Close'] * self.data['Volume']

        print(f"Fetched {len(self.data)} days of data")
        return self.data

    def calculate_potential_energy(self, price, volume):
        """Calculate potential energy based on price and volume"""
        return price * volume

    def calculate_kinetic_energy(self, cash_flow):
        """Calculate kinetic energy based on cash flow"""
        return 0.5 * (cash_flow ** 2)

    def generate_signals(self):
        """Generate trading signals based on Hamiltonian mechanics"""
        # Initialize signals DataFrame with the same index as self.data
        signals = pd.DataFrame(index=self.data.index)
        signals['Position'] = 0  # Default position is neutral

        # Calculate energies
        potential_energy = self.calculate_potential_energy(
            self.data['Close'],
            self.data['Volume']
        )
        kinetic_energy = self.calculate_kinetic_energy(self.data['Cash_Flow'])

        # Total energy (Hamiltonian)
        total_energy = potential_energy + kinetic_energy

        # Generate signals based on energy changes
        energy_change = total_energy.pct_change().fillna(0)

        # Generate buy/sell signals
        signals['Position'] = np.where(
            energy_change > self.params['price_threshold'], 1,
            np.where(energy_change < -self.params['price_threshold'], -1, 0)
        )

        return signals

    def backtest(self, initial_capital=100000):
        """Perform backtest of the strategy"""
        print("Starting backtest...")

        # Generate trading signals
        signals = self.generate_signals()

        # Initialize portfolio metrics
        portfolio = pd.DataFrame(index=signals.index)
        portfolio['Position'] = signals['Position']
        portfolio['Close'] = self.data['Close']
        portfolio['Holdings'] = portfolio['Position'] * portfolio['Close']

        # Calculate returns
        portfolio['Returns'] = portfolio['Holdings'].pct_change().fillna(0)
        portfolio['Strategy_Returns'] = portfolio['Position'].shift(
            1) * portfolio['Returns']

        # Calculate portfolio value
        portfolio['Portfolio_Value'] = (
            1 + portfolio['Strategy_Returns']).cumprod() * initial_capital

        self.portfolio = portfolio
        print("Backtest completed")
        return portfolio

    def calculate_metrics(self):
        """Calculate performance metrics"""
        returns = self.portfolio['Strategy_Returns'].dropna()

        metrics = {
            'Total Return': (self.portfolio['Portfolio_Value'].iloc[-1] /
                             self.portfolio['Portfolio_Value'].iloc[0] - 1) * 100,
            'Annual Return': returns.mean() * 252 * 100,
            'Volatility': returns.std() * np.sqrt(252) * 100,
            'Sharpe Ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() != 0 else 0,
            'Max Drawdown': (self.portfolio['Portfolio_Value'] /
                             self.portfolio['Portfolio_Value'].cummax() - 1).min() * 100
        }

        return pd.Series(metrics)
