# Algorithmic Trading System

A comprehensive algorithmic trading platform that supports both financial markets and sports betting, featuring a web-based interface for data analysis, backtesting, and strategy execution.

## Features

### Data Processing
- Support for market data in CSV format (OHLCV data)
- Automated data preprocessing and cleaning
- Real-time data validation

### Technical Analysis
- Multiple technical indicators:
  - Moving Averages (MA)
  - Relative Strength Index (RSI)
  - Moving Average Convergence Divergence (MACD)
- Custom indicator development capability

### Machine Learning Models
- Random Forest classifier for market prediction
- Extensible model architecture
- Built-in train/test split functionality
- Model performance metrics

### Risk Management
- Position sizing using Kelly Criterion
- Stop-loss and take-profit functionality
- Portfolio value tracking
- Maximum drawdown monitoring

### Backtesting Engine
- Historical performance simulation
- Trade-by-trade analysis
- Performance metrics:
  - Total return
  - Win rate
  - Maximum drawdown
  - Trade statistics

### Web Interface
- Interactive dashboard
- Data upload functionality
- Real-time configuration adjustments
- Visual performance analytics
- Equity curve visualization

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/algorithmic-trading-system.git
cd algorithmic-trading-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the web application:
```bash
python run.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Upload your market data CSV file with the following format:
```csv
date,open,high,low,close,volume
2024-01-01,100.0,101.5,99.0,100.5,1000000
```

4. Configure your trading parameters:
   - Initial capital
   - Stop-loss percentage
   - Take-profit percentage

5. View backtest results and performance metrics

## Project Structure

```
algorithmic-trading-system/
├── data/                # Data storage
│   ├── raw/            # Original market data
│   └── processed/      # Processed datasets
├── src/                # Source code
│   ├── data_loader.py  # Data loading and preprocessing
│   ├── feature_engineering.py  # Technical indicators
│   ├── models.py       # Machine learning models
│   ├── backtest.py     # Backtesting engine
│   ├── risk_manager.py # Risk management
│   └── web/           # Web interface
├── tests/              # Unit tests
├── requirements.txt    # Dependencies
└── run.py             # Application entry point
```

## Configuration

Adjust trading parameters in `config/settings.yaml`:
```yaml
data:
  path: "data/raw"
  market_data_file: "market_data.csv"

model:
  type: "random_forest"
  n_estimators: 100
  max_depth: 10

backtest:
  initial_capital: 100000
  position_size: 0.1
  stop_loss: 0.02
  take_profit: 0.05
```

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New Features
1. Create a feature branch
2. Implement your changes
3. Add tests
4. Submit a pull request

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

## Acknowledgments

- Thanks to all contributors
- Inspired by various open-source trading projects
