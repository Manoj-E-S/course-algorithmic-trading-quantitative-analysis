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


class TechniCharter:
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
            self.__df: pd.DataFrame = self.__instrument.get_candlesticks()
        elif isinstance(self.__instrument, Renko):
            self.__df: pd.DataFrame = self.__instrument.get_renko()
        else:
            raise TypeError("TechniCharter support is currently limited to Candlesticks and Renko.")
        
    
    # Getters
    @property
    def instrument(self) -> Instrument:
        return self.__instrument
    

    # Chainable Setters
    @instrument.setter
    def instrument(self, source_instrument: Instrument) -> 'TechniCharter':
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
    ) -> 'TechniCharter':
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
        :rtype: TechniCharter
        """
        self.__df = IndicatorCalculator.macd(self.__df, fast_period, slow_period, signal_period)
        return self
    

    def atr(
        self,
        window: int = 14
    ) -> 'TechniCharter':
        """
        Calculate the ATR (Average true Range) for the configured instrument symbol, and include it in the dataframe.
        
        The ATR is calculated using the following formula:
            TR = max((high - low), abs(high - prev_close), abs(low - prev_close))
            ATR = EMA(TR)

        :param window: The period for the EMA of the True Range(TR). Default is 14.
        :type window: int

        :return: self
        :rtype: TechniCharter
        """
        self.__df = IndicatorCalculator.atr(self.__df, window)
        return self
    

    def bollinger_bands(
        self,
        window: int = 20
    ) -> 'TechniCharter':
        """
        Calculate the Bollinger band data for the configured instrument symbol, and include it in the dataframe.
        
        The Bollinger band data is calculated using the following formula:
            middle_boll_band = window_period_SMA(close)
            upper_boll_band = middle_boll_band + 2*window_period_std(close) [for population]
            lower_boll_band = middle_boll_band - 2*window_period_std(close) [for population]

        :param window: The period for the SMA for the middle_boll_band. Default is 20.
        :type window: int

        :return: self
        :rtype: TechniCharter
        """
        self.__df = IndicatorCalculator.bollinger_bands(self.__df, window)
        return self
    

    def rsi(
        self,
        window: int = 14
    ) -> 'TechniCharter':
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
        :rtype: TechniCharter
        """
        self.__df = IndicatorCalculator.rsi(self.__df, window)
        return self
    

    def adx(
        self,
        window: int = 14
    ) -> 'TechniCharter':
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
        :rtype: TechniCharter
        """
        self.__df = IndicatorCalculator.adx(self.__df, window)
        return self
    

    def plot_macd(
        self,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plot the MACD for the configured instrument symbol.

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        
        :return: None
        :rtype: None
        
        :raises ValueError: If the MACD is not calculated yet.
        """
        if 'macd' not in self.__df.columns or 'macd_signal' not in self.__df.columns or 'macd_histogram' not in self.__df.columns:
            self.macd()
        
        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None
        ax2: plt.Axes = None
        ax3: plt.Axes = None

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1, 1]})
        fig.suptitle(title if title else f"{self.instrument.instrument_symbol}", fontsize=16)

        # TODO: Remove plotting of price line graph after UI is implemented
        from technical_analysis.visualization.uni_instrument import InstrumentCharter
        InstrumentCharter(self.instrument).subplot_ohlc(ax1, OHLCVUDEnum.CLOSE)
        ax1.set_title("Prices")
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.legend().set_visible(False)

        ax2.plot(self.__df.index, self.__df['macd'], label='MACD', color='blue')
        ax2.plot(self.__df.index, self.__df['macd_signal'], label='Signal Line', color='red')
        ax2.set_title(f"MACD Line & Signal Line")
        ax2.legend()

        ax3.bar(self.__df.index, self.__df['macd_histogram'], color='gray', alpha=0.5, width=1.0, label='Histogram')
        ax3.axhline(0, color='black', lw=1, linestyle='--')
        ax3.set_xlabel("Date")
        ax3.set_title("MACD Histogram")
        ax3.legend().set_visible(False)

        ax3.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()


    def plot_atr(
        self,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plot the ATR for the configured instrument symbol.

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        
        :return: None
        :rtype: None
        
        :raises ValueError: If the ATR is not calculated yet.
        """
        if 'atr' not in self.__df.columns:
            self.atr()
        
        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None
        ax2: plt.Axes = None

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        fig.suptitle(title if title else f"{self.instrument.instrument_symbol}", fontsize=16)

        # TODO: Remove plotting of price line graph after UI is implemented
        from technical_analysis.visualization.uni_instrument import InstrumentCharter
        InstrumentCharter(self.instrument).subplot_ohlc(ax1, OHLCVUDEnum.CLOSE)
        ax1.set_title("Prices")
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.legend().set_visible(False)

        ax2.plot(self.__df.index, self.__df['atr'], label='ATR', color='blue')
        ax2.set_title(f"ATR Line")
        ax2.legend().set_visible(False)

        ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()

    
    def plot_bollinger_bands(
        self,
        should_plot_band_width: bool = True,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plot the Bollinger Bands for the configured instrument symbol.

        :param should_plot_band_width: If a separate plot od the band wwidths is required.
        :type should_plot_band_width: bool

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        
        :return: None
        :rtype: None
        
        :raises ValueError: If the Bollinger Bands data is not calculated yet.
        """
        if 'middle_boll_band' not in self.__df.columns or 'upper_boll_band' not in self.__df.columns or 'lower_boll_band' not in self.__df.columns or 'band_width' not in self.__df.columns:
            self.bollinger_bands()
        
        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None
        ax2: plt.Axes = None

        if should_plot_band_width:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(14, 8))
        
        fig.suptitle(title if title else f"{self.instrument.instrument_symbol}", fontsize=16)

        # TODO: Remove plotting of price line graph after UI is implemented
        from technical_analysis.visualization.uni_instrument import InstrumentCharter
        InstrumentCharter(self.instrument).subplot_ohlc(ax1, OHLCVUDEnum.CLOSE)

        ax1.plot(self.__df.index, self.__df['middle_boll_band'], label='Middle Band', color='blue')
        ax1.plot(self.__df.index, self.__df['upper_boll_band'], label='Upper Band', color='red')
        ax1.plot(self.__df.index, self.__df['lower_boll_band'], label='Lower Band', color='green')
        ax1.set_title("Prices")
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.legend().set_visible(True)

        if ax2:
            ax2.plot(self.__df.index, self.__df['band_width'], label='Band Width', color='brown')
            ax2.set_title(f"Band Width")
            ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        else:
            ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()

    
    def plot_rsi(
        self,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plot the RSI for the configured instrument symbol.

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        
        :return: None
        :rtype: None
        
        :raises ValueError: If the RSI is not calculated yet.
        """
        if 'rsi' not in self.__df.columns:
            self.rsi()

        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None
        ax2: plt.Axes = None

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        fig.suptitle(title if title else f"{self.instrument.instrument_symbol}", fontsize=16)

        # TODO: Remove plotting of price line graph after UI is implemented
        from technical_analysis.visualization.uni_instrument import InstrumentCharter
        InstrumentCharter(self.instrument).subplot_ohlc(ax1, OHLCVUDEnum.CLOSE)
        ax1.set_title("Prices")
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.legend().set_visible(False)

        ax2.plot(self.__df.index, self.__df['rsi'], label='RSI', color='green')
        ax2.plot(self.__df.index, np.repeat([70], self.__df.index.size), color='purple')
        ax2.plot(self.__df.index, np.repeat([30], self.__df.index.size), color='purple')
        ax2.set_title(f"RSI")
        ax2.legend().set_visible(False)

        ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()


    def plot_adx(
        self,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plot the ADX for the configured instrument symbol.

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        
        :return: None
        :rtype: None
        
        :raises ValueError: If the ADX is not calculated yet.
        """
        if 'adx' not in self.__df.columns:
            self.adx()
        
        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None
        ax2: plt.Axes = None

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        fig.suptitle(title if title else f"{self.instrument.instrument_symbol}", fontsize=16)

        # TODO: Remove plotting of price line graph after UI is implemented
        from technical_analysis.visualization.uni_instrument import InstrumentCharter
        InstrumentCharter(self.instrument).subplot_ohlc(ax1, OHLCVUDEnum.CLOSE)
        ax1.set_title("Prices")
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.legend().set_visible(False)

        ax2.plot(self.__df.index, self.__df['adx'], label='ADX', color='blue')
        ax2.plot(self.__df.index, np.repeat([25], self.__df.index.size), color='purple')
        ax2.plot(self.__df.index, np.repeat([50], self.__df.index.size), color='orange')
        ax2.plot(self.__df.index, np.repeat([75], self.__df.index.size), color='green')
        ax2.set_title(f"ADX Line")
        ax2.legend().set_visible(False)

        ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()