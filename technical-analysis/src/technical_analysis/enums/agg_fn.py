import numpy as np
from technical_analysis.utils.enum_helpers import EnumWithValuesList


class AggregatorFunctionEnum(EnumWithValuesList):
    MEAN_FN             = lambda x: x.mean() if not x.empty else np.nan
    MEAN_OF_FINITES_FN  = lambda x: x[(x != np.inf) & (x != -np.inf)].mean() if not x.empty else np.nan
    MAX_FN              = lambda x: x.max() if not x.empty else np.nan