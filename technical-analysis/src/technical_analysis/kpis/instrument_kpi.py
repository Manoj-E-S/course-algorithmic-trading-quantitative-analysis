from functools import cached_property
import pandas as pd

from technical_analysis.kpis.calculators.dataframe_enhanced_kpi_calculator import DataFrameEnhancedKPICalculator
from technical_analysis.models.instrument import Instrument


class InstrumentKPI:
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
        self.__after_property_update()
    

    # Getters
    @property
    def instrument(self) -> Instrument:
        return self.__instrument


    # Chainable Setters   
    @instrument.setter
    def instrument(self, instrument: Instrument) -> 'InstrumentKPI':
        self.__instrument = instrument
        self.__after_property_update()
        return self
    

    # Cached callable properties
    @cached_property
    def cached_CAGR(self) -> float:
        return DataFrameEnhancedKPICalculator.cagr_from_df(
            self.__instrument.ohlcv_df,
            from_date=None,
            until_date=None
        )


    @cached_property
    def cached_MAX_DRAWDOWN(self) -> float:
        return DataFrameEnhancedKPICalculator.max_drawdown_from_df(
            self.__instrument.cumulative_returns_series,
            from_date=None,
            until_date=None
        )


    @cached_property
    def cached_CALAMAR_RATIO(self) -> float:
        return DataFrameEnhancedKPICalculator.calamar_ratio(
            annual_return=self.cached_CAGR,
            max_drawdown=self.cached_MAX_DRAWDOWN,
        )


    # Public methods
    def cagr(self, from_date: pd.Timestamp | None = None, until_date: pd.Timestamp | None = None) -> float:
        """
        Calculate the Compound Annual Growth Rate (CAGR) of the instrument.

        :param from_date: The date from which to calculate the CAGR. If None, uses the earliest date
        :type from_date: pd.Timestamp | None

        :param until_date: The date until which to calculate the CAGR.
        :type until_date: pd.Timestamp | None

        :return: The CAGR as a float.
        """
        if until_date is None and from_date is None:
            return self.cached_CAGR

        return DataFrameEnhancedKPICalculator.cagr_from_df(
            self.__instrument.ohlcv_df,
            from_date=from_date,
            until_date=until_date
        )


    def max_drawdown(self, from_date: pd.Timestamp | None = None, until_date: pd.Timestamp | None = None) -> float:
        """
        Calculate the maximum drawdown of the instrument.

        :param from_date: The date from which to calculate the maximum drawdown. If None, uses the earliest date.
        :type from_date: pd.Timestamp | None

        :param until_date: The date until which to calculate the maximum drawdown. If None, uses the latest date.
        :type until_date: pd.Timestamp | None
        
        :return: The maximum drawdown as a float.
        """
        if until_date is None and from_date is None:
            return self.cached_MAX_DRAWDOWN

        return DataFrameEnhancedKPICalculator.max_drawdown_from_df(
            self.__instrument.cumulative_returns_series,
            from_date=from_date,
            until_date=until_date
        )


    def calamar_ratio(self, from_date: pd.Timestamp | None = None, until_date: pd.Timestamp | None = None) -> float:
        """
        Calculate the Calmar Ratio of the instrument.

        :param from_date: The date from which to calculate the Calmar Ratio. If None, uses the earliest date.
        :type from_date: pd.Timestamp | None

        :param until_date: The date until which to calculate the Calmar Ratio. If None, uses the latest date.
        :type until_date: pd.Timestamp | None
        
        :return: The Calmar Ratio as a float.
        """
        if until_date is None and from_date is None:
            return self.cached_CALAMAR_RATIO

        return DataFrameEnhancedKPICalculator.calamar_ratio(
            annual_return=self.cagr(
                from_date=from_date,
                until_date=until_date
            ),
            max_drawdown=self.max_drawdown(
                from_date=from_date,
                until_date=until_date
            )
        )


    def annualized_volatility(self, from_date: pd.Timestamp | None = None, until_date: pd.Timestamp | None = None, downside: bool = False) -> float:
        """
        Calculate the annualized volatility of the instrument.

        :param from_date: The date from which to calculate the annualized volatility. If None, uses the earliest date.
        :type from_date: pd.Timestamp | None

        :param until_date: The date until which to calculate the annualized volatility. If None, uses the latest date.
        :type until_date: pd.Timestamp | None

        :param downside: If True, calculate downside volatility; otherwise, calculate total volatility.
        :type downside: bool
        
        :return: The annualized volatility as a float.
        :rtype: float
        """
        return DataFrameEnhancedKPICalculator.annualized_volatility_from_df(
            returns_series=self.__instrument.returns_series,
            row_span=self.__instrument.candle_span,
            from_date=from_date,
            until_date=until_date,
            downside=downside
        )
    

    def sharpe_ratio(self, risk_free_rate: float, from_date: pd.Timestamp | None = None, until_date: pd.Timestamp | None = None) -> float:
        """
        Calculate the Sharpe Ratio of the instrument.

        :param risk_free_rate: The risk-free rate to be used in the calculation.
        :type risk_free_rate: float

        :param from_date: The date from which to calculate the Sharpe Ratio. If None, uses the earliest date.
        :type from_date: pd.Timestamp | None

        :param until_date: The date until which to calculate the Sharpe Ratio. If None, uses the latest date.
        :type until_date: pd.Timestamp | None
        
        :return: The Sharpe Ratio as a float.
        :rtype: float
        """
        return DataFrameEnhancedKPICalculator.sharpe_ratio(
            risk_free_rate = risk_free_rate,
            expected_returns = self.cagr(
                from_date=from_date,
                until_date=until_date
            ),
            volatility = self.annualized_volatility(
                from_date=from_date,
                until_date=until_date,
                downside=False
            )
        )
    

    def sortino_ratio(self, risk_free_rate: float, from_date: pd.Timestamp | None = None, until_date: pd.Timestamp | None = None) -> float:
        """
        Calculate the Sortino Ratio of the instrument.
        
        :param risk_free_rate: The risk-free rate to be used in the calculation.
        :type risk_free_rate: float

        :param from_date: The date from which to calculate the Sortino Ratio. If None, uses the earliest date.
        :type from_date: pd.Timestamp | None

        :param until_date: The date until which to calculate the Sortino Ratio. If None, uses the latest date.
        :type until_date: pd.Timestamp | None
        
        :return: The Sortino Ratio as a float.
        :rtype: float
        """
        return DataFrameEnhancedKPICalculator.sortino_ratio(
            risk_free_rate=risk_free_rate,
            expected_returns=self.cagr(
                from_date=from_date,
                until_date=until_date
            ),
            downside_volatility=self.annualized_volatility(
                from_date=from_date,
                until_date=until_date,
                downside=True
            )
        )


    # Private methods
    def __after_property_update(self) -> None:
        """
        This method is called after any property update to invalidate cached properties, and perform any other actions needed.
        """
        self.__instrument_type = type(self.__instrument).__name__
        self.__invalidate_cached_properties()


    def __invalidate_cached_properties(self) -> None:
        """
        Invalidate cached properties.
        """
        for attr in dir(self):
            if isinstance(getattr(self, attr), cached_property):
                delattr(self, attr)