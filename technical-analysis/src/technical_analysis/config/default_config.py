import datetime
import os


class DefaultConfigConstants:
    """
    Default configuration values for the application.
    """
    # Project root directory
    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    
    # Default Cache configuration values
    DEFAULT_RESPONSE_CACHE_DIR: str = os.path.join(PROJECT_ROOT, "response_cache")
    DEFAULT_CACHE_THRESHOLD_PERIOD_DAYS: datetime.timedelta = datetime.timedelta(days=5)
