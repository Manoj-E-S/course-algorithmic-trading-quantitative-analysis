from technical_analysis.utils.enum_helpers import EnumWithValuesList


class CandlespanEnum(EnumWithValuesList):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

    @classmethod
    def periods_per_year(cls, span: 'CandlespanEnum') -> int:
        """
        Returns the number of periods in a year for the given candle span.

        :return: The number of periods in a year for the given span.
        :rtype: int
        """
        periods: int = None
        if span == cls.DAILY:
            periods = 252
        elif span == cls.WEEKLY:
            periods = 52
        elif span == cls.MONTHLY:
            periods = 12

        if periods is None:
            raise ValueError(f"Unsupported candle span: {span}. Supported spans are: {cls.values()}.")

        return periods