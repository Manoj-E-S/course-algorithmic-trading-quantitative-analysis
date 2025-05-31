import pandas as pd


class KpiCalculator:
    """
    A class to calculate various KPIs for the trading strategy.
    """

    def __init__(self):
        pass


    @staticmethod
    def cagr(start_price: float, end_price: float, periods: float) -> float:
        """
        Calculate the Compound Annual Growth Rate (CAGR).

        :param start_price: The initial price of the investment.
        :type start_price: float

        :param end_price: The final price of the investment.
        :type end_price: float

        :param periods: The number of periods (years) over which the growth is calculated.
        :type periods: float

        :return: The CAGR as a fraction.
        :rtype: float

        :raises ValueError: If start_price, end_price, or periods are less than or equal to zero.
        """
        if start_price <= 0 or end_price <= 0 or periods <= 0:
            raise ValueError("Start price, end price, and periods must be greater than zero.")

        return (end_price / start_price) ** (1 / periods) - 1


    @staticmethod
    def non_annualized_volatility(returns_series: pd.Series, downside: bool = False) -> float:
        """
        Calculate the volatility of a returns series.

        :param returns_series: A pandas Series of returns for the asset.
        :type returns_series: pd.Series

        :return: The volatility as a fraction.
        :rtype: float
        """
        if returns_series.empty:
            return 0.0
        
        if downside:
            negative_returns = returns_series[returns_series < 0]
            if negative_returns.empty:
                return 0.0
            return negative_returns.std()

        return returns_series.std()


    @staticmethod
    def sharpe_ratio(expected_returns: float, risk_free_rate: float, volatility: float) -> float:
        """
        Calculate the Sharpe ratio.

        :param expected_returns: The expected return of the investment.
        :type expected_returns: float

        :param risk_free_rate: The risk-free rate of return.
        :type risk_free_rate: float

        :param volatility: The volatility of the investment.
        :type volatility: float

        :return: The Sharpe ratio.
        :rtype: float
        """
        return (expected_returns - risk_free_rate) / volatility if volatility else 0.0


    @staticmethod
    def sortino_ratio(expected_returns: float, risk_free_rate: float, downside_volatility: float) -> float:
        """
        Calculate the Sortino ratio.

        :param expected_returns: The expected return of the investment.
        :type expected_returns: float

        :param risk_free_rate: The risk-free rate of return.
        :type risk_free_rate: float

        :param downside_volatility: The downside volatility of the investment.
        :type downside_volatility: float

        :return: The Sortino ratio.
        :rtype: float
        """
        return (expected_returns - risk_free_rate) / downside_volatility if downside_volatility else 0.0
    

    @staticmethod
    def max_drawdown(cumulative_returns_series: pd.Series) -> float:
        """
        Calculate the maximum drawdown from a series of cumulative returns.

        :param cumulative_returns_series: A pandas Series of cumulative returns for the asset.
        :type cumulative_returns_series: pd.Series

        :return: The maximum drawdown as a percentage.
        :rtype: float
        """
        if cumulative_returns_series.empty:
            return 0.0
        
        cumulative_peaks = cumulative_returns_series.cummax()
        fractional_drawdowns = (cumulative_peaks - cumulative_returns_series) / cumulative_peaks
        return fractional_drawdowns.max()
    

    @staticmethod
    def calmar_ratio(annual_return: float, max_drawdown: float) -> float:
        """
        Calculate the Calmar ratio.

        :param annual_return: The annual return of the investment.
        :type annual_return: float

        :param max_drawdown: The maximum drawdown as a percentage.
        :type max_drawdown: float

        :return: The Calmar ratio.
        :rtype: float
        """
        if max_drawdown == 0:
            return float('inf')
        
        return annual_return / abs(max_drawdown)
    