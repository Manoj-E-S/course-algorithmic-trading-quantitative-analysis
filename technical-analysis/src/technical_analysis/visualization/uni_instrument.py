from typing import Literal

from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

import pandas as pd

from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.models.candlesticks import Candlesticks
from technical_analysis.models.instrument import Instrument
from technical_analysis.models.renko import Renko


class InstrumentCharter:
    """
    A component to plot the price/volume charts of an instrument in different formats
    """

    def __init__(
        self,
        source_instrument: Instrument,
    ):
        if not isinstance(source_instrument, Instrument):
            raise TypeError("source_instrument must be an instance of Instrument or its subclasses.")
        
        self.__instrument: Instrument = source_instrument

        if isinstance(source_instrument, Candlesticks):
            self.__df: pd.DataFrame = source_instrument.get_candlesticks()
        elif isinstance(source_instrument, Renko):
            self.__df = source_instrument.get_renko()
        else:
            raise TypeError("InstrumentCharter support is currently limited to Candlesticks and Renko.")


    # Getters
    @property
    def instrument(self) -> Instrument:
        return self.__instrument
    

    # Chainable Setters
    @instrument.setter
    def instrument(self, source_instrument: Instrument) -> 'InstrumentCharter':
        self.__instrument = source_instrument
        return self

    def plot_price_line(
        self,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plot the line chart of price for the configured instrument symbol, based on data from the configured store.

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        
        :return: None
        :rtype: None
        """
        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None

        fig, ax1 = plt.subplots(1, 1, figsize=(14, 8), sharex=True)
        fig.suptitle(title if title else f"{self.instrument.instrument_symbol}", fontsize=16)

        self.subplot_ohlc(ax1, OHLCVUDEnum.CLOSE)
        ax1.set_title("Prices")
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.legend().set_visible(False)

        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()

    
    def plot_volume_bar(
        self,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plot the bar chart of volumes for the configured instrument symbol, based on data from the configured store.

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        
        :return: None
        :rtype: None
        """
        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None

        fig, ax1 = plt.subplots(1, 1, figsize=(14, 8), sharex=True)
        fig.suptitle(title if title else f"{self.instrument.instrument_symbol}", fontsize=16)

        self.subplot_volume(ax1)
        ax1.set_title("Volumes")
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.legend().set_visible(False)

        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()

    
    def subplot_ohlc(
        self,
        ax: plt.Axes,
        metric: Literal[OHLCVUDEnum.CLOSE, OHLCVUDEnum.OPEN, OHLCVUDEnum.HIGH, OHLCVUDEnum.LOW] = OHLCVUDEnum.CLOSE
    ) -> None:
        """
        Subplots the OHLC line graph in the given plt.Axes

        :param ax: The axes along which to plot
        :type ax: plt.Axes

        :param metric: O, H, L, or C of the OHLCVUDEnum type; Defaults to C
        :type metric: Literal[OHLCVUDEnum.CLOSE, OHLCVUDEnum.OPEN, OHLCVUDEnum.HIGH, OHLCVUDEnum.LOW]

        :return: None
        :rtype: None

        :raises ValueError: Unsupported Metric, when metric is anything other than O, H, L or C

        Note: 
        1. Does not show the plot. That is the responsibility of the plot method that calls this subplot method
        2. Hides the legend since it only plots one line for the (ohlc) price. The plot method calling this method can handle the legend visibility based on need
        """
        if metric.value not in OHLCVUDEnum.price_values():
            raise ValueError(f"Unsupported Metric {metric.value} for ohlc line plot")
        
        metric_series = self.__df[metric.value]
        ax.plot(metric_series.index, metric_series.values, label=f'{metric.value.capitalize()} prices', linestyle='-', color='black', alpha=0.6)


    def subplot_volume(
        self,
        ax: plt.Axes
    ) -> None:
        """
        Subplots the Volume bar graph in the given plt.Axes

        :param ax: The axes along which to plot
        :type ax: plt.Axes

        :return: None
        :rtype: None

        Note: 
        1. Does not show the plot, that is the responsibility of the plot method that calls this subplot method
        """
        volume_series = self.__df[OHLCVUDEnum.VOLUME.value]
        ax.bar(volume_series.index, volume_series.values, 35.0, label=OHLCVUDEnum.VOLUME.value.lower(), linestyle='-', color='gray', alpha=0.5)