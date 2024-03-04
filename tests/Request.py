import requests
from tests.Config import config
from tests.Logger import Logger
from typing import Optional

log = Logger("Request").log

class Request:
    """Wrapper of the requests built from config to handle get and post """

    def __init__(self, request_name: str):
        self.request_name = request_name
        request_obj = config.get_request(request_name)
        self.method = request_obj["method"]
        self.url = request_obj["url"]
        self.params = request_obj.get("params")

    def name(self) -> str:
        return self.request_name

    def send(self) -> tuple[Optional[requests.Response], Optional[str]]:
        try:
            if self.method == "GET":
                return requests.get(self.url, params=self.params), None
            elif self.method == "POST":
                return requests.post(self.url, json=self.params), None
            else:
                raise ValueError(f"Unsupported method {self.method}")
        except Exception as ex:
            error_name = type(ex).__name__
            log(f"Request failed for {self.request_name} with error {error_name}")
            return None, error_name
