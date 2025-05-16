from technical_analysis.components.alpha_vantage import StockMetricVisualisationComponent, StockTechnicalIndicationComponent
from technical_analysis.components.alpha_vantage.data_store_component import DataStoreComponent
from technical_analysis.models import CandlespanEnum, OHLCVEnum

if __name__ == "__main__":

    metric: OHLCVEnum = OHLCVEnum.CLOSE
    candle_span: CandlespanEnum = CandlespanEnum.MONTHLY
    na_strategy: str = 'backfill'
    use_api_cache_when_applicable: bool = True

    """
    Uncomment below line for all valid instrument symbols
    """
    instrument_symbols: list[str] = ['RELIANCE.BSE', 'HDFCBANK.BSE', 'ICICIBANK.BSE', 'SBIN.BSE', 'TATAMOTORS.BSE', 'ITC.BSE']
    
    """
    Uncomment below line for one invalid instrument symbol (ahbgd) in instrument_symbols
    """
    # instrument_symbols: list[str] = ['RELIANCE.BSE', 'HDFCBANK.BSE', 'ICICIBANK.BSE', 'SBIN.BSE', 'TATAMOTORS.BSE', 'ITC.BSE', 'XYZ', 'ahbgd']

    daily_ohlcv_store: DataStoreComponent = DataStoreComponent(
        metric=metric, 
        candle_span=candle_span, 
        instrument_symbols=instrument_symbols,
        na_strategy=na_strategy,
        use_api_cache_when_applicable=use_api_cache_when_applicable
    )

    """
    Uncomment below line to verify that invalid instruments are dropped by the DataStoreComponent
    """
    # print(daily_ohlcv_store.instrument_symbols)

    print(daily_ohlcv_store.main_metric_df)
    print(
        daily_ohlcv_store.get_simple_moving_operation_df(
            on_which_df='main_metric', 
            which_operation='mean', 
            window=10
        )
    )
    print(
        daily_ohlcv_store.get_exponential_moving_operation_df(
            on_which_df='main_metric', 
            which_operation='mean', 
            window=10
        )
    )
    print(daily_ohlcv_store.change_in_main_metric_df)
    print(daily_ohlcv_store.cumulative_change_in_main_metric_df)
    
    """
    Uncomment the following lines to visualize the stock metric data
    """
    # stock_metric_visualiser: StockMetricVisualisationComponent = StockMetricVisualisationComponent(daily_ohlcv_store)
    
    # stock_metric_visualiser.plot_change_in_metric_of_all_instruments(
    #     cumulative=False,
    #     # title="Daily returns",
    #     # ylabel="Daily returns"
    # )
    # stock_metric_visualiser.plot_change_in_metric_of_instrument(
    #     instrument_symbol='RELIANCE.BSE',
    #     cumulative=True,
    #     # title="Cumulative daily returns",
    #     # ylabel="Cumulative daily returns"
    # )
    # stock_metric_visualiser.bar_average_change_in_main_metric(
    #     # title="Average daily returns",
    #     # ylabel="Daily returns"
    # )
    # stock_metric_visualiser.bar_volatility_of_main_metric(
    #     # title="Market volatility",
    #     # ylabel="Daily returns"
    # )
    # stock_metric_visualiser.double_bar_volatility_and_average_of_change_in_main_metric(
    #     # title="Average daily returns alongside volatility",
    #     # ylabel="Standard deviation of daily returns"
    # )

    stock_technicals: dict[str, StockTechnicalIndicationComponent] = {}
    for i in range(len(instrument_symbols)):
        stock_technicals[instrument_symbols[i]] = StockTechnicalIndicationComponent(
            financial_data_store=daily_ohlcv_store,
            instrument_symbol=instrument_symbols[i]
        )


    for symbol, stock_technical in stock_technicals.items():
        stock_technical.macd()#.plot_macd()
        stock_technical.atr()#.plot_atr()
        stock_technical.bollinger_bands()#.plot_bollinger_bands(should_plot_band_width=False)
        stock_technical.rsi()#.plot_rsi()
        stock_technical.adx().plot_adx()

        print(f"Indicator-Augmented Dataframe for {symbol}:")
        print(stock_technical.collect())
