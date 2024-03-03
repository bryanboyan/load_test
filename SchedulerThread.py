from time import time, sleep
from threading import Thread, Event
from typing import TypedDict, List
from Config import config
from Metrics import metrics
from Request import Request
from RequestThreadManager import RequestThreadManager
from Logger import Logger

log = Logger("SchedulerThread").log

class SchedulerThread(Thread):
    def __init__(self, request_name: str):
        super().__init__()
        self.stop_event = Event()
        request = Request(request_name)
        self.request = request
        self.thread_manager = RequestThreadManager(request)
        self.schedules = config.get_schedule_shape(request_name)

    def run(self) -> None:
        log(f"SchedulerThread: Running scheduler for {self.request.name()}")
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
                log(f"using {time_elapsed} to compare with {schedule['time']}")
                if time_elapsed < schedule["time"]:
                    has_schedule = True
                    schedule_index = i
                    self.thread_manager.run(schedule["threads"], schedule.get("ramp"))
                    break
            if not has_schedule:
                break
            sleep(0.5)

        # Finished running all schedules, clean up
        self.thread_manager.stop_all()
        metrics.get_recorder(self.request.name()).log_finished()
        log(f"SchedulerThread: Scheduler for {self.request.name()} finished")

    def stop(self) -> None:
        self.stop_event.set()
