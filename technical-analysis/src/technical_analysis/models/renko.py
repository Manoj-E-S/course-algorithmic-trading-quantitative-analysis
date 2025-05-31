from functools import cached_property
import pandas as pd

from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.indicators.indicator_calculator import IndicatorCalculator
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.models.instrument import Instrument
from technical_analysis.providers.data_view import DataViewProvider
from technical_analysis.utils.decorators import mutually_exclusive_args, override


class Renko(Instrument):
    """
    A static class that helps in modeling regular candlestick data as renko data
    """
    # Type Aliases
    _NumberOfPeriodsType = int
    _RenkoBrickType = tuple[pd.Timestamp, float, float, float, float, bool]  # [datetime, open, high, low, close, uptrend]

    # Helper Variables
    _RenkoColumnHeaders: list[str] = [
        OHLCVUDEnum.DATETIME.value,
        OHLCVUDEnum.OPEN.value,
        OHLCVUDEnum.HIGH.value,
        OHLCVUDEnum.LOW.value,
        OHLCVUDEnum.CLOSE.value,
        OHLCVUDEnum.UPTREND.value
    ]

    @mutually_exclusive_args("brick_size_from_atr", "brick_size")
    def __init__(
        self,
        instrument_symbol: str,
        source_candle_span: CandlespanEnum,
        data_view_provider: DataViewProvider,
        brick_size_from_atr: tuple[CandlespanEnum, _NumberOfPeriodsType] | None = None,
        brick_size: int | None = None
    ):
        super().__init__(instrument_symbol, source_candle_span, data_view_provider)

        if brick_size is not None:
            self.__brick_size: int = brick_size
        else:
            self.__brick_size: int = self.__get_brick_size_from_atr(*brick_size_from_atr)


    # Getters
    @property
    def source_candle_span(self) -> CandlespanEnum:
        return self._candle_span
    
    @property
    def brick_size(self) -> int:
        return self.__brick_size
    

    # Chainable Setters
    @brick_size.setter
    def brick_size(self, brick_size: int) -> 'Renko':
        if self.__brick_size != brick_size:
            self.__brick_size = brick_size
            self._after_property_update()
        return self
    
    @source_candle_span.setter
    def source_candle_span(self, source_candle_span: CandlespanEnum) -> 'Renko':
        if self._candle_span != source_candle_span:
            self._candle_span = source_candle_span
            self._after_property_update()
        return self
    

    # Cached Properties
    @cached_property
    def source_candle_df(self) -> pd.DataFrame:

        candle_df: pd.DataFrame = self.ohlcv_df.copy(deep=True)
        candle_df.reset_index(inplace=True)
        candle_df.rename(columns={'index': OHLCVUDEnum.DATETIME.value}, inplace=True)
        candle_df[OHLCVUDEnum.DATETIME.value] = pd.to_datetime(candle_df[OHLCVUDEnum.DATETIME.value])

        return candle_df


    @cached_property
    def renko_df(self) -> pd.DataFrame:
        """
        Returns the renko dataframe for the instrument symbol

        :return: pd.DataFrame containing renko data
        :rtype: pd.DataFrame
        """
        rdf: pd.DataFrame = pd.DataFrame(columns=Renko._RenkoColumnHeaders, data=None)
        rdf.loc[0, :] = self.__get_initial_uptrend_renko_brick()
        
        for _, candle in self.source_candle_df.iterrows():
            prev_renko_brick: pd.Series = rdf.iloc[-1]
            
            curr_candle_date: pd.Timestamp   = pd.Timestamp(candle[OHLCVUDEnum.DATETIME.value])
            curr_candle_close: float         = float(candle[OHLCVUDEnum.CLOSE.value])
            curr_candle_high: float          = float(candle[OHLCVUDEnum.HIGH.value])
            curr_candle_low: float           = float(candle[OHLCVUDEnum.LOW.value])

            prev_renko_uptrend: bool        = prev_renko_brick[OHLCVUDEnum.UPTREND.value]
            prev_renko_close: float         = prev_renko_brick[OHLCVUDEnum.CLOSE.value]
            prev_renko_open: float          = prev_renko_brick[OHLCVUDEnum.OPEN.value]

            signed_num_bricks: int = self.__calculate_signed_num_of_bricks(curr_candle_close, prev_renko_close)

            next_bricks: list[Renko._RenkoBrickType] = self.__generate_next_bricks(
                curr_candle_date,
                curr_candle_high,
                curr_candle_low,
                prev_renko_close,
                prev_renko_open,
                prev_renko_uptrend,
                signed_num_bricks
            )
            
            if next_bricks:
                df_of_next_bricks = pd.DataFrame(data=next_bricks, columns=Renko._RenkoColumnHeaders)
                rdf = pd.concat([rdf, df_of_next_bricks], axis='index', ignore_index=True)

        rdf[OHLCVUDEnum.DATETIME.value] = pd.to_datetime(rdf[OHLCVUDEnum.DATETIME.value])
        return rdf

    
    # Private Methods
    def __get_brick_size_from_atr(
        self,
        candle_span: CandlespanEnum,
        periods: int
    ) -> int:
        
        candle_df_for_atr: pd.DataFrame = self._views.instrument_ohlcv_view(candle_span, self.instrument_symbol)
        candle_df_for_atr = IndicatorCalculator.atr(candle_df_for_atr, periods)
        return 3 * round(candle_df_for_atr["atr"].iloc[-1])
    

    def __get_initial_uptrend_renko_brick(self) -> _RenkoBrickType:
        """
        Returns the initial uptrend renko brick based on the first row of the source candle dataframe.
        """
        source_candle_df: pd.DataFrame = self.source_candle_df

        close: float        = (float(source_candle_df.loc[0, OHLCVUDEnum.CLOSE.value]) // self.__brick_size) * self.__brick_size
        low: float          = float(source_candle_df.loc[0, OHLCVUDEnum.LOW.value])
        date: pd.Timestamp  = pd.Timestamp(source_candle_df.loc[0, OHLCVUDEnum.DATETIME.value])
        uptrend: bool       = True

        return (date, close - self.__brick_size, close, min(low, close - self.__brick_size), close, uptrend)


    def __calculate_signed_num_of_bricks(
        self,
        curr_candle_close: float,
        prev_renko_close: float
    ) -> int:
        return int((curr_candle_close - prev_renko_close) / self.__brick_size)


    def __generate_next_bricks(
        self,
        curr_candle_date: pd.Timestamp,
        curr_candle_high: float,
        curr_candle_low: float,
        prev_renko_close: float,
        prev_renko_open: float,
        prev_renko_uptrend: bool,
        signed_num_bricks: int
    ) -> list[_RenkoBrickType]:

        if prev_renko_uptrend and signed_num_bricks >= 1:
            return self.__continue_uptrend(curr_candle_date, curr_candle_low, prev_renko_close, prev_renko_open, abs(signed_num_bricks))
        elif prev_renko_uptrend and signed_num_bricks <= -2:
            return self.__reverse_to_downtrend(curr_candle_date, curr_candle_high, prev_renko_close, prev_renko_open, abs(signed_num_bricks + 1))
        elif not prev_renko_uptrend and signed_num_bricks <= -1:
            return self.__continue_downtrend(curr_candle_date, curr_candle_high, prev_renko_close, prev_renko_open, abs(signed_num_bricks))
        elif not prev_renko_uptrend and signed_num_bricks >= 2:
            return self.__reverse_to_uptrend(curr_candle_date, curr_candle_low, prev_renko_close, prev_renko_open, abs(signed_num_bricks - 1))

        return []


    def __continue_uptrend(
        self,
        curr_candle_date: pd.Timestamp,
        curr_candle_low: float,
        prev_renko_close: float,
        prev_renko_open: float,
        num_bricks: int
    ) -> list[_RenkoBrickType]:
        
        bricks = []
        for _ in range(num_bricks):
            close = prev_renko_close + self.__brick_size
            low = min(max(curr_candle_low, prev_renko_open - self.__brick_size), prev_renko_close)

            brick: Renko._RenkoBrickType = (curr_candle_date, prev_renko_close, close, low, close, True)
            bricks.append(brick)

            prev_renko_close += self.__brick_size
            prev_renko_open += self.__brick_size

        return bricks


    def __reverse_to_downtrend(
        self,
        curr_candle_date: pd.Timestamp,
        curr_candle_high: float,
        prev_renko_close: float,
        prev_renko_open: float,
        num_bricks: int
    ) -> list[_RenkoBrickType]:
        
        bricks = []
        for _ in range(abs(num_bricks)):
            high = max(min(curr_candle_high, prev_renko_close + self.__brick_size), prev_renko_open)
            close = prev_renko_open - self.__brick_size

            brick: Renko._RenkoBrickType = (curr_candle_date, prev_renko_open, high, close, close, False)
            bricks.append(brick)

            prev_renko_close -= self.__brick_size
            prev_renko_open -= self.__brick_size

        return bricks


    def __continue_downtrend(
        self,
        curr_candle_date: pd.Timestamp,
        curr_candle_high: float,
        prev_renko_close: float,
        prev_renko_open: float,
        num_bricks: int
    ) -> list[_RenkoBrickType]:
        
        bricks = []
        for _ in range(abs(num_bricks)):
            high = max(min(curr_candle_high, prev_renko_open + self.__brick_size), prev_renko_close)
            close = prev_renko_close - self.__brick_size

            brick: Renko._RenkoBrickType = (curr_candle_date, prev_renko_close, high, close, close, False)
            bricks.append(brick)

            prev_renko_close -= self.__brick_size
            prev_renko_open -= self.__brick_size

        return bricks


    def __reverse_to_uptrend(
        self,
        curr_candle_date: pd.Timestamp,
        curr_candle_low: float,
        prev_renko_close: float,
        prev_renko_open: float,
        num_bricks: int
    ) -> list[_RenkoBrickType]:
        
        bricks = []
        for _ in range(num_bricks):
            close = prev_renko_open + self.__brick_size
            low = min(max(curr_candle_low, prev_renko_close - self.__brick_size), prev_renko_open)

            brick: Renko._RenkoBrickType = (curr_candle_date, prev_renko_open, close, low, close, True)
            bricks.append(brick)

            prev_renko_close += self.__brick_size
            prev_renko_open += self.__brick_size

        return bricks
    

    @override
    def _after_property_update(self) -> None:
        """
        Cleans up the renko_df attribute after any property update to ensure it is recalculated when needed.
        """
        super()._after_property_update()
        self.__dict__.pop("renko_df", None)
        self.__dict__.pop("source_candle_df", None)
