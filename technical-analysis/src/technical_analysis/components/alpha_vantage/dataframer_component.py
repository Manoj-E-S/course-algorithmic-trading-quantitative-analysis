from typing import Literal, Callable, Optional
import pandas as pd

from technical_analysis.components import ResponseCacherComponent
from technical_analysis.mappers import CandlespanMappers, ToTimeSeriesJsonKeyMappers
from technical_analysis.models import CandlespanEnum, OHLCVEnum

class DataframerComponent:
    """
    A component to map JSON responses into pandas.Dataframe and provide related support
    """

    def __init__(self):
        pass


    @staticmethod
    def __get_aggregated_data_for_multiple_instruments(
        candle_span: CandlespanEnum,
        instrument_symbols: list[str]
    ) -> dict:
        """
        Aggregates responses of all instruments in instrument_symbols and returns a dict with symbol as key and its response data as value

        Args:
            candle_span(CandlespanEnum): Is the candle requirement daily, weekly or monthly
            instrument_symbols(list[str]): Which instruments' api_responses are to be aggregated

        Returns:
            dict: aggregated api_responses
        
        Note:
            If the api fails to fetch some of the instruments' data, they are not aggregated in the returned , the partial dict is returned.
            If the api fails to fetch all of the instruments' data, an empty dictionary is returned
        """
        instruments: dict = {}
        for symbol in instrument_symbols:
            # Get cached data if available
            cached_instrument = ResponseCacherComponent.retrieve_from_cache(CandlespanMappers.CANDLESPAN_ALPHAVANTAGEENUM_MAPPER[candle_span], symbol)

            if cached_instrument:
                instruments[symbol] = cached_instrument
                continue

            # Make API Call
            api_service_method: Callable[
                [
                    str, 
                    Optional[Literal['full', 'compact']], 
                    Optional[Literal['json', 'csv']]
                ], 
                dict | None
            ] = CandlespanMappers.CANDLESPAN_SERVICEMETHOD_MAPPER[candle_span]

            response_data = api_service_method(symbol)

            if not response_data:
                continue

            # Cache the response
            ResponseCacherComponent.cache_response_data(CandlespanMappers.CANDLESPAN_ALPHAVANTAGEENUM_MAPPER[candle_span], symbol, response_data)

            # Update instruments dict
            instruments[symbol] = response_data
        
        return instruments


    @staticmethod
    def get_dataframe(
        of_metric: OHLCVEnum,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str]
    ) -> pd.DataFrame | None:
        """
        Returns a dataframe with dates as index, instrument symbols as columns and of_metric as the cell-metric

        Args:
            of_metric(OHLCVEnum): What metric out of OHLCV should be populated as the cell-data
            candle_span(CandlespanEnum): Is the candle requirement daily, weekly or monthly
            instrument_symbols(list[str]): Which instruments' data should be included

        Returns:
            (DataFrame | None): Pandas DataFrame with the required data if the data could be retrieved, None otherwise
        
        Note:
            If the api fails to fetch some of the instruments' data, the partial dataframe is returned.
        """
        instruments: dict = DataframerComponent.__get_aggregated_data_for_multiple_instruments(candle_span, instrument_symbols)

        if not instruments: # no instruments were fetched
            return

        symbolwise_closes_dict: dict = {}

        for symbol, json_data in instruments.items():
            datewise_ohlcv: dict = json_data[ToTimeSeriesJsonKeyMappers.CANDLESPAN_MAINJSONKEY_MAPPER[candle_span]]

            series_data = {
                date: float(values[CandlespanMappers.CANDLESPAN_OHLCVMAPPER_MAPPER[candle_span][of_metric]])
                for date, values in datewise_ohlcv.items() if values
            }
            symbolwise_closes_dict[symbol] = pd.Series(series_data)

        df = pd.DataFrame(symbolwise_closes_dict)

        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        return df
            