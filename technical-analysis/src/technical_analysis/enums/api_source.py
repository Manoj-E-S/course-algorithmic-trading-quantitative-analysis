from technical_analysis.utils.enum_helpers import EnumWithValuesList


class ApiSourceEnum(EnumWithValuesList):
    """
    Enum to provide the source of API data for various modules in the technical analysis package.
    The class of each api's dataframing service (aka the api data source) is stored as values.
    """
    from technical_analysis.services.base_api_dataframing_service import BaseApiDataframingService

    # Alpha Vantage API Dataframing Service
    from technical_analysis.services.alpha_vantage.api_dataframing_service import ApiDataframingService as AlphaVantageApiDataframingService
    ALPHA_VANTAGE: type[BaseApiDataframingService] = AlphaVantageApiDataframingService

    # Placeholder for future services
    INDIAN_API: type[BaseApiDataframingService] = None
