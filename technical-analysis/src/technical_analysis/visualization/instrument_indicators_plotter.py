from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

import numpy as np

import pandas as pd

from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.indicators.instrument_indicators import InstrumentIndicators
from technical_analysis.models.instrument import Instrument


class InstrumentIndicatorsPlotter:
    """
    A class to plot technical indicators for a given instrument.
    """

    def __init__(self, instrument: Instrument):
        self.__instrument_indicators = InstrumentIndicators(instrument)


    # Getters
    @property
    def instrument(self) -> Instrument:
        return self.__instrument_indicators.instrument
    

    # Chainable Setters
    @instrument.setter
    def instrument(self, instrument: Instrument) -> 'InstrumentIndicatorsPlotter':
        self.__instrument_indicators.instrument = instrument
        return self
    

    # Public Methods
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
        df: pd.DataFrame = self.__instrument_indicators.collect_as_dataframe()

        if 'macd' not in df.columns or 'macd_signal' not in df.columns or 'macd_histogram' not in df.columns:
            self.__instrument_indicators.macd()
            df = self.__instrument_indicators.collect_as_dataframe()

        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None
        ax2: plt.Axes = None
        ax3: plt.Axes = None

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1, 1]})
        fig.suptitle(title if title else f"{self.instrument.instrument_symbol}", fontsize=16)

        # TODO: Remove plotting of price line graph after UI is implemented
        from technical_analysis.visualization.instrument_plotter import InstrumentPlotter
        InstrumentPlotter(self.instrument).subplot_ohlc(ax1, OHLCVUDEnum.CLOSE)
        ax1.set_title("Prices")
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.legend().set_visible(False)

        ax2.plot(df.index, df['macd'], label='MACD', color='blue')
        ax2.plot(df.index, df['macd_signal'], label='Signal Line', color='red')
        ax2.set_title(f"MACD Line & Signal Line")
        ax2.legend()

        ax3.bar(df.index, df['macd_histogram'], color='gray', alpha=0.5, width=1.0, label='Histogram')
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
        df: pd.DataFrame = self.__instrument_indicators.collect_as_dataframe()

        if 'atr' not in df.columns:
            self.__instrument_indicators.atr()
            df = self.__instrument_indicators.collect_as_dataframe()
        
        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None
        ax2: plt.Axes = None

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        fig.suptitle(title if title else f"{self.instrument.instrument_symbol}", fontsize=16)

        # TODO: Remove plotting of price line graph after UI is implemented
        from technical_analysis.visualization.instrument_plotter import InstrumentPlotter
        InstrumentPlotter(self.instrument).subplot_ohlc(ax1, OHLCVUDEnum.CLOSE)
        ax1.set_title("Prices")
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.legend().set_visible(False)

        ax2.plot(df.index, df['atr'], label='ATR', color='blue')
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
        df: pd.DataFrame = self.__instrument_indicators.collect_as_dataframe()

        if 'middle_boll_band' not in df.columns or 'upper_boll_band' not in df.columns or 'lower_boll_band' not in df.columns or 'band_width' not in df.columns:
            self.__instrument_indicators.bollinger_bands()
            df = self.__instrument_indicators.collect_as_dataframe()

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
        from technical_analysis.visualization.instrument_plotter import InstrumentPlotter
        InstrumentPlotter(self.instrument).subplot_ohlc(ax1, OHLCVUDEnum.CLOSE)

        ax1.plot(df.index, df['middle_boll_band'], label='Middle Band', color='blue')
        ax1.plot(df.index, df['upper_boll_band'], label='Upper Band', color='red')
        ax1.plot(df.index, df['lower_boll_band'], label='Lower Band', color='green')
        ax1.set_title("Prices")
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.legend().set_visible(True)

        if ax2:
            ax2.plot(df.index, df['band_width'], label='Band Width', color='brown')
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
        df: pd.DataFrame = self.__instrument_indicators.collect_as_dataframe()

        if 'rsi' not in df.columns:
            self.__instrument_indicators.rsi()
            df = self.__instrument_indicators.collect_as_dataframe()

        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None
        ax2: plt.Axes = None

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        fig.suptitle(title if title else f"{self.instrument.instrument_symbol}", fontsize=16)

        # TODO: Remove plotting of price line graph after UI is implemented
        from technical_analysis.visualization.instrument_plotter import InstrumentPlotter
        InstrumentPlotter(self.instrument).subplot_ohlc(ax1, OHLCVUDEnum.CLOSE)
        ax1.set_title("Prices")
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.legend().set_visible(False)

        ax2.plot(df.index, df['rsi'], label='RSI', color='green')
        ax2.plot(df.index, np.repeat([70], df.index.size), color='purple')
        ax2.plot(df.index, np.repeat([30], df.index.size), color='purple')
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
        df: pd.DataFrame = self.__instrument_indicators.collect_as_dataframe()

        if 'adx' not in df.columns:
            self.__instrument_indicators.adx()
            df = self.__instrument_indicators.collect_as_dataframe()

        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None
        ax2: plt.Axes = None

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        fig.suptitle(title if title else f"{self.instrument.instrument_symbol}", fontsize=16)

        # TODO: Remove plotting of price line graph after UI is implemented
        from technical_analysis.visualization.instrument_plotter import InstrumentPlotter
        InstrumentPlotter(self.instrument).subplot_ohlc(ax1, OHLCVUDEnum.CLOSE)
        ax1.set_title("Prices")
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.legend().set_visible(False)

        ax2.plot(df.index, df['adx'], label='ADX', color='blue')
        ax2.plot(df.index, np.repeat([25], df.index.size), color='purple')
        ax2.plot(df.index, np.repeat([50], df.index.size), color='orange')
        ax2.plot(df.index, np.repeat([75], df.index.size), color='green')
        ax2.set_title(f"ADX Line")
        ax2.legend().set_visible(False)

        ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
