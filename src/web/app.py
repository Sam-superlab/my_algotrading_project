from src.backtest import Backtester
from src.models import TradingModel
from src.feature_engineering import FeatureEngineer
from src.data_loader import DataLoader
from flask import Flask, render_template, request, jsonify
import pandas as pd
import sys
import os

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

# Configure data directories
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')

# Create directories if they don't exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)


app = Flask(__name__)

# Initialize components
data_loader = DataLoader()
feature_engineer = FeatureEngineer()
trading_model = TradingModel()


@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_data():
    """Handle data file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save uploaded file with full path
    file_path = os.path.join(RAW_DATA_DIR, file.filename)
    file.save(file_path)

    return jsonify({'message': 'File uploaded successfully'})


@app.route('/backtest', methods=['POST'])
def run_backtest():
    """Run backtest with current configuration"""
    try:
        # Load and process data
        df = data_loader.load_market_data(request.form['filename'])
        if df is None:
            return jsonify({'error': 'Failed to load data'}), 400

        # Generate features
        df = feature_engineer.calculate_technical_indicators(df)

        # Train model and get predictions
        X, y = trading_model.prepare_data(df)
        trading_model.train(X, y)
        predictions = trading_model.predict(X)

        # Run backtest
        backtester = Backtester(data_loader.config)
        results = backtester.run(df, predictions)

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
