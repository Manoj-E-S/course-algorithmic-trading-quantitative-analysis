from technical_analysis.utils.enum_helpers import EnumWithValuesList


class ApiDataframingServiceEnum(EnumWithValuesList):

    from technical_analysis.services.base_api_dataframing_service import BaseApiDataframingService

    # Alpha Vantage API Dataframing Service
    from technical_analysis.services.alpha_vantage.api_dataframing_service import ApiDataframingService as AlphaVantageApiDataframingService
    ALPHA_VANTAGE: type[BaseApiDataframingService] = AlphaVantageApiDataframingService

    # Placeholder for future services
    INDIAN_API: type[BaseApiDataframingService] = None
