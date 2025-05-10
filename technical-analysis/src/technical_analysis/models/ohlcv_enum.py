from technical_analysis.utils import EnumWithValuesList

class OHLCVEnum(EnumWithValuesList):
    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOLUME = "volume"