import matplotlib.pyplot as plt


from technical_analysis.kpis.instrument_kpi import InstrumentKPI
from technical_analysis.models.instrument_group import InstrumentGroup


class InstrumentGroupKpiPlotter:
    """
    A class to plot KPIs for a group of financial instruments.
    """

    def __init__(self, instrument_group: InstrumentGroup):
        self.__instrument_group: InstrumentGroup = instrument_group
        self.__reset_instrument_kpi()



    # Getters
    @property
    def instrument_group(self) -> InstrumentGroup:
        return self.__instrument_group
    

    # Chainable Setters
    @instrument_group.setter
    def instrument_group(self, instrument_group: InstrumentGroup) -> 'InstrumentGroupKpiPlotter':
        self.__instrument_group = instrument_group
        self.__reset_instrument_kpi()
        return self
    

    # Public Methods
    def plot_cagrs(
        self,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plots the Compound Annual Growth Rate (CAGR) for all instruments in the group.

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        """
        plt.style.use(styling)

        cagr_values = {symbol: kpi.cagr() for symbol, kpi in self.__instrument_kpi.items()}
        
        fig: plt.Figure = plt.figure(figsize=(10, 6))
        ax: plt.Axes = fig.add_subplot(111)

        ax.bar(cagr_values.keys(), cagr_values.values(), width=0.4)
        ax.set_title(title or "CAGR of Instruments")
        ax.set_ylabel("CAGR")
        ax.set_xlabel("Instruments")
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    
    def plot_volatilities(
        self,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plots the volatility for all instruments in the group.

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        """
        plt.style.use(styling)

        volatility_values = {symbol: kpi.annualized_volatility() for symbol, kpi in self.__instrument_kpi.items()}
        
        fig: plt.Figure = plt.figure(figsize=(10, 6))
        ax: plt.Axes = fig.add_subplot(111)

        ax.bar(volatility_values.keys(), volatility_values.values(), width=0.4)
        ax.set_title(title or "Volatility of Instruments")
        ax.set_ylabel("Standard Deviation of Returns")
        ax.set_xlabel("Instruments")
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    
    def plot_cagr_vs_volatility(
        self,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plots CAGR against volatility for all instruments in the group.

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        """
        plt.style.use(styling)
        
        cagr_values = [kpi.cagr() for kpi in self.__instrument_kpi.values()]
        volatility_values = [kpi.annualized_volatility() for kpi in self.__instrument_kpi.values()]

        fig: plt.Figure = plt.figure(figsize=(10, 6))
        ax: plt.Axes = fig.add_subplot(111)

        ax.scatter(volatility_values, cagr_values)
        ax.set_title(title or "CAGR vs Volatility of Instruments")
        ax.set_xlabel("Volatility (Standard Deviation of Returns)")
        ax.set_ylabel("CAGR")

        for symbol, kpi in self.__instrument_kpi.items():
            ax.annotate(symbol, (kpi.annualized_volatility(), kpi.cagr()), fontsize=8)

        ax.grid(True)
        plt.tight_layout()
        plt.show()


    def plot_sharpe_ratios(
        self,
        risk_free_rate: float = 0.06,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plots the Sharpe Ratio for all instruments in the group.

        :param risk_free_rate: The risk-free rate to be used in the calculation of Sharpe Ratio. Default is 0.06.
        :type risk_free_rate: float

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        """
        plt.style.use(styling)

        sharpe_ratios = {symbol: kpi.sharpe_ratio(risk_free_rate) for symbol, kpi in self.__instrument_kpi.items()}

        fig: plt.Figure = plt.figure(figsize=(10, 6))
        ax: plt.Axes = fig.add_subplot(111)

        ax.bar(sharpe_ratios.keys(), sharpe_ratios.values(), width=0.4)
        ax.set_title(title or "Sharpe Ratio of Instruments")
        ax.set_ylabel("Sharpe Ratio")
        ax.set_xlabel("Instruments")
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    
    def plot_sortino_ratios(
        self,
        risk_free_rate: float = 0.06,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plots the Sortino Ratio for all instruments in the group.

        :param risk_free_rate: The risk-free rate to be used in the calculation of Sortino Ratio. Default is 0.06.
        :type risk_free_rate: float

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        """
        plt.style.use(styling)

        sortino_ratios = {symbol: kpi.sortino_ratio(risk_free_rate) for symbol, kpi in self.__instrument_kpi.items()}

        fig: plt.Figure = plt.figure(figsize=(10, 6))
        ax: plt.Axes = fig.add_subplot(111)

        ax.bar(sortino_ratios.keys(), sortino_ratios.values(), width=0.4)
        ax.set_title(title or "Sortino Ratio of Instruments")
        ax.set_ylabel("Sortino Ratio")
        ax.set_xlabel("Instruments")
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    
    def plot_max_drawdowns(
        self,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plots the maximum drawdown for all instruments in the group.

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        """
        plt.style.use(styling)
        
        max_drawdowns = {symbol: kpi.max_drawdown() for symbol, kpi in self.__instrument_kpi.items()}

        fig: plt.Figure = plt.figure(figsize=(10, 6))
        ax: plt.Axes = fig.add_subplot(111)

        ax.bar(max_drawdowns.keys(), max_drawdowns.values(), width=0.4)
        ax.set_title(title or "Maximum Drawdown of Instruments")
        ax.set_ylabel("Maximum Drawdown")
        ax.set_xlabel("Instruments")
        ax.grid(True)
        plt.tight_layout()
        plt.show()


    def plot_calmar_ratios(
        self,
        title: str | None = None,
        styling: str = 'ggplot'
    ) -> None:
        """
        Plots the Calmar Ratio for all instruments in the group.

        :param title: The title of the plot.
        :type title: str | None

        :param styling: The styling of the plot. Default is 'ggplot'.
        :type styling: str
        """
        plt.style.use(styling)
        
        calmar_ratios = {symbol: kpi.calmar_ratio() for symbol, kpi in self.__instrument_kpi.items()}

        fig: plt.Figure = plt.figure(figsize=(10, 6))
        ax: plt.Axes = fig.add_subplot(111)

        ax.bar(calmar_ratios.keys(), calmar_ratios.values(), width=0.4)
        ax.set_title(title or "Calmar Ratio of Instruments")
        ax.set_ylabel("Calmar Ratio")
        ax.set_xlabel("Instruments")
        ax.grid(True)
        plt.tight_layout()
        plt.show()
    

    # Private Methods
    def __reset_instrument_kpi(self) -> None:
        """
        Updates the instrument KPIs for the current instrument group.
        """
        self.__instrument_kpi: dict[str, InstrumentKPI] = {}
        for symbol, instrument in self.__instrument_group.as_instruments().items():
            self.__instrument_kpi[symbol] = InstrumentKPI(instrument)