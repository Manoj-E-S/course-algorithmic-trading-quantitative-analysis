from typing import Protocol
import pandas as pd

class supportsOptimizationSteps(Protocol):
    
    def update_current_holdings_kpis(self, current_holdings_kpis: pd.DataFrame) -> pd.DataFrame: ...
    
    def append_to_history(self, history: pd.DataFrame, current_holdings_kpis: pd.DataFrame) -> pd.DataFrame: ...