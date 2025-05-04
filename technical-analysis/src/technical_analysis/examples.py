from technical_analysis.components.alpha_vantage import DataframerComponent
from technical_analysis.models import AlphaVantageEnum, IndianAPIEnum
from technical_analysis.models import CandlespanEnum, OHLCVEnum
from technical_analysis.services import IndianAPI, AlphaVantage
from technical_analysis.components import ResponseCacherComponent

class _Examples:

    def __init__(self):
        pass


    @staticmethod
    def indian_api_historical_data() -> None:
        stock_name: str = "Tata Steel"

        if ResponseCacherComponent.is_response_data_cached(IndianAPIEnum.HISTORICAL_DATA, stock_name):
            print(f"[INFO] Skipping API request as the response is cached at {ResponseCacherComponent.RESPONSE_CACHE_DIR}")
            return

        response_data = IndianAPI.HistoricalDataService.get_historical_data(stock_name)

        if not response_data:
            return
        
        ResponseCacherComponent.cache_response_data(IndianAPIEnum.HISTORICAL_DATA, stock_name, response_data)


    @staticmethod
    def indian_api_stock_details() -> None:
        stock_name: str = "Tata Steel"

        if ResponseCacherComponent.is_response_data_cached(IndianAPIEnum.STOCK_DETAILS, stock_name):
            print(f"[INFO] Skipping API request as the response is cached at {ResponseCacherComponent.RESPONSE_CACHE_DIR}")
            return

        response_data = IndianAPI.StockDetailService.get_stock_details_data(stock_name)

        if not response_data:
            return
        
        ResponseCacherComponent.cache_response_data(IndianAPIEnum.STOCK_DETAILS, stock_name, response_data)


    
    @staticmethod
    def alpha_vantage_time_series_daily() -> None:
        symbol: str = "RELIANCE.BSE"

        if ResponseCacherComponent.is_response_data_cached(AlphaVantageEnum.TIME_SERIES_DAILY, symbol):
            print(f"[INFO] Skipping API request as the response is cached at {ResponseCacherComponent.RESPONSE_CACHE_DIR}")
            return

        response_data = AlphaVantage.TimeSeriesService.get_daily_data(symbol)

        if not response_data:
            return
        
        ResponseCacherComponent.cache_response_data(AlphaVantageEnum.TIME_SERIES_DAILY, symbol, response_data)


    
    @staticmethod
    def alpha_vantage_time_series_weekly() -> None:
        symbol: str = "RELIANCE.BSE"

        if ResponseCacherComponent.is_response_data_cached(AlphaVantageEnum.TIME_SERIIES_WEEKLY, symbol):
            print(f"[INFO] Skipping API request as the response is cached at {ResponseCacherComponent.RESPONSE_CACHE_DIR}")   
            return

        response_data = AlphaVantage.TimeSeriesService.get_weekly_data(symbol)

        if not response_data:
            return
        
        ResponseCacherComponent.cache_response_data(AlphaVantageEnum.TIME_SERIIES_WEEKLY, symbol, response_data)


    
    @staticmethod
    def alpha_vantage_time_series_monthly() -> None:
        symbol: str = "RELIANCE.BSE"

        if ResponseCacherComponent.is_response_data_cached(AlphaVantageEnum.TIME_SERIES_MONTHLY, symbol):
            print(f"[INFO] Skipping API request as the response is cached at {ResponseCacherComponent.RESPONSE_CACHE_DIR}")
            return

        response_data = AlphaVantage.TimeSeriesService.get_monthly_data(symbol)

        if not response_data:
            return
        
        ResponseCacherComponent.cache_response_data(AlphaVantageEnum.TIME_SERIES_MONTHLY, symbol, response_data)




if __name__ == "__main__":
    # _Examples.indian_api_historical_data()
    # _Examples.indian_api_stock_details()
    # _Examples.alpha_vantage_time_series_daily()
    # _Examples.alpha_vantage_time_series_weekly()
    # _Examples.alpha_vantage_time_series_monthly()
    DataframerComponent.get_dataframe(OHLCVEnum.CLOSE, CandlespanEnum.MONTHLY, ['RELIANCE.BSE', 'HDFCBANK.BSE', 'ICICIBANK.BSE', 'INFY.BSE', 'SBIN.BSE', 'TATAMOTORS.BSE', 'ITC.BSE'])