from flask import Flask, request
import random
from time import sleep
from typing import Tuple

# Given random request args, return the sleep time and success flag
def random_params(failure_rate: float, max_sleep: int) -> Tuple[int, bool]:
    sleep_time = random.randint(0, int(max_sleep))
    r = random.random()
    return (sleep_time, r >= float(failure_rate))

app = Flask(__name__)

@app.route('/quick', methods=['GET'])
def quick_get():
    return "success", 200


@app.route("/slow", methods=["GET"])
def slow_get():
    sleep_time = random.randint(1, 10)
    sleep(sleep_time)
    return "success", 200


@app.route("/random", methods=["GET"])
def random_get():
    sleep_time, success = random_params(
        float(request.args.get("failure_rate")), int(request.args.get("max_sleep"))
    )
    if (sleep_time > 0):
        sleep(sleep_time)

    if success:
        return "success", 200
    return "failure", 500

@app.route('/quick', methods=['POST'])
def quick_post():
    return "success", 200

@app.route('/slow', methods=['POST'])
def slow_post():
    sleep_time = random.randint(1, 10)
    sleep(sleep_time)
    return "success", 200

@app.route("/random", methods=['POST'])
def random_post():
    sleep_time, success = random_params(
        float(request.json.get("failure_rate")), int(request.json.get("max_sleep"))
    )
    if sleep_time > 0:
        sleep(sleep_time)

    if success:
        return "success", 200
    return "failure", 500

if __name__ == '__main__':
    app.run(host='localhost', port=8080)
