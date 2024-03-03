import csv
from queue import Queue
from threading import Thread, Event
from time import time
from tests.Logger import Logger

DATA_FOLDER = "data"
FLAG_FINISHED = "FINISHED"

log = Logger("Metrics").log

class RecorderBase(Thread):
    def __init__(self):
        super().__init__()
        self.stop_event = Event()
        self.queue = Queue()

    def filename(self):
        pass

    def run(self):
        with open(self.filename(), "w") as file:
            writer = csv.writer(file, delimiter=',')
            while not self.stop_event.is_set():
                try:
                    log(f"Waiting for log line in {self.filename()}")
                    line = self.queue.get()
                    if line is FLAG_FINISHED:
                        break
                    writer.writerow(line)
                    file.flush()
                    self.queue.task_done()
                except Exception as e:
                    log(f"Error in {self.__class__.__name__}: {e}")
                    file.close()
                    break
        log(f"Wrapped up file {self.filename()}")

    def stop(self):
        self.stop_event.set()

    def enqueue(self, elems: list):
        self.queue.put(elems)

    def log_finished(self):
        self.queue.put(FLAG_FINISHED)


class LoadRecorder(RecorderBase):
    def __init__(self):
        super().__init__()

    def filename(self):
        return f"{DATA_FOLDER}/load.csv"

    def log_threads(self, request_name: str, current_threads: int):
        self.enqueue([time(), request_name, current_threads])


class MetricRecorder(RecorderBase):
    def __init__(self, request_name: str):
        super().__init__()
        self.request_name = request_name

    def filename(self):
        return f"{DATA_FOLDER}/{self.request_name}.csv"

    def log_result(self, time: float, request_time: float):
        self.enqueue([time, "success", request_time])

    def log_failure(self, time: float, status_code: int):
        self.enqueue([time, "failure", status_code])


class Metrics:
    def __init__(self):
        self.recorders = {}
        self.load_recorder = LoadRecorder()
        self.load_recorder.start()

    def init_recorder(self, request_name: str) -> None:
        if request_name not in self.recorders:
            self.recorders[request_name] = MetricRecorder(request_name)
            self.recorders[request_name].start()

    def get_recorder(self, request_name: str) -> MetricRecorder:
        return self.recorders[request_name]

    def get_load_recorder(self) -> LoadRecorder:
        return self.load_recorder

    def terminate(self):
        for thread in self.recorders.values():
            thread.stop()
            thread.join()
        self.load_recorder.stop()
        self.load_recorder.join()


metrics = Metrics()
