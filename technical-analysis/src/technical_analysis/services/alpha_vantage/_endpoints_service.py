class EndpointsService:
    """
    A class to manage API endpoints for stock market data.
    """

    def __init__(self):
        pass


    @staticmethod
    def __get_alpha_vantage_baseurl() -> str:
        """
        Returns the base URL for the Indian stock market API.

        Returns:
            str: The base URL for the Indian stock market API.
        """
        return "https://www.alphavantage.co"


    @staticmethod
    def get_query_endpoint() -> str:
        """
        Returns the endpoint for fetching stock details.

        Returns:
            str: The endpoint URL for fetching stock details.
        """
        return f"{EndpointsService.__get_alpha_vantage_baseurl()}/query"