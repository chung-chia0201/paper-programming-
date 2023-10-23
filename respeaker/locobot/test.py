import tkinter as tk
##寫成class且每秒更新狀態的視窗

class TwoAreaGUI:
    def __init__(self, root):
        self.root = root
        root.title("每秒更新狀態")

        # 上區域
        self.frame1 = tk.Frame(root, borderwidth=2, relief="solid")
        self.frame1.pack(side="top", padx=10, pady=10)
        
        # 下區域
        self.frame2 = tk.Frame(root, borderwidth=2, relief="solid")
        self.frame2.pack(side="top", padx=10, pady=10)

        # 上區域資訊
        self.label1 = tk.Label(self.frame1, text="區域1: 初始資訊1")
        self.label1.pack()
        self.update_area1()

        # 下區域內容
        self.label2 = tk.Label(self.frame2, text="區域2: 初始資訊2")
        self.label2.pack()        
        self.update_area2()

    def update_area1(self):
        new_info = "區域1: 這是新的資訊1"  #在這裡用subscriber
        self.label1.config(text=new_info)
        print(new_info)  # 在控制台中顯示新資訊
        self.root.after(1000, self.update_area1)

    def update_area2(self):
        new_info = "區域2: 這是新的資訊2"
        self.label2.config(text=new_info)
        print(new_info)  # 在控制台中顯示新資訊
        self.root.after(1000, self.update_area2)

if __name__ == "__main__":
    root = tk.Tk()
    app = TwoAreaGUI(root)
    root.mainloop()

