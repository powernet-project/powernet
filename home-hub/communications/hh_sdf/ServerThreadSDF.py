# Need to check when client drop connection how to close
# the socket and end thread

import socket
from threading import Thread
from SocketServer import ThreadingMixIn
import requests
import time

# Multithreaded Python server : TCP Server Socket Thread Pool
class ClientThread(Thread):

    def __init__(self,ip,port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.SDF1_URL = 'http://pwrnet-158117.appspot.com/api/v1/device/21'
        print "[+] New server socket thread started for " + ip + ":" + str(port)

    def run(self):
        i = 0
        state_prev = requests.get(self.SDF1_URL,timeout=10).json()['status']
        prevTime = time.time()
        while True :
            try:
                if (i == 0):
                    data = conn.recv(2048)
                    print "Server received data:", data
                    print "IP and PORT #: ", self.ip, self.port
                    MESSAGE = state_prev
                    i = 1
                    conn.sendall(MESSAGE)
                    prevTime = time.time()
                else:
                    state = requests.get(self.SDF1_URL, timeout=10).json()['status']
                    if state == 'UNKNOWN':
                        print 'State = Unknown...'
                        conn.close()
                        break
                    else:
                        if state != state_prev:
                            MESSAGE  = state
                            state_prev = state
                            print 'Your new state should be: ', state
                            conn.sendall(MESSAGE)
                            prevTime = time.time()
                        else:
                            # Checking if comms is still alive
                            if time.time()-prevTime > 10:
                                conn.sendall('heartbeat')
                                time.sleep(0.5)
                                conn.sendall('heartbeat')
                                prevTime = time.time()

                '''print "Your state should be: ", state
                MESSAGE = state
                if MESSAGE == 'Unknown':
                    conn.close()
                    break
                conn.send(MESSAGE)  # echo'''
            except Exception as exc:
                print "Exception"
                conn.close()
                break

            time.sleep(2)


# Multithreaded Python server : TCP Server Socket Program Stub
TCP_IP = ''
TCP_PORT = 8888
BUFFER_SIZE = 20  # Usually 1024, but we need quick response

tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#tcpServer.setblocking(0)
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpServer.bind((TCP_IP, TCP_PORT))
threads = []

while True:
    tcpServer.listen(4)
    try:
        print "MAIN: Waiting for connections from TCP clients... \n"
        (conn, (ip,port)) = tcpServer.accept()
        print "ip, port: ", ip, port
        newthread = ClientThread(ip,port)
        newthread.start()
        threads.append(newthread)
    except Exception as exc:
        print "Exception..."
        tcpServer.close()
