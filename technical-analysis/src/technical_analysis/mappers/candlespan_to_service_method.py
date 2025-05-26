from technical_analysis.enums.candlespan import CandlespanEnum


class CandlespanToServiceMethod:

    from technical_analysis.services.alpha_vantage.time_seris_service import TimeSeriesService
    ForAlphaVantage: dict = {
        CandlespanEnum.DAILY: TimeSeriesService.get_daily_data,
        CandlespanEnum.WEEKLY: TimeSeriesService.get_weekly_data,
        CandlespanEnum.MONTHLY: TimeSeriesService.get_monthly_data
    }
