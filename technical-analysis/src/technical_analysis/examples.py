from datetime import datetime
from pprint import pprint
import pandas as pd
from technical_analysis.config.data_view_config import GlobalDataViewConfig
from technical_analysis.enums.ohlcvud import OHLCVUDEnum
from technical_analysis.models.candlesticks import Candlesticks
from technical_analysis.models.instrument import Instrument
from technical_analysis.models.instrument_universe import InstrumentUniverse
from technical_analysis.models.portfolio import Portfolio
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


class DefaultConstants:
    """
    Constants for example usage of the technical analysis library.
    """
    API_SOURCE: ApiSourceEnum = ApiSourceEnum.ALPHA_VANTAGE
    BRICK_SIZE: int = 100
    BRICK_SIZE_FROM_ATR: tuple[CandlespanEnum, int] = (CandlespanEnum.DAILY, 300)
    CACHE_OUTDATION_PERIOD_DAYS: int = 5
    CANDLE_SPAN: CandlespanEnum = CandlespanEnum.DAILY
    SAMPLE_INSTRUMENT: str = 'RELIANCE.BSE'
    NA_STRATEGY: str = 'backfill'
    RISK_FREE_RATE: float = 0.06  # 6% annual risk-free rate
    
    INSTRUMENT_SYMBOLS: list[str] = [
        'RELIANCE.BSE', 'HDFCBANK.BSE', 'ICICIBANK.BSE', 'SBIN.BSE', 'TATAMOTORS.BSE', 'ITC.BSE'
    ]
    INSTRUMENT_SYMBOLS_WITH_INVALID: list[str] = [
        'RELIANCE.BSE', 'HDFCBANK.BSE', 'ICICIBANK.BSE', 'SBIN.BSE', 'TATAMOTORS.BSE', 'ITC.BSE', 'XYZ', 'ahbgd'
    ]
    NIFTY_50_UNIVERSE: list[str] = [
        'RELIANCE.BSE',
        'HDFCBANK.BSE',
        'TCS.BSE',
        'BHARTIARTL.BSE',
        'ICICIBANK.BSE',
        'SBIN.BSE',
        'INFY.BSE',
        'BAJFINANCE.BSE',
        'HINDUNILVR.BSE',
        'ITC.BSE',
        'LT.BSE',
        'HCLTECH.BSE',
        'KOTAKBANK.BSE',
        'SUNPHARMA.BSE',
        'MARUTI.BSE',
        'M&M.BSE',
        'AXISBANK.BSE',
        'ULTRACEMCO.BSE',
        'NTPC.BSE', # 532555.BSE
        'BAJAJFINSV.BSE',
        'ADANIPORTS.BSE',
        'TITAN.BSE',
        'ONGC.BSE',
        'ADANIENT.BSE',
        # Bharat Electronics: BHARATELE.BSE,
        'POWERGRID.BSE',
        'TATAMOTORS.BSE',
        'WIPRO.BSE', # 507685.BSE
        # Eternal (Zomato): ZOMATO.BSE,
        'COALINDIA.BSE', # 533278.BSE
        'JSWSTEEL.BSE', # 500228.BSE
        'BAJAJ-AUTO.BSE', # 532977.BSE
        'NESTLEIND.BSE', # 500790.BSE
        'ASIANPAINT.BSE',
        'TRENT.BSE',
        'TATASTEEL.BSE',
        # Jio Financial Serv.: JIOFINANCIAL.BSE,
        'SBILIFE.BSE',
        'GRASIM.BSE', # 500300.BSE
        'HDFCLIFE.BSE',
        'TECHM.BSE',
        'EICHERMOT.BSE', # 505200.BSE
        'HINDALCO.BSE',
        'SHRIRAMFIN.BSE',
        'CIPLA.BSE', # 500087.BSE
        'TATACONSUM.BSE', # 500800.BSE
        # Dr Reddy's Labs: DR_REDDYS_LABS.BSE,
        'APOLLOHOSP.BSE',
        'HEROMOTOCO.BSE',
        'INDUSINDBK.BSE', 
    ]


