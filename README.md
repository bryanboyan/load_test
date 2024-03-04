
# Architectural

## Load Tester

1. `tester.py` is the entry point for running the load test and `tests/` folder has all component for load testing
2. `tester.py` calls into `SchedulerThread` for each task/request_name
3. `SchedulerThread` calls into `RequestThreadManager` to tune up/down number of `RequestThread`s to send `Request`
4. Separately, `Metrics` singleton manages the threads to do logging that's published by the threads from `RequestThread` and more.

## Server

A simple server that receives http calls from the load tester for both get and post. Some APIs returns failures and some takes time to return.

## Analyzer

The module that uses the published data to show results