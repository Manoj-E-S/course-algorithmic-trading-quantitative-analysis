from technical_analysis.providers.data_cleaning import DataCleaningProvider
from technical_analysis.providers.data_view import DataViewProvider
from technical_analysis.visualization.kpis import InstrumentKPIs
from technical_analysis.visualization.uni_instrument import InstrumentCharter
from technical_analysis.visualization.multi_instrument import InstrumentGroupVisualizer
from technical_analysis.caching.response_cacher import ResponseCacher
from technical_analysis.visualization.technical_indicators import TechniCharter
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.api_source import ApiSourceEnum
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
    candle_span: CandlespanEnum = CandlespanEnum.DAILY
    na_strategy: str = 'backfill'

    brick_size_from_atr: tuple[CandlespanEnum, int] = (CandlespanEnum.DAILY, 300)
    brick_size: int = 100

    # Uncomment below line for all valid instrument symbols
    instrument_symbols: list[str] = ['RELIANCE.BSE', 'HDFCBANK.BSE', 'ICICIBANK.BSE', 'SBIN.BSE', 'TATAMOTORS.BSE', 'ITC.BSE']

    # Uncomment below line for one invalid instrument symbol (ahbgd) in instrument_symbols
    # instrument_symbols: list[str] = ['RELIANCE.BSE', 'HDFCBANK.BSE', 'ICICIBANK.BSE', 'SBIN.BSE', 'TATAMOTORS.BSE', 'ITC.BSE', 'XYZ', 'ahbgd']

    common_data_view_provider: DataViewProvider = DataViewProvider(
        on_which_api_source=ApiSourceEnum.ALPHA_VANTAGE,
        data_cleaning_provider=DataCleaningProvider(na_strategy=na_strategy)
    )

    daily_indian_instruments_group: InstrumentGroup = InstrumentGroup(
        instrument_symbols=instrument_symbols,
        candle_span=candle_span,
        data_view_provider=common_data_view_provider
    )


    """
    Uncomment below line to verify configurational properties of InstrumentGroup
    """
    # print(daily_indian_instruments_group.instrument_symbols)
    # print(daily_indian_instruments_group.candle_span)

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
    Uncomment the following lines to see usage of TechniCharter and InstrumentKPIs
    """
    # technical_indicators_for_all_instruments: dict[str, TechniCharter] = {}
    # kpis_for_all_instruments: dict[str, InstrumentKPIs] = {}


    # # With Candlesticks as the Instrument
    # for candlestick in daily_indian_instruments_group.as_candlesticks().values():
    #     technical_indicators_for_all_instruments[candlestick.instrument_symbol] = TechniCharter(candlestick)
    #     kpis_for_all_instruments[candlestick.instrument_symbol] = InstrumentKPIs(candlestick)

    # for symbol, technical_indicator in technical_indicators_for_all_instruments.items():
    #     technical_indicator.macd().plot_macd()
    #     technical_indicator.atr().plot_atr()
    #     technical_indicator.bollinger_bands().plot_bollinger_bands(should_plot_band_width=False)
    #     technical_indicator.rsi().plot_rsi()
    #     technical_indicator.adx().plot_adx()

    #     print(f"Indicator-Augmented Dataframe for {symbol}:")
    #     print(technical_indicators_for_all_instruments[symbol].collect_as_dataframe())

    # for symbol, kpi in kpis_for_all_instruments.items():
    #     print(f"CAGR for {symbol}: {kpi.cagr()}")


    # # With Renko as the Instrument
    # for renko in daily_indian_instruments_group.as_renkos(brick_size_from_atr=brick_size_from_atr).values():
    #     technical_indicators_for_all_instruments[renko.instrument_symbol] = TechniCharter(renko)
    #     kpis_for_all_instruments[renko.instrument_symbol] = InstrumentKPIs(renko)

    # for symbol, technical_indicator in technical_indicators_for_all_instruments.items():
    #     technical_indicator.macd().plot_macd()
    #     technical_indicator.atr().plot_atr()
    #     technical_indicator.bollinger_bands().plot_bollinger_bands(should_plot_band_width=False)
    #     technical_indicator.rsi().plot_rsi()
    #     technical_indicator.adx().plot_adx()

    #     print(f"Indicator-Augmented Dataframe for {symbol}:")
    #     print(technical_indicators_for_all_instruments[symbol].collect_as_dataframe())
    
    # for symbol, kpi in kpis_for_all_instruments.items():
    #     print(f"CAGR for {symbol}: {kpi.cagr()}")



    """
    Uncomment the following lines to see usage of InstrumentCharter
    """
    # instrument_charters: dict[str, InstrumentCharter] = {}


    # # With Candlesticks as the Instrument
    # for candlestick in daily_indian_instruments_group.as_candlesticks().values():
    #     instrument_charters[candlestick.instrument_symbol] = InstrumentCharter(candlestick)

    # for symbol, charter in instrument_charters.items():
    #     charter.plot_price_line()
    #     charter.plot_volume_bar()


    # # With Renko as the Instrument  
    # for renko in daily_indian_instruments_group.as_renkos(brick_size=brick_size).values():
    #     instrument_charters[renko.instrument_symbol] = InstrumentCharter(renko)

    # for symbol, charter in instrument_charters.items():
    #     charter.plot_price_line()
    #     # TODO: Extend Volume support to Renko
    #     # charter.plot_volume_bar()


    """
    Uncomment the following lines to see usage of Renko
    """
    renko: Renko = Renko(
        instrument_symbol='RELIANCE.BSE',
        source_candle_span=CandlespanEnum.DAILY,
        data_view_provider=common_data_view_provider,
        brick_size_from_atr=brick_size_from_atr,
        # brick_size=brick_size
    )
    print(f"Renko Instrument Symbol: {renko.instrument_symbol}")
    print(f"Renko Brick Size: {renko.brick_size}")
    print(f"Renko DataFrame:\n{renko.get_renko()}")