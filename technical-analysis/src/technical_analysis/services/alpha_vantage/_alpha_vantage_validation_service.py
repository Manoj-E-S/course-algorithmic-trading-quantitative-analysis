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
        for k, v in response_json.items():
            if "info" in k.lower() or "note" in k.lower():
                if "limit" in v.lower():
                    return True
        return False