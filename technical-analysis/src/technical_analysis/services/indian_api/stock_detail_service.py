import requests

from technical_analysis.services._validation_service import ValidationService
from technical_analysis.services.indian_api._auth_service import AuthService
from technical_analysis.services.indian_api._endpoints_service import EndpointsService


class StockDetailService:
    """
    A service class to interact with the Stock data of the IndianAPI
    """

    def __init__(self):
        pass

    @staticmethod
    def get_stock_details_data(stock_name: str) -> dict | None:
        """
        Calls the indian stock details api and returns its response

        Args:
            stock_name(str): The name of the stock whose data is required

        Returns:
            api_response.json(): dict | None
        """
        print(f"[INFO] Making API request for stock details of {stock_name}...")
        response: requests.Response = requests.get(
            EndpointsService.get_stock_details_endpoint(),
            headers = AuthService.get_auth_header(),
            params = {
                "name": stock_name
            }
        )

        if not (ValidationService.is_status_code_ok(response) and ValidationService.does_json_exist(response)):
            return

        return response.json()