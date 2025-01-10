import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from typing import Tuple, Dict, Any


class TradingModel:
    """Trading model class for market prediction"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.model = self._initialize_model()

    def _initialize_model(self) -> Any:
        """Initialize the machine learning model"""
        model_config = self.config.get('model', {})
        model_type = model_config.get('type', 'random_forest')

        if model_type == 'random_forest':
            return RandomForestClassifier(
                n_estimators=model_config.get('n_estimators', 100),
                random_state=42
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for training"""
        # Create target variable (1 if price goes up, 0 if down)
        df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

        # Remove date column and target column for features
        feature_cols = [
            col for col in df.columns if col not in ['date', 'target']]

        return df[feature_cols], df['target']

    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        """Train the model"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)

        # Print model performance
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        print(f"Train accuracy: {train_score:.4f}")
        print(f"Test accuracy: {test_score:.4f}")

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        return self.model.predict(X)
