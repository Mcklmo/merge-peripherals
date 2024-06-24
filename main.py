import os
import sys
from scr.sentry import Sentry
from modules.TacxTrainer.main import TestForBenchmarking
# from modules.Joystick.main import run as JoystickStart, get_joystick_output as JoystickGet
import time
import json
import psutil
import threading
import numpy as np

sentry = Sentry()

# Register your modules here!


def benchmark():
    # let the sentry store data...
    time.sleep(300)

    print("done...")

    print(sys.getsizeof(sentry.benchmark),len(sentry.benchmark)) # 70396120 8155295
    averaged_data=average_cycle_time(sentry.benchmark,10000)
    print("average:",sys.getsizeof(averaged_data),len(averaged_data)) # average: 6936 815

    try:
        with open("./benchmark_results.json", "w") as f:
            json.dump(averaged_data, f)
    except Exception as e:
        print(e)
        os.exit(1)

    print("written to disc")
    
    os._exit(0)

def average_cycle_time(data,factor):
    """takes an array of objects, returns an array of the same format with size =/ factor.
    the result cycle time is the average of each {factor} elements' cycle time.
    """
    # Remove elements from the end if the length is not divisible by 1000
    if len(data) % factor != 0:
        data = data[:-(len(data) % factor)]

    result = []
    num_groups = len(data) // factor

    for i in range(num_groups):
        group = data[i*factor:(i+1)*factor]
        average_cycle_time = 0
        for item in group:
            average_cycle_time+=item.get("cycle_time",0)

        average_cycle_time/= factor

        item["cycle_time"]=average_cycle_time

        result.append(item)

    return result


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