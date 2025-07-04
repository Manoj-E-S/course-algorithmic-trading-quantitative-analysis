from dataclasses import dataclass, field

import pandas as pd

from technical_analysis.enums.kpi import KPIEnum
from technical_analysis.models.instrument_universe import InstrumentUniverse
from technical_analysis.portfolio_optimizers._base import Optimizer
from technical_analysis.portfolio_optimizers.mixins.optimization import OptimizationMixin
from technical_analysis.portfolio_optimizers.mixins.optimization_history import OptimizationHistoryMixin
from technical_analysis.portfolio_optimizers.top_picks import _OptimizerResolvedConfig, OptimizerConfig
from technical_analysis.utils.decorators import override


@dataclass(kw_only=True)
class RebalancingOptimizerConfig(OptimizerConfig):
    # User facing configuration
    """
    Config for Rebalancing optimization strategy.

    Extends :class:`OptimizerConfig`.

    :Fields:
    - number_of_replacements: int
    - allow_repeated_replacements: bool (default - True)
    - risk_free_rate: float (default - global risk-free rate)
    """
    number_of_replacements: int
    allow_repeated_replacements: bool = field(default=True)


@dataclass(kw_only=True)
class _RebalancingResolvedOptimizerConfig(_OptimizerResolvedConfig, RebalancingOptimizerConfig):
    # Internally used configuration
    """
    Internal resolved config for Rebalancing optimization strategy.

    Extends :class:`_OptimizerResolvedConfig` and :class:`RebalancingOptimizerConfig`.

    :Fields:
    - universe: InstrumentUniverse
    - number_of_holdings: int
    - start_date: pd.Timestamp
    - end_date: pd.Timestamp
    - in_precomputed_mode: bool
    - number_of_replacements: int
    - allow_repeated_replacements: bool (default - True)
    - risk_free_rate: float (default - global risk-free rate)
    """
    
    def __post_init__(self):
        # Ensure that the number of replacements does not exceed the number of holdings
        if self.number_of_replacements > self.number_of_holdings:
            raise ValueError("Number of replacements cannot be greater than the number of holdings.")


class RebalancingOptimizer(OptimizationHistoryMixin, OptimizationMixin, Optimizer):
    """
    This is the portfolio optimizer that implements the Rebalancing strategy.

    Strategy:
    - Start with the best `n` instruments in the universe `(n = number of holdings in the portfolio)`
    - Replace `x` worst performing holdings in the portfolio with the `x` so-far best-performing instruments in the universe. `(x = number of replacements)`
    - Replacement happens for every period
    """
    

    def __init__(
        self,
        config: _RebalancingResolvedOptimizerConfig
    ):
        self._config = config


    @property
    def config(self) -> _RebalancingResolvedOptimizerConfig:
        """
        Returns the configuration of the Rebalancing optimizer.

        :return: The configuration of the Rebalancing optimizer.
        :rtype: _RebalancingResolvedOptimizerConfig
        """
        return self._config


    @override
    def init_current_holdings_kpis(self) -> pd.DataFrame:
        """
        Initializes the holdings with their KPIs as a DataFrame as per the rebalancing strategy.

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
        Updates the current holdings with their KPIs as a DataFrame as per the rebalancing strategy.

        :param current_holdings_kpis: The current holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        :type current_holdings_kpis: pd.DataFrame

        :return pd.DataFrame: The holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        """
        latest_synced_holdings = self.__sync_current_holdings_kpis_to_latest(current_holdings_kpis)
        retained_holdings = self.__remove_underperforming_instruments(latest_synced_holdings)
        possible_replacements = self.__get_possible_replacements()

        if self._config.allow_repeated_replacements:
            return self.__replace_with_repeats(retained_holdings, possible_replacements)
        else:
            return self.__replace_without_repeats(retained_holdings, possible_replacements)
    

    @override
    def precompute(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Precomputes the holdings and history dataframes.

        :return: A tuple containing the precomputed holdings and history dataframes.
        :rtype: tuple[pd.DataFrame, pd.DataFrame]
        """
        current_holdings_kpis: pd.DataFrame = self.init_current_holdings_kpis()
        history: pd.DataFrame = self.init_history(current_holdings_kpis)
        
        for _, current_holdings_kpis_, history_ in self.optimize(current_holdings_kpis, history):
            current_holdings_kpis = current_holdings_kpis_
            history = history_

        return (
            current_holdings_kpis,
            history
        )


    # Private Methods
    def __remove_underperforming_instruments(self, current_holdings_kpis: pd.DataFrame) -> pd.DataFrame:
        """
        Removes `number_of_replacements` underperforming instruments from the current holdings.

        :param current_holdings_kpis: The current holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        :type current_holdings_kpis: pd.DataFrame

        :return pd.DataFrame: The holdings with their KPIs as a pd.DataFrame, with `number_of_replacements` underperforming instruments removed
        """
        n: int = self._config.number_of_holdings - self._config.number_of_replacements
        return current_holdings_kpis.nlargest(n, KPIEnum.CAGR.value)
    

    def __sync_current_holdings_kpis_to_latest(self, current_holdings_kpis: pd.DataFrame) -> pd.DataFrame:
        """Update KPIs for current holdings as of the latest snapshot date."""
        all_kpis = self._config.universe.sorted_kpi_snapshot(
            sort_by=KPIEnum.CAGR,
            overall_start_date=self._config.start_date,
            snapshot_date=self._config.end_date,
            rf_sharpe_sortino=self._config.risk_free_rate,
            ascending=False
        )
        return all_kpis.loc[current_holdings_kpis.index]


    def __get_possible_replacements(self) -> pd.DataFrame:
        """Get all instruments sorted by KPI for the current snapshot date."""
        return self._config.universe.sorted_kpi_snapshot(
            sort_by=KPIEnum.CAGR,
            overall_start_date=self._config.start_date,
            snapshot_date=self._config.end_date,
            rf_sharpe_sortino=self._config.risk_free_rate,
            ascending=False
        )


    def __replace_with_repeats(self, retained_holdings: pd.DataFrame, possible_replacements: pd.DataFrame) -> pd.DataFrame:
        """Replace underperformers, allowing repeated replacements."""
        top_replacements = possible_replacements.head(self._config.number_of_replacements)
        common = retained_holdings.index.intersection(top_replacements.index)
        new = top_replacements.index.difference(retained_holdings.index)

        updated = retained_holdings.copy()
        
        if not common.empty:
            updated.loc[common, InstrumentUniverse._Number_Of_Holdings_Column_Name] += top_replacements.loc[common, InstrumentUniverse._Number_Of_Holdings_Column_Name]
        
        if not new.empty:
            updated = pd.concat([updated, top_replacements.loc[new]], axis=0)

        return updated.sort_values(KPIEnum.CAGR.value, ascending=False)


    def __replace_without_repeats(self, retained_holdings: pd.DataFrame, possible_replacements: pd.DataFrame) -> pd.DataFrame:
        """Replace underperformers, not allowing repeated replacements."""
        replacements = possible_replacements.drop(axis=0, labels=retained_holdings.index).head(self._config.number_of_replacements)
        return pd.concat([retained_holdings, replacements], axis=0).sort_values(KPIEnum.CAGR.value, ascending=False)