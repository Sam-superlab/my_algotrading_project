from typing import Dict, Any
from .hamiltonian_strategy import HamiltonianStrategy
from .momentum_strategy import MomentumStrategy
from .mean_reversion import MeanReversionStrategy


class StrategyFactory:
    @staticmethod
    def create_strategy(strategy_type: str, params: Dict[str, Any]):
        try:
            if strategy_type == 'hamiltonian':
                return HamiltonianStrategy(
                    symbol=params['symbol'],
                    start_date=params['start_date'],
                    end_date=params['end_date'],
                    damping=params.get('damping', 0.15),
                    external_influence=params.get('external_influence', 0.4),
                    friction=params.get('friction', 0.03),
                    price_threshold=params.get('price_threshold', 0.02)
                )
            elif strategy_type == 'momentum':
                return MomentumStrategy(
                    symbol=params['symbol'],
                    start_date=params['start_date'],
                    end_date=params['end_date'],
                    lookback_period=params.get('lookback_period', 20),
                    threshold=params.get('threshold', 0)
                )
            elif strategy_type == 'meanReversion':
                return MeanReversionStrategy(
                    symbol=params['symbol'],
                    start_date=params['start_date'],
                    end_date=params['end_date'],
                    window=params.get('window', 20),
                    std_dev=params.get('std_dev', 2.0)
                )
            else:
                raise ValueError(f"Unknown strategy type: {strategy_type}")
        except Exception as e:
            raise Exception(f"Error creating strategy: {str(e)}")
