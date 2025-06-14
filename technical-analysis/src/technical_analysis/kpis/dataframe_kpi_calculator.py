import pandas as pd

from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.kpis.kpi_calculator import KpiCalculator
from technical_analysis.utils.dataframe_date_helper import DataFrameDateIndexHelper


class DataFrameExtendedKPICalculator:
    """
    A class to calculate Key Performance Indicators (KPIs) from a DataFrame.
    This class is designed to work on DataFrames that contains financial data, such as OHLCV (Open, High, Low, Close, Volume) data.
    """

    def __init__(self):
        pass


    @staticmethod
    def get_years_between_date_indices(
        ohlcv_df: pd.DataFrame,
        candle_span: CandlespanEnum,
        start_date_idx: int = 0,
        end_date_idx: int = -1
    ) -> float:
        """
        Get the number of years between two date indices in the OHLCV DataFrame.

        :param ohlcv_df: The OHLCV DataFrame containing the instrument data.
        :type ohlcv_df: pd.DataFrame

        :param candle_span: The candle span of the instrument (e.g., daily, weekly, monthly).
        :type candle_span: CandlespanEnum
        
        :param start_date_idx: The index of the start date in the DataFrame. Default is 0.
        :type start_date_idx: int
        
        :param end_date_idx: The index of the end date in the DataFrame. Default is -1 (last index).
        :type end_date_idx: int
        
        :return: The number of years between the two dates as a float.
        :rtype: float
        """
        start_date: pd.Timestamp = ohlcv_df.index[start_date_idx]
        end_date: pd.Timestamp = ohlcv_df.index[end_date_idx]
        
        if start_date > end_date:
            raise ValueError("start_date cannot be later than end_date.")

        if start_date == end_date:
            return 0.0

        if candle_span == CandlespanEnum.DAILY:
            return (end_date - start_date).days / 252
        elif candle_span == CandlespanEnum.WEEKLY:
            return ((end_date - start_date).days/5) / 52
        elif candle_span == CandlespanEnum.MONTHLY:
            return ((end_date - start_date).days/20) / 12
        else:
            err: str = f"Unsupported candle span. Suppported candle spans are: {CandlespanEnum.values()}"
            raise ValueError(err)
    

    @staticmethod
    def compute_cagr(
        ohlcv_df: pd.DataFrame,
        candle_span: CandlespanEnum,
        from_date: pd.Timestamp | None = None,
        until_date: pd.Timestamp | None = None
    ) -> float:
        """
        Compute the CAGR

        :param ohlcv_df: The OHLCV DataFrame containing the instrument data.
        :type ohlcv_df: pd.DataFrame

        :param candle_span: The candle span of the instrument (e.g., daily, weekly, monthly).
        :type candle_span: CandlespanEnum

        :param from_date: The date from which to calculate the CAGR. If None, uses the earliest date.
        :type from_date: pd.Timestamp | None

        :param until_date: The date until which to calculate the CAGR. If None, uses the latest date.
        :type until_date: pd.Timestamp | None
        
        :return: The CAGR as a float.
        """
        if ohlcv_df.empty:
            return 0.0

        start_date_idx, end_date_idx = DataFrameDateIndexHelper.resolve_date_range_to_idx_range(
            df=ohlcv_df,
            from_date=from_date,
            until_date=until_date
        )

        periods: float = DataFrameExtendedKPICalculator.get_years_between_date_indices(ohlcv_df, candle_span, start_date_idx, end_date_idx)
        if periods <= 0:
            return 0.0
        
        return KpiCalculator.cagr(
            start_price=ohlcv_df[OHLCVUDEnum.CLOSE.value].iloc[start_date_idx],
            end_price=ohlcv_df[OHLCVUDEnum.CLOSE.value].iloc[end_date_idx],
            periods=periods
        )
    

    @staticmethod
    def compute_max_drawdown(
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
            df=cumulative_returns.to_frame(),
            from_date=from_date,
            until_date=until_date
        )

        return KpiCalculator.max_drawdown(
            cumulative_returns_series=cumulative_returns.iloc[start_date_idx:end_date_idx + 1]
        )
    

    @staticmethod
    def compute_annualized_volatility(
        returns_series: pd.Series,
        candle_span: CandlespanEnum,
        from_date: pd.Timestamp | None = None,
        until_date: pd.Timestamp | None = None,
        downside: bool = False
    ) -> float:
        """
        Compute the annualized volatility

        :param returns_series: The returns series of the instrument.
        :type returns_series: pd.Series
        
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
            df=returns_series.to_frame(),
            from_date=from_date,
            until_date=until_date
        )

        returns_series: pd.Series = returns_series.iloc[start_date_idx:end_date_idx + 1]

        if returns_series.empty:
            return 0.0
        
        volatility = KpiCalculator.non_annualized_volatility(returns_series, downside=downside)
        
        if candle_span == CandlespanEnum.DAILY:
            return volatility * (252 ** 0.5)
        elif candle_span == CandlespanEnum.WEEKLY:
            return volatility * (52 ** 0.5)
        elif candle_span == CandlespanEnum.MONTHLY:
            return volatility * (12 ** 0.5)
        else:
            err: str = f"Unsupported candle span. Suppported candle spans are: {CandlespanEnum.values()}"
            raise ValueError(err)
        
    
    @staticmethod
    def compute_calamar_ratio(
        cagr: float,
        max_drawdown: float
    ) -> float:
        """
        Compute the Calmar Ratio

        :param cagr: The Compound Annual Growth Rate (CAGR) of the instrument.
        :type cagr: float
        
        :param max_drawdown: The maximum drawdown of the instrument.
        :type max_drawdown: float
        
        :return: The Calmar Ratio as a float.
        :rtype: float
        """
        return KpiCalculator.calmar_ratio(cagr, max_drawdown)
    

    @staticmethod
    def compute_sharpe_ratio(
        risk_free_rate: float, 
        expected_returns: float,
        volatility: float
    ) -> float:
        """
        Compute the Sharpe Ratio
        
        :param risk_free_rate: The risk-free rate to be used in the calculation.
        :type risk_free_rate: float

        :param expected_returns: The expected returns of the instrument.
        :type expected_returns: float

        :param volatility: The annualized volatility of the instrument.
        :type volatility: float
        
        :return: The Sharpe Ratio as a float.
        :rtype: float
        """
        return KpiCalculator.sharpe_ratio(expected_returns, risk_free_rate, volatility)
    

    @staticmethod
    def compute_sortino_ratio(
        risk_free_rate: float,
        expected_returns: float,
        downside_volatility: float
    ) -> float:
        """
        Compute the Sortino Ratio
        
        :param risk_free_rate: The risk-free rate to be used in the calculation.
        :type risk_free_rate: float

        :param expected_returns: The expected returns of the instrument.
        :type expected_returns: float

        :param downside_volatility: The annualized downside volatility of the instrument.
        :type downside_volatility: float
        
        :return: The Sortino Ratio as a float.
        :rtype: float
        """
        return KpiCalculator.sortino_ratio(expected_returns, risk_free_rate, downside_volatility)
