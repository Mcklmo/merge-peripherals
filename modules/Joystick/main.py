#!/usr/bin/python
import spidev
import os
import time
import json
import sys

 
# Define Axis Channels (channel 3 to 7 can be assigned for more buttons / joysticks)
swt_channel = 0
vrx_channel = 1
vry_channel = 2

#Time delay, which tells how many seconds the value is read out

# Spi oeffnen
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000
# Function for reading the MCP3008 channel between 0 and 7
def readChannel(channel):
	val = spi.xfer2([1,(8+channel)<<4,0])
	data = ((val[1]&3) << 8) + val[2]
	return data


CALIBRATION_DATA =  {
        'vrx_min': 1023,
        'vrx_max': 0,
        'vry_min': 1023,
        'vry_max': 0
    }

# The normalize_value function
def normalize_value(current, min_val, max_val):
    # Ensure the value is within bounds to avoid division by zero
    if max_val - min_val == 0:
        return 0  # default value
    # Scale the current value from 0 to 100
    normalized = (current - min_val) / (max_val - min_val) * 100
    return normalized
    


def get_joystick_output():
    vrx_pos = readChannel(vrx_channel)
    vry_pos = readChannel(vry_channel)
    swt_val = readChannel(swt_channel)

    vrx_pos_normalized = normalize_value(vrx_pos, CALIBRATION_DATA['vrx_min'], CALIBRATION_DATA['vrx_max'])
    vry_pos_normalized = normalize_value(vry_pos, CALIBRATION_DATA['vry_min'], CALIBRATION_DATA['vry_max'])

    return {"x": vrx_pos_normalized, "y": vry_pos_normalized, "pressed": swt_val}




def run():
      return True

	
