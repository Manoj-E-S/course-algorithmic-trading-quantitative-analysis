from technical_analysis.providers.data_cleaning import DataCleaningProvider
from technical_analysis.providers.data_view import DataViewProvider
from technical_analysis.kpis.instrument_kpi import InstrumentKPI
from technical_analysis.visualization.instrument_group_kpi_plotter import InstrumentGroupKpiPlotter
from technical_analysis.visualization.instrument_indicators_plotter import InstrumentIndicatorsPlotter
from technical_analysis.visualization.instrument_plotter import InstrumentPlotter
from technical_analysis.visualization.instrument_group_plotter import InstrumentGroupPlotter
from technical_analysis.caching.response_cacher import ResponseCacher
from technical_analysis.indicators.instrument_indicators import InstrumentIndicators
from technical_analysis.enums.candlespan import CandlespanEnum
from technical_analysis.enums.api_source import ApiSourceEnum
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
    # print(daily_indian_instruments_group.candle_span.value)

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
    Uncomment the following lines to see the usage of InstrumentGroupPlotter
    """
    # daily_indian_instrument_group_visualizer: InstrumentGroupPlotter = InstrumentGroupPlotter(daily_indian_instruments_group)
    
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
    Uncomment the following lines to see usage of InstrumentIndicators and InstrumentKPI
    """
    technical_indicators_for_all_instruments: dict[str, InstrumentIndicators] = {}
    technical_indicator_plotters: dict[str, InstrumentIndicatorsPlotter] = {}
    kpis_for_all_instruments: dict[str, InstrumentKPI] = {}


    # With Candlesticks as the Instrument
    for candlestick in daily_indian_instruments_group.as_candlesticks().values():
        technical_indicators_for_all_instruments[candlestick.instrument_symbol] = InstrumentIndicators(candlestick)
        technical_indicator_plotters[candlestick.instrument_symbol] = InstrumentIndicatorsPlotter(candlestick)
        kpis_for_all_instruments[candlestick.instrument_symbol] = InstrumentKPI(candlestick)

    for symbol, technical_indicator in technical_indicators_for_all_instruments.items():
        technical_indicator.macd()
        technical_indicator.atr()
        technical_indicator.bollinger_bands()
        technical_indicator.rsi()
        technical_indicator.adx()
        print(f"Indicator-Augmented Dataframe for {symbol}:")
        print(technical_indicators_for_all_instruments[symbol].collect_as_dataframe())

    # for symbol, technical_indicator_plotter in technical_indicator_plotters.items():
    #     technical_indicator_plotter.plot_macd()
    #     technical_indicator_plotter.plot_atr()
    #     technical_indicator_plotter.plot_bollinger_bands(should_plot_band_width=False)
    #     technical_indicator_plotter.plot_rsi()
    #     technical_indicator_plotter.plot_adx()

    for symbol, kpi in kpis_for_all_instruments.items():
        print()
        print(f"Instrument Symbol: {symbol}, Candle Span: {kpi.instrument.candle_span.value}")
        print("==============================================================")
        print(f"CAGR: {kpi.cagr()}")
        print(f"Volatility: {kpi.annualized_volatility()}")
        print(f"Sharpe Ratio: {kpi.sharpe_ratio(risk_free_rate=0.06)}")
        print(f"Sortino Ratio: {kpi.sortino_ratio(risk_free_rate=0.06)}")
        print(f"Max Drawdown: {kpi.max_drawdown()}")
        print(f"Calmar Ratio: {kpi.calmar_ratio()}")
        print()


    # With Renko as the Instrument
    for renko in daily_indian_instruments_group.as_renkos(brick_size_from_atr=brick_size_from_atr).values():
        technical_indicators_for_all_instruments[renko.instrument_symbol] = InstrumentIndicators(renko)
        technical_indicator_plotters[renko.instrument_symbol] = InstrumentIndicatorsPlotter(renko)
        kpis_for_all_instruments[renko.instrument_symbol] = InstrumentKPI(renko)

    for symbol, technical_indicator in technical_indicators_for_all_instruments.items():
        technical_indicator.macd()
        technical_indicator.atr()
        technical_indicator.bollinger_bands()
        technical_indicator.rsi()
        technical_indicator.adx()
        print(f"Indicator-Augmented Dataframe for {symbol}:")
        print(technical_indicators_for_all_instruments[symbol].collect_as_dataframe())

    # for symbol, technical_indicator_plotter in technical_indicator_plotters.items():
    #     technical_indicator_plotter.plot_macd()
    #     technical_indicator_plotter.plot_atr()
    #     technical_indicator_plotter.plot_bollinger_bands(should_plot_band_width=False)
    #     technical_indicator_plotter.plot_rsi()
    #     technical_indicator_plotter.plot_adx()
    
    for symbol, kpi in kpis_for_all_instruments.items():
        print()
        print(f"Instrument Symbol: {symbol}, Candle Span: {kpi.instrument.candle_span.value}")
        print("==============================================================")
        print(f"CAGR: {kpi.cagr()}")
        print(f"Volatility: {kpi.annualized_volatility()}")
        print(f"Sharpe Ratio: {kpi.sharpe_ratio(risk_free_rate=0.06)}")
        print(f"Sortino Ratio: {kpi.sortino_ratio(risk_free_rate=0.06)}")
        print(f"Max Drawdown: {kpi.max_drawdown()}")
        print(f"Calmar Ratio: {kpi.calmar_ratio()}")
        print()


    """
    Uncomment the following lines to see usage of follInstrumentGroupKpiPlotter
    """
    # instrument_group_kpi_plotter = InstrumentGroupKpiPlotter(daily_indian_instruments_group)
    # instrument_group_kpi_plotter.plot_cagrs()
    # instrument_group_kpi_plotter.plot_volatilities()
    # instrument_group_kpi_plotter.plot_cagr_vs_volatility()
    # instrument_group_kpi_plotter.plot_sharpe_ratios()
    # instrument_group_kpi_plotter.plot_sortino_ratios()
    # instrument_group_kpi_plotter.plot_max_drawdowns()
    # instrument_group_kpi_plotter.plot_calmar_ratios()

    """
    Uncomment the following lines to see usage of InstrumentPlotter
    """
    # instrument_plotters: dict[str, InstrumentPlotter] = {}


    # # With Candlesticks as the Instrument
    # for candlestick in daily_indian_instruments_group.as_candlesticks().values():
    #     instrument_plotters[candlestick.instrument_symbol] = InstrumentPlotter(candlestick)

    # for symbol, charter in instrument_plotters.items():
    #     charter.plot_price_line()
    #     charter.plot_volume_bar()


    # # With Renko as the Instrument  
    # for renko in daily_indian_instruments_group.as_renkos(brick_size=brick_size).values():
    #     instrument_plotters[renko.instrument_symbol] = InstrumentPlotter(renko)

    # for symbol, charter in instrument_plotters.items():
    #     charter.plot_price_line()
    #     # TODO: Extend Volume support to Renko
    #     # charter.plot_volume_bar()


    """
    Uncomment the following lines to see usage of Renko
    """
    # renko: Renko = Renko(
    #     instrument_symbol='RELIANCE.BSE',
    #     source_candle_span=CandlespanEnum.DAILY,
    #     data_view_provider=common_data_view_provider,
    #     brick_size_from_atr=brick_size_from_atr,
    #     # brick_size=brick_size
    # )
    # print(f"Renko Instrument Symbol: {renko.instrument_symbol}")
    # print(f"Renko Brick Size: {renko.brick_size}")
    # print(f"Renko DataFrame:\n{renko.renko_df}")