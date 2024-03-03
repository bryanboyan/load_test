from queue import Queue
from threading import Thread, Event
from time import time

DATA_FOLDER = "data"
FLAG_FINISHED = "FINISHED"


class RecorderBase(Thread):
    def __init__(self):
        super().__init__()
        self.stop_event = Event()
        self.queue = Queue()

    def filename(self):
        pass
    
    def run(self):
        with open(self.filename(), "w") as file:
            while not self.stop_event.is_set():
                line = self.queue.get()
                if line is FLAG_FINISHED:
                    break
                file.write(f"{line}\n")
                file.flush()
                self.queue.task_done()

    def stop(self):
        self.stop_event.set()

    def log_line(self, line: str):
        self.queue.put(line)

    def log_finished(self):
        self.queue.put(FLAG_FINISHED)


class LoadRecorder(RecorderBase):
    def __init__(self):
        super().__init__()

    def filename(self):
        return f"{DATA_FOLDER}/load.csv"

    def log_threads(self, request_name: str, current_threads: int):
        self.log_line(f"{time():.4f},{request_name},{current_threads}")


class MetricRecorder(RecorderBase):
    def __init__(self, request_name: str):
        super().__init__()
        self.request_name = request_name

    def filename(self):
        return f"{DATA_FOLDER}/{self.request_name}.csv"

    def log_result(self, time: float, request_time: float):
        self.log_line(f"{time:.4f},success,{request_time}")

    def log_failure(self, time: float, status_code: int):
        self.log_line(f"{time:.4f},failure,{status_code}")


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
