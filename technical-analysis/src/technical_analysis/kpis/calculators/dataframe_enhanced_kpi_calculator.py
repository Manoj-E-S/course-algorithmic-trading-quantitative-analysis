import numpy as np

import pandas as pd

from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.kpis.calculators.kpi_calculator import KPICalculator
from technical_analysis.utils.dataframe_date_helper import DataFrameDateIndexHelper


class DataFrameEnhancedKPICalculator(KPICalculator):
    """
    A class to enhance the bare-bones functionality of KPICalculator to DataFrames and Series.
    """

    def __init__(self):
        raise NotImplementedError("This class is not meant to be instantiated directly. Use static methods instead.")

    
    @staticmethod
    def cagr_from_df(
        ohlcv_df: pd.DataFrame,
        row_span: CandlespanEnum,
        from_date: pd.Timestamp | None = None,
        until_date: pd.Timestamp | None = None
    ) -> float:
        """
        Compute the CAGR

        :param ohlcv_df: The OHLCV DataFrame containing the instrument data.
        :type ohlcv_df: pd.DataFrame

        :param row_span: The candle span of the instrument (e.g., daily, weekly, monthly).
        :type row_span: CandlespanEnum

        :param from_date: The date from which to calculate the CAGR. If None, uses the earliest date.
        :type from_date: pd.Timestamp | None

        :param until_date: The date until which to calculate the CAGR. If None, uses the latest date.
        :type until_date: pd.Timestamp | None
        
        :return: The CAGR as a float.
        """
        if ohlcv_df.empty:
            return 0.0

        start_date_idx, end_date_idx = DataFrameDateIndexHelper.resolve_date_range_to_idx_range(
            datetime_index=ohlcv_df.index,
            from_date=from_date,
            until_date=until_date
        )

        periods: float = DataFrameDateIndexHelper.get_years_between_date_indices(ohlcv_df.index, row_span, start_date_idx, end_date_idx)
        if periods <= 0:
            return 0.0
        
        return KPICalculator.cagr(
            start_price=ohlcv_df[OHLCVUDEnum.CLOSE.value].iloc[start_date_idx],
            end_price=ohlcv_df[OHLCVUDEnum.CLOSE.value].iloc[end_date_idx],
            periods=periods
        )
    

    @staticmethod
    def max_drawdown_from_df(
        cumulative_returns: pd.Series,
        from_date: pd.Timestamp | None = None,
        until_date: pd.Timestamp | None = None
    ) -> float:
        """
        Compute the maximum drawdown

        :param cumulative_returns: The cumulative returns series of the instrument.
        :type cumulative_returns: pd.Series

        :param from_date: The date from which to calculate the maximum drawdown. If None, uses the earliest date.
        :type from_date: pd.Timestamp | None

        :param until_date: The date until which to calculate the maximum drawdown. If None, uses the latest date.
        :type until_date: pd.Timestamp | None
        
        :return: The maximum drawdown as a float.
        """
        if cumulative_returns.empty:
            return 0.0

        start_date_idx, end_date_idx = DataFrameDateIndexHelper.resolve_date_range_to_idx_range(
            datetime_index=cumulative_returns.to_frame().index,
            from_date=from_date,
            until_date=until_date
        )

        return KPICalculator.max_drawdown(
            cumulative_returns_series=cumulative_returns.iloc[start_date_idx:end_date_idx + 1]
        )
    

    @staticmethod
    def annualized_volatility_from_df(
        returns_series: pd.Series,
        row_span: CandlespanEnum,
        from_date: pd.Timestamp | None = None,
        until_date: pd.Timestamp | None = None,
        downside: bool = False
    ) -> float:
        """
        Compute the annualized volatility

        :param returns_series: The returns series of the instrument.
        :type returns_series: pd.Series

        :param row_span: The period each row in the DataFrame represents (e.g., daily, weekly, monthly).
        :type row_span: CandlespanEnum

        :param from_date: The date from which to calculate the annualized volatility. If None, uses the earliest date.
        :type from_date: pd.Timestamp | None
        
        :param until_date: The date until which to calculate the annualized volatility. If None, uses the latest date.
        :type until_date: pd.Timestamp | None
        
        :param downside: If True, calculate downside volatility; otherwise, calculate total volatility.
        :type downside: bool
        
        :return: The annualized volatility as a float.
        :rtype: float
        """
        start_date_idx, end_date_idx = DataFrameDateIndexHelper.resolve_date_range_to_idx_range(
            datetime_index=returns_series.index,
            from_date=from_date,
            until_date=until_date
        )

        returns_series: pd.Series = returns_series.iloc[start_date_idx:end_date_idx + 1]

        if returns_series.empty:
            return 0.0
        
        volatility = KPICalculator.non_annualized_volatility(returns_series, downside=downside)
        
        multiplier: float = np.sqrt(CandlespanEnum.periods_per_year(row_span))
        return volatility * multiplier