from technical_analysis.utils.enum_helpers import EnumWithValuesList


class OHLCVUDEnum(EnumWithValuesList):
    # API and Candlesticks support
    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOLUME = "volume"

    # Renko support
    UPTREND = "uptrend"
    DATETIME = "datetime"


    @classmethod
    def price_values(cls):
        """
        Returns a list of price enum values (O, H, L, and C).

        :return: A list of price enum values.
        """
        return [item.value for item in cls if item not in (OHLCVUDEnum.VOLUME, OHLCVUDEnum.UPTREND, OHLCVUDEnum.DATETIME)]