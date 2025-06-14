from typing import Any, Generator
import pandas as pd

from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.kpi import KpiEnum
from technical_analysis.kpis.instrument_kpi import InstrumentKPI
from technical_analysis.mappers.kpi_to_method import KpiToMethod
from technical_analysis.models.instrument_group import InstrumentGroup
from technical_analysis.providers.data_view import DataViewProvider


class InstrumentUniverse(InstrumentGroup):
    """
    A class that represents a universe of financial instruments.
    This class is a specialized version of InstrumentGroup, designed to manage a collection of instruments.
    """

    def __init__(
        self,
        instrument_symbols: list[str],
        candle_span: CandlespanEnum,
        data_view_provider: DataViewProvider | None = None
    ):
        super().__init__(instrument_symbols, candle_span, data_view_provider)

    
    def sorted_instruments_by_kpi(
        self,
        sort_kpi: KpiEnum.ForInstrumentKPI,
        ascending: bool = True,
        metric_kpi: KpiEnum.ForInstrumentKPI | None = None,
        kwargs_for_sort_kpi: dict[str, Any] | None = None,
        kwargs_for_metric_kpi: dict[str, Any] | None = None,
    ) -> pd.Series:
        """
        Sorts the instruments in the universe by a specified KPI.

        :param sort_kpi: The KPI to sort by (e.g., 'CAGR', 'ANNUALIZED_VOLATILITY').
        :type sort_kpi: KpiEnum.ForInstrumentKPI

        :param ascending: Whether to sort in ascending order. Defaults to True.
        :type ascending: bool
        
        :param metric_kpi: The KPI to be calculated for each instrument. If None, uses the KPI specified in `sort_kpi`.
        :type metric_kpi: KpiEnum.ForInstrumentKPI | None

        :param kwargs_for_sort_kpi: Additional keyword arguments for the KPI calculation for sorting.
        :type kwargs_for_sort_kpi: dict[str, Any] | None

        :param kwargs_for_metric_kpi: Additional keyword arguments for the KPI calculation for the metric KPI.
        :type kwargs_for_metric_kpi: dict[str, Any] | None

        Available keys for kpi kwargs are:
        - `risk_free_rate (float)`          : [Required][Sharpe Ratio,Sortino Ratio] The risk-free rate to be used in the calculation for KPIs that require it.
        - `downside (bool)`                 : [Optional][Volatility] Whether to calculate downside volatility for the 'volatility' KPI.
        - `from_date (pd.Timestamp)`    : [Optional][All] The date from which to consider the instruments.
        - `until_date (pd.Timestamp)`   : [Optional][All] The date until which to consider the instruments.

        :return: A pandas Series containing the top/bottom N instruments sorted by the specified KPI, indexed by instrument symbol.
        :rtype: pd.Series

        :raises ValueError: If the KPI is not supported or if the required parameters are not provided.
        """
        if metric_kpi is None:
            metric_kpi = sort_kpi

        if metric_kpi not in KpiToMethod.ForInstrumentKPI:
            raise ValueError(f"KPI '{metric_kpi}' is not supported. Supported KPIs are: {list(KpiToMethod.ForInstrumentKPI.keys())}")
        kwargs_for_metric_kpi = self.__get_validated_kwargs_for_kpi(metric_kpi, kwargs_for_metric_kpi)
        

        if sort_kpi not in KpiToMethod.ForInstrumentKPI:
            raise ValueError(f"KPI '{sort_kpi}' is not supported for sorting. Supported KPIs are: {list(KpiToMethod.ForInstrumentKPI.keys())}")
        kwargs_for_sort_kpi = self.__get_validated_kwargs_for_kpi(sort_kpi, kwargs_for_sort_kpi)


        indices, data, _ = \
            zip(
                *sorted(
                    # Generator expression to lazily compute KPI values and save on memory
                    (
                        (
                            instrument.instrument_symbol,
                            KpiToMethod.ForInstrumentKPI[metric_kpi].__get__(InstrumentKPI(instrument))(**kwargs_for_metric_kpi),
                            KpiToMethod.ForInstrumentKPI[sort_kpi].__get__(InstrumentKPI(instrument))(**kwargs_for_sort_kpi)
                        )
                        for instrument in self.as_instruments().values()
                    ),
                    key=lambda x: x[2],
                    reverse=not ascending
                )
            )
        
        return pd.Series(data, index=indices, dtype='float64', name=metric_kpi.value)


    def n_sorted_instruments_by_kpi(
        self,
        sort_kpi: KpiEnum.ForInstrumentKPI,
        n: int,
        ascending: bool = True,
        metric_kpi: KpiEnum.ForInstrumentKPI | None = None,
        kwargs_for_sort_kpi: dict[str, Any] | None = None,
        kwargs_for_metric_kpi: dict[str, Any] | None = None,
    ) -> pd.Series:
        """
        Returns the N top/bottom instruments sorted by the specified KPI. (Uses `heapq.nlargest` or `heapq.nsmallest` for efficiency)

        :param sort_kpi: The KPI to sort by.
        :type sort_kpi: KpiEnum.ForInstrumentKPI

        :param n: The number of top instruments to return.
        :type n: int

        :param ascending: Whether to sort in ascending order (Note: Provide based on `sort_kpi`). Defaults to True.
        :type ascending: bool
        
        :param metric_kpi: The KPI to be calculated for each instrument. If None, uses the KPI specified in `sort_kpi`.
        :type metric_kpi: KpiEnum.ForInstrumentKPI | None

        :param kwargs_for_sort_kpi: Additional keyword arguments for the KPI calculation for sorting.
        :type kwargs_for_sort_kpi: dict[str, Any] | None

        :param kwargs_for_metric_kpi: Additional keyword arguments for the KPI calculation for the metric KPI.
        :type kwargs_for_metric_kpi: dict[str, Any] | None

        Available keys for kpi kwargs are:
        - `risk_free_rate (float)`          : [Required][Sharpe Ratio,Sortino Ratio] The risk-free rate to be used in the calculation for KPIs that require it.
        - `downside (bool)`                 : [Optional][Volatility] Whether to calculate downside volatility for the 'volatility' KPI.
        - `from_date (pd.Timestamp)`    : [Optional][All] The date from which to consider the instruments.
        - `until_date (pd.Timestamp)`   : [Optional][All] The date until which to consider the instruments.

        :return: A pandas Series containing the top/bottom N instruments sorted by the specified KPI, indexed by instrument symbol.
        :rtype: pd.Series

        :raises ValueError: If the KPI is not supported or if the required parameters are not provided.
        """
        if metric_kpi is None:
            metric_kpi = sort_kpi

        if metric_kpi not in KpiToMethod.ForInstrumentKPI:
            raise ValueError(f"KPI '{metric_kpi}' is not supported. Supported KPIs are: {list(KpiToMethod.ForInstrumentKPI.keys())}")
        kwargs_for_metric_kpi = self.__get_validated_kwargs_for_kpi(metric_kpi, kwargs_for_metric_kpi)
        

        if sort_kpi not in KpiToMethod.ForInstrumentKPI:
            raise ValueError(f"KPI '{sort_kpi}' is not supported for sorting. Supported KPIs are: {list(KpiToMethod.ForInstrumentKPI.keys())}")
        kwargs_for_sort_kpi = self.__get_validated_kwargs_for_kpi(sort_kpi, kwargs_for_sort_kpi)

        # Generator expression to lazily compute KPI values
        instrument_kpi_iterable: Generator[tuple[str, float, float], None, None] = (
            (
                instrument.instrument_symbol,
                KpiToMethod.ForInstrumentKPI[metric_kpi].__get__(InstrumentKPI(instrument))(**kwargs_for_metric_kpi),
                KpiToMethod.ForInstrumentKPI[sort_kpi].__get__(InstrumentKPI(instrument))(**kwargs_for_sort_kpi)
            )
            for instrument in self.as_instruments().values()
        )

        import heapq
        n_instruments_and_kpis = \
            heapq.nsmallest(n, instrument_kpi_iterable, key=lambda x: x[2]) if ascending \
            else heapq.nlargest(n, instrument_kpi_iterable, key=lambda x: x[2])
        
        indices, data, _ = zip(*n_instruments_and_kpis)
        return pd.Series(data, index=indices, dtype='float64', name=metric_kpi.value)


    # Private methods
    def __get_validated_kwargs_for_kpi(
        self,
        kpi: KpiEnum.ForInstrumentKPI,
        kwargs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Validates the keyword arguments for the specified KPI.
        
        :param kpi: The KPI for which to validate the keyword arguments.
        :type kpi: KpiEnum.ForInstrumentKPI
        
        :param kwargs: The keyword arguments to validate.
        :type kwargs: dict[str, Any]
        
        :raises ValueError: If the keyword arguments are not valid for the specified KPI.
        
        :return: A dictionary of keyword arguments with defaults for optionals.
        :rtype: dict[str, Any]
        """
        kwargs_with_defaults = {
            # Optional parameters with defaults or passed values
            'from_date': kwargs.get('from_date', None),
            'until_date': kwargs.get('until_date', None),
            # ... other parameters will be added subsequently
        }

        # cagr, max_drawdown, calmar_ratio --> [None]
        if kpi in [KpiEnum.ForInstrumentKPI.CAGR, KpiEnum.ForInstrumentKPI.MAX_DRAWDOWN, KpiEnum.ForInstrumentKPI.CALMAR_RATIO]:
            if kwargs.get('risk_free_rate', None) is not None:
                raise ValueError(f"KPI '{kpi}' does not require a risk-free rate.")
            if kwargs.get('downside', None) is not None:
                raise ValueError(f"KPI '{kpi}' does not require downside volatility.")
            

        # sharpe_ratio, sortino_ratio --> [Required] risk-free rate
        elif kpi in [KpiEnum.ForInstrumentKPI.SHARPE_RATIO, KpiEnum.ForInstrumentKPI.SORTINO_RATIO]:
            if kwargs.get('downside', None) is not None:
                raise ValueError(f"KPI '{kpi}' does not require downside volatility.")
            if kwargs.get('risk_free_rate', None) is None:
                raise ValueError(f"KPI '{kpi}' requires a risk-free rate to be specified.")
            
            kwargs_with_defaults['risk_free_rate'] = kwargs.get('risk_free_rate')


        # annualized_volatility --> [Optional] use_downside_volatility
        elif kpi == KpiEnum.ForInstrumentKPI.ANNUALIZED_VOLATILITY:
            if kwargs.get('risk_free_rate', None) is not None:
                raise ValueError("Annualized Volatility does not require a risk-free rate.")

            kwargs_with_defaults['downside'] = kwargs.get('downside', False)

        return kwargs_with_defaults
