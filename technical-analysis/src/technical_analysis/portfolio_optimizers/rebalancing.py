from dataclasses import dataclass, field

import pandas as pd

from technical_analysis.config.risk_free_rate_config import GlobalRiskFreeRateConfig
from technical_analysis.enums.kpi import KPIEnum
from technical_analysis.models.instrument_universe import InstrumentUniverse
from technical_analysis.portfolio_optimizers.base import _DefaultResolvedOptimizerConfig, BaseOptimizer, DefaultOptimizerConfig
from technical_analysis.utils.dataframe_date_helper import DataFrameDateIndexHelper
from technical_analysis.utils.decorators import override


@dataclass
class RebalancingOptimizerConfig:
    # User facing configuration
    """
    Config for Rebalancing optimization strategy.

    Fields:
    - number_of_replacements: int
    - allow_repeated_replacements: bool (default - True)
    - risk_free_rate: float (default - global risk-free rate)
    """
    number_of_replacements: int
    allow_repeated_replacements: bool = field(default_factory=lambda: True)
    risk_free_rate: float = field(default_factory=GlobalRiskFreeRateConfig.get)


@dataclass
class _RebalancingResolvedOptimizerConfig:
    # Internally used configuration
    """
    Internal resolved config for Rebalancing optimization strategy.

    Fields:
    - universe: InstrumentUniverse
    - number_of_holdings: int
    - start_date: pd.Timestamp
    - end_date: pd.Timestamp
    - number_of_replacements: int
    - allow_repeated_replacements: bool (default - True)
    - risk_free_rate: float (default - global risk-free rate)
    """
    universe: InstrumentUniverse
    number_of_holdings: int
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    number_of_replacements: int
    allow_repeated_replacements: bool = field(default_factory=lambda: True)
    risk_free_rate: float = field(default_factory=GlobalRiskFreeRateConfig.get)
    
    def __post_init__(self):
        # Ensure that the number of replacements does not exceed the number of holdings
        if self.number_of_replacements > self.number_of_holdings:
            raise ValueError("Number of replacements cannot be greater than the number of holdings.")


