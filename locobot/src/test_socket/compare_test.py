#!/usr/bin/env python3
## locobot subscriber, 2publisher and 1 subscriber
import rospy
from std_msgs.msg import String

def callback(data):
    rospy.loginfo("I heard %s", data.data)

def listener():
    rospy.init_node('locobot_compare', anonymous=True)
    rospy.Subscriber("res_sr_11000", String, callback)
    rospy.Subscriber("res_sr_16000", String, callback)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
