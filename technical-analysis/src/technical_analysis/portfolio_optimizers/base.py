from dataclasses import dataclass, field

import pandas as pd

from technical_analysis.config.risk_free_rate_config import GlobalRiskFreeRateConfig
from technical_analysis.enums.kpi import KPIEnum
from technical_analysis.models.instrument_universe import InstrumentUniverse
from technical_analysis.utils.dataframe_date_helper import DataFrameDateIndexHelper
from technical_analysis.utils.decorators import optionally_overridable


@dataclass
class DefaultOptimizerConfig:
    # User facing configuration
    """
    Config for Default optimization strategy.

    :Fields:
    - risk_free_rate: float (default - global risk-free rate)
    """
    risk_free_rate: float = field(default_factory=GlobalRiskFreeRateConfig.get)


@dataclass
class _DefaultResolvedOptimizerConfig:
    # Internally used configuration
    """
    Internal resolved config for Default optimization strategy.

    Fields:
    - universe: InstrumentUniverse
    - number_of_holdings: int
    - start_date: pd.Timestamp
    - end_date: pd.Timestamp
    - risk_free_rate: float (default - global risk-free rate)
    """
    universe: InstrumentUniverse
    number_of_holdings: int
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    risk_free_rate: float = field(default_factory=GlobalRiskFreeRateConfig.get)


class BaseOptimizer:
    """
    Base class for all portfolio optimizers.
    This is the default portfolio optimizer that implements a simple replacement strategy (default strategy).

    Strategy:
    - Start with the best n instruments in the universe (n = number of holdings in the portfolio)
    - Replaces all n holdings, to pick the so-far best-performing n instruments of the universe
    - Replacement happens for every period
    """

    def __init__(
        self,
        config: _DefaultResolvedOptimizerConfig
    ):
        self.__config = config


    @property
    def config(self) -> _DefaultResolvedOptimizerConfig:
        return self.__config

    
    @optionally_overridable
    def init_holdings_v_kpis(self) -> pd.DataFrame:
        """
        Initializes the holdings with their KPIs as a DataFrame as per the default strategy.

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
    

    @optionally_overridable
    def update_holdings_v_kpis(self, current_holdings_v_kpis: pd.DataFrame) -> pd.DataFrame:
        """
        Updates the current holdings with their KPIs as a DataFrame as per the default strategy.

        :param current_holdings_v_kpis: The current holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        :type current_holdings_v_kpis: pd.DataFrame

        :return pd.DataFrame: The holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        """
        return self.init_holdings_v_kpis()
    

    @optionally_overridable
    def precomputed_holdings_v_kpis(self, holdings_history: pd.DataFrame) -> pd.DataFrame:
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


    @optionally_overridable
    def precomputed_history(self) -> pd.DataFrame:
        """
        Precomputes the history of KPIs based on the default strategy.

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
    

    @optionally_overridable
    def optimize(self, current_holdings_v_kpis: pd.DataFrame) -> tuple[pd.Timestamp, pd.DataFrame]:
        """
        Optimizes the portfolio based on the default strategy.

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