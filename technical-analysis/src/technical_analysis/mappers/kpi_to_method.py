from typing import Callable

import pandas as pd
from technical_analysis.enums.kpi import KPIEnum
from technical_analysis.kpis.calculators.rolling_kpi_calculator import RollingKPICalculator
from technical_analysis.kpis.instrument_kpi import InstrumentKPI


class KPIToMethod:
    ForInstrumentKPI: dict[KPIEnum, Callable[..., float]] = \
        {
            KPIEnum.CAGR                    : InstrumentKPI.cagr,
            KPIEnum.MAX_DRAWDOWN            : InstrumentKPI.max_drawdown,
            KPIEnum.CALAMAR_RATIO            : InstrumentKPI.calamar_ratio,
            KPIEnum.SHARPE_RATIO            : InstrumentKPI.sharpe_ratio,
            KPIEnum.SORTINO_RATIO           : InstrumentKPI.sortino_ratio,
            KPIEnum.ANNUALIZED_VOLATILITY   : InstrumentKPI.annualized_volatility
        }

    ForRollingKPICalculator: dict[KPIEnum, Callable[..., pd.DataFrame]] = \
        {
            KPIEnum.CAGR                    : RollingKPICalculator.cumulative_cagrs,
            KPIEnum.MAX_DRAWDOWN            : RollingKPICalculator.cumulative_max_drawdowns,
            KPIEnum.CALAMAR_RATIO            : RollingKPICalculator.cumulative_calamar_ratios,
            KPIEnum.SHARPE_RATIO            : RollingKPICalculator.cumulative_sharpe_ratios,
            KPIEnum.SORTINO_RATIO           : RollingKPICalculator.cumulative_sortino_ratios,
            KPIEnum.ANNUALIZED_VOLATILITY   : RollingKPICalculator.cumulative_annualized_volatilities,
            KPIEnum.ANNUALIZED_DOWNSIDE_VOLATILITY   : RollingKPICalculator.cumulative_annualized_downside_volatilities
        }
