from typing import Literal, Callable, Optional
import pandas as pd

from technical_analysis.components import ResponseCacherComponent
from technical_analysis.mappers import CandlespanMappers, ToTimeSeriesJsonKeyMappers
from technical_analysis.models import CandlespanEnum, OHLCVEnum

class DataframerComponent:
    """
    A component to map JSON responses into pandas.Dataframe and provide related support
    """
    ResponseCacherComponent.set_cache_threshold_period(5)

    def __init__(self):
        pass


    @staticmethod
    def __get_aggregated_data_for_multiple_instruments(
        candle_span: CandlespanEnum,
        instrument_symbols: list[str],
        use_api_cache_when_applicable: bool = True
    ) -> dict[str, dict]:
        """
        Aggregates responses of all instruments in instrument_symbols and returns a dict with symbol as key and its response data as value

        Args:
            candle_span(CandlespanEnum): Is the candle requirement daily, weekly or monthly
            instrument_symbols(list[str]): Which instruments' api_responses are to be aggregated
            use_api_cache_when_applicable(bool): Retrieve from cache if applicable

        Returns:
            dict: aggregated api_responses
        
        Note:
            If the api fails to fetch some of the instruments' data, they are not aggregated in the returned , the partial dict is returned.
            If the api fails to fetch all of the instruments' data, an empty dictionary is returned
        """
        instruments: dict = {}
        for symbol in instrument_symbols:
            cached_instrument = None
            if use_api_cache_when_applicable:
                # Get cached data if available
                cached_instrument = ResponseCacherComponent.retrieve_from_cache(CandlespanMappers.CANDLESPAN_ALPHAVANTAGEENUM_MAPPER[candle_span], symbol)

            if cached_instrument is not None:
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
    def get_dataframe_of_metric(
        metric: OHLCVEnum,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str],
        use_api_cache_when_applicable: bool = True
    ) -> pd.DataFrame | None:
        """
        Returns a dataframe with dates as index, instrument symbols as columns and metric as the cell-metric

        Args:
            metric(OHLCVEnum): What metric out of OHLCV should be populated as the cell-data
            candle_span(CandlespanEnum): Is the candle requirement daily, weekly or monthly
            instrument_symbols(list[str]): Which instruments' data should be included

        Returns:
            (DataFrame | None): Pandas DataFrame with the required data if the data could be retrieved, None otherwise
        
        Note:
            If the api fails to fetch some of the instruments' data, the partial dataframe is returned.
        """
        instruments: dict = DataframerComponent.__get_aggregated_data_for_multiple_instruments(candle_span, instrument_symbols, use_api_cache_when_applicable)

        if not instruments: # no instruments were fetched
            return

        symbolwise_closes_dict: dict = {}

        for symbol, json_data in instruments.items():
            datewise_ohlcv: dict = json_data[ToTimeSeriesJsonKeyMappers.CANDLESPAN_MAINJSONKEY_MAPPER[candle_span]]

            series_data = {
                date: float(values[CandlespanMappers.CANDLESPAN_OHLCVMAPPER_MAPPER[candle_span][metric]])
                for date, values in datewise_ohlcv.items() if values
            }
            symbolwise_closes_dict[symbol] = pd.Series(series_data)

        df = pd.DataFrame(symbolwise_closes_dict)

        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        return df
    

    @staticmethod
    def get_ohlcv_dataframe_by_symbol(
        candle_span: CandlespanEnum,
        instrument_symbol: str,
        use_api_cache_when_applicable: bool = True
    ) -> pd.DataFrame | None:
        """
        Returns a dataframe with dates as index, instrument symbols as columns and metric as the cell-metric

        Args:
            metric(OHLCVEnum): What metric out of OHLCV should be populated as the cell-data
            candle_span(CandlespanEnum): Is the candle requirement daily, weekly or monthly
            instrument_symbol(str): Data of which instrument should be included

        Returns:
            (pd.DataFrame | None): DataFrame with the required data if the data could be retrieved, None otherwise
        """
        instruments: dict[str, dict] = DataframerComponent.__get_aggregated_data_for_multiple_instruments(candle_span, [instrument_symbol], use_api_cache_when_applicable)

        if instruments.get(instrument_symbol, None) is None: # instrument was not fetched
            return

        datewise_ohlcv: dict = instruments[instrument_symbol][ToTimeSeriesJsonKeyMappers.CANDLESPAN_MAINJSONKEY_MAPPER[candle_span]]

        datewise_ohlcv_df = (
            pd.DataFrame
            .from_dict(datewise_ohlcv, orient='index', dtype='float64')
            .rename(
                columns={
                    CandlespanMappers.CANDLESPAN_OHLCVMAPPER_MAPPER[candle_span][OHLCVEnum.OPEN]: OHLCVEnum.OPEN.value,
                    CandlespanMappers.CANDLESPAN_OHLCVMAPPER_MAPPER[candle_span][OHLCVEnum.HIGH]: OHLCVEnum.HIGH.value,
                    CandlespanMappers.CANDLESPAN_OHLCVMAPPER_MAPPER[candle_span][OHLCVEnum.LOW]: OHLCVEnum.LOW.value,
                    CandlespanMappers.CANDLESPAN_OHLCVMAPPER_MAPPER[candle_span][OHLCVEnum.CLOSE]: OHLCVEnum.CLOSE.value,
                    CandlespanMappers.CANDLESPAN_OHLCVMAPPER_MAPPER[candle_span][OHLCVEnum.VOLUME]: OHLCVEnum.VOLUME.value
                }
            )
            .filter([
                OHLCVEnum.OPEN.value,
                OHLCVEnum.HIGH.value,
                OHLCVEnum.LOW.value,
                OHLCVEnum.CLOSE.value,
                OHLCVEnum.VOLUME.value
            ])
        )
        datewise_ohlcv_df.index = pd.to_datetime(datewise_ohlcv_df.index)
        datewise_ohlcv_df.sort_index(inplace=True)

        return datewise_ohlcv_df
        