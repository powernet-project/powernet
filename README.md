# Powernet
    
## Setup

#### Clone Source Code
```
git clone https://github.com/powernet-project/powernet.git
cd powernet
git checkout master
``` 
### The algorithm for powernet already developed is added to the alogorithm folder
         ##  local_controller.py
### The code to calculate the average powerconsumed by the device over time,  and the code to pass the power to the powernet algroithm is addded to the file  
## home_battery_optimizer.py
        ##  Functiona name  - avg_power_for_device(parm_device_id)
        ## Functiona name optimize_home_battery()
## Need further clarification and review on the average calculation - 
    ## 1. Currently I am taking all the values of power available form the begining of time for each device ? Is there a time span that need to be defined to to calculate the average power ?
## 2. The logic to write the optimized output from the model back to the battery is not incorporated.
