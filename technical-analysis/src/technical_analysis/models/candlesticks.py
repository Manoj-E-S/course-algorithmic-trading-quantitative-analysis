import pandas as pd

from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.api_dataframing import ApiDataframingServiceEnum
from technical_analysis.models.instrument_group import InstrumentGroup
from technical_analysis.services.base_api_dataframing_service import BaseApiDataframingService


class Candlesticks:
    """
    A class that models ohlcv data as candlesticks
    """

    def __init__(
        self,
        instrument_symbol: str,
        candle_span: CandlespanEnum,
        source_api_class_for_dataframing: ApiDataframingServiceEnum
    ):
        self.__DATAFRAMING_CLASS: type[BaseApiDataframingService] = source_api_class_for_dataframing.value
        self.__candle_span: CandlespanEnum = candle_span

        self.__raise_if_invalid_instrument(instrument_symbol)

        self.__instrument_symbol: str = instrument_symbol
        self.__df: pd.DataFrame = self.__DATAFRAMING_CLASS.get_ohlcv_dataframe_by_symbol(self.candle_span, self.__instrument_symbol)


    # Getters
    @property
    def candle_span(self) -> InstrumentGroup:
        return self.__candle_span
    
    @property
    def instrument_symbol(self) -> str:
        return self.__instrument_symbol
    

    # Chainable Setters
    @candle_span.setter
    def candle_span(self, candle_span: CandlespanEnum) -> 'Candlesticks':
        self.__candle_span = candle_span
        return self
    
    @instrument_symbol.setter
    def instrument_symbol(self, instrument_symbol: str) -> 'Candlesticks':
        self.__instrument_symbol = instrument_symbol
        return self


    # Public Methods
    def get_candlesticks(self) -> pd.DataFrame:
        """
        Returns the candlesticks dataframe.
        """
        return self.__df
    

    # Private methods
    def __raise_if_invalid_instrument(self, instrument_symbol: str) -> None:
        """
        Raises ValueError if the instrument symbol is not valid

        :param instrument_symbol: The instrument symbol to be validated
        :type instrument_symbol: str

        :return: None
        
        :raises ValueError: If the instrument symbol is not valid
        """
        if not self.__DATAFRAMING_CLASS.is_instrument_valid(self.__candle_span, instrument_symbol=instrument_symbol):
            print(f"[ERROR] {self.__class__.__name__} class Initialization Error")
            error_message: str = f"Instrument {instrument_symbol} is invalid"
            raise ValueError(error_message)