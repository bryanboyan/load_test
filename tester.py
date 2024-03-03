import signal
from tests.Config import config
from tests.Logger import Logger
from tests.Metrics import metrics
from tests.SchedulerThread import SchedulerThread

log = Logger("main").log

request_names = config.get_tasks()

for name in request_names:
    metrics.init_recorder(name)

scheduler_threads = []
for name in request_names:
    thread = SchedulerThread(name)
    scheduler_threads.append(thread)
    thread.start()

def signal_handler(signal, frame):
    log("Early termination, exiting...")

    # Stop all opened threads (scheduling threads and metrics threads)
    for thread in scheduler_threads:
        thread.stop()

    exit(0)

signal.signal(signal.SIGINT, signal_handler)

for thread in scheduler_threads:
    thread.join()
metrics.terminate()

log("All threads finished, exiting...")
