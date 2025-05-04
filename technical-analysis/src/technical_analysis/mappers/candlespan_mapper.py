from technical_analysis.models import AlphaVantageEnum, CandlespanEnum
from technical_analysis.services import AlphaVantage
from technical_analysis.mappers.alpha_vantage import ToTimeSeriesJsonKeyMappers

class CandlespanMappers:
    CANDLESPAN_ALPHAVANTAGEENUM_MAPPER: dict = {
        CandlespanEnum.DAILY: AlphaVantageEnum.TIME_SERIES_DAILY,
        CandlespanEnum.WEEKLY: AlphaVantageEnum.TIME_SERIIES_WEEKLY,
        CandlespanEnum.MONTHLY: AlphaVantageEnum.TIME_SERIES_MONTHLY
    }

    CANDLESPAN_SERVICEMETHOD_MAPPER: dict = {
        CandlespanEnum.DAILY: AlphaVantage.TimeSeriesService.get_daily_data,
        CandlespanEnum.WEEKLY: AlphaVantage.TimeSeriesService.get_weekly_data,
        CandlespanEnum.MONTHLY: AlphaVantage.TimeSeriesService.get_monthly_data
    }

    CANDLESPAN_OHLCVMAPPER_MAPPER: dict = {
        CandlespanEnum.DAILY: ToTimeSeriesJsonKeyMappers.DAILY_OHLCV_JSONKEY_MAPPER,
        CandlespanEnum.WEEKLY: ToTimeSeriesJsonKeyMappers.WEEKLY_OHLCV_JSONKEY_MAPPER,
        CandlespanEnum.MONTHLY: ToTimeSeriesJsonKeyMappers.MONTHLY_OHLCV_JSONKEY_MAPPER
    }