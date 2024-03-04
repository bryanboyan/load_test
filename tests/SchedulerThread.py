from time import time, sleep
from threading import Thread, Event
from typing import TypedDict, List
from tests.Config import config
from tests.Metrics import metrics
from tests.Request import Request
from tests.RequestThreadManager import RequestThreadManager
from tests.Logger import Logger

log = Logger("SchedulerThread").log

class SchedulerThread(Thread):
    """Thread to scheduling the management (leveraging RequestThreadManager) of requests for a given request type"""
    def __init__(self, request_name: str):
        super().__init__()
        self.stop_event = Event()
        request = Request(request_name)
        self.request = request
        self.thread_manager = RequestThreadManager(request)
        self.schedules = config.get_schedule_shape(request_name)

    def run(self) -> None:
        log(f"Starting thread {self.name} for {self.__class__.__name__}")
        start_time = time()
        schedule_index = -1
        while not self.stop_event.is_set():
            time_elapsed = time() - start_time

            # If time not elapsed, continue the current schedule
            if schedule_index >= 0 and self.schedules[schedule_index]['time'] > time_elapsed:
                sleep(0.5)
                continue
            # Time elapsed, check for next schedule
            has_schedule = False
            for i in range(schedule_index+1, len(self.schedules)):
                schedule = self.schedules[i]
                if time_elapsed < schedule["time"]:
                    has_schedule = True
                    schedule_index = i
                    self.thread_manager.run(schedule["threads"], schedule.get("ramp"))
                    break
            if not has_schedule:
                break
            sleep(0.5)

        # Finished running all schedules, clean up both the request_threads andn metrics threads.
        self.thread_manager.stop_all()
        metrics.get_request_recorder(self.request.name()).log_finished()
        metrics.get_response_recorder(self.request.name()).log_finished()
        log(f"Scheduler for {self.request.name()} finished, thread name {self.name}")

    def stop(self) -> None:
        self.stop_event.set()
