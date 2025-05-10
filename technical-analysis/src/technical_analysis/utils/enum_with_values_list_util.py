from enum import Enum

class EnumWithValuesList(Enum):
    """
    A class that provides a list of enum values for a given enum class.
    """

    @classmethod
    def values(cls):
        """
        Returns a list of enum values for the given enum class.

        :param enum_class: The enum class to get the values from.
        :return: A list of enum values.
        """
        return [item.value for item in cls]