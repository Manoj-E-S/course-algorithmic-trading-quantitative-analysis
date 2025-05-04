from enum import Enum


class AlphaVantageEnum(Enum):
    TIME_SERIES_DAILY = "alpha_vantage.time_series_daily"
    TIME_SERIIES_WEEKLY = "alpha_vantage.time_series_weekly"
    TIME_SERIES_MONTHLY = "alpha_vantage.time_series_monthly"


class IndianAPIEnum(Enum):
    STOCK_DETAILS = "indian_api.stock_details"
    HISTORICAL_DATA = "indian_api.historical_data"