from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import time
import requests

# Global variables
#PWRNET_API_BASE_URL = 'http://pwrnet-158117.appspot.com/api/v1/'
SERVER_HOST = "192.168.0.51"
SERVER_PORT = 502
tcpClient = ModbusClient(host=SERVER_HOST, port=SERVER_PORT, unit_id= 247,timeout=15,auto_open=True)


# Power function
def batteryPower_RT(powerTime, tcpClient, battVal = 0):

    #print "Command_Mode: ", command_mode
    addr_disPower = 63248
    addr_chaPower = 63246

    if battVal > 0:
        command_mode = 4 # Discharging (positive values)
    elif battVal < 0:
        command_mode = 3 # Charging (negative values)
    else: command_mode = 1

    # Battery power
    battPower = abs(battVal)      # [W]: float32: [-3300W ... 3300W]
    addr_command = 63245
    addr_time = 63243
    timeP = powerTime           # How long to discharge [s]: uint32

    if tcpClient.is_open():

        # Setting time
        regs_timeout = tcpClient.write_multiple_registers(addr_time,[timeP&0xffff,(timeP&0xffff0000)>>16])

        # Setting mode
        regs_command = tcpClient.write_single_register(addr_command, command_mode)

        # Setting power
        if (command_mode == 4):
            powerFloat = utils.encode_ieee(battPower) # Converting to ieee float32
            regs_disPower = tcpClient.write_multiple_registers(addr_disPower,[powerFloat&0xffff,(powerFloat&0xffff0000)>>16])
            print "disPower Write: ", str(regs_disPower)
            #print "disPower: ", battVal

            if (str(regs_disPower) != "True"):    # Check if write function worked
                return 0
            else:
                return float(time.time())

        elif (command_mode == 3):
            powerFloat = utils.encode_ieee(battPower) # Converting to ieee float32
            regs_chaPower = tcpClient.write_multiple_registers(addr_chaPower,[powerFloat&0xffff,(powerFloat&0xffff0000)>>16])
            print "chaPower Write: ", str(regs_chaPower)
            #print "chaPower: ", battVal

            if (str(regs_chaPower) != "True"):    # Check if write function worked
                return 0
            else:
                #print "chaPowerTime: ",
                return float(time.time())

        else:
            #print "battery OFF"
            return 0

    else:
        print "tcpClient did not open"
        tcpClient.open()
        return -1


def main():

    powerTime = 10
    battTime = 0.0

    while True:

        #PW2 = requests.get(url=PWRNET_API_BASE_URL + "device/19/", timeout=10)
        #status_PW2 = PW2.json()["status"]
        #print "status_PW2: ", status_PW2


        #print "dTIME: ", current_time - battTime
        val = float(raw_input("Enter battery power value - positive = discharge, negative = charge: "))
        current_time = float(time.time())
        battTime = batteryPower_RT(powerTime, tcpClient, battVal=val)
        #print float(time.time())-current_time
        #print "battTime: ", battTime
        #if (current_time - battTime > powerTime):
        #    print "Entering battery Power function..."
        #    battTime = batteryPower(status_PW2, powerTime, tcpClient)

        #print "battTime: ", battTime
        #print "currTime: ", current_time
        time.sleep(1)

if __name__ == '__main__':

    main()