class RebalancingOptimizer(BaseOptimizer):
    """
    This class implements the rebalancing portfolio optimization strategy.

    Strategy:
    - Start with the best n instruments in the universe (n = number of holdings in the portfolio)
    - Replace x worst performing holdings in the portfolio with the x so-far best-performing instruments in the universe. (x = number of replacements)
    - Replacement happens for every period
    """
    
    def __init__(
        self,
        config: _RebalancingResolvedOptimizerConfig
    ):
        self.__config = config


    @property
    def config(self) -> _RebalancingResolvedOptimizerConfig:
        return self.__config
    

    @override
    def init_holdings_v_kpis(self) -> pd.DataFrame:
        """
        Initializes the holdings with their KPIs as a DataFrame as per the rebalancing strategy.

        :return pd.DataFrame: The holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        """
        return self.__config.universe.instruments_sorted_by_kpi_for_date_snapshot(
            by_which_kpi=KPIEnum.CAGR,
            overall_start_date=self.__config.start_date,
            snapshot_date=self.__config.end_date,
            risk_free_rate_for_sharpe_and_sortino=self.__config.risk_free_rate,
            ascending=False,
            top_n=self.__config.number_of_holdings
        )

    
    @override
    def update_holdings_v_kpis(self, current_holdings_v_kpis: pd.DataFrame) -> pd.DataFrame:
        """
        Updates the current holdings with their KPIs as a DataFrame as per the rebalancing strategy.

        :param current_holdings_v_kpis: The current holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        :type current_holdings_v_kpis: pd.DataFrame

        :return pd.DataFrame: The holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        """
        current_holdings_v_kpis = (
            self.__config.universe.instruments_sorted_by_kpi_for_date_snapshot(
                by_which_kpi=KPIEnum.CAGR,
                overall_start_date=self.__config.start_date,
                snapshot_date=self.__config.end_date,
                risk_free_rate_for_sharpe_and_sortino=self.__config.risk_free_rate,
                ascending=False
            )
            .loc[current_holdings_v_kpis.index]
        )

        current_holdings_v_kpis = self.__remove_underperforming_instruments(current_holdings_v_kpis)
        possible_replacements = self.__config.universe.instruments_sorted_by_kpi_for_date_snapshot(
            by_which_kpi=KPIEnum.CAGR,
            overall_start_date=self.__config.start_date,
            snapshot_date=self.__config.end_date,
            risk_free_rate_for_sharpe_and_sortino=self.__config.risk_free_rate,
            ascending=False
        )


        if self.__config.allow_repeated_replacements:
            top_possible_replacements = possible_replacements.head(self.__config.number_of_replacements)
            
            common_holdings = current_holdings_v_kpis.index.intersection(top_possible_replacements.index)
            new_holdings = top_possible_replacements.index.difference(current_holdings_v_kpis.index)

            if common_holdings.empty:
                return pd.concat([current_holdings_v_kpis, top_possible_replacements], axis=0).sort_values(KPIEnum.CAGR.value, ascending=False)
            
            updated_holdings = current_holdings_v_kpis.copy()
            updated_holdings.loc[common_holdings, InstrumentUniverse._Number_Of_Holdings_Column_Name] += top_possible_replacements.loc[common_holdings, InstrumentUniverse._Number_Of_Holdings_Column_Name]
            
            if new_holdings.empty:
                return updated_holdings.sort_values(KPIEnum.CAGR.value, ascending=False)
            
            return (
                pd.concat(
                    [updated_holdings, top_possible_replacements.loc[new_holdings]],
                    axis=0
                )
                .sort_values(
                    KPIEnum.CAGR.value,
                    ascending=False
                )
            )

        top_possible_replacements = (
            possible_replacements
            .drop(axis=0, labels=current_holdings_v_kpis.index, errors='ignore')
            # .loc[~possible_replacements.index.isin(current_holdings_v_kpis.index)]
            # .sort_values(KPIEnum.CAGR.value, ascending=False)
            .head(self.__config.number_of_replacements)
        )
        return (
            pd.concat(
                [current_holdings_v_kpis, top_possible_replacements],
                axis=0
            ).sort_values(
                KPIEnum.CAGR.value,
                ascending=False
            )
        )

    @override
    def precomputed_holdings_v_kpis(self, holdings_history: pd.DataFrame) -> pd.DataFrame:
        """
        Updates the current holdings with their KPIs as a DataFrame as per the default strategy.

        :param holdings_history: The historical holdings with their KPIs as a DataFrame. Index is (date, symbol), and the columns are the KPI values.
        :type holdings_history: pd.DataFrame

        :return pd.DataFrame: The holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        """
        return super().precomputed_holdings_v_kpis(holdings_history)
    

    @override
    def precomputed_history(self) -> pd.DataFrame:
        """
        Precomputes the history of KPIs based on the rebalancing strategy.

        :return pd.DataFrame: The precomputed history of the portfolio, sorted by CAGR. Multi-Index - (date, symbol), columns - KPIs.
        """
        return self.__config.universe.instrument_history_sorted_by_kpi_per_date_for_date_range(
            by_which_kpi=KPIEnum.CAGR,
            period_start_date=self.__config.start_date,
            period_end_date=self.__config.end_date,
            ascending=False,
            risk_free_rate_for_sharpe_and_sortino=self.__config.risk_free_rate,
            top_n=self.__config.number_of_holdings
        )
    

    @override
    def optimize(self, current_holdings_v_kpis: pd.DataFrame) -> tuple[pd.Timestamp, pd.DataFrame]:
        """
        Optimizes the portfolio based on the rebalancing strategy.

        :param current_holdings_v_kpis: The current holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        :type current_holdings_v_kpis: pd.DataFrame

        :return tuple[pd.Timestamp, pd.DataFrame]: A tuple with the last optimized date and a DataFrame of the optimized holdings and their KPIs as of that date.
        """
        try:
            end_date = DataFrameDateIndexHelper.next_date(
                df_with_datetime_index=self.__config.universe.closes_df,
                date=self.__config.end_date
            )
        except IndexError:
            print("[WARNING] There are no more dates available in the universe to optimize the portfolio. Skipping optimization.")
            return self.__config.end_date, self.update_holdings_v_kpis(current_holdings_v_kpis)

        self.__config.end_date = end_date
        return self.__config.end_date, self.update_holdings_v_kpis(current_holdings_v_kpis)
    

    # Private Methods
    def __remove_underperforming_instruments(self, current_holdings_v_kpis: pd.DataFrame) -> pd.DataFrame:
        """
        Removes `number_of_replacements` underperforming instruments from the current holdings.

        :param current_holdings_v_kpis: The current holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        :type current_holdings_v_kpis: pd.DataFrame

        :return pd.DataFrame: The holdings with their KPIs as a pd.DataFrame, with `number_of_replacements` underperforming instruments removed
        """
        n: int = self.__config.number_of_holdings - self.__config.number_of_replacements
        return current_holdings_v_kpis.nlargest(n, KPIEnum.CAGR.value)