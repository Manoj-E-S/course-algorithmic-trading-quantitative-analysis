from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.ohlcvud import OHLCVUDEnum


class BaseApiDataframingService(ABC):
    """
    Base Service Class for transforming API data into a DataFrame.
    """

    def __init__(self):
        pass


    @classmethod
    @abstractmethod
    def _get_aggregated_data_for_multiple_instruments(
        cls,
        *args: Any,
        **kwargs: Any
    ) -> dict[str, dict]:
        """
        Aggregates responses of all instruments in instrument_symbols and returns a dict with symbol as key and its response data as value

        Args:
            *args: Variable length argument list
            **kwargs: Variable length keyword arguments
            /Typical args and kwargs/
                - candle_span (CandlespanEnum): Is the candle requirement daily, weekly or monthly?
                - instrument_symbols (list[str]): Which instruments' api_responses are to be aggregated

        Returns:
            dict: aggregated api_responses
        
        Note:
            If the api fails to fetch some of the instruments' data, they are not aggregated in the returned dict, the partial dict is returned.
            If the api fails to fetch all of the instruments' data, an empty dictionary is returned
        """

        raise NotImplementedError(
            "This method should be implemented in a subclass."
        )
    

    @classmethod
    @abstractmethod
    def get_all_instruments_dataframe_by_metric(
        cls,
        metric: OHLCVUDEnum,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str]
    ) -> pd.DataFrame | None:
        """
        Returns a dataframe with dates as index, instrument symbols as columns and metric as the cell-metric

        Args:
            metric(OHLCVUDEnum): What metric out of OHLCV should be populated as the cell-data
            candle_span(CandlespanEnum): Is the candle requirement daily, weekly or monthly
            instrument_symbols(list[str]): Which instruments' data should be included

        Returns:
            (DataFrame | None): Pandas DataFrame with the required data if the data could be retrieved, None otherwise
        
        Note:
            If the api fails to fetch some of the instruments' data, the partial dataframe is returned.
        """

        raise NotImplementedError(
            "This method should be implemented in a subclass."
        )
    

    @classmethod
    @abstractmethod
    def get_ohlcv_dataframe_by_symbol(
        cls,
        candle_span: CandlespanEnum,
        instrument_symbol: str
    ) -> pd.DataFrame | None:
        """
        Returns a dataframe with dates as index, OHLCV as columns for the said instrument symbol

        Args:
            candle_span(CandlespanEnum): Is the candle requirement daily, weekly or monthly
            instrument_symbol(str): OHLCV Data of which instrument should be included

        Returns:
            (pd.DataFrame | None): DataFrame with the required data if the data could be retrieved, None otherwise
        """

        raise NotImplementedError(
            "This method should be implemented in a subclass."
        )
    


    @classmethod
    @abstractmethod
    def get_instrument_ohlcvdf_dict(
        cls,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str]
    ) -> dict[str, pd.DataFrame]:
        """
        Returns a dict with instrument_symbol as key and its ohlcv dataframe as value

        Args:
            candle_span(CandlespanEnum): Is the candle requirement daily, weekly or monthly?
            instrument_symbols(list[str]): Which instruments' ohlcv dataframes are required

        Returns:
            dict: instrument_symbol - ohlcv_dataframe mapping
        
        Note:
            If the api fails to fetch some of the instruments' data, they are not included in the returned dictionary, the partial dict is returned.
            If the api fails to fetch all of the instruments' data, an empty dictionary is returned
        """

        raise NotImplementedError(
            "This method should be implemented in a subclass."
        )
    

    @classmethod
    @abstractmethod
    def is_instrument_valid(
        cls,
        candle_span: CandlespanEnum,
        instrument_symbol: str
    ) -> bool:
        """
        Checks if the given instrument symbol is valid under the context of the implementing API Dataframeing Service class.

        Args:
            candle_span (CandlespanEnum): The candle span for which the instrument symbol is to be validated.
            instrument_symbol (str): The symbol of the instrument to validate.

        Returns:
            bool: True if the instrument symbol is valid, False otherwise.
        """

        raise NotImplementedError(
            "This method should be implemented in a subclass."
        )
        
