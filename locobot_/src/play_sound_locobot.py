#!/usr/bin/env python

# This node vote collect bearing of sound over a time
# and vote for a most appear bearing
# just like duckietown classic lane filter

import rospy
import numpy as np
import math
from math import cos, sin, atan2, radians, degrees
# from sound_localize.msg import SoundBearing
from std_msgs.msg import Bool,Float32MultiArray,Int64, Int16MultiArray
# from sound_localize.msg import SoundRaw
# import librosa
import rospkg
# from scipy.signal import butter, lfilter
# import matplotlib.pyplot as plt
# from mmse import logMMSE
# from tra_process_old_th import tra_process_new_th
import sounddevice as sd
# import pyaudio
# import scikits.audiolab
import time

sd.default.samplerate = 16000
sd.default.channels = 1

volume = 0.5     # range [0.0, 1.0]
fs = 16000       # sampling rate, Hz, must be integer
duration = 2.0   # in seconds, may be float
f = 440.0

k_ = None

switch = 1
test = 'no'

def play_pause(this_msg):

    global test, switch
    # print("child_rec: ", this_msg)
    test = this_msg


    # print("Now switch: ", switch)

def to_ear_locobot_cb(sound_msg):

    frame = np.divide( np.array(sound_msg.data).astype(np.float32), 100000)
    frame = 100 * frame
    sd.play(frame)
    # time.sleep(0.5)

    # samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)
    # sd.play(samples, mapping=[2])

# def to_ear_husky2_cb(sound_msg):

#     global switch

#     if switch == False:
#         return

#     frame = np.divide( np.array(sound_msg.data).astype(np.float32), 100000)
#     frame = 100 * frame
#     sd.play(frame)



if __name__ == '__main__':
    
    rospy.init_node('play_sound_locobot',anonymous=False)
    
    sub_sound_husky1 = rospy.Subscriber('/locobot/listen_to_this', Int16MultiArray, to_ear_locobot_cb, queue_size=1)
    # sub_sound_husky2 = rospy.Subscriber('/husky2/listen_to_this', Int16MultiArray, to_ear_husky2_cb, queue_size=1)

    rospy.spin()
