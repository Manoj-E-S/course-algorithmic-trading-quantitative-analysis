import pandas as pd

from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.indicators.indicator_calculator import IndicatorCalculator
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.api_dataframing import ApiDataframingServiceEnum
from technical_analysis.services.base_api_dataframing_service import BaseApiDataframingService
from technical_analysis.utils.decorators import mutually_exclusive_args


class Renko:
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

    @mutually_exclusive_args("brick_size_from_atr_of", "brick_size")
    def __init__(
        self,
        instrument_symbol: str,
        source_candle_span: CandlespanEnum,
        source_api_class_for_dataframing: ApiDataframingServiceEnum,
        brick_size_from_atr_of: tuple[CandlespanEnum, _NumberOfPeriodsType] | None = None,
        brick_size: int | None = None
    ):
        self.__DATAFRAMING_CLASS: type[BaseApiDataframingService] = source_api_class_for_dataframing.value
        self.__source_candle_span: CandlespanEnum = source_candle_span

        self.__raise_if_invalid_instrument(instrument_symbol)
        self.__instrument_symbol: str = instrument_symbol

        if brick_size is not None:
            self.__brick_size: int = brick_size
        else:
            self.__brick_size: int = self.__get_brick_size_from_atr(*brick_size_from_atr_of)


    # Getters
    @property
    def source_candle_span(self) -> str:
        return self.__source_candle_span.value

    @property
    def instrument_symbol(self) -> str:
        return self.__instrument_symbol
    
    @property
    def brick_size(self) -> int:
        return self.__brick_size
    

    @property
    def source_candle_df(self) -> pd.DataFrame:
        """
        Returns the source candle dataframe for the instrument symbol

        :return: pd.DataFrame containing source candle data
        :rtype: pd.DataFrame
        """
        candle_df: pd.DataFrame = self.__DATAFRAMING_CLASS.get_ohlcv_dataframe_by_symbol(
            candle_span=self.__source_candle_span,
            instrument_symbol=self.__instrument_symbol,
        )
        candle_df.reset_index(inplace=True)
        candle_df.rename(columns={'index': OHLCVUDEnum.DATETIME.value}, inplace=True)
        candle_df[OHLCVUDEnum.DATETIME.value] = pd.to_datetime(candle_df[OHLCVUDEnum.DATETIME.value])

        return candle_df


    def get_renko(self) -> pd.DataFrame:
        """
        Returns the renko dataframe for the instrument symbol

        :return: pd.DataFrame containing renko data
        :rtype: pd.DataFrame
        """
        renko_df: pd.DataFrame = pd.DataFrame(columns=Renko._RenkoColumnHeaders, data=None)
        renko_df.loc[0, :] = self.__get_initial_uptrend_renko_brick()
        
        for _, candle in self.source_candle_df.iterrows():
            prev_renko_brick: pd.Series = renko_df.iloc[-1]
            
            curr_renko_close: float         = float(candle[OHLCVUDEnum.CLOSE.value])
            curr_renko_date: pd.Timestamp   = pd.Timestamp(candle[OHLCVUDEnum.DATETIME.value])
            curr_renko_high: float          = float(candle[OHLCVUDEnum.HIGH.value])
            curr_renko_low: float           = float(candle[OHLCVUDEnum.LOW.value])

            prev_renko_uptrend: bool        = prev_renko_brick[OHLCVUDEnum.UPTREND.value]
            prev_renko_close: float         = prev_renko_brick[OHLCVUDEnum.CLOSE.value]
            prev_renko_open: float          = prev_renko_brick[OHLCVUDEnum.OPEN.value]

            signed_num_of_bricks: int = self.__calculate_signed_num_of_bricks(curr_renko_close, prev_renko_close)

            next_bricks: list[Renko._RenkoBrickType] = self.__generate_next_bricks(
                curr_date = curr_renko_date,
                curr_high = curr_renko_high,
                curr_low = curr_renko_low,
                prev_close = prev_renko_close,
                prev_open = prev_renko_open,
                uptrend = prev_renko_uptrend,
                signed_num_bricks = signed_num_of_bricks
            )
            
            if next_bricks:
                df_of_next_bricks = pd.DataFrame(data=next_bricks, columns=Renko._RenkoColumnHeaders)
                renko_df = pd.concat([renko_df, df_of_next_bricks], axis='index', ignore_index=True)

        renko_df[OHLCVUDEnum.DATETIME.value] = pd.to_datetime(renko_df[OHLCVUDEnum.DATETIME.value])
        return renko_df

    
    def __get_brick_size_from_atr(
        self,
        candle_span: CandlespanEnum,
        periods: int
    ) -> int:
        
        candle_df_for_atr: pd.DataFrame = self.__DATAFRAMING_CLASS.get_ohlcv_dataframe_by_symbol(
            candle_span=candle_span,
            instrument_symbol=self.__instrument_symbol,
        )
        candle_df_for_atr = IndicatorCalculator.atr(candle_df_for_atr, periods)
        return 3 * round(candle_df_for_atr["atr"].iloc[-1])
    

    def __get_initial_uptrend_renko_brick(self) -> _RenkoBrickType:
        """
        Returns the initial uptrend renko brick based on the first row of the source candle dataframe.
        """
        close: float        = (float(self.source_candle_df.loc[0, OHLCVUDEnum.CLOSE.value]) // self.__brick_size) * self.__brick_size
        low: float          = float(self.source_candle_df.loc[0, OHLCVUDEnum.LOW.value])
        date: pd.Timestamp  = pd.Timestamp(self.source_candle_df.loc[0, OHLCVUDEnum.DATETIME.value])
        uptrend: bool       = True

        return (date, close - self.__brick_size, close, min(low, close - self.__brick_size), close, uptrend)


    def __calculate_signed_num_of_bricks(
        self,
        curr_close: float,
        prev_close: float
    ) -> int:
        return int((curr_close - prev_close) / self.__brick_size)


    def __generate_next_bricks(
        self,
        curr_date: pd.Timestamp,
        curr_high: float,
        curr_low: float,
        prev_close: float,
        prev_open: float,
        uptrend: bool,
        signed_num_bricks: int
    ) -> list[_RenkoBrickType]:
        
        if uptrend and signed_num_bricks >= 1:
            return self.__continue_uptrend(curr_date, curr_low, prev_close, prev_open, abs(signed_num_bricks))
        elif uptrend and signed_num_bricks <= -2:
            return self.__reverse_to_downtrend(curr_date, curr_high, prev_close, prev_open, abs(signed_num_bricks + 1))
        elif not uptrend and signed_num_bricks <= -1:
            return self.__continue_downtrend(curr_date, curr_high, prev_close, prev_open, abs(signed_num_bricks))
        elif not uptrend and signed_num_bricks >= 2:
            return self.__reverse_to_uptrend(curr_date, curr_low, prev_close, prev_open, abs(signed_num_bricks - 1))
        
        return []


    def __continue_uptrend(
        self,
        curr_date: pd.Timestamp,
        curr_low: float,
        prev_close: float,
        prev_open: float,
        num_bricks: int
    ) -> list[_RenkoBrickType]:
        
        bricks = []
        for _ in range(num_bricks):
            close = prev_close + self.__brick_size
            low = min(max(curr_low, prev_open - self.__brick_size), prev_close)

            brick = (curr_date, prev_close, close, low, close, True)
            bricks.append(brick)
            
            prev_close += self.__brick_size
            prev_open += self.__brick_size
        
        return bricks


    def __reverse_to_downtrend(
        self,
        curr_date: pd.Timestamp,
        curr_high: float,
        prev_close: float,
        prev_open: float,
        num_bricks: int
    ) -> list[_RenkoBrickType]:
        
        bricks = []
        for _ in range(abs(num_bricks)):
            high = max(min(curr_high, prev_close + self.__brick_size), prev_open)
            close = prev_open - self.__brick_size
            
            brick = (curr_date, prev_open, high, close, close, False)
            bricks.append(brick)
            
            prev_close -= self.__brick_size
            prev_open -= self.__brick_size
        
        return bricks


    def __continue_downtrend(
        self,
        curr_date: pd.Timestamp,
        curr_high: float,
        prev_close: float,
        prev_open: float,
        num_bricks: int
    ) -> list[_RenkoBrickType]:
        
        bricks = []
        for _ in range(abs(num_bricks)):
            high = max(min(curr_high, prev_open + self.__brick_size), prev_close)
            close = prev_close - self.__brick_size
            brick = (curr_date, prev_close, high, close, close, False)
            bricks.append(brick)
            prev_close -= self.__brick_size
            prev_open -= self.__brick_size
        
        return bricks


    def __reverse_to_uptrend(
        self,
        curr_date: pd.Timestamp,
        curr_low: float,
        prev_close: float,
        prev_open: float,
        num_bricks: int
    ) -> list[_RenkoBrickType]:
        
        bricks = []
        for _ in range(num_bricks):
            close = prev_open + self.__brick_size
            low = min(max(curr_low, prev_close - self.__brick_size), prev_open)

            brick = (curr_date, prev_open, close, low, close, True)
            bricks.append(brick)
            
            prev_close += self.__brick_size
            prev_open += self.__brick_size
        
        return bricks



    def __raise_if_invalid_instrument(self, instrument_symbol: str) -> None:
        """
        Raises ValueError if the instrument symbol is not valid

        :param instrument_symbol: The instrument symbol to be validated
        :type instrument_symbol: str

        :return: None
        
        :raises ValueError: If the instrument symbol is not valid
        """
        if not self.__DATAFRAMING_CLASS.is_instrument_valid(self.__source_candle_span, instrument_symbol):
            print(f"[ERROR] {self.__class__.__name__} class Initialization Error")
            error_message: str = f"Instrument {instrument_symbol} is invalid"
            raise ValueError(error_message)
        
