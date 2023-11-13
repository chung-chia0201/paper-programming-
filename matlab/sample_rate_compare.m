clc;clear;close all;

N1=8;
N2=16;
L=1;

f1=2;
f2=6;

amp1=1;
amp2=1;

signal_shift=320;

time_length=10000;
time_array=linspace(0,1,time_length+1);

time_sample1=0:L/N1:L;
time_sample1=time_sample1(1:end-1);
time_sample2=0:L/N2:L;
time_sample2=time_sample2(1:end-1);

delta_t1=time_length/N1;
delta_t2=time_length/N2;

signal1=amp1*sin(2*pi*f1*time_array);
signal2=amp2*sin(2*pi*f2*time_array);
signal3=signal1+signal2;
signal3=signal3/(amp1+amp2);         %normalized

signal=cat(2,signal3(signal_shift+1:end),signal3(1:signal_shift));

signal_N1=zeros(1,N1);
for i=0:N1-1
    signal_N1(i+1)=signal(delta_t1*i+1);
end

signal_N2=zeros(1,N2);
for i=0:N2-1
    signal_N2(i+1)=signal(delta_t2*i+1);
end

%%frequence domain
freq_array1=0:1/L:N1/2;
freq_array2=0:1/L:N2/2;

fft_N1=fft(signal_N1);
fft_N1=abs(fft_N1/N1);
fft_N1=fft_N1(1:N1/2+1);
fft_N1(2:end-1)=2*fft_N1(2:end-1);

fft_N2=fft(signal_N2);
fft_N2=abs(fft_N2/N2);
fft_N2=fft_N2(1:N2/2+1);
fft_N2(2:end-1)=2*fft_N2(2:end-1);

figure1=figure;
subplot(3,1,1)
text="signal1: "+num2str(f1)+" Hz";
plot(time_array,signal1);title(text);xlabel("time(sec)");ylabel("ampltuide");

subplot(3,1,2)
text="signal2: "+num2str(f2)+" Hz";
plot(time_array,signal2);title(text);xlabel("time(sec)");ylabel("ampltuide");

subplot(3,1,3)
plot(time_array,signal3);title("signal is sum of signal1 and signal2");xlabel("time(sec)");ylabel("ampltuide");

figure2=figure("Name","sample rate 8");
subplot(3,1,1)
hold on
for i=2:N1
    plot([time_sample1(i),time_sample1(i)],[1,-1],"k")
end
text="signal shift "+num2str(signal_shift);
plot(time_array,signal);title(text);xlabel("time(sec)");ylabel("ampltuide");
plot(time_sample1,signal_N1,'bd');
hold off

subplot(3,1,2)
hold on
for i=2:N1
    plot([time_sample1(i),time_sample1(i)],[1,-1],"k")
end
plot(time_sample1,signal_N1,'b');title("respeaker data");xlabel("time(sec)");ylabel("ampltuide");axis([0 1 -1 1]);
plot(time_sample1,signal_N1,'bd');
hold off

subplot(3,1,3)
plot(freq_array1,fft_N1,'-o');title("frequenc domain");xlabel("frequence");ylabel("ampltuide");ylim([0 1]);

f3=figure("Name","sample rate 16");
subplot(3,1,1)
hold on
for i=2:N2
    plot([time_sample2(i),time_sample2(i)],[1,-1],"k")
end
text="signal shift "+num2str(signal_shift);
plot(time_array,signal);title(text);xlabel("time(sec)");ylabel("ampltuide");
plot(time_sample2,signal_N2,'rd');
hold off

subplot(3,1,2)
hold on
for i=2:N2
    plot([time_sample2(i),time_sample2(i)],[1,-1],"k")
end
plot(time_sample2,signal_N2,'r');title("respeaker data");xlabel("time(sec)");ylabel("ampltuide");axis([0 1 -1 1]);
plot(time_sample2,signal_N2,'rd');
hold off

subplot(3,1,3)
plot(freq_array2,fft_N2,'r-o');title("frequenc domain");xlabel("frequence");ylabel("ampltuide");ylim([0 1]);

function fc=fourier_coefficient(signal,n,N)
    k=0:1:N-1;
    fc=complex(1/N*(sum(cos(2*pi*n*k/N).*signal)),1/N*(sum(-sin(2*pi*n*k/N).*signal)));
end


