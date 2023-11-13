import numpy as np
import pyaudio
import queue as Queue
import time
import socket
##從5繼承來的，嘗試socket

class detect_freq(object):

    def __init__(self, fs=11000, nframes=2048*8, num_mics=2):
        self.fs         = fs
        self.nframes    = nframes
        self.nchannels  = num_mics  #注意respeaker上是8
        self.num_mics   = num_mics
        self.delays     = None
        self.pyaudio_instance = pyaudio.PyAudio()

        self.stream = self.pyaudio_instance.open(format=pyaudio.paInt16, channels=self.nchannels, rate=self.fs, input=True,
                        frames_per_buffer=self.nframes)     

    def listen(self):
        # print("start")
        self.listen_queue=np.zeros((self.num_mics,self.nframes))
        self.stream.start_stream()
        buffer = self.stream.read(self.nframes)
        temp_buffer = np.frombuffer(buffer, dtype=np.int16)
        for num_mic in range(self.num_mics):
            self.listen_queue[num_mic] = temp_buffer[num_mic::self.nchannels]
        self.stream.stop_stream()
        # print("end")
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
        start_time=time.time()   ###計時
        self.listen() 
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
        end_time=time.time()
        spend_time=format(end_time-start_time)
        return max_freq_all,spend_time
    
def main():
    count=0
    times=5
    # while count<times:
    #     start_detect=detect_freq()
    #     max_freq_all,spend_time=start_detect.freq_compution()
    #     print("max frequence:",max_freq_all,"spend time:",spend_time,"sec")
    #     count+=1

    while True:
        start_detect=detect_freq()
        max_freq_all,spend_time=start_detect.freq_compution()     ###傳送這兩個
        s.send(max_freq_all.encode())
        print("max frequence:",max_freq_all,"spend time:",spend_time,"sec")
        count+=1

# main()

if __name__ == '__main__':
    HOST = '172.20.10.2' # The respeaker ip 
    PORT = 8001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    # s.bind((HOST, PORT))
    print ('Respeaker Server at: %s:%s' %(HOST, PORT))
    print ('wait for connection...')
    s.listen(5)
    main()

