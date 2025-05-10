from typing import Literal
import pandas as pd
from technical_analysis.components.alpha_vantage import DataframerComponent
from technical_analysis.models import CandlespanEnum, OHLCVEnum

class StockTechnicalIndicationComponent:
    """
    A class to represent all technical indicators.
    This class is responsible for providing technical indicators on the dataframe it is configured with.
    """
    def __init__(
        self,
        metric: OHLCVEnum,
        candle_span: CandlespanEnum,
        instrument_symbol: str,
        na_strategy: Literal['drop_date', 'drop_metric', 'backfill', 'forwardfill'] = 'backfill'
    ):
        self.__metric = metric
        self.__candle_span = candle_span
        self.__instrument_symbol = instrument_symbol
        self.__na_strategy = na_strategy

        self.__make_dfs_dict()
    

    # Getters
    @property
    def metric(self) -> OHLCVEnum:
        return self.__metric.value

    @property
    def candle_span(self) -> CandlespanEnum:
        return self.__candle_span.value
    
    @property
    def instrument_symbol(self) -> str:
        return self.__instrument_symbol
    

    # Setters
    @metric.setter
    def metric(self, metric: OHLCVEnum) -> None:
        self.__metric = metric
    
    @candle_span.setter
    def candle_span(self, candle_span: CandlespanEnum) -> None:
        self.__candle_span = candle_span
        self.__make_dfs_dict()

    @instrument_symbol.setter
    def instrument_symbol(self, instrument_symbol: str) -> None:
        self.__instrument_symbol = instrument_symbol
        self.__make_dfs_dict()
    

    # Private Methods
    def __make_dfs_dict(self) -> None:
        """
        This method is responsible for creating the dataframes for the given instrument symbols.
        """
        df: pd.DataFrame = DataframerComponent.get_ohlcv_dataframe_by_symbol(self.__candle_span, self.__instrument_symbol)

        if df is None:
            raise ValueError(f"No data found for the given instrument symbol: {self.__instrument_symbol}")
        
        self.__df = df
        self.__handle_na_by_strategy()
    

    def __backfillna(self) -> None:
        self.__df.bfill(axis='index', inplace=True)
        

    def __forwardfillna(self) -> None:
        self.__df.ffill(axis='index', inplace=True)

    
    def __dropna_by_date(self) -> None:
        self.__df.dropna(axis='index', inplace=True)


    def __dropna_by_metric(self) -> None:
        self.__df.dropna(axis='columns', inplace=True)
    

    def __handle_na_by_strategy(self) -> None:
        if self.__na_strategy == 'backfill':
            self.__backfillna()
        elif self.__na_strategy == 'forwardfill':
            self.__forwardfillna()
        elif self.__na_strategy == 'drop_date':
            self.__dropna_by_date()
        elif self.__na_strategy == 'drop_metric':
            self.__dropna_by_metric()


    # Methods
    def collect(self) -> pd.DataFrame:
        """
        Returns the OHLCV+indicator_columns dataframe for the given instrument symbol.
        """
        return self.__df
    

    def macd(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> 'StockTechnicalIndicationComponent':
        """
        Calculate the MACD (Moving Average Convergence Divergence) for the configured instrument symbols, and include it in the corresponding dataframe.
        
        The MACD is calculated using the following formula:
            MACD = fast_period_EMA - slow_period_EMA
            MACD Signal line = signal_period_EMA of the MACD

        :param slow_period: The period for the slow EMA. Default is 26.
        :param fast_period: The period for the fast EMA. Default is 12.
        :param signal_period: The period for the signal line. Default is 9.

        :type slow_period: int
        :type fast_period: int
        :type signal_period: int

        :returns: current object to allow method chaining.
        """
        self.__df['fast_ema'] = self.__df[self.__metric.value].ewm(span=fast_period, adjust=False).mean()
        self.__df['slow_ema'] = self.__df[self.__metric.value].ewm(span=slow_period, adjust=False).mean()
        self.__df['mcad'] = self.__df['fast_ema'] - self.__df['slow_ema']
        self.__df['mcad_signal'] = self.__df['mcad'].ewm(span=signal_period, adjust=False).mean()
        self.__df['mcad_histogram'] = self.__df['mcad'] - self.__df['mcad_signal']
        self.__df.drop(columns=['fast_ema', 'slow_ema'], inplace=True)
        
        return self