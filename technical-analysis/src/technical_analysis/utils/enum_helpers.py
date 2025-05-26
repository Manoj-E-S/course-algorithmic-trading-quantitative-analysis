from enum import Enum

class EnumWithValuesList(Enum):
    """
    A class that provides a list of enum values for a given enum class.
    """

    @classmethod
    def values(cls):
        """
        Returns a list of enum values.

        :return: A list of enum values.
        """
        return [item.value for item in cls]