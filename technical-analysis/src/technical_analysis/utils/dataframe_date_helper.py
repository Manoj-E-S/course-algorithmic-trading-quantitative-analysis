import pandas as pd


class DataFrameDateIndexHelper:
    """
    A helper class for working with date indices in pandas DataFrames.
    """

    def __init__(self):
        pass


    @staticmethod
    def resolve_date_range_to_idx_range(
        df: pd.DataFrame,
        from_date: pd.Timestamp | None = None,
        until_date: pd.Timestamp | None = None
    ) -> tuple[int, int]:
        """
        Convert a date to its index in the DataFrame that has pd.Timestamp as its index type.

        :param df: A DataFrame.
        :type df: pd.DataFrame

        :param from_date: The start date of the range. If None, uses the earliest date.
        :type from_date: pd.Timestamp | None

        :param until_date: The end date of the range. If None, uses the latest date.
        :type until_date: pd.Timestamp | None

        :return: A tuple containing the start and end indices.
        :rtype: tuple[int, int]
        """
        if df.index.empty:
            raise ValueError("The DataFrame index is empty. Cannot resolve date range from inexistent DatetimeIndex.")
        
        if from_date is None:
            from_date = DataFrameDateIndexHelper.get_earliest_date(df)

        if until_date is None:
            until_date = DataFrameDateIndexHelper.get_latest_date(df)

        if from_date > until_date:
            raise ValueError("from_date cannot be later than until_date.")

        # Find the index of the date nearest to until_date
        until_date_idx: int = DataFrameDateIndexHelper.get_nearest_date_idx(df, date=until_date)

        # Find the index of the date nearest to from_date
        from_date_idx: int = DataFrameDateIndexHelper.get_nearest_date_idx(df, date=from_date)

        # Ensure at least one day range
        if from_date_idx == until_date_idx:
            until_date_idx += 1

        return from_date_idx, until_date_idx
    

    @staticmethod
    def get_earliest_date(df: pd.DataFrame) -> pd.Timestamp:
        """
        Get the earliest date in the DataFrame index.

        :param df: A DataFrame with a datetime index.
        :type df: pd.DataFrame

        :raises ValueError: If the DataFrame is empty.

        :return: The earliest date in the DataFrame index.
        :rtype: pd.Timestamp
        """
        if df.index.empty:
            raise ValueError("The DataFrame index is empty. Cannot resolve date range from inexistent DatetimeIndex.")
        
        return df.index.min()
    

    @staticmethod
    def get_latest_date(df: pd.DataFrame) -> pd.Timestamp:
        """
        Get the latest date in the DataFrame index.

        :param df: A DataFrame with a datetime index.
        :type df: pd.DataFrame

        :raises ValueError: If the DataFrame is empty.

        :return: The latest date in the DataFrame index.
        :rtype: pd.Timestamp
        """
        if df.index.empty:
            raise ValueError("The DataFrame index is empty. Cannot resolve date range from inexistent DatetimeIndex.")
        
        return df.index.max()
    

    @staticmethod
    def get_nearest_date(df: pd.DataFrame, date: pd.Timestamp) -> pd.Timestamp:
        """
        Get the nearest date in the DataFrame index to the specified date.

        :param df: A DataFrame with a datetime index.
        :type df: pd.DataFrame

        :param date: The date to find the nearest to.
        :type date: pd.Timestamp

        :return: The nearest date in the DataFrame index.
        :rtype: pd.Timestamp
        """
        return df.index[DataFrameDateIndexHelper.get_nearest_date_idx(df, date=date)]
    

    @staticmethod
    def get_nearest_date_idx(df: pd.DataFrame, date: pd.Timestamp) -> int:
        """
        Get the index of the nearest date in the DataFrame index to the specified date.

        :param df: A DataFrame with a datetime index.
        :type df: pd.DataFrame

        :param date: The date to find the nearest to.
        :type date: pd.Timestamp

        :raises ValueError: If the DataFrame is empty or if the date is not present in the index.

        :return: The index of the nearest date in the DataFrame index.
        :rtype: int
        """
        if df.index.empty:
            raise ValueError("The DataFrame index is empty. Cannot resolve date range from inexistent DatetimeIndex.")
        
        df = df.sort_index()
        idx: int = df.index.get_indexer([date], method='nearest')[0]
        if idx == -1:
            err: str = f"{date} is not present in the DataFrame index."
            raise ValueError(err)
        
        return idx