import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

import pandas as pd

from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.indicators.indicator_calculator import IndicatorCalculator
from technical_analysis.models.candlesticks import Candlesticks
from technical_analysis.models.instrument import Instrument
from technical_analysis.models.renko import Renko


class InstrumentIndicators:
    """
    A class to represent all technical indicators.
    This class is responsible for providing technical indicators on the data store's instrument it is configured with.
    """

    def __init__(
        self,
        source_instrument: Instrument
    ):
        if not isinstance(source_instrument, Instrument):
            raise TypeError("source_instrument must be an instance of Instrument or its subclasses.")
        
        self.__instrument: Instrument = source_instrument

        if isinstance(self.__instrument, Candlesticks):
            self.__df: pd.DataFrame = self.__instrument.candle_df
        elif isinstance(self.__instrument, Renko):
            self.__df: pd.DataFrame = self.__instrument.renko_df
        elif isinstance(self.__instrument, Instrument):
            self.__df: pd.DataFrame = self.__instrument.ohlcv_df
        else:
            raise TypeError("InstrumentIndicators support is currently limited to Candlesticks, Renko, and Instrument.")


    # Getters
    @property
    def instrument(self) -> Instrument:
        return self.__instrument
    

    # Chainable Setters
    @instrument.setter
    def instrument(self, source_instrument: Instrument) -> 'InstrumentIndicators':
        self.__instrument = source_instrument
        return self


    # Public Methods
    def collect_as_dataframe(self) -> pd.DataFrame:
        """
        Returns the dataframe (with all the technical indicators if calculated).
        
        :return: The dataframe with all the technical indicators if calculated.
        :rtype: pd.DataFrame
        """
        return self.__df
    

    def macd(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> 'InstrumentIndicators':
        """
        Calculate the MACD (Moving Average Convergence Divergence) for the configured instrument symbol, and include it in the dataframe.
        
        The MACD is calculated using the following formula:
            MACD = fast_period_EMA - slow_period_EMA
            MACD Signal line = signal_period_EMA of the MACD

        :param slow_period: The period for the slow EMA. Default is 26.
        :type slow_period: int
        
        :param fast_period: The period for the fast EMA. Default is 12.
        :type fast_period: int
        
        :param signal_period: The period for the signal line. Default is 9.
        :type signal_period: int

        :return: self
        :rtype: InstrumentIndicators
        """
        self.__df = IndicatorCalculator.macd(self.__df, fast_period, slow_period, signal_period)
        return self
    

    def atr(
        self,
        window: int = 14
    ) -> 'InstrumentIndicators':
        """
        Calculate the ATR (Average true Range) for the configured instrument symbol, and include it in the dataframe.
        
        The ATR is calculated using the following formula:
            TR = max((high - low), abs(high - prev_close), abs(low - prev_close))
            ATR = EMA(TR)

        :param window: The period for the EMA of the True Range(TR). Default is 14.
        :type window: int

        :return: self
        :rtype: InstrumentIndicators
        """
        self.__df = IndicatorCalculator.atr(self.__df, window)
        return self
    

    def bollinger_bands(
        self,
        window: int = 20
    ) -> 'InstrumentIndicators':
        """
        Calculate the Bollinger band data for the configured instrument symbol, and include it in the dataframe.
        
        The Bollinger band data is calculated using the following formula:
            middle_boll_band = window_period_SMA(close)
            upper_boll_band = middle_boll_band + 2*window_period_std(close) [for population]
            lower_boll_band = middle_boll_band - 2*window_period_std(close) [for population]

        :param window: The period for the SMA for the middle_boll_band. Default is 20.
        :type window: int

        :return: self
        :rtype: InstrumentIndicators
        """
        self.__df = IndicatorCalculator.bollinger_bands(self.__df, window)
        return self
    

    def rsi(
        self,
        window: int = 14
    ) -> 'InstrumentIndicators':
        """
        Calculate the RSI (Relative Strength Index) for the configured instrument symbol, and include it in the dataframe.
        
        The RSI is calculated using the following formulae:
            change = current_close - previous_close
            gain = change >= 0 ? change : 0
            loss = change < 0 ? -1*change : 0
            avg_gain = rma(gain, window) (Reference - https://www.tradingcode.net/tradingview/relative-moving-average/#calculation-process)
            avg_loss = rma(loss, window) (Reference - https://www.tradingcode.net/tradingview/relative-moving-average/#calculation-process)
            rs = avg_gain/avg_loss
            rsi = 100 - (100 / (1 + rs))

        :param window: The period for all the operations Default is 14.
        :type window: int

        :return: self
        :rtype: InstrumentIndicators
        """
        self.__df = IndicatorCalculator.rsi(self.__df, window)
        return self
    

    def adx(
        self,
        window: int = 14
    ) -> 'InstrumentIndicators':
        """
        Calculate the ADX (Average Directional Index) for the configured instrument symbol, and include it in the dataframe.
        
        The ADX is calculated using the following formulae:
            DM_up = (curr_high - prev_high) > (prev_low - curr_low) ? max((curr_high - prev_high), 0) : 0
            DM_down = (curr_high - prev_high) < (prev_low - curr_low) ? max((prev_low - curr_low), 0) : 0
            DI_up = 100*EMA(DM_up)/ATR
            DI_down = 100*EMA(DM_down)/ATR
            DX = abs((DI_up - DI_down)/(DI_up + DI_down))
            ADX = 100*EMA(DX)

        :param window: The period for all the operations; Default is 14.
        :type window: int

        :return: self
        :rtype: InstrumentIndicators
        """
        self.__df = IndicatorCalculator.adx(self.__df, window)
        return self