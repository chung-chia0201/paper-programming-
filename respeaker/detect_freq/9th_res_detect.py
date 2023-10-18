#!/usr/bin/env python3
#
## Copyright 2023 NYCU, Chung-Chia Chen
##
## *****************************************************
##  DESCRIPTION :
##  This is the server-side(socket) on ReSpeaker Core v2.0, and the IP needs to be changed.
##
#

import numpy as np
import pyaudio
import queue as Queue
import time
import socket

class detect_freq(object):

    def __init__(self, fs=11000, nframes=2048*8, num_mics=6):
        self.fs         = fs
        self.nframes    = nframes
        self.nchannels  = num_mics  
        self.num_mics   = num_mics
        self.delays     = None
        self.pyaudio_instance = pyaudio.PyAudio()

        self.stream = self.pyaudio_instance.open(format=pyaudio.paInt16, channels=self.nchannels, rate=self.fs, input=True,
                        frames_per_buffer=self.nframes)     

    def listen(self):
        self.listen_queue=np.zeros((self.num_mics,self.nframes))
        self.stream.start_stream()
        buffer = self.stream.read(self.nframes)
        temp_buffer = np.frombuffer(buffer, dtype=np.int16)
        for num_mic in range(self.num_mics):
            self.listen_queue[num_mic] = temp_buffer[num_mic::self.nchannels]
        self.stream.stop_stream()
        return

    def radix_2_fft(self,x):
        N = len(x)
        
        if N <= 1:
            return x
        
        even = self.radix_2_fft(x[0::2])
        odd = self.radix_2_fft(x[1::2])
        
        factor = np.exp(-2j * np.pi * np.arange(N) / N)
        
        first_half = even + factor[:N//2] * odd
        second_half = even + factor[N//2:] * odd
        
        return np.concatenate([first_half, second_half])
    
    def freq_compution(self):
        start_time=time.time()   ###timer
        self.listen()            
        end_time_1=time.time()   ###listening time

        max_freq_all=np.zeros(self.num_mics)
        data_len=self.nframes
        self.listen_queue=self.listen_queue*2**(-15)
        for num_mic in range(self.num_mics):
            y_fft =self.radix_2_fft(self.listen_queue[num_mic])
            y_fft = np.abs(y_fft) / data_len
            y_fft = y_fft[:data_len // 2]
            y_fft[1:-1] = 2 * y_fft[1:-1]
            max_index=np.argmax(y_fft,axis=0)
            max_freq=max_index*self.fs/data_len
            max_freq_all[num_mic]=max_freq
        end_time_2=time.time()   ###calculation time

        listen_spend_time=format(end_time_1-start_time)
        fft_spend_time=format(end_time_2-end_time_1)

        return max_freq_all,listen_spend_time,fft_spend_time
    
def main():
    while True:
        conn, addr = s.accept()    
        while True:
            try:
                start_detect=detect_freq()
                max_freq_all,listen_spend_time,fft_spend_time=start_detect.freq_compution()     
                max_freq_all=str(max_freq_all)
                print("max frequence:",max_freq_all,"listen spend time:",listen_spend_time,"sec ","fft spend time:",fft_spend_time,"sec")
                conn.send(max_freq_all.encode())
            except Exception:
                continue
        conn.close()

if __name__ == '__main__':
    HOST = '127.0.0.1' # respeaker ip
    PORT = 8001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((HOST, PORT))
    s.bind((HOST, PORT))
    print ('Respeaker Server at: %s:%s' %(HOST, PORT))
    print ('wait for connection...')
    s.listen(5)
    main()

