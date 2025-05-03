import os

from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), '..', '.env'))

class AuthService:
    """
    A class to manage authentication for API requests.
    """

    def __init__(self):
        pass


    @staticmethod
    def __get_auth_token() -> str | None:
        """
        Returns the authentication token for API requests.

        Returns:
            str: The authentication token.
        """
        return os.environ.get("indian_stock_market_api_key", None)
    

    @staticmethod
    def get_auth_header() -> dict:
        """
        Returns the authentication header for API requests.

        Returns:
            dict: The authentication header.
        
        Raises:
            ValueError: If the authentication token is not set in the environment variables.
        """
        if not AuthService.__get_auth_token():
            raise ValueError("Authentication token is not set in the environment variables.")

        return {
            "X-Api-Key": f"{AuthService.__get_auth_token()}"
        }