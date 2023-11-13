#!/usr/bin/env python3
## locobot subscriber, 2publisher and 1 subscriber
import rospy
from std_msgs.msg import String
import tkinter as tk
import numpy as np
import textwrap
##寫成class且隨時更新狀態的視窗，不要動

class Detect_frequence:
    def __init__(self, root):
        self.root = root
        root.title("alarm")
        root.resizable(500,500)
        self.msg0="result csm: start detect"
        self.msg1="result csm: start detect"
        self.msg2="result csm: start detect"
        self.f1_count=0
        self.f1_count_bool=0

        self.msg10="result 17: start detect"
        self.msg11="result 17: start detect"
        self.msg12="result 17: start detect"
        self.f2_count=0
        self.f2_count_bool=0

        self.detect="detect"

        self.res_csm_sign="csm signal"
        self.res_17_sign="17 signal"

        self.constriction=1
        self.target_freq=3500
        self.target_freq_count=3
        self.res_csm_sign=0
        self.res_17_sign=0

        # 上區域
        self.frame0 = tk.Frame(root, borderwidth=2, relief="solid")
        self.frame0.pack(side="top", padx=10, pady=10)
        
        # 中區域
        self.frame1 = tk.Frame(root, borderwidth=2, relief="solid")
        self.frame1.pack(side="top", padx=10, pady=10)
        
        # 下區域
        self.frame2 = tk.Frame(root, borderwidth=2, relief="solid")
        self.frame2.pack(side="top", padx=10, pady=10)

        # 上區域資訊
        self.label0 = tk.Label(self.frame0, text=self.msg0,width=90,font=("Helvetica",16),anchor="w") #靠左對齊 
        self.label0.pack(pady=1)
        
        self.label1 = tk.Label(self.frame0, text=self.msg1,width=90,font=("Helvetica",16),anchor="w")
        self.label1.pack(pady=2)
        
        self.label2 = tk.Label(self.frame0, text=self.msg2,width=90,font=("Helvetica",16),anchor="w")
        self.label2.pack(pady=3)

        # 中區域內容
        self.label10 = tk.Label(self.frame1, text=self.msg10,width=90,font=("Helvetica",16),anchor="w") #靠左對齊 
        self.label10.pack(pady=1)
        
        self.label11 = tk.Label(self.frame1, text=self.msg11,width=90,font=("Helvetica",16),anchor="w")
        self.label11.pack(pady=2)
        
        self.label12 = tk.Label(self.frame1, text=self.msg12,width=90,font=("Helvetica",16),anchor="w")
        self.label12.pack(pady=3)       
        
        # 下區域內容
        self.label20 = tk.Label(self.frame2, text=self.detect,width=90,font=("Helvetica",16),anchor="c") #靠中間
        self.label20.pack()   

        rospy.init_node('locobot_compare', anonymous=True)
      
        rospy.Subscriber("result_csm", String, self.callback_csm)
        rospy.Subscriber("result_17", String, self.callback_17)

        # rospy.Subscriber("result_csm", String, self.callback_csm)
        # rospy.Subscriber("result_csm", String, self.callback_17)


    def callback_csm(self,data):
        if self.f1_count%3==0:
            if self.f1_count_bool==0:
                self.msg0="result csm: "+textwrap.fill(data.data,width=130)
                self.label0.config(text= self.msg0)
            else:
                self.msg0="result csm: "+textwrap.fill(data.data,width=130)
                self.label0.config(text= self.msg1)
                self.label1.config(text= self.msg2)
                self.label2.config(text= self.msg0)

        if self.f1_count%3==1:
            if self.f1_count_bool==0:
                self.msg1="result csm: "+textwrap.fill(data.data,width=130)
                self.label1.config(text= self.msg1)
            else:
                self.msg1="result csm: "+textwrap.fill(data.data,width=130)
                self.label0.config(text= self.msg2)
                self.label1.config(text= self.msg0)
                self.label2.config(text= self.msg1)

        if self.f1_count%3==2:
            if self.f1_count_bool==0:
                self.msg2="result csm: "+textwrap.fill(data.data,width=130)
                self.label2.config(text= self.msg2)
            else:
                self.msg2="result csm: "+textwrap.fill(data.data,width=130)
                self.label0.config(text= self.msg0)
                self.label1.config(text= self.msg1)
                self.label2.config(text= self.msg2)
            if self.f1_count_bool==0:
                self.f1_count_bool=1

        self.f1_count=self.f1_count%3+1
        flash=np.fromstring(data.data,dtype=float,sep=" ")-self.target_freq
        if len(flash[(flash[:]<self.constriction) & (flash[:]>-self.constriction)])>self.target_freq_count:
            self.res_csm_sign=1
        else:
            self.res_csm_sign=0
        Detect_frequence.safe_or_danger(self)

    def callback_17(self,data):
        if self.f2_count%3==0:
            if self.f2_count_bool==0:
                self.msg10="result 17: "+textwrap.fill(data.data,width=130)
                self.label10.config(text= self.msg10)
            else:
                self.msg10="result 17: "+textwrap.fill(data.data,width=130)
                self.label10.config(text= self.msg11)
                self.label11.config(text= self.msg12)
                self.label12.config(text= self.msg10)

        if self.f2_count%3==1:
            if self.f2_count_bool==0:
                self.msg11="result 17: "+textwrap.fill(data.data,width=130)
                self.label11.config(text= self.msg11)
            else:
                self.msg11="result 17: "+textwrap.fill(data.data,width=130)
                self.label10.config(text= self.msg12)
                self.label11.config(text= self.msg10)
                self.label12.config(text= self.msg11)

        if self.f2_count%3==2:
            if self.f2_count_bool==0:
                self.msg12="result 17: "+textwrap.fill(data.data,width=130)
                self.label12.config(text= self.msg12)
            else:
                self.msg12="result 17: "+textwrap.fill(data.data,width=130)
                self.label10.config(text= self.msg10)
                self.label11.config(text= self.msg11)
                self.label12.config(text= self.msg12)
            if self.f2_count_bool==0:
                self.f2_count_bool=1

        self.f2_count=self.f2_count%3+1
        
        flash=np.fromstring(data.data,dtype=float,sep=" ")-self.target_freq
        if len(flash[(flash[:]<self.constriction) & (flash[:]>-self.constriction)])>self.target_freq_count:
            self.res_17_sign=1
        else:
            self.res_17_sign=0
        Detect_frequence.safe_or_danger(self)

    def safe_or_danger(self):
        # result=self.res_csm_sign-self.res_17_sign
    
        #if len(result[(result[:]<self.constriction) & (result[:]>-self.constriction)])>3:
            #self.label20.config(text="danger",bg="#FF0000")   #red 
        #else:
            #self.label20.config(text="safe",bg="#00FF00")     #green
            
        if self.res_csm_sign==1 and self.res_17_sign==1:
            self.label20.config(text="danger",bg="#FF0000")   #red 
        else:
            self.label20.config(text="safe",bg="#00FF00")     #green
        
if __name__ == "__main__":
    root = tk.Tk()
    app = Detect_frequence(root)
    root.mainloop()
