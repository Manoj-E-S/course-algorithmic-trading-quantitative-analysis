from matplotlib import pyplot as plt
import matplotlib.dates as mdates

import pandas as pd
from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.models.instrument import Instrument
from technical_analysis.models.portfolio import Portfolio


class PortfolioPlotter:
    
    def __init__(self, portfolio: Portfolio, benchmark_instrument: Instrument):
        self.portfolio = portfolio
        self.benchmark_instrument = benchmark_instrument


    def plot_returns(
        self,
        title: str = "Portfolio Returns Over Time",
        styling: str = 'ggplot'
    ) -> None:
        """
        Plot the portfolio returns over time.

        :param title: The title of the plot. Defaults to "Portfolio Returns Over Time".
        :type title: str

        :param styling: The styling of the plot. Defaults to 'ggplot'.
        :type styling: str
        """
        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None

        fig, ax1 = plt.subplots(1, 1, figsize=(14, 8))
        fig.suptitle(title, fontsize=16)

        ax1.plot(self.portfolio.returns_series, label="Portfolio Returns", color='blue')
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Returns")
        ax1.legend()
        ax1.grid()
        
        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
    

    def plot_cumulative_returns(
        self,
        title: str = "Portfolio Cumulative Returns Over Time",
        styling: str = 'ggplot'
    ) -> None:
        """
        Plot the portfolio cumulative returns over time.
        
        :param title: The title of the plot. Defaults to "Portfolio Cumulative Returns Over Time".
        :type title: str
        
        :param styling: The styling of the plot. Defaults to 'ggplot'.
        :type styling: str
        """
        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None

        fig, ax1 = plt.subplots(1, 1, figsize=(14, 8))
        fig.suptitle(title, fontsize=16)

        ax1.plot(self.portfolio.cumulative_returns_series, label="Portfolio Cumulative Returns", color='blue')
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Cumulative Returns")
        ax1.legend()
        ax1.grid()
        
        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
    
    
    def plot_portfolio_vs_benchmark(
        self,
        title: str = "Portfolio vs Benchmark Cumulative Returns",
        styling: str = 'ggplot'
    ) -> None:
        """
        Plot the portfolio cumulative returns against the benchmark cumulative returns over time.
        
        :param title: The title of the plot. Defaults to "Portfolio vs Benchmark Cumulative Returns".
        :type title: str
        
        :param styling: The styling of the plot. Defaults to 'ggplot'.
        :type styling: str
        """
        benchmark_cumulative_returns: pd.Series = self.__get_clipped_benchmark_cumulative_returns()

        plt.style.use(styling)

        fig: plt.Figure = None
        ax1: plt.Axes = None

        fig, ax1 = plt.subplots(1, 1, figsize=(14, 8))
        fig.suptitle(title, fontsize=16)

        ax1.plot(self.portfolio.cumulative_returns_series, label="Portfolio Cumulative Returns", color='blue')
        ax1.plot(benchmark_cumulative_returns, label="Benchmark Cumulative Returns", color='orange')
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Cumulative Returns")
        ax1.legend()
        ax1.grid()

        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        fig.autofmt_xdate(rotation=70)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()


    def __get_clipped_benchmark_cumulative_returns(self) -> pd.Series:
        """
        Clips the benchmark cumulative returns to the portfolio's date range.
        
        :return: Clipped benchmark cumulative returns.
        :rtype: pd.Series
        """
        return (
            self
            .benchmark_instrument
            .ohlcv_df
            .loc [
                self.portfolio.start_date : self.portfolio.end_date + pd.Timedelta(days=1),
                OHLCVUDEnum.CLOSE.value
            ]
            .pct_change()
            .fillna(0)
            .add(1)
            .cumprod()
        )