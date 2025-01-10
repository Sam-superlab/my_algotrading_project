from src.backtest import Backtester
from src.models import TradingModel
from src.feature_engineering import FeatureEngineer
from src.data_loader import DataLoader
from src.strategies.hamiltonian_strategy import HamiltonianStrategy
from src.strategies.strategy_factory import StrategyFactory
from flask import Flask, render_template, request, jsonify
import pandas as pd
import sys
import os

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)


app = Flask(__name__)


@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')


@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    """Fetch stock data from Yahoo Finance"""
    try:
        data = request.json
        symbol = data['symbol']
        start_date = data['start_date']
        end_date = data['end_date']

        strategy = HamiltonianStrategy(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )

        df = strategy.fetch_data()
        return jsonify({'message': 'Data fetched successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/run_strategy', methods=['POST'])
def run_strategy():
    """Run the selected trading strategy"""
    try:
        params = request.json
        print(f"Received parameters: {params}")

        strategy = StrategyFactory.create_strategy(
            strategy_type=params['strategy_type'],
            params=params
        )

        print("Fetching data...")
        df = strategy.fetch_data()

        # Get original stock data for comparison
        stock_data = {
            'dates': df.index.strftime('%Y-%m-%d').tolist(),
            'prices': df['Close'].values.tolist(),
            'volume': df['Volume'].values.tolist()
        }

        print("Running backtest...")
        portfolio = strategy.backtest(
            initial_capital=params['initial_capital'])

        metrics = strategy.calculate_metrics()
        print(f"Metrics calculated: {metrics}")

        results = {
            'equity_curve': portfolio['Portfolio_Value'].values.tolist(),
            'dates': portfolio.index.strftime('%Y-%m-%d').tolist(),
            'prices': strategy.data['Close'].values.tolist(),
            'buy_dates': portfolio[portfolio['Position'] == 1].index.strftime('%Y-%m-%d').tolist(),
            'buy_prices': strategy.data.loc[portfolio[portfolio['Position'] == 1].index, 'Close'].values.tolist(),
            'sell_dates': portfolio[portfolio['Position'] == -1].index.strftime('%Y-%m-%d').tolist(),
            'sell_prices': strategy.data.loc[portfolio[portfolio['Position'] == -1].index, 'Close'].values.tolist(),
            'stock_data': stock_data,  # Add original stock data
            'metrics': {
                'Total Return': float(metrics['Total Return']),
                'Annual Return': float(metrics['Annual Return']),
                'Volatility': float(metrics['Volatility']),
                'Sharpe Ratio': float(metrics['Sharpe Ratio']),
                'Max Drawdown': float(metrics['Max Drawdown'])
            }
        }

        return jsonify(results)

    except Exception as e:
        print(f"Error in run_strategy: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
