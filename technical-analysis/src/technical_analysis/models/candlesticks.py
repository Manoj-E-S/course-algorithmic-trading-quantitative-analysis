import pandas as pd

from technical_analysis.config.data_view_config import GlobalDataViewConfig
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.models.instrument import Instrument
from technical_analysis.providers.data_view import DataViewProvider


class Candlesticks(Instrument):
    """
    A class that models ohlcv data as candlesticks
    """

    def __init__(
        self,
        instrument_symbol: str,
        candle_span: CandlespanEnum,
        data_view_provider: DataViewProvider | None = None
    ):
        super().__init__(instrument_symbol, candle_span, data_view_provider)


    # Properties
    @property
    def candle_df(self) -> pd.DataFrame:
        """
        Returns the candlesticks dataframe.
        """
        return self.ohlcv_df