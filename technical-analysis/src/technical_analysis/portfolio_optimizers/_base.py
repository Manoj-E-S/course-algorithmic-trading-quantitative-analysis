from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generator

import pandas as pd
from technical_analysis.config.risk_free_rate_config import GlobalRiskFreeRateConfig
from technical_analysis.models.instrument_universe import InstrumentUniverse


@dataclass(kw_only=True)
class OptimizerConfig:
    # User facing configuration
    """
    Config for portfolio optimizers.

    :Fields:
    - risk_free_rate: float (default - global risk-free rate)
    """
    risk_free_rate: float = field(default_factory=GlobalRiskFreeRateConfig.get)


@dataclass(kw_only=True)
class _OptimizerResolvedConfig(OptimizerConfig):
    # Internally used configuration
    """
    Internal resolved config for portfolio optimizers.

    Extends :class:`OptimizerConfig`

    :Fields:
    - universe: InstrumentUniverse
    - number_of_holdings: int
    - start_date: pd.Timestamp
    - end_date: pd.Timestamp
    - in_precomputed_mode: bool
    - risk_free_rate: float (default - global risk-free rate)
    """
    universe: InstrumentUniverse
    number_of_holdings: int
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    in_precomputed_mode: bool


class Optimizer(ABC):
    """
    Abstract base class for portfolio optimizers.
    """

    def __init__(self):
        raise NotImplementedError("This class is abstract and cannot be instantiated directly. Please use a subclass.")


    @abstractmethod
    def init_current_holdings_kpis(self) -> pd.DataFrame:
        pass


    @abstractmethod
    def update_current_holdings_kpis(self, current_holdings_kpis: pd.DataFrame) -> pd.DataFrame:
        pass


    @abstractmethod
    def init_history(self, current_holdings_kpis: pd.DataFrame) -> pd.DataFrame:
        pass


    @abstractmethod
    def append_to_history(self, history: pd.DataFrame, current_holdings_kpis: pd.DataFrame) -> pd.DataFrame:
        pass


    @abstractmethod
    def precompute(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        pass


    @abstractmethod
    def optimize(
        self,
        current_holdings_kpis: pd.DataFrame,
        history: pd.DataFrame
    ) -> Generator[tuple[pd.Timestamp, pd.DataFrame, pd.DataFrame], None, None]:
        pass