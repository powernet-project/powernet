# Python TCP Client A
import socket

#host = socket.gethostname()
host = '192.168.1.70'
# Create as many ports as is required to perform all comms
port_control = 7
port_duty = 8
BUFFER_SIZE = 2000
MESSAGE = "This is tcpClient_control"

# Control the state of SDF: Hard ON/OFF Soft ON/OFF
tcpClient_control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClient_control.connect((host, port_control))

# Control the state of SDF: Hard ON/OFF Soft ON/OFF
tcpClient_duty = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClient_duty.connect((host, port_duty))
#### NEED TO FINALIZE THE CODE AND AUTOMATE THE PORTS, CREATE THREADS AND CHECK IF CONNECTION DROPPED ######
i=0

while True:
    try:
        if (i == 0):
            tcpClient_control.sendall(MESSAGE)
            i=1
        data = tcpClient_control.recv(BUFFER_SIZE)
        print " ClientA received data:", data
        #MESSAGE = raw_input("tcpClient_control: Enter message to continue/ Enter exit:")
    except Exception as exc:
        tcpClient_control.close()
        break
print 'Closing socket...'
tcpClient_control.close()
