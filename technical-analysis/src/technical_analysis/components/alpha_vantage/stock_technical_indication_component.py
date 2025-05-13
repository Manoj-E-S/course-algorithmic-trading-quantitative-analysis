import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import pandas as pd

from technical_analysis.components.alpha_vantage import DataStoreComponent
from technical_analysis.models import OHLCVEnum


class StockTechnicalIndicationComponent:
    """
    A class to represent all technical indicators.
    This class is responsible for providing technical indicators on the data store's instrument it is configured with.
    """
    def __init__(
        self,
        financial_data_store: DataStoreComponent,
        instrument_symbol: str
    ):
        self.__store: DataStoreComponent = financial_data_store

        if not self.__store.is_instrument_valid(instrument_symbol):
            print(f"[ERROR] {self.__class__.__name__} class Initialization Error")
            error_message: str = f"Instrument {instrument_symbol} is invalid"
            raise ValueError(error_message)

        self.__instrument_symbol: str = instrument_symbol
        self.__df: pd.DataFrame = self.__store.instrument_ohlcvdf_dict.get(self.__instrument_symbol)
    

    # Getters
    @property
    def data_store(self) -> DataStoreComponent:
        return self.__store
    
    @property
    def instrument_symbol(self) -> str:
        return self.__instrument_symbol
    

    # Chainable Setters
    @data_store.setter
    def data_store(self, data_store: DataStoreComponent) -> 'StockTechnicalIndicationComponent':
        self.__store = data_store
        return self
    
    @instrument_symbol.setter
    def instrument_symbol(self, instrument_symbol: str) -> 'StockTechnicalIndicationComponent':
        self.__instrument_symbol = instrument_symbol
        return self


    # Methods
    def collect(self) -> pd.DataFrame:
        """
        Returns the dataframe with OHLCV columns and indicator columns (if any) for the associated instrument from the associated store.
        """
        return self.__df
    

    def macd(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> 'StockTechnicalIndicationComponent':
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
        :rtype: StockTechnicalIndicationComponent
        """
        self.__df['fast_ema']       = self.__df[self.data_store.metric].ewm(span=fast_period, adjust=False).mean()
        self.__df['slow_ema']       = self.__df[self.data_store.metric].ewm(span=slow_period, adjust=False).mean()
        self.__df['macd']           = self.__df['fast_ema'] - self.__df['slow_ema']
        self.__df['macd_signal']    = self.__df['macd'].ewm(span=signal_period).mean()
        self.__df['macd_histogram'] = self.__df['macd'] - self.__df['macd_signal']

        self.__df.drop(columns=['fast_ema', 'slow_ema'], inplace=True)
        
        return self
    

    def atr(
        self,
        window: int = 14
    ) -> 'StockTechnicalIndicationComponent':
        """
        Calculate the ATR (Average true Range) for the configured instrument symbol, and include it in the dataframe.
        
        The ATR is calculated using the following formula:
            TR = max((high - low), abs(high - prev_close), abs(low - prev_close))
            ATR = EMA(TR)

        :param window: The period for the EMA of the True Range(TR). Default is 14.
        :type window: int

        :return: self
        :rtype: StockTechnicalIndicationComponent
        """
        self.__df["H-L"]    = self.__df[OHLCVEnum.HIGH.value] - self.__df[OHLCVEnum.LOW.value]
        self.__df["H-PC"]   = (self.__df[OHLCVEnum.HIGH.value] - self.__df[OHLCVEnum.CLOSE.value].shift(1)).abs()
        self.__df["L-PC"]   = (self.__df[OHLCVEnum.LOW.value] - self.__df[OHLCVEnum.CLOSE.value].shift(1)).abs()
        self.__df["TR"]     = self.__df[["H-L", "H-PC", "L-PC"]].max(axis='columns', skipna=False)
        self.__df["atr"]    = self.__df["TR"].ewm(span=window).mean()

        self.__df.drop(columns=["H-L", "H-PC", "L-PC", "TR"], inplace=True)

        return self
    

    def plot_main_metric(
        self,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plot the main metric line graph for the configured instrument symbol.

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

        self.__subplot_main_metric(ax1)

        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()


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
            raise ValueError("MACD not calculated yet. Please call the macd() method before plotting.")
        
        plt.style.use(styling)

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1, 1]})
        fig.suptitle(title if title else f"{self.__instrument_symbol}", fontsize=16)

        self.__subplot_main_metric(ax1)

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
            raise ValueError("ATR not calculated yet. Please call the atr() method before plotting.")
        
        plt.style.use(styling)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        fig.suptitle(title if title else f"{self.__instrument_symbol}", fontsize=16)

        self.__subplot_main_metric(ax1)

        ax2.plot(self.__df.index, self.__df['atr'], label='ATR', color='blue')
        ax2.set_title(f"ATR Line")
        ax2.legend().set_visible(False)

        ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()


    def __subplot_main_metric(
        self,
        ax: plt.Axes
    ) -> None:
        """
        Subplots the main metric line graph in the given plt.Axes

        :param ax: The axes along which to plot
        :type ax: plt.Axes

        :return: None
        :rtype: None

        Note: Does not show the plot, that is the responsibility of the plot method that calls this subplot method
        """
        main_df = self.data_store.main_metric_df

        ax.plot(main_df.index, main_df.loc[:, self.__instrument_symbol], label=self.data_store.metric.lower(), linestyle='-', color='black', alpha=0.6)
        ax.set_title(f"{self.data_store.metric.capitalize()}s")
        ax.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax.legend().set_visible(False)