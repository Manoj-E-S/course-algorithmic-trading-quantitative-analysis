import numpy as np
import pandas as pd

from technical_analysis.config.risk_free_rate_config import GlobalRiskFreeRateConfig
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.kpi import KPIEnum
from technical_analysis.kpis.calculators.rolling_kpi_calculator import RollingKPICalculator
from technical_analysis.mappers.kpi_to_method import KPIToMethod
from technical_analysis.models.instrument_group import InstrumentGroup
from technical_analysis.providers.data_view import DataViewProvider
from technical_analysis.utils.dataframe_date_helper import DataFrameDateIndexHelper


class InstrumentUniverse(InstrumentGroup):
    """
    A class that represents a universe of financial instruments.
    This class is a specialized version of InstrumentGroup, designed to manage a collection of instruments.
    """

    # Constants
    _Number_Of_Holdings_Column_Name: str = "NUMBER_OF_HOLDINGS"


    def __init__(
        self,
        instrument_symbols: list[str],
        candle_span: CandlespanEnum,
        data_view_provider: DataViewProvider | None = None
    ):
        super().__init__(instrument_symbols, candle_span, data_view_provider)


    def kpi_history(
        self,
        from_date: pd.Timestamp,
        to_date: pd.Timestamp,
        rf_sharpe_sortino: float | None = None,
    ) -> pd.DataFrame:
        """
        Get the KPI history of instruments in the uiverse over a specified date range.
        This method calculates cumulative KPIs for the instruments in the universe over a specified date range.

        :param from_date: The start date of the date range.
        :type from_date: pd.Timestamp
        
        :param to_date: The end date of the date range.
        :type to_date: pd.Timestamp
        
        :param rf_sharpe_sortino: The risk-free rate to use for Sharpe and Sortino ratios. If None, uses the global risk-free rate.
        :type rf_sharpe_sortino: float
        
        :return: A DataFrame containing the cumulative KPIs for each instrument in the universe over the specified date range.
        :rtype: pd.DataFrame
        """
        if rf_sharpe_sortino is None:
            rf_sharpe_sortino = GlobalRiskFreeRateConfig.get()

        rolling_kpi_calculator: RollingKPICalculator = RollingKPICalculator(self.closes_df, self.candle_span, from_date, to_date)

        kpi_dfs: dict[str, pd.DataFrame] = {}
        for kpi_enum in KPIToMethod.ForRollingKPICalculator.keys():
            kpi_df: pd.DataFrame = pd.DataFrame(
                data=(
                    KPIToMethod.ForRollingKPICalculator[kpi_enum]
                        .__get__(rolling_kpi_calculator)()
                    if kpi_enum not in [KPIEnum.SHARPE_RATIO, KPIEnum.SORTINO_RATIO]

                    #=======================

                    else
                    KPIToMethod.ForRollingKPICalculator[kpi_enum]
                        .__get__(rolling_kpi_calculator)(risk_free_rate=rf_sharpe_sortino)
                ),
                columns=self.instrument_symbols
            )
            kpi_dfs[kpi_enum.value] = kpi_df

        combined_df: pd.DataFrame = pd.concat(kpi_dfs.values(), keys=kpi_dfs.keys(), names=['kpi', 'date']).stack().unstack(level='kpi')
        combined_df[InstrumentUniverse._Number_Of_Holdings_Column_Name] = np.ones(combined_df.shape[0], dtype='int32')
        combined_df.columns.name = 'kpi'
        combined_df.index.names = ['date', 'symbol']
        combined_df.sort_index(level='date', inplace=True)
        return combined_df


    def kpi_snapshot(
        self,
        overall_start_date: pd.Timestamp,
        snapshot_date: pd.Timestamp,
        rf_sharpe_sortino: float | None = None,
    ) -> pd.DataFrame:
        """
        Get a snapshot of KPIs for the instruments in the universe at a specific date.
        This method calculates the KPIs for each instrument in the universe at a specific date, considering data starting from the overall start date up to that date.
        
        :param overall_start_date: The start date of the overall period for which KPIs are calculated.
        :type overall_start_date: pd.Timestamp
        
        :param snapshot_date: The date for which the KPI snapshot is taken.
        :type snapshot_date: pd.Timestamp
        
        :param rf_sharpe_sortino: The risk-free rate to use for Sharpe and Sortino ratios. If None, uses the global risk-free rate.
        :type rf_sharpe_sortino: float | None
        
        :return: A DataFrame containing the KPIs for each instrument in the universe at the specified date.
        :rtype: pd.DataFrame
        """
        if rf_sharpe_sortino is None:
            rf_sharpe_sortino = GlobalRiskFreeRateConfig.get()

        rolling_kpi_calculator: RollingKPICalculator = RollingKPICalculator(self.closes_df, self.candle_span, overall_start_date, snapshot_date)

        data: dict[str, pd.Series] = {}
        for kpi_enum in KPIToMethod.ForRollingKPICalculator.keys():
            kpi_series: pd.Series = pd.Series(
                data= (
                    KPIToMethod.ForRollingKPICalculator[kpi_enum]
                        .__get__(rolling_kpi_calculator)()
                        .loc[DataFrameDateIndexHelper.get_nearest_date(self.closes_df.index, snapshot_date)]
                    if kpi_enum not in [KPIEnum.SHARPE_RATIO, KPIEnum.SORTINO_RATIO]

                    #=======================
                    
                    else
                    KPIToMethod.ForRollingKPICalculator[kpi_enum]
                        .__get__(rolling_kpi_calculator)(risk_free_rate=rf_sharpe_sortino)
                        .loc[DataFrameDateIndexHelper.get_nearest_date(self.closes_df.index, snapshot_date)]
                )
            )
            kpi_series.name = kpi_enum.value
            data[kpi_enum.value] = kpi_series
        
        df: pd.DataFrame = pd.DataFrame.from_dict(data, orient='index').T
        df[InstrumentUniverse._Number_Of_Holdings_Column_Name] = np.ones(df.shape[0], dtype='int32')
        df.columns.name = 'kpi'
        df.index.names = ['symbol']
        return df


    def sorted_kpi_snapshot(
        self,
        sort_by: KPIEnum,
        overall_start_date: pd.Timestamp,
        snapshot_date: pd.Timestamp,
        rf_sharpe_sortino: float | None = None,
        ascending: bool = True,
        top_n: int | None = None,
    ) -> pd.DataFrame:
        """
        Get a sorted DataFrame of instruments based on a specific KPI at a given date snapshot.
        This method retrieves the KPI snapshot for the instruments in the universe at a specific date and sorts them by the specified KPI.
        
        :param sort_by: The KPI by which to sort the instruments.
        :type sort_by: KPIEnum
        
        :param overall_start_date: The start date of the overall period for which KPIs are calculated.
        :type overall_start_date: pd.Timestamp
        
        :param snapshot_date: The date for which the KPI snapshot is taken.
        :type snapshot_date: pd.Timestamp

        :param rf_sharpe_sortino: The risk-free rate to use for Sharpe and Sortino ratios. If None, uses the global risk-free rate.
        :type rf_sharpe_sortino: float | None
        
        :param ascending: Whether to sort the KPI values in ascending order. Default is True.
        :type ascending: bool
        
        :param top_n: If specified, return only the top N instruments sorted by the KPI. Default is None, which returns all instruments.
        :type top_n: int | None
        
        :return: A DataFrame containing the instruments sorted by the specified KPI at the given date snapshot.
        :rtype: pd.DataFrame
        
        :raises ValueError: If the specified KPI is not available in the KPI DataFrame.
        """
        if rf_sharpe_sortino is None:
            rf_sharpe_sortino = GlobalRiskFreeRateConfig.get()

        kpi_df: pd.DataFrame = self.kpi_snapshot(overall_start_date, snapshot_date, rf_sharpe_sortino)

        if sort_by.value not in kpi_df.columns:
            raise ValueError(f"KPI '{sort_by.value}' is not available in the KPI DataFrame.")

        kpi_df.sort_values(by=sort_by.value, ascending=ascending, inplace=True)
        
        if top_n:
            return kpi_df.head(top_n)
        
        return kpi_df
    

    def sorted_kpi_history(
        self,
        sort_by: KPIEnum,
        period_start_date: pd.Timestamp,
        period_end_date: pd.Timestamp,
        ascending: bool = True,
        rf_sharpe_sortino: float | None = None,
        top_n: int | None = None,
    ) -> pd.DataFrame:
        """
        Get a DataFrame of instruments sorted by a specific KPI for each date in a given date range.
        This method retrieves the KPI history for the instruments in the universe over a specified date range and sorts them by the specified KPI for each date.
        
        :param sort_by: The KPI by which to sort the instruments.
        :type sort_by: KPIEnum
        
        :param period_start_date: The start date of the period for which the KPI history is retrieved.
        :type period_start_date: pd.Timestamp
        
        :param period_end_date: The end date of the period for which the KPI history is retrieved.
        :type period_end_date: pd.Timestamp
        
        :param rf_sharpe_sortino: The risk-free rate to use for Sharpe and Sortino ratios. If None, uses the global risk-free rate.
        :type rf_sharpe_sortino: float
        
        :param ascending: Whether to sort the KPI values in ascending order. Default is True.
        :type ascending: bool
        
        :param top_n: If specified, return only the top N instruments sorted by the KPI for each date. Default is None, which returns all instruments.
        :type top_n: int | None
        
        :return: A DataFrame containing the instruments sorted by the specified KPI for each date in the given date range.
        :rtype: pd.DataFrame
        
        :raises ValueError: If the specified KPI is not available in the KPI DataFrame.
        """
        if rf_sharpe_sortino is None:
            rf_sharpe_sortino = GlobalRiskFreeRateConfig.get()
        
        kpi_history_df: pd.DataFrame = self.kpi_history(
            from_date=period_start_date,
            to_date=period_end_date,
            rf_sharpe_sortino=rf_sharpe_sortino
        )

        if sort_by.value not in kpi_history_df.columns:
            raise ValueError(f"KPI '{sort_by.value}' is not available in the KPI DataFrame.")

        kpi_history_df.sort_index(level='date', inplace=True)
        
        if top_n:
            return\
                kpi_history_df\
                .groupby(level='date', group_keys=False)\
                .apply(lambda g: g.sort_values(by=sort_by.value, ascending=ascending).head(top_n))
        
        return\
            kpi_history_df\
            .groupby(level='date', group_keys=False)\
            .apply(lambda g: g.sort_values(by=sort_by.value, ascending=ascending))
