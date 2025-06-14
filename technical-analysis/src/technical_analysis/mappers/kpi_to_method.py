from typing import Callable

from technical_analysis.enums.kpi import KpiEnum
from technical_analysis.kpis.instrument_kpi import InstrumentKPI


class KpiToMethod:
    ForInstrumentKPI: dict[KpiEnum.ForInstrumentKPI, Callable[..., float]] = \
        {
            KpiEnum.ForInstrumentKPI.CAGR                    : InstrumentKPI.cagr,
            KpiEnum.ForInstrumentKPI.MAX_DRAWDOWN            : InstrumentKPI.max_drawdown,
            KpiEnum.ForInstrumentKPI.CALMAR_RATIO            : InstrumentKPI.calmar_ratio,
            KpiEnum.ForInstrumentKPI.SHARPE_RATIO            : InstrumentKPI.sharpe_ratio,
            KpiEnum.ForInstrumentKPI.SORTINO_RATIO           : InstrumentKPI.sortino_ratio,
            KpiEnum.ForInstrumentKPI.ANNUALIZED_VOLATILITY   : InstrumentKPI.annualized_volatility
        }
