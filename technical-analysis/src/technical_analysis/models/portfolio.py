from dataclasses import asdict
from datetime import datetime
from functools import cached_property
from itertools import islice
from typing import Generator

import numpy as np
import pandas as pd

from technical_analysis.enums.agg_fn import AggregatorFunctionEnum
from technical_analysis.enums.kpi import KPIEnum
from technical_analysis.enums.portfolio_optimization_strategy import PortfolioOptimizationStrategy
from technical_analysis.mappers.aggfn_to_name import AggFnToName
from technical_analysis.mappers.kpi_to_aggfn import KPIToAggFn
from technical_analysis.models.instrument_universe import InstrumentUniverse
from technical_analysis.portfolio_optimizers.top_picks import TopPicksOptimizer, OptimizerConfig
from technical_analysis.utils.dataframe_date_helper import DataFrameDateIndexHelper


class Portfolio:
    """
    A class that represents a portfolio of financial instruments.
    """

    def __init__(
        self,
        number_of_holdings: int,
        source_universe: InstrumentUniverse,
        enable_precomputed_mode: bool = False,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        optimization_strategy: PortfolioOptimizationStrategy = PortfolioOptimizationStrategy.TOP_PICKS,
        optimizer_config: OptimizerConfig | None = None
    ):
        if optimizer_config is None:
            optimizer_config = OptimizerConfig()

        if not enable_precomputed_mode and end_date is not None:
            raise ValueError("In incremental mode, end date is meaningless. Either do not provide this parameter, or create a new portfolio in precomputed mode.")

        self.__universe: InstrumentUniverse = source_universe
        self.__number_of_holdings: int = number_of_holdings

        self.__precomputed: bool = enable_precomputed_mode
        self.__precomputation_not_done()

        self.__init_start_and_end_dates(
            start_date=start_date,
            end_date=end_date
        )

        self.__optimization_strategy: PortfolioOptimizationStrategy = optimization_strategy
        self.__optimizer_config: OptimizerConfig = optimizer_config

        self.__optimizer: TopPicksOptimizer = self.__get_optimizer()
        self.__setup_data()
        self.__setup_metadata()


    # Getters
    @property
    def optimization_strategy(self) -> PortfolioOptimizationStrategy:
        return self.__optimization_strategy

    @property
    def optimizer_config(self) -> OptimizerConfig:
        return self.__optimizer_config

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
    def current_holdings(self) -> pd.DataFrame:
        self.__current_holdings_kpis[InstrumentUniverse._Number_Of_Holdings_Column_Name] = self.__current_holdings_kpis[InstrumentUniverse._Number_Of_Holdings_Column_Name].astype('int32')
        return self.__current_holdings_kpis[InstrumentUniverse._Number_Of_Holdings_Column_Name].to_frame()

    @property
    def current_holdings_kpis(self) -> pd.DataFrame:
        self.__current_holdings_kpis[InstrumentUniverse._Number_Of_Holdings_Column_Name] = self.__current_holdings_kpis[InstrumentUniverse._Number_Of_Holdings_Column_Name].astype('int32')
        return self.__current_holdings_kpis
    
    @property
    def holding_history(self) -> pd.DataFrame:
        self.__history[InstrumentUniverse._Number_Of_Holdings_Column_Name] = self.__history[InstrumentUniverse._Number_Of_Holdings_Column_Name].astype('int32')
        return self.__history
    
    @property
    def date_range(self) -> pd.DatetimeIndex:
        return self.__history.index.get_level_values('date').unique()
    
    @property
    def metadata(self) -> pd.DataFrame:
        return self.__metadata
    
    @property
    def in_precomputed_mode(self) -> bool:
        return self.__precomputed
    
    @property
    def in_incremental_mode(self) -> bool:
        return not self.__precomputed
    
    @property
    def pct_return(self) -> float:
        return float((self.cumulative_returns_series.iloc[-1] - 1.0) * 100)


    @cached_property
    def portfolio_kpis(self) -> pd.DataFrame:
        rows = []
        for kpi, agg_fn in KPIToAggFn.Mapper.items():
            series: pd.Series = self.__current_holdings_kpis[kpi.value]

            agg_val: float = agg_fn(series)
            agg_method: str = AggFnToName.Mapper.get(agg_fn, "UNKNOWN")
            contributing_instrument: str = self.__find_contributing_instrument_for_aggregator(series, agg_fn)

            rows.append({
                "kpi_value": agg_val,
                "agg_method": agg_method,
                "max_contrib_value": series[contributing_instrument] if contributing_instrument in series.index else "N/A",
                "max_contrib_symbol": contributing_instrument,
            })

        portfolio_kpis_df = pd.DataFrame(data=rows, index=KPIEnum.values())
        portfolio_kpis_df.index.name = "kpi"
        return portfolio_kpis_df


    @cached_property
    def returns_series(self) -> pd.Series:
        current_holdings_returns_df: pd.DataFrame = self.__universe.closes_df[self.__current_holdings_kpis.index].loc[self.date_range].pct_change().fillna(0)
        weights: pd.Series = self.__current_holdings_kpis[InstrumentUniverse._Number_Of_Holdings_Column_Name]
        return current_holdings_returns_df.mul(weights, axis=1).sum(axis=1).div(weights.sum(), axis=0)
    

    @cached_property
    def cumulative_returns_series(self) -> pd.Series:
        return (1 + self.returns_series).cumprod()


    # Chainable Setters
    @number_of_holdings.setter
    def number_of_holdings(self, number_of_holdings: int) -> 'Portfolio':
        if self.__number_of_holdings != number_of_holdings:
            self.__number_of_holdings = number_of_holdings
            self.__after_property_update()
        return self
    

    @start_date.setter
    def start_date(self, start_date: datetime | None) -> 'Portfolio':
        if self.in_incremental_mode:
            raise ValueError("This portfolio is in incremental mode. Cannot change start date. Create a new portfolio in precomputed mode instead.")

        if self.__start_date != start_date:
            start_date = self.__universe.get_all_available_dates(
                start_date=None if start_date is None else pd.Timestamp(start_date),
                end_date=self.__end_date
            )[0]
            self.__start_date = start_date
            self.__after_property_update()
        return self
    

    @end_date.setter
    def end_date(self, end_date: datetime | None) -> 'Portfolio':
        if self.in_incremental_mode:
            raise ValueError("This portfolio is in incremental mode. Cannot change end date. Create a new portfolio in precomputed mode instead.")

        if self.__end_date != end_date:
            end_date = self.__universe.get_all_available_dates(
                start_date=self.__start_date,
                end_date=None if end_date is None else pd.Timestamp(end_date)
            )[-1]
            self.__end_date = end_date
            self.__after_property_update()
        return self
    

    # Public methods
    def change_optimizer(self, optimization_strategy: PortfolioOptimizationStrategy, optimizer_config: OptimizerConfig) -> 'Portfolio':
        if self.__optimization_strategy != optimization_strategy:
            self.__optimization_strategy = optimization_strategy
            self.__optimizer_config = optimizer_config
            self.__after_property_update()

        return self
    

    def step_to(self, date: datetime) -> 'Portfolio':
        """
        Moves the portfolio to the specified date. If the date is before the start date, it will move to the start date.
        If the date is after the end date, it will move to the end date.

        :param date: The date to step to.
        :type date: datetime

        :return: The optimized portfolio instance.
        
        :raises ValueError: If the portfolio is in precomputed mode.
        """
        if self.in_precomputed_mode:
            raise ValueError("This portfolio is in precomputed mode. It is already optimized fully. Create a new portfolio in incremental mode instead.")

        possible_dates: pd.DatetimeIndex = self.__universe.get_all_available_dates(start_date=self.__start_date)
        
        date = pd.Timestamp(date)
        if date < possible_dates[0]:
            date = possible_dates[0]
        elif date > possible_dates[-1]:
            date = possible_dates[-1]
        else:
            date = DataFrameDateIndexHelper.get_nearest_date(
                datetime_index=possible_dates,
                date=date
            )

        if date > self.__end_date:
            # Find number of periods from the current end date to the target date
            curr_end_idx, target_end_idx = DataFrameDateIndexHelper.resolve_date_range_to_idx_range(
                datetime_index=possible_dates,
                from_date=self.__end_date,
                until_date=date
            )
            num_periods: int = target_end_idx - curr_end_idx
            # step_up portfolio upto the specified date
            return self.step_up(num_periods)
        
        if date < self.__end_date:
            # Find number of periods from the target date to the current end date
            target_end_idx, curr_end_idx = DataFrameDateIndexHelper.resolve_date_range_to_idx_range(
                datetime_index=possible_dates,
                from_date=date,
                until_date=self.__end_date
            )
            num_periods: int = curr_end_idx - target_end_idx
            # step_back portfolio upto the specified date
            return self.step_back(num_periods)
        
        # If the date is the same as the current end date, do nothing
        return self


    def step_back(self, num_periods: int = 1) -> 'Portfolio':
        """
        Moves the portfolio back by `num_periods` periods.
        If `num_periods` is greater than the number of available periods, it will step back to the first available date.

        :param num_periods: The number of periods to step back. Default is 1.
        :type num_periods: int

        :return: The portfolio instance.
        
        :raises ValueError: If the portfolio is in precomputed mode.
        """
        if self.in_precomputed_mode:
            raise ValueError("This portfolio is in precomputed mode. It is already optimized fully. Create a new portfolio in incremental mode instead.")

        if len(self.date_range) <= 1:
            return self

        if num_periods > len(self.date_range) - 1:
            num_periods = len(self.date_range) - 1

        dates_to_be_dropped = self.date_range[-num_periods:]
        self.__history.drop(index=dates_to_be_dropped, level='date', inplace=True)
        self.__metadata.drop(index=dates_to_be_dropped, inplace=True)
        self.__current_holdings_kpis = self.__history.loc[self.date_range[-1], :]

        self.__reset_cached_properties()
        return self


    def step_up(self, num_periods: int = 1) -> 'Portfolio':
        """
        Moves the portfolio ahead by `num_periods` periods.
        If `num_periods` is greater than the number of available periods, it will step up to the last available date.

        :param num_periods: The number of periods to step up. Default is 1.
        :type num_periods: int

        :return: The portfolio instance.
        
        :raises ValueError: If the portfolio is in precomputed mode.
        """
        if self.in_precomputed_mode:
            raise ValueError("This portfolio is in precomputed mode. It is already optimized fully. Create a new portfolio in incremental mode instead.")

        optimization_gen: Generator[tuple[pd.Timestamp, pd.DataFrame, pd.DataFrame], None, None]\
            = self.__optimizer.optimize(self.__current_holdings_kpis, self.__history)
        
        for result in islice(optimization_gen, num_periods):
            self.__end_date, self.__current_holdings_kpis, self.__history = result
            self.__update_metadata()

        self.__reset_cached_properties()
        return self
    

    # Private methods
    def __init_start_and_end_dates(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> None:
        available_dates = self.__universe.get_all_available_dates(
            start_date=pd.Timestamp(start_date) if start_date else None,
            end_date=pd.Timestamp(end_date) if end_date else None
        )

        if self.in_precomputed_mode:
            self.__start_date: pd.Timestamp = available_dates[0]
            self.__end_date: pd.Timestamp = available_dates[-1]
        else:
            self.__start_date: pd.Timestamp = available_dates[0]
            self.__end_date: pd.Timestamp = self.__start_date


    def __get_optimizer(self) -> TopPicksOptimizer:
        """
        Returns the appropriate optimizer based on the optimization strategy, and initializes it with the provided configuration.
        """
        return PortfolioOptimizationStrategy.get_optimizer(
            strategy=self.__optimization_strategy,
            config=dict(
                universe=self.__universe,
                number_of_holdings=self.__number_of_holdings,
                start_date=self.__start_date,
                end_date=self.__end_date,
                in_precomputed_mode=self.in_precomputed_mode,
                **asdict(self.__optimizer_config),
            )
        )
    

    def __setup_data(self) -> None:
        """
        Sets up the data for the portfolio by initializing holdings with KPIs and the holding history.
        """
        if self.in_precomputed_mode:
            self.__precompute_data()
            return
        
        self.__current_holdings_kpis: pd.DataFrame = self.__optimizer.init_current_holdings_kpis()
        self.__history: pd.DataFrame = self.__optimizer.init_history(self.__current_holdings_kpis)
        self.__reset_cached_properties()


    def __sync_data(self) -> None:
        """
        Syncs the data for the portfolio by updating holdings with KPIs and the holding history.
        """
        if self.in_precomputed_mode:
            self.__precompute_data()
            return
        
        self.__current_holdings_kpis = self.__optimizer.update_current_holdings_kpis(self.__current_holdings_kpis)
        self.__history = self.__optimizer.append_to_history(self.__history, self.__current_holdings_kpis)
        self.__reset_cached_properties()

    
    def __precompute_data(self) -> None:
        """
        Precomputes the data for the portfolio in precomputed mode.
        """
        if self.in_incremental_mode:
            raise ValueError("This portfolio is not in precomputed mode. Cannot precompute data. Create a new portfolio in precomputed mode instead.")

        if self.__precomputation_done_:
            return
        
        self.__current_holdings_kpis, self.__history = self.__optimizer.precompute()
        self.__reset_cached_properties()
        self.__precomputation_done()

    
    def __setup_metadata(self) -> None:
        """
        Initializes the metadata DataFrame for the portfolio.
        """
        self.__metadata: pd.DataFrame = \
            pd.DataFrame(
                index=pd.Index([f'{self.__start_date.date()} - {self.__end_date.date()}' if self.in_precomputed_mode else self.__end_date], name='date'),
                columns=['optimization_strategy', 'number_of_holdings', 'kpi_risk_free_rate'],
                data=[
                    [
                        self.__optimization_strategy.value,
                        self.__number_of_holdings,
                        self.__optimizer.config.risk_free_rate
                    ]
                ]
            )


    def __update_metadata(self) -> None:
        """
        Updates the current metadata into the metadata DataFrame for the portfolio.
        """
        if self.in_precomputed_mode:
            raise ValueError("This portfolio is in precomputed mode. Cannot update metadata. Create a new portfolio in incremental mode instead.")
        
        if self.__end_date in self.__metadata.index:
            self.__metadata.drop(index=self.__end_date, inplace=True)
        
        self.__metadata.loc[self.__end_date] = [
            self.__optimization_strategy.value,
            self.__number_of_holdings,
            self.__optimizer.config.risk_free_rate
        ]


    def __precomputation_done(self) -> None:
        if self.in_incremental_mode:
            self.__precomputation_done_ = None
            return

        self.__precomputation_done_ = True


    def __precomputation_not_done(self) -> None:
        if self.in_incremental_mode:
            self.__precomputation_done_ = None
            return
        
        self.__precomputation_done_ = False

    
    def __find_contributing_instrument_for_aggregator(self, series: pd.Series, agg_fn: AggregatorFunctionEnum) -> str:
        """
        Finds the instrument that contributes the most to the aggregation function.

        :param series: The series of values for the KPI.
        :type series: pd.Series

        :param agg_fn: The aggregation function used.
        :type agg_fn: AggregatorFunctionEnum

        :return: The symbol of the instrument contributing the most to the aggregation.
        :rtype: str
        """
        if agg_fn == AggregatorFunctionEnum.MEAN_FN:
            return series.idxmax() if not series.empty else "N/A"
        
        if agg_fn == AggregatorFunctionEnum.MEAN_OF_FINITES_FN:
            finite_series = series[np.isfinite(series)]
            return finite_series.idxmax() if not finite_series.empty else "N/A"
        
        if agg_fn == AggregatorFunctionEnum.MAX_FN:
            return series.idxmax() if not series.empty else "N/A"

        return "N/A"
    

    def __after_property_update(self) -> 'Portfolio':
        """
        Called after a property update to refresh the holdings and history.
        """
        self.__precomputation_not_done()
        self.__optimizer = self.__get_optimizer()
        self.__sync_data()
        self.__update_metadata()
        self.__reset_cached_properties()
        return self
    

    def __reset_cached_properties(self) -> None:
        """
        Resets the cached properties of the portfolio.
        """
        self.__dict__.pop('returns_series', None)
        self.__dict__.pop('cumulative_returns_series', None)
        self.__dict__.pop('portfolio_kpis', None)