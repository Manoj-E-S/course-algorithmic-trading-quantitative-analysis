from typing import Literal
import requests

from technical_analysis.services._validation_service import ValidationService
from technical_analysis.services.indian_api._auth_service import AuthService
from technical_analysis.services.indian_api._endpoints_service import EndpointsService


class HistoricalDataService:
    """
    A service class to interact with the Historical data of the IndianAPI
    """

    def __init__(self):
        pass

    @staticmethod
    def get_historical_data(
        stock_name: str, 
        period: Literal["1m", "6m", "1yr", "3yr", "5yr", "10yr", "max"] = "max", 
        filter: Literal["default", "price", "pe", "sm", "evebitda", "ptb", "mcs"] = "default"
    ) -> dict | None:
        """
        Calls the indian historical data api and returns its response

        Args:
            stock_name(str): [Required] The name of the stock whose data is required
            period(Literal["1m", "6m", "1yr", "3yr", "5yr", "10yr", "max"]): [Optional] Duration for which the data is required, defaults to "max"
            filter(Literal["default", "price", "pe", "sm", "evebitda", "ptb", "mcs"]): [Optional] How to filter the data, defaults to "default"

        Returns:
            api_response.json(): dict | None
        """
        print(f"[INFO] Making API request for historical data of {stock_name}...")
        response: requests.Response = requests.get(
            EndpointsService.get_historical_data_endpoint(),
            headers = AuthService.get_auth_header(),
            params = {
                "stock_name": stock_name,
                "period": period,
                "filter": filter
            }
        )

        if not (ValidationService.is_status_code_ok(response) and ValidationService.does_json_exist(response)):
            return

        return response.json()