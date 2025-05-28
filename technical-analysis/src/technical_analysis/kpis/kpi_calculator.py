import pandas as pd
from technical_analysis.enums.candlespan import CandlespanEnum


class KpiCalculator:
    """
    A class to calculate various KPIs for the trading strategy.
    """

    def __init__(self):
        pass


    @staticmethod
    def cagr(start_value: float, end_value: float, periods: int) -> float:
        """
        Calculate the Compound Annual Growth Rate (CAGR).

        :param start_value: The initial value of the investment.
        :type start_value: float

        :param end_value: The final value of the investment.
        :type end_value: float

        :param periods: The number of periods (years) over which the growth is calculated.
        :type periods: int

        :return: The CAGR as a percentage.
        :rtype: float
        """
        if start_value <= 0 or end_value <= 0 or periods <= 0:
            raise ValueError("Start value, end value, and periods must be greater than zero.")
        
        return ((end_value / start_value) ** (1 / periods) - 1) * 100


    @staticmethod
    def profit_loss(entry_price: float, exit_price: float, quantity: float) -> float:
        """
        Calculate the profit or loss from a trade.

        :param entry_price: The price at which the asset was bought.
        :type entry_price: float

        :param exit_price: The price at which the asset was sold.
        :type exit_price: float

        :param quantity: The number of units traded.
        :type quantity: float

        :return: The profit or loss from the trade.
        :rtype: float
        """
        return (exit_price - entry_price) * quantity
    

    @staticmethod
    def return_on_investment(entry_price: float, exit_price: float, quantity: float) -> float:
        """
        Calculate the return on investment (ROI) from a trade.

        :param entry_price: The price at which the asset was bought.
        :type entry_price: float

        :param exit_price: The price at which the asset was sold.
        :type exit_price: float

        :param quantity: The number of units traded.
        :type quantity: float

        :return: The ROI as a percentage.
        :rtype: float
        """
        profit_loss = KpiCalculator.profit_loss(entry_price, exit_price, quantity)
        return (profit_loss / (entry_price * quantity)) * 100
    

    @staticmethod
    def win_rate(trades: list[float]) -> float:
        """
        Calculate the win rate of a series of trades.

        :param trades: A list of profit/loss values for each trade.
        :type trades: list[float]

        :return: The win rate as a percentage.
        :rtype: float
        """
        if not trades:
            return 0.0
        
        wins = sum(1 for trade in trades if trade > 0)
        return (wins / len(trades)) * 100
    

    @staticmethod
    def average_profit(trades: list[float]) -> float:
        """
        Calculate the average profit from a series of trades.

        :param trades: A list of profit/loss values for each trade.
        :type trades: list[float]

        :return: The average profit.
        :rtype: float
        """
        if not trades:
            return 0.0
        
        return sum(trades) / len(trades)
    

    @staticmethod
    def max_drawdown(trades: list[float]) -> float:
        """
        Calculate the maximum drawdown from a series of trades.

        :param trades: A list of profit/loss values for each trade.
        :type trades: list[float]

        :return: The maximum drawdown as a percentage.
        :rtype: float
        """
        if not trades:
            return 0.0
        
        max_drawdown = 0.0
        peak = trades[0]
        
        for trade in trades:
            if trade > peak:
                peak = trade
            drawdown = (peak - trade) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    

    @staticmethod
    def sharpe_ratio(returns: list[float], risk_free_rate: float = 0.0) -> float:
        """
        Calculate the Sharpe ratio of a series of returns.

        :param returns: A list of returns for each period.
        :type returns: list[float]

        :param risk_free_rate: The risk-free rate of return.
        :type risk_free_rate: float

        :return: The Sharpe ratio.
        :rtype: float
        """
        if not returns:
            return 0.0

        excess_returns = [r - risk_free_rate for r in returns]
        return sum(excess_returns) / len(excess_returns)


    @staticmethod
    def sortino_ratio(returns: list[float], risk_free_rate: float = 0.0) -> float:
        """
        Calculate the Sortino ratio of a series of returns.

        :param returns: A list of returns for each period.
        :type returns: list[float]

        :param risk_free_rate: The risk-free rate of return.
        :type risk_free_rate: float

        :return: The Sortino ratio.
        :rtype: float
        """
        if not returns:
            return 0.0
        
        downside_returns = [r for r in returns if r < risk_free_rate]
        downside_deviation = (sum((r - risk_free_rate) ** 2 for r in downside_returns) / len(downside_returns)) ** 0.5 if downside_returns else 0.0
        
        excess_returns = [r - risk_free_rate for r in returns]
        return sum(excess_returns) / (downside_deviation if downside_deviation > 0 else 1)
    

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
    

    @staticmethod
    def alpha(returns: list[float], benchmark_returns: list[float], risk_free_rate: float = 0.0) -> float:
        """
        Calculate the alpha of a series of returns compared to a benchmark.

        :param returns: A list of returns for the investment.
        :type returns: list[float]

        :param benchmark_returns: A list of returns for the benchmark.
        :type benchmark_returns: list[float]

        :param risk_free_rate: The risk-free rate of return.
        :type risk_free_rate: float

        :return: The alpha value.
        :rtype: float
        """
        if not returns or not benchmark_returns:
            return 0.0
        
        excess_returns = [r - risk_free_rate for r in returns]
        excess_benchmark_returns = [b - risk_free_rate for b in benchmark_returns]
        
        return sum(excess_returns) - sum(excess_benchmark_returns)
    

    @staticmethod
    def beta(returns: list[float], benchmark_returns: list[float]) -> float:
        """
        Calculate the beta of a series of returns compared to a benchmark.

        :param returns: A list of returns for the investment.
        :type returns: list[float]

        :param benchmark_returns: A list of returns for the benchmark.
        :type benchmark_returns: list[float]

        :return: The beta value.
        :rtype: float
        """
        if not returns or not benchmark_returns:
            return 0.0
        
        covariance = sum((r - sum(returns) / len(returns)) * (b - sum(benchmark_returns) / len(benchmark_returns)) for r, b in zip(returns, benchmark_returns))
        variance = sum((b - sum(benchmark_returns) / len(benchmark_returns)) ** 2 for b in benchmark_returns)
        
        return covariance / variance if variance != 0 else 0.0
    

    @staticmethod
    def r_squared(returns: list[float], benchmark_returns: list[float]) -> float:
        """
        Calculate the R-squared value of a series of returns compared to a benchmark.

        :param returns: A list of returns for the investment.
        :type returns: list[float]

        :param benchmark_returns: A list of returns for the benchmark.
        :type benchmark_returns: list[float]

        :return: The R-squared value.
        :rtype: float
        """
        if not returns or not benchmark_returns:
            return 0.0
        
        beta = KpiCalculator.beta(returns, benchmark_returns)
        variance_benchmark = sum((b - sum(benchmark_returns) / len(benchmark_returns)) ** 2 for b in benchmark_returns)
        
        return beta * (sum((r - sum(returns) / len(returns)) ** 2 for r in returns) / variance_benchmark) if variance_benchmark != 0 else 0.0
    

    @staticmethod
    def information_ratio(returns: list[float], benchmark_returns: list[float], risk_free_rate: float = 0.0) -> float:
        """
        Calculate the information ratio of a series of returns compared to a benchmark.

        :param returns: A list of returns for the investment.
        :type returns: list[float]

        :param benchmark_returns: A list of returns for the benchmark.
        :type benchmark_returns: list[float]

        :param risk_free_rate: The risk-free rate of return.
        :type risk_free_rate: float

        :return: The information ratio.
        :rtype: float
        """
        if not returns or not benchmark_returns:
            return 0.0
        
        excess_returns = [r - risk_free_rate for r in returns]
        excess_benchmark_returns = [b - risk_free_rate for b in benchmark_returns]
        
        tracking_error = (sum((er - eb) ** 2 for er, eb in zip(excess_returns, excess_benchmark_returns)) / len(excess_benchmark_returns)) ** 0.5
        
        return sum(excess_returns) / tracking_error if tracking_error != 0 else 0.0
    

    @staticmethod
    def omega_ratio(returns: list[float], risk_free_rate: float = 0.0) -> float:
        """
        Calculate the Omega ratio of a series of returns.

        :param returns: A list of returns for the investment.
        :type returns: list[float]

        :param risk_free_rate: The risk-free rate of return.
        :type risk_free_rate: float

        :return: The Omega ratio.
        :rtype: float
        """
        if not returns:
            return 0.0
        
        gains = sum(r for r in returns if r > risk_free_rate)
        losses = abs(sum(r for r in returns if r < risk_free_rate))
        
        return gains / losses if losses != 0 else float('inf')