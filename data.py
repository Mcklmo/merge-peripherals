import json

with open("./benchmark_results.json", "r") as f:
    data = json.load(f)
    
print("Loaded data")

merged_data = []
temp = []
for reading in data:
    if reading["type"] == "reading":
        temp.append(reading)
    else:
        for t in temp:
            merged_data.append({
                **t,
                "cpu": reading["cpu"],
                "ram": reading["ram"]
            })
        temp = []

print("Rinsed data..")

sec_in_nano = 10**9
d_dict = dict()
for d in merged_data:
    if 1/d["target_freq"] not in d_dict: d_dict[1/d["target_freq"]] = []
    d_dict[1/d["target_freq"]].append({"target_rate": (sec_in_nano*d["target_freq"])/(d["cycle_time"]), "cpu": d["cpu"], "ram": d["ram"]})
    
target_rate = []
cpu = []
ram = []
for key, value in d_dict.items():
    target_rate.append((key, sum(_["target_rate"] for _ in value)/len(value)))
    cpu.append((key, sum(_["cpu"] for _ in value)/len(value)))
    ram.append((key, sum(_["ram"] for _ in value)/len(value)))
    
print("Prepared data")
    
import matplotlib.pyplot as plt

#plt.plot([_[0] for _ in target_rate], [_[1] for _ in target_rate], 'r') # plotting t, a separately 


new_stuff = []
for t in target_rate:
    new_stuff.append(t[0]*t[1])
plt.plot([_[0] for _ in target_rate], new_stuff, 'b') # plotting t, a separately 
#plt.plot([_[0] for _ in target_rate], [_[1] for _ in cpu], 'b') # plotting t, b separately 
#plt.plot([_[0] for _ in target_rate], [_[1] for _ in ram], 'g') # plotting t, c separately 

plt.show()