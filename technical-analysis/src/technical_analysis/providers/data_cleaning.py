from typing import Literal

import pandas as pd


class DataCleaningProvider:
    """
    A provider class for data cleaning operations.
    This class is responsible for cleaning and preprocessing data before analysis.
    """

    def __init__(
        self, 
        na_strategy: Literal['drop_index', 'drop_column', 'backfill', 'forwardfill'] = 'backfill'
    ):
        """
        Initializes the DataCleaningProvider with the specified NA strategy.

        :param na_strategy: The strategy to handle null values in the data.
        :type na_strategy: Literal['drop_index', 'drop_column', 'backfill', 'forwardfill']
        """
        self.__na_strategy = na_strategy


    # Getters
    @property
    def na_strategy(self) -> Literal['drop_index', 'drop_column', 'backfill', 'forwardfill']:
        return self.__na_strategy
    

    # Chainable Setter
    @na_strategy.setter
    def na_strategy(self, na_strategy: Literal['drop_index', 'drop_column', 'backfill', 'forwardfill']) -> 'DataCleaningProvider':
        self.__na_strategy = na_strategy
        return self
    
    
    # Public Methods
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the raw data by removing null values.

        :return: Cleaned data.
        """
        return self.__handle_na_by_strategy(df)
    

    # Private Methods
    def __backfillna(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Backfills null values in the DataFrame.
        
        :param df: The DataFrame to clean.
        :type df: pd.DataFrame
        
        :return: The DataFrame with null values backfilled.
        :rtype: pd.DataFrame
        """
        return df.bfill(inplace=False)
    

    def __forwardfillna(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Forward fills null values in the DataFrame.
        
        :param df: The DataFrame to clean.
        :type df: pd.DataFrame
        
        :return: The DataFrame with null values forward filled.
        :rtype: pd.DataFrame
        """
        return df.ffill(inplace=False)

    
    def __dropna_by_index(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Drops rows with null values from the DataFrame.
        
        :param df: The DataFrame to clean.
        :type df: pd.DataFrame
        
        :return: The cleaned DataFrame with rows containing null values removed.
        :rtype: pd.DataFrame
        """
        return df.dropna(axis='index', inplace=False)
    

    def __dropna_by_column(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Drops columns with null values from the DataFrame.
        
        :param df: The DataFrame to clean.
        :type df: pd.DataFrame
        
        :return: The cleaned DataFrame with columns containing null values removed.
        :rtype: pd.DataFrame
        """
        return df.dropna(axis='columns', inplace=False)
    

    def __handle_na_by_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handles null values in the DataFrame based on the specified NA strategy.
        
        :param df: The DataFrame to clean.
        :type df: pd.DataFrame
        
        :return: The cleaned DataFrame.
        :rtype: pd.DataFrame
        """
        if self.__na_strategy == 'backfill':
            df = self.__backfillna(df)
        elif self.__na_strategy == 'forwardfill':
            df = self.__forwardfillna(df)
        elif self.__na_strategy == 'drop_index':
            df = self.__dropna_by_index(df)
        elif self.__na_strategy == 'drop_column':
            df = self.__dropna_by_column(df)

        return df