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
import rospkg
from std_msgs.msg import String
import time

class Save_detect_data:
    def __init__(self):
        self.file_name="detect_csm.txt"
        self.path=rospkg.RosPack().get_path('locobot')+"/output/sample_rate_8000/"+self.file_name
        self.date_bool=0

        rospy.init_node('save_csm', anonymous=True)     
        rospy.Subscriber("result_csm", String, self.callback)

        

    def callback(self,data): 
        rospy.loginfo("recive data: %s", data) 

        now_time=time.localtime(time.time())

        text=str(now_time.tm_hour)+":"+str(now_time.tm_min)+":"+str(now_time.tm_sec)

        f=open(self.path,'a')

        if self.date_bool==0:
            title_text=str(now_time.tm_year)+"/"+str(now_time.tm_mon)+"/"+str(now_time.tm_mday)+"-"+str(now_time.tm_wday)
            f.write(title_text+"\n")
            self.date_bool=1


        f.write("time:"+text+"\t"+data.data+"\n")
        f.close()

    
    def run(self):
        rospy.spin()    

  
if __name__ == '__main__':     
    try: 
        node=Save_detect_data()
        node.run() 
    except rospy.ROSInterruptException: 
        pass