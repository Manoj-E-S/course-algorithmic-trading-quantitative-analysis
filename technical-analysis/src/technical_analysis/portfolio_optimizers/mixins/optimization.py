from typing import Generator
import pandas as pd
from technical_analysis.portfolio_optimizers.protocols.supports_optimization import supportsOptimization
from technical_analysis.utils.dataframe_date_helper import DataFrameDateIndexHelper
from technical_analysis.utils.decorators import optionally_overridable, override


class OptimizationMixin:
    """
    Mixin class to provide optimization functionality.

    - Provides methods to optimize the portfolio.
    - Designed to be used with classes that implement the `supportsOptimization` protocol.

    :Methods (can be overridden for custom behavior):
    - `optimize`: Generator that yields (last_optimized_date, current_holdings_kpis, history) at each step.
    - `_step_optimize_precomputed_mode`: Optimizes the portfolio in precomputed mode.
    - `_step_optimize_incremental_mode`: Optimizes the portfolio in incremental mode.

    :Functionality provided:
    - In Precomputed Mode:
        - Iterates through the dates in the universe, optimizing the portfolio for each date.
        - Updates holdings and appends to history.
        - Starts from the `start_date` configured.
        - Continues until the `end_date` configured.
    - In Incremental Mode:
        - Optimizes the portfolio for the next date in the universe, updating holdings and appending to history.
        - Starts from the `start_date` configured.
        - Continues until there are no more dates available in the universe.
    """
    
    @override
    def optimize(
        self: supportsOptimization,
        current_holdings_kpis: pd.DataFrame,
        history: pd.DataFrame
    ) -> Generator[tuple[pd.Timestamp, pd.DataFrame, pd.DataFrame], None, None]:
        """
        Generator that optimizes the portfolio based on the default strategy.

        :param current_holdings_kpis: The current holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        :type current_holdings_kpis: pd.DataFrame

        :param history: The historical holdings with their KPIs as a DataFrame. Index is (date, symbol), and the columns are the KPI values.
        :type history: pd.DataFrame

        :return Generator: that yields (last_optimized_date, current_holdings_kpis, history) at each step.
        """
        if self.config.in_precomputed_mode:
            yield from self._step_optimize_precomputed_mode(
                current_holdings_kpis,
                history
            )
        else:
            yield from self._step_optimize_incremental_mode(
                current_holdings_kpis,
                history
            )


    @optionally_overridable
    def _step_optimize_precomputed_mode(
        self: supportsOptimization,
        current_holdings_kpis: pd.DataFrame,
        history: pd.DataFrame,
    ) -> Generator[tuple[pd.Timestamp, pd.DataFrame, pd.DataFrame], None, None]:
        
        latest_optimized_date: pd.Timestamp = self.config.start_date
        terminate_at_date: pd.Timestamp = self.config.end_date
        
        while True:
            try:
                latest_optimized_date = DataFrameDateIndexHelper.next_date(
                    datetime_index=self.config.universe.closes_df.index,
                    date=latest_optimized_date
                )
                if latest_optimized_date > terminate_at_date:
                    break
                print(f"[INFO] Optimizing portfolio for date: {latest_optimized_date} in precomputed mode...")
            except IndexError:
                print("[WARNING] There are no more dates available in the universe to optimize the portfolio. Stopping Optimization.")
                break

            self.config.end_date = latest_optimized_date
            current_holdings_kpis = self.update_current_holdings_kpis(current_holdings_kpis)
            history = self.append_to_history(history, current_holdings_kpis)

            yield latest_optimized_date, current_holdings_kpis, history

    
    @optionally_overridable
    def _step_optimize_incremental_mode(
        self: supportsOptimization,
        current_holdings_kpis: pd.DataFrame,
        history: pd.DataFrame,
    ) -> Generator[tuple[pd.Timestamp, pd.DataFrame, pd.DataFrame], None, None]:
        
        while True:
            try:
                latest_optimized_date = DataFrameDateIndexHelper.next_date(
                    datetime_index=self.config.universe.closes_df.index,
                    date=self.config.end_date
                )
                print(f"[INFO] Optimizing portfolio for date: {latest_optimized_date} in incremental mode...")
            except IndexError:
                print("[WARNING] There are no more dates available in the universe to optimize the portfolio. Stopping Optimization.")
                break

            self.config.end_date = latest_optimized_date
            current_holdings_kpis = self.update_current_holdings_kpis(current_holdings_kpis)
            history = self.append_to_history(history, current_holdings_kpis)

            yield latest_optimized_date, current_holdings_kpis, history
