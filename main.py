import os
from scr.sentry import Sentry
from modules.TacxTrainer.main import TestForBenchmarking
# from modules.Joystick.main import run as JoystickStart, get_joystick_output as JoystickGet
import time
import json
import psutil
import threading

sentry = Sentry()

# Register your modules here!


def benchmark():
    time.sleep(5)
    for i in range(1, 10000, 100):
        cpu=psutil.cpu_percent()
        ram=psutil.virtual_memory().percent
        sentry.benchmark.append({"type": "system_reading", "cpu": cpu, "ram": ram})
        sentry.frequency = 1/i
        print(f"Frequency is now: {i}, cpu: {cpu}, ram: {ram}")
        time.sleep(2)

    try:
        with open("./benchmark_results.json", "w") as f:
            json.dump(sentry.benchmark, f)
    except Exception as e:
        print(e)
    
    os._exit(0)

# this is the mocked bicycle home trainer
_ = TestForBenchmarking()
sentry.register_module(
    "Tacx Trainer",
    _.run, 
    ("EAAA3D1F-6760-4D77-961E-8DDAC1CC9AED", 5),
    _.get,
    speed=0
)


threading.Thread(target=benchmark, daemon=True).start()
sentry.start_server(1)