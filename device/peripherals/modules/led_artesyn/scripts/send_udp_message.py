#!/usr/bin/env python3

import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 8888

print(f"Please type a message to send then hit Enter: ", end="")
msg = input().encode('utf-8')

sock = socket.socket(socket.AF_INET,    # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(msg, (UDP_IP, UDP_PORT))

