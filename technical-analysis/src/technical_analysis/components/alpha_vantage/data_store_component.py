from typing import Literal, overload
import pandas as pd
from technical_analysis.components.alpha_vantage import DataframerComponent
from technical_analysis.models import OHLCVEnum, CandlespanEnum


class DataStoreComponent:
    """
    A class to get all dataframes useful for financial analyses
    """

    def __init__(
        self,
        metric: OHLCVEnum,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str],
        na_strategy: Literal['drop_index', 'drop_column', 'backfill', 'forwardfill'] = 'backfill',
        use_api_cache_when_applicable: bool = True
    ):
        self.__metric: OHLCVEnum = metric
        self.__candle_span: CandlespanEnum = candle_span
        self.__na_strategy: Literal['drop_index', 'drop_column', 'backfill', 'forwardfill'] = na_strategy
        self.__use_api_cache_when_applicable: bool = use_api_cache_when_applicable
        
        print("[WARNING] Initializing DataStoreComponent instruments. Invalid instrument symbols (if any), will be dropped")
        self.__instrument_symbols: list[str] = self.valid_instruments(instrument_symbols)
    
    
    # Getters
    @property
    def metric(self) -> str:
        return self.__metric.value

    @property
    def candle_span(self) -> str:
        return self.__candle_span.value
    
    @property
    def instrument_symbols(self) -> list[str]:
        return self.__instrument_symbols
    
    @property
    def na_strategy(self) -> Literal['drop_index', 'drop_column', 'backfill', 'forwardfill']:
        return self.__na_strategy
    
    @property
    def use_api_cache_when_applicable(self) -> bool:
        return self.__use_api_cache_when_applicable
    

    # Chainable Setters
    @metric.setter
    def metric(self, metric: OHLCVEnum) -> 'DataStoreComponent':
        self.__metric = metric
        return self
    
    @candle_span.setter
    def candle_span(self, candle_span: CandlespanEnum) -> 'DataStoreComponent':
        self.__candle_span = candle_span
        return self

    @instrument_symbols.setter
    def instrument_symbols(self, instrument_symbols: list[str]) -> 'DataStoreComponent':
        self.__instrument_symbols = instrument_symbols
        return self

    @na_strategy.setter
    def na_strategy(self, na_strategy: Literal['drop_index', 'drop_column', 'backfill', 'forwardfill']) -> 'DataStoreComponent':
        self.__na_strategy = na_strategy
        return self
    
    @use_api_cache_when_applicable.setter
    def use_api_cache_when_applicable(self, use_api_cache_when_applicable: bool) -> 'DataStoreComponent':
        self.__use_api_cache_when_applicable = use_api_cache_when_applicable
        return self


    # DataFrames
    @property
    def main_metric_df(self) -> pd.DataFrame:
        df: pd.DataFrame | None = DataframerComponent.get_dataframe_of_metric(
            self.__metric,
            self.__candle_span,
            self.__instrument_symbols,
            self.__use_api_cache_when_applicable
        )

        if df is None:
            raise ValueError(f"Could not fetch main_metric dataframe for metric: {self.__metric.value}, candle_span: {self.__candle_span.value}, instrument_symbols: {self.__instrument_symbols}")
        
        return self.__handle_na_by_strategy(df)

    
    @property
    def instrument_ohlcvdf_dict(self) -> dict[str, pd.DataFrame]:
        dfs_dict: dict[str, pd.DataFrame] = {}
        for instrument_symbol in self.__instrument_symbols:
            df: pd.DataFrame = DataframerComponent.get_ohlcv_dataframe_by_symbol(self.__candle_span, instrument_symbol, self.__use_api_cache_when_applicable)

            if df is None:
                print(f"No data found for the given instrument symbol: {instrument_symbol}")
                print(f"Skipping {instrument_symbol}...")
                self.remove_instrument_if_present(instrument_symbol)
                continue
            
            dfs_dict[instrument_symbol] = self.__handle_na_by_strategy(df)
        
        if not dfs_dict:
            raise ValueError(f"Could not fetch instrument data for metric: {self.__metric.value}, candle_span: {self.__candle_span.value}, instrument_symbols: {self.__instrument_symbols}")
        
        return dfs_dict
    

    @property
    def change_in_main_metric_df(self) -> pd.DataFrame:
        """
        Daily, Weekly, or Monthly (based on candle_span) returns for OHLC metrics, volume change for V metric
        """
        df = self.main_metric_df

        # Avoid division by zero
        shifted_df = df.shift(1).replace(0, 1e-10)

        change_in_metric_df = (df / shifted_df) - 1
        change_in_metric_df.dropna(axis='index', inplace=True)

        # Clip extreme values to avoid numerical instability
        change_in_metric_df = change_in_metric_df.clip(lower=-1e10, upper=1e10)
        
        return change_in_metric_df
    

    @property
    def cumulative_change_in_main_metric_df(self, initial_value: float = 1) -> pd.DataFrame:
        """
        Daily, Weekly, or Monthly (based on candle_span) cumulative compounded returns for OHLC metrics, cumulative volume change for V metric
        
        Compounding:
        => metric_initial_value * (1 + change_in_metric_between_candle_0_and_1) * (1 + change_in_metric_between_candle_1_and_2) * ...
        => 1 * cumulative_product(1 + change_in_metric_between_candle_i_and_(i+1))
        where 
            metric_initial_value = 1 (assumed to be 1, by default)
        """
        return initial_value * (1 + self.change_in_main_metric_df).cumprod().dropna(axis='index')
    

    def get_ohlcv_df_for_instrument(self, instrument_symbol: str) -> pd.DataFrame | None:
        self.add_instrument_if_not_present(instrument_symbol)
        return self.instrument_ohlcvdf_dict.get(instrument_symbol)


    def get_renko_df(self, instrument_symbol: str) -> pd.DataFrame | None:
        pass


    def get_simple_moving_operation_df(
        self, 
        on_which_df: Literal['main_metric', 'change_in_main_metric'],
        which_operation: Literal['mean', 'var', 'std', 'min', 'max'],
        window: int
    ) -> pd.DataFrame:
        
        df: pd.DataFrame = pd.DataFrame()
        if on_which_df == 'main_metric':
            df = self.main_metric_df
        elif on_which_df == 'change_in_main_metric':
            df = self.change_in_main_metric_df
        else:
            raise ValueError(f"Unsupported dataframe: {on_which_df}")

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
        

    def get_exponential_moving_operation_df(
        self, 
        on_which_df: Literal['main_metric', 'change_in_main_metric'],
        which_operation: Literal['mean', 'var', 'std', 'corr', 'cov'], 
        window: int,
        min_periods: int = 0,
    ) -> pd.DataFrame:
        
        df: pd.DataFrame = pd.DataFrame()
        if on_which_df == 'main_metric':
            df = self.main_metric_df
        elif on_which_df == 'change_in_main_metric':
            df = self.change_in_main_metric_df
        else:
            raise ValueError(f"Unsupported dataframe: {on_which_df}")

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
        
    
    def add_instrument_if_not_present(self, instrument_symbol: str) -> None:
        if instrument_symbol not in self.__instrument_symbols:
            if not self.is_instrument_valid(instrument_symbol):
                raise Exception(f"Unable to add instrument {instrument_symbol}. {instrument_symbol} seems to be invalid")
        
            self.__instrument_symbols.append(instrument_symbol)
            

    def remove_instrument_if_present(self, instrument_symbol: str) -> None:
        if instrument_symbol in self.__instrument_symbols:
            self.__instrument_symbols.remove(instrument_symbol)


    def is_instrument_valid(self, instrument_symbol: str) -> bool:
        returned_df: pd.DataFrame | None = DataframerComponent.get_ohlcv_dataframe_by_symbol(self.__candle_span, instrument_symbol)
        return returned_df is not None


    def valid_instruments(self, instrument_symbols: list[str]) -> list[str]:
        valid_instrument_symbols: list[str] = []
        for instrument_symbol in instrument_symbols:
            if not self.is_instrument_valid(instrument_symbol):
                print(f"[WARNING] Instrument {instrument_symbol} is invalid")
                continue

            valid_instrument_symbols.append(instrument_symbol)

        if len(valid_instrument_symbols) == 0:
            err_msg: str = f"[{self.__class__.__name__}.valid_instruments] no instruments are supplied/valid"
            raise ValueError(err_msg)
        
        return valid_instrument_symbols


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