def default_data_cleaning_provider() -> DataCleaningProvider:
    """
    Returns a default DataCleaningProvider with the NA strategy set to default NA Strategy.
    """
    return DataCleaningProvider(na_strategy=DefaultConstants.NA_STRATEGY)


def default_data_view_provider() -> DataViewProvider:
    """
    Returns a default DataViewProvider with the API source set to default API Source and the default DataCleaningProvider.
    """
    return DataViewProvider(
        on_which_api_source=DefaultConstants.API_SOURCE,
        data_cleaning_provider=default_data_cleaning_provider()
    )


def default_instrument_group() -> InstrumentGroup:
    """
    Returns a default InstrumentGroup with the instrument symbols set to default instrument symbols,
    the candle span set to default candle span, and the data view provider set to default data view provider.
    """
    return InstrumentGroup(
        instrument_symbols=DefaultConstants.INSTRUMENT_SYMBOLS,
        candle_span=DefaultConstants.CANDLE_SPAN,
    )


def default_renko(
    from_atr: bool,
    instrument_symbol: str = DefaultConstants.SAMPLE_INSTRUMENT,
    candle_span: CandlespanEnum = DefaultConstants.CANDLE_SPAN,
    brick_size_from_atr: tuple[CandlespanEnum, int] = DefaultConstants.BRICK_SIZE_FROM_ATR,
    brick_size: int = DefaultConstants.BRICK_SIZE
) -> Renko:
    """
    Returns a default Renko instrument with the given parameters.
    If from_atr is True, it uses the brick size from ATR, otherwise it uses the fixed brick size.
    """
    if from_atr:
        return Renko(
            instrument_symbol=instrument_symbol,
            source_candle_span=candle_span,
            brick_size_from_atr=brick_size_from_atr
        )
    else:
        return Renko(
            instrument_symbol=instrument_symbol,
            source_candle_span=candle_span,
            brick_size=brick_size
        )
    

def default_candlesticks(
    instrument_symbol: str = DefaultConstants.SAMPLE_INSTRUMENT,
    candle_span: CandlespanEnum = DefaultConstants.CANDLE_SPAN,
) -> Candlesticks:
    """
    Returns a default Candlesticks instrument with the given parameters.
    """
    return Candlesticks(
        instrument_symbol=instrument_symbol,
        source_candle_span=candle_span,
    )


def setup_response_caching():
    """
    Setup cache outdation threshold period
    """
    ResponseCacher().set_cache_threshold_period(DefaultConstants.CACHE_OUTDATION_PERIOD_DAYS)
    print(f"API Response Cache threshold period set to {ResponseCacher().get_cache_threshold_period()}")


def configure_data_view_provider_globally():
    """
    Setup the global data view config with the default DataViewProvider.
    """
    GlobalDataViewConfig(default_data_view_provider())


def configure_risk_free_rate_globally(risk_free_rate: float | None = None):
    """
    Configure the global risk-free rate.
    This is used in financial calculations like Sharpe Ratio and Sortino Ratio.
    """
    from technical_analysis.config.risk_free_rate_config import GlobalRiskFreeRateConfig
    GlobalRiskFreeRateConfig.set(risk_free_rate or DefaultConstants.RISK_FREE_RATE)
    print(f"Global Risk-Free Rate set to {GlobalRiskFreeRateConfig.get()}")


def example_usage_instrument_group(
    instruments_group: InstrumentGroup | None = None
):
    """
    Example usage of the InstrumentGroup with daily Indian instruments.
    """
    if instruments_group is None:
        instruments_group = default_instrument_group()

    # Returns DataFrames
    print(instruments_group.closes_df)
    print(instruments_group.returns_df)
    print(instruments_group.cumulative_returns_df)

    # Volume DataFrames
    print(instruments_group.volume_df)
    print(instruments_group.volume_change_df)
    print(instruments_group.cumulative_volume_change_df)

    # Applying moving operations on the InstrumentGroup
    print(
        instruments_group.apply_exponential_moving_operation(
            on_which_data='returns', 
            which_operation='mean', 
            window=10,
            min_periods=10
        )
    )
    print(
        instruments_group.apply_simple_moving_operation(
            on_which_data='cumulative_returns',
            which_operation='mean',
            window=10
        )
    )


def example_usage_instrument_group_plotter(
    instruments_group: InstrumentGroup | None = None
):
    """
    Example usage of the InstrumentGroupPlotter with daily Indian instruments.
    """
    if instruments_group is None:
        instruments_group = default_instrument_group()

    instrument_group_plotter = InstrumentGroupPlotter(instruments_group)
    
    # Plotting returns of all instruments
    instrument_group_plotter.plot_returns_of_all_instruments(
        cumulative=True,
        title="Daily Returns",
        ylabel="Daily Returns"
    )
    
    # Plotting returns of a specific instrument
    instrument_group_plotter.plot_returns_of_instrument(
        instrument_symbol='RELIANCE.BSE',
        cumulative=False,
        title="Cumulative Daily Returns",
        ylabel="Cumulative Daily Returns"
    )
    
    # Bar plots for average returns and volume change
    instrument_group_plotter.bar_average_returns(
        title="Average Daily Returns",
        ylabel="Daily Returns"
    )
    
    instrument_group_plotter.bar_average_volume_change(
        title="Average Daily Volume Change",
        ylabel="Volume Change"
    )
    
    # Bar plot for market volatility
    instrument_group_plotter.bar_instrument_volatility(
        title="Market Volatility",
        ylabel="Volatility (Standard Deviation of Daily Returns)"
    )
    
    # Double bar plot for volatility and average returns
    instrument_group_plotter.double_bar_volatility_and_average_returns(
        title="Average Daily Returns alongside Volatility",
        ylabel="Standard Deviation of Daily Returns"
    )


def example_usage_candlestick_instrument_indicators(
    instrument_group: InstrumentGroup | None = None
):
    """
    Example usage of the InstrumentIndicators
    """
    if instrument_group is None:
        instrument_group = default_instrument_group()

    indicators: dict[str, InstrumentIndicators] = {}

    for candlestick in instrument_group.as_candlesticks().values():
        indicators[candlestick.instrument_symbol] = InstrumentIndicators(candlestick)

    for indicator in indicators.values():
        indicator.macd().atr().bollinger_bands().rsi().adx()
        print(f"Indicator-Augmented Dataframe for {indicator.instrument.instrument_symbol}:")
        print(indicator.collect_as_dataframe())


def example_usage_renko_instrument_indicators(
    from_atr: bool,
    brick_size_from_atr: tuple[CandlespanEnum, int] = DefaultConstants.BRICK_SIZE_FROM_ATR,
    brick_size: int = DefaultConstants.BRICK_SIZE,
    instrument_group: InstrumentGroup | None = None
):
    """
    Example usage of the InstrumentIndicators
    """
    if instrument_group is None:
        instrument_group = default_instrument_group()
    
    indicators: dict[str, InstrumentIndicators] = {}

    if from_atr:
        # Using brick size from ATR
        for renko in instrument_group.as_renkos(brick_size_from_atr=brick_size_from_atr).values():
            indicators[renko.instrument_symbol] = InstrumentIndicators(renko)
    else:
        # Using fixed brick size
        for renko in instrument_group.as_renkos(brick_size=brick_size).values():
            indicators[renko.instrument_symbol] = InstrumentIndicators(renko)

    for indicator in indicators.values():
        indicator.macd().atr().bollinger_bands().rsi().adx()
        print(f"Indicator-Augmented Dataframe for {indicator.instrument.instrument_symbol}:")
        print(indicator.collect_as_dataframe())


def example_usage_candlestick_instrument_indicator_plotter(
    instrument_group: InstrumentGroup | None = None
):
    """
    Example usage of the InstrumentPlotter
    """
    if instrument_group is None:
        instrument_group = default_instrument_group()

    indicator_plotters: dict[str, InstrumentIndicatorsPlotter] = {}

    for candlestick in instrument_group.as_candlesticks().values():
        indicator_plotters[candlestick.instrument_symbol] = InstrumentIndicatorsPlotter(candlestick)

    for indicator_plotter in indicator_plotters.values():
        indicator_plotter.plot_macd()
        indicator_plotter.plot_atr()
        indicator_plotter.plot_bollinger_bands(should_plot_band_width=False)
        indicator_plotter.plot_rsi()
        indicator_plotter.plot_adx()


def example_usage_renko_instrument_indicator_plotter(
    from_atr: bool,
    brick_size_from_atr: tuple[CandlespanEnum, int] = DefaultConstants.BRICK_SIZE_FROM_ATR,
    brick_size: int = DefaultConstants.BRICK_SIZE,
    instrument_group: InstrumentGroup | None = None
):
    """
    Example usage of the InstrumentPlotter
    """
    if instrument_group is None:
        instrument_group = default_instrument_group()

    indicator_plotters: dict[str, InstrumentIndicatorsPlotter] = {}

    if from_atr:
        # Using brick size from ATR
        for renko in instrument_group.as_renkos(brick_size_from_atr=brick_size_from_atr).values():
            indicator_plotters[renko.instrument_symbol] = InstrumentIndicatorsPlotter(renko)
    else:
        # Using fixed brick size
        for renko in instrument_group.as_renkos(brick_size=brick_size).values():
            indicator_plotters[renko.instrument_symbol] = InstrumentIndicatorsPlotter(renko)

    for indicator_plotter in indicator_plotters.values():
        indicator_plotter.plot_macd()
        indicator_plotter.plot_atr()
        indicator_plotter.plot_bollinger_bands(should_plot_band_width=False)
        indicator_plotter.plot_rsi()
        indicator_plotter.plot_adx()


def example_usage_candlestick_instrument_kpi(
    instrument_group: InstrumentGroup | None = None
):
    """
    Example usage of the InstrumentKPI
    """
    if instrument_group is None:
        instrument_group = default_instrument_group()

    kpis: dict[str, InstrumentKPI] = {}

    for candlestick in instrument_group.as_candlesticks().values():
        kpis[candlestick.instrument_symbol] = InstrumentKPI(candlestick)

    for kpi in kpis.values():
        print()
        print(f"Instrument Symbol: {kpi.instrument.instrument_symbol}, Candle Span: {kpi.instrument.candle_span.value}")
        print("==============================================================")
        print(f"CAGR: {kpi.cagr()}")
        print(f"Volatility: {kpi.annualized_volatility()}")
        print(f"Sharpe Ratio: {kpi.sharpe_ratio(risk_free_rate=0.06)}")
        print(f"Sortino Ratio: {kpi.sortino_ratio(risk_free_rate=0.06)}")
        print(f"Max Drawdown: {kpi.max_drawdown()}")
        print(f"Calmar Ratio: {kpi.calmar_ratio()}")
        print()


def example_usage_renko_instrument_kpi(
    from_atr: bool,
    brick_size_from_atr: tuple[CandlespanEnum, int] = DefaultConstants.BRICK_SIZE_FROM_ATR,
    brick_size: int = DefaultConstants.BRICK_SIZE,
    instrument_group: InstrumentGroup | None = None
):
    """
    Example usage of the InstrumentKPI
    """
    if instrument_group is None:
        instrument_group = default_instrument_group()

    kpis: dict[str, InstrumentKPI] = {}

    if from_atr:
        # Using brick size from ATR
        for renko in instrument_group.as_renkos(brick_size_from_atr=brick_size_from_atr).values():
            kpis[renko.instrument_symbol] = InstrumentKPI(renko)
    else:
        # Using fixed brick size
        for renko in instrument_group.as_renkos(brick_size=brick_size).values():
            kpis[renko.instrument_symbol] = InstrumentKPI(renko)

    for kpi in kpis.values():
        print()
        print(f"Instrument Symbol: {kpi.instrument.instrument_symbol}, Candle Span: {kpi.instrument.candle_span.value}")
        print("==============================================================")
        print(f"CAGR: {kpi.cagr()}")
        print(f"Volatility: {kpi.annualized_volatility()}")
        print(f"Sharpe Ratio: {kpi.sharpe_ratio(risk_free_rate=0.06)}")
        print(f"Sortino Ratio: {kpi.sortino_ratio(risk_free_rate=0.06)}")
        print(f"Max Drawdown: {kpi.max_drawdown()}")
        print(f"Calmar Ratio: {kpi.calmar_ratio()}")
        print()


def example_usage_instrument_group_kpi(
    instrument_group: InstrumentGroup | None = None
):
    """
    Example usage of the InstrumentGroupKpiPlotter
    """
    if instrument_group is None:
        instrument_group = default_instrument_group()

    instrument_group_kpi_plotter = InstrumentGroupKpiPlotter(instrument_group)
    instrument_group_kpi_plotter.plot_cagrs()
    instrument_group_kpi_plotter.plot_volatilities()
    instrument_group_kpi_plotter.plot_cagr_vs_volatility()
    instrument_group_kpi_plotter.plot_sharpe_ratios()
    instrument_group_kpi_plotter.plot_sortino_ratios()
    instrument_group_kpi_plotter.plot_max_drawdowns()
    instrument_group_kpi_plotter.plot_calmar_ratios()


def example_usage_candlestick_instrument_plotter(
    instrument_group: InstrumentGroup | None = None
):
    """
    Example usage of the InstrumentPlotter
    """
    if instrument_group is None:
        instrument_group = default_instrument_group()

    for candlestick in instrument_group.as_candlesticks().values():
        instrument_plotter = InstrumentPlotter(candlestick)

        # Plotting price line
        instrument_plotter.plot_price_line(
            # title="Price Line"
        )

        # Plotting volume bar
        instrument_plotter.plot_volume_bar(
            # title="Volume Bar"
        )


def example_usage_renko_instrument_plotter(
    from_atr: bool,
    brick_size_from_atr: tuple[CandlespanEnum, int] = DefaultConstants.BRICK_SIZE_FROM_ATR,
    brick_size: int = DefaultConstants.BRICK_SIZE,
    instrument_group: InstrumentGroup | None = None
):
    """
    Example usage of the InstrumentPlotter for Renko instruments
    """
    if instrument_group is None:
        instrument_group = default_instrument_group()

    if from_atr:
        # Using brick size from ATR
        renkos = instrument_group.as_renkos(brick_size_from_atr=brick_size_from_atr).values()
    else:
        # Using fixed brick size
        renkos = instrument_group.as_renkos(brick_size=brick_size).values()
    
    for renko in renkos:
        instrument_plotter = InstrumentPlotter(renko)

        # Plotting price line
        instrument_plotter.plot_price_line(
            # title="Price Line",
        )

        # TODO: Extend Volume support to Renko
        # instrument_plotter.plot_volume_bar(
        #     # title="Volume Bar",
        # )


def example_usage_renko_dataframe(
    from_atr: bool,
    instrument_symbol: str = DefaultConstants.SAMPLE_INSTRUMENT,
    candle_span: CandlespanEnum = DefaultConstants.CANDLE_SPAN,
    brick_size_from_atr: tuple[CandlespanEnum, int] = DefaultConstants.BRICK_SIZE_FROM_ATR,
    brick_size: int = DefaultConstants.BRICK_SIZE,
):
    """
    Example usage of the Renko DataFrame
    """
    renko: Renko = default_renko(
        from_atr=from_atr,
        instrument_symbol=instrument_symbol,
        candle_span=candle_span,
        brick_size_from_atr=brick_size_from_atr,
        brick_size=brick_size,
    )
    
    print(f"Renko Instrument Symbol: {renko.instrument_symbol}")
    print(f"Renko Brick Size: {renko.brick_size}")
    print(f"Renko DataFrame:\n{renko.renko_df}")



if __name__ == "__main__":
    """
    Configure the global data view provider and response caching.
    """
    setup_response_caching()
    configure_data_view_provider_globally()
    configure_risk_free_rate_globally()

    """
    Some default constants for example usage.
    """
    instrument: str = DefaultConstants.SAMPLE_INSTRUMENT
    ig: InstrumentGroup = default_instrument_group()
    brick_size_from_atr: tuple[CandlespanEnum, int] = DefaultConstants.BRICK_SIZE_FROM_ATR
    brick_size: int = DefaultConstants.BRICK_SIZE

    """
    InstrumentGroup and its Plotter
    """
    # example_usage_instrument_group(ig)
    # example_usage_instrument_group_plotter(ig)


    """
    Individual Instrument Plotters
    """
    # example_usage_candlestick_instrument_plotter(ig)
    # example_usage_renko_instrument_plotter(from_atr=True, brick_size_from_atr=brick_size_from_atr, instrument_group=ig)
    # example_usage_renko_instrument_plotter(from_atr=False, brick_size=brick_size, instrument_group=ig)


    """
    Individual Instrument Indicators and their Plotters
    """
    # example_usage_candlestick_instrument_indicators(ig)
    # example_usage_candlestick_instrument_indicator_plotter(ig)

    # example_usage_renko_instrument_indicators(from_atr=True, brick_size_from_atr=brick_size_from_atr, instrument_group=ig)
    # example_usage_renko_instrument_indicator_plotter(from_atr=True, brick_size_from_atr=brick_size_from_atr, instrument_group=ig)
    
    # example_usage_renko_instrument_indicators(from_atr=False, brick_size=brick_size, instrument_group=ig)
    # example_usage_renko_instrument_indicator_plotter(from_atr=False, brick_size=brick_size, instrument_group=ig)


    """
    Individual Instrument KPIs
    """
    # example_usage_candlestick_instrument_kpi(ig)
    # example_usage_renko_instrument_kpi(from_atr=True, brick_size_from_atr=brick_size_from_atr, instrument_group=ig)
    # example_usage_renko_instrument_kpi(from_atr=False, brick_size=brick_size, instrument_group=ig)
    

    """
    Instrument Group KPIs
    """
    # example_usage_instrument_group_kpi(ig)


    """
    Renko Bricks Dataframe Example
    """
    # example_usage_renko_dataframe(from_atr=True, brick_size_from_atr=brick_size_from_atr)
    # example_usage_renko_dataframe(from_atr=False, brick_size=brick_size)


    """
    Portfolio and Instrument Universe
    """
    nifty_50_index: Instrument = Instrument(
        instrument_symbol='NIFTYBEES.BSE',
        candle_span=CandlespanEnum.MONTHLY
    )

    sensex_30_index: Instrument = Instrument(
        instrument_symbol='SENSEXBEES.BSE',
        candle_span=CandlespanEnum.MONTHLY
    )

    nifty_50_universe = InstrumentUniverse(
        instrument_symbols=DefaultConstants.NIFTY_50_UNIVERSE,
        candle_span=CandlespanEnum.MONTHLY
    )

    start_time = datetime.now()
    print(f"Start Time: {start_time}")
    portfolio = Portfolio(
        number_of_holdings=10,
        source_universe=nifty_50_universe,
        # optimization_strategy='rebalancing',
        # start_date=datetime(2023, 10, 1, 0, 0, 0, 0, tzinfo=None),
        # end_date=datetime(2024, 10, 1, 0, 0, 0, 0, tzinfo=None),
        # start_date='earliest',
        # end_date='latest'
    )
    end_time = datetime.now()
    print(f"End Time: {end_time}")
    print(f"Time taken to create portfolio: {end_time - start_time}")

    # print(portfolio._Portfolio__holdings_v_kpis_as_of_date(pd.Timestamp('2023-09-29')))

    print()
    print("Portfolio Start Date:")
    pprint(portfolio.start_date)
    print()
    print("Portfolio End Date:")
    pprint(portfolio.end_date)
    print()
    print("Portfolio Optimization Strategy:")
    pprint(portfolio.optimization_strategy)
    print()
    print("Portfolio Number of Holdings:")
    pprint(portfolio.number_of_holdings)
    print()
    print("Portfolio Current Holdings:")
    pprint(portfolio.current_holdings)
    print()
    print("Portfolio Current Holdings with KPIs:")
    pprint(portfolio.current_holdings_v_kpis)
    print()
    print("Portfolio Holding History:")
    pprint(portfolio.holding_history)
    print()