from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.ohlcvud import OHLCVUDEnum


class CandlespanToMainJsonKey:
    
    ForAlphaVantage: dict = {
        CandlespanEnum.DAILY: "Time Series (Daily)",
        CandlespanEnum.WEEKLY: "Weekly Adjusted Time Series",
        CandlespanEnum.MONTHLY: "Monthly Adjusted Time Series"
    }