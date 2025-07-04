
from typing import Generator, Protocol
import pandas as pd
from technical_analysis.portfolio_optimizers.protocols.has_optimizer_config import hasOptimizerConfig
from technical_analysis.portfolio_optimizers.protocols.supports_optimization_steps import supportsOptimizationSteps


class supportsOptimization(hasOptimizerConfig, supportsOptimizationSteps, Protocol):
    
    def _step_optimize_precomputed_mode(
        self,
        current_holdings_kpis: pd.DataFrame,
        history: pd.DataFrame,
    ) -> Generator[tuple[pd.Timestamp, pd.DataFrame, pd.DataFrame], None, None]:
        ...

    def _step_optimize_incremental_mode(
        self,
        current_holdings_kpis: pd.DataFrame,
        history: pd.DataFrame,
    ) -> Generator[tuple[pd.Timestamp, pd.DataFrame, pd.DataFrame], None, None]:
        ...