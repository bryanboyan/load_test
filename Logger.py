from time import localtime, strftime

class Logger:
    def __init__(self, caller: str):
        self.caller = caller

    def log(self, msg):
        t = strftime("%H:%M:%S", localtime())
        print(f"[{t}] ({self.caller}) - {msg}")
