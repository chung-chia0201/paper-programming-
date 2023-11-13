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
        self.msg1="result 17: start detect"
        self.f1_count=0
        self.f1_count_bool=0

        self.f2_count=0
        self.f2_count_bool=0

        self.detect="detect"

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

        # 上區域資訊(res_csm)
        self.label0 = tk.Label(self.frame0, text=self.msg0,width=90,font=("Helvetica",16),anchor="w") #靠左對齊 
        self.label1 = tk.Label(self.frame0, text=self.msg0,width=90,font=("Helvetica",16),anchor="w")      
        self.label2 = tk.Label(self.frame0, text=self.msg0,width=90,font=("Helvetica",16),anchor="w")

        self.labels0=[self.label0,self.label1,self.label2]
        # print(self.labels0)
        [label.pack(pady=1) for label in self.labels0]
        self.msgs0=["result csm: start detect","result csm: start detect","result csm: start detect"]

        # 中區域內容(res_17)
        self.label10 = tk.Label(self.frame1, text=self.msg1,width=90,font=("Helvetica",16),anchor="w") #靠左對齊       
        self.label11 = tk.Label(self.frame1, text=self.msg1,width=90,font=("Helvetica",16),anchor="w")       
        self.label12 = tk.Label(self.frame1, text=self.msg1,width=90,font=("Helvetica",16),anchor="w")

        self.labels1=[self.label10,self.label11,self.label12]
        [label.pack(pady=1) for label in self.labels1]
        self.msgs1=["result 17: start detect","result 17: start detect","result 17: start detect"]   
        
        # 下區域內容
        self.label20 = tk.Label(self.frame2, text=self.detect,width=90,font=("Helvetica",16),anchor="c") #靠中間
        self.label20.pack()   

        rospy.init_node('locobot_compare', anonymous=True)
      
        rospy.Subscriber("result_csm", String, self.callback_csm)
        rospy.Subscriber("result_csm", String, self.callback_17)

    def callback_csm(self,data):
        self.msgs0.pop(0)
        self.msgs0.append("result csm: "+textwrap.fill(data.data,width=130))
        for i,v in enumerate(self.labels0):
            # print(v)
            v.config(text=self.msgs0[i])

        flash=np.fromstring(data.data,dtype=float,sep=" ")-self.target_freq
        if len(flash[(flash[:]<self.constriction) & (flash[:]>-self.constriction)])>self.target_freq_count:
            self.res_csm_sign=1
        else:
            self.res_csm_sign=0
        Detect_frequence.safe_or_danger(self)

    def callback_17(self,data):
        self.msgs1.pop(0)
        self.msgs1.append("result 17: "+textwrap.fill(data.data,width=130))
        for i,v in enumerate(self.labels1):
            v.config(text=self.msgs1[i])

        flash=np.fromstring(data.data,dtype=float,sep=" ")-self.target_freq
        if len(flash[(flash[:]<self.constriction) & (flash[:]>-self.constriction)])>self.target_freq_count:
            self.res_17_sign=1
        else:
            self.res_17_sign=0
        Detect_frequence.safe_or_danger(self)

    def safe_or_danger(self):        
        if self.res_csm_sign==1 and self.res_17_sign==1:
            self.label20.config(text="danger",bg="#FF0000")   #red 
        else:
            self.label20.config(text="safe",bg="#00FF00")     #green        

if __name__ == "__main__":
    root = tk.Tk()
    app = Detect_frequence(root)
    root.mainloop()
