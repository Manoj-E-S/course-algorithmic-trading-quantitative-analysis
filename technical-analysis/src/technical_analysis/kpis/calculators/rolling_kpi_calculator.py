from functools import cached_property

import numpy as np

import pandas as pd

from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.kpis.calculators.kpi_calculator import KPICalculator
from technical_analysis.utils.dataframe_date_helper import DataFrameDateIndexHelper


class RollingKPICalculator:
    """
    A class to calculate Key Performance Indicators (KPIs) from a DataFrame.
    """

    def __init__(
        self,
        prices_df: pd.DataFrame,
        row_span: CandlespanEnum,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None
    ):
        """
        Initialize the RollingKPICalculator with a DataFrame containing prices.

        :param prices_df: A DataFrame containing price data (one of O, H, L, or C) of one or more instruments (instrument identifiers as the columns) with a DateTime index.
        :type prices_df: pd.DataFrame

        :param row_span: The time span of each row in the DataFrame (e.g., daily, weekly, monthly).
        :type row_span: CandlespanEnum

        :param start_date: The start date for the KPI calculations. If None, uses the earliest date in prices_df.
        :type start_date: pd.Timestamp | None
        
        :param end_date: The end date for the KPI calculations. If None, uses the latest date in prices_df.
        :type end_date: pd.Timestamp | None
        
        :raises ValueError: If prices_df is empty.
        :raises TypeError: If prices_df index is not a DateTimeIndex.
        :raises ValueError: If start_date is later than end_date.
        """
        if prices_df.empty:
            raise ValueError("prices_df cannot be empty.")

        if not pd.api.types.is_datetime64_any_dtype(prices_df.index):
            raise TypeError("prices_df index must be a DateTimeIndex.")
        
        if start_date is not None and end_date is not None and start_date > end_date:
            raise ValueError("start_date cannot be later than end_date.")
        
        if start_date is None:
            start_date = prices_df.index.min()
        
        if end_date is None:
            end_date = prices_df.index.max()

        self.__start_date: pd.Timestamp = DataFrameDateIndexHelper.get_nearest_date(prices_df.index, start_date)
        self.__end_date: pd.Timestamp = DataFrameDateIndexHelper.get_nearest_date(prices_df.index, end_date)

        if row_span.value not in CandlespanEnum.values():
            raise ValueError(f"Unsupported row_span. Supported row spans are: {CandlespanEnum.values()}")
        
        self.__row_span: CandlespanEnum = row_span

        self.__prices_df: pd.DataFrame = prices_df

    # Getters
    @property
    def prices_df(self) -> pd.DataFrame:
        return self.__date_bound_prices_df()

    @property
    def start_date(self) -> pd.Timestamp:
        return self.__start_date

    @property
    def end_date(self) -> pd.Timestamp:
        return self.__end_date

    @property
    def date_range(self) -> pd.DatetimeIndex:
        return self.__date_bound_prices_df().index
    
    @property
    def row_span(self) -> CandlespanEnum:
        return self.__row_span


    # Chainable Setters
    @start_date.setter
    def start_date(self, start_date: pd.Timestamp) -> 'RollingKPICalculator':
        if start_date > self.end_date:
            raise ValueError("start_date cannot be later than existing end_date.")

        self.__start_date = start_date
        self.__after_property_update()
        return self


    @end_date.setter
    def end_date(self, end_date: pd.Timestamp) -> 'RollingKPICalculator':
        if end_date < self.start_date:
            raise ValueError("end_date cannot be earlier than existing start_date.")

        self.__end_date = end_date
        self.__after_property_update()
        return self
    

    # Cached properties
    @cached_property
    def __cached_cumulative_cagrs(self) -> pd.DataFrame:
        prices_df: pd.DataFrame = self.__date_bound_prices_df()
        periods_per_year: int = CandlespanEnum.periods_per_year(self.__row_span)
        
        cumulative_years_series = pd.Series(
            data=(np.arange(0, len(prices_df)) / periods_per_year),
            index=prices_df.index
        )
        cumulative_years: np.ndarray = cumulative_years_series.values.reshape(-1, 1)        # Reshape to ensure it is column vector for broadcasting
        safe_years: np.ndarray = np.where(cumulative_years <= 0, np.nan, cumulative_years)  # Replace cumulative_years <= 0 with np.nan to avoid division by zero

        start_prices: pd.Series = pd.Series(prices_df.loc[self.__start_date])               # Get the prices at the start date for each instrument

        cumulative_cagrs_df = prices_df.div(start_prices).pow(1 / safe_years) - 1
        return cumulative_cagrs_df


    @cached_property
    def __cached_cumulative_max_drawdowns(self) -> pd.DataFrame:
        cumulative_returns_df = self.__date_bound_prices_df().pct_change().fillna(0.0).add(1.0).cumprod()
        cumulative_peaks_df = cumulative_returns_df.cummax()
        max_drawdowns_df = cumulative_peaks_df.sub(cumulative_returns_df).div(cumulative_peaks_df).cummax(axis=0)
        return max_drawdowns_df
    

    @cached_property
    def __cached_cumulative_calamar_ratios(self) -> pd.DataFrame:
        cagrs_df = self.__cached_cumulative_cagrs
        max_drawdowns_df = self.__cached_cumulative_max_drawdowns
        calamar_ratios_df = cagrs_df.div(max_drawdowns_df)
        return calamar_ratios_df
    

    @cached_property
    def __cached_cumulative_annualized_volatilities(self) -> pd.DataFrame:
        return self.__cumulative_annualized_volatility_df(downside=False)


    @cached_property
    def __cached_cumulative_annualized_downside_volatilities(self) -> pd.DataFrame:
        return self.__cumulative_annualized_volatility_df(downside=True)
    

    # Cumulative KPI methods
    def cumulative_cagrs(self) -> pd.DataFrame:
        """
        Calculate the cumulative CAGR for each instrument in the prices DataFrame.

        :return: A DataFrame containing the cumulative CAGR (cumulative by date) for each instrument.
        :rtype: pd.DataFrame
        """
        return self.__cached_cumulative_cagrs


    def cumulative_max_drawdowns(self) -> pd.DataFrame:
        """
        Calculate the cumulative maximum drawdown for each instrument in the prices DataFrame.
        
        :return: A DataFrame containing the cumulative maximum drawdown (cumulative by date) for each instrument.
        :rtype: pd.DataFrame
        """
        return self.__cached_cumulative_max_drawdowns


    def cumulative_calamar_ratios(self) -> pd.DataFrame:
        """
        Calculate the cumulative Calmar Ratio for each instrument in the prices DataFrame.
        
        :return: A DataFrame containing the cumulative Calmar Ratio (cumulative by date) for each instrument.
        :rtype: pd.DataFrame
        """
        return self.__cached_cumulative_calamar_ratios


    def cumulative_annualized_volatilities(self) -> pd.DataFrame:
        """
        Calculate the annualized volatility for each instrument in the prices DataFrame.

        :return: A DataFrame containing the cumulative annualized volatilities (cumulative by date) for each instrument.
        :rtype: pd.DataFrame
        """
        return self.__cached_cumulative_annualized_volatilities


    def cumulative_annualized_downside_volatilities(self) -> pd.DataFrame:
        """
        Calculate the annualized downside volatility for each instrument in the prices DataFrame.

        :return: A DataFrame containing the cumulative annualized downside volatility (cumulative by date) for each instrument.
        :rtype: pd.DataFrame
        """
        return self.__cached_cumulative_annualized_downside_volatilities


    def cumulative_sharpe_ratios(self, risk_free_rate: float) -> pd.DataFrame:
        """
        Calculate the cumulative Sharpe Ratio for each instrument in the prices DataFrame.

        :param risk_free_rate: The risk-free rate to be used in the calculation.
        :type risk_free_rate: float

        :return: A DataFrame containing the cumulative Sharpe Ratios (cumulative by date) for each instrument.
        :rtype: pd.DataFrame
        """
        return self.cumulative_cagrs().sub(risk_free_rate).div(self.cumulative_annualized_volatilities())


    def cumulative_sortino_ratios(self, risk_free_rate: float) -> pd.DataFrame:
        """
        Calculate the cumulative Sortino Ratio for each instrument in the prices DataFrame.

        :param risk_free_rate: The risk-free rate to be used in the calculation.
        :type risk_free_rate: float

        :return: A DataFrame containing the cumulative Sortino Ratios (cumulative by date) for each instrument.
        :rtype: pd.DataFrame
        """
        return self.cumulative_cagrs().sub(risk_free_rate).div(self.cumulative_annualized_downside_volatilities())
    

    # Private methods
    def __cumulative_annualized_volatility_df(self, downside: bool = False) -> pd.DataFrame:
        """
        Calculate the annualized volatility for each instrument in the returns DataFrame.

        :param downside: If True, calculate downside volatility; otherwise, calculate total volatility.
        :type downside: bool

        :return: A DataFrame containing the annualized volatility for each instrument.
        :rtype: pd.DataFrame
        """
        returns_df = self.__date_bound_prices_df().pct_change().fillna(0.0)

        volatility_df = pd.DataFrame(index=returns_df.index, columns=returns_df.columns, dtype=float)
        for date in returns_df.index:
            start_date_idx, current_date_idx = DataFrameDateIndexHelper.resolve_date_range_to_idx_range(
                datetime_index=returns_df.index,
                from_date=self.__start_date,
                until_date=date
            )
            volatility_df.loc[date] = KPICalculator.non_annualized_volatility(returns_df.iloc[start_date_idx:current_date_idx + 1], downside=downside)

        # Convert non-annualized volatility to annualized volatility based on the row span
        multiplier: float = np.sqrt(CandlespanEnum.periods_per_year(self.__row_span))
        return volatility_df * multiplier
        

    def __date_bound_prices_df(self) -> pd.DataFrame:
        """
        Get a DataFrame of prices bounded by the specified date range.

        :return: A DataFrame containing prices within the specified date range.
        :rtype: pd.DataFrame
        """
        start_date_idx, end_date_idx = DataFrameDateIndexHelper.resolve_date_range_to_idx_range(
            datetime_index=self.__prices_df.index,
            from_date=self.__start_date,
            until_date=self.__end_date
        )
        return self.__prices_df.iloc[start_date_idx:end_date_idx + 1]

    
    def __clear_cached_properties(self) -> None:
        """
        Clear cached properties to ensure they are recalculated when accessed next.
        """
        self.__dict__.pop('__cached_cumulative_cagrs', None)
        self.__dict__.pop('__cached_cumulative_max_drawdowns', None)
        self.__dict__.pop('__cached_cumulative_calamar_ratios', None)
        self.__dict__.pop('__cached_cumulative_annualized_volatilities', None)
        self.__dict__.pop('__cached_cumulative_annualized_downside_volatilities', None)

    
    def __after_property_update(self) -> None:
        self.__clear_cached_properties()
