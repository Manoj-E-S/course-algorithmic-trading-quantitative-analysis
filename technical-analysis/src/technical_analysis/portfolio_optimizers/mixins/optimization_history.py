import pandas as pd
from technical_analysis.portfolio_optimizers.protocols.has_optimizer_config import hasOptimizerConfig
from technical_analysis.utils.decorators import override


class OptimizationHistoryMixin:
    """
    Mixin class to provide optimization history functionality.

    - Provides methods to initialize and append to the optimization history DataFrame.
    - Designed to be used with classes that implement the `hasOptimizerConfig` protocol.

    :Methods (can be overridden if needed):
    - `init_history`: Creates a new history DataFrame and inserts the current holdings DataFrame into it.
    - `append_to_history`: Inserts the current holdings with KPIs into the history DataFrame.
    """

    @override
    def init_history(
        self: hasOptimizerConfig,
        current_holdings_kpis: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Creates new history dataframe and inserts the current holdings dataframe into it

        :param current_holdings_kpis: The current holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        :type current_holdings_kpis: pd.DataFrame

        :return pd.DataFrame: The history of the portfolio, sorted by date. Multi-Index - (date, symbol), columns - KPIs.
        """
        return (
            pd.DataFrame(
                data=current_holdings_kpis.values,
                index=pd.MultiIndex.from_product(
                    [[self.config.end_date], current_holdings_kpis.index],
                    names=['date', 'symbol']
                ),
                columns=current_holdings_kpis.columns
            )
        )
    

    @override
    def append_to_history(
        self: hasOptimizerConfig,
        history: pd.DataFrame,
        current_holdings_kpis: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Inserts the current holdings with KPIs into the history DataFrame.

        :param history: The historical holdings with their KPIs as a DataFrame. Index is (date, symbol), and the columns are the KPI values.
        :type history: pd.DataFrame

        :param current_holdings_kpis: The current holdings with their KPIs as a DataFrame. Index is the instrument symbol, and the columns are the KPI values.
        :type current_holdings_kpis: pd.DataFrame

        :return pd.DataFrame: The updated history of the portfolio, sorted by date. Multi-Index - (date, symbol), columns - KPIs.
        """
        current_holdings_kpis_with_date = current_holdings_kpis.copy()
        current_holdings_kpis_with_date.index = pd.MultiIndex.from_product(
            [[self.config.end_date], current_holdings_kpis_with_date.index],
            names=["date", "symbol"]
        )

        if self.config.end_date in history.index.get_level_values("date"):
            history.drop(index=self.config.end_date, level="date", inplace=True)

        return pd.concat([history, current_holdings_kpis_with_date])
