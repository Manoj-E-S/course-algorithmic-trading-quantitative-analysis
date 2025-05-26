from technical_analysis.enums.candlespan import CandlespanEnum


class CandlespanToApi:

    from technical_analysis.enums.api import AlphaVantageEnum
    ForAlphaVantage: dict = {
        CandlespanEnum.DAILY: AlphaVantageEnum.TIME_SERIES_DAILY,
        CandlespanEnum.WEEKLY: AlphaVantageEnum.TIME_SERIIES_WEEKLY,
        CandlespanEnum.MONTHLY: AlphaVantageEnum.TIME_SERIES_MONTHLY
    }