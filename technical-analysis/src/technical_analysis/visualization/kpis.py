from functools import cached_property
import pandas as pd

from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.kpis.kpi_calculator import KpiCalculator
from technical_analysis.models.instrument import Instrument


class InstrumentKPIs:
    """
    A class to represent key performance indicators (KPIs) for a financial instrument.
    """

    def __init__(
        self,
        source_instrument: Instrument
    ):
        if not isinstance(source_instrument, Instrument):
            raise TypeError("source_instrument must be an instance of Instrument or its subclasses.")
        
        self.__instrument: Instrument = source_instrument
        self.__after_property_update()
    

    # Getters
    @property
    def instrument(self) -> Instrument:
        return self.__instrument


    # Chainable Setters   
    @instrument.setter
    def instrument(self, instrument: Instrument) -> 'InstrumentKPIs':
        self.__instrument = instrument
        self.__after_property_update()
        return self
    

    # Cached callable properties
    @cached_property
    def computed_or_cached_CAGR(self) -> float:
        ohlcv_df: pd.DataFrame = self.__instrument.ohlcv_df
        if ohlcv_df.empty:
            return 0.0

        start_date_idx: int = 0
        end_date_idx: int = -1
        periods: float = self.__get_years_between_date_indices(ohlcv_df, start_date_idx, end_date_idx)

        return KpiCalculator.cagr(
            start_price = ohlcv_df[OHLCVUDEnum.CLOSE.value].iloc[start_date_idx],
            end_price = ohlcv_df[OHLCVUDEnum.CLOSE.value].iloc[end_date_idx],
            periods = periods
        )
    

    @cached_property
    def computed_or_cached_MAX_DRAWDOWN(self) -> float:
        cumulative_returns: pd.Series = self.__instrument.cumulative_returns_series
        if cumulative_returns.empty:
            return 0.0
        
        return KpiCalculator.max_drawdown(cumulative_returns)


    @cached_property
    def computed_or_cached_CALMAR_RATIO(self) -> float:
        annual_returns: float = self.cagr()
        max_drawdown: float = self.max_drawdown()

        return KpiCalculator.calmar_ratio(annual_returns, max_drawdown)
    

    # Public methods
    def cagr(self) -> float:
        """
        Calculate the Compound Annual Growth Rate (CAGR) of the instrument.
        
        :return: The CAGR as a float.
        """
        return self.computed_or_cached_CAGR


    def max_drawdown(self) -> float:
        """
        Calculate the maximum drawdown of the instrument.
        
        :return: The maximum drawdown as a float.
        """
        return self.computed_or_cached_MAX_DRAWDOWN


    def calmar_ratio(self) -> float:
        """
        Calculate the Calmar Ratio of the instrument.
        
        :return: The Calmar Ratio as a float.
        """
        return self.computed_or_cached_CALMAR_RATIO


    def annualized_volatility(self, downside: bool = False) -> float:
        """
        Calculate the annualized volatility of the instrument.
        
        :param downside: If True, calculate downside volatility; otherwise, calculate total volatility.
        :type downside: bool
        
        :return: The annualized volatility as a float.
        :rtype: float
        """
        returns_series: pd.Series = self.__instrument.returns_series

        if returns_series.empty:
            return 0.0
        
        volatility = KpiCalculator.non_annualized_volatility(returns_series, downside=downside)
        
        if self.instrument.candle_span == CandlespanEnum.DAILY:
            return volatility * (252 ** 0.5)
        elif self.instrument.candle_span == CandlespanEnum.WEEKLY:
            return volatility * (52 ** 0.5)
        elif self.instrument.candle_span == CandlespanEnum.MONTHLY:
            return volatility * (12 ** 0.5)
        else:
            err: str = f"Unsupported candle span. Suppported candle spans are: {CandlespanEnum.values()}"
            raise ValueError(err)
    

    def sharpe_ratio(self, risk_free_rate: float) -> float:
        """
        Calculate the Sharpe Ratio of the instrument.

        :param risk_free_rate: The risk-free rate to be used in the calculation.
        :type risk_free_rate: float
        
        :return: The Sharpe Ratio as a float.
        :rtype: float
        """
        expected_returns: float = self.cagr()
        volatility: float = self.annualized_volatility()

        return KpiCalculator.sharpe_ratio(expected_returns, risk_free_rate, volatility)
    

    def sortino_ratio(self, risk_free_rate: float) -> float:
        """
        Calculate the Sortino Ratio of the instrument.
        
        :param risk_free_rate: The risk-free rate to be used in the calculation.
        :type risk_free_rate: float
        
        :return: The Sortino Ratio as a float.
        :rtype: float
        """
        expected_returns: float = self.cagr()
        downside_volatility: float = self.annualized_volatility(downside=True)

        return KpiCalculator.sortino_ratio(expected_returns, risk_free_rate, downside_volatility)


    # Private methods
    def __get_years_between_date_indices(self, ohlcv_df: pd.DataFrame, start_date_idx: int = 0, end_date_idx: int = -1) -> float:
        """
        Get the number of years between two date indices in the OHLCV DataFrame.

        :param ohlcv_df: The OHLCV DataFrame containing the instrument data.
        :type ohlcv_df: pd.DataFrame
        
        :param start_date_idx: The index of the start date in the DataFrame. Default is 0.
        :type start_date_idx: int
        
        :param end_date_idx: The index of the end date in the DataFrame. Default is -1 (last index).
        :type end_date_idx: int
        
        :return: The number of years between the two dates as a float.
        :rtype: float
        """
        start_date: pd.Timestamp = ohlcv_df.index[start_date_idx]
        end_date: pd.Timestamp = ohlcv_df.index[end_date_idx]

        if self.instrument.candle_span == CandlespanEnum.DAILY:
            return (end_date - start_date).days / 252
        elif self.instrument.candle_span == CandlespanEnum.WEEKLY:
            return (end_date - start_date).days / 52
        elif self.instrument.candle_span == CandlespanEnum.MONTHLY:
            return (end_date - start_date).days / 12
        else:
            err: str = f"Unsupported candle span. Suppported candle spans are: {CandlespanEnum.values()}"
            raise ValueError(err)
        
    
    def __after_property_update(self) -> None:
        """
        This method is called after any property update to invalidate cached properties, and perform any other actions needed.
        """
        self.__instrument_type = type(self.__instrument).__name__
        self.__invalidate_cached_properties()


    def __invalidate_cached_properties(self) -> None:
        """
        Invalidate cached properties.
        """
        for attr in dir(self):
            if isinstance(getattr(self, attr), cached_property):
                delattr(self, attr)
