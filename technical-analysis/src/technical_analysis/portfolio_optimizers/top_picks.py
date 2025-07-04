from dataclasses import dataclass, field

import pandas as pd

from technical_analysis.enums.kpi import KPIEnum
from technical_analysis.portfolio_optimizers._base import _OptimizerResolvedConfig, Optimizer, OptimizerConfig
from technical_analysis.portfolio_optimizers.mixins.optimization import OptimizationMixin
from technical_analysis.portfolio_optimizers.mixins.optimization_history import OptimizationHistoryMixin
from technical_analysis.utils.decorators import override


@dataclass(kw_only=True)
class TopPicksOptimizerConfig(OptimizerConfig):
    # User facing configuration
    """
    Config for Top Picks optimization strategy.

    Extends :class:`OptimizerConfig`.

    :Fields:
    - risk_free_rate: float (default - global risk-free rate)
    """
    pass


@dataclass(kw_only=True)
class _TopPicksResolvedOptimizerConfig(_OptimizerResolvedConfig, TopPicksOptimizerConfig):
    # Internally used configuration
    """
    Internal resolved config for Top Picks optimization strategy.

    Extends :class:`_OptimizerResolvedConfig` and :class:`TopPicksOptimizerConfig`.

    :Fields:
    - universe: InstrumentUniverse
    - number_of_holdings: int
    - start_date: pd.Timestamp
    - end_date: pd.Timestamp
    - in_precomputed_mode: bool
    - risk_free_rate: float (default - global risk-free rate)
    """
    pass


class TopPicksOptimizer(OptimizationHistoryMixin, OptimizationMixin, Optimizer):
    """
    This is the portfolio optimizer that implements the Top Picks strategy.

    Strategy:
    - Start with the best `n` instruments in the universe `(n = number of holdings in the portfolio)`
    - Replaces all `n` holdings, with the so-far best-performing (top) `n` instruments of the universe
    - Replacement happens for every period
    """

    def __init__(
        self,
        config: _TopPicksResolvedOptimizerConfig
    ):
        self._config = config


    @property
    def config(self) -> _TopPicksResolvedOptimizerConfig:
        """
        Returns the configuration of the Top Picks optimizer.

        :return: The configuration of the Top Picks optimizer.
        :rtype: _TopPicksResolvedOptimizerConfig
        """
        return self._config
    

    @override
    def init_current_holdings_kpis(self) -> pd.DataFrame:
        """
        Initializes the holdings with their KPIs as a DataFrame as per the default strategy.

        :return pd.DataFrame: The holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        """
        return self._config.universe.sorted_kpi_snapshot(
            sort_by=KPIEnum.CAGR,
            overall_start_date=self._config.start_date,
            snapshot_date=self._config.end_date,
            rf_sharpe_sortino=self._config.risk_free_rate,
            ascending=False,
            top_n=self._config.number_of_holdings
        )
    

    @override
    def update_current_holdings_kpis(self, current_holdings_kpis: pd.DataFrame) -> pd.DataFrame:
        """
        Updates the current holdings with their KPIs as a DataFrame as per the default strategy.

        :param current_holdings_kpis: The current holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        :type current_holdings_kpis: pd.DataFrame

        :return pd.DataFrame: The holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        """
        return self.init_current_holdings_kpis()
    

    @override
    def precompute(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Precomputes the holdings and history dataframes.

        :return: A tuple containing the precomputed holdings and history dataframes.
        :rtype: tuple[pd.DataFrame, pd.DataFrame]
        """
        history: pd.DataFrame = self.__precomputed_history()
        current_holdings_kpis: pd.DataFrame = self.__precomputed_current_holdings_kpis(history)
        
        return (
            current_holdings_kpis,
            history
        )


    # Private methods
    def __precomputed_current_holdings_kpis(self, holdings_history: pd.DataFrame) -> pd.DataFrame:
        """
        Updates the current holdings with their KPIs as a DataFrame as per the default strategy.

        :param holdings_history: The historical holdings with their KPIs as a DataFrame. Index is (date, symbol), and the columns are the KPI values.
        :type holdings_history: pd.DataFrame

        :return pd.DataFrame: The holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        """
        return (
            holdings_history
            .sort_index(
                level='date',
                ascending=True
            )
            .loc[holdings_history.index.get_level_values('date')[-1], :]
            .sort_values(
                by=KPIEnum.CAGR.value,
                ascending=False
            )
        )


    def __precomputed_history(self) -> pd.DataFrame:
        """
        Precomputes the history of KPIs based on the default strategy.

        :return pd.DataFrame: The precomputed history of the portfolio, sorted by CAGR. Multi-Index - (date, symbol), columns - KPIs.
        """
        return self._config.universe.sorted_kpi_history(
            sort_by=KPIEnum.CAGR,
            period_start_date=self._config.start_date,
            period_end_date=self._config.end_date,
            ascending=False,
            rf_sharpe_sortino=self._config.risk_free_rate,
            top_n=self._config.number_of_holdings
        )