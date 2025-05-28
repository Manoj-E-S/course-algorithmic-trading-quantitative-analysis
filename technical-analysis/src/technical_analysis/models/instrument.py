import pandas as pd

from technical_analysis.enums.api_source import ApiSourceEnum
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.services.base_api_dataframing_service import BaseApiDataframingService
from technical_analysis.utils.decorators import optionally_overridable


class Instrument:
    """
    Base class for financial instruments.
    """

    def __init__(
        self,
        instrument_symbol: str,
        candle_span: CandlespanEnum,
        api_source: ApiSourceEnum
    ):
        self._DATAFRAMING_CLASS: type[BaseApiDataframingService] = api_source.value
        self._candle_span: CandlespanEnum = candle_span

        self._raise_if_invalid_instrument(instrument_symbol)
        self._instrument_symbol: str = instrument_symbol
        
        self._after_property_update()


    # Getters
    @property
    def candle_span(self) -> str:
        return self._candle_span.value

    @property
    def instrument_symbol(self) -> str:
        return self._instrument_symbol
    
    @property
    def ohlcv_df(self) -> pd.DataFrame:
        return self._df
    

    # Chainable Setters
    @candle_span.setter
    def candle_span(self, candle_span: CandlespanEnum) -> 'Instrument':
        self._candle_span = candle_span
        self._after_property_update()
        return self

    @instrument_symbol.setter
    def instrument_symbol(self, instrument_symbol: str) -> 'Instrument':
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
        if not self._DATAFRAMING_CLASS.is_instrument_valid(self._candle_span, instrument_symbol=instrument_symbol):
            print(f"[ERROR] {self.__class__.__name__} class Initialization Error")
            error_message: str = f"Instrument {instrument_symbol} is invalid"
            raise ValueError(error_message)
        

    @optionally_overridable
    def _after_property_update(self) -> None:
        """
        Perform actions after any properties in the base/subclass are updated.
        
        In Base Class: 
            sets the ohlcv_df, indicators, and charter for the current instrument symbol and candle span.
        
        In Subclass:
            May be overridden to perform additional actions after property updates.
        
        :return: None
        :rtype: None
        """
        self._df = self._DATAFRAMING_CLASS.get_ohlcv_dataframe_by_symbol(self._candle_span, self._instrument_symbol)