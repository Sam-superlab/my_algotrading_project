import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    def __init__(self, symbol: str, start_date: str, end_date: str,
                 window: int = 20, std_dev: float = 2.0):
        super().__init__(symbol, start_date, end_date)
        self.window = window
        self.std_dev = std_dev

    def generate_signals(self) -> pd.DataFrame:
        signals = pd.DataFrame(index=self.data.index)
        signals['Position'] = 0

        # Calculate Bollinger Bands
        rolling_mean = self.data['Close'].rolling(window=self.window).mean()
        rolling_std = self.data['Close'].rolling(window=self.window).std()
        upper_band = rolling_mean + (rolling_std * self.std_dev)
        lower_band = rolling_mean - (rolling_std * self.std_dev)

        # Generate signals
        signals['Position'] = np.where(self.data['Close'] < lower_band, 1,
                                       np.where(self.data['Close'] > upper_band, -1, 0))

        return signals
