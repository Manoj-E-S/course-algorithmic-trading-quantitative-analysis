class EndpointsService:
    """
    A class to manage API endpoints for stock market data.
    """

    def __init__(self):
        pass


    @staticmethod
    def __get_indian_stock_market_api_baseurl() -> str:
        """
        Returns the base URL for the Indian stock market API.

        Returns:
            str: The base URL for the Indian stock market API.
        """
        return "https://stock.indianapi.in"


    @staticmethod
    def get_stock_details_endpoint() -> str:
        """
        Returns the endpoint for fetching stock details.

        Returns:
            str: The endpoint URL for fetching stock details.
        """
        return f"{EndpointsService.__get_indian_stock_market_api_baseurl()}/stock"
    
        
    @staticmethod
    def get_historical_data_endpoint() -> str:
        """
        Returns the endpoint for fetching stock details.

        Returns:
            str: The endpoint URL for fetching stock details.
        """
        return f"{EndpointsService.__get_indian_stock_market_api_baseurl()}/historical_data"