from technical_analysis.components.alpha_vantage import DataOperatorComponent
from technical_analysis.models import CandlespanEnum, OHLCVEnum


if __name__ == "__main__":

    metric: OHLCVEnum = OHLCVEnum.CLOSE
    candle_span: CandlespanEnum = CandlespanEnum.DAILY
    instrument_symbols: list[str] = ['RELIANCE.BSE', 'HDFCBANK.BSE', 'ICICIBANK.BSE', 'SBIN.BSE', 'TATAMOTORS.BSE', 'ITC.BSE']
    na_strategy: str = 'backfill'
    
    df_operator: DataOperatorComponent = DataOperatorComponent(
        metric=metric, 
        candle_span=candle_span, 
        instrument_symbols=instrument_symbols,
        na_strategy=na_strategy
    )

    print(df_operator.get_simple_moving_operation_results(10, 'mean', True))
    print(df_operator.get_exponential_moving_operation_results(10, 'mean', 10, True))
    print(df_operator.get_change_in_metric_df())
    print(df_operator.get_cumulative_change_in_metric_df())
    df_operator.plot_change_in_metric(cumulative=True, title="Cumulative daily returns", ylabel="Cumulative returns", styling='ggplot')
    df_operator.plot_avg_change_in_metric()
    df_operator.plot_std_of_change_in_metric()
    df_operator.plot_mean_std_change_in_metric()