import json
import os

from technical_analysis.services import IndianAPI, AlphaVantage

class _Examples:

    def __init__(self):
        pass


    @staticmethod
    def write_as_json_file(
        response_data: dict,
        response_file_path: str,
        indent: int = 4
    ) -> None:
        data_dir = os.path.dirname(response_file_path)
        print(data_dir)

        os.makedirs(data_dir, exist_ok=True)
        with open(response_file_path, 'w') as f:
            json.dump(response_data, f, indent=indent)


    @staticmethod
    def indian_api_historical_data() -> None:
        stock_name: str = "Tata Steel"

        response_filename: str = "historical_data_response.json"
        data_dir: str = os.path.join(os.getcwd(), "data", "indian_api", stock_name.lower().replace(' ', '_'))
        response_file: str = os.path.join(data_dir, response_filename)

        if os.path.exists(response_file):
            print("[INFO] Skipping API request")
            print(f"[INFO] Response cached at {response_file}")
            return

        response_data = IndianAPI.HistoricalDataService.get_historical_data(stock_name)

        if not response_data:
            return
        
        _Examples.write_as_json_file(response_data, response_file)


    @staticmethod
    def indian_api_stock_details() -> None:
        stock_name: str = "Tata Steel"

        response_filename: str = "stock_details_response.json"
        data_dir: str = os.path.join(os.getcwd(), "data", "indian_api", stock_name.lower().replace(' ', '_'))
        response_file: str = os.path.join(data_dir, response_filename)

        if os.path.exists(response_file):
            print("[INFO] Skipping API request")
            print(f"[INFO] Response cached at {response_file}")
            return

        response_data = IndianAPI.StockDetailService.get_stock_details_data(stock_name)

        if not response_data:
            return
        
        _Examples.write_as_json_file(response_data, response_file)


    
    @staticmethod
    def alpha_vantage_time_series_daily() -> None:
        symbol: str = "RELIANCE.BSE"

        response_filename: str = "time_series_daily_response.json"
        data_dir: str = os.path.join(os.getcwd(), "data", "alpha_vantage", symbol.lower().replace(' ', '_').replace('.', '_').replace(':', '_'))
        response_file: str = os.path.join(data_dir, response_filename)

        if os.path.exists(response_file):
            print("[INFO] Skipping API request")
            print(f"[INFO] Response cached at {response_file}")
            return

        response_data = AlphaVantage.TimeSeriesService.get_daily_data(symbol)

        if not response_data:
            return
        
        _Examples.write_as_json_file(response_data, response_file)


    
    @staticmethod
    def alpha_vantage_time_series_weekly() -> None:
        symbol: str = "RELIANCE.BSE"

        response_filename: str = "time_series_weekly_response.json"
        data_dir: str = os.path.join(os.getcwd(), "data", "alpha_vantage", symbol.lower().replace(' ', '_').replace('.', '_').replace(':', '_'))
        response_file: str = os.path.join(data_dir, response_filename)

        if os.path.exists(response_file):
            print("[INFO] Skipping API request")
            print(f"[INFO] Response cached at {response_file}")
            return

        response_data = AlphaVantage.TimeSeriesService.get_weekly_data(symbol)

        if not response_data:
            return
        
        _Examples.write_as_json_file(response_data, response_file)


    
    @staticmethod
    def alpha_vantage_time_series_monthly() -> None:
        symbol: str = "RELIANCE.BSE"

        response_filename: str = "time_series_monthly_response.json"
        data_dir: str = os.path.join(os.getcwd(), "data", "alpha_vantage", symbol.lower().replace(' ', '_').replace('.', '_').replace(':', '_'))
        response_file: str = os.path.join(data_dir, response_filename)

        if os.path.exists(response_file):
            print("[INFO] Skipping API request")
            print(f"[INFO] Response cached at {response_file}")
            return

        response_data = AlphaVantage.TimeSeriesService.get_monthly_data(symbol)

        if not response_data:
            return
        
        _Examples.write_as_json_file(response_data, response_file)




if __name__ == "__main__":
    _Examples.indian_api_historical_data()
    _Examples.indian_api_stock_details()
    _Examples.alpha_vantage_time_series_daily()
    _Examples.alpha_vantage_time_series_weekly()
    _Examples.alpha_vantage_time_series_monthly()