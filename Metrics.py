from queue import Queue
from threading import Thread, Event
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


class MetricRecorder(Thread):
    def __init__(self, request_name: str):
        super().__init__()
        self.stop_event = Event()
        self.request_name = request_name
        self.queue = Queue()

    def log_result(self, time: float, request_time: float):
        self.queue.put((time, 'success', request_time))

    def log_failure(self, time: float, status_code: int):
        self.queue.put((time, 'failure', status_code))

    def log_finished(self):
        self.queue.put(FLAG_FINISHED)

    def run(self):
        filename = f"{DATA_FOLDER}/{self.request_name}.csv"
        with open(filename, "w") as file:
            while not self.stop_event.is_set():
                result = self.queue.get()
                if result is FLAG_FINISHED:
                    break
                time, status, data = result
                file.write(f"{time},{status},{data}\n")
                self.queue.task_done()

    def stop(self):
        self.stop_event.set()


class Metrics:
    def __init__(self):
        self.recorders = {}

    def init_recorder(self, request_name: str) -> None:
        if request_name not in self.recorders:
            self.recorders[request_name] = MetricRecorder(request_name)
            self.recorders[request_name].start()

    def get_recorder(self, request_name: str) -> MetricRecorder:
        return self.recorders[request_name]

    def terminate(self):
        for thread in self.recorders.values():
            thread.stop()
            thread.join()


metrics = Metrics()
