import asyncio
#from modules.TacxTrainer.custom_bleak_client import CustomBleakClient # Fake
from modules.TacxTrainer.custom_bleak_client import CustomBleakClient # Fake
#import pycycling
from pycycling.tacx_trainer_control import TacxTrainerControl
import os

DATA = {
    "speed": 0
}

def get():
    return DATA

async def run(address, update_frequency):
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    async with CustomBleakClient(update_frequency, address) as client:
        def my_page_handler(data):
            DATA["speed"] = round(data[3], 1)

        await client.is_connected()
        trainer = TacxTrainerControl(client)
        trainer.set_general_fe_data_page_handler(my_page_handler)
        await trainer.enable_fec_notifications()
        
        return True
