from src.data_loader import DataLoader
from src.feature_engineering import FeatureEngineer
from src.models import TradingModel
from src.backtest import Backtester
from src.risk_manager import RiskManager


def main():
    # Initialize components
    data_loader = DataLoader()
    feature_engineer = FeatureEngineer()
    trading_model = TradingModel()

    # Load and process data
    df = data_loader.load_market_data("market_data.csv")
    if df is None:
        print("Failed to load data")
        return

    # Generate features
    df = feature_engineer.calculate_technical_indicators(df)

    # Prepare and train model
    X, y = trading_model.prepare_data(df)
    trading_model.train(X, y)

    # Make predictions
    predictions = trading_model.predict(X)

    # Run backtest
    config = data_loader.config  # Reuse the loaded config
    backtester = Backtester(config)
    results = backtester.run(df, predictions)

    # Print backtest results
    print("\nBacktest Results:")
    for key, value in results.items():
        print(f"{key}: {value:.4f}" if isinstance(
            value, float) else f"{key}: {value}")


if __name__ == "__main__":
    main()
