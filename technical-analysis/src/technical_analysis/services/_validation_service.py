from requests import Response

class ValidationService:
    """
    A Class to validate API responses
    """

    def __init__(self):
        pass


    @staticmethod
    def is_status_code_ok(response: Response) -> bool:
        """
        Checks if the response returned with a status code 200 OK

        Args:
            response(requests.Response): the API response to be validated

        Returns:
            bool: True if response OK, False otherwise
        """
        if response.status_code != 200:
            print(f"[ERROR] API Responded with Status Code: {response.status_code}")
            response.raise_for_status()
            return False

        return True
    

    @staticmethod
    def does_json_exist(response: Response) -> bool:
        """
        Checks if the response.json() returns a non-empty dictionary if it is decodable

        Args:
            response(requests.Response): the API response to be validated

        Returns:
            bool: True if response.json() is decodable and a non-empty dictionary, False otherwise
        """
        try:
            data = response.json()
            if isinstance(data, dict) and data:  # ensure data is a non-empty dictionary
                print("[SUCCESS] API Response JSON obtained successfully")
                return True
            elif not data:
                print("[ERROR] Response JSON is empty.")
            else:
                print("[ERROR] Response JSON is not a dict.")
        except ValueError as e:
            print("[ERROR] Failed to decode Response JSON\n", str(e))

        return False