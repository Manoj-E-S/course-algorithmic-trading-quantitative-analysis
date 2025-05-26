from typing import Literal
import pandas as pd

from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.api_dataframing import ApiDataframingServiceEnum
from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.services.base_api_dataframing_service import BaseApiDataframingService


class InstrumentGroup:
    """
    A class to get all dataframes useful for financial analyses
    """

    def __init__(
        self,
        instrument_symbols: list[str],
        candle_span: CandlespanEnum,
        source_api_class_for_dataframing: ApiDataframingServiceEnum,
        na_strategy: Literal['drop_index', 'drop_column', 'backfill', 'forwardfill'] = 'backfill'
    ):
        self.__DATAFRAMING_CLASS: type[BaseApiDataframingService] = source_api_class_for_dataframing.value

        self.__candle_span: CandlespanEnum = candle_span
        self.__na_strategy: Literal['drop_index', 'drop_column', 'backfill', 'forwardfill'] = na_strategy

        print("[WARNING] Initializing InstrumentGroup instruments. Invalid instrument symbols (if any), will be dropped")
        self.__instrument_symbols: list[str] = self.__filter_valid_instruments(instrument_symbols)
    
    
    # Getters
    @property
    def candle_span(self) -> str:
        return self.__candle_span.value
    
    @property
    def instrument_symbols(self) -> list[str]:
        return self.__instrument_symbols
    
    @property
    def na_strategy(self) -> Literal['drop_index', 'drop_column', 'backfill', 'forwardfill']:
        return self.__na_strategy
    

    # Chainable Setters
    @candle_span.setter
    def candle_span(self, candle_span: CandlespanEnum) -> 'InstrumentGroup':
        self.__candle_span = candle_span
        return self

    @instrument_symbols.setter
    def instrument_symbols(self, instrument_symbols: list[str]) -> 'InstrumentGroup':
        self.__instrument_symbols = instrument_symbols
        return self

    @na_strategy.setter
    def na_strategy(self, na_strategy: Literal['drop_index', 'drop_column', 'backfill', 'forwardfill']) -> 'InstrumentGroup':
        self.__na_strategy = na_strategy
        return self


    # Additional Properties
    @property
    def instrument_ohlcvdf_dict(self) -> dict[str, pd.DataFrame]:
        dfs_dict: dict[str, pd.DataFrame] = self.__DATAFRAMING_CLASS.get_instrument_ohlcvdf_dict(self.__candle_span, self.__instrument_symbols)

        if not dfs_dict:
            raise ValueError(f"Could not fetch instrument data for candle_span: {self.__candle_span.value}, instrument_symbols: {self.__instrument_symbols}")
        
        return dfs_dict
    

    @property
    def closes_df(self) -> pd.DataFrame:
        """
        Returns a DataFrame with dates as index, instrument symbols as columns and close prices as the cell-data
        """
        return self.__get_metric_df(OHLCVUDEnum.CLOSE)
    

    @property
    def volume_df(self) -> pd.DataFrame:
        """
        Returns a DataFrame with dates as index, instrument symbols as columns and volume as the cell-data
        """
        return self.__get_metric_df(OHLCVUDEnum.VOLUME)
    

    @property
    def returns_df(self) -> pd.DataFrame:
        """
        Returns a DataFrame with dates as index, instrument symbols as columns and returns as the cell-data
        """
        return self.__get_change_in_metric_df(OHLCVUDEnum.CLOSE)
    

    @property
    def volume_change_df(self) -> pd.DataFrame:
        """
        Returns a DataFrame with dates as index, instrument symbols as columns and volume change as the cell-data
        """
        return self.__get_change_in_metric_df(OHLCVUDEnum.VOLUME)
    

    @property
    def cumulative_returns_df(self) -> pd.DataFrame:
        """
        Returns a DataFrame with dates as index, instrument symbols as columns and cumulative returns as the cell-data
        """
        return self.__get_cumulative_change_in_metric_df(OHLCVUDEnum.CLOSE)

    @property
    def cumulative_volume_change_df(self) -> pd.DataFrame:
        """
        Returns a DataFrame with dates as index, instrument symbols as columns and cumulative volume change as the cell-data
        """
        return self.__get_cumulative_change_in_metric_df(OHLCVUDEnum.VOLUME)


    # Public Methods
    def add_instrument(self, instrument_symbol: str) -> None:
        if instrument_symbol not in self.__instrument_symbols:
            if not self.__DATAFRAMING_CLASS.is_instrument_valid(self.__candle_span, instrument_symbol):
                raise Exception(f"Unable to add instrument {instrument_symbol}. {instrument_symbol} seems to be invalid")
        
            self.__instrument_symbols.append(instrument_symbol)
            

    def remove_instrument(self, instrument_symbol: str) -> None:
        if instrument_symbol in self.__instrument_symbols:
            self.__instrument_symbols.remove(instrument_symbol)
    

    def apply_simple_moving_operation(
        self,
        on_which_data: Literal['closes', 'returns', 'cumulative_returns', 'volume', 'volume_change', 'cumulative_volume_change'],
        which_operation: Literal['mean', 'var', 'std', 'min', 'max'],
        window: int
    ) -> pd.DataFrame:
        
        df: pd.DataFrame = pd.DataFrame()
        if on_which_data == 'closes':
            df = self.closes_df
        elif on_which_data == 'returns':
            df = self.returns_df
        elif on_which_data == 'cumulative_returns':
            df = self.cumulative_returns_df
        elif on_which_data == 'volume':
            df = self.volume_df
        elif on_which_data == 'volume_change':
            df = self.volume_change_df
        elif on_which_data == 'cumulative_volume_change':
            df = self.cumulative_volume_change_df
        else:
            raise ValueError(f"Unsupported dataframe: {on_which_data}")

        if which_operation == 'mean':
            return df.rolling(window=window).mean().dropna(axis='index')
        elif which_operation == 'var':
            return df.rolling(window=window).var().dropna(axis='index')
        elif which_operation == 'std':
            return df.rolling(window=window).std().dropna(axis='index')
        elif which_operation == 'min':
            return df.rolling(window=window).min().dropna(axis='index')
        elif which_operation == 'max':
            return df.rolling(window=window).max().dropna(axis='index')
        else:
            raise ValueError(f"Unsupported operation: {which_operation}")


    def apply_exponential_moving_operation(
        self,
        on_which_data: Literal['closes', 'returns', 'cumulative_returns', 'volume', 'volume_change', 'cumulative_volume_change'],
        which_operation: Literal['mean', 'var', 'std', 'corr', 'cov'], 
        window: int,
        min_periods: int = 0,
    ) -> pd.DataFrame:
        
        df: pd.DataFrame = pd.DataFrame()
        if on_which_data == 'closes':
            df = self.closes_df
        elif on_which_data == 'returns':
            df = self.returns_df
        elif on_which_data == 'cumulative_returns':
            df = self.cumulative_returns_df
        elif on_which_data == 'volume':
            df = self.volume_df
        elif on_which_data == 'volume_change':
            df = self.volume_change_df
        elif on_which_data == 'cumulative_volume_change':
            df = self.cumulative_volume_change_df
        else:
            raise ValueError(f"Unsupported dataframe: {on_which_data}")

        if which_operation == 'mean':
            return df.ewm(span=window, min_periods=min_periods).mean().dropna(axis='index')
        elif which_operation == 'var':
            return df.ewm(span=window, min_periods=min_periods).var().dropna(axis='index')
        elif which_operation == 'std':
            return df.ewm(span=window, min_periods=min_periods).std().dropna(axis='index')
        elif which_operation == 'corr':
            return df.ewm(span=window, min_periods=min_periods).corr().dropna(axis='index')
        elif which_operation == 'cov':
            return df.ewm(span=window, min_periods=min_periods).cov().dropna(axis='index')
        else:
            raise ValueError(f"Unsupported operation: {which_operation}")
    
    
    # Private Methods
    def __backfillna(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        return df.bfill(inplace=False)
    

    def __forwardfillna(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        return df.ffill(inplace=False)

    
    def __dropna_by_index(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        return df.dropna(axis='index', inplace=False)
    

    def __dropna_by_column(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        return df.dropna(axis='columns', inplace=False)
    

    def __handle_na_by_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.__na_strategy == 'backfill':
            df = self.__backfillna(df)
        elif self.__na_strategy == 'forwardfill':
            df = self.__forwardfillna(df)
        elif self.__na_strategy == 'drop_index':
            df = self.__dropna_by_index(df)
        elif self.__na_strategy == 'drop_column':
            df = self.__dropna_by_column(df)

        return df
    

    def __filter_valid_instruments(self, instrument_symbols: list[str]) -> list[str]:
        valid_instrument_symbols: list[str] = []
        for instrument_symbol in instrument_symbols:
            if not self.__DATAFRAMING_CLASS.is_instrument_valid(self.__candle_span, instrument_symbol):
                print(f"[WARNING] Instrument {instrument_symbol} is invalid and hence dropped")
                continue

            valid_instrument_symbols.append(instrument_symbol)

        if len(valid_instrument_symbols) == 0:
            err_msg: str = f"[{self.__class__.__name__}.valid_instruments] no instruments are supplied/valid"
            raise ValueError(err_msg)
        
        return valid_instrument_symbols
    

    def __get_metric_df(self, metric: OHLCVUDEnum) -> pd.DataFrame:
        df: pd.DataFrame | None = self.__DATAFRAMING_CLASS.get_all_instruments_dataframe_by_metric(
            metric,
            self.__candle_span,
            self.__instrument_symbols
        )

        if df is None:
            raise ValueError(f"Could not fetch dataframe for metric: {metric.value}, candle_span: {self.__candle_span.value}, instrument_symbols: {self.__instrument_symbols}")
        
        return self.__handle_na_by_strategy(df)


    def __get_change_in_metric_df(self, metric: OHLCVUDEnum) -> pd.DataFrame:
        """
        Daily, Weekly, or Monthly (based on candle_span) returns for OHLC metrics, volume change for V metric
        """
        df = self.__get_metric_df(metric)

        # Avoid division by zero
        shifted_df = df.shift(1).replace(0, 1e-10)

        change_in_metric_df = (df / shifted_df) - 1
        change_in_metric_df.dropna(axis='index', inplace=True)

        # Clip extreme values to avoid numerical instability
        change_in_metric_df = change_in_metric_df.clip(lower=-1e10, upper=1e10)
        
        return change_in_metric_df
    

    def __get_cumulative_change_in_metric_df(self, metric: OHLCVUDEnum, initial_value: float = 1) -> pd.DataFrame:
        """
        Daily, Weekly, or Monthly (based on candle_span) cumulative compounded returns for OHLC metrics, cumulative volume change for V metric
        
        Compounding:
        => metric_initial_value * (1 + change_in_metric_between_candle_0_and_1) * (1 + change_in_metric_between_candle_1_and_2) * ...
        => 1 * cumulative_product(1 + change_in_metric_between_candle_i_and_(i+1))
        where 
            metric_initial_value = 1 (assumed to be 1, by default)
        """
        return initial_value * (1 + self.__get_change_in_metric_df(metric)).cumprod().dropna(axis='index')
    



