from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import time
import requests
import logging


class Storage:

    def __init__(self, maxpower=3300, addr_command=63245, addr_time=63243, addr_disPower=63248, addr_chaPower=63246, SERVER_HOST="192.168.0.51", SERVER_PORT=502, PWRNET_API_BASE_URL = 'http://pwrnet-158117.appspot.com/api/v1/'):
        self.maxPower = maxpower
        self.addr_command = addr_command
        self.addr_time = addr_time
        self.addr_disPower = addr_disPower
        self.addr_chaPower = addr_chaPower
        self.SERVER_HOST = SERVER_HOST
        self.SERVER_PORT = SERVER_PORT
        self.tcpClient = ModbusClient(host=self.SERVER_HOST, port=self.SERVER_PORT, unit_id= 247,timeout=15,auto_open=True)
        self.PWRNET_API_BASE_URL = PWRNET_API_BASE_URL
        logging.info('Storage class called')

    def realtime(self, battVal = 0.0):

        logging.info('StorageRT function called')

        if battVal > 0:
            command_mode = 4    # Discharging (positive values)
        elif battVal < 0:
            command_mode = 3    # Charging (negative values)
        else:
            command_mode = 1

        # Battery power
        battPower = abs(battVal)      # [W]: float32: [-3300W ... 3300W]
        timeP = 10           # How long to discharge [s]: uint32

        if self.tcpClient.is_open():
            # Setting time
            regs_timeout = self.tcpClient.write_multiple_registers(self.addr_time,[timeP&0xffff,(timeP&0xffff0000)>>16])

            # Setting mode
            regs_command = self.tcpClient.write_single_register(self.addr_command, command_mode)

            # Setting power
            if command_mode == 4:
                powerFloat = utils.encode_ieee(battPower) # Converting to ieee float32
                regs_disPower = self.tcpClient.write_multiple_registers(self.addr_disPower,[powerFloat&0xffff,(powerFloat&0xffff0000)>>16])
                print "disPower Write: ", str(regs_disPower)
                # print "disPower: ", battVal

                if str(regs_disPower) != "True":    # Check if write function worked
                    return 0
                else:
                    return float(time.time())

            elif command_mode == 3:
                powerFloat = utils.encode_ieee(battPower) # Converting to ieee float32
                regs_chaPower = self.tcpClient.write_multiple_registers(self.addr_chaPower,[powerFloat&0xffff,(powerFloat&0xffff0000)>>16])
                print "chaPower Write: ", str(regs_chaPower)
                # print "chaPower: ", battVal

                if str(regs_chaPower) != "True":    # Check if write function worked
                    return 0
                else:
                    # print "chaPowerTime: ",
                    return float(time.time())

            else:
                #print "battery OFF"
                return 0

        else:
            print "tcpClient did not open"
            self.tcpClient.open()
            return -1

    def urlBased(self, devId):
        logging.info('Storage URL function called')
        batt = requests.get(url=self.PWRNET_API_BASE_URL + "device/" + devId + "/", timeout=10)
        battStatus = batt.json()["status"]

        if (battStatus == "DISCHARGE"):
            command_mode = 4

        elif (battStatus == "CHARGE"):
            command_mode = 3

        else:
            command_mode = 1

        print "Command_Mode: ", command_mode
        disPower = 1500         # [W]: float32: [-3300W ... 3300W]
        chaPower = 1000         # [W]: float32
        timeP = 10              # How long to discharge [s]: uint32

        if self.tcpClient.is_open():

            # Setting time
            regs_timeout = self.tcpClient.write_multiple_registers(self.addr_time, [timeP & 0xffff, (timeP & 0xffff0000) >> 16])

            # Setting mode
            regs_command = self.tcpClient.write_single_register(self.addr_command, command_mode)

            # Setting power
            if (command_mode == 4):
                powerFloat = utils.encode_ieee(disPower) # Converting to ieee float32
                regs_disPower = self.tcpClient.write_multiple_registers(self.addr_disPower, [powerFloat & 0xffff, (powerFloat & 0xffff0000) >> 16])
                #print "disPower Write: ", str(regs_disPower)

                if (str(regs_disPower) != "True"):    # Check if write function worked
                    return 0
                else:
                    return float(time.time())

            elif (command_mode == 3):
                powerFloat = utils.encode_ieee(chaPower) # Converting to ieee float32
                regs_chaPower = self.tcpClient.write_multiple_registers(self.addr_chaPower, [powerFloat & 0xffff, (powerFloat & 0xffff0000) >> 16])
                #print "chaPower Write: ", str(regs_chaPower)

                if (str(regs_chaPower) != "True"):    # Check if write function worked
                    return 0
                else:
                    #print "chaPowerTime: ",
                    return float(time.time())

            else:
                off_status = requests.put(url=self.PWRNET_API_BASE_URL+'device/' + devId + '/', data={'id': 19, 'type': 'STORAGE', 'name': 'PW2', 'status': 'OFF'},timeout=10)
                #print "status: ", off_status
                return 0

        else:
            self.tcpClient.open()
            return -1



########################

if __name__ == '__main__':
    storageRT = Storage()
    storageURL = Storage()
    powerTime = 10
    battTime = 0.0
    deviceId = '19'
    funStor = raw_input("Which function to test, urlBased or storageRT: ")

    while True:
        if funStor == "storageRT":
            val = float(raw_input("Enter battery power value - positive = discharge, negative = charge: "))
            current_time = float(time.time())
            battTime = storageRT.realtime(val)
            if battTime == -1:
                battTime = storageRT.realtime(val)
            time.sleep(1)
        else:
            battTime = storageURL.urlBased(deviceId)
            if battTime == -1:
                battTime = storageURL.urlBased(deviceId)
            time.sleep(1)
