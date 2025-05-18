from typing import Literal
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from technical_analysis.components.alpha_vantage import DataStoreComponent
from technical_analysis.models.ohlcv_enum import OHLCVEnum


class PriceCharterComponent:
    """
    A component to plot the price chart of a stock in dfferent formats
    """

    def __init__(
        self,
        instrument_symbol: str,
        financial_data_store: DataStoreComponent
    ):
        self.__store: DataStoreComponent = financial_data_store

        if not self.__store.is_instrument_valid(instrument_symbol):
            print(f"[ERROR] {self.__class__.__name__} class Initialization Error")
            error_message: str = f"Instrument {instrument_symbol} is invalid"
            raise ValueError(error_message)
    
        self.__instrument_symbol: str = instrument_symbol


    # Getters
    @property
    def data_store(self) -> DataStoreComponent:
        return self.__store
    
    @property
    def instrument_symbol(self) -> str:
        return self.__instrument_symbol
    

    # Chainable Setters
    @data_store.setter
    def data_store(self, data_store: DataStoreComponent) -> 'PriceCharterComponent':
        self.__store = data_store
        return self
    
    @instrument_symbol.setter
    def instrument_symbol(self, instrument_symbol: str) -> 'PriceCharterComponent':
        self.__instrument_symbol = instrument_symbol
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

        fig, ax1 = plt.subplots(1, 1, figsize=(14, 8), sharex=True)
        fig.suptitle(title if title else f"{self.__instrument_symbol}", fontsize=16)

        self.subplot_ohlc(ax1, OHLCVEnum.CLOSE)
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

        fig, ax1 = plt.subplots(1, 1, figsize=(14, 8), sharex=True)
        fig.suptitle(title if title else f"{self.__instrument_symbol}", fontsize=16)

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
        metric: Literal[OHLCVEnum.CLOSE, OHLCVEnum.OPEN, OHLCVEnum.HIGH, OHLCVEnum.LOW] = OHLCVEnum.CLOSE
    ) -> None:
        """
        Subplots the OHLC line graph in the given plt.Axes

        :param ax: The axes along which to plot
        :type ax: plt.Axes

        :param metric: O, H, L, or C of the OHLCVEnum type; Defaults to C
        :type metric: Literal[OHLCVEnum.CLOSE, OHLCVEnum.OPEN, OHLCVEnum.HIGH, OHLCVEnum.LOW]

        :return: None
        :rtype: None

        :raises ValueError: Unsupported Metric, when metric is anything other than O, H, L or C

        Note: 
        1. Does not show the plot. That is the responsibility of the plot method that calls this subplot method
        2. Hides the legend since it only plots one line for the (ohlc) price. The plot method calling this method can handle the legend visibility based on need
        """
        if metric.value not in OHLCVEnum.price_values():
            raise ValueError(f"Unsupported Metric {metric.value} for ohlc line plot")
        
        metric_series = self.data_store.get_ohlcv_df_for_instrument(self.__instrument_symbol)[metric.value]
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
        volume_series = self.data_store.get_ohlcv_df_for_instrument(self.__instrument_symbol)[OHLCVEnum.VOLUME.value]
        ax.bar(volume_series.index, volume_series.values, 35.0, label=OHLCVEnum.VOLUME.value.lower(), linestyle='-', color='gray', alpha=0.5)