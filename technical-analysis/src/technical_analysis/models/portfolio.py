from datetime import datetime
from typing import Iterator, Literal

import pandas as pd

from technical_analysis.config.risk_free_rate_config import GlobalRiskFreeRateConfig
from technical_analysis.enums.kpi import KPIEnum
from technical_analysis.enums.portfolio_optimization_strategy import PortfolioOptimizationStrategy
from technical_analysis.models.instrument import Instrument
from technical_analysis.models.instrument_universe import InstrumentUniverse
from technical_analysis.utils.dataframe_date_helper import DataFrameDateIndexHelper


class Portfolio:
    """
    A class that represents a portfolio of financial instruments.
    """

    def __init__(
        self,
        number_of_holdings: int,
        source_universe: InstrumentUniverse,
        optimization_strategy: PortfolioOptimizationStrategy = PortfolioOptimizationStrategy.REBALANCING,
        start_date: datetime | Literal['earliest'] = 'earliest',
        end_date: datetime | Literal['latest'] = 'latest',
        risk_free_rate: float | None = None
    ):
        if risk_free_rate is None:
            risk_free_rate = GlobalRiskFreeRateConfig.get()
        
        self.__universe: InstrumentUniverse = source_universe
        self.__number_of_holdings: int = number_of_holdings
        self.__optimization_strategy: PortfolioOptimizationStrategy = optimization_strategy
        self.__risk_free_rate: float = risk_free_rate

        available_dates: pd.DatetimeIndex = self.__available_dates(
            start_date=None if start_date == 'earliest' else pd.Timestamp(start_date),
            end_date=None if end_date == 'latest' else pd.Timestamp(end_date)
        )

        self.__start_date: pd.Timestamp = available_dates[0]
        self.__end_date: pd.Timestamp = available_dates[-1]

        self.__holdings_v_kpis: pd.DataFrame = self.__compute_holdings_v_kpis()
        self.__history: pd.DataFrame = self.__compute_history()


    # Getters
    @property
    def optimization_strategy(self) -> PortfolioOptimizationStrategy:
        return self.__optimization_strategy

    @property
    def number_of_holdings(self) -> int:
        return self.__number_of_holdings

    @property
    def universe(self) -> InstrumentUniverse:
        return self.__universe

    @property
    def start_date(self) -> pd.Timestamp:
        return self.__start_date

    @property
    def end_date(self) -> pd.Timestamp:
        return self.__end_date

    @property
    def current_holdings(self) -> list[str]:
        return list(self.__holdings_v_kpis.index)
    
    @property
    def current_holdings_v_kpis(self) -> pd.DataFrame:
        return self.__holdings_v_kpis
    
    @property
    def holding_history(self) -> pd.DataFrame:
        return self.__history
    
    @property
    def risk_free_rate(self) -> float:
        return self.__risk_free_rate


    # Chainable Setters
    @optimization_strategy.setter
    def optimization_strategy(self, optimization_strategy: PortfolioOptimizationStrategy) -> 'Portfolio':
        if self.__optimization_strategy != optimization_strategy:
            self.__optimization_strategy = optimization_strategy
            self.__after_property_update()

        return self
    
    @number_of_holdings.setter
    def number_of_holdings(self, number_of_holdings: int) -> 'Portfolio':
        if self.__number_of_holdings != number_of_holdings:
            self.__number_of_holdings = number_of_holdings
            self.__after_property_update()
        return self
    

    @start_date.setter
    def start_date(self, start_date: datetime | Literal['earliest']) -> 'Portfolio':
        if self.__start_date != start_date:
            start_date = self.__available_dates(
                start_date=None if start_date == 'earliest' else pd.Timestamp(start_date),
                end_date=self.__end_date
            )[0]
            self.__start_date = start_date
            self.__after_property_update()
        return self
    

    @end_date.setter
    def end_date(self, end_date: datetime | Literal['latest']) -> 'Portfolio':
        if self.__end_date != end_date:
            end_date = self.__available_dates(
                start_date=self.__start_date,
                end_date=None if end_date == 'latest' else pd.Timestamp(end_date)
            )[-1]
            self.__end_date = end_date
            self.__after_property_update()
        return self
    

    @risk_free_rate.setter
    def risk_free_rate(self, risk_free_rate: float) -> 'Portfolio':
        if self.__risk_free_rate != risk_free_rate:
            self.__risk_free_rate = risk_free_rate
            self.__after_property_update()
        return self
    

    # Private methods
    def __compute_holdings_v_kpis(self) -> pd.DataFrame:
        """
        Returns the current holdings with their KPIs as a DataFrame.
        The index is the instrument symbol, and the columns are the KPI values.
        """
        if self.__optimization_strategy == PortfolioOptimizationStrategy.REBALANCING:
            return self.__universe.instruments_sorted_by_kpi_for_date_snapshot(
                by_which_kpi=KPIEnum.CAGR,
                overall_start_date=self.__start_date,
                snapshot_date=self.__end_date,
                risk_free_rate_for_sharpe_and_sortino=self.__risk_free_rate,
                ascending=False,
                top_n=self.__number_of_holdings
            )
        else:
            raise NotImplementedError(f"Optimization strategy {self.__optimization_strategy} is not implemented.")
        
    
    def __compute_history(self) -> pd.DataFrame:
        """
        Returns the portfolio history as a DataFrame.
        The indices are (date, instrument_symbol) and the columns are the KPIs.
        """
        if self.__optimization_strategy == PortfolioOptimizationStrategy.REBALANCING:
            return self.__universe.instrument_history_sorted_by_kpi_per_date_for_date_range(
                by_which_kpi=KPIEnum.CAGR,
                period_start_date=self.__start_date,
                period_end_date=self.__end_date,
                ascending=False,
                risk_free_rate_for_sharpe_and_sortino=self.__risk_free_rate,
                top_n=self.__number_of_holdings
            )
        else:
            raise NotImplementedError(f"Optimization strategy {self.__optimization_strategy} is not implemented.")
    

    def __available_dates(
        self,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None
    ) -> pd.DatetimeIndex:
        """
        Returns a DatetimeIndex of available dates in the universe.

        :param start_date: The start date of the range. If None, uses the earliest date.
        :type start_date: pd.Timestamp

        :param end_date: The end date of the range. If None, uses the latest date.
        :type end_date: pd.Timestamp

        :returns pd.DatetimeIndex: A DatetimeIndex of available dates.
        """
        instruments_iter: Iterator[Instrument] = iter(self.__universe.as_instruments().values())
        datetime_index: pd.DatetimeIndex = next(instruments_iter).ohlcv_df.index

        for instrument in instruments_iter:
            datetime_index = datetime_index.union(instrument.ohlcv_df.index)

        start_date_idx, end_date_idx = DataFrameDateIndexHelper.resolve_date_range_to_idx_range(
            df_with_datetime_index=pd.DataFrame(index=datetime_index),
            from_date=start_date,
            until_date=end_date
        )

        return datetime_index[start_date_idx:end_date_idx].sort_values()


    def __after_property_update(self) -> 'Portfolio':
        """
        Called after a property update to refresh the holdings and history.
        """
        self.__holdings_v_kpis = self.__compute_holdings_v_kpis()
        self.__history = self.__compute_history()
        return self