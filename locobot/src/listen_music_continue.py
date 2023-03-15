#!/usr/bin/env python

# This node vote collect bearing of sound over a time
# and vote for a most appear bearing
# just like duckietown classic lane filter

import rospy
import numpy as np
import math
from math import cos, sin, atan2, radians, degrees
from respeaker.msg import SoundBearing
from std_msgs.msg import Bool,Float32MultiArray,Int64, Int16MultiArray
from respeaker.msg import SoundRaw
import rospkg
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
from mmse import logMMSE
from tra_process_old_th import tra_process_new_th


class ListenMusic(object):
    """docstring for ListenMusic."""
    def __init__(self):
        super(ListenMusic, self).__init__()

        # parameter
        self.frame_num = rospy.get_param("~frame_num", 25)
        r = rospkg.RosPack()
        self.folder = r.get_path('respeaker') + '/output/'
        nyq = 0.5 * 16000

        # variable
        self.frames = {}
        self.count = {}
        self.frame_counter = {}
        self.left_ready = False
        self.right_ready = False
        self.frame_2ch = np.zeros((2, 81600))
        robot = rospy.get_param("~veh")

        if robot == 'locobot':
	        locobot_r1 = rospy.Subscriber('locobot/sound_raw', SoundRaw, self.sound_cb, ('locobot'), queue_size=1)
        else:
            print("Neeeewwwww rooobbooootttt")
        
        self.channel_pub = rospy.Publisher('listen_to_this', Int16MultiArray, queue_size=1)
        
    def sound_cb(self, sound_msg, respeaker):

        if respeaker not in self.count:
            self.count[respeaker] = 0
            self.frames[respeaker] = []
            self.frame_counter[respeaker] = 0

        self.count[respeaker] += 1
        
        if self.count[respeaker] == 1:
            self.frames[respeaker] = np.array(sound_msg.data).astype(np.float32)
        else:
            self.frames[respeaker] = np.concatenate((self.frames[respeaker],np.array(sound_msg.data).astype(np.float32)),axis=0)
        
        if self.frame_num == 0:
            pass
        elif self.count[respeaker] == self.frame_num:
            print("save sound ", respeaker, ': ', self.frame_counter[respeaker])
            self.play_music(self.frames[respeaker], self.frame_counter[respeaker], respeaker)
            self.frames[respeaker] = []
            self.count[respeaker] = 0
            self.frame_counter[respeaker] += 1

    def play_music(self, play_frame, frame_th, res):

        MicSignal = np.zeros((6,len(play_frame[1::8])))
        MicProcess = np.zeros((6,50880))

        for i in range(6):
            MicSignal[i]=play_frame[i::8]
            
            if (res == "locobot" and i==1): 
                start_time = rospy.Time.now()
                print("Max before: ", np.max(MicSignal[i]))
                MicProcess[i]=logMMSE(MicSignal[i])
                MicProcess[i] = 100000*MicProcess[i] # scale to use int16
                end_time = rospy.Time.now()
                print("Max after: ", np.max(MicProcess[i]))
                print("log mmse time: ", (end_time.to_sec()-start_time.to_sec()))
                print("------------------------------")
                pub_msg = Int16MultiArray()
                pub_msg.data = np.array(MicProcess[i]).astype(np.int16).tolist()
                self.channel_pub.publish(pub_msg)

if __name__ == '__main__':
    
    rospy.init_node('listen_music_continue',anonymous=False)
    lm = ListenMusic()

    rospy.spin()