#!/usr/bin/env python3

import sys, os, socket, threading, random
import udp_server


sys.path.append(".")
sys.path.append("..")
import artesyn_udp_messaging

path = os.path.dirname(__file__) + "/../setups/artesyn_config.json"

msg = artesyn_udp_messaging.Messaging(config_file=path, 
        simulate=True, debug=True) # default artesyn port of 8888

udp_server.run_server() # listens on port 8889, responds to port 8888

while True:
    print(f'\n\n>> Please enter one of the commands and press Enter:')
    for cmd in msg.get_commands():
        print(f'\t{cmd}')
    command = input()
    value = 0
    if command == 'set_slot_current':
        value = random.randint(0, 100) # output current percent
        print(f'Setting output current percent to {value}')
    # send to our test svr
    msg.send(command=command, IP="127.0.0.1", port=8889, value=value) 

