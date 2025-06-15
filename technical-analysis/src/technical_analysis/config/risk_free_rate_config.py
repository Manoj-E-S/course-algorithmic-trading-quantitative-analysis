class GlobalRiskFreeRateConfig:
    """
    Configuration class for the global risk-free rate.
    This class holds the risk-free rate value used in financial calculations.
    """

    RISK_FREE_RATE: float = 0.06


    @classmethod
    def set(cls, rate: float):
        """
        Set the global risk-free rate.

        :param rate: The risk-free rate to set (in percentage).
        """
        cls.RISK_FREE_RATE = rate
    

    @classmethod
    def get(cls) -> float:
        """
        Get the global risk-free rate.

        :return: The current global risk-free rate (in percentage).
        """
        return cls.RISK_FREE_RATE
    

    @classmethod
    def reset(cls):
        """
        Reset the global risk-free rate to its default value.
        """
        cls.RISK_FREE_RATE = 0.06