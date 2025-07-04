from functools import cached_property
from typing import Literal

import pandas as pd

from technical_analysis.config.data_view_config import GlobalDataViewConfig
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.models.candlesticks import Candlesticks
from technical_analysis.models.instrument import Instrument
from technical_analysis.models.renko import Renko
from technical_analysis.providers.data_view import DataViewProvider
from technical_analysis.utils.dataframe_date_helper import DataFrameDateIndexHelper
from technical_analysis.utils.decorators import mutually_exclusive_args, optionally_overridable


class InstrumentGroup:
    """
    A class to get all dataframes useful for financial analyses
    """

    def __init__(
        self,
        instrument_symbols: list[str],
        candle_span: CandlespanEnum,
        data_view_provider: DataViewProvider | None = None
    ):
        if data_view_provider is None:
            data_view_provider = GlobalDataViewConfig().get()
            if data_view_provider is None:
                raise ValueError("No DataViewProvider configured globally or custom provided while instantiating InstrumentGroup or its subclasses.")

        self._candle_span: CandlespanEnum = candle_span
        self._views: DataViewProvider = data_view_provider

        print("[WARNING] Initializing InstrumentGroup instruments. Invalid instrument symbols (if any), will be dropped")
        self._instrument_symbols: list[str] = self._filter_valid_instruments(instrument_symbols)
    
    
    # Getters
    @property
    def candle_span(self) -> CandlespanEnum:
        return self._candle_span

    @property
    def instrument_symbols(self) -> list[str]:
        return self._instrument_symbols


    # Chainable Setters
    @candle_span.setter
    def candle_span(self, candle_span: CandlespanEnum) -> 'InstrumentGroup':
        if self._candle_span != candle_span:
            self._candle_span = candle_span
            self._invalidate_cached_properties()
        return self

    @instrument_symbols.setter
    def instrument_symbols(self, instrument_symbols: list[str]) -> 'InstrumentGroup':
        if self._instrument_symbols != instrument_symbols:
            self._instrument_symbols = self._filter_valid_instruments(instrument_symbols)
            self._invalidate_cached_properties()
        return self


    # Cached Dataframes
    @cached_property
    def closes_df(self) -> pd.DataFrame:
        """
        Returns a DataFrame with dates as index, instrument symbols as columns and close prices as the cell-data
        """
        return self._views.instrument_group_metric_view(OHLCVUDEnum.CLOSE, self._candle_span, self._instrument_symbols)


    @cached_property
    def volume_df(self) -> pd.DataFrame:
        """
        Returns a DataFrame with dates as index, instrument symbols as columns and volume as the cell-data
        """
        return self._views.instrument_group_metric_view(OHLCVUDEnum.VOLUME, self._candle_span, self._instrument_symbols)


    @cached_property
    def returns_df(self) -> pd.DataFrame:
        """
        Returns a DataFrame with dates as index, instrument symbols as columns and returns as the cell-data
        """
        return self._views.instrument_group_change_in_metric_view(OHLCVUDEnum.CLOSE, self._candle_span, self._instrument_symbols)


    @cached_property
    def volume_change_df(self) -> pd.DataFrame:
        """
        Returns a DataFrame with dates as index, instrument symbols as columns and volume change as the cell-data
        """
        return self._views.instrument_group_change_in_metric_view(OHLCVUDEnum.VOLUME, self._candle_span, self._instrument_symbols)


    @cached_property
    def cumulative_returns_df(self) -> pd.DataFrame:
        """
        Returns a DataFrame with dates as index, instrument symbols as columns and cumulative returns as the cell-data
        """
        return self._views.instrument_group_cumulative_change_in_metric_view(OHLCVUDEnum.CLOSE, self._candle_span, self._instrument_symbols)


    @cached_property
    def cumulative_volume_change_df(self) -> pd.DataFrame:
        """
        Returns a DataFrame with dates as index, instrument symbols as columns and cumulative volume change as the cell-data
        """
        return self._views.instrument_group_cumulative_change_in_metric_view(OHLCVUDEnum.VOLUME, self._candle_span, self._instrument_symbols)
    

    def get_all_available_dates(
        self,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None
    ) -> pd.DatetimeIndex:
        """
        Returns a DatetimeIndex of available dates between said start and end dates.

        :param start_date: The start date of the range. If None, uses the earliest date.
        :type start_date: pd.Timestamp

        :param end_date: The end date of the range. If None, uses the latest date.
        :type end_date: pd.Timestamp

        :returns pd.DatetimeIndex: A DatetimeIndex of all available dates.
        """
        full_datetime_index: pd.DatetimeIndex = self.closes_df.index

        start_date_idx, end_date_idx = DataFrameDateIndexHelper.resolve_date_range_to_idx_range(
            datetime_index=full_datetime_index,
            from_date=start_date,
            until_date=end_date
        )

        return full_datetime_index[start_date_idx:end_date_idx + 1].sort_values()


    # Public Methods
    def as_instruments(self) -> dict[str, Instrument]:
        return {
            instrument_symbol: Instrument(instrument_symbol, self._candle_span, self._views)
            for instrument_symbol in self._instrument_symbols
        }
    

    def as_candlesticks(self) -> dict[str, Candlesticks]:
        return {
            instrument_symbol: Candlesticks(instrument_symbol, self._candle_span, self._views)
            for instrument_symbol in self._instrument_symbols
        }


    @mutually_exclusive_args("brick_size_from_atr", "brick_size")
    def as_renkos(
        self, 
        brick_size_from_atr: tuple[CandlespanEnum, Renko._NumberOfPeriodsType] | None = None,
        brick_size: int | None = None
    ) -> dict[str, Renko]:
        return {
            instrument_symbol: Renko(instrument_symbol, self._candle_span, self._views, brick_size_from_atr, brick_size)
            for instrument_symbol in self._instrument_symbols
        }
    

    def get_instrument(self, instrument_symbol: str) -> Instrument | None:
        return Instrument(instrument_symbol, self._candle_span, self._views) if self.is_instrument_available(instrument_symbol) else None


    def get_instrument_candlesticks(self, instrument_symbol: str) -> Candlesticks | None:
        return Candlesticks(instrument_symbol, self._candle_span, self._views) if self.is_instrument_available(instrument_symbol) else None


    @mutually_exclusive_args("brick_size_from_atr", "brick_size")
    def get_instrument_renko(
        self, 
        instrument_symbol: str, 
        brick_size_from_atr: tuple[CandlespanEnum, Renko._NumberOfPeriodsType] | None = None,
        brick_size: int | None = None
    ) -> Renko | None:
        return Renko(
            instrument_symbol,
            self._candle_span,
            self._views,
            brick_size_from_atr,
            brick_size
        ) if self.is_instrument_available(instrument_symbol) else None
    

    def is_instrument_available(self, instrument_symbol: str) -> bool:
        return instrument_symbol in self._instrument_symbols
    

    def add_instrument(self, instrument_symbol: str) -> 'InstrumentGroup':
        if instrument_symbol not in self._instrument_symbols:
            if not self._views.source_api.is_instrument_valid(self._candle_span, instrument_symbol):
                raise ValueError(f"Unable to add instrument {instrument_symbol}. {instrument_symbol} seems to be invalid")
        
            self._instrument_symbols.append(instrument_symbol)

        return self
    

    def remove_instrument(self, instrument_symbol: str) -> 'InstrumentGroup':
        if instrument_symbol in self._instrument_symbols:
            self._instrument_symbols.remove(instrument_symbol)

        return self


    def apply_simple_moving_operation(
        self,
        on_which_data: Literal['closes', 'returns', 'cumulative_returns', 'volume', 'volume_change', 'cumulative_volume_change'],
        which_operation: Literal['mean', 'var', 'std', 'corr', 'cov', 'min', 'max'],
        window: int
    ) -> pd.DataFrame:
        
        return self._operate_on_df(
            self._resolve_df(on_which_data),
            operation=which_operation,
            operation_type='simple',
            window=window
        )


    def apply_exponential_moving_operation(
        self,
        on_which_data: Literal['closes', 'returns', 'cumulative_returns', 'volume', 'volume_change', 'cumulative_volume_change'],
        which_operation: Literal['mean', 'var', 'std', 'corr', 'cov'], 
        window: int,
        min_periods: int = 0,
    ) -> pd.DataFrame:
        
        return self._operate_on_df(
            self._resolve_df(on_which_data),
            operation=which_operation,
            operation_type='exponential',
            window=window,
            min_periods=min_periods
        )


    # Protected Methods
    @optionally_overridable
    def _filter_valid_instruments(self, instrument_symbols: list[str]) -> list[str]:
        valid_instrument_symbols: list[str] = []
        for instrument_symbol in instrument_symbols:
            if not self._views.source_api.is_instrument_valid(self._candle_span, instrument_symbol):
                print(f"[WARNING] Instrument {instrument_symbol} is invalid and hence dropped")
                continue

            valid_instrument_symbols.append(instrument_symbol)

        if len(valid_instrument_symbols) == 0:
            err_msg: str = f"[{self.__class__.__name__}.valid_instruments] no instruments are supplied/valid"
            raise ValueError(err_msg)
        
        return valid_instrument_symbols
    

    @optionally_overridable
    def _resolve_df(
        self,
        df_name: Literal['closes', 'returns', 'cumulative_returns', 'volume', 'volume_change', 'cumulative_volume_change']
    ) -> pd.DataFrame:
        """
        Resolves the DataFrame based on the provided DataFrame name.
        """
        unsupported_df_err_msg: str = \
            f"Unsupported Data: {df_name}. Allowed data are: [{', '.join(['closes', 'returns', 'cumulative_returns', 'volume', 'volume_change', 'cumulative_volume_change'])}]."

        if df_name == "closes":
            return self.closes_df
        elif df_name == "returns":
            return self.returns_df
        elif df_name == "cumulative_returns":
            return self.cumulative_returns_df
        elif df_name == "volume":
            return self.volume_df
        elif df_name == "volume_change":
            return self.volume_change_df
        elif df_name == "cumulative_volume_change":
            return self.cumulative_volume_change_df
        else:
            raise ValueError(unsupported_df_err_msg)
        
    
    @optionally_overridable
    def _operate_on_df(
        self,
        df: pd.DataFrame,
        operation: Literal['mean', 'var', 'std', 'min', 'max', 'corr', 'cov'],
        operation_type: Literal['simple', 'exponential'],
        window: int,
        min_periods: int = 0
    ) -> pd.DataFrame:
        """
        Resolves the DataFrame and applies the specified operation.
        """
        unsupported_operation_err_msg: str = \
            f"{operation_type.capitalize()} {operation} operation is not supported. Allowed operations are: [{', '.join(['mean', 'var', 'std', 'corr', 'cov', 'min', 'max'] if operation_type == 'simple' else ['mean', 'var', 'std', 'corr', 'cov'])}]."

        unsupported_operation_type_err_msg: str = \
            f"{operation_type.capitalize()} is an unsupported operation type. Allowed operation types are: ['simple', 'exponential']."

        if operation_type == 'simple':

            if operation == 'mean':
                return df.rolling(window=window, min_periods=min_periods).mean().dropna(axis='index')
            elif operation == 'var':
                return df.rolling(window=window, min_periods=min_periods).var().dropna(axis='index')
            elif operation == 'std':
                return df.rolling(window=window, min_periods=min_periods).std().dropna(axis='index')
            elif operation == 'corr':
                return df.rolling(window=window, min_periods=min_periods).corr().dropna(axis='index')
            elif operation == 'cov':
                return df.rolling(window=window, min_periods=min_periods).cov().dropna(axis='index')
            elif operation == 'min':
                return df.rolling(window=window, min_periods=min_periods).min().dropna(axis='index')
            elif operation == 'max':
                return df.rolling(window=window, min_periods=min_periods).max().dropna(axis='index')
            else:
                raise ValueError(unsupported_operation_err_msg)
            
        elif operation_type == 'exponential':

            if operation == 'mean':
                return df.ewm(span=window, min_periods=min_periods).mean().dropna(axis='index')
            elif operation == 'var':
                return df.ewm(span=window, min_periods=min_periods).var().dropna(axis='index')
            elif operation == 'std':
                return df.ewm(span=window, min_periods=min_periods).std().dropna(axis='index')
            elif operation == 'corr':
                return df.ewm(span=window, min_periods=min_periods).corr().dropna(axis='index')
            elif operation == 'cov':
                return df.ewm(span=window, min_periods=min_periods).cov().dropna(axis='index')
            else:
                raise ValueError(unsupported_operation_err_msg)
            
        else:
            raise ValueError(unsupported_operation_type_err_msg)
        

    @optionally_overridable
    def _invalidate_cached_properties(self) -> None:
        """
        Invalidates all cached properties.

        :return: None
        :rtype: None
        """
        self.__dict__.pop('closes_df', None)
        self.__dict__.pop('returns_df', None)
        self.__dict__.pop('cumulative_returns_df', None)
        self.__dict__.pop('volume_df', None)
        self.__dict__.pop('volume_change_df', None)
        self.__dict__.pop('cumulative_volume_change_df', None)