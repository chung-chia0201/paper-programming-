#!/usr/bin/env python3
#
## Copyright 2023 NYCU, Chung-Chia Chen
##
## *****************************************************
##  DESCRIPTION :
##  This is the subscriber(ros) on ReSpeaker Core v2.0
##
#

import rospy
from std_msgs.msg import String

def callback(data): 
      
    # print the actual message in its raw format 
    rospy.loginfo("Here's what was subscribed: %s", data) 
      
    # otherwise simply print a convenient message on the terminal 
    print('Data from result_csm received') 
  
  
def main(): 
      
    # initialize a node by the name 'listener'. 
    # you may choose to name it however you like, 
    # since you don't have to use it ahead 
    rospy.init_node('compare_result', anonymous=True) 
    
    rospy.Subscriber("result_csm", String, callback) 
      
    # spin() simply keeps python from 
    # exiting until this node is stopped 
    rospy.spin() 
  
if __name__ == '__main__': 
      
    try: 
        main() 
    except rospy.ROSInterruptException: 
        pass
