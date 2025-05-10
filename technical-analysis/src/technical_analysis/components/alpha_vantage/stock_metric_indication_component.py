from typing import Any, Literal
import pandas as pd
from technical_analysis.components.alpha_vantage import DataframerComponent
from technical_analysis.models import OHLCVEnum, CandlespanEnum

class StockMetricIndicationComponent:
    """
    A component to operate on the date-x-instrument dataframe of an OHLCV metric
    """
    
    def __init__(
        self,
        metric: OHLCVEnum,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str],
        na_strategy: Literal['drop_date', 'drop_symbol', 'backfill', 'forwardfill'] = 'backfill'
    ):
        self.__metric: OHLCVEnum = metric
        self.__candle_span: CandlespanEnum = candle_span
        self.__instrument_symbols: list[str] = instrument_symbols
        self.__na_strategy: str = na_strategy
        
        self.__make_df()
    

    def __make_df(self) -> None:
        df: pd.DataFrame | None = DataframerComponent.get_dataframe_of_metric(
            self.__metric,
            self.__candle_span,
            self.__instrument_symbols
        )

        if df is None:
            raise ValueError(f"Could not fetch dataframe for metric: {self.__metric.value}, candle_span: {self.__candle_span.value}, instrument_symbols: {self.__instrument_symbols}")
        
        self.__df = df
        self.__handle_na_by_strategy()
    

    # Getters
    def get_metric(self) -> OHLCVEnum:
        return self.__metric
    
    def get_candle_span(self) -> CandlespanEnum:
        return self.__candle_span
    
    def get_instrument_symbols(self) -> list[str]:
        return self.__instrument_symbols
    
    def get_na_strategy(self) -> str:
        return self.__na_strategy
    
    def get_df(self) -> pd.DataFrame:
        return self.__df
    
    def get_change_in_metric_df(self) -> pd.DataFrame:
        """
        Daily, Weekly, or Monthly (based on candle_span) returns for OHLC metrics, volume change for V metric
        """
        # Avoid division by zero
        shifted_df = self.__df.shift(1).replace(0, 1e-10)

        change_in_metric_df = (self.__df / shifted_df) - 1
        change_in_metric_df.dropna(axis='index', inplace=True)

        # Clip extreme values to avoid numerical instability
        change_in_metric_df = change_in_metric_df.clip(lower=-1e10, upper=1e10)
        
        return change_in_metric_df


    # Setters
    def set_metric(self, metric: OHLCVEnum) -> None:
        self.__metric = metric
        self.__make_df()

    def set_candle_span(self, candle_span: CandlespanEnum) -> None:
        self.__candle_span = candle_span
        self.__make_df()

    def set_instrument_symbols(self, instrument_symbols: list[str]) -> None:
        self.__instrument_symbols = instrument_symbols
        self.__make_df()

    def set_na_strategy(
        self, 
        na_strategy: Literal['drop_date', 'drop_symbol', 'backfill', 'forwardfill']
    ) -> None:
        self.__na_strategy = na_strategy
        self.__make_df()


    def __backfillna(
        self,
        inplace: bool = True
    ) -> pd.DataFrame | None:
        return self.__df.bfill(inplace=inplace)
    

    def __forwardfillna(
        self,
        inplace: bool = True
    ) -> pd.DataFrame | None:
        return self.__df.ffill(inplace=inplace)

    
    def __dropna_by_date(
        self,
        inplace: bool = True
    ) -> pd.DataFrame | None:
        return self.__df.dropna(axis='index', inplace=inplace)
    

    def __dropna_by_symbol(
        self,
        inplace: bool = True
    ) -> pd.DataFrame | None:
        return self.__df.dropna(axis='columns', inplace=inplace)
    

    def __handle_na_by_strategy(self) -> None:
        if self.__na_strategy == 'backfill':
            self.__backfillna()
        elif self.__na_strategy == 'forwardfill':
            self.__forwardfillna()
        elif self.__na_strategy == 'drop_date':
            self.__dropna_by_date()
        elif self.__na_strategy == 'drop_symbol':
            self.__dropna_by_symbol()

    
    def get_simple_moving_operation_results(
        self, 
        window: int, 
        operation: Literal['mean', 'var', 'std', 'min', 'max'], 
        use_change_in_metric_df: bool = False
    ) -> pd.DataFrame:
        df: pd.DataFrame = pd.DataFrame()
        if use_change_in_metric_df:
            df = self.get_change_in_metric_df()
        else:
            df = self.__df

        if operation == 'mean':
            return df.rolling(window=window).mean().dropna(axis='index')
        elif operation == 'var':
            return df.rolling(window=window).var().dropna(axis='index')
        elif operation == 'std':
            return df.rolling(window=window).std().dropna(axis='index')
        elif operation == 'min':
            return df.rolling(window=window).min().dropna(axis='index')
        elif operation == 'max':
            return df.rolling(window=window).max().dropna(axis='index')
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        
    
    def get_exponential_moving_operation_results(
        self, 
        com: float,
        operation: Literal['mean', 'var', 'std', 'corr', 'cov'], 
        min_periods: int = 0,
        use_change_in_metric_df: bool = False
    ) -> pd.DataFrame:
        df: pd.DataFrame = pd.DataFrame()
        if use_change_in_metric_df:
            df = self.get_change_in_metric_df()
        else:
            df = self.__df

        if operation == 'mean':
            return df.ewm(com=com, min_periods=min_periods).mean().dropna(axis='index')
        elif operation == 'var':
            return df.ewm(com=com, min_periods=min_periods).var().dropna(axis='index')
        elif operation == 'std':
            return df.ewm(com=com, min_periods=min_periods).std().dropna(axis='index')
        elif operation == 'corr':
            return df.ewm(com=com, min_periods=min_periods).corr().dropna(axis='index')
        elif operation == 'cov':
            return df.ewm(com=com, min_periods=min_periods).cov().dropna(axis='index')
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        

    def get_cumulative_change_in_metric_df(self, initial_value: float = 1) -> pd.DataFrame:
        """
        Daily, Weekly, or Monthly (based on candle_span) cumulative compounded returns for OHLC metrics, cumulative volume change for V metric
        
        Compounding:
        => metric_initial_value * (1 + change_in_metric_between_candle_0_and_1) * (1 + change_in_metric_between_candle_1_and_2) * ...
        => 1 * cumulative_product(1 + change_in_metric_between_candle_i_and_(i+1))
        where 
            metric_initial_value = 1 (assumed to be 1, by default)
        """
        return initial_value * (1 + self.get_change_in_metric_df()).cumprod().dropna(axis='index')
    

    def plot_change_in_metric(self, cumulative: bool, title: str | None = None, ylabel: str | None = None, styling: str | dict[str, Any] = 'ggplot') -> None:
        """
        Plot the change_in_metric (cumulative/non-cumulative) data
        """
        import math
        import matplotlib.pyplot as plt
        import matplotlib.style as style
        import matplotlib.dates as mdates

        style.use(styling)

        df = self.get_cumulative_change_in_metric_df() if cumulative else self.get_change_in_metric_df()

        n = len(self.__instrument_symbols)
        ncols = math.ceil(n / 2)
        nrows = 2
        
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(6 * ncols, 4 * nrows))

        axes = [axes] if len(self.__instrument_symbols) == 1 else axes.flatten()
        for i in range(n, len(axes)):
            fig.delaxes(axes[i])

        fig.suptitle(title if title else f"Change in {self.__candle_span.value.capitalize()} {self.__metric.value.capitalize()}")
        fig.tight_layout()
        fig.subplots_adjust(top=0.85, left=0.05, right=0.95, hspace=0.3, wspace=0.2)
        fig.autofmt_xdate(ha='center', rotation=70)
        
        for i, symbol in enumerate(self.__instrument_symbols):  
            axes[i].set_title(symbol)
            axes[i].set_xlabel('Date')
            axes[i].set_ylabel(ylabel if ylabel else f"Change in {self.__metric.value.capitalize()}")

            axes[i].plot(df.index, df[symbol], label=symbol)
            axes[i].legend().set_visible(False)
            axes[i].grid(True)
            
            axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        
        plt.show()


    def plot_avg_change_in_metric(
        self, 
        title: str | None = None, 
        ylabel: str | None = None, 
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Plot the average change_in_metric data as a bar graph instrument-wise
        """
        import matplotlib.pyplot as plt
        import matplotlib.style as style

        style.use(styling)

        avg_change_in_metric = self.get_change_in_metric_df().mean(axis=0)

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle(title if title else f"Average Change in {self.__candle_span.value.capitalize()} {self.__metric.value.capitalize()}")
        fig.tight_layout()
        fig.subplots_adjust(top=0.9, bottom=0.25, left=0.1, right=0.9, hspace=0.3, wspace=0.2)
        
        ax.bar(avg_change_in_metric.index, avg_change_in_metric.values)
        ax.set_xlabel('Instrument')
        ax.set_ylabel(ylabel if ylabel else f"Average Change in {self.__metric.value.capitalize()}")
        
        plt.xticks(rotation=45)
        plt.show()

    
    def plot_std_of_change_in_metric(
        self, 
        title: str | None = None, 
        ylabel: str | None = None, 
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Plot the standard deviation of change_in_metric data as a bar graph instrument-wise
        """
        import matplotlib.pyplot as plt
        import matplotlib.style as style

        style.use(styling)

        std_change_in_metric = self.get_change_in_metric_df().std(axis=0)

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle(title if title else f"Standard Deviation of Change in {self.__candle_span.value.capitalize()} {self.__metric.value.capitalize()}")
        fig.tight_layout()
        fig.subplots_adjust(top=0.9, bottom=0.25, left=0.1, right=0.9, hspace=0.3, wspace=0.2)
        
        ax.bar(std_change_in_metric.index, std_change_in_metric.values)
        ax.set_xlabel('Instrument')
        ax.set_ylabel(ylabel if ylabel else f"Standard Deviation of Change in {self.__metric.value.capitalize()}")
        
        plt.xticks(rotation=45)
        plt.show()

    
    def plot_mean_std_change_in_metric(
        self, 
        title: str | None = None, 
        ylabel: str | None = None, 
        styling: str | dict[str, Any] = 'ggplot'
    ) -> None:
        """
        Plot the mean and standard deviation of change_in_metric data as a double bar graph instrument-wise
        """
        import matplotlib.pyplot as plt
        import matplotlib.style as style
        import numpy as np

        style.use(styling)

        mean_change_in_metric = self.get_change_in_metric_df().mean(axis=0)
        std_change_in_metric = self.get_change_in_metric_df().std(axis=0)

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle(title if title else f"Mean and Standard Deviation of Change in {self.__candle_span.value.capitalize()} {self.__metric.value.capitalize()}")
        fig.tight_layout()
        fig.subplots_adjust(top=0.9, bottom=0.25, left=0.1, right=0.9, hspace=0.3, wspace=0.2)
        
        bar_width = 0.35
        x = np.arange(len(mean_change_in_metric.index))

        ax.bar(x - bar_width / 2, mean_change_in_metric.values, width=bar_width, label='Mean')
        ax.bar(x + bar_width / 2, std_change_in_metric.values, width=bar_width, label='Standard Deviation')

        ax.set_xlabel('Instrument')
        ax.set_ylabel(ylabel if ylabel else f"Change in {self.__metric.value.capitalize()}")
        
        ax.set_xticks(x)
        ax.set_xticklabels(mean_change_in_metric.index)
        
        plt.xticks(rotation=45)
        plt.legend()
        plt.show()
