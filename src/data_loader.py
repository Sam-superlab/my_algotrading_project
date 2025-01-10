import os
import pandas as pd
import yaml
from typing import Dict, Optional


class DataLoader:
    """Data loading and preprocessing class"""

    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize DataLoader with configuration"""
        self.config = self._load_config(config_path)
        self.data_path = self.config.get("data", {}).get("path", "data/raw")

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from yaml file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def load_market_data(self, filename: str) -> Optional[pd.DataFrame]:
        """Load market data from CSV file"""
        try:
            file_path = os.path.join(self.data_path, filename)
            df = pd.read_csv(file_path)
            return self._preprocess_market_data(df)
        except Exception as e:
            print(f"Error loading market data: {e}")
            return None

    def _preprocess_market_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess market data"""
        # Convert date column to datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # Handle missing values
        df = df.fillna(method='ffill')

        return df
