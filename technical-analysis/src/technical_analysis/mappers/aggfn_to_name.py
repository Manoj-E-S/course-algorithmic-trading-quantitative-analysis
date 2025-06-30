from technical_analysis.enums.agg_fn import AggregatorFunctionEnum


class AggFnToName:
    Mapper = {
        AggregatorFunctionEnum.MEAN_FN           : "MEAN",
        AggregatorFunctionEnum.MEAN_OF_FINITES_FN: "MEAN_OF_FINITES",
        AggregatorFunctionEnum.MAX_FN            : "MAX"
    }
