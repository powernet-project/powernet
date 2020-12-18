# Powernet
    
## Setup

#### Clone Source Code
```
git clone https://github.com/powernet-project/powernet.git
cd powernet
git checkout master
``` 
### The alogorithm for powernet already develiped is added to the alogorithm folder
         ##  local_controller.py
### The code to calculate the average power of consumed by the device over time  and the pass the power to the powernet algrithm is addded to the file  
## home_battery_optimizer.py
        ##  Functiona name  - avg_power_for_device(parm_device_id)
## Need further clarification and review on the average calculation - 
## 1. Currently I am taking all the values of power available form the begiging of time ? Is there a time span that need to be defined to to clauclate the power ?
## 2. The logic to write the optimized output from the model bakc to the battery is not incorporated.
