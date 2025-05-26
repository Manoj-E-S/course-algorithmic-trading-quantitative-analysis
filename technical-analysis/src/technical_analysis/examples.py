from technical_analysis.visualization.uni_instrument import InstrumentCharter
from technical_analysis.visualization.multi_instrument import InstrumentGroupVisualizer
from technical_analysis.caching.response_cacher import ResponseCacher
from technical_analysis.indicators.technichart import TechniCharter
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.api_dataframing import ApiDataframingServiceEnum
from technical_analysis.models.candlesticks import Candlesticks
from technical_analysis.models.instrument_group import InstrumentGroup
from technical_analysis.models.renko import Renko


if __name__ == "__main__":

    """
    Setup cache outdation threshold period
    """
    ResponseCacher().set_cache_threshold_period(5)
    print(f"API Response Cache threshold period set to {ResponseCacher().get_cache_threshold_period()}")


    """
    Setup data
    """
    # main_metric: OHLCVUDEnum = OHLCVUDEnum.CLOSE
    candle_span: CandlespanEnum = CandlespanEnum.WEEKLY
    na_strategy: str = 'backfill'

    # Uncomment below line for all valid instrument symbols
    instrument_symbols: list[str] = ['RELIANCE.BSE', 'HDFCBANK.BSE', 'ICICIBANK.BSE', 'SBIN.BSE', 'TATAMOTORS.BSE', 'ITC.BSE']

    # Uncomment below line for one invalid instrument symbol (ahbgd) in instrument_symbols
    # instrument_symbols: list[str] = ['RELIANCE.BSE', 'HDFCBANK.BSE', 'ICICIBANK.BSE', 'SBIN.BSE', 'TATAMOTORS.BSE', 'ITC.BSE', 'XYZ', 'ahbgd']

    daily_indian_instruments_group: InstrumentGroup = InstrumentGroup(
        instrument_symbols=instrument_symbols,
        candle_span=candle_span,
        source_api_class_for_dataframing=ApiDataframingServiceEnum.ALPHA_VANTAGE,
        na_strategy=na_strategy
    )


    """
    Uncomment below line to verify that invalid instruments are dropped by the InstrumentGroup
    """
    # print(daily_indian_instruments_group.instrument_symbols)

    """
    Uncomment below line to verify some dataframes from the InstrumentGroup
    """
    # # Returns DataFrames
    # print(daily_indian_instruments_group.closes_df)
    # print(daily_indian_instruments_group.returns_df)
    # print(daily_indian_instruments_group.cumulative_returns_df)

    # # Volume DataFrames
    # print(daily_indian_instruments_group.volume_df)
    # print(daily_indian_instruments_group.volume_change_df)
    # print(daily_indian_instruments_group.cumulative_volume_change_df)

    # # Applying moving operations on the InstrumentGroup
    # print(
    #     daily_indian_instruments_group.apply_exponential_moving_operation(
    #         on_which_data='returns', 
    #         which_operation='mean', 
    #         window=10,
    #         min_periods=10
    #     )
    # )
    # print(
    #     daily_indian_instruments_group.apply_simple_moving_operation(
    #         on_which_data='cumulative_returns',
    #         which_operation='mean',
    #         window=10
    #     )
    # )

    """
    Uncomment the following lines to see the usage of InstrumentGroupVisualizer
    """
    # daily_indian_instrument_group_visualizer: InstrumentGroupVisualizer = InstrumentGroupVisualizer(daily_indian_instruments_group)
    
    # daily_indian_instrument_group_visualizer.plot_returns_of_all_instruments(
    #     cumulative=False,
    #     # title="Daily returns",
    #     # ylabel="Daily returns"
    # )
    # daily_indian_instrument_group_visualizer.plot_returns_of_instrument(
    #     instrument_symbol='RELIANCE.BSE',
    #     cumulative=True,
    #     # title="Cumulative daily returns",
    #     # ylabel="Cumulative daily returns"
    # )
    # daily_indian_instrument_group_visualizer.bar_average_returns(
    #     # title="Average daily returns",
    #     # ylabel="Daily returns"
    # )
    # daily_indian_instrument_group_visualizer.bar_average_volume_change(
    #     # title="Average daily returns",
    #     # ylabel="Daily returns"
    # )
    # daily_indian_instrument_group_visualizer.bar_instrument_volatility(
    #     # title="Market volatility",
    #     # ylabel="Daily returns"
    # )
    # daily_indian_instrument_group_visualizer.double_bar_volatility_and_average_returns(
    #     # title="Average daily returns alongside volatility",
    #     # ylabel="Standard deviation of daily returns"
    # )


    """
    Uncomment the following lines to see usage of TechniCharter
    """
    # candlesticks: list[Candlesticks] = [Candlesticks(instrument_symbol, candle_span, ApiDataframingServiceEnum.ALPHA_VANTAGE) for instrument_symbol in instrument_symbols]
    
    # technical_indicators: dict[str, TechniCharter] = {}
    # for candlestick in candlesticks:
    #     technical_indicators[candlestick.instrument_symbol] = TechniCharter(candlestick)

    # for symbol, technical_indicator in technical_indicators.items():
    #     technical_indicator.macd().plot_macd()
    #     technical_indicator.atr().plot_atr()
    #     technical_indicator.bollinger_bands().plot_bollinger_bands(should_plot_band_width=False)
    #     technical_indicator.rsi().plot_rsi()
    #     technical_indicator.adx().plot_adx()

    #     print(f"Indicator-Augmented Dataframe for {symbol}:")
    #     print(technical_indicator.collect_as_dataframe())


    """
    Uncomment the following lines to see usage of InstrumentCharter
    """
    # pricer_charter: InstrumentCharter = InstrumentCharter(candlesticks[0])
    # pricer_charter.plot_price_line()
    # pricer_charter.plot_volume_bar()


    """
    Uncomment the following lines to see usage of RenkoChartComponent
    """
    renko: Renko = Renko(
        instrument_symbol='RELIANCE.BSE',
        source_candle_span=CandlespanEnum.DAILY,
        source_api_class_for_dataframing=ApiDataframingServiceEnum.ALPHA_VANTAGE,
        brick_size_from_atr_of=(CandlespanEnum.DAILY, 300),
        # brick_size=100
    )
    print(f"Renko Brick Size: {renko.brick_size}")
    print(f"Renko DataFrame:\n{renko.get_renko()}")