from tests.Config import config
import requests


class Request:
    def __init__(self, request_name: str):
        self.request_name = request_name
        request_obj = config.get_request(request_name)
        self.method = request_obj["method"]
        self.url = request_obj["url"]
        self.params = request_obj.get("params")

    def name(self) -> str:
        return self.request_name

    def send(self) -> requests.Response:
        if self.method == "GET":
            return requests.get(self.url, params=self.params)
        elif self.method == "POST":
            return requests.post(self.url, json=self.params)
        else:
            raise ValueError(f"Unsupported method {self.method}")
