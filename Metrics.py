from queue import Queue
from threading import Thread
from time import time

DATA_FOLDER = "data"
FLAG_FINISHED = "FINISHED"

# class LoadRecorder:
#     def __init__(self):
#         self.queue = Queue()
#         self.write_thread = None
#         self.enabled = False
    
#     def log_load(self, request_name: str, current_threads: int):
#         self.queue.put((time(), request_name, current_threads))
    


class MetricRecorder:
    def __init__(self, request_name):
        self.request_name = request_name
        self.queue = Queue()
        self.write_thread = None
        self.enabled = False

    def log_result(self, request_time: float):
        self.queue.put(request_time)

    def log_failure(self, status_code: int):
        self.queue.put(status_code)

    def log_finished(self):
        self.queue.put(FLAG_FINISHED)

    def start_recording(self):
        self.enabled = True
        if self.write_thread is None:
            self.write_thread = Thread(target=self.write_file)
            self.write_thread.start()

    def write_file(self):
        filename = f"{DATA_FOLDER}/{self.request_name}.csv"
        with open(filename, "w") as file:
            while self.enabled:
                result = self.queue.get()
                if result is FLAG_FINISHED:
                    break
                file.write(str(result) + "\n")
                self.queue.task_done()
    
    def terminate(self):
        self.enabled = False
        self.write_thread.join()


class Metrics:
    def __init__(self):
        self.recorders = {}

    def init_recorder(self, request_name: str) -> None:
        if request_name not in self.recorders:
            self.recorders[request_name] = MetricRecorder(request_name)
            self.recorders[request_name].start_recording()

    def get_recorder(self, request_name: str) -> MetricRecorder:
        return self.recorders[request_name]

    def terminate(self):
        for recorder in self.recorders.values():
            recorder.terminate()


metrics = Metrics()
