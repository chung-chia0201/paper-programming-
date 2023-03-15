#!/usr/bin/env python3
#
## Copyright 2019 PME
##
## *****************************************************
##  DESCRIPTION :
##
##
#
import time
import threading   ##平行化處理
import numpy as np
import pyaudio
import os
import logging   ##debug 用
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
    def __init__(self, fs=16000, nframes=2000, num_mics=6
                    , quit_event=None, name='respeaker-7'):
        self.fs         = fs
        self.nframes    = nframes
        self.nchannels  = (num_mics + 2 if name == 'respeaker-7' else num_mic)
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

    def listen(self, duration=9, timeout=1):
        self.listen_queue.queue.clear()
        self.start()

        logger.info('Start Listening')

        def _listen():
            """
            Generator for input signals
            """
            try:
                data = self.listen_queue.get(timeout=timeout)    #取出queue,timeout可設定等待時間
                while data and not self.quit_event.is_set():
                    yield data
                    data = self.listen_queue.get(timeout=timeout)
            except Queue.Empty:
                pass
            self.stop()

        return _listen()
        ##看到這   
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
        #pyaudio.paContinue = 0 There is more audio data to come
        #pyaudio.paContinue = 1 This was the last block of audio data



def task(quit_event,sockets,flag):
    # DEBUG
    # from scipy.io.wavfile import write
    uca = UCA(fs=16000, nframes=2048, num_mics=6,quit_event=quit_event, name='respeaker-7')
    p_temp =np.zeros((6,2048))
    listenflag = 1
    count = 0

    conn, addr = s.accept() # server connect to client
    if flag==1:
        a = 0
        while not quit_event.is_set():
            chunks = uca.listen()
            for chunk in chunks:
                a = a+1
                if (a==1 or a==2):
                    # sockets.sendall(chunk)
                    conn.sendall(chunk)
                else:
                    pass
                if a==4:
                    a=0
    else:
        while not quit_event.is_set():
            recorderror_flag = 1
            chunks=uca.listen()
            for chunk in chunks:
                count = count+1
                p_tempbuff = np.frombuffer(chunk,'Int16')
                for i in range(6):
                    p_temp[i]=p_tempbuff[i::8]
                    # print(np.max(np.abs(p_temp[i]))) 有資料 
                    if np.max(np.abs(p_temp[i]))==0:
                        recorderror_flag = 0
                        break

                    if np.max(np.abs(p_temp[i]))>32768:
                        recorderror_flag = 0
                        break

                if recorderror_flag == 0:
                    listenflag = 0
                    break
                else:
                    listenflag = 1
                    # sockets.sendall(chunk)
                    conn.sendall(chunk)
                    print(np.max(np.abs(p_temp),axis=1),count)

            if listenflag == 0:
                uca.close()
                del chunks,uca
                uca = UCA(fs=16000, nframes=2048, num_mics=6,quit_event=quit_event, name='respeaker-7')
                print('breakdown recording')
            else:
                pass
        #s.close()
    #uca.close()

def main():
    logging.basicConfig(level=logging.DEBUG)   ##將錯誤訊息儲存起來(.log檔案) 加filename
    flag =0
    q = threading.Event()
    t = threading.Thread(target=task, args=(q,s,flag))  #平行化處理
    t.start()
    while True:
        # data = s.recv(1024).decode('utf-8')
        #print(data)
        # pixel_ring.wakeup(float(data)+25.0)
        #time.sleep(1)
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            print('Quit')
            q.set()
            break
    # wait for the thread
    t.join()

if __name__ == '__main__':
    HOST = '172.20.10.2' # The respeaker ip 
    PORT = 8001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((HOST, PORT))
    s.bind((HOST, PORT))
    print ('Respeaker Server at: %s:%s' %(HOST, PORT))
    print ('wait for connection...')
    s.listen(5)
    main()
