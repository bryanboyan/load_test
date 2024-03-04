from abc import abstractmethod
import csv
from queue import Queue
from threading import Thread, Event
from time import time, sleep
from tests.Logger import Logger
import traceback

DATA_FOLDER = "data"
FLAG_FINISHED = "FINISHED"

log = Logger("Metrics").log

class RecorderBase(Thread):
    """Base class for threaded recorders with queue and stop event"""
    def __init__(self, request_name: str):
        super().__init__()
        self.request_name = request_name
        self.stop_event = Event()
        self.queue = Queue()

    @abstractmethod
    def filename(self) -> str:
        pass

    def run(self):
        log(f"Starting thread {self.name} for {self.__class__.__name__}")
        with open(self.filename(), "w") as file:
            writer = csv.writer(file, delimiter=',')
            while not self.stop_event.is_set():
                try:
                    row = self.queue.get()
                    if row is FLAG_FINISHED:
                        break
                    writer.writerow(row)
                    file.flush()
                    self.queue.task_done()
                except Exception as e:
                    log(f"Error in {self.__class__.__name__}: {str(e)}")
                    file.close()
                    break
        log(f"Wrapped up class {self.__class__.__name__}, thread name {self.name}")

    def stop(self):
        self.stop_event.set()

    def enqueue(self, elems: list):
        self.queue.put(elems)

    def log_finished(self):
        self.queue.put(FLAG_FINISHED)


class RequestRecorder(RecorderBase):
    """Recorder thread to record the load change of load-tests"""

    def filename(self) -> str:
        return f"{DATA_FOLDER}/request_{self.request_name}.csv"

    def log_request(self):
        self.enqueue([time()])


class ResponseRecorder(RecorderBase):
    """Recorder thread to record the metrics of the request."""

    def filename(self) -> str:
        return f"{DATA_FOLDER}/response_{self.request_name}.csv"

    def log_result(self, time: float, request_time: float):
        self.enqueue([time, "success", request_time])

    def log_failure(self, time: float, status_code: int):
        self.enqueue([time, "failure", status_code])


class Metrics:
    """Singleton class to manage different types of recorders."""
    def __init__(self):
        self.request_recorders = {}
        self.response_recorders = {}

    def init_recorders(self, request_name: str) -> None:
        if request_name not in self.request_recorders:
            self.request_recorders[request_name] = RequestRecorder(request_name)
            self.request_recorders[request_name].start()
            self.response_recorders[request_name] = ResponseRecorder(request_name)
            self.response_recorders[request_name].start()

    def get_response_recorder(self, request_name: str) -> ResponseRecorder:
        return self.response_recorders[request_name]

    def get_request_recorder(self, request_name: str) -> RequestRecorder:
        return self.request_recorders[request_name]

    def terminate(self):
        for thread in self.request_recorders.values():
            thread.log_finished()
            thread.stop()
            thread.join()
        for thread in self.response_recorders.values():
            thread.log_finished()
            thread.stop()
            thread.join()

metrics = Metrics()
