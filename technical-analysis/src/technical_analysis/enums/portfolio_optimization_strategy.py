from pprint import pprint
from technical_analysis.portfolio_optimizers._base import Optimizer
from technical_analysis.utils.enum_helpers import EnumWithValuesList


class PortfolioOptimizationStrategy(EnumWithValuesList):
    TOP_PICKS = "TOP_PICKS"
    """
    TOP_PICKS:
    - Start with the best `n` instruments in the universe `(n = number of holdings in the portfolio)`
    - Replaces all `n` holdings, with the so-far best-performing `n` instruments of the universe
    - Replacement happens for every period
    """

    REBALANCING = "REBALANCING"
    """
    REBALANCING:
    - Start with the best `n` instruments in the universe `(n = number of holdings in the portfolio)`
    - Replace `x` worst performing holdings in the portfolio with the `x` so-far best-performing instruments in the universe. `(x = number of replacements)`
    - Replacement happens for every period
    """
    # MEAN_VARIANCE = "MEAN_VARIANCE"
    # RISK_PARITY = "RISK_PARITY"
    # MAX_SHARPE_RATIO = "MAX_SHARPE_RATIO"
    # MIN_VARIANCE = "MIN_VARIANCE"
    # CUSTOM = "CUSTOM"


    @classmethod
    def get_optimizer(cls, strategy: 'PortfolioOptimizationStrategy', config: dict) -> Optimizer:
        """
        Returns the appropriate optimizer based on the strategy.

        :param strategy: The portfolio optimization strategy to use.
        :type strategy: PortfolioOptimizationStrategy
        
        :param config: The configuration for the optimizer.
        :type config: dict
        
        :return: An instance of the appropriate optimizer.
        """
        if strategy == cls.TOP_PICKS:
            from technical_analysis.portfolio_optimizers.top_picks import TopPicksOptimizer, _TopPicksResolvedOptimizerConfig
            print("Creating Default Optimizer with config:")
            pprint(config)
            return TopPicksOptimizer(_TopPicksResolvedOptimizerConfig(**config))

        elif strategy == cls.REBALANCING:
            from technical_analysis.portfolio_optimizers.rebalancing import RebalancingOptimizer, _RebalancingResolvedOptimizerConfig
            print("Creating Rebalancing Optimizer with config:")
            pprint(config)
            return RebalancingOptimizer(_RebalancingResolvedOptimizerConfig(**config))

        raise ValueError(f"Unsupported portfolio optimization strategy: {strategy}")