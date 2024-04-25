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
delay = 0.5

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


# class AxisCalculator():
# 	AVG_SPAN = 10
         
# 	calibration_data = 
      

# 		self.avg = []
        
# 	def add_value_to_average(self, val):
# 		if len(self.avg) == self.AVG_SPAN:
# 			self.avg.pop()
# 		self.avg.insert(0,val)

# 	def read_channel(self):
# 		# Sum analouge shit
# 		val = spi.xfer2([1,(8+self.channel)<<4,0])
# 		data = ((val[1]&3) << 8) + val[2]

# 		self.add_value_to_average(data)
# 		return data
	
# 	def calc_ref_val(self, val):
# 		pass

	# The normalize_value function
def normalize_value(current, min_val, max_val):
    # Ensure the value is within bounds to avoid division by zero
    if max_val - min_val == 0:
        return 0  # default value
    # Scale the current value from 0 to 100
    normalized = (current - min_val) / (max_val - min_val) * 100
    return normalized
      
# def save_calibration_data(filepath="calibration_data.json"):
#     		with open(filepath, "w") as file:
#         		json.dump(AxisCalculator.calibration_data, file)
	
# def load_calibration_data(filepath="calibration_data.json"):
#     try:
#         with open(filepath, "r") as file:
#             AxisCalculator.calibration_data = json.load(file)
#             return True
#     except FileNotFoundError:
#         	return False



# 	# Calibration function
# def calibrate():
#     print("Starting calibration. Move the joystick to all extremes, then release.")
#     start_time = time.time()
#     calibration_duration = 5  # Calibrate for 5 seconds
#     while time.time() - start_time < calibration_duration:
#         vrx_pos = readChannel(vrx_channel)
#         vry_pos = readChannel(vry_channel)
        
#         # Update calibration data
#         AxisCalculator.calibration_data['vrx_min'] = min(AxisCalculator.calibration_data['vrx_min'], vrx_pos)
#         AxisCalculator.calibration_data['vrx_max'] = max(AxisCalculator.calibration_data['vrx_max'], vrx_pos)
#         AxisCalculator.calibration_data['vry_min'] = min(AxisCalculator.calibration_data['vry_min'], vry_pos)
#         AxisCalculator.calibration_data['vry_max'] = max(AxisCalculator.calibration_data['vry_max'], vry_pos)

#         time.sleep(0.1)  # Short delay to prevent flooding with reads
#     print("Calibration complete.")



def get_joystick_output():
    vrx_pos = readChannel(vrx_channel)
    vry_pos = readChannel(vry_channel)
    swt_val = readChannel(swt_channel)

    vrx_pos_normalized = normalize_value(vrx_pos, CALIBRATION_DATA['vrx_min'], CALIBRATION_DATA['vrx_max'])
    vry_pos_normalized = normalize_value(vry_pos, CALIBRATION_DATA['vry_min'], CALIBRATION_DATA['vry_max'])

    return {"x": vrx_pos_normalized, "y": vry_pos_normalized, "pressed": swt_val}




def run():
      return True

	
