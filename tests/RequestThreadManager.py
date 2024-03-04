from time import sleep
from tests.Metrics import metrics
from tests.RequestThread import RequestThread
from tests.Logger import Logger

log = Logger("RequestThreadManager").log


class RequestThreadManager:
    """Directly manage the requsetThreads (threads up/down) for the request type."""
    def __init__(self, request):
        self.threads = []
        self.request = request
        self.load_recorder = metrics.get_load_recorder()

    def run(self, target_threads: int, ramp: int) -> None:
        """Run the threads with the target number of threads and ramp speed."""
        log(
            f"RequestThreadManager: Running {target_threads} threads for {self.request.name()}"
        )
        if target_threads > len(self.threads):
            self.rampup_threads(target_threads, ramp)
        elif target_threads < len(self.threads):
            self.rampdown_threads(target_threads, ramp)

    def rampup_threads(self, target_threads: int, ramp: int) -> None:
        """Ramp up the number of threads to the target number with ramp speed per second."""
        while len(self.threads) < target_threads:
            delta = min(target_threads - len(self.threads), ramp)
            self.add_threads(delta)
            sleep(1)

    def add_threads(self, delta: int) -> None:
        """Add the delta number of threads to the pool."""
        for _ in range(delta):
            thread = RequestThread(self.request)
            self.threads.append(thread)
            thread.start()
            self.load_recorder.log_threads(self.request.name(), len(self.threads))

    def rampdown_threads(self, target_threads: int, ramp: int) -> None:
        """Ramp down the number of threads to the target number with ramp speed per second."""
        while len(self.threads) > target_threads:
            delta = min(len(self.threads) - target_threads, ramp)
            self.kill_threads(delta)
            sleep(1)

    def kill_threads(self, delta: int) -> None:
        """Kill the delta number of threads from the pool."""
        for _ in range(delta):
            thread = self.threads.pop()
            thread.stop()
            thread.join()
            self.load_recorder.log_threads(self.request.name(), len(self.threads))

    def stop_all(self) -> None:
        """Stop all threads."""
        for thread in self.threads:
            thread.stop()
            thread.join()
        self.threads.clear()
        self.load_recorder.log_threads(self.request.name(), len(self.threads))
