#!/usr/bin/env python3
#
## Copyright 2023 NYCU, Chung-Chia Chen
##
## *****************************************************
##  DESCRIPTION :
##  This is a test of the available sample rate of ReSpeaker Core v2.0.
##
#

import numpy as np
import pyaudio

test_interval=5
test_sample_rate=[(i+1)*1000 for i in range(test_interval)]
available_sample_rate=[]
print("test sample rate: ",test_sample_rate)

nchannels=2
num_mics=2
nframes=2048

for sample_rate in test_sample_rate:
    try:
        pyaudio_instance = pyaudio.PyAudio()
        stream = pyaudio_instance.open(format=pyaudio.paInt16, channels=nchannels, rate=sample_rate, input=True, frames_per_buffer=nframes)
        stream.start_stream()
        buffer = stream.read(nframes)
        temp_buffer = np.frombuffer(buffer, dtype=np.int16)
        listen_queue=np.zeros((num_mics,nframes))
        for num_mic in range(num_mics):
            listen_queue[num_mic] = temp_buffer[num_mic::nchannels]
        print("max signal: ", [max(listen_queue[i]) for i in range(num_mics)],"\t sample rate: ",sample_rate)
        stream.stop_stream()
        available_sample_rate.append(sample_rate)
    except:
        pass
print("available sample rate: ",available_sample_rate)