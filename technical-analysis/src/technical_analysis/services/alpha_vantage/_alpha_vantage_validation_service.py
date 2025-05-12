class AlphaVantageValidationService:
    """
    A Class to validate API responses specific to alpha vantage api.

    This was created to handle the peculiarities of the alpha vantage api :)
    For instance, the alpha vantage api responds with status code 200 OK, even when api response is an ERROR Response
    """

    def __init__(self):
        pass


    @staticmethod
    def does_response_json_have_error_message(response_json: dict) -> bool:
        """
        :Scenario handled:
        Alpha vantage api responds with status code 200 OK, even when api response is an ERROR Response :)
        """
        if any(["error" in key.lower() for key in response_json.keys()]):
            return True
        return False
    

    @staticmethod
    def does_response_json_have_api_limit_message(response_json: dict) -> bool:
        """
        :Scenario handled:
        Alpha vantage api responds with status code 200 OK, even when api response is an INFO Response relating to the daily api request limit :)
        """
        if any(["limit" in value.lower() for value in response_json.values()]) or any(["note" in key.lower() for key in response_json.keys()]):
            return True
        return False