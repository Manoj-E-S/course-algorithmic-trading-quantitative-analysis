import os
import json

from technical_analysis.models import AlphaVantageEnum, IndianAPIEnum
from technical_analysis.utils import SingletonMeta

class ResponseCacherComponent(metaclass=SingletonMeta):
    """
    A component to interact with the server's file system
    """

    RESPONSE_CACHE_DIR: str = os.path.join(os.getcwd(), "response_cache")

    def __init__(self):
        pass


    @staticmethod
    def cache_response_data(
        which_api: AlphaVantageEnum | IndianAPIEnum,
        which_instrument: str,
        response_data: dict,
        indent: int = 4
    ) -> None:
        """
        Writes response data into a json file

        Args:
            which_api(AlphaVantageEnum | IndianAPIEnum): The response is from which API
            which_instrument(str): Which istrument's api_response is being stored
            response_data(dict): api_response.json()
            indent(int): json file indent number, defaults to 4
        """
        api_dir: str = f"{which_api.value.split('.')[0]}"
        dir_for_response_file: str = f"{which_instrument.lower().replace(' ', '_').replace('.', '_').replace(':', '_')}"
        response_file_name: str = f"{which_api.value.split('.')[1]}_response.json"

        response_file_path = os.path.join(ResponseCacherComponent.RESPONSE_CACHE_DIR, api_dir, dir_for_response_file, response_file_name)

        os.makedirs(os.path.dirname(response_file_path), exist_ok=True)
        with open(response_file_path, 'w') as f:
            json.dump(response_data, f, indent=indent)

        print(f"[INFO] Cached response data at {response_file_path}")

    
    @staticmethod
    def is_response_data_cached(
        which_api: AlphaVantageEnum | IndianAPIEnum,
        which_instrument: str
    ) -> bool:
        """
        Checks if given api response data is already present in the response cache directory

        Args:
            which_api(AlphaVantageEnum | IndianAPIEnum): The response from which API is to be searched
            which_instrument(str): Which istrument's api_response is being searched

        Returns:
            bool: True if the response for that instrument is cached, False otherwise
        """
        api_dir: str = f"{which_api.value.split('.')[0]}"
        dir_for_response_file: str = f"{which_instrument.lower().replace(' ', '_').replace('.', '_').replace(':', '_')}"
        response_file_name: str = f"{which_api.value.split('.')[1]}_response.json"

        response_file_path = os.path.join(ResponseCacherComponent.RESPONSE_CACHE_DIR, api_dir, dir_for_response_file, response_file_name)
        return os.path.exists(response_file_path)
            

    @staticmethod
    def retrieve_from_cache(
        which_api: AlphaVantageEnum | IndianAPIEnum,
        which_instrument: str
    ) -> dict | None:
        """
        Retrieves a given response data if it is already present in the response cache directory

        Args:
            which_api(AlphaVantageEnum | IndianAPIEnum): The response from which API is to be searched
            which_instrument(str): Which istrument's api_response is being searched

        Returns:
            dict | None: api_response.json() if cached, None otherwise
        """
        if not ResponseCacherComponent.is_response_data_cached(which_api, which_instrument):
            print(f"[INFO] {which_api.value} API data is not cached...")
            return
        
        api_dir: str = f"{which_api.value.split('.')[0]}"
        dir_for_response_file: str = f"{which_instrument.lower().replace(' ', '_').replace('.', '_').replace(':', '_')}"
        response_file_name: str = f"{which_api.value.split('.')[1]}_response.json"

        retrieval_file_path: str = os.path.join(ResponseCacherComponent.RESPONSE_CACHE_DIR, api_dir, dir_for_response_file, response_file_name)

        cached_instrument: dict = {}
        with open(retrieval_file_path, 'r') as f:
            cached_instrument = json.load(f)

        return cached_instrument
