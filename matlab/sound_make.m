clc;clear;close all;

% N=8000;                              %喇叭的頻率響應

f=3520
f=11000-f

fs=44000;

plot_signal_len=440*0.5;
time_length=180;      

time_array=0:1/fs:time_length;
time_array=time_array(1:end-1);
freq_array=0:1/time_length:fs/2;
freq_array=freq_array(1:end-1);

signal=sin(2*pi*f*time_array);

figure1=figure;
subplot(2,1,1)
text="signal: "+ num2str(f)+"hz(local) time domain";
plot(time_array(1:plot_signal_len),signal(1:plot_signal_len));title(text);xlabel("time(s)");ylabel("ampltuide")

subplot(2,1,2)
data_len=length(signal);
y_fft=fft(signal);
y_fft=abs(y_fft/data_len);
y_fft=y_fft(1:data_len/2);
y_fft(2:end-1)=2*y_fft(2:end-1);
text="signal:"+num2str(f)+" hz frequence domain";
plot(freq_array,y_fft);title(text);xlabel("frequence");ylabel("ampltuide");ylim([0 1.2]);

% sound(signal, fs)

% filename_wav="test_sound_fs_"+num2str(fs)+"_freq_"+num2str(f)+".wav";
filename_wav="alarm_sound_freq_"+num2str(f)+".wav";

filename_mat="test_sound_fs_"+num2str(fs)+"_freq_"+num2str(f)+".mat";

% audiowrite(filename_wav,signal,fs)
% save(filename_mat)
