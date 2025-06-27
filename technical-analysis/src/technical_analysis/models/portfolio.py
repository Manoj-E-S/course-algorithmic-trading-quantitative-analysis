from dataclasses import asdict
from datetime import datetime

import pandas as pd

from technical_analysis.enums.kpi import KPIEnum
from technical_analysis.enums.portfolio_optimization_strategy import PortfolioOptimizationStrategy
from technical_analysis.models.instrument_universe import InstrumentUniverse
from technical_analysis.portfolio_optimizers.base import BaseOptimizer, DefaultOptimizerConfig
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
        optimization_strategy: PortfolioOptimizationStrategy = PortfolioOptimizationStrategy.DEFAULT,
        optimizer_config: DefaultOptimizerConfig | None = None
    ):
        if optimizer_config is None:
            optimizer_config = DefaultOptimizerConfig()

        if enable_precomputed_mode and end_date is not None:
            raise ValueError("In precomputed mode, end date is meaningless. Either do not provide this parameter, or create a new portfolio in incremental mode.")

        self.__universe: InstrumentUniverse = source_universe
        self.__number_of_holdings: int = number_of_holdings

        self.__precomputed: bool = enable_precomputed_mode
        self.__unset_precomputation_done_()

        self.__init_start_and_end_dates(
            start_date=start_date,
            end_date=end_date
        )

        self.__optimization_strategy: PortfolioOptimizationStrategy = optimization_strategy
        self.__optimizer_config: DefaultOptimizerConfig = optimizer_config

        self.__optimizer: BaseOptimizer = self.__get_optimizer()
        self.__setup_data()
        self.__setup_metadata()


    # Getters
    @property
    def optimization_strategy(self) -> PortfolioOptimizationStrategy:
        return self.__optimization_strategy

    @property
    def optimizer_config(self) -> DefaultOptimizerConfig:
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
    def current_holdings(self) -> list[str]:
        return list(self.__holdings_v_kpis.index)
    
    @property
    def current_holdings_v_kpis(self) -> pd.DataFrame:
        return self.__holdings_v_kpis
    
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
    def portfolio_kpis(self) -> pd.Series:
        return self.__holdings_v_kpis.agg(
            {
                KPIEnum.CAGR.value: 'mean',
                KPIEnum.MAX_DRAWDOWN.value: 'max',
                KPIEnum.CALAMAR_RATIO.value: 'mean',
                KPIEnum.SHARPE_RATIO.value: 'mean',
                KPIEnum.SORTINO_RATIO.value: 'mean',
                KPIEnum.ANNUALIZED_VOLATILITY.value: 'mean',
                KPIEnum.ANNUALIZED_DOWNSIDE_VOLATILITY.value: 'mean',
                InstrumentUniverse._Number_Of_Holdings_Column_Name: 'sum'
            },
            axis='index'
        )


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
            start_date = self.__available_dates(
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
            end_date = self.__available_dates(
                start_date=self.__start_date,
                end_date=None if end_date is None else pd.Timestamp(end_date)
            )[-1]
            self.__end_date = end_date
            self.__after_property_update()
        return self
    

    # Public methods
    def change_optimizer(self, optimization_strategy: PortfolioOptimizationStrategy, optimizer_config: DefaultOptimizerConfig) -> 'Portfolio':
        if self.__optimization_strategy != optimization_strategy:
            self.__optimization_strategy = optimization_strategy
            self.__optimizer_config = optimizer_config
            self.__after_property_update()

        return self
    

    def optimize(self) -> 'Portfolio':
        """
        Optimizes the portfolio for the next date.

        :return: The optimized portfolio instance.
        
        :raises ValueError: If the portfolio is in precomputed mode.
        """
        if self.in_precomputed_mode:
            raise ValueError("This portfolio is in precomputed mode. Cannot optimize a portfolio in precomputed mode. Create a new portfolio in incremental mode instead.")

        self.__end_date, self.__holdings_v_kpis = self.__optimizer.optimize(self.__holdings_v_kpis)
        self.__insert_into_incremental_history(self.__holdings_v_kpis)
        self.__update_metadata()

        return self
    

    # Private methods
    def __init_start_and_end_dates(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> None:
        available_dates: pd.DatetimeIndex = self.__available_dates(
            start_date=None if start_date is None else pd.Timestamp(start_date),
            end_date=None if end_date is None else pd.Timestamp(end_date)
        )

        if self.in_precomputed_mode:
            self.__start_date: pd.Timestamp = available_dates[0]
            self.__end_date: pd.Timestamp = available_dates[-1]
        else:
            self.__start_date: pd.Timestamp = available_dates[0]
            self.__end_date: pd.Timestamp = self.__start_date

    
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


    def __get_optimizer(self) -> BaseOptimizer:
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
                **asdict(self.__optimizer_config),
            )
        )
    

    def __init_incremental_history(self, holdings_v_kpis: pd.DataFrame) -> None:
        """
        Initializes the history DataFrame for the portfolio.
        """
        if self.in_precomputed_mode:
            raise ValueError("This portfolio is in precomputed mode. Cannot initialize via current holdings. Create a new portfolio in incremental mode instead.")
        
        self.__history: pd.DataFrame = \
            pd.DataFrame(
                data=holdings_v_kpis.values,
                index=pd.MultiIndex.from_product(
                    [[self.__end_date], holdings_v_kpis.index],
                    names=['date', 'symbol']
                ),
                columns=holdings_v_kpis.columns
            )


    def __insert_into_incremental_history(self, holdings_v_kpis: pd.DataFrame) -> None:
        """
        Inserts the current holdings with KPIs into the history DataFrame.
        """
        if self.in_precomputed_mode:
            raise ValueError("This portfolio is in precomputed mode. Cannot insert into history. Create a new portfolio in incremental mode instead.")

        holdings_v_kpis_with_date = holdings_v_kpis.copy()
        holdings_v_kpis_with_date.index = pd.MultiIndex.from_product(
            [[self.__end_date], holdings_v_kpis_with_date.index],
            names=["date", "symbol"]
        )

        if self.__end_date in self.__history.index.get_level_values("date"):
            self.__history.drop(index=self.__end_date, level="date", inplace=True)

        self.__history = pd.concat([self.__history, holdings_v_kpis_with_date])
    

    def __setup_data(self) -> None:
        """
        Sets up the data for the portfolio by initializing holdings with KPIs and the holding history.
        """
        if self.in_precomputed_mode:
            self.__precompute_data()
            return

        self.__holdings_v_kpis = self.__optimizer.init_holdings_v_kpis()
        self.__init_incremental_history(self.__holdings_v_kpis)

    
    def __sync_data(self) -> None:
        """
        Syncs the data for the portfolio by updating holdings with KPIs and the holding history.
        """
        if self.in_precomputed_mode:
            self.__precompute_data()
            return
        
        self.__holdings_v_kpis = self.__optimizer.update_holdings_v_kpis(self.__holdings_v_kpis)
        self.__insert_into_incremental_history(self.__holdings_v_kpis)

    
    def __precompute_data(self) -> None:
        """
        Precomputes the data for the portfolio in precomputed mode.
        """
        if self.in_incremental_mode:
            raise ValueError("This portfolio is not in precomputed mode. Cannot precompute data. Create a new portfolio in precomputed mode instead.")

        if self.__precomputation_done_:
            return
        
        self.__history = self.__optimizer.precomputed_history()
        self.__holdings_v_kpis = self.__optimizer.precomputed_holdings_v_kpis(self.__history)
        self.__set_precomputation_done_()

    
    def __setup_metadata(self) -> None:
        """
        Initializes the metadata DataFrame for the portfolio.
        """
        self.__metadata: pd.DataFrame = \
            pd.DataFrame(
                index=pd.Index(['all_dates' if self.in_precomputed_mode else self.__end_date], name='date'),
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
            raise ValueError("This portfolio is in precomputed mode. Cannot insert into metadata. Create a new portfolio in incremental mode instead.")
        
        if self.__end_date in self.__metadata.index:
            self.__metadata.drop(index=self.__end_date, inplace=True)
        
        self.__metadata.loc[self.__end_date] = [
            self.__optimization_strategy.value,
            self.__number_of_holdings,
            self.__optimizer.config.risk_free_rate
        ]

    
    def __after_property_update(self) -> 'Portfolio':
        """
        Called after a property update to refresh the holdings and history.
        """
        self.__unset_precomputation_done_()
        self.__optimizer = self.__get_optimizer()
        self.__sync_data()
        self.__update_metadata()
        return self


    def __set_precomputation_done_(self) -> None:
        if self.in_incremental_mode:
            self.__precomputation_done_ = None
            return

        self.__precomputation_done_ = True


    def __unset_precomputation_done_(self) -> None:
        if self.in_incremental_mode:
            self.__precomputation_done_ = None
            return
        
        self.__precomputation_done_ = False