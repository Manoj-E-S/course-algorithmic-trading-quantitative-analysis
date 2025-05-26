import pandas as pd

from technical_analysis.enums.ohlcvud import OHLCVUDEnum


class IndicatorCalculator:
    
    def __init__(self):
        pass

    @staticmethod
    def macd(
        df: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> pd.DataFrame:
        """
        Static method to calculate MACD on a given DataFrame.

        :param df: The DataFrame containing OHLCV data.
        :type df: pd.DataFrame

        :param fast_period: The period for the fast EMA. Default is 12.
        :type fast_period: int

        :param slow_period: The period for the slow EMA. Default is 26.
        :type slow_period: int

        :param signal_period: The period for the signal line. Default is 9.
        :type signal_period: int

        :return: DataFrame with MACD, Signal Line, and Histogram.
        :rtype: pd.DataFrame
        """
        df['fast_ema'] = df[OHLCVUDEnum.CLOSE.value].ewm(span=fast_period, min_periods=fast_period, adjust=False).mean()
        df['slow_ema'] = df[OHLCVUDEnum.CLOSE.value].ewm(span=slow_period, min_periods=slow_period, adjust=False).mean()
        df['macd'] = df['fast_ema'] - df['slow_ema']
        df['macd_signal'] = df['macd'].ewm(span=signal_period, min_periods=signal_period).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        df.drop(columns=['fast_ema', 'slow_ema'], inplace=True)

        return df
    

    @staticmethod
    def atr(
        df: pd.DataFrame,
        window: int = 14
    ) -> pd.DataFrame:
        """
        Static method to calculate ATR on a given DataFrame.

        :param df: The DataFrame containing OHLCV data.
        :type df: pd.DataFrame

        :param window: The period for the ATR calculation. Default is 14.
        :type window: int

        :return: DataFrame with ATR.
        :rtype: pd.DataFrame
        """
        df["H-L"]   = df[OHLCVUDEnum.HIGH.value] - df[OHLCVUDEnum.LOW.value]
        df["H-PC"]  = (df[OHLCVUDEnum.HIGH.value] - df[OHLCVUDEnum.CLOSE.value].shift(1)).abs()
        df["L-PC"]  = (df[OHLCVUDEnum.LOW.value] - df[OHLCVUDEnum.CLOSE.value].shift(1)).abs()
        df["TR"]    = df[["H-L", "H-PC", "L-PC"]].max(axis='columns', skipna=False)
        df["atr"]   = df["TR"].ewm(span=window, min_periods=window).mean()

        df.drop(columns=["H-L", "H-PC", "L-PC", "TR"], inplace=True)

        return df
    

    @staticmethod
    def bollinger_bands(
        df: pd.DataFrame,
        window: int = 20
    ) -> pd.DataFrame:
        """
        Static method to calculate Bollinger Bands on a given DataFrame.

        :param df: The DataFrame containing OHLCV data.
        :type df: pd.DataFrame

        :param window: The period for the SMA for the middle band. Default is 20.
        :type window: int

        :return: DataFrame with Bollinger Bands and Band Width.
        :rtype: pd.DataFrame
        """
        df["middle_boll_band"]  = df[OHLCVUDEnum.CLOSE.value].rolling(window).mean()
        df["upper_boll_band"]   = df["middle_boll_band"] + 2 * df[OHLCVUDEnum.CLOSE.value].rolling(window).std(ddof=0)
        df["lower_boll_band"]   = df["middle_boll_band"] - 2 * df[OHLCVUDEnum.CLOSE.value].rolling(window).std(ddof=0)
        df["band_width"]        = df["upper_boll_band"] - df["lower_boll_band"]

        return df
    

    @staticmethod
    def rsi(
        df: pd.DataFrame,
        window: int = 14
    ) -> pd.DataFrame:
        """
        Static method to calculate RSI on a given DataFrame.

        :param df: The DataFrame containing OHLCV data.
        :type df: pd.DataFrame

        :param window: The period for the RSI calculation. Default is 14.
        :type window: int

        :return: DataFrame with RSI.
        :rtype: pd.DataFrame
        """
        df['close_change']   = df[OHLCVUDEnum.CLOSE.value] - df[OHLCVUDEnum.CLOSE.value].shift(1)
        df['gain']           = df['close_change'].apply(lambda x: x if x >= 0 else 0.0)
        df['loss']           = df['close_change'].apply(lambda x: -x if x < 0 else 0.0)
        df['avg_gain']       = df['gain'].ewm(alpha=(1/window), min_periods=window).mean()
        df['avg_loss']       = df['loss'].ewm(alpha=(1/window), min_periods=window).mean()
        df['rs']             = df['avg_gain'] / df['avg_loss']
        df['rsi']            = 100 - (100 / ( 1 + df['rs']))

        df.drop(columns=['close_change', 'gain', 'loss', 'avg_gain', 'avg_loss', 'rs'], inplace=True)

        return df
    

    @staticmethod
    def adx(
        df: pd.DataFrame,
        window: int = 14
    ) -> pd.DataFrame:
        """
        Static method to calculate ADX on a given DataFrame.

        :param df: The DataFrame containing OHLCV data.
        :type df: pd.DataFrame

        :param window: The period for the ADX calculation. Default is 14.
        :type window: int

        :return: DataFrame with ADX.
        :rtype: pd.DataFrame
        """
        do_not_delete_atr_post_calculation: bool = False
        if 'atr' in df.columns:
            do_not_delete_atr_post_calculation = True
        else:
            df = IndicatorCalculator.atr(df, window)

        df['hh']         = df[OHLCVUDEnum.HIGH.value] - df[OHLCVUDEnum.HIGH.value].shift(1)
        df['ll']         = df[OHLCVUDEnum.LOW.value].shift(1) - df[OHLCVUDEnum.LOW.value]

        df['dm_up']      = df[['hh','ll']].apply(lambda row: max(row['hh'], 0) if row['hh'] > row['ll'] else 0, axis='columns')
        df['dm_down']    = df[['hh','ll']].apply(lambda row: max(row['ll'], 0) if row['ll'] > row['hh'] else 0, axis='columns')

        df['di_up']      = (100/df['atr']) * df['dm_up'].ewm(alpha=(1/window), min_periods=window).mean()
        df['di_down']    = (100/df['atr']) * df['dm_down'].ewm(alpha=(1/window), min_periods=window).mean()

        df['dx']         = ((df['di_up'] - df['di_down']) / (df['di_up'] + df['di_down'])).abs()

        df['adx']        = 100 * df['dx'].ewm(alpha=(1/window), min_periods=window).mean()

        df.drop(columns=['hh', 'll', 'dm_up', 'dm_down', 'di_up', 'di_down', 'dx'], inplace=True)
        if not do_not_delete_atr_post_calculation:
            df.drop(columns=['atr'], inplace=True)

        return df