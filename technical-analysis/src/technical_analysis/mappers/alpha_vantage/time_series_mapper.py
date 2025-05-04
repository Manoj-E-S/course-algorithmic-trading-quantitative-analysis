from technical_analysis.models import CandlespanEnum, OHLCVEnum

class ToTimeSeriesJsonKeyMappers:
    CANDLESPAN_MAINJSONKEY_MAPPER: dict = {
        CandlespanEnum.DAILY: "Time Series (Daily)",
        CandlespanEnum.WEEKLY: "Weekly Adjusted Time Series",
        CandlespanEnum.MONTHLY: "Monthly Adjusted Time Series"
    }
    
    DAILY_OHLCV_JSONKEY_MAPPER: dict = {
        OHLCVEnum.OPEN: "1. open",
        OHLCVEnum.HIGH: "2. high",
        OHLCVEnum.LOW: "3. low",
        OHLCVEnum.CLOSE: "4. close",
        OHLCVEnum.VOLUME: "5. volume",
    }

    WEEKLY_OHLCV_JSONKEY_MAPPER: dict = {
        OHLCVEnum.OPEN: "1. open",
        OHLCVEnum.HIGH: "2. high",
        OHLCVEnum.LOW: "3. low",
        OHLCVEnum.CLOSE: "4. close",
        OHLCVEnum.VOLUME: "6. volume",
    }

    MONTHLY_OHLCV_JSONKEY_MAPPER: dict = {
        OHLCVEnum.OPEN: "1. open",
        OHLCVEnum.HIGH: "2. high",
        OHLCVEnum.LOW: "3. low",
        OHLCVEnum.CLOSE: "4. close",
        OHLCVEnum.VOLUME: "6. volume",
    }