#!/usr/bin/env python
## Copyright 2019 PME Tommy,Cheng, Shinchen-Huang
##
## *****************************************************
##  DESCRIPTION :
##  socket of server  main.py
## use:
# please set ip  and host port first in the bottom accroding to environments
import time
import threading
import numpy as np
import os
import logging
import math
from utils import *
from scipy import signal
import socket

import rospy
from std_msgs.msg import Int16MultiArray
from respeaker.msg import SoundRaw

logger              = logging.getLogger('MicArray')

chunk_buffer = None
chunk_lock = True
azimuth_global = 0
chunk_time = None

IP_RES = {"172.20.10.2": "locobot"}   # The respeaker ip

def rec_thread(quit_event,respeaker):
    # conn, addr = s.accept()

    pubFrameRaw = rospy.Publisher('sound_raw', SoundRaw, queue_size=8)

    while not rospy.is_shutdown():
        chunk_buffer = s.recv(32768,socket.MSG_WAITALL) #接收資料回來,s為socket變數
        chunk_time = rospy.Time.now()

        xx = np.frombuffer(chunk_buffer,'int16')
        print("size: ", xx.shape)
        s_raw_msg = SoundRaw()
        s_raw_msg.data = xx
        s_raw_msg.header.frame_id = respeaker
        s_raw_msg.header.stamp = chunk_time
        pubFrameRaw.publish(s_raw_msg)

def main(respeaker):

    # ros init
    rospy.init_node('sound_localize',anonymous=False)

    import time
    logging.basicConfig(level=logging.DEBUG)
    # create thread for  microphone array beamforming to do localization with TODA or MUSIC
    q = threading.Event()
    rec_t = threading.Thread(target=rec_thread, args=(q, respeaker))

    rec_t.start()
    rospy.spin()
    rec_t.join()

if __name__ == '__main__':

    # ros init
    rospy.init_node('sound_localize',anonymous=False)
    # set socket server client ip and port
    # HOST = rospy.get_param("~IP", "192.168.1.12")
    HOST = rospy.get_param("~IP","172.20.10.2")
    print("HOST: ", HOST)
    PORT = 8001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT)) # change to client in socket
    print ('Client find at: %s:%s' %(HOST, PORT))
    print ('wait for connection...')
    main(IP_RES[HOST])
    

