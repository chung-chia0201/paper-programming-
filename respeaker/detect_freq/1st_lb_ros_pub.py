#!/usr/bin/env python3
#
## Copyright 2023 NYCU, Chung-Chia Chen
##
## *****************************************************
##  DESCRIPTION :
##  This is the client-side(socket) on ReSpeaker Core v2.0, please set ip  and host port first in the bottom accroding to environments.
##
#

import socket
import numpy as np
import rospy
from std_msgs.msg import Float32MultiArray

def pub_sound():
    pub = rospy.Publisher('result_csm', Float32MultiArray, queue_size=10)
    r = rospy.Rate(1)

    while not rospy.is_shutdown():
        ret=s.recv(1024)
        print(ret.decode())
        pub.publish(ret)
        r.sleep()

def main():
    rospy.init_node('sound_localize_csm',anonymous=False)
    pub_sound()
    rospy.spin()

if __name__ == '__main__':
    #　ros init
    #　rospy.init_node('sound_localize',anonymous=False)
    HOST = '127.0.0.1' #respeaker ip
    PORT = 8001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT)) # change to client in socket
    print ('Client find at: %s:%s' %(HOST, PORT))
    print ('wait for connection...')
    main()