from datetime import datetime
from typing import Iterator, Literal
import numpy as np
import pandas as pd
from technical_analysis.enums.kpi import KpiEnum
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
        end_date: datetime | Literal['latest'] = 'latest'
    ):
        self.__universe: InstrumentUniverse = source_universe
        self.__number_of_holdings: int = number_of_holdings
        self.__optimization_strategy: PortfolioOptimizationStrategy = optimization_strategy

        available_dates: pd.DatetimeIndex = self.__available_dates(
            start_date=None if start_date == 'earliest' else pd.Timestamp(start_date),
            end_date=None if end_date == 'latest' else pd.Timestamp(end_date)
        )

        self.__start_date: pd.Timestamp = available_dates[0]
        self.__end_date: pd.Timestamp = available_dates[-1]

        self.__holdings_v_kpis: pd.DataFrame = self.__current_holdings_v_kpis()
        
        self.__history: pd.DataFrame = self.__get_history()


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
        """
        Returns the portfolio history as a DataFrame.
        The index is the date, and the columns are the instrument symbols with their respective KPI values.
        """
        return self.__history


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
    

    # Private methods
    def __current_holdings_v_kpis(self) -> pd.DataFrame:
        """
        Computes the holdings based on the optimization strategy and number of holdings.

        :returns pd.DataFrame: A pandas DataFrame mapping instrument symbols to their respective KPI values.

        :raises ValueError: If the optimization strategy is not supported.
        """
        return self.__holdings_v_kpis_as_of_date(self.__end_date)


    def __holdings_v_kpis_as_of_date(self, date: pd.Timestamp) -> pd.DataFrame:
        """
        Computes the holdings based on the optimization strategy and number of holdings.

        :param date: The date as of which to compute the holdings.
        :type date: pd.Timestamp
        
        :returns pd.DataFrame: A pandas DataFrame mapping instrument symbols to their respective KPI values as of the specified date.

        :raises ValueError: If the optimization strategy is not supported.
        """
        print("Holdings as of date:", date)
        if self.__optimization_strategy == PortfolioOptimizationStrategy.REBALANCING:
            data: dict[KpiEnum.ForInstrumentKPI, np.ndarray] = {}
            cagrs_series: pd.Series = pd.Series(dtype='float64', name=KpiEnum.ForInstrumentKPI.CAGR.value)
            
            for kpi_value in KpiEnum.ForInstrumentKPI.values():
                # kpi series of Top N most-profitable instruments, profitable by CAGR
                kpi_enum = KpiEnum.ForInstrumentKPI(kpi_value)
                kpi_series = self.__universe.n_sorted_instruments_by_kpi(
                    sort_kpi=KpiEnum.ForInstrumentKPI.CAGR,
                    n=self.__number_of_holdings,
                    ascending=False,
                    metric_kpi=kpi_enum,
                    kwargs_for_sort_kpi={
                        'from_date': self.__start_date,
                        'until_date': date
                    },
                    kwargs_for_metric_kpi={
                        'from_date': self.__start_date,
                        'until_date': date,
                        'risk_free_rate': 0.06 if kpi_enum in [KpiEnum.ForInstrumentKPI.SHARPE_RATIO, KpiEnum.ForInstrumentKPI.SORTINO_RATIO] else None,
                        'downside': False if kpi_enum == KpiEnum.ForInstrumentKPI.ANNUALIZED_VOLATILITY else None
                    }
                )
                data[kpi_value] = kpi_series.values
                if kpi_enum == KpiEnum.ForInstrumentKPI.CAGR:
                    cagrs_series = kpi_series
                
            return pd.DataFrame(index=cagrs_series.index, data=data, columns=KpiEnum.ForInstrumentKPI.values())
        else:
            raise ValueError(f"Invalid Portfolio Optimization strategy. Supported strategies are: {PortfolioOptimizationStrategy.values()}")


    def __get_history(self) -> pd.DataFrame:
        """
        Populates the portfolio history DataFrame with the holdings and KPIs from the start date to the end date.

        :returns pd.DataFrame: A pandas DataFrame containing the portfolio history from the start date to the end date.
        :rtype: pd.DataFrame
        """
        history_multiindex: pd.MultiIndex = pd.MultiIndex.from_product(
            [
                self.__available_dates(
                    start_date=self.__start_date,
                    end_date=self.__end_date
                ),
                KpiEnum.ForInstrumentKPI.values()
            ],
            names=['date', 'kpi']
        )
        
        history = pd.DataFrame(data=np.nan, index=history_multiindex, columns=self.__holdings_v_kpis.index)
        
        all_dates_iter: Iterator[pd.Timestamp] = iter(history_multiindex.get_level_values('date').unique())
        for date in all_dates_iter:
            kpis_df: pd.DataFrame = self.__holdings_v_kpis_as_of_date(date)
            for kpi in kpis_df.columns:
                history.loc[(date, kpi), :] = kpis_df[kpi].values
        
        history.sort_index(inplace=True)
        history.dropna(inplace=True)

        return history


    def __available_dates(self, start_date: pd.Timestamp | None = None, end_date: pd.Timestamp | None = None) -> pd.DatetimeIndex:
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
            df=pd.DataFrame(index=datetime_index),
            from_date=start_date,
            until_date=end_date
        )

        return datetime_index[start_date_idx:end_date_idx].sort_values()


    def __after_property_update(self) -> 'Portfolio':
        """
        Called after a property update to refresh the holdings and history.
        """
        self.__holdings_v_kpis = self.__current_holdings_v_kpis()
        self.__history = self.__get_history()
        return self