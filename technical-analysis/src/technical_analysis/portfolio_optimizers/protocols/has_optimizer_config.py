
from typing import Protocol
from technical_analysis.portfolio_optimizers._base import _OptimizerResolvedConfig


class hasOptimizerConfig(Protocol):
    
    @property
    def config(self) -> _OptimizerResolvedConfig: ...
