import datetime
import os
import json
import time

from technical_analysis.enums.api import APIEnum
from technical_analysis.utils.singleton import SingletonMeta


class ResponseCacher(metaclass=SingletonMeta):
    """
    A component to cache API responses of APIs
    """

    RESPONSE_CACHE_DIR: str = os.path.join(os.getcwd(), "response_cache")
    CACHE_THRESHOLD_PERIOD: datetime.timedelta = datetime.timedelta(days=5)


    def __init__(self):
        pass


    def get_cache_threshold_period(self) -> datetime.timedelta:
        return self.CACHE_THRESHOLD_PERIOD

    def set_cache_threshold_period(self, cache_threshold_period_days: int) -> None:
        self.CACHE_THRESHOLD_PERIOD = datetime.timedelta(days=cache_threshold_period_days)


    def cache_response_data(
        self,
        which_api: APIEnum,
        which_instrument: str,
        response_data: dict,
        indent: int = 4
    ) -> None:
        """
        Writes response data into a json file

        Args:
            which_api(APIEnum): The response is from which API
            which_instrument(str): Which istrument's api_response is being stored
            response_data(dict): api_response.json()
            indent(int): json file indent number, defaults to 4
        """
        api_dir: str = f"{which_api.value.split('.')[0]}"
        dir_for_response_file: str = f"{which_instrument.lower().replace(' ', '_').replace('.', '_').replace(':', '_')}"
        response_file_name: str = f"{which_api.value.split('.')[1]}_response.json"

        response_file_path = os.path.join(self.RESPONSE_CACHE_DIR, api_dir, dir_for_response_file, response_file_name)

        os.makedirs(os.path.dirname(response_file_path), exist_ok=True)
        with open(response_file_path, 'w') as f:
            json.dump(response_data, f, indent=indent)

        print(f"[INFO] Cached response data at {response_file_path}")


    def is_response_data_cached(
        self,
        which_api: APIEnum,
        which_instrument: str
    ) -> bool:
        """
        Checks if given api response data is already present in the response cache directory

        Args:
            which_api(APIEnum): The response from which API is to be searched
            which_instrument(str): Which istrument's api_response is being searched

        Returns:
            bool: True if the response for that instrument is cached and the caching happend within the cache's threshold period, False otherwise
        """
        api_dir: str = f"{which_api.value.split('.')[0]}"
        dir_for_response_file: str = f"{which_instrument.lower().replace(' ', '_').replace('.', '_').replace(':', '_')}"
        response_file_name: str = f"{which_api.value.split('.')[1]}_response.json"

        response_file_path = os.path.join(self.RESPONSE_CACHE_DIR, api_dir, dir_for_response_file, response_file_name)

        if not os.path.exists(response_file_path):
            return False
        
        modified_time: float = os.path.getmtime(response_file_path)
        time_elapsed_since_last_modification = datetime.timedelta(seconds=(time.time() - modified_time))
        return time_elapsed_since_last_modification <= self.CACHE_THRESHOLD_PERIOD
            

    def retrieve_from_cache(
        self,
        which_api: APIEnum,
        which_instrument: str
    ) -> dict | None:
        """
        Retrieves a given response data if it is already present in the response cache directory

        Args:
            which_api(APIEnum): The response from which API is to be searched
            which_instrument(str): Which istrument's api_response is being searched

        Returns:
            dict | None: api_response.json() if cached, None otherwise
        """
        if not self.is_response_data_cached(which_api, which_instrument):
            print(f"[INFO] {which_api.value} API data is not cached...")
            return
        
        api_dir: str = f"{which_api.value.split('.')[0]}"
        dir_for_response_file: str = f"{which_instrument.lower().replace(' ', '_').replace('.', '_').replace(':', '_')}"
        response_file_name: str = f"{which_api.value.split('.')[1]}_response.json"

        retrieval_file_path: str = os.path.join(self.RESPONSE_CACHE_DIR, api_dir, dir_for_response_file, response_file_name)

        cached_instrument: dict = {}
        with open(retrieval_file_path, 'r') as f:
            cached_instrument = json.load(f)

        return cached_instrument
