import pandas as pd


class DataFrameDateIndexHelper:
    """
    A helper class for working with date indices in pandas DataFrames.
    """

    def __init__(self):
        pass


    @staticmethod
    def get_years_between_date_indices(
        df_with_datetime_index: pd.DataFrame,
        start_date_idx: int = 0,
        end_date_idx: int = -1
    ) -> float:
        """
        Get the number of years between two date indices in the DataFrame.

        :param df_with_datetime_index: The DataFrame containing the instrument data.
        :type df_with_datetime_index: pd.DataFrame

        :param candle_span: The candle span of the instrument (e.g., daily, weekly, monthly).
        :type candle_span: CandlespanEnum
        
        :param start_date_idx: The index of the start date in the DataFrame. Default is 0.
        :type start_date_idx: int
        
        :param end_date_idx: The index of the end date in the DataFrame. Default is -1 (last index).
        :type end_date_idx: int
        
        :return: The number of years between the two dates as a float.
        :rtype: float
        """
        start_date: pd.Timestamp = df_with_datetime_index.index[start_date_idx]
        end_date: pd.Timestamp = df_with_datetime_index.index[end_date_idx]

        if start_date > end_date:
            raise ValueError("start_date cannot be later than end_date.")

        if start_date == end_date:
            return 0.0

        return (end_date - start_date).days / 252


    @staticmethod
    def resolve_date_range_to_idx_range(
        df_with_datetime_index: pd.DataFrame,
        from_date: pd.Timestamp | None = None,
        until_date: pd.Timestamp | None = None
    ) -> tuple[int, int]:
        """
        Convert a date to its index in the DataFrame that has pd.Timestamp as its index type.

        :param df_with_datetime_index: A DataFrame.
        :type df_with_datetime_index: pd.DataFrame

        :param from_date: The start date of the range. If None, uses the earliest date.
        :type from_date: pd.Timestamp | None

        :param until_date: The end date of the range. If None, uses the latest date.
        :type until_date: pd.Timestamp | None

        :return: A tuple containing the start and end indices.
        :rtype: tuple[int, int]
        """
        if df_with_datetime_index.index.empty:
            raise ValueError("The DataFrame index is empty. Cannot resolve date range from inexistent DatetimeIndex.")
        
        if from_date is None:
            from_date = DataFrameDateIndexHelper.get_earliest_date(df_with_datetime_index)

        if until_date is None:
            until_date = DataFrameDateIndexHelper.get_latest_date(df_with_datetime_index)

        if from_date > until_date:
            raise ValueError("from_date cannot be later than until_date.")

        # Find the index of the date nearest to until_date
        until_date_idx: int = DataFrameDateIndexHelper.get_nearest_date_idx(df_with_datetime_index, date=until_date)

        # Find the index of the date nearest to from_date
        from_date_idx: int = DataFrameDateIndexHelper.get_nearest_date_idx(df_with_datetime_index, date=from_date)

        # Ensure at least one day range
        if from_date_idx == until_date_idx:
            until_date_idx += 1

        return from_date_idx, until_date_idx
    

    @staticmethod
    def get_earliest_date(df_with_datetime_index: pd.DataFrame) -> pd.Timestamp:
        """
        Get the earliest date in the DataFrame index.

        :param df_with_datetime_index: A DataFrame with a datetime index.
        :type df_with_datetime_index: pd.DataFrame

        :raises ValueError: If the DataFrame is empty.

        :return: The earliest date in the DataFrame index.
        :rtype: pd.Timestamp
        """
        if df_with_datetime_index.index.empty:
            raise ValueError("The DataFrame index is empty. Cannot get earliest date from inexistent DatetimeIndex.")

        return df_with_datetime_index.index.min()


    @staticmethod
    def get_latest_date(df_with_datetime_index: pd.DataFrame) -> pd.Timestamp:
        """
        Get the latest date in the DataFrame index.

        :param df_with_datetime_index: A DataFrame with a datetime index.
        :type df_with_datetime_index: pd.DataFrame

        :raises ValueError: If the DataFrame is empty.

        :return: The latest date in the DataFrame index.
        :rtype: pd.Timestamp
        """
        if df_with_datetime_index.index.empty:
            raise ValueError("The DataFrame index is empty. Cannot get latest date from inexistent DatetimeIndex.")

        return df_with_datetime_index.index.max()


    @staticmethod
    def get_nearest_date(df_with_datetime_index: pd.DataFrame, date: pd.Timestamp) -> pd.Timestamp:
        """
        Get the nearest date in the DataFrame index to the specified date.

        :param df_with_datetime_index: A DataFrame with a datetime index.
        :type df_with_datetime_index: pd.DataFrame

        :param date: The date to find the nearest to.
        :type date: pd.Timestamp

        :return: The nearest date in the DataFrame index.
        :rtype: pd.Timestamp
        """
        return df_with_datetime_index.index[DataFrameDateIndexHelper.get_nearest_date_idx(df_with_datetime_index, date=date)]


    @staticmethod
    def get_nearest_date_idx(df_with_datetime_index: pd.DataFrame, date: pd.Timestamp) -> int:
        """
        Get the index of the nearest date in the DataFrame index to the specified date.

        :param df_with_datetime_index: A DataFrame with a datetime index.
        :type df_with_datetime_index: pd.DataFrame

        :param date: The date to find the nearest to.
        :type date: pd.Timestamp

        :raises ValueError: If the DataFrame is empty or if the date is not present in the index.

        :return: The index of the nearest date in the DataFrame index.
        :rtype: int
        """
        if df_with_datetime_index.index.empty:
            raise ValueError("The DataFrame index is empty. Cannot resolve date range from inexistent DatetimeIndex.")

        df_with_datetime_index = df_with_datetime_index.sort_index()
        idx: int = df_with_datetime_index.index.get_indexer([date], method='nearest')[0]
        if idx == -1:
            err: str = f"{date} is not present in the DataFrame index."
            raise ValueError(err)
        
        return idx