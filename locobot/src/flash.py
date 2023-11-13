#!/usr/bin/env python3
## locobot subscriber, 2publisher and 1 subscriber

import rospy

import tkinter as tk

root = tk.Tk()
root.title("flash test")

frame=tk.Frame(root, width=300 ,height=200, borderwidth=2, relief="solid")
frame.pack()

label1 = tk.Label(frame, text="result csm: start detect",font=("Helvetica",16))
label1.grid(row=0,column=0,pady=10)

label2 = tk.Label(frame, text="result csm: end detect",font=("Helvetica",24))
label2.grid(row=1,column=0,pady=15)


root.mainloop()

