from technical_analysis.utils import EnumWithValuesList

class OHLCVEnum(EnumWithValuesList):
    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOLUME = "volume"


    @classmethod
    def price_values(cls):
        """
        Returns a list of price enum values (O, H, L, and C).

        :return: A list of price enum values.
        """
        return [item.value for item in cls if item != OHLCVEnum.VOLUME]