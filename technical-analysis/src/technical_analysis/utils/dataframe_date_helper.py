import pandas as pd
from technical_analysis.enums.candlespan import CandlespanEnum


class DataFrameDateIndexHelper:
    """
    A helper class for working with date indices in pandas DataFrames.
    """

    def __init__(self):
        pass


    @staticmethod
    def get_years_between_date_indices(
        datetime_index: pd.DatetimeIndex,
        row_span: CandlespanEnum,
        start_date_idx: int = 0,
        end_date_idx: int = -1
    ) -> float:
        """
        Get the number of years between two date indices in the DataFrame.

        :param datetime_index: The DatetimeIndex of the dataframe containing the instrument data.
        :type datetime_index: pd.DatetimeIndex

        :param row_span: The candle span of the instrument (e.g., daily, weekly, monthly).
        :type row_span: CandlespanEnum
        
        :param start_date_idx: The index of the start date in the DataFrame. Default is 0.
        :type start_date_idx: int
        
        :param end_date_idx: The index of the end date in the DataFrame. Default is -1 (last index).
        :type end_date_idx: int
        
        :return: The number of years between the two dates as a float.
        :rtype: float
        """
        start_date: pd.Timestamp = datetime_index[start_date_idx]
        end_date: pd.Timestamp = datetime_index[end_date_idx]

        if start_date > end_date:
            raise ValueError("start_date cannot be later than end_date.")

        if start_date == end_date:
            return 0.0

        periods_per_year: int = CandlespanEnum.periods_per_year(row_span)
        
        return len(datetime_index[start_date_idx:end_date_idx + 1]) / periods_per_year


    @staticmethod
    def next_date(
        datetime_index: pd.DatetimeIndex,
        date: pd.Timestamp
    ) -> pd.Timestamp:
        """
        Get the next date after the specified date in the DataFrame that has pd.Timestamp as its index type.

        :param datetime_index: A DataFrame.
        :type datetime_index: pd.DataFrame

        :param date: The date to find the next index for.
        :type date: pd.Timestamp

        :return: The index of the next date after the specified date.
        :rtype: int

        :raises IndexError: If there is no next date after the specified date in the DataFrame index.
        """
        current_date_index: int = DataFrameDateIndexHelper.get_nearest_date_idx(datetime_index, date=date)

        if current_date_index + 1 >= len(datetime_index):
            raise IndexError("There is no next date after the specified date in the DataFrame index.")

        return datetime_index[current_date_index + 1]


    @staticmethod
    def resolve_date_range_to_idx_range(
        datetime_index: pd.DatetimeIndex,
        from_date: pd.Timestamp | None = None,
        until_date: pd.Timestamp | None = None
    ) -> tuple[int, int]:
        """
        Convert a date to its index in the DataFrame that has pd.Timestamp as its index type.

        :param datetime_index: A DatetimeIndex.
        :type datetime_index: pd.DatetimeIndex

        :param from_date: The start date of the range. If None, uses the earliest date.
        :type from_date: pd.Timestamp | None

        :param until_date: The end date of the range. If None, uses the latest date.
        :type until_date: pd.Timestamp | None

        :return: A tuple containing the start and end indices.
        :rtype: tuple[int, int]
        """
        if datetime_index.empty:
            raise ValueError("The DataFrame index is empty. Cannot resolve date range from inexistent DatetimeIndex.")
        
        if from_date is None:
            from_date = DataFrameDateIndexHelper.get_earliest_date(datetime_index)

        if until_date is None:
            until_date = DataFrameDateIndexHelper.get_latest_date(datetime_index)

        if from_date > until_date:
            raise ValueError("from_date cannot be later than until_date.")

        # Find the index of the date nearest to until_date
        until_date_idx: int = DataFrameDateIndexHelper.get_nearest_date_idx(datetime_index, date=until_date)

        # Find the index of the date nearest to from_date
        from_date_idx: int = DataFrameDateIndexHelper.get_nearest_date_idx(datetime_index, date=from_date)

        return from_date_idx, until_date_idx
    

    @staticmethod
    def get_earliest_date(datetime_index: pd.DatetimeIndex) -> pd.Timestamp:
        """
        Get the earliest date in the DataFrame index.

        :param datetime_index: A datetime index.
        :type datetime_index: pd.DatetimeIndex

        :raises ValueError: If the DataFrame is empty.

        :return: The earliest date in the DataFrame index.
        :rtype: pd.Timestamp
        """
        if datetime_index.empty:
            raise ValueError("The DataFrame index is empty. Cannot get earliest date from inexistent DatetimeIndex.")

        return datetime_index.min()


    @staticmethod
    def get_latest_date(datetime_index: pd.DatetimeIndex) -> pd.Timestamp:
        """
        Get the latest date in the DataFrame index.

        :param datetime_index: A datetime index.
        :type datetime_index: pd.DatetimeIndex

        :raises ValueError: If the DataFrame is empty.

        :return: The latest date in the DataFrame index.
        :rtype: pd.Timestamp
        """
        if datetime_index.empty:
            raise ValueError("The DataFrame index is empty. Cannot get latest date from inexistent DatetimeIndex.")

        return datetime_index.max()


    @staticmethod
    def get_nearest_date(datetime_index: pd.DatetimeIndex, date: pd.Timestamp) -> pd.Timestamp:
        """
        Get the nearest date in the DataFrame index to the specified date.

        :param datetime_index: A datetime index.
        :type datetime_index: pd.DatetimeIndex

        :param date: The date to find the nearest to.
        :type date: pd.Timestamp

        :return: The nearest date in the DataFrame index.
        :rtype: pd.Timestamp
        """
        return datetime_index[DataFrameDateIndexHelper.get_nearest_date_idx(datetime_index, date=date)]


    @staticmethod
    def get_nearest_date_idx(datetime_index: pd.DatetimeIndex, date: pd.Timestamp) -> int:
        """
        Get the index of the nearest date in the DataFrame index to the specified date.

        :param datetime_index: A datetime index.
        :type datetime_index: pd.DatetimeIndex

        :param date: The date to find the nearest to.
        :type date: pd.Timestamp

        :raises ValueError: If the DataFrame is empty or if the date is not present in the index.

        :return: The index of the nearest date in the DataFrame index.
        :rtype: int
        """
        if datetime_index.empty:
            raise ValueError("The DataFrame index is empty. Cannot resolve date range from inexistent DatetimeIndex.")

        datetime_index = datetime_index.sort_values()
        idx: int = datetime_index.get_indexer([date], method='nearest')[0]
        if idx == -1:
            err: str = f"{date} is not present in the DataFrame index."
            raise ValueError(err)
        
        return idx