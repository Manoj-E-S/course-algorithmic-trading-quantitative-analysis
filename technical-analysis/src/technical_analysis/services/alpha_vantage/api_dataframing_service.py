from typing import Literal, Callable, Optional
import pandas as pd

from technical_analysis.caching.response_cacher import ResponseCacher
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.mappers.candlespan_to_main_json_key import CandlespanToMainJsonKey
from technical_analysis.mappers.candlespan_to_api import CandlespanToApi
from technical_analysis.mappers.candlespan_to_ohlcv_keys import CandlespanToOhlcvKeys
from technical_analysis.mappers.candlespan_to_service_method import CandlespanToServiceMethod
from technical_analysis.services.base_api_dataframing_service import BaseApiDataframingService


class ApiDataframingService(BaseApiDataframingService):
    """
    A Service to map Alpha Vantage JSON responses into pandas.Dataframe and provide related support
    """

    def __init__(self):
        pass


    # override
    @classmethod
    def _get_aggregated_data_for_multiple_instruments(
        cls,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str]
    ) -> dict[str, dict]:
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
            cached_instrument = ResponseCacher().retrieve_from_cache(CandlespanToApi.ForAlphaVantage[candle_span], symbol)

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
            ] = CandlespanToServiceMethod.ForAlphaVantage[candle_span]

            response_data = api_service_method(symbol)

            if not response_data:
                continue

            # Cache the response
            ResponseCacher().cache_response_data(CandlespanToApi.ForAlphaVantage[candle_span], symbol, response_data)

            # Update instruments dict
            instruments[symbol] = response_data
        
        return instruments


    # override
    @classmethod
    def get_all_instruments_dataframe_by_metric(
        cls,
        metric: OHLCVUDEnum,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str]
    ) -> pd.DataFrame | None:
        instruments: dict = ApiDataframingService._get_aggregated_data_for_multiple_instruments(candle_span, instrument_symbols)

        if not instruments: # no instruments were fetched
            return

        symbolwise_closes_dict: dict = {}

        for symbol, json_data in instruments.items():
            datewise_ohlcv: dict = json_data[CandlespanToMainJsonKey.ForAlphaVantage[candle_span]]

            series_data = {
                date: float(values[CandlespanToOhlcvKeys.ForAlphaVantage[candle_span][metric]])
                for date, values in datewise_ohlcv.items() if values
            }
            symbolwise_closes_dict[symbol] = pd.Series(series_data)

        df = pd.DataFrame(symbolwise_closes_dict)

        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        return df
    

    # override
    @classmethod
    def get_ohlcv_dataframe_by_symbol(
        cls,
        candle_span: CandlespanEnum,
        instrument_symbol: str
    ) -> pd.DataFrame | None:
        instruments: dict[str, dict] = ApiDataframingService._get_aggregated_data_for_multiple_instruments(candle_span, [instrument_symbol])

        if instruments.get(instrument_symbol, None) is None: # instrument was not fetched
            return

        datewise_ohlcv: dict = instruments[instrument_symbol][CandlespanToMainJsonKey.ForAlphaVantage[candle_span]]

        datewise_ohlcv_df = (
            pd.DataFrame
            .from_dict(datewise_ohlcv, orient='index', dtype='float64')
            .rename(
                columns={
                    CandlespanToOhlcvKeys.ForAlphaVantage[candle_span][OHLCVUDEnum.OPEN]: OHLCVUDEnum.OPEN.value,
                    CandlespanToOhlcvKeys.ForAlphaVantage[candle_span][OHLCVUDEnum.HIGH]: OHLCVUDEnum.HIGH.value,
                    CandlespanToOhlcvKeys.ForAlphaVantage[candle_span][OHLCVUDEnum.LOW]: OHLCVUDEnum.LOW.value,
                    CandlespanToOhlcvKeys.ForAlphaVantage[candle_span][OHLCVUDEnum.CLOSE]: OHLCVUDEnum.CLOSE.value,
                    CandlespanToOhlcvKeys.ForAlphaVantage[candle_span][OHLCVUDEnum.VOLUME]: OHLCVUDEnum.VOLUME.value
                }
            )
            .filter([
                OHLCVUDEnum.OPEN.value,
                OHLCVUDEnum.HIGH.value,
                OHLCVUDEnum.LOW.value,
                OHLCVUDEnum.CLOSE.value,
                OHLCVUDEnum.VOLUME.value
            ])
        )
        datewise_ohlcv_df.index = pd.to_datetime(datewise_ohlcv_df.index)
        datewise_ohlcv_df.sort_index(inplace=True)

        return datewise_ohlcv_df
    

    # override
    @classmethod
    def get_instrument_ohlcvdf_dict(
        cls,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str]
    ) -> dict[str, pd.DataFrame]:
        dfs_dict: dict[str, pd.DataFrame] = {}
        for instrument_symbol in instrument_symbols:
            df: pd.DataFrame = ApiDataframingService.get_ohlcv_dataframe_by_symbol(candle_span, instrument_symbol)

            if df is None:
                print(f"No data found for the given instrument symbol: {instrument_symbol}")
                print(f"Skipping {instrument_symbol}...")
                continue
            
            dfs_dict[instrument_symbol] = df
        
        return dfs_dict
    

    # override
    @classmethod
    def is_instrument_valid(
        cls,
        candle_span: CandlespanEnum,
        instrument_symbol: str
    ) -> bool:
        symbol_df_dict: dict[str, dict] = ApiDataframingService._get_aggregated_data_for_multiple_instruments(candle_span, [instrument_symbol])
        return symbol_df_dict.get(instrument_symbol, None) is not None

        