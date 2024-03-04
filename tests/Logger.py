from tests.Config import config
from time import localtime, strftime

class Logger:
    def __init__(self, caller: str):
        self.caller = caller
        self.muted = config.is_actor_muted(caller)

    def log(self, msg):
        if self.muted:
            return
        t = strftime("%H:%M:%S", localtime())
        print(f"[{t}] ({self.caller}) - {msg}")
