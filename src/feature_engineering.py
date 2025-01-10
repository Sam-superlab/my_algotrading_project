import pandas as pd
import numpy as np
from typing import List, Dict


class FeatureEngineer:
    """Feature engineering for market data"""

    def __init__(self, config: Dict = None):
        self.config = config or {}

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for market data"""
        df = df.copy()

        # Moving averages
        for window in [5, 10, 20, 50]:
            df[f'MA_{window}'] = df['close'].rolling(window=window).mean()

        # RSI
        df['RSI'] = self._calculate_rsi(df['close'])

        # MACD
        df = self._calculate_macd(df)

        return df

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicator"""
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()

        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        return df
