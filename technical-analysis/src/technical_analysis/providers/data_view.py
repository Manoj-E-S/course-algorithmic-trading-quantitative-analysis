import pandas as pd

from technical_analysis.enums.api_source import ApiSourceEnum
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.providers.data_cleaning import DataCleaningProvider
from technical_analysis.services.base_api_dataframing_service import BaseApiDataframingService


class DataViewProvider:
    """
    Provides view(s) of the underlying OHLCV API data suitable for consumption by models.
    """

    def __init__(
        self,
        on_which_api_source: ApiSourceEnum,
        data_cleaning_provider: DataCleaningProvider = DataCleaningProvider(na_strategy='backfill')
    ):
        self._DATAFRAMING_CLASS: type[BaseApiDataframingService] = on_which_api_source.value
        self._data_cleaner = data_cleaning_provider

    
    # Getters
    @property
    def data_cleaner(self) -> DataCleaningProvider:
        return self._data_cleaner
    
    @property
    def source_api(self) -> type[BaseApiDataframingService]:
        """
        Returns the API source class used for data framing.
        
        :return: The class of the API source used for data framing.
        :rtype: type[BaseApiDataframingService]
        """
        return self._DATAFRAMING_CLASS
    

    # Chainable Setters
    @data_cleaner.setter
    def data_cleaner(self, data_cleaning_provider: DataCleaningProvider) -> 'DataViewProvider':
        if self._data_cleaner != data_cleaning_provider:
            self._data_cleaner = data_cleaning_provider
        return self


    # Public Methods
    def instrument_ohlcv_view(self, candle_span: CandlespanEnum, instrument_symbol: str) -> pd.DataFrame:
        """
        Returns the OHLCV view for the instrument.

        :param candle_span: The candle span for the OHLCV data.
        :type candle_span: CandlespanEnum

        :param instrument_symbol: The symbol of the instrument.
        :type instrument_symbol: str

        :return: A DataFrame containing the OHLCV data for the given instrument symbol.
        :rtype: pd.DataFrame

        :raises ValueError: If OHLCV data is not found for the given instrument symbol.
        """
        df: pd.DataFrame | None = self._DATAFRAMING_CLASS.get_ohlcv_dataframe_by_symbol(candle_span, instrument_symbol)

        if df is None or df.empty:
            raise ValueError(f"No {candle_span.value} OHLCV data found for instrument symbol: {instrument_symbol}.")

        return self.data_cleaner.clean(df)
    

    def instrument_returns_view(
        self,
        candle_span: CandlespanEnum,
        instrument_symbol: str
    ) -> pd.Series:
        """
        Returns the returns view for the instrument.
        
        :param candle_span: The candle span for the returns data.
        :type candle_span: CandlespanEnum
        
        :param instrument_symbol: The symbol of the instrument.
        :type instrument_symbol: str
        
        :return: A Series containing the returns data for the given instrument symbol.
        :rtype: pd.Series
        
        :raises ValueError: If returns data is not found for the given instrument symbol.
        """
        df: pd.DataFrame = self.instrument_ohlcv_view(candle_span, instrument_symbol)

        if df.empty:
            raise ValueError(f"No {candle_span.value} returns data found for instrument symbol: {instrument_symbol}.")

        return df[OHLCVUDEnum.CLOSE.value].pct_change(fill_method=None).dropna(axis='index')
    

    def instrument_cumulative_returns_view(
        self,
        candle_span: CandlespanEnum,
        instrument_symbol: str,
        initial_value: float = 1.0
    ) -> pd.Series:
        """
        Returns the cumulative returns view for the instrument.

        :param candle_span: The candle span for the cumulative returns data.
        :type candle_span: CandlespanEnum

        :param instrument_symbol: The symbol of the instrument.
        :type instrument_symbol: str

        :param initial_value: The initial value to start the cumulative returns calculation from. Default is 1.0.
        :type initial_value: float

        :return: A Series containing the cumulative returns data for the given instrument symbol.
        :rtype: pd.Series

        :raises ValueError: If cumulative returns data is not found for the given instrument symbol.
        """
        returns_series = self.instrument_returns_view(candle_span, instrument_symbol)
        return initial_value * (1 + returns_series).cumprod().dropna(axis='index')


    def instrument_group_ohlcv_view(
        self,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str]
    ) -> dict[str, pd.DataFrame]:
        """
        Returns the OHLCV view for a group of instruments.

        :param candle_span: The candle span for the OHLCV data.
        :type candle_span: CandlespanEnum

        :param instrument_symbols: A list of instrument symbols.
        :type instrument_symbols: list[str]

        :return: A dictionary where keys are instrument symbols and values are DataFrames containing the OHLCV data. If OHLCV data is fetched only for some of the instrument symbols, the dictionary will contain only those symbols.
        :rtype: dict[str, pd.DataFrame]

        :raises ValueError: If OHLCV data is not found for any given instrument symbols.
        """
        dfs_dict: dict[str, pd.DataFrame] = {}

        for instrument_symbol in instrument_symbols:
            try:
                df = self.instrument_ohlcv_view(candle_span, instrument_symbol)
                dfs_dict[instrument_symbol] = df
            except Exception as e:
                print(f"[WARN] Skipping {instrument_symbol} due to error: {e}")
                continue

        if not dfs_dict:
            raise ValueError(f"No {candle_span.value} OHLCV data found for any of the instrument symbols: {instrument_symbols}.")

        return dfs_dict
    

    def instrument_group_metric_view(
        self,
        metric: OHLCVUDEnum,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str]
    ) -> pd.DataFrame:
        """
        Returns the view of a specific metric for a group of instruments.

        :param metric: The metric to be fetched (e.g., 'close', 'volume').
        :type metric: OHLCVUDEnum
        
        :param candle_span: The candle span for the metric data.
        :type candle_span: CandlespanEnum

        :param instrument_symbols: A list of instrument symbols.
        :type instrument_symbols: list[str]

        :return: A DataFrame containing the specified metric data for all of the given instrument symbols. If some of the instrument symbols do not have data for the specified metric, they will not be included in the DataFrame.
        :rtype: pd.DataFrame

        :raises ValueError: If no data is found for the given instrument symbols and metric.
        """
        df: pd.DataFrame | None = self._DATAFRAMING_CLASS.get_all_instruments_dataframe_by_metric(metric, candle_span, instrument_symbols)

        if df is None or df.empty:
            raise ValueError(f"No {candle_span.value} {metric.value} data found for instrument symbols: {instrument_symbols}.")

        return self.data_cleaner.clean(df)


    def instrument_group_change_in_metric_view(
        self,
        metric: OHLCVUDEnum,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str]
    ) -> pd.DataFrame:
        """
        Returns the view of the change in a specific metric for a group of instruments.

        :param metric: The metric to be fetched (e.g., 'close', 'volume').
        :type metric: OHLCVUDEnum

        :param candle_span: The candle span for the change in metric data.
        :type candle_span: CandlespanEnum

        :param instrument_symbols: A list of instrument symbols.
        :type instrument_symbols: list[str]

        :return: A DataFrame containing the change in the specified metric data for all of the given instrument symbols. If some of the instrument symbols do not have data for the specified metric, they will not be included in the DataFrame.
        :rtype: pd.DataFrame

        :raises ValueError: If no data is found for the given instrument symbols and metric.
        """
        df: pd.DataFrame = self.instrument_group_metric_view(metric, candle_span, instrument_symbols)
        return df.pct_change(fill_method=None).dropna(axis='index')
    

    def instrument_group_cumulative_change_in_metric_view(
        self,
        metric: OHLCVUDEnum,
        candle_span: CandlespanEnum,
        instrument_symbols: list[str],
        initial_value: float = 1.0
    ) -> pd.DataFrame:
        """
        Returns the view of the cumulative change in a specific metric for a group of instruments.

        :param metric: The metric to be fetched (e.g., 'close', 'volume').
        :type metric: OHLCVUDEnum

        :param candle_span: The candle span for the cumulative change in metric data.
        :type candle_span: CandlespanEnum

        :param instrument_symbols: A list of instrument symbols.
        :type instrument_symbols: list[str]

        :param initial_value: The initial value to start the cumulative change calculation from. Default is 1.0.
        :type initial_value: float

        :return: A DataFrame containing the cumulative change in the specified metric data for all of the given instrument symbols. If some of the instrument symbols do not have data for the specified metric, they will not be included in the DataFrame.
        :rtype: pd.DataFrame

        :raises ValueError: If no data is found for the given instrument symbols and metric.
        """
        return initial_value * (1 + self.instrument_group_change_in_metric_view(metric, candle_span, instrument_symbols)).cumprod().dropna(axis='index')