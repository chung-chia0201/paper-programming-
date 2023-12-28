#!/usr/bin/env python3
#
## Copyright 2023 NYCU, Chung-Chia Chen
##
## *****************************************************
##  DESCRIPTION :
##
##
#
import time
import threading   
import numpy as np
import pyaudio
import os
import logging   
import math
# from pixel_ring import pixel_ring
import socket
# import mraa
from scipy import signal

try:
    # python2 supporting
    import Queue
except:
    # python3
    import queue as Queue

logger              = logging.getLogger('uca')

# en = mraa.Gpio(12)
# en.dir(mraa.DIR_OUT)
# en.write(0)
# pixel_ring.set_brightness(20)


class UCA(object):
    SOUND_SPEED = 343 #聲音在攝氏20度的速度
    """
    UCA (Uniform Circular Array)

     
    """
    def __init__(self, fs=8000, nframes=2000, num_mics=6
                    , quit_event=None, name='respeaker-7'):
        self.fs         = fs
        self.nframes    = nframes
        self.nchannels  = (num_mics + 2 if name == 'respeaker-7' else num_mics)
        self.num_mics   = num_mics
        self.delays     = None
        self.pyaudio_instance = pyaudio.PyAudio()

        self.device_idx = None
        for i in range(self.pyaudio_instance.get_device_count()):
            dev  = self.pyaudio_instance.get_device_info_by_index(i)
            name = dev['name'].encode('utf-8')
            print(i, name, dev['maxInputChannels'], dev['maxOutputChannels'])
            if dev['maxInputChannels'] == self.nchannels:
                print('Use {}'.format(name))
                self.device_idx = i
                break

        if self.device_idx is None:
            raise ValueError('Wrong #channels of mic array!')

        self.stream = self.pyaudio_instance.open(
            input       = True,
            start       = False,
            format      = pyaudio.paInt16,
            channels    = self.nchannels,
            rate        = self.fs,
            frames_per_buffer   = int(self.nframes),
            stream_callback     = self._callback,
            input_device_index  = self.device_idx
        )

        self.quit_event = quit_event if quit_event else threading.Event()

        # multi-channels input
        self.listen_queue = Queue.Queue()

        self.active = False

    def listen(self, duration=9, timeout=2):
        self.listen_queue.queue.clear()
        self.start()

        logger.info('Start Listening')

        def _listen():
            """
            Generator for input signals
            """
            try:
                data = self.listen_queue.get(timeout=timeout)    
                while data and not self.quit_event.is_set():
                    yield data
                    data = self.listen_queue.get(timeout=timeout)
            except Queue.Empty:
                pass
            self.stop()

        return _listen()
    
    def start(self):
        if self.stream.is_stopped():
            self.stream.start_stream()

    def stop(self):
        if self.stream.is_active():
            self.stream.stop_stream()

    def close(self):
        self.quit()
        self.stream.close()
        # pixel_ring.off()

    def quit(self):
        self.status = 0     # flag down everything
        #self.quit_event.set()
        self.listen_queue.put('') # put logitical false into queue

    def _callback(self, in_data, frame_count, time_info, status):

        self.listen_queue.put(in_data)

        return None, pyaudio.paContinue

def radix_2_fft(x):
    N = len(x)
    
    if N <= 1:
        return x
    
    even = radix_2_fft(x[0::2])
    odd = radix_2_fft(x[1::2])
    
    factor = np.exp(-2j * np.pi * np.arange(N) / N)
    
    first_half = even + factor[:N//2] * odd
    second_half = even + factor[N//2:] * odd
    
    return np.concatenate([first_half, second_half])

def freq_compution(raw_data):
    max_freq_all=np.zeros(6)
    data_len=8192
    fs=8000
    correct_data=raw_data*2**(-15)
    for num_mic in range(6):
        y_fft =radix_2_fft(correct_data[num_mic::8])
        y_fft = np.abs(y_fft) / data_len
        y_fft = y_fft[:data_len // 2]
        y_fft[1:-1] = 2 * y_fft[1:-1]
        max_index=np.argmax(y_fft,axis=0)
        max_freq=max_index*fs/data_len
        max_freq_all[num_mic]=max_freq
    return max_freq_all
    
def main():
    logging.basicConfig(level=logging.DEBUG)   
    flag =0
    q = threading.Event()
    uca=UCA(fs=8000, nframes=2048*4, num_mics=6, quit_event=q, name='respeaker-7')
    p_temp =np.zeros((6,2048*4))
    listenflag = 1
    recorderror_flag=1
    count = 0

    try:
        while True:
            chunks=uca.listen()
            for chunk in chunks:
                count+=1
                p_tempbuff=np.frombuffer(chunk,'Int16')
                for i in range(6):
                    p_temp[i]=p_tempbuff[i::8]

                    if np.max(np.abs(p_temp[i]))==0:
                        recorderror_flag=0
                        break
                    if max(np.abs(p_temp[i]))>32768:
                        recorderror_flag=0
                        break

                if recorderror_flag==0:
                    listenflag=0
                    break
                else:
                    listenflag=1
                uca.stream.stop_stream()
                xx=np.frombuffer(chunk,'Int16')
                fft_result=freq_compution(xx)
                print(fft_result)
                send_data=str(fft_result)
                send_data=send_data.replace(send_data[-1],"")
                send_data=send_data.replace(send_data[0],"")
                conn.send(send_data.encode())
                uca.stream.start_stream()

            if listenflag==0:
                uca.close()
                del chunks,uca
                uca=UCA(fs=8000, nframes=2048*4, num_mics=6, quit_event=q, name='respeaker-7')
                print('breakdown recording')
            else:
                pass
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('Quit')
        q.set()
    finally:
        uca.close()

if __name__ == '__main__':
    HOST = '172.20.10.2' # The respeaker ip 
    PORT = 8001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((HOST, PORT))
    s.bind((HOST, PORT))
    print ('Respeaker Server at: %s:%s' %(HOST, PORT))
    print ('wait for connection...')
    s.listen(5)
    conn,addr=s.accept()
    main()
