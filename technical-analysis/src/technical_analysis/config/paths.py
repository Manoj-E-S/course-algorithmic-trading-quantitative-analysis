import os

class PathConfigurations:
    """
    Paths class to manage file paths for technical analysis data.
    """

    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))