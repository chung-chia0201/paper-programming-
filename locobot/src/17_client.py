#!/usr/bin/env python
## Copyright 2023 NYCU chung-chia,chen
##
## *****************************************************
## client-respeaker no.17

import socket
import numpy as np

HOST = '172.20.10.6'   #respeaker ip
PORT = 8001

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((HOST,PORT))

while True:
    while True:
        ret=s.recv(1024)
        print(ret.decode())
