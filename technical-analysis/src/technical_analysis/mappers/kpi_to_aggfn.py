from technical_analysis.enums.agg_fn import AggregatorFunctionEnum
from technical_analysis.enums.kpi import KPIEnum


class KPIToAggFn:
    Mapper = {
        KPIEnum.CAGR                          : AggregatorFunctionEnum.MEAN_FN,
        KPIEnum.MAX_DRAWDOWN                  : AggregatorFunctionEnum.MAX_FN,
        KPIEnum.CALAMAR_RATIO                 : AggregatorFunctionEnum.MEAN_OF_FINITES_FN,
        KPIEnum.SHARPE_RATIO                  : AggregatorFunctionEnum.MEAN_FN,
        KPIEnum.SORTINO_RATIO                 : AggregatorFunctionEnum.MEAN_OF_FINITES_FN,
        KPIEnum.ANNUALIZED_VOLATILITY         : AggregatorFunctionEnum.MEAN_FN,
        KPIEnum.ANNUALIZED_DOWNSIDE_VOLATILITY: AggregatorFunctionEnum.MEAN_FN
    }