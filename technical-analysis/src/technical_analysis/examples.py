from technical_analysis.components.alpha_vantage import StockMetricIndicationComponent, StockTechnicalIndicationComponent
from technical_analysis.models import CandlespanEnum, OHLCVEnum

if __name__ == "__main__":

    metric: OHLCVEnum = OHLCVEnum.CLOSE
    candle_span: CandlespanEnum = CandlespanEnum.DAILY
    instrument_symbols: list[str] = ['RELIANCE.BSE', 'HDFCBANK.BSE', 'ICICIBANK.BSE', 'SBIN.BSE', 'TATAMOTORS.BSE', 'ITC.BSE']
    na_strategy: str = 'backfill'
    
    stock_metric_operator: StockMetricIndicationComponent = StockMetricIndicationComponent(
        metric=metric, 
        candle_span=candle_span, 
        instrument_symbols=instrument_symbols,
        na_strategy=na_strategy
    )

    print(stock_metric_operator.get_simple_moving_operation_results(10, 'mean', True))
    print(stock_metric_operator.get_exponential_moving_operation_results(10, 'mean', 10, True))
    print(stock_metric_operator.get_change_in_metric_df())
    print(stock_metric_operator.get_cumulative_change_in_metric_df())

    """
    Uncomment the following lines to visualize the data
    """
    # stock_metric_operator.plot_change_in_metric(cumulative=False, title="Daily returns", ylabel="Daily returns", styling='ggplot')
    # stock_metric_operator.plot_change_in_metric(cumulative=True, title="Cumulative daily returns", ylabel="Cumulative returns", styling='ggplot')
    # stock_metric_operator.plot_avg_change_in_metric()
    # stock_metric_operator.plot_std_of_change_in_metric()
    # stock_metric_operator.plot_mean_std_change_in_metric()

    stock_technicals: dict[str, StockTechnicalIndicationComponent] = {}
    for i in range(len(instrument_symbols)):
        stock_technicals[instrument_symbols[i]] = StockTechnicalIndicationComponent(
            metric=metric, 
            candle_span=candle_span, 
            instrument_symbol=instrument_symbols[i],
            na_strategy=na_strategy
        )


    for symbol, stock_technical in stock_technicals.items():
        print(f"MACD indicator for {symbol}:")
        print(stock_technical.macd().collect())
        print()

