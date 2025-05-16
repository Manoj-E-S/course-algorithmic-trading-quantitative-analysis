import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import numpy as np
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
    

    def bollinger_bands(
        self,
        window: int = 20
    ) -> 'StockTechnicalIndicationComponent':
        """
        Calculate the Bollinger band data for the configured instrument symbol, and include it in the dataframe.
        
        The Bollinger band data is calculated using the following formula:
            middle_boll_band = window_period_SMA(close)
            upper_boll_band = middle_boll_band + 2*window_period_std(close) [for population]
            lower_boll_band = middle_boll_band - 2*window_period_std(close) [for population]

        :param window: The period for the SMA for the middle_boll_band. Default is 20.
        :type window: int

        :return: self
        :rtype: StockTechnicalIndicationComponent
        """
        self.__df["middle_boll_band"]   = self.__df[OHLCVEnum.CLOSE.value].rolling(window).mean()
        self.__df["upper_boll_band"]    = self.__df["middle_boll_band"] + 2 * self.__df[OHLCVEnum.CLOSE.value].rolling(window).std(ddof=0)
        self.__df["lower_boll_band"]    = self.__df["middle_boll_band"] - 2 * self.__df[OHLCVEnum.CLOSE.value].rolling(window).std(ddof=0)
        self.__df["band_width"]         = self.__df["upper_boll_band"] - self.__df["lower_boll_band"]

        return self
    

    def rsi(
        self,
        window: int = 14
    ) -> 'StockTechnicalIndicationComponent':
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
        :rtype: StockTechnicalIndicationComponent
        """
        self.__df['close_change']   = self.__df[OHLCVEnum.CLOSE.value] - self.__df[OHLCVEnum.CLOSE.value].shift(1)
        self.__df['gain']           = self.__df['close_change'].apply(lambda x: x if x >= 0 else 0.0)
        self.__df['loss']           = self.__df['close_change'].apply(lambda x: -x if x < 0 else 0.0)
        self.__df['avg_gain']       = self.__df['gain'].ewm(alpha=(1/window)).mean()
        self.__df['avg_loss']       = self.__df['loss'].ewm(alpha=(1/window)).mean()
        self.__df['rs']             = self.__df['avg_gain'] / self.__df['avg_loss']
        self.__df['rsi']            = 100 - (100 / ( 1 + self.__df['rs']))

        self.__df.drop(columns=['close_change', 'gain', 'loss', 'avg_gain', 'avg_loss', 'rs'], inplace=True)
        
        return self
    

    def adx(
        self,
        window: int = 14
    ) -> 'StockTechnicalIndicationComponent':
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
        :rtype: StockTechnicalIndicationComponent
        """
        do_not_delete_atr_post_calculation: bool = False
        if 'atr' in self.__df.columns:
            do_not_delete_atr_post_calculation = True
        else:
            self.atr()
        
        self.__df['hh']         = self.__df[OHLCVEnum.HIGH.value] - self.__df[OHLCVEnum.HIGH.value].shift(1)
        self.__df['ll']         = self.__df[OHLCVEnum.LOW.value].shift(1) - self.__df[OHLCVEnum.LOW.value]

        self.__df['dm_up']      = self.__df[['hh','ll']].apply(lambda row: max(row['hh'], 0) if row['hh'] > row['ll'] else 0, axis='columns')
        self.__df['dm_down']    = self.__df[['hh','ll']].apply(lambda row: max(row['ll'], 0) if row['ll'] > row['hh'] else 0, axis='columns')

        self.__df['di_up']      = (100/self.__df['atr']) * self.__df['dm_up'].ewm(alpha=(1/window)).mean()
        self.__df['di_down']    = (100/self.__df['atr']) * self.__df['dm_down'].ewm(alpha=(1/window)).mean()

        self.__df['dx']         = ((self.__df['di_up'] - self.__df['di_down']) / (self.__df['di_up'] + self.__df['di_down'])).abs()

        self.__df['adx']        = 100 * self.__df['dx'].ewm(alpha=(1/window)).mean()

        self.__df.drop(columns=['hh', 'll', 'dm_up', 'dm_down', 'di_up', 'di_down', 'dx'], inplace=True)
        if not do_not_delete_atr_post_calculation:
            self.__df.drop(columns=['atr'], inplace=True)
        
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
            raise ValueError("Bollinger Bands not calculated yet. Please call the bollinger_bands() method before plotting.")
        
        plt.style.use(styling)

        ax2: plt.Axes = None
        if should_plot_band_width:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(14, 8))
        
        fig.suptitle(title if title else f"{self.__instrument_symbol}", fontsize=16)

        self.__subplot_main_metric(ax1)

        ax1.plot(self.__df.index, self.__df['middle_boll_band'], label='Middle Band', color='blue')
        ax1.plot(self.__df.index, self.__df['upper_boll_band'], label='Upper Band', color='red')
        ax1.plot(self.__df.index, self.__df['lower_boll_band'], label='Lower Band', color='green')
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
            raise ValueError("RSI not calculated yet. Please call the rsi() method before plotting.")
        
        plt.style.use(styling)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        fig.suptitle(title if title else f"{self.__instrument_symbol}", fontsize=16)

        self.__subplot_main_metric(ax1)

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
            raise ValueError("ADX not calculated yet. Please call the adx() method before plotting.")
        
        plt.style.use(styling)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        fig.suptitle(title if title else f"{self.__instrument_symbol}", fontsize=16)

        self.__subplot_main_metric(ax1)

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