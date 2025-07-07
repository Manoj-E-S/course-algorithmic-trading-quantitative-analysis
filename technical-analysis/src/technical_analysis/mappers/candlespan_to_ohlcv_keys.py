from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.ohlcvud import OHLCVUDEnum


class CandlespanToOhlcvKeys:
    
    from technical_analysis.mappers.candlespan_to_main_json_key import CandlespanToMainJsonKey
    ForAlphaVantage: dict = \
    {
        CandlespanEnum.DAILY: {
            OHLCVUDEnum.OPEN: "1. open",
            OHLCVUDEnum.HIGH: "2. high",
            OHLCVUDEnum.LOW: "3. low",
            OHLCVUDEnum.CLOSE: "4. close",
            OHLCVUDEnum.VOLUME: "5. volume",
        },

        CandlespanEnum.WEEKLY: {
            OHLCVUDEnum.OPEN: "1. open",
            OHLCVUDEnum.HIGH: "2. high",
            OHLCVUDEnum.LOW: "3. low",
            OHLCVUDEnum.CLOSE: "5. adjusted close",
            OHLCVUDEnum.VOLUME: "6. volume",
        },
        
        CandlespanEnum.MONTHLY: {
            OHLCVUDEnum.OPEN: "1. open",
            OHLCVUDEnum.HIGH: "2. high",
            OHLCVUDEnum.LOW: "3. low",
            OHLCVUDEnum.CLOSE: "5. adjusted close",
            OHLCVUDEnum.VOLUME: "6. volume",
        }
    }
