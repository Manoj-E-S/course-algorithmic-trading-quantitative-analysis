from technical_analysis.services import AlphaVantage, BaseApiDataframingService
from technical_analysis.utils.enum_helpers import EnumWithValuesList


class DataframingServiceEnum(EnumWithValuesList):
    ALPHA_VANTAGE: type[BaseApiDataframingService] = AlphaVantage.DataframingService
    INDIAN_API: type[BaseApiDataframingService] = None  # Placeholder for future services
