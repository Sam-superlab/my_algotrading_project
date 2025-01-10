import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    def __init__(self, symbol: str, start_date: str, end_date: str,
                 lookback_period: int = 20, threshold: float = 0):
        super().__init__(symbol, start_date, end_date)
        self.lookback_period = lookback_period
        self.threshold = threshold

    def generate_signals(self) -> pd.DataFrame:
        signals = pd.DataFrame(index=self.data.index)
        signals['Position'] = 0

        # Calculate momentum
        momentum = self.data['Close'].pct_change(self.lookback_period)

        # Generate signals
        signals['Position'] = np.where(momentum > self.threshold, 1,
                                       np.where(momentum < -self.threshold, -1, 0))

        return signals
