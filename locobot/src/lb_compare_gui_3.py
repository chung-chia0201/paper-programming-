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
        # root.resizable(500,500)
        self.msg30="respeaker csm result:"
        self.msg40="respeaker 17 result:"
        self.msg_detect="detect"

        self.msg31=["0","0","0","0","0","0"]
        self.msg32=["0","0","0","0","0","0"]
        self.msg33=["0","0","0","0","0","0"]
        self.msgs3=[self.msg31,self.msg32,self.msg33]

        self.msg41=["0","0","0","0","0","0"]
        self.msg42=["0","0","0","0","0","0"]
        self.msg43=["0","0","0","0","0","0"]
        self.msgs4=[self.msg41,self.msg42,self.msg43]

        self.res_csm_bool=0
        self.res_17_bool=0

        # self.f1_count=0
        # self.f1_count_bool=0

        # self.f2_count=0
        # self.f2_count_bool=0

        self.constriction=5
        self.target_freq=3520
        self.target_freq_count=3
        self.res_csm_sign=0
        self.res_17_sign=0

        #上區域(偵測有無連接)
        self.top_frame=tk.Frame(root)
        self.top_frame.pack(side="top",fill="both",expand=True)
        self.frame1 = tk.Frame(self.top_frame,bg="red", borderwidth=2, relief="solid")
        self.frame2 = tk.Frame(self.top_frame,bg="green", borderwidth=2, relief="solid")

        self.frame1.grid(row=0,column=0,padx=10,pady=10)
        self.frame2.grid(row=0,column=1,padx=10,pady=10)

        #中區域(偵測結果)
        self.midden_frame=tk.Frame(root)
        self.midden_frame.pack(side="top",fill="both",expand=True)
        self.frame3 = tk.Frame(self.midden_frame, borderwidth=2, relief="solid")
        self.frame4 = tk.Frame(self.midden_frame, borderwidth=2, relief="solid")

        self.frame3.grid(row=0,column=0,padx=10,pady=10)
        self.frame4.grid(row=0,column=1,padx=10,pady=10)

        #中區域當中各三次的檢測結果
        #frame3(left side)
        self.left_frame=tk.Frame(self.frame3)
        self.left_frame.pack(side="top",fill="both",expand=True)
        self.frame30 = tk.Frame(self.left_frame, relief="solid")
        self.left_frame_bottom = tk.Frame(self.left_frame, relief="solid")

        self.frame30.grid(row=0,column=0)
        self.left_frame_bottom.grid(row=1,column=0)

        self.left_frame_bottom_frame=tk.Frame(self.left_frame_bottom)
        self.left_frame_bottom_frame.pack(side="top",fill="both",expand=True)
        self.frame31=tk.Frame(self.left_frame_bottom_frame)
        self.frame32=tk.Frame(self.left_frame_bottom_frame)
        self.frame33=tk.Frame(self.left_frame_bottom_frame)
        self.frames3=[self.frame31,self.frame32,self.frame33]

        self.frame31.grid(row=0,column=1)
        self.frame32.grid(row=0,column=2)
        self.frame33.grid(row=0,column=3)


        #frame4(right side)
        self.right_frame=tk.Frame(self.frame4)
        self.right_frame.pack(side="top",fill="both",expand=True)
        self.frame40 = tk.Frame(self.right_frame, relief="solid")
        self.right_frame_bottom = tk.Frame(self.right_frame, relief="solid")

        self.frame40.grid(row=0,column=0)
        self.right_frame_bottom.grid(row=1,column=0)

        self.right_frame_bottom_frame=tk.Frame(self.right_frame_bottom)
        self.right_frame_bottom_frame.pack(side="top",fill="both",expand=True)
        self.frame41=tk.Frame(self.right_frame_bottom_frame)
        self.frame42=tk.Frame(self.right_frame_bottom_frame)
        self.frame43=tk.Frame(self.right_frame_bottom_frame)
        self.frames4=[self.frame41,self.frame42,self.frame43]

        self.frame41.grid(row=0,column=1)
        self.frame42.grid(row=0,column=2)
        self.frame43.grid(row=0,column=3)

        #下區域(是否觸發警報)
        self.bottom_frame=tk.Frame(root)
        self.bottom_frame.pack(side="top",fill="both",expand=True)
        self.frame5 = tk.Frame(self.bottom_frame, borderwidth=2,  relief="solid")

        self.frame5.grid(row=0,column=0,padx=10,pady=10)

        #上區域資訊
        self.label1 = tk.Label(self.frame1, text="respeaker csm wait for connection ...",width=60,font=("Helvetica",16),bg="#FF0000",anchor="w") #靠左對齊
        self.label1.pack()
        self.label2 = tk.Label(self.frame2, text="respeaker 17 wait for connection ...",width=60,font=("Helvetica",16),bg="#FF0000",anchor="w") #靠左對齊
        self.label2.pack()

        #中區域資訊
        #left side
        self.label30 = tk.Label(self.frame30, text=self.msg30,width=60,font=("Helvetica",16),anchor="w") #靠左對齊
        self.label30.pack()

        self.labels31=[tk.Label(self.frame31, text=msg,width=19,font=("Helvetica",16),anchor="w") for msg in self.msg31]
        self.labels32=[tk.Label(self.frame32, text=msg,width=19,font=("Helvetica",16),anchor="w") for msg in self.msg32]
        self.labels33=[tk.Label(self.frame33, text=msg,width=19,font=("Helvetica",16),anchor="w") for msg in self.msg33]
        self.labels3=[self.labels31,self.labels32,self.labels33]
        [label.pack() for label in self.labels31]
        [label.pack() for label in self.labels32]
        [label.pack() for label in self.labels33]



        #right side
        self.label40 = tk.Label(self.frame40, text=self.msg40,width=60,font=("Helvetica",16),anchor="w") #靠左對齊
        self.label40.pack()
        self.labels41=[tk.Label(self.frame41, text=msg,width=19,font=("Helvetica",16),anchor="w") for msg in self.msg41]
        self.labels42=[tk.Label(self.frame42, text=msg,width=19,font=("Helvetica",16),anchor="w") for msg in self.msg42]
        self.labels43=[tk.Label(self.frame43, text=msg,width=19,font=("Helvetica",16),anchor="w") for msg in self.msg43]
        self.labels4=[self.labels41,self.labels42,self.labels43]
        [label.pack() for label in self.labels41]
        [label.pack() for label in self.labels42]
        [label.pack() for label in self.labels43]

        #下區域資訊
        self.label5 = tk.Label(self.frame5, text=self.msg_detect,width=122,font=("Helvetica",16),anchor="c") #靠中對齊
        self.label5.pack()   

        rospy.init_node('locobot_compare', anonymous=True)
      
        #rospy.Subscriber("result_csm", String, self.callback_csm)
        #rospy.Subscriber("result_csm", String, self.callback_17)

        rospy.Subscriber("result_csm", String, self.callback_csm)
        rospy.Subscriber("result_17", String, self.callback_17)

    def callback_csm(self,data):
        if self.res_csm_bool==0:
            self.res_csm_bool=1
            self.label1.config(text="connect",bg="#00FF00")
        self.msgs3.pop(0)
        self.msgs3.append(np.fromstring(data.data,dtype=float,sep=" "))
        for index_label3,label3 in enumerate(self.labels3):
            for index_label,label in enumerate(label3):
                label.config(text=self.msgs3[index_label3][index_label])

        flash=np.fromstring(data.data,dtype=float,sep=" ")-self.target_freq
        if len(flash[(flash[:]<self.constriction) & (flash[:]>-self.constriction)])>self.target_freq_count:
            self.res_csm_sign=1
        else:
            self.res_csm_sign=0
        Detect_frequence.safe_or_danger(self)

    def callback_17(self,data):
        if self.res_17_bool==0:
            self.res_17_bool=1
            self.label2.config(text="connect",bg="#00FF00")
        self.msgs4.pop(0)
        self.msgs4.append(np.fromstring(data.data,dtype=float,sep=" "))
        for index_label4,label4 in enumerate(self.labels4):
            for index_label,label in enumerate(label4):
                label.config(text=self.msgs4[index_label4][index_label])

        flash=np.fromstring(data.data,dtype=float,sep=" ")-self.target_freq
        if len(flash[(flash[:]<self.constriction) & (flash[:]>-self.constriction)])>self.target_freq_count:
            self.res_17_sign=1
        else:
            self.res_17_sign=0
        Detect_frequence.safe_or_danger(self)

    def safe_or_danger(self):        
        if self.res_csm_sign==1 and self.res_17_sign==1:
            self.label5.config(text="danger",bg="#FF0000")   #red 
        else:
            self.label5.config(text="safe",bg="#00FF00")     #green        

if __name__ == "__main__":
    root = tk.Tk()
    app = Detect_frequence(root)
    root.mainloop()
