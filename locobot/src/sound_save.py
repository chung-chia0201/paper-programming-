#!/usr/bin/env python

import numpy as np
import rospy
import rospkg
from respeaker.msg import SoundRaw
from std_msgs.msg import String
import math

class SoundSave(object):
    """docstring for SoundSave."""
    def __init__(self):
        super(SoundSave, self).__init__()

        res = rospy.get_param("~res")
	
        self.filename = rospkg.RosPack().get_path('respeaker')+"/output/"+res

        self.frame = 0

        ## subscribers
        pozyx_sub = rospy.Subscriber('sound_raw', SoundRaw, self.sound_cb,queue_size=1)

    def sound_cb(self, sound_msg):

        chunk = np.array(sound_msg.data)

        MicSignal = np.zeros((8,len(chunk[1::8]))) #從位置1開始每隔8個取值
        for i in range(8):
            MicSignal[i]=chunk[i::8]

        self.dump_data(MicSignal, self.frame)
        self.frame += 1

    def dump_data(self, array,frame):

        for i in range(len(array)):
            filename = self.filename + '_frame_' + str(frame) + '_channel_' + str(i+1) + '.npy'
            np.save(filename, array[i])

if __name__ == '__main__':
	rospy.init_node('sound_save',anonymous=False)
	s = SoundSave()
	rospy.spin()
