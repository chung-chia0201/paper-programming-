#!/usr/bin/env python

# This node vote collect bearing of sound over a time
# and vote for a most appear bearing
# just like duckietown classic lane filter

import rospy
import numpy as np
import math
from math import cos, sin, atan2, radians, degrees
from respeaker.msg import SoundBearing
from std_msgs.msg import Bool,Int64MultiArray,Int64
from respeaker.msg import SoundRaw
import librosa
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
        self.frame_num = rospy.get_param("~frame_num", 148)
        r = rospkg.RosPack()
        self.folder = r.get_path('respeaker') + '/output/'
        nyq = 0.5 * 16000
        self.b, self.a = butter(5, 4000./nyq, btype='lowpass')

        # variable
        self.frames = {}
        self.count = {}
        self.frame_counter = {}

        robot = rospy.get_param("~veh")

        if robot == 'locobot':
	        locobot_r1 = rospy.Subscriber('locobot/sound_raw', SoundRaw, self.sound_cb, ('locobot'), queue_size=1)
        else:
            print("Neeeewwwww rooobbooootttt")
        
    def sound_cb(self, sound_msg, respeaker):

        if respeaker not in self.count:
            self.count[respeaker] = 0
            self.frames[respeaker] = []
            self.frame_counter[respeaker] = 0

        self.count[respeaker] += 1
        
        if self.count[respeaker] == 1:
            self.frames[respeaker] = np.array(sound_msg.data).astype(np.int16)
        else:
            self.frames[respeaker] = np.concatenate((self.frames[respeaker],np.array(sound_msg.data).astype(np.int16)),axis=0)
        
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
        MicProcess = np.zeros((6,302720))

        for i in range(6):
            MicSignal[i]=play_frame[i::8]
            
            if i == 1:
                print("this tra: ", str(i))
                MicProcess[i]=logMMSE(MicSignal[i])
                print("end tra")

        librosa.output.write_wav(self.folder+res+'stationary_ch8_'+str(frame_th)+'.wav', MicSignal[1],sr=16000,norm=True)
        librosa.output.write_wav(self.folder+res+'stationary_mmse_0'+'_ch8_'+str(frame_th)+'.wav', MicProcess[1],sr=16000,norm=True)

if __name__ == '__main__':
    
    rospy.init_node('listen_music',anonymous=False)
    lm = ListenMusic()

    rospy.spin()
