from typing import Any

import math

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.dates as mdates

from technical_analysis.models.instrument_group import InstrumentGroup


class InstrumentGroupVisualizer:
    """
    Visualizes Comparative Returns and Volume Changes of Instruments in an Instrument Group
    """

    def __init__(
        self,
        financial_instrument_group: InstrumentGroup
    ):
        self.__instrument_group: InstrumentGroup = financial_instrument_group
    

    # Getters
    @property
    def instrument_group(self) -> InstrumentGroup:
        return self.__instrument_group
    

    # Chainable Setter
    @instrument_group.setter
    def instrument_group(self, instrument_group: InstrumentGroup) -> 'InstrumentGroupVisualizer':
        self.__instrument_group = instrument_group
        return self
    

    def plot_returns_of_all_instruments(
        self,
        cumulative: bool,
        title: str | None = None,
        ylabel: str | None = None,
        nrows: int = 3,
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Plot the returns (cumulative/non-cumulative) for all instruments in the assosiated instrument group
        """
        style.use(styling)

        fig: plt.Figure = None
        axes: tuple[plt.Axes] = None

        df = self.instrument_group.cumulative_returns_df if cumulative else self.instrument_group.returns_df

        n = len(self.instrument_group.instrument_symbols)
        ncols = math.ceil(n / nrows)
        
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(8 * ncols, 6 * nrows))

        axes = [axes] if n == 1 else axes.flatten()
        for i in range(n, len(axes)):
            fig.delaxes(axes[i])

        fig.suptitle(title if title else f"{self.instrument_group.candle_span.capitalize()}{' cumulative' if cumulative else ''} returns")
        fig.tight_layout()
        fig.subplots_adjust(top=0.85, left=0.05, right=0.95, hspace=0.3, wspace=0.2)
        fig.autofmt_xdate(ha='center', rotation=70)
        
        for i, symbol in enumerate(self.instrument_group.instrument_symbols):  
            axes[i].set_title(symbol)
            axes[i].set_xlabel('Date')
            axes[i].set_ylabel(ylabel if ylabel else f"{self.instrument_group.candle_span.capitalize()}{' cumulative' if cumulative else ''} returns")

            axes[i].plot(df.index, df[symbol], label=symbol)
            
            axes[i].legend().set_visible(False)
            axes[i].grid(True)
            axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        
        plt.show()

    
    def bar_volume_change_of_all_instruments(
        self,
        cumulative: bool,
        title: str | None = None,
        ylabel: str | None = None,
        nrows: int = 3,
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Plot the volume changes (cumulative/non-cumulative) for all instruments in the assosiated instrument group
        """
        style.use(styling)

        fig: plt.Figure = None
        axes: tuple[plt.Axes] = None

        df = self.instrument_group.cumulative_volume_change_df if cumulative else self.instrument_group.volume_change_df

        n = len(self.instrument_group.instrument_symbols)
        ncols = math.ceil(n / nrows)
        
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(8 * ncols, 6 * nrows))

        axes = [axes] if n == 1 else axes.flatten()
        for i in range(n, len(axes)):
            fig.delaxes(axes[i])

        fig.suptitle(title if title else f"{self.instrument_group.candle_span.capitalize()}{' cumulative' if cumulative else ''} volume changes")
        fig.tight_layout()
        fig.subplots_adjust(top=0.85, left=0.05, right=0.95, hspace=0.3, wspace=0.2)
        fig.autofmt_xdate(ha='center', rotation=70)
        
        for i, symbol in enumerate(self.instrument_group.instrument_symbols):  
            axes[i].set_title(symbol)
            axes[i].set_xlabel('Date')
            axes[i].set_ylabel(ylabel if ylabel else f"{self.instrument_group.candle_span.capitalize()}{' cumulative' if cumulative else ''} volume changes")

            axes[i].bar(df.index, df[symbol], label=symbol, width=35, color='orange')
            
            axes[i].legend().set_visible(False)
            axes[i].grid(True)
            axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        
        plt.show()

    
    def plot_returns_of_instrument(
        self,
        instrument_symbol: str,
        cumulative: bool,
        title: str | None = None,
        ylabel: str | None = None,
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Plot the returns (cumulative/non-cumulative) for a given instrument in the assosiated instrument group
        """
        if instrument_symbol not in self.instrument_group.instrument_symbols:
            raise ValueError(f"Associated Instrument Group does not have data for instrument: {instrument_symbol}")

        style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None

        df = self.instrument_group.cumulative_returns_df if cumulative else self.instrument_group.returns_df

        fig, ax1 = plt.subplots(figsize=(10, 6))

        fig.suptitle(title if title else f"{instrument_symbol}")
        fig.tight_layout()
        fig.subplots_adjust(top=0.85, left=0.05, right=0.95, hspace=0.3, wspace=0.2)
        fig.autofmt_xdate(ha='center', rotation=70)
        
        ax1.set_title(f"{self.instrument_group.candle_span.capitalize()}{' cumulative' if cumulative else ''} returns")
        ax1.set_xlabel('Date')
        ax1.set_ylabel(ylabel if ylabel else f"{self.instrument_group.candle_span.capitalize()}{' cumulative' if cumulative else ''} returns")

        ax1.plot(df.index, df[instrument_symbol], label=instrument_symbol)
        
        ax1.legend().set_visible(False)
        ax1.grid(True)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        
        plt.show()


    def bar_volume_changes_of_instrument(
        self,
        instrument_symbol: str,
        cumulative: bool,
        title: str | None = None,
        ylabel: str | None = None,
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Plot the volume changes (cumulative/non-cumulative) for a given instrument in the assosiated instrument group
        """
        if instrument_symbol not in self.instrument_group.instrument_symbols:
            raise ValueError(f"Associated Instrument Group does not have data for instrument: {instrument_symbol}")

        style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None

        df = self.instrument_group.cumulative_volume_change_df if cumulative else self.instrument_group.volume_change_df

        fig, ax1 = plt.subplots(figsize=(10, 6))

        fig.suptitle(title if title else f"{instrument_symbol}")
        fig.tight_layout()
        fig.subplots_adjust(top=0.85, left=0.05, right=0.95, hspace=0.3, wspace=0.2)
        fig.autofmt_xdate(ha='center', rotation=70)

        ax1.set_title(f"{self.instrument_group.candle_span.capitalize()}{' cumulative' if cumulative else ''} volume changes")
        ax1.set_xlabel('Date')
        ax1.set_ylabel(ylabel if ylabel else f"{self.instrument_group.candle_span.capitalize()}{' cumulative' if cumulative else ''} volume changes")

        ax1.plot(df.index, df[instrument_symbol], label=instrument_symbol)
        
        ax1.legend().set_visible(False)
        ax1.grid(True)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        
        plt.show()


    def bar_average_returns(
        self, 
        title: str | None = None, 
        ylabel: str | None = None, 
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Bar plot the average returns for all instruments in the instrument group
        """
        style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None

        avg_returns = self.instrument_group.returns_df.mean(axis=0)

        fig, ax1 = plt.subplots(figsize=(10, 6))
        fig.suptitle(title if title else f"Average {self.instrument_group.candle_span.lower()} returns")
        fig.tight_layout()
        fig.subplots_adjust(top=0.9, bottom=0.25, left=0.1, right=0.9, hspace=0.3, wspace=0.2)
        
        ax1.bar(avg_returns.index, avg_returns.values)
        ax1.set_xlabel('Instrument')
        ax1.set_ylabel(ylabel if ylabel else f"{self.instrument_group.candle_span.capitalize()} returns")

        plt.xticks(rotation=45)
        plt.show()


    def bar_average_volume_change(
        self, 
        title: str | None = None, 
        ylabel: str | None = None, 
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Bar plot the average volume changes for all instruments in the instrument group
        """
        style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None

        avg_volume_changes = self.instrument_group.volume_change_df.mean(axis=0)

        fig, ax1 = plt.subplots(figsize=(10, 6))
        fig.suptitle(title if title else f"Average {self.instrument_group.candle_span.lower()} volume changes")
        fig.tight_layout()
        fig.subplots_adjust(top=0.9, bottom=0.25, left=0.1, right=0.9, hspace=0.3, wspace=0.2)
        
        ax1.bar(avg_volume_changes.index, avg_volume_changes.values)
        ax1.set_xlabel('Instrument')
        ax1.set_ylabel(ylabel if ylabel else f"{self.instrument_group.candle_span.capitalize()} volume changes")

        plt.xticks(rotation=45)
        plt.show()

    
    def bar_instrument_volatility(
        self, 
        title: str | None = None, 
        ylabel: str | None = None, 
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Bar plot the standard deviation of returns for all instruments in the instrument group
        """
        style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None

        std_of_returns = self.instrument_group.returns_df.std(axis=0)

        fig, ax1 = plt.subplots(figsize=(10, 6))
        fig.suptitle(title if title else f"Volatility (standard deviation) of instruments")
        fig.tight_layout()
        fig.subplots_adjust(top=0.9, bottom=0.25, left=0.1, right=0.9, hspace=0.3, wspace=0.2)
        
        ax1.bar(std_of_returns.index, std_of_returns.values)
        ax1.set_xlabel('Instrument')
        ax1.set_ylabel(ylabel if ylabel else f"{self.instrument_group.candle_span.capitalize()} returns")
        
        plt.xticks(rotation=45)
        plt.show()

    
    def double_bar_volatility_and_average_returns(
        self, 
        title: str | None = None, 
        ylabel: str | None = None, 
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Double bar plot the averages and standard deviations of returns for all instruments in the instrument group
        """
        style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None

        df = self.instrument_group.returns_df

        mean_returns = df.mean(axis=0)
        std_returns = df.std(axis=0)

        fig, ax1 = plt.subplots(figsize=(10, 6))
        fig.suptitle(title if title else f"Average and standard deviation of {self.instrument_group.candle_span.lower()} returns")
        fig.tight_layout()
        fig.subplots_adjust(top=0.9, bottom=0.25, left=0.1, right=0.9, hspace=0.3, wspace=0.2)
        
        bar_width = 0.35
        x = np.arange(len(mean_returns.index))

        ax1.bar(x - bar_width / 2, mean_returns.values, width=bar_width, label='Average returns')
        ax1.bar(x + bar_width / 2, std_returns.values, width=bar_width, label='Volatility (std dev)')

        ax1.set_xlabel('Instrument')
        ax1.set_ylabel(ylabel if ylabel else f"{self.instrument_group.candle_span.capitalize()} returns")

        ax1.set_xticks(x)
        ax1.set_xticklabels(mean_returns.index)

        plt.xticks(rotation=45)
        plt.legend()
        plt.show()
