from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import time
import requests

# Global variables
PWRNET_API_BASE_URL = 'http://pwrnet-158117.appspot.com/api/v1/'
SERVER_HOST = "192.168.0.51"
SERVER_PORT = 502
tcpClient = ModbusClient(host=SERVER_HOST, port=SERVER_PORT, unit_id= 247,timeout=15,auto_open=True)


# Power function
def batteryPower(mode, powerTime, tcpClient):

    if (mode == "DISCHARGE"):
        command_mode = 4

    elif (mode == "CHARGE"):
        command_mode = 3

    else:
        command_mode = 1

    print "Command_Mode: ", command_mode
    addr_disPower = 63248
    addr_chaPower = 63246
    disPower = 1500         # [W]: float32
    chaPower = 1000         # [W]: float32


    addr_command = 63245
    # command_mode = 4    # 4 -> Discharging: uint16

    addr_time = 63243
    time = powerTime           # How long to discharge [s]: uint32

    if tcpClient.is_open():

        # Setting time
        regs_timeout = tcpClient.write_multiple_registers(addr_time,[time&0xffff,(time&0xffff0000)>>16])

        # Setting mode
        regs_command = tcpClient.write_single_register(addr_command, command_mode)

        # Setting power
        if (command_mode == 4):
            powerFloat = utils.encode_ieee(disPower) # Converting to ieee float32
            regs_disPower = tcpClient.write_multiple_registers(addr_disPower,[powerFloat&0xffff,(powerFloat&0xffff0000)>>16])
            #print "disPower Write: ", str(regs_disPower)

            if (str(regs_disPower) != True):    # Check if write function worked
                return 0
            else:
                return int(time.time())

        elif (command_mode == 3):
            powerFloat = utils.encode_ieee(chaPower) # Converting to ieee float32
            regs_chaPower = tcpClient.write_multiple_registers(addr_chaPower,[powerFloat&0xffff,(powerFloat&0xffff0000)>>16])
            #print "chaPower Write: ", str(regs_chaPower)

            if (str(regs_chaPower) != True):    # Check if write function worked
                return 0
            else:
                #print "chaPowerTime: ",
                return int(time.time())

        else:
            off_status = requests.put(url=PWRNET_API_BASE_URL+'device/19/', data={'id': 19, 'type': 'STORAGE', 'name': 'PW2', 'status': 'OFF'},timeout=10)
            #print "status: ", off_status
            return 0

    else:
        tcpClient.open()
        return 0


def main():

    powerTime = 10
    battTime = 0

    while True:

        PW2 = requests.get(url=PWRNET_API_BASE_URL + "device/19/", timeout=10)
        status_PW2 = PW2.json()["status"]
        #print "status_PW2: ", status_PW2

        current_time = int(time.time())
        #print "dTIME: ", current_time - battTime

        if (current_time - battTime > powerTime):
            #print "Entering battery Power function..."
            battTime = batteryPower(status_PW2, powerTime, tcpClient)

        #print "battTime: ", battTime
        #print "currTime: ", current_time
        time.sleep(1)

if __name__ == '__main__':

    main()
