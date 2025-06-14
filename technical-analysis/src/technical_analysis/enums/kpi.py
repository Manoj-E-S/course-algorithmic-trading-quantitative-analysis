from technical_analysis.utils.enum_helpers import EnumWithValuesList

class _KpiStrings:
    CAGR = "CAGR"
    MAX_DRAWDOWN = "MAX_DRAWDOWN"
    CALMAR_RATIO = "CALMAR_RATIO"
    SHARPE_RATIO = "SHARPE_RATIO"
    SORTINO_RATIO = "SORTINO_RATIO"
    VOLATILITY = "VOLATILITY"
    ANNUALIZED_VOLATILITY = "ANNUALIZED_VOLATILITY"
    ANNUALIZED_DOWNSIDE_VOLATILITY = "ANNUALIZED_DOWNSIDE_VOLATILITY"


class KpiEnum:
    class ForInstrumentKPI(EnumWithValuesList):
        CAGR                    = _KpiStrings.CAGR
        MAX_DRAWDOWN            = _KpiStrings.MAX_DRAWDOWN
        CALMAR_RATIO            = _KpiStrings.CALMAR_RATIO
        SHARPE_RATIO            = _KpiStrings.SHARPE_RATIO
        SORTINO_RATIO           = _KpiStrings.SORTINO_RATIO
        ANNUALIZED_VOLATILITY   = _KpiStrings.ANNUALIZED_VOLATILITY

    class AllKPIs(EnumWithValuesList):
        CAGR                            = _KpiStrings.CAGR
        MAX_DRAWDOWN                    = _KpiStrings.MAX_DRAWDOWN
        CALMAR_RATIO                    = _KpiStrings.CALMAR_RATIO
        SHARPE_RATIO                    = _KpiStrings.SHARPE_RATIO
        SORTINO_RATIO                   = _KpiStrings.SORTINO_RATIO
        VOLATILITY                      = _KpiStrings.VOLATILITY
        ANNUALIZED_VOLATILITY           = _KpiStrings.ANNUALIZED_VOLATILITY
        ANNUALIZED_DOWNSIDE_VOLATILITY  = _KpiStrings.ANNUALIZED_DOWNSIDE_VOLATILITY
