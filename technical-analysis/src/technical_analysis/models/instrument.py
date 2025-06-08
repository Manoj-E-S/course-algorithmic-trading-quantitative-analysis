from functools import cached_property

import pandas as pd

from technical_analysis.config.data_view_config import GlobalDataViewConfig
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.providers.data_view import DataViewProvider
from technical_analysis.utils.decorators import optionally_overridable


class Instrument:
    """
    Base class for financial instruments.
    """

    def __init__(
        self,
        instrument_symbol: str,
        candle_span: CandlespanEnum,
        data_view_provider: DataViewProvider | None = None
    ):
        if data_view_provider is None:
            data_view_provider = GlobalDataViewConfig().get()
            if data_view_provider is None:
                raise ValueError("No DataViewProvider configured globally or custom provided while instantiating Instrument or its subclasses.")

        self._views: DataViewProvider = data_view_provider
        self._candle_span: CandlespanEnum = candle_span

        self._raise_if_invalid_instrument(instrument_symbol)
        self._instrument_symbol: str = instrument_symbol


    # Getters
    @property
    def candle_span(self) -> CandlespanEnum:
        return self._candle_span

    @property
    def instrument_symbol(self) -> str:
        return self._instrument_symbol
    
    @cached_property
    def ohlcv_df(self) -> pd.DataFrame:
        return self._views.instrument_ohlcv_view(self._candle_span, self._instrument_symbol)

    @cached_property
    def returns_series(self) -> pd.Series:
        return self._views.instrument_returns_view(self._candle_span, self._instrument_symbol)

    @cached_property
    def cumulative_returns_series(self) -> pd.Series:
        return self._views.instrument_cumulative_returns_view(self._candle_span, self._instrument_symbol)
    

    # Chainable Setters
    @candle_span.setter
    def candle_span(self, candle_span: CandlespanEnum) -> 'Instrument':
        if self._candle_span != candle_span:
            self._candle_span = candle_span
            self._after_property_update()
        return self

    @instrument_symbol.setter
    def instrument_symbol(self, instrument_symbol: str) -> 'Instrument':
        if self._instrument_symbol != instrument_symbol:
            self._raise_if_invalid_instrument(instrument_symbol)
            self._instrument_symbol = instrument_symbol
            self._after_property_update()
        return self


    # Methods
    def _raise_if_invalid_instrument(self, instrument_symbol: str) -> None:
        """
        Raises ValueError if the instrument symbol is not valid

        :param instrument_symbol: The instrument symbol to be validated
        :type instrument_symbol: str

        :return: None
        
        :raises ValueError: If the instrument symbol is not valid
        """
        if not self._views.source_api.is_instrument_valid(self._candle_span, instrument_symbol=instrument_symbol):
            print(f"[ERROR] {self.__class__.__name__} class Initialization Error")
            error_message: str = f"Instrument {instrument_symbol} is invalid"
            raise ValueError(error_message)
        

    @optionally_overridable
    def _after_property_update(self) -> None:
        """
        Perform actions after any properties in the base/subclass are updated.
        
        In Base Class (Instrument): 
            Invalidates cached properties related to OHLCV data, returns, and cumulative returns.
        
        In Subclass:
            May be overridden to perform additional/new actions after property updates.
        
        :return: None
        :rtype: None
        """
        self.__dict__.pop("ohlcv_df", None)
        self.__dict__.pop("returns_series", None)
        self.__dict__.pop("cumulative_returns_series", None)