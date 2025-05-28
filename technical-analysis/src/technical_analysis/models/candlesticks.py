import pandas as pd

from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.api_source import ApiSourceEnum
from technical_analysis.models.instrument import Instrument


class Candlesticks(Instrument):
    """
    A class that models ohlcv data as candlesticks
    """

    def __init__(
        self,
        instrument_symbol: str,
        candle_span: CandlespanEnum,
        api_source: ApiSourceEnum
    ):
        super().__init__(instrument_symbol, candle_span, api_source)

    # Public Methods
    def get_candlesticks(self) -> pd.DataFrame:
        """
        Returns the candlesticks dataframe.
        """
        return self.ohlcv_df