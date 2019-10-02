#!/usr/bin/env python3

import sys, os, socket, threading

IP = "127.0.0.1"

class UDP_Server:
    def __init__(self, IP, PORT) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.sock.bind((IP, PORT)) 
        # no timeout, sleep forever waiting for data
        #self.sock.settimeout(0.2) 
    def recv(self) -> bytes:
        data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
        print(f"test server recv:\n\t{data}")
        return data
    def send_response(self, IP, PORT) -> None:
        data = bytes.fromhex('00000001' + 'A0' + '00' + '00' + '00' + '00')
        print(f"test server sending OK response:\n\t{data}")
        self.sock.sendto(data, (IP, PORT))

# pretend this is the artesyn module and show messages
def thread_func():
    # UDP server on a different port from what artesyn is using (8888)
    server = UDP_Server(IP, 8889)
    while True:
        data = server.recv()
        server.send_response(IP, 8888) # respond to artesyn class port

def run_server():
    daemon = threading.Thread(target=thread_func, daemon=True)
    daemon.start()
