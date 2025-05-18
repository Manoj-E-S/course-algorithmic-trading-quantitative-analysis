from typing import Any
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.dates as mdates

from technical_analysis.components.alpha_vantage import DataStoreComponent
from technical_analysis.models import OHLCVEnum


class StockMetricVisualisationComponent:
    """
    A component to operate on the date-x-instrument dataframe of an OHLCV metric
    """
    PLOT_HELPER_STRINGS: dict[str, str] = {
        'destructive_backspace': '\b \b',
        'cumulative_change': 'Cumulative change',
        'prices_or_backspace': None
    }

    def __init__(
        self,
        financial_data_store: DataStoreComponent
    ):
        self.__store: DataStoreComponent = financial_data_store
        self.PLOT_HELPER_STRINGS.update({
            'prices_or_backspace': f"{'prices' if self.data_store.metric != OHLCVEnum.VOLUME else self.PLOT_HELPER_STRINGS['destructive_backspace']}"
        })
    

    # Getters
    @property
    def data_store(self) -> DataStoreComponent:
        return self.__store
    

    # Chainable Setter
    @data_store.setter
    def data_store(self, data_store: DataStoreComponent) -> 'StockMetricVisualisationComponent':
        self.__store = data_store
        return self
    

    def plot_change_in_metric_of_all_instruments(
        self,
        cumulative: bool,
        title: str | None = None,
        ylabel: str | None = None,
        nrows: int = 3,
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Plot the change (cumulative/non-cumulative) in Open, High, Low, Close, or Volume metrics for all instruments in the assosiated financial store
        """
        style.use(styling)

        df = self.data_store.cumulative_change_in_main_metric_df if cumulative else self.data_store.change_in_main_metric_df

        n = len(self.data_store.instrument_symbols)
        ncols = math.ceil(n / nrows)
        
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(8 * ncols, 6 * nrows))

        axes = [axes] if n == 1 else axes.flatten()
        for i in range(n, len(axes)):
            fig.delaxes(axes[i])

        fig.suptitle(title if title else f"{self.PLOT_HELPER_STRINGS['cumulative_change'] if cumulative else 'Change'} in {self.data_store.candle_span.lower()} {self.data_store.metric.lower()} {self.PLOT_HELPER_STRINGS['prices_or_backspace']}")
        fig.tight_layout()
        fig.subplots_adjust(top=0.85, left=0.05, right=0.95, hspace=0.3, wspace=0.2)
        fig.autofmt_xdate(ha='center', rotation=70)
        
        for i, symbol in enumerate(self.data_store.instrument_symbols):  
            axes[i].set_title(symbol)
            axes[i].set_xlabel('Date')
            axes[i].set_ylabel(ylabel if ylabel else f"Change in {self.data_store.metric.lower()} {self.PLOT_HELPER_STRINGS['prices_or_backspace']}")

            axes[i].plot(df.index, df[symbol], label=symbol)
            
            axes[i].legend().set_visible(False)
            axes[i].grid(True)
            axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        
        plt.show()

    
    def plot_change_in_metric_of_instrument(
        self,
        instrument_symbol: str,
        cumulative: bool,
        title: str | None = None,
        ylabel: str | None = None,
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Plot the change (cumulative/non-cumulative) in Open, High, Low, Close, or Volume metrics for said instrument
        """
        if instrument_symbol not in self.data_store.instrument_symbols:
            raise ValueError(f"Associated Financial Store does not have data for instrument: {instrument_symbol}")

        style.use(styling)

        df = self.data_store.cumulative_change_in_main_metric_df if cumulative else self.data_store.change_in_main_metric_df
        
        fig, axes = plt.subplots(figsize=(10, 6))

        fig.suptitle(title if title else f"{instrument_symbol}")
        fig.tight_layout()
        fig.subplots_adjust(top=0.85, left=0.05, right=0.95, hspace=0.3, wspace=0.2)
        fig.autofmt_xdate(ha='center', rotation=70)
        
        axes.set_title(f"{self.PLOT_HELPER_STRINGS['cumulative_change'] if cumulative else 'Change'} in {self.data_store.candle_span.lower()} {self.PLOT_HELPER_STRINGS['prices_or_backspace']}")
        axes.set_xlabel('Date')
        axes.set_ylabel(ylabel if ylabel else f"Change in {self.data_store.metric.lower()} {self.PLOT_HELPER_STRINGS['prices_or_backspace']}")

        axes.plot(df.index, df[instrument_symbol], label=instrument_symbol)
        
        axes.legend().set_visible(False)
        axes.grid(True)
        axes.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        
        plt.show()


    def bar_average_change_in_main_metric(
        self, 
        title: str | None = None, 
        ylabel: str | None = None, 
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Bar plot the averages of change in Open, High, Low, Close, or Volume metrics for all instruments in the data store
        """
        style.use(styling)

        avg_change_in_main_metric = self.data_store.change_in_main_metric_df.mean(axis=0)

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle(title if title else f"Average of change in {self.data_store.candle_span.lower()} {self.data_store.metric.lower()} {self.PLOT_HELPER_STRINGS['prices_or_backspace']}")
        fig.tight_layout()
        fig.subplots_adjust(top=0.9, bottom=0.25, left=0.1, right=0.9, hspace=0.3, wspace=0.2)
        
        ax.bar(avg_change_in_main_metric.index, avg_change_in_main_metric.values)
        ax.set_xlabel('Instrument')
        ax.set_ylabel(ylabel if ylabel else f"Change in {self.data_store.metric.lower()} {self.PLOT_HELPER_STRINGS['prices_or_backspace']}")
        
        plt.xticks(rotation=45)
        plt.show()

    
    def bar_volatility_of_main_metric(
        self, 
        title: str | None = None, 
        ylabel: str | None = None, 
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Bar plot the standard deviation of change in Open, High, Low, Close, or Volume metrics for all instruments in the data store
        """
        style.use(styling)

        std_change_in_main_metric = self.data_store.change_in_main_metric_df.std(axis=0)

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle(title if title else f"Volatility of {self.data_store.candle_span.lower()} {self.data_store.metric.lower()} {self.PLOT_HELPER_STRINGS['prices_or_backspace']}")
        fig.tight_layout()
        fig.subplots_adjust(top=0.9, bottom=0.25, left=0.1, right=0.9, hspace=0.3, wspace=0.2)
        
        ax.bar(std_change_in_main_metric.index, std_change_in_main_metric.values)
        ax.set_xlabel('Instrument')
        ax.set_ylabel(ylabel if ylabel else f"Change in {self.data_store.metric.lower()} {self.PLOT_HELPER_STRINGS['prices_or_backspace']}")
        
        plt.xticks(rotation=45)
        plt.show()

    
    def double_bar_volatility_and_average_of_change_in_main_metric(
        self, 
        title: str | None = None, 
        ylabel: str | None = None, 
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Double bar plot the averages and standard deviations of change in Open, High, Low, Close, or Volume metrics for all instruments in the data store
        """
        style.use(styling)

        change_in_main_metric_df = self.data_store.change_in_main_metric_df

        mean_change_in__main_metric = change_in_main_metric_df.mean(axis=0)
        std_change_in_main_metric = change_in_main_metric_df.std(axis=0)

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle(title if title else f"Double Bar for {self.data_store.candle_span.lower()} {self.data_store.metric.lower()} {self.PLOT_HELPER_STRINGS['prices_or_backspace']}")
        fig.tight_layout()
        fig.subplots_adjust(top=0.9, bottom=0.25, left=0.1, right=0.9, hspace=0.3, wspace=0.2)
        
        bar_width = 0.35
        x = np.arange(len(mean_change_in__main_metric.index))

        ax.bar(x - bar_width / 2, mean_change_in__main_metric.values, width=bar_width, label='Average')
        ax.bar(x + bar_width / 2, std_change_in_main_metric.values, width=bar_width, label='Standard Deviation')

        ax.set_xlabel('Instrument')
        ax.set_ylabel(ylabel if ylabel else f"Change in {self.data_store.metric.lower()} {self.PLOT_HELPER_STRINGS['prices_or_backspace']}")
        
        ax.set_xticks(x)
        ax.set_xticklabels(mean_change_in__main_metric.index)
        
        plt.xticks(rotation=45)
        plt.legend()
        plt.show()
