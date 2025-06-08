from technical_analysis.providers.data_view import DataViewProvider
from technical_analysis.utils.singleton import SingletonMeta


class GlobalDataViewConfig(metaclass=SingletonMeta):
    """
    Global Data View configuration class for technical analysis.
    """


    def __init__(
        self,
        data_view_provider: DataViewProvider | None = None
    ):
        """
        Initializes the global configuration with the specified parameters.

        :param data_view_provider: The data view provider instance.
        :type data_view_provider: DataViewProvider
        """
        self.__data_view_provider: DataViewProvider | None = data_view_provider


    # Getters
    def get(self) -> DataViewProvider | None:
        return self.__data_view_provider
    

    # Setters
    def set(self, data_view_provider: DataViewProvider) -> 'GlobalDataViewConfig':
        if not isinstance(data_view_provider, (DataViewProvider, None)):
            raise TypeError("data_view_provider must be an instance of DataViewProvider or None.")
        
        self.__data_view_provider = data_view_provider
        return self
    

    # Reset Methods
    def reset(self) -> 'GlobalDataViewConfig':
        self.__data_view_provider = None
        return self

