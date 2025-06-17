from datetime import datetime
from typing import Literal

import pandas as pd

from technical_analysis.config.risk_free_rate_config import GlobalRiskFreeRateConfig
from technical_analysis.enums.kpi import KPIEnum
from technical_analysis.enums.portfolio_optimization_strategy import PortfolioOptimizationStrategy
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
        enable_precomputed_mode: bool = False,
        start_date: datetime | Literal['earliest'] = 'earliest',
        end_date: datetime | Literal['latest'] = 'latest',
        risk_free_rate: float | None = None,
    ):
        if risk_free_rate is None:
            risk_free_rate = GlobalRiskFreeRateConfig.get()

        if enable_precomputed_mode and end_date != 'latest':
            raise ValueError("In precomputed mode, end date is meaningless. Either do not provide this parameter, or create a new portfolio in incremental mode.")

        self.__universe: InstrumentUniverse = source_universe
        self.__number_of_holdings: int = number_of_holdings
        self.__optimization_strategy: PortfolioOptimizationStrategy = optimization_strategy
        self.__risk_free_rate: float = risk_free_rate

        self.__precomputed: bool = enable_precomputed_mode
        self.__precomputation_done_: bool = False # Only used in precomputed mode

        self.__init_start_and_end_dates(
            start_date=start_date,
            end_date=end_date
        )

        self.__holdings_v_kpis: pd.DataFrame = self.__latest_holdings_v_kpis()
        self.__history: pd.DataFrame = self.__sync_history()
        self.__sync_metadata()


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
    def date_range(self) -> pd.DatetimeIndex:
        return self.__history.index.get_level_values('date').unique()
    
    @property
    def metadata(self) -> pd.DataFrame:
        if self.in_precomputed_mode:
            return pd.DataFrame(
                index=pd.Index(['all_dates'], name='date'),
                columns=['optimization_strategy', 'number_of_holdings', 'kpi_risk_free_rate'],
                data=[
                    [
                        self.__optimization_strategy.value,
                        self.__number_of_holdings,
                        self.__risk_free_rate
                    ]
                ]
            )
        
        return self.__metadata
    
    @property
    def risk_free_rate(self) -> float:
        return self.__risk_free_rate
    
    @property
    def in_precomputed_mode(self) -> bool:
        return self.__precomputed
    
    @property
    def in_incremental_mode(self) -> bool:
        return not self.__precomputed


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
        if self.in_incremental_mode:
            raise ValueError("This portfolio is in incremental mode. Cannot change start date. Create a new portfolio in precomputed mode instead.")

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
        if self.in_incremental_mode:
            raise ValueError("This portfolio is in incremental mode. Cannot change end date. Create a new portfolio in precomputed mode instead.")

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
    

    def optimize(self) -> 'Portfolio':
        """
        Optimizes the portfolio based on the current settings.
        This method is a no-op in this implementation, as the portfolio is already optimized
        when it is created or when properties are updated.
        
        :return: The optimized portfolio instance.
        """
        if self.in_precomputed_mode:
            raise ValueError("This portfolio is in precomputed mode. Cannot optimize a portfolio in precomputed mode. Create a new portfolio in incremental mode instead.")

        try:
            end_date = DataFrameDateIndexHelper.next_date(
                df_with_datetime_index=self.__universe.closes_df,
                date=self.__end_date
            )
        except IndexError:
            print("[WARNING] There are no more dates available in the universe to optimize the portfolio. Skipping optimization.")
            return self

        self.__end_date = end_date
        self.__holdings_v_kpis = self.__latest_holdings_v_kpis()
        self.__history = self.__sync_history()
        self.__sync_metadata()

        return self
    

    # Private methods
    def __init_start_and_end_dates(
        self,
        start_date: pd.Timestamp | Literal['earliest'] = 'earliest',
        end_date: pd.Timestamp | Literal['latest'] = 'latest'
    ) -> None:
        available_dates: pd.DatetimeIndex = self.__available_dates(
            start_date=None if start_date == 'earliest' else pd.Timestamp(start_date),
            end_date=None if end_date == 'latest' else pd.Timestamp(end_date)
        )

        if self.in_precomputed_mode:
            self.__start_date: pd.Timestamp = available_dates[0]
            self.__end_date: pd.Timestamp = available_dates[-1]
        else:
            self.__start_date: pd.Timestamp = available_dates[0]
            self.__end_date: pd.Timestamp = self.__start_date


    def __latest_holdings_v_kpis(self) -> pd.DataFrame:
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


    def __sync_history(self) -> pd.DataFrame:
        """
        Updates the portfolio's holding history.
        In precomputed mode, precomputes the entire history if not already done.
        In incremental mode, appends the current holdings to the history.
        """
        if self.in_precomputed_mode:
            if self.__precomputation_done_:
                return self.__history
            
            history: pd.DataFrame = self.__precompute_history()
            self.__precomputation_done_ = True
            return history

        return self.__init_or_insert_to_history()

    
    def __sync_metadata(self) -> None:
        if self.in_precomputed_mode:
            return
        
        self.__init_or_insert_to_metadata()


    def __precompute_history(self) -> pd.DataFrame:
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
            raise NotImplementedError(
                f"Optimization strategy {self.__optimization_strategy} is not implemented."
            )


    def __init_or_insert_to_history(self) -> pd.DataFrame:
        if not hasattr(self, '_Portfolio__history'):
            self.__history = pd.DataFrame(
                index=pd.MultiIndex.from_product(
                    [[self.__end_date], self.__holdings_v_kpis.index],
                    names=['date', 'symbol']
                ),
                columns=self.__holdings_v_kpis.columns
            )
        
        holdings_v_kpis_with_date = self.__holdings_v_kpis.copy()
        holdings_v_kpis_with_date.index = pd.MultiIndex.from_product(
            [[self.__end_date], holdings_v_kpis_with_date.index],
            names=["date", "symbol"]
        )

        if self.__end_date in self.__history.index.get_level_values("date"):
            self.__history.drop(index=self.__end_date, level="date", inplace=True)

        return pd.concat([self.__history, holdings_v_kpis_with_date])


    def __init_or_insert_to_metadata(self) -> None:
        if not hasattr(self, '_Portfolio__metadata'):
            self.__metadata: pd.DataFrame = pd.DataFrame(
                index=self.__history.index.get_level_values('date').unique(),
                columns=['optimization_strategy', 'number_of_holdings', 'kpi_risk_free_rate'],
            )
            self.__metadata.index.name = 'date'

        if self.__end_date in self.__metadata.index:
            self.__metadata.drop(index=self.__end_date, inplace=True)
        
        self.__metadata.loc[self.__end_date] = [
            self.__optimization_strategy.value,
            self.__number_of_holdings,
            self.__risk_free_rate
        ]
    

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
        full_datetime_index: pd.DatetimeIndex = self.__universe.closes_df.index

        start_date_idx, end_date_idx = DataFrameDateIndexHelper.resolve_date_range_to_idx_range(
            df_with_datetime_index=pd.DataFrame(index=full_datetime_index),
            from_date=start_date,
            until_date=end_date
        )

        return full_datetime_index[start_date_idx:end_date_idx + 1].sort_values()


    def __after_property_update(self) -> 'Portfolio':
        """
        Called after a property update to refresh the holdings and history.
        """
        self.__precomputation_done_ = False # Only used in precomputed mode
        self.__holdings_v_kpis = self.__latest_holdings_v_kpis()
        self.__history = self.__sync_history()
        self.__sync_metadata()
        return self