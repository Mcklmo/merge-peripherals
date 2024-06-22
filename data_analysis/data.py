import json
import matplotlib.pyplot as plt
import numpy as np

def calculate_frequency(time_per_iteration_ns):
    """
    Calculate the frequency of a loop given the time per iteration in nanoseconds.

    Parameters:
    time_per_iteration_ns (float): Time per iteration in nanoseconds.

    Returns:
    tuple: Frequency in Hertz (Hz), Kilohertz (kHz), Megahertz (MHz), and Gigahertz (GHz).
    """
    # Convert time per iteration from nanoseconds to seconds
    time_per_iteration_s = time_per_iteration_ns * 1e-9
    
    # Calculate frequency in Hertz
    frequency_hz = 1 / time_per_iteration_s
    
    # Convert frequency to Kilohertz
    frequency_khz = frequency_hz * 1e-3
    
    # Convert frequency to Megahertz
    frequency_mhz = frequency_hz * 1e-6
    
    # Convert frequency to Gigahertz
    frequency_ghz = frequency_hz * 1e-9
    
    return frequency_hz, frequency_khz, frequency_mhz, frequency_ghz

def get_frequency_khz(cycle_time_ns):
    return calculate_frequency(cycle_time_ns)[1]

with open("./benchmark_results.json", "r") as f:
    data = json.load(f)
    
print("Loaded data")

# Extracting x_axis and y_axis from the data
x_axis = np.array([reading["time"] for reading in data])
y_axis = np.array([get_frequency_khz(reading["cycle_time"]) for reading in data])

plt.plot(x_axis, y_axis, label='Original Data')

mean_cycle_time_ns=np.mean(y_axis)
print("mean:",mean_cycle_time_ns)

smooth_data=True
if smooth_data:
    # Define the window size for the moving average
    window_size = 20


    # Compute the moving average
    y_smooth = np.convolve(y_axis, np.ones(window_size)/window_size, mode='valid')
    # To plot the smoothed line along with the original data
    plt.plot(x_axis[:len(y_smooth)], y_smooth, label='Smoothed Data', color='red')
plt.plot(x_axis,[mean_cycle_time_ns for _ in x_axis],label="Average",color="yellow")
plt.xlabel('Time')
plt.ylabel('kHz')
plt.legend()
plt.show()


# sec_in_nano = 10**9
# d_dict = dict()
# for d in data:
#     if 1/d["target_freq"] not in d_dict: d_dict[1/d["target_freq"]] = []
#     d_dict[1/d["target_freq"]].append({"target_rate": (sec_in_nano*d["target_freq"])/(d["cycle_time"])})
    
# target_rate = []
# for key, value in d_dict.items():
#     target_rate.append((key, sum(_["target_rate"] for _ in value)/len(value)))
    
# print("Prepared data")
    

# # plt.plot([_[0] for _ in target_rate], [_[1] for _ in target_rate], 'r') # plotting t, a separately 

# new_stuff = []
# for t in target_rate:
#     new_stuff.append(t[0]*t[1])
# plt.plot([_[0] for _ in target_rate], new_stuff, 'b') # plotting t, a separately 
#plt.plot([_[0] for _ in target_rate], [_[1] for _ in cpu], 'b') # plotting t, b separately 
#plt.plot([_[0] for _ in target_rate], [_[1] for _ in ram], 'g') # plotting t, c separately 
plt.show()
