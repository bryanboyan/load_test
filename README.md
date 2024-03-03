
# Architectural

1. `main.py` is the entry point for running the load test
2. `main.py` calls into `SchedulerThread` for each task/request_name
3. `SchedulerThread` calls into `RequestThreadManager` to tune up/down number of `RequestThread`s to send `Request`
4. Separately, `Metrics` singleton manages the threads to do logging that's published by the threads from `RequestThread` and more.