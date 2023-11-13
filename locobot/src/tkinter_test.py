import tkinter as tk
##寫成class且每秒更新狀態的視窗

class TwoAreaGUI:
    def __init__(self, root):
        self.root = root
        root.title("每秒更新狀態")

        #上區域框架
        self.top_frame=tk.Frame(root)
        self.top_frame.pack(side="top",fill="both",expand=True)

        self.frame1 = tk.Frame(self.top_frame,bg="red", width=200, heigh=100, borderwidth=2,  relief="solid")
        self.frame2 = tk.Frame(self.top_frame,bg="green", width=200, heigh=100, borderwidth=2,  relief="solid")
        self.frame3 = tk.Frame(self.top_frame,bg="blue", width=200, heigh=100, borderwidth=2,  relief="solid")
        self.frame4 = tk.Frame(self.top_frame,bg="yellow", width=200, heigh=100, borderwidth=2,  relief="solid")

        self.frame1.grid(row=0,column=0,padx=10,pady=10)
        self.frame2.grid(row=0,column=1,padx=10,pady=10)
        self.frame3.grid(row=1,column=0,padx=10,pady=10)
        self.frame4.grid(row=1,column=1,padx=10,pady=10)

        #下區域框架
        self.bottom_frame=tk.Frame(root)
        self.bottom_frame.pack(side="top",fill="both",expand=True)

        self.frame5 = tk.Frame(self.bottom_frame,bg="orange", width=200, heigh=100, borderwidth=2,  relief="solid")
        self.frame6 = tk.Frame(self.bottom_frame,bg="purple", width=200, heigh=100, borderwidth=2,  relief="solid")

        self.frame5.grid(row=0,column=0,padx=10,pady=10)
        self.frame6.grid(row=0,column=1,padx=10,pady=10)

        # # 上區域資訊
        # self.label1 = tk.Label(self.frame1, text="區域1: 初始資訊1")
        # self.label1.pack()

        # # 下區域內容
        # self.label2 = tk.Label(self.frame2, text="區域2: 初始資訊2")
        # self.label2.pack()        


if __name__ == "__main__":
    root = tk.Tk()
    app = TwoAreaGUI(root)
    root.mainloop()

