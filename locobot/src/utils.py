# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 15:12:45 2019

@author: TommyCheng
"""

import numpy as np
import math

from numpy.linalg import inv
from numpy.linalg import norm
import math
from numpy.linalg import solve, norm
from scipy.io.wavfile import read,write
#from snr_seg_one import snr_seg_one
from matplotlib import pyplot
from scipy.signal import find_peaks
import time

def UCAMic(radius,MicNumber):
    mic_theta           = np.arange(0, 2*math.pi, 2*math.pi/MicNumber)
    MicPos = radius*np.array([np.cos(mic_theta),np.sin(mic_theta),np.zeros(6)])
    return MicPos

def Mix_from_mic(MicPos,MicSignal):
    c      = 343.0
    fs     = 16000
    NWIN       = int(2048)
    hopsize    = int(NWIN / 2)                               #50% overlap
    win        = np.hanning(NWIN+1)
    win        = win[:NWIN]
    ## FFT
    NFFT       = int(2048)
    df         = fs/NFFT
    Freqs      = np.arange(0,(NFFT/2)*df,df)

    MicNumber,SorLen = MicSignal.shape
    NumOfFrame = int(2*np.floor(SorLen/NWIN)-1)
    P_half      = np.zeros((MicNumber,len(Freqs),NumOfFrame),dtype=complex)
    source_win  = np.zeros((MicNumber,NWIN))
    source_zp   = np.zeros((MicNumber,NFFT))
    SOURCE_half = np.zeros((6,int(NFFT/2)),dtype=complex)
    for frameNo in range(NumOfFrame):
        t_start = frameNo*hopsize
        tt      = np.arange(int(t_start),int(t_start+NWIN),1)
        for ss in range(MicNumber):
            source_win[ss,:]  = np.multiply(MicSignal[ss,tt],win)
            source_zp[ss,:]   = np.concatenate((source_win[ss,:],np.zeros((NFFT-NWIN))))
            SOURCE_half[ss,:] = np.fft.fft(source_zp[ss,:],NFFT)[:int(NFFT/2)]

        for ff in range(len(Freqs)):
             P_half[:,ff,frameNo]=SOURCE_half[:,ff]

    return P_half

# MUSIC Parameter
def MUSIC_Parameter(P_half,fs,select_range):
    MicNo=np.size(P_half,0)
    NWIN=2048
    NFFT=NWIN
    df=fs/NFFT
    Freqs  = np.arange(0,(NFFT/2)*df,df)
    c=343

    length_select_range=len(select_range)
    k = np.divide(2*math.pi*Freqs[select_range],c)
    PN=np.zeros([MicNo,MicNo,length_select_range],dtype=complex)
    eigenvalue_sum = np.zeros(MicNo)
    for ff in range(length_select_range):
        x_1 = P_half[:,select_range[ff],:]
        Rxx=np.dot(x_1,x_1.conj().T)
        [a,b]=np.linalg.eig(Rxx)
        eigenvalue_sum = eigenvalue_sum + a[a.argsort()[::-1]]
    eigenvalue_sum = np.real(eigenvalue_sum)
    #if we don't know how many source are here ...
    # print(eigenvalue_sum)
    # SorNum = EVD_criterion(eigenvalue_sum,200,0.01)
    #print("eigen value:", eigenvalue_sum[0]/eigenvalue_sum[-1])
    #SorNum = EVD_criterion(eigenvalue_sum,4000) ->2000?
    # SorNum = EVD_criterion(eigenvalue_sum, 1000) # artifacts sounds
    SorNum = 1
    #print(eigenvalue_sum)

    if SorNum == 0:
        print('zero source has been detected')
        return 0,0,0
    else:
        for ff in range(length_select_range):
            x_1 = P_half[:,select_range[ff],:]
            Rxx=np.dot(x_1,x_1.conj().T)
            [a,b]=np.linalg.eig(Rxx)
            US = b[:,a.argsort()[::-1]][:,:SorNum]
            PN[:,:,ff] = np.identity(6)-np.dot(US,np.conj(US.T))

        return k,PN,SorNum

# Cost MUSIC

def EVD_criterion(eigenvalue_sum,source_baseline):
    if eigenvalue_sum[0]/eigenvalue_sum[-1] >= source_baseline:
        flag=True
    else:
        flag=False

    if flag ==True:
        counter = 1
        # for i in range(1,6,1):
        #     if eigenvalue_sum[i]/eigenvalue_sum[0] >= magnitude_baseline and eigenvalue_sum[i]/eigenvalue_sum[-1] >= source_baseline:
        #         counter = counter + 1
        #     else:
        #         counter = counter
    else:
        counter = 0

    return counter

def cost_MUSIC(position,MicPos,PN,k):
    cost=0
    NumOfFreqs=len(k)
    for ff in range(NumOfFreqs):
    #for ff in range(6,200):
        w=np.exp(1j*k[ff]*np.dot(position,MicPos))
        cost+=abs(1/np.dot(np.dot(w.conj(),PN[:,:,ff]),w.T))
    return cost

def MUSIC_PSO_localization(P_half,MicPos,SorNum,PN,k):
    inertia=0.6
    correction_factor=1.2
    correction_factor_group=1.6
    Rshare=50
    iterations=5
    particles=72
    swarm =np.zeros((particles,7))
    Ang = np.arange(0,360,30)
    Yang = np.arange(0,90,15)
    Distance_matrix = np.zeros((particles,particles))
    M=np.zeros((particles,particles))
    temp1=np.zeros(2)
    counter=0
    for x in range(12):
        for y in range(6):
            swarm[counter,0:2]=np.array([Ang[x],Yang[y]])
            counter = counter + 1
    for iter  in range(iterations):
        for i in range(particles):
            for j in range(2):
                swarm[i,j] =swarm[i,j] + swarm[i,j+4]

                if j==0 and swarm[i,j] < 0:
                    swarm[i,j]= np.random.randint(360)
                if j==0 and swarm[i,j]> 360:
                    swarm[i,j]=np.random.randint(360)
                if j==1 and swarm[i,j]<=20:
                    swarm[i,j]=10+np.random.randint(60)
                if j==1 and swarm[i,j]>=80:
                    swarm[i,j] =10+ np.random.randint(60)

            kappa = np.array([np.cos(math.pi*swarm[i,0]/180.0)*np.cos(math.pi*swarm[i,1]/180.0),np.sin(math.pi*swarm[i,0]/180.0)*np.cos(math.pi*swarm[i,1]/180.0),np.sin(math.pi*swarm[i,1]/180.0)])
            P_out =cost_MUSIC(kappa,MicPos,PN,k)

            if P_out > swarm[i,6]:
                for q in range(2):
                    swarm[i,q+2] = swarm[i,q]
            swarm[i,6]= P_out
            for j in range(i,particles):
                if j==i:
                    Distance_matrix[i,j]= 0
                else:
                    Distance_matrix[i,j] = norm(swarm[i,0:2]-swarm[j,0:2])

                Distance_matrix[j,i]=Distance_matrix[i,j]

            for z  in range(particles):
                if Distance_matrix[i,z]<Rshare:
                    M[z,i]=1
                else:
                    M[z,i]=0

        Follow_matrix = np.zeros((particles,particles))

        for i in range(particles):
            Decision_matrix = np.multiply(swarm[:,6],M[:,i])
            fbest = np.argmax(Decision_matrix)
            Follow_matrix[i,fbest] = 1
            for q in range(2):
                swarm[i,q+4] = inertia*swarm[i,q+4]+correction_factor*np.random.rand()*(swarm[i,q+2]-swarm[i,q])+correction_factor_group*np.random.rand()*(swarm[fbest,q+2]-swarm[i,q])

        #best_swarm_index = np.argmax(np.sum(Follow_matrix,axis=0))
        peaks , _ =find_peaks(np.sum(Follow_matrix,axis=0))
        index = peaks[np.argsort(swarm[peaks,6])][-SorNum:]
        best_swarm = swarm[index[0],0:2]

        inertia = inertia*0.8
        correction_factor=correction_factor*0.8
        correction_factor_group=correction_factor_group*0.8
        if iter<=1:
            temp1 =best_swarm
        else:
            if norm(best_swarm-temp1) <1:
                break
            else:
                temp1=best_swarm


    return best_swarm[0],best_swarm[1]


def MUSIC_Localization_freqrange_grid_search(MicPos,k,PN,azi_min,azi_max,find_mode=False):

    # 360* 90 ->30sec  180*18->3sec
    azi_step = 3
    yang_step = 5
    Ang = np.arange(azi_min,azi_max,3)
    Yang = np.arange(0,90,5)
    P_out=np.zeros((18,(azi_max-azi_min)/azi_step))
    for theta  in range(len(Ang)):
        for phi in range(len(Yang)):
            kappa = np.array([np.cos(math.pi*Ang[theta]/180.0)*np.cos(math.pi*Yang[phi]/180.0),np.sin(math.pi*Ang[theta]/180.0)*np.cos(math.pi*Yang[phi]/180.0),np.sin(math.pi*Yang[phi]/180.0)])
            P_out[phi,theta] =cost_MUSIC(kappa,MicPos,PN,k)

    MaxValue = np.max(np.max(P_out,axis=1),axis=0)
    location = np.argwhere(P_out==MaxValue)
    azimuth_angle = Ang[location[0][1]]
    elevation_angle =Yang[location[0][0]]
    #print(azimuth_angle,elevation_angle)
    if find_mode == True:
        advance_Ang=np.arange(azimuth_angle-2,azimuth_angle+2,1);
        advance_phi=np.arange(elevation_angle-3,elevation_angle+3,1);
        P_out_advance=np.zeros((4,3))

        for theta  in range(len(advance_Ang)):
            for phi in range(len(advance_phi)):
                    kappa = np.array([np.cos(math.pi*advance_Ang[theta]/180.0)*np.cos(math.pi*advance_phi[phi]/180.0),np.sin(math.pi*advance_Ang[theta]/180.0)*np.cos(math.pi*advance_phi[phi]/180.0),np.sin(math.pi*advance_phi[phi]/180.0)])
                    P_out_advance[phi,theta] =cost_MUSIC(kappa,MicPos,PN,k)

        MaxValue = np.max(np.max(P_out_advance,axis=1),axis=0)
        location = np.argwhere(P_out_advance==MaxValue)
        azimuth_angle = advance_Ang[location[0][1]]
        elevation_angle =advance_phi[location[0][0]]
        return azimuth_angle,elevation_angle

    else:
        return azimuth_angle,elevation_angle

def Multi_MUSIC_Localization_freqrange_grid_search(MicPos,k,PN,SorNum=2,find_mode=False):
    Ang = np.arange(0,360,3)
    Yang = np.arange(0,90,5)
    P_out=np.zeros((18,120))
    for theta  in range(len(Ang)):
        for phi in range(len(Yang)):
            kappa = np.array([np.cos(math.pi*Ang[theta]/180.0)*np.cos(math.pi*Yang[phi]/180.0),np.sin(math.pi*Ang[theta]/180.0)*np.cos(math.pi*Yang[phi]/180.0),np.sin(math.pi*Yang[phi]/180.0)])
            P_out[phi,theta] =cost_MUSIC(kappa,MicPos,PN,k)

    MaxValue = np.max(np.max(P_out,axis=1),axis=0)
    location = np.argwhere(P_out==MaxValue)
    azimuth_angle1 = Ang[location[0][1]]
    elevation_angle1 =Yang[location[0][0]]

    if  location[0][1]<=5:
        thetaselect1 = np.arange(0, location[0][1]+6,1)
        thetaselect2 = np.arange(120-(5-location[0][1]),120,1)
        thetaselect = np.concatenate((thetaselect1,thetaselect2),axis = 0)
    elif  location[0][1]>=115:
        thetaselect1 = np.arange(0, 5-(120-location[0][1]),1)
        thetaselect2 = np.arange(location[0][1]-5,120,1)
        thetaselect = np.concatenate((thetaselect1,thetaselect2),axis = 0)
    else:
        thetaselect = np.arange(location[0][1]-5,location[0][1]+6,1)

    if  location[0][0]>= 14 :
        phiselect = np.arange(location[0][0]-4,18,1)
    elif location[0][0]<= 4:
        phiselect = np.arange(0,location[0][0]+4,1)
    else:
        phiselect = np.arange(location[0][0]-4,location[0][0]+4,1)

    # zero masking arround best position to find second peak
    for theta  in thetaselect:
            for phi in phiselect:
                P_out[phi,theta]=0

    MaxValue2 = np.max(np.max(P_out,axis=1),axis=0)
    location2 = np.argwhere(P_out==MaxValue2)
    azimuth_angle2 = Ang[location2[0][1]]
    elevation_angle2 =Yang[location2[0][0]]

    if find_mode == True:
        advance_Ang1=np.arange(azimuth_angle-2,azimuth_angle+2,1);
        advance_phi1=np.arange(elevation_angle-3,elevation_angle+3,1);
        advance_Ang2=np.arange(azimuth_angle2-2,azimuth_angle2+2,1);
        advance_phi2=np.arange(elevation_angle2-3,elevation_angle2+3,1);
        P_out_advance=np.zeros((4,6))
        P_out_advance2=np.zeros((4,6))

        for theta  in range(len(advance_Ang1)):
            for phi in range(len(advance_phi1)):
                    kappa = np.array([np.cos(math.pi*advance_Ang1[theta]/180.0)*np.cos(math.pi*advance_phi1[phi]/180.0),np.sin(math.pi*advance_Ang1[theta]/180.0)*np.cos(math.pi*advance_phi1[phi]/180.0),np.sin(math.pi*advance_phi1[phi]/180.0)])
                    P_out_advance[phi,theta] =cost_MUSIC(kappa,MicPos,PN,k)

        MaxValue3 = np.max(np.max(P_out_advance,axis=1),axis=0)
        location3 = np.argwhere(P_out_advance==MaxValue3)
        azimuth_angle1 = advance_Ang[location3[0][1]]
        elevation_angle1 =advance_phi[location3[0][0]]

        for theta  in range(len(advance_Ang2)):
            for phi in range(len(advance_phi2)):
                    kappa = np.array([np.cos(math.pi*advance_Ang2[theta]/180.0)*np.cos(math.pi*advance_phi2[phi]/180.0),np.sin(math.pi*advance_Ang2[theta]/180.0)*np.cos(math.pi*advance_phi2[phi]/180.0),np.sin(math.pi*advance_phi2[phi]/180.0)])
                    P_out_advance2[phi,theta] =cost_MUSIC(kappa,MicPos,PN,k)

        MaxValue4 = np.max(np.max(P_out_advance2,axis=1),axis=0)
        location4 = np.argwhere(P_out_advance2==MaxValue4)
        azimuth_angle2 = advance_Ang[location4[0][1]]
        elevation_angle2 =advance_phi[location4[0][0]]
        return azimuth_angle1,elevation_angle1,azimuth_angle2,elevation_angle2
    else:
        return azimuth_angle1,elevation_angle1,azimuth_angle2,elevation_angle2


def MUSIC_Localization_freqrange_theta_given_phi(MicPos,input_phi,k,PN,azi_min,azi_max,find_mode=False):
    Ang = np.arange(azi_min,azi_max,3)
    Yang = np.arange(input_phi-5,input_phi+5,1)
    P_out=np.zeros((10,120))

    for theta  in range(len(Ang)):
        for phi in range(len(Yang)):
            kappa = np.array([np.cos(math.pi*Ang[theta]/180.0)*np.cos(math.pi*Yang[phi]/180.0),np.sin(math.pi*Ang[theta]/180.0)*np.cos(math.pi*Yang[phi]/180.0),np.sin(math.pi*Yang[phi]/180.0)])
            P_out[phi,theta] =cost_MUSIC(kappa,MicPos,PN,k)

    MaxValue = np.max(np.max(P_out,axis=1),axis=0)
    location = np.argwhere(P_out==MaxValue)
    azimuth_angle = Ang[location[0][1]]
    elevation_angle =Yang[location[0][0]]
    if find_mode==True:
        advance_Ang=np.arange(azimuth_angle-2,azimuth_angle+2,1)
        P_out_advance=np.zeros(4)
        for theta2  in range(len(advance_Ang)):
            kappa = np.array([np.cos(math.pi*advance_Ang[theta2]/180.0)*np.cos(math.pi*elevation_angle/180.0),np.sin(math.pi*advance_Ang[theta2]/180.0)*np.cos(math.pi*elevation_angle/180.0),np.sin(math.pi*elevation_angle/180.0)])
            P_out_advance[theta2] =cost_MUSIC(kappa,MicPos,PN,k)

        index = np.argmax(P_out_advance)
        azimuth_angle = advance_Ang[index]
        return azimuth_angle,elevation_angle
    else:
        return azimuth_angle,elevation_angle

def Multi_MUSIC_Localization_freqrange_theta_given_phi(MicPos,input_phi,k,PN,SorNum=2):
    Ang = np.arange(0,360,3)
    Yang1 = np.arange(input_phi[0]-5,input_phi[0]+5,1)
    Yang2 =  np.arange(input_phi[1]-5,input_phi[1]+5,1)
    P_out=np.zeros((10,120))
    P_out2=np.zeros((10,120))
    for theta  in range(len(Ang)):
        for phi in range(len(Yang)):
            kappa = np.array([np.cos(math.pi*Ang[theta]/180.0)*np.cos(math.pi*Yang[phi]/180.0),np.sin(math.pi*Ang[theta]/180.0)*np.cos(math.pi*Yang[phi]/180.0),np.sin(math.pi*Yang[phi]/180.0)])
            P_out[phi,theta] =cost_MUSIC(kappa,MicPos,PN,k)
    MaxValue = np.max(np.max(P_out,axis=1),axis=0)
    location = np.argwhere(P_out==MaxValue)
    azimuth_angle = Ang[location[0][1]]
    elevation_angle =Yang[location[0][0]]

    for theta  in range(len(Ang)):
        for phi in range(len(Yang)):
            kappa = np.array([np.cos(math.pi*Ang[theta]/180.0)*np.cos(math.pi*Yang2[phi]/180.0),np.sin(math.pi*Ang[theta]/180.0)*np.cos(math.pi*Yang2[phi]/180.0),np.sin(math.pi*Yang2[phi]/180.0)])
            P_out2[phi,theta] =cost_MUSIC(kappa,MicPos,PN,k)

    MaxValue2 = np.max(np.max(P_out2,axis=1),axis=0)
    location2 = np.argwhere(P_out2==MaxValue2)
    azimuth_angle2 = Ang[location2[0][1]]
    elevation_angle2 =Yang2[location2[0][0]]


    return azimuth_angle,elevation_angle,azimuth_angle2,elevation_angle2

def MUSIC_Localization_freqrange_theta_constant_phi(MicPos,phi,k,PN,find_mode=False):
    Ang = np.arange(0,360,3)
    P_out=np.zeros(120)
    P_out_advance=np.zeros(4)
    for theta  in range(len(Ang)):
        kappa = np.array([np.cos(math.pi*Ang[theta]/180.0)*np.cos(math.pi*phi/180.0),np.sin(math.pi*Ang[theta]/180.0)*np.cos(math.pi*phi/180.0),np.sin(math.pi*phi/180.0)])
        P_out[theta] =cost_MUSIC(kappa,MicPos,PN,k)

    index = np.argmax(P_out)
    azimuth_angle = Ang[index]
    if find_mode ==True:
        advance_Ang=np.arange(azimuth_angle-2,azimuth_angle+2,1)
        for theta2  in range(len(advance_Ang)):
            kappa = np.array([np.cos(math.pi*advance_Ang[theta2]/180.0)*np.cos(math.pi*phi/180.0),np.sin(math.pi*advance_Ang[theta2]/180.0)*np.cos(math.pi*phi/180.0),np.sin(math.pi*phi/180.0)])
            P_out_advance[theta2] =cost_MUSIC(kappa,MicPos,PN,k)
        index = np.argmax(P_out_advance)
        azimuth_angle = advance_Ang[index]
        return azimuth_angle
    else:
        return azimuth_angle

def Multi_MUSIC_Localization_freqrange_theta_constant_phi(MicPos,phi,k,PN,SorNum=2,find_mode=False):

    Ang = np.arange(0,360,3)
    P_out=np.zeros(120)
    P_out_advance=np.zeros(4)
    P_out_advance2=np.zeros(4)

    for theta in range(len(Ang)):
        kappa  = np.array([np.cos(math.pi*Ang[theta]/180.0)*np.cos(math.pi*phi/180.0),np.sin(math.pi*Ang[theta]/180.0)*np.cos(math.pi*phi/180.0),np.sin(math.pi*phi/180.0)])
        #kappa2 = np.array([np.cos(math.pi*Ang[theta]/180.0)*np.cos(math.pi*phi[1]/180.0),np.sin(math.pi*Ang[theta]/180.0)*np.cos(math.pi*phi[1]/180.0),np.sin(math.pi*phi[1]/180.0)])
        P_out[theta] =cost_MUSIC(kappa,MicPos,PN,k)

    # avoid maxima at mostleft and mostright

    P_out = np.concatenate((np.concatenate((np.array([P_out[-1]]),P_out),axis=0),np.array([P_out[0]])),axis=0)
    '''
    pyplot.figure()
    pyplot.plot(P_out)
    pyplot.show()
    '''
    peaks , _ =find_peaks(P_out)
    #peaks , _ =find_peaks(P_out)
    index = peaks[np.argsort(P_out[peaks])][-SorNum:]
    index = index - 1

    if  Ang[index[0]] <=  Ang[index[1]]:
        azimuth_angle= Ang[index[0]]
        azimuth_angle2 = Ang[index[1]]
    else:
        azimuth_angle= Ang[index[1]]
        azimuth_angle2 = Ang[index[0]]

    advance_Ang=np.arange(azimuth_angle-2,azimuth_angle+2,1);
    advance_Ang2=np.arange(azimuth_angle2-2,azimuth_angle2+2,1);

    if find_mode == True:
        for theta2  in range(len(advance_Ang)):
            kappa = np.array([np.cos(math.pi*advance_Ang[theta2]/180.0)*np.cos(math.pi*phi/180.0),np.sin(math.pi*advance_Ang[theta2]/180.0)*np.cos(math.pi*phi/180.0),np.sin(math.pi*phi/180.0)])
            P_out_advance[theta2] =cost_MUSIC(kappa,MicPos,PN,k)
        index = np.argmax(P_out_advance)
        azimuth_angle = advance_Ang[index]

        for theta2  in range(len(advance_Ang2)):
            kappa = np.array([np.cos(math.pi*advance_Ang2[theta2]/180.0)*np.cos(math.pi*phi/180.0),np.sin(math.pi*advance_Ang2[theta2]/180.0)*np.cos(math.pi*phi/180.0),np.sin(math.pi*phi/180.0)])
            P_out_advance2[theta2] =cost_MUSIC(kappa,MicPos,PN,k)
        index = np.argmax(P_out_advance2)
        azimuth_angle2 = advance_Ang2[index]

        return azimuth_angle,azimuth_angle2
    else:
        return azimuth_angle,azimuth_angle2

def DOA(MicSignal,Max_delay,MIC_GROUP,tdoa_matrix,tdoa_measures,fs):
    tau = [0] * 5
    len_of_sig= len(MicSignal[0])
    n = len_of_sig*2
    MicSignal = np.fft.rfft(MicSignal, n)

    # estimate each group of delay
    # gcc_phat
    interp = 7
    max_tau = Max_delay
    for i, v in enumerate(MIC_GROUP):
        SIG = MicSignal[v[0]]
        RESIG = MicSignal[v[1]]
        R = SIG * np.conj(RESIG)
        cc = np.fft.irfft(R / np.abs(R), n=(interp * n))
        max_shift = int(interp * n/2 )
        if max_tau:
            max_shift = np.minimum(int(interp * fs * max_tau), max_shift)
        cc = np.concatenate((cc[-max_shift:], cc[:max_shift+1]))
        # find max cross correlation index
        shift = np.argmax(np.abs(cc)) - max_shift
        tau[i] = shift / float(interp * fs)

        # least square solution of (cos, sin)
    sol = np.linalg.pinv(tdoa_matrix).dot( \
            (tdoa_measures * np.array(tau)).reshape(5, 1))
    phi_in_rad = min( sol[0] / math.cos(math.atan2(sol[1],sol[0]) ), 1)

    # phi in degree
    phi = 90 - np.rad2deg( math.asin(phi_in_rad))
    direction = [(math.atan2(sol[1], sol[0])/math.pi*180.0 + 177.0) % 360, phi]

    return direction
############################################################
def combine_information(array1_center,array2_center,array1_input_theta,array2_input_theta):
    center_distance =norm(array1_center-array2_center)
    distance_source_to_array2 = center_distance/np.sin(math.pi*(array2_input_theta-array1_input_theta)/180.0)*np.sin(math.pi*array1_input_theta/180.0)
    distance_source_to_array1 = center_distance/np.sin(math.pi*(array2_input_theta-array1_input_theta)/180.0)*np.sin(math.pi*array2_input_theta/180.0)
    sorPos_array1 = array1_center + distance_source_to_array1* np.array([np.cos(math.pi*array1_input_theta/180.0),np.sin(math.pi*array1_input_theta/180.0)])
    sorPos_array2 = array2_center + distance_source_to_array2* np.array([np.cos(math.pi*array2_input_theta/180.0),np.sin(math.pi*array2_input_theta/180.0)])
    error = sorPos_array2-sorPos_array1
    print(error)
    return sorPos_array1,sorPos_array2

############################################################
if __name__ == '__main__':
    MicNumber = 6
    radius = 0.047
    select_range= np.arange(256,384,1)
    MicPos = UCAMic(radius,MicNumber)
    P_half = Mix_3D_pro_function_one_source_simulation(MicPos)
    t_start=time.time()



    #k,PN=MUSIC_Parameter(P_half,16000,1,select_range)
    #azimuth_angle,elevation_angle=MUSIC_Grid_Search(MicPos,PN,k)
    #azimuth_angle,elevation_angle=MUSIC_Localization_freqrange_grid_search(P_half,MicPos,1,select_range)
    #azimuth_angle,elevation_angle=MUSIC_Localization_freqrange_theta_constant_phi(P_half,MicPos,1,select_range,20)
    #azimuth_angle,elevation_angle=MUSIC_PSO_localization(P_half,MicPos,1,select_range)
    tend=time.time()
    print(azimuth_angle,elevation_angle,tend-t_start)
    #azimuth,elevation,swarm= MUSIC_PSO_localization(P_half,MicPos,1)
    #azimuth_angle,elevation_angle=MUSIC_Localization(P_half,MicPos,1)
