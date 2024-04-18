import time 
from typing import Any, Callable
import asyncio
import random
import threading

class FakeBleDataPackage:

    def __init__(self, now_time, start_time, new_total_distance, new_speed, new_heartrate) -> None:
        self.data_obj =  [
            None, #Unused index
            2, # The data length. This is two to manipulate the data extraction when doing `message_data = data[4:4 + message_length - 1]`
            "message_type", # Fake
            "message_channel",  # Fake
            [
                16, # data_page_no (Should be 16 to hit _general_fe_data_page_handler). Try look up in docs
                25, # equipment_type_code, 25 == trainer
                (now_time-start_time)*4, # elapsed_time (this should be multiplied by 4, as it is devided with 4 for some reason)
                new_total_distance, # distance_traveled,
                round(new_speed*1000) & 0xFF, # speed (# Least significant byte)  # Speed is divided with 1000 in the handler
                (round(new_speed*1000) >> 8) & 0xFF, #  speed (# Most significant byte - note that speed is evaluated as such `speed_raw = int.from_bytes(message_data[4:6], 'little')`)
                new_heartrate, # heartrate,
                160 # This value is used to extract fe_state & lap_toggle. For fe_state: `(val >> 4)  & 0x7` [first bitshift 4, then mask last 3 bits].
                # For lap_toggle: `bool((val >> 4) & 0x8)` [first bitshift, then mask]. Afterwards, both is mapped.
                # lap_toggle should be 1 and fe_state should be 2, hence x >> should be 1010. x = 160.
                
            ] # Data
        ]
    
    def __getitem__(self, index):
        if type(index) == int: # Normal subscript
            return self.data_obj[index]
        
        if type(index) == slice:
            return self.data_obj[index][0] # To manipulate the use of list as message data
        

class CustomBleakClient:
    def __init__(self, update_freqency:int, *args):
        self.update_sleep_time = 1/update_freqency

        self._is_connected = False
        
        self.stream_active = False
        self.stream_callback = None

        self.data_behaviour = {
            "speed": {
                "max": 10, 
                "min": .5,
                "current": 5,
                "progression": .2
            },
            "heartrate": {
                "max": 254, # Max is 255
                "min": 60,
                "current": 254/2,
                "progression": 1
            },
            "distance": {
                "total": 0
            },
            "last_sent_time": time.time(),
            "start_time": time.time()
        }
    

    async def __aenter__(self):
        time.sleep(.5) # Emulates connection time
        self._is_connected = True
        return self
    
    async def __aexit__(self, *args):
        pass

    async def is_connected(self):
        return self._is_connected
    
    async def write_gatt_char(self, *args):
        # Emulate that we write to device
        asyncio.sleep(.2)

    async def start_notify(self, tacx_uart_tx_id, callback:Callable):
        self.stream_callback = callback
        self.stream_active = True
        threading.Thread(target=self.stream_producer, daemon=True).start()
        


    async def stop_notify(self, tacx_uart_tx_id):
        asyncio.sleep(.1)
        self.stream_active = False
        self.stream_callback = None

    def _build_fake_data_obj(self):
        

        now_time = time.time()

        new_speed = self.data_behaviour["speed"]["current"] + (self.data_behaviour["speed"]["progression"]*random.choice([1, -1]))
        if new_speed > self.data_behaviour["speed"]["max"]: new_speed = self.data_behaviour["speed"]["max"]
        if new_speed < self.data_behaviour["speed"]["min"]: new_speed = self.data_behaviour["speed"]["min"]
        

        new_total_distance = self.data_behaviour["distance"]["total"] + ((now_time-self.data_behaviour["last_sent_time"])*new_speed)
        

        new_heartrate = self.data_behaviour["heartrate"]["current"] + (self.data_behaviour["heartrate"]["progression"]*random.choice([1, -1]))
        if new_heartrate > self.data_behaviour["heartrate"]["max"]: new_heartrate = self.data_behaviour["heartrate"]["max"]
        if new_heartrate < self.data_behaviour["heartrate"]["min"]: new_heartrate = self.data_behaviour["heartrate"]["min"]
        


        data_obj = FakeBleDataPackage(
            now_time=now_time,
            start_time=self.data_behaviour["start_time"],
            new_total_distance=new_total_distance,
            new_speed=new_speed,
            new_heartrate=new_heartrate
        )
        
        

        self.data_behaviour["speed"]["current"] = new_speed
        self.data_behaviour["heartrate"]["current"] = new_heartrate
        self.data_behaviour["last_sent_time"] = now_time
        self.data_behaviour["distance"]["total"] = new_total_distance

        return data_obj

    def stream_producer(self):
        self.data_behaviour["start_time"] = time.time()
        while self.stream_active:
            time.sleep(self.update_sleep_time)
            self.stream_callback(
                None, #sender
                self._build_fake_data_obj()
            )