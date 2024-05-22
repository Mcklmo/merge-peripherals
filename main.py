from scr.sentry import Sentry
from modules.TacxTrainer.main import TestForBenchmarking
from modules.Joystick.main import run as JoystickStart, get_joystick_output as JoystickGet
import time
import json
import psutil
import threading

sentry = Sentry()

# Register your modules here!


def benchmark():
    step = 100
    time.sleep(5)
    for i in range(1, 1000*10, step):
        
        sentry.benchmark.append({"type": "system_reading", "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent})
        # Starting next batch
        for j in range(step):
            _ = TestForBenchmarking()
            sentry.register_module(
                f"Tacx Trainer {i+j}",
                _.run, 
                ("EAAA3D1F-6760-4D77-961E-8DDAC1CC9AED", 5),
                _.get,
                speed=0
            )
            sentry.modules[-1].start()
        
        print(f"Added {step} EMs. Count is now {len(sentry.modules)}")
        
        time.sleep(20)


    with open("./benchmark_results.json", "wb") as f:
        json.dump(sentry.benchmark, f)

# this is the mocked bicycle home trainer
_ = TestForBenchmarking()
sentry.register_module(
    "Tacx Trainer",
    _.run, 
    ("EAAA3D1F-6760-4D77-961E-8DDAC1CC9AED", 5),
    _.get,
    speed=0
)

sentry.register_module(
    "JoyStick",
    JoystickStart, 
    (),
    JoystickGet,
    x=0,
    y=0,
    pressed=0
)

# sentry.register_module(
#     "Tacx Trainer",
#     TacxStart,
#     ("EAAA3D1F-6760-4D77-961E-8DDAC1CC9AED", ),
#     TacxGet,
#     speed=0
# )


threading.Thread(target=benchmark, daemon=True).start()
sentry.start_server(10)