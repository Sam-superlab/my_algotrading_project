import numpy as np
from typing import Dict, Optional


class RiskManager:
    """Risk management module for position sizing and risk control"""

    def __init__(self, config: Dict):
        self.config = config
        self.max_position_size = config.get(
            'risk', {}).get('max_position_size', 0.2)
        self.max_drawdown = config.get('risk', {}).get('max_drawdown', 0.2)
        self.portfolio_value = config.get(
            'risk', {}).get('initial_capital', 100000)

    def calculate_position_size(self,
                                signal_strength: float,
                                volatility: float,
                                current_price: float) -> Optional[float]:
        """
        Calculate position size based on Kelly Criterion and risk limits

        Args:
            signal_strength: Model's prediction probability (0 to 1)
            volatility: Historical volatility of the asset
            current_price: Current asset price

        Returns:
            Number of units to trade, or None if no trade recommended
        """
        if signal_strength < 0.55:  # Minimum confidence threshold
            return None

        # Kelly position sizing
        kelly_fraction = self._kelly_criterion(signal_strength, volatility)

        # Apply position limits
        position_size = min(kelly_fraction, self.max_position_size)
        position_value = self.portfolio_value * position_size

        # Convert to units
        units = position_value / current_price

        return units

    def _kelly_criterion(self, win_prob: float, volatility: float) -> float:
        """
        Calculate Kelly Criterion fraction

        Args:
            win_prob: Probability of winning (0 to 1)
            volatility: Historical volatility

        Returns:
            Kelly fraction (0 to 1)
        """
        loss_prob = 1 - win_prob
        win_loss_ratio = 1 + volatility  # Simplified assumption

        kelly = (win_prob * win_loss_ratio - loss_prob) / win_loss_ratio
        return max(0, kelly)  # Never take negative positions

    def check_risk_limits(self,
                          current_drawdown: float,
                          open_positions: int) -> bool:
        """
        Check if new trades are allowed given current risk exposure

        Returns:
            bool: True if new trades are allowed, False otherwise
        """
        if current_drawdown > self.max_drawdown:
            return False

        # Add other risk checks as needed
        return True

    def update_portfolio_value(self, new_value: float) -> None:
        """Update portfolio value for position sizing calculations"""
        self.portfolio_value = new_value
