from threading import Thread, Event
from time import time, sleep
from tests.Config import config
from tests.Logger import Logger
from tests.Metrics import metrics
from tests.Request import Request

log = Logger("RequestThread").log

class RequestThread(Thread):
    """Thread to call Request to actually send, and log results."""

    def __init__(self, request: Request):
        super().__init__()
        self.stop_event = Event()

        self.request = request
        self.intervals = config.get_request_interval_ms(request.name()) / 1000

    def run(self) -> None:
        log(f"Starting thread {self.name} for {self.__class__.__name__}")
        recorder = metrics.get_recorder(self.request.name())
        while not self.stop_event.is_set():
            start_time = time()
            response, error = self.request.send()
            
            if error is not None:
                log(f"Tester side request failed for {self.request.name()} with error {error}")
            elif response.status_code == 200:
                recorder.log_result(time(), time() - start_time)
            else:
                recorder.log_failure(time(), response.status_code)
            
            sleep(self.intervals)
        log(
            f"RequestThread: Finished for {self.request.name()} with thread name {self.name}"
        )

    def stop(self) -> None:
        self.stop_event.set()
