#!/usr/bin/env python3
## respeaker csm publisher

import rospy
import time
from std_msgs.msg import String

def talker():
    pub = rospy.Publisher('res_sr_16000', String, queue_size=10)
    rospy.init_node('res_17', anonymous=True)
    rate = rospy.Rate(0.5) # 10hz
    while not rospy.is_shutdown():
        hello_str = "no.17 %s" % rospy.get_time()
        rospy.loginfo(hello_str)
        send_msg="no.17"
        pub.publish(send_msg)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
