from pathlib import Path
from typing import List, TypedDict
import yaml

class RequestDefinition(TypedDict):
    url: str
    method: str

class ScheduleShape(TypedDict):
    time: int
    threads: int
    ramp: int

file_path = Path(__file__).parent.parent / "config.yaml"

class Config:
    def __init__(self):
        with open(file_path, "r") as file:
            config_data = yaml.safe_load(file)
        self.tasks = config_data["tasks"]
        self.requests = config_data["requests"]
        self.shapes = config_data["shapes"]
        self.logging = config_data.get("logging", dict())
        self.config_data = config_data

        # sanity check configs
        for req in self.tasks:
            assert req in self.requests, f"Request {req} not found in requests"
            assert req in self.shapes, f"Request {req} not found in shapes"

    def get_tasks(self) -> List[str]:
        return self.tasks

    def get_request(self, request_name) -> RequestDefinition:
        return self.requests[request_name]

    def get_schedule_shape(self, request_name) -> List[ScheduleShape]:
        return self.shapes[request_name]['shape']

    def get_request_interval_ms(self, request_name) -> int:
        return self.shapes[request_name]["interval_ms"]

    def is_actor_muted(self, actor) -> bool:
        if self.logging.get('allowed_actors'):
            return actor not in self.logging['allowed_actors']
        return False

config = Config()
