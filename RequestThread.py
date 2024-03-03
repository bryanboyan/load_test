from Config import config
from Metrics import metrics
from Request import Request
from threading import Thread, Event
from time import time, sleep
from Logger import Logger

log = Logger("RequestThread").log

class RequestThread(Thread):

    def __init__(self, request: Request):
        super().__init__()
        self.stop_event = Event()

        self.request = request
        self.intervals = config.get_request_interval_ms(request.name()) / 1000

    def run(self) -> None:
        recorder = metrics.get_recorder(self.request.name())
        while not self.stop_event.is_set():
            start_time = time()
            response = self.request.send()
            if response.status_code == 200:
                recorder.log_result(time() - start_time)
            else:
                recorder.log_failure(response.status_code)
            sleep(self.intervals)
        log(
            f"RequestThread: Finished for {self.request.name()} with thread name {self.name}"
        )

    def stop(self) -> None:
        self.stop_event.set()