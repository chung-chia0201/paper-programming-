#!/usr/bin/env python

import rospy
import time

file_name="flash.txt"
path="/home/locobot/catkin_ws/src/locobot/output/"+file_name

f_test=open(path,"r")

print(f_test.read())

f_test.close()

# f=open(path,'a')
# now_time=time.localtime(time.time())

# text=str(now_time.tm_hour)+":"+str(now_time.tm_min)+":"+str(now_time.tm_sec)

# print(text)

# f.write(text+"\n")

# f.close()