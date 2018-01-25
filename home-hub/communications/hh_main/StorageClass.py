import time
import requests
import logging
import struct
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
from raven import Client

# Global variables
SENTRY_DSN = 'https://e3b3b7139bc64177b9694b836c1c5bd6:fbd8d4def9db41d0abe885a35f034118@sentry.io/230474'
client = Client(SENTRY_DSN)

class Storage:

    def __init__(self, maxpower=3300, addr_command=63245, addr_time=63243, addr_disPower=63248, addr_chaPower=63246, timeBatt = 10, SERVER_HOST="192.168.0.51", SERVER_PORT=502, PWRNET_API_BASE_URL = 'http://pwrnet-158117.appspot.com/api/v1/'):
        self.maxPower = maxpower
        self.addr_command = addr_command
        self.addr_time = addr_time
        self.addr_disPower = addr_disPower
        self.addr_chaPower = addr_chaPower
        self.timeBatt = timeBatt            # How long to (dis)charge [s]: uint32
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
        powerFloat = utils.encode_ieee(battPower) # Converting to ieee float32

        if self.tcpClient.is_open():
            # Setting time
            self.tcpClient.write_multiple_registers(self.addr_time,[self.timeBatt&0xffff,(self.timeBatt&0xffff0000)>>16])

            # Setting mode
            self.tcpClient.write_single_register(self.addr_command, command_mode)

            # Setting power
            if command_mode == 4:

                regs_disPower = self.tcpClient.write_multiple_registers(self.addr_disPower,[powerFloat&0xffff,(powerFloat&0xffff0000)>>16])

                if str(regs_disPower) != "True":    # Check if write function worked
                    return 0
                else:
                    return float(time.time())

            elif command_mode == 3:
                regs_chaPower = self.tcpClient.write_multiple_registers(self.addr_chaPower,[powerFloat&0xffff,(powerFloat&0xffff0000)>>16])

                if str(regs_chaPower) != "True":    # Check if write function worked
                    return 0
                else:
                    return float(time.time())

            else:
                return 0

        else:

            self.tcpClient.open()
            return -1

    def urlBased(self, devId, state=None, powerReal=0):
        logging.info('Storage URL function called')
        if state == None:
            batt = requests.get(url=self.PWRNET_API_BASE_URL + "device/" + devId + "/", timeout=10)
            battStatus = batt.json()["status"]
        else:
            battStatus = state

        if (battStatus == "DISCHARGE"):
            command_mode = 4

        elif (battStatus == "CHARGE"):
            command_mode = 3

        else:
            command_mode = 1

        powerFloat = utils.encode_ieee(powerReal) # Converting power to ieee float32

        if self.tcpClient.is_open():

            # Setting time
            self.tcpClient.write_multiple_registers(self.addr_time, [self.timeBatt & 0xffff, (self.timeBatt & 0xffff0000) >> 16])

            # Setting mode
            self.tcpClient.write_single_register(self.addr_command, command_mode)

            # Setting power
            if (command_mode == 4):
                regs_disPower = self.tcpClient.write_multiple_registers(self.addr_disPower, [powerFloat & 0xffff, (powerFloat & 0xffff0000) >> 16])


                if (str(regs_disPower) != "True"):    # Check if write function worked
                    return 0
                else:
                    return float(time.time())

            elif (command_mode == 3):
                regs_chaPower = self.tcpClient.write_multiple_registers(self.addr_chaPower, [powerFloat & 0xffff, (powerFloat & 0xffff0000) >> 16])

                if (str(regs_chaPower) != "True"):    # Check if write function worked
                    return 0
                else:
                    return float(time.time())

            else:
                return 0

        else:
            self.tcpClient.open()
            return -1

    def battery_thread(self, q_batt):
        logging.info('Battery Thread called')
        state = "OFF"
        fct = "url"     # Which function to call, url or realtime
        battval = 0
        #devId = 19
        while True:
            if not q_batt.empty():
                try:
                    queue_param = q_batt.get(True,1)
                    state = queue_param[0]      # State: CHARGING, DISCHARGING, OFF
                    fct = queue_param[1]        # Function: url, realtime
                    battval = queue_param[2]    # Only used for realtime function
                    q_batt.task_done()
                    #print "Queue battery: ", queue_param
                except Exception as exc:
                    logging.exception(exc)
                    client.captureException()
            if fct == "url":
                batt = self.urlBased(19, state, battval)
                while batt == -1:
                    try:
                        batt = self.urlBased(19, state, battval)
                    except Exception as exc:
                        logging.exception(exc)
                        client.captureException()
            else:
                batt = self.realtime(battval)
                while batt == -1:
                    try:
                        batt = self.realtime(battval)
                    except Exception as exc:
                        logging.exception(exc)
                        client.captureException()

    def readSOE(self,):
        logging.info('readSOE called')
        addr = 62852    # Modbus address of SOE

        if self.tcpClient.is_open():
            try:
                resp = self.tcpClient.read_holding_registers(addr, 2)   # Reading 2 registers, int16
                Lh = hex(resp[0])
                Mh = hex(resp[1])
                Sh = Mh[2:]+Lh[2:]
                val = struct.unpack('f',struct.pack('i',int(Sh,16)))    # Converting from hex to float
                return val[0]

            except Exception as exc:
                logging.exception(exc)
                client.captureException()
        else:
            self.tcpClient.open()
            return -1





########################

if __name__ == '__main__':
    storage = Storage()
    powerTime = 10
    battTime = 0.0
    deviceId = '19'
    soe = 0
    funStor = raw_input("Which function to test: urlBased, storageRT, readSOE: ")

    while True:
        if funStor == "storageRT":
            val = float(raw_input("Enter battery power value - positive = discharge, negative = charge: "))
            current_time = float(time.time())
            battTime = storage.realtime(val)
            if battTime == -1:
                battTime = storage.realtime(val)
            time.sleep(1)
        elif funStor == "urlBased":
            battTime = storage.urlBased(deviceId)
            if battTime == -1:
                battTime = storage.urlBased(deviceId)
            time.sleep(1)
        else:
            soe = storage.readSOE()
            if soe == -1:
                soe = storage.readSOE()
            print "SOE: ", soe
            time.sleep(1)
