from typing import Literal

import requests
from technical_analysis.services.alpha_vantage._endpoints_service import EndpointsService
from technical_analysis.services.alpha_vantage._auth_service import AuthService
from technical_analysis.services._validation_service import ValidationService

class TimeSeriesService:
    """
    A service class to interact with the Time Series data of the Alpha vantage API
    """

    FUNCTIONS_PARAM: dict = {
        "DAILY": "TIME_SERIES_DAILY",
        "WEEKLY": "TIME_SERIES_WEEKLY_ADJUSTED",
        "MONTHLY": "TIME_SERIES_MONTHLY_ADJUSTED"
    }

    def __init__(self):
        pass

    @staticmethod
    def __get_data(
        which_series: Literal["DAILY", "WEEKLY", "MONTHLY"],
        symbol: str, 
        output_size: Literal["compact", "full"] = "full",
        data_type: Literal["json", "csv"] = "json"
    ) -> dict | None:
        """
        Calls the Alpha Vantage API for specified time_series data and returns its response

        Args:
            which_series(Literal["DAILY", "WEEKLY", "MONTHLY"]): Type of time series required
            symbol(str): The identifier of the instrument whose data is required
            output_size(Literal["compact", "full"]): Strings "compact" and "full" are accepted with the following specifications - "compact" returns only the latest 100 data points; "full" returns the full-length time series of 20+ years of historical data. The "compact" option is recommended if you would like to reduce the data size of each API call. Defaults to "full".
            data_type(Literal["json", "csv"]): Strings "json" and "csv" are accepted with the following specifications - "json" returns the daily time series in JSON format; "csv" returns the time series as a CSV (comma separated value) file. Defaults to "json".

        Returns:
            api_response.json(): dict | None
        """
        # SAMPLE ENDPOINT
        # https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=RELIANCE.BSE&outputsize=full&datatype=json&apikey=demo

        print(f"[INFO] Making API request for time-series-{which_series.lower()} data of the instrument identified by {symbol}...")
        response: requests.Response = requests.get(
            EndpointsService.get_query_endpoint(),
            params = {
                "function": TimeSeriesService.FUNCTIONS_PARAM.get(which_series),
                "symbol": symbol,
                "outputsize": output_size,
                "datatype": data_type,
                **AuthService.get_auth_param()
            }
        )

        if not (ValidationService.is_status_code_ok(response) and ValidationService.does_json_exist(response)):
            return

        return response.json()
    

    @staticmethod
    def get_daily_data(
        symbol: str, 
        output_size: Literal["compact", "full"] = "full",
        data_type: Literal["json", "csv"] = "json"
    ) -> dict | None:
        """
        Calls the Alpha Vantage API for time_series_daily data and returns its response

        Args:
            symbol(str): The identifier of the instrument whose data is required
            output_size(Literal["compact", "full"]): Strings "compact" and "full" are accepted with the following specifications - "compact" returns only the latest 100 data points; "full" returns the full-length time series of 20+ years of historical data. The "compact" option is recommended if you would like to reduce the data size of each API call. Defaults to "full".
            data_type(Literal["json", "csv"]): Strings "json" and "csv" are accepted with the following specifications - "json" returns the daily time series in JSON format; "csv" returns the time series as a CSV (comma separated value) file. Defaults to "json".

        Returns:
            api_response.json(): dict | None
        """

        return TimeSeriesService.__get_data(
            "DAILY",
            symbol,
            output_size,
            data_type
        )
    
    
    @staticmethod
    def get_weekly_data(
        symbol: str, 
        output_size: Literal["compact", "full"] = "full",
        data_type: Literal["json", "csv"] = "json"
    ) -> dict | None:
        """
        Calls the Alpha Vantage API for time_series_weekly data and returns its response

        Args:
            symbol(str): The identifier of the instrument whose data is required
            output_size(Literal["compact", "full"]): Strings "compact" and "full" are accepted with the following specifications - "compact" returns only the latest 100 data points; "full" returns the full-length time series of 20+ years of historical data. The "compact" option is recommended if you would like to reduce the data size of each API call. Defaults to "full".
            data_type(Literal["json", "csv"]): Strings "json" and "csv" are accepted with the following specifications - "json" returns the daily time series in JSON format; "csv" returns the time series as a CSV (comma separated value) file. Defaults to "json".

        Returns:
            api_response.json(): dict | None
        """

        return TimeSeriesService.__get_data(
            "WEEKLY",
            symbol,
            output_size,
            data_type
        )
    
    
    @staticmethod
    def get_monthly_data(
        symbol: str, 
        output_size: Literal["compact", "full"] = "full",
        data_type: Literal["json", "csv"] = "json"
    ) -> dict | None:
        """
        Calls the Alpha Vantage API for time_series_monthly data and returns its response

        Args:
            symbol(str): The identifier of the instrument whose data is required
            output_size(Literal["compact", "full"]): Strings "compact" and "full" are accepted with the following specifications - "compact" returns only the latest 100 data points; "full" returns the full-length time series of 20+ years of historical data. The "compact" option is recommended if you would like to reduce the data size of each API call. Defaults to "full".
            data_type(Literal["json", "csv"]): Strings "json" and "csv" are accepted with the following specifications - "json" returns the daily time series in JSON format; "csv" returns the time series as a CSV (comma separated value) file. Defaults to "json".

        Returns:
            api_response.json(): dict | None
        """

        return TimeSeriesService.__get_data(
            "MONTHLY",
            symbol,
            output_size,
            data_type
        )