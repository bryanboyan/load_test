import signal
import sys
from tests.Config import config
from tests.Logger import Logger
from tests.Metrics import metrics
from tests.SchedulerThread import SchedulerThread
from threading import enumerate
import traceback

log = Logger("main").log

request_names = config.get_tasks()

for name in request_names:
    metrics.init_recorder(name)

scheduler_threads = []
for name in request_names:
    thread = SchedulerThread(name)
    scheduler_threads.append(thread)
    thread.start()

def check_threads() -> int:
    active_threads = enumerate()
    for t in active_threads:
        log(f"{t.ident}. name {t.name}")
        stack = sys._current_frames().get(t.ident, None)
        if stack:
            traceback.print_stack(stack)
        else:
            log("No stack for thread")
    return len(active_threads)

def signal_handler(_, __):
    log("Early termination, exiting...")

    # Stop all opened threads (scheduling threads and metrics threads)
    for thread in scheduler_threads:
        thread.stop()

    num_active_threads = check_threads()

    exit(num_active_threads)

signal.signal(signal.SIGINT, signal_handler)

for thread in scheduler_threads:
    thread.join()
metrics.terminate()

log("All threads finished, exiting...")
