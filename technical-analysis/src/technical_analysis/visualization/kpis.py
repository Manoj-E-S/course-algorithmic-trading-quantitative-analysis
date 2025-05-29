import pandas as pd
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.kpis.kpi_calculator import KpiCalculator
from technical_analysis.models.candlesticks import Candlesticks
from technical_analysis.models.instrument import Instrument
from technical_analysis.models.renko import Renko


class InstrumentKPIs:
    """
    A class to represent key performance indicators (KPIs) for a financial instrument.
    """

    def __init__(
        self,
        source_instrument: Instrument
    ):
        if not isinstance(source_instrument, Instrument):
            raise TypeError("source_instrument must be an instance of Instrument or its subclasses.")
        
        self.__instrument: Instrument = source_instrument

        if isinstance(self.__instrument, Candlesticks):
            self.__df: pd.DataFrame = self.__instrument.get_candlesticks()
            self.__instrument_type: str = Candlesticks.__name__
        elif isinstance(self.__instrument, Renko):
            self.__df: pd.DataFrame = self.__instrument.get_renko()
            self.__instrument_type: str = Renko.__name__
        else:
            raise TypeError("InstrumentKPIs support is currently limited to Candlesticks and Renko.")
    

    # Getters
    @property
    def instrument(self) -> Instrument:
        return self.__instrument


    # Chainable Setters   
    @instrument.setter
    def instrument(self, instrument: Instrument) -> 'InstrumentKPIs':
        self.__instrument = instrument
        return self
    

    # Public methods
    def cagr(self) -> float:
        """
        Calculate the Compound Annual Growth Rate (CAGR) of the instrument.
        
        Returns:
            float: The CAGR value.
        """
        if self.__df.empty:
            return 0.0

        start_date_idx: int = 0
        end_date_idx: int = -1
        periods: float = self.__get_years_between_date_indices(start_date_idx, end_date_idx)

        return KpiCalculator.cagr(
            start_value=self.__df[OHLCVUDEnum.CLOSE.value].iloc[start_date_idx],
            end_value=self.__df[OHLCVUDEnum.CLOSE.value].iloc[end_date_idx],
            periods=periods
        )
    

    # Private methods
    def __get_years_between_date_indices(self, start_date_idx: int = 0, end_date_idx: int = -1) -> float:
        """
        Calculate the number of periods based on the instrument type and candle span.
        Returns:
            float : The number of periods between the first and last data points of corresponding instrument.

        Raises:
            ValueError: If the candle span is unsupported for the instrument type.
            TypeError: If the instrument type is unsupported.
        """
        
        if self.__instrument_type == Candlesticks.__name__:
            start_date: pd.Timestamp = self.__df.index[start_date_idx]
            end_date: pd.Timestamp = self.__df.index[end_date_idx]
        elif self.__instrument_type == Renko.__name__:
            start_date: pd.Timestamp = self.__df[OHLCVUDEnum.DATETIME.value][start_date_idx]
            end_date: pd.Timestamp = self.__df[OHLCVUDEnum.DATETIME.value][end_date_idx]
        else:
            raise TypeError("InstrumentKPIs support is currently limited to Candlesticks and Renko.")

        if self.instrument.candle_span == CandlespanEnum.DAILY.value:
            return (end_date - start_date).days / 252
        elif self.instrument.candle_span == CandlespanEnum.WEEKLY.value:
            return (end_date - start_date).days / 52
        elif self.instrument.candle_span == CandlespanEnum.MONTHLY.value:
            return (end_date - start_date).days / 12
        else:
            err: str = f"Unsupported candle span: {self.instrument.candle_span}. Suppported candle spans are: {CandlespanEnum.values()}"
            raise ValueError(err)
