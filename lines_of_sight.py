#%%
#Written by: Izel Gediz
#Date of Creation: 16.09.2022
#This code uses data collected in the measurement of the lines of sight of the bolometerchannels which was produced using a 2D Stepping Motor.


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
import re
from scipy.interpolate import pchip_interpolate
#from bolo_radiation import LoadData, PlotAllTimeseries, PlotAllTimeseriesTogether, PlotSingleTimeseries

#%%

def MotorData(save=False):
    x,a,p =np.genfromtxt(motordata, unpack=True)    #x is the position data in mm, a is the "amplitude" data stored and processed by the software, p is the "Phase" data stored and processed by the software
    x_=np.arange(x[0],x[-1],0.00001)
    fit=pchip_interpolate(x,a,x_)
    amp=list(i-min(a) for i in fit)
    plt.plot(x_,amp,'r.--', label='Interpolated signal "Amplitude"')
    signal_edge_list=[np.argwhere(amp>max(amp)/np.e), np.argwhere(amp>max(amp)/10)]
    for signal_edge in signal_edge_list:
        fwhm1, fwhm2=x_[signal_edge[0]],x_[signal_edge[-1]]
        plt.plot(fwhm1,amp[int(signal_edge[0])],'bo')
        plt.plot(fwhm2,amp[int(signal_edge[-1])],'bo')
        fwhm=float(fwhm2-fwhm1)
        plt.plot([fwhm1,fwhm2],[amp[int(signal_edge[0])],amp[int(signal_edge[-1])]], color='blue', label='Width of channel: {} m'.format(float(f'{fwhm:.6f}')))
        
    #plt.plot(x,a,'b.--', label='"Amplitude Data"'.format(float(f'{np.mean(a):.4f}')))
    #plt.plot(x,p, label='"Phase Data": {} V'.format(float(f'{np.mean(p):.4f}')))
    plt.xlabel('Position [m]')
    plt.ylabel('Preprocessed Signal [V]')
    plt.suptitle(motordatatitle)
    plt.legend(loc=1, bbox_to_anchor=(1.4,1))
    fig1= plt.gcf()
    plt.show()
    if save==True:
        fig1.savefig(str(motordataoutfile)+str(filename[:-4])+".pdf", bbox_inches='tight')

#This function takes one channelsignal aquired during a sweep with a lightsource across it and determines
#The width of the signal at different heights after inverting it and substracting the backgroundsignal
def BoloDataWidths(i=1, save=False):
    cut=1000
    y= LoadData(location)["Bolo{}".format(i)][cut:]        #aprox. the first 10 seconds are ignored because due to the motormovement a second peak appeared there
    time = LoadData(location)['Zeit [ms]'][cut:] / 1000
    title='Shot n° {s} // Channel "Bolo {n}" \n {e}'.format(s=shotnumber, n=i, e=extratitle)

    ##finding background mean value:
    steps=[]
    for j in np.arange(cut, len(y)-100):
        step= (y[j]-y[j+100])
        steps.append(abs(step))
    start=(np.argwhere(np.array([steps])>0.009)[0][1]+cut-100)
    stop=(np.argwhere(np.array([steps])>0.009)[-1][1]+cut+400)
    background_x = np.concatenate((time[0:start-cut],time[stop-cut:-1]))
    background_y=np.concatenate((y[0:start-cut],y[stop-cut:-1]))
    amp=list((j-np.mean(background_y))*(-1) for j in y)

    ##enable these plots to see how the signal was manipulated
    plt.plot(time, y,color='red', alpha=0.5)
    plt.hlines(np.mean(background_y), time[cut],time[-2:-1])
    plt.plot(time[start],y[start],'ro')
    plt.plot(time[stop],y[stop],'ro')

    ##Signal width like in MotorData()
    signal_edge_list=[np.argwhere(amp>max(amp)/np.e), np.argwhere(amp>max(amp)/10)]
    for signal_edge in signal_edge_list:
        fwhm1, fwhm2=time[cut+int(signal_edge[0])],time[cut+int(signal_edge[-1])]
        print(fwhm1,fwhm2)
        plt.plot(fwhm1,amp[int(signal_edge[0])],'bo')
        plt.plot(fwhm2,amp[int(signal_edge[-1])],'bo')
        fwhm=float(fwhm2-fwhm1)
        plt.plot([fwhm1,fwhm2],[amp[int(signal_edge[0])],amp[int(signal_edge[-1])]], color='blue', label='Width of channel: {} s'.format(float(f'{fwhm:.4f}')))
        

    plt.legend(loc=1, bbox_to_anchor=(1.4,1))
    plt.plot(time,amp,color='blue')
    plt.suptitle(title)
    plt.xlabel('Time [s]')
    plt.ylabel('Signal [V]')
    fig1= plt.gcf()
    plt.show()
    if save==True:
        fig1.savefig(str(outfile)+"shot{n}/shot{n}_channel_{c}_raw_signal_and_widths_in_s.pdf".format(n=shotnumber, c=i), bbox_inches='tight')

def BoloDataWholeSweep(save=False):
    plt.figure(figsize=(10,5))
    plt.suptitle ('All Bolometer Signals of shot n°{n} together. \n {e}'.format(n=shotnumber,  e=extratitle))
    cut=1000
    time = LoadData(location)['Zeit [ms]'][cut:] / 1000
    width=[]
    height=[]
    position=[]
    c=[1,2,3,4,5,6,7,8]
    for i in c:
        y= LoadData(location)["Bolo{}".format(i)][cut:] 
        steps=[]
        for j in np.arange(cut, len(y)-100):
            step= (y[j]-y[j+100])
            steps.append(abs(step))
        start=(np.argwhere(np.array([steps])>0.009)[0][1]+cut-100)
        stop=(np.argwhere(np.array([steps])>0.009)[-1][1]+cut+450)
        background_x = np.concatenate((time[0:start-cut],time[stop-cut:-1]))
        background_y=np.concatenate((y[0:start-cut],y[stop-cut:-1]))
        amp=list((j-np.mean(background_y))*(-1) for j in y)
        #plt.plot(time, y,color='red', alpha=0.5)
        plt.plot(time,  amp, label="Bolo{}".format(i) )
        signal_edge=np.argwhere(amp>max(amp)/np.e)
        fwhm1, fwhm2=time[cut+int(signal_edge[0])],time[cut+int(signal_edge[-1])]
        plt.plot(fwhm1,amp[int(signal_edge[0])],'bo')
        plt.plot(fwhm2,amp[int(signal_edge[-1])],'bo')
        fwhm=float(fwhm2-fwhm1)
        plt.plot([fwhm1,fwhm2],[amp[int(signal_edge[0])],amp[int(signal_edge[-1])]], color='blue', label='Width of channel: {} s'.format(float(f'{fwhm:.4f}')))
        plt.plot(time[int(np.argwhere(amp==max(amp))[0])+cut], max(amp),'ro', label='Maximum: {} V'.format(float(f'{max(amp):.4f}')))
        width.append(fwhm)
        position.append(time[int(np.argwhere(amp==max(amp))[0])+cut])
        height.append(max(amp))
    print(height,width,position)
    plt.xlabel('Time [s]')
    plt.ylabel('Signal [V]')
    plt.legend(loc=1, bbox_to_anchor=(1.3,1) )
    fig1= plt.gcf()
    plt.show()
    if save==True:
        fig1.savefig(str(outfile)+"shot{n}/shot{n}_all_bolo_channels_raw_signals_together_analyzed.pdf".format(n=shotnumber), bbox_inches='tight')
        data = np.column_stack([np.array(c), np.array(position),np.array(height),np.array(width)])
        np.savetxt(outfile+'shot{n}/shot{n}_all_bolo_channels_raw_signals_together_analyzed.txt'.format(n=shotnumber), data, delimiter='\t \t', fmt=['%d', '%10.4f', '%10.4f', '%10.4f'], header='Analysis of the Bolometersignals from shot°{s} \n Title for Boloprofileplot: \n shot n°{s}, {m}\n channelnumber \t Position [s] \t Height [V] \t Width [s]'.format(s=shotnumber,m=motordatatitle))


#importing and using functions from bolo_radiation.py doesn't work yet so I copied them here
def LoadData(location):
    with open(location, "r") as f:
        cols = f.readlines()[3]
        cols = re.sub(r"\t+", ';', cols)[:-2].split(';')
    data = pd.read_csv(location, skiprows=4, sep="\t\t", names=cols, engine='python')
    return data

#This Function plots a timeseries of your choosing
#-->use these channelnames: Zeit [ms]		8 GHz power		2 GHz Richtk. forward	I_Bh			U_B			Pressure		2 GHz Richtk. backward	slot1			I_v			Interferometer (Mueller)	Interferometer digital	8 GHz refl. power	Interferometer (Zander)	Bolo_sum		Bolo1			Bolo2			Bolo3			Bolo4			Bolo5			Bolo6			Bolo7			Bolo8			optDiode		r_vh			Coil Temperature
def PlotSingleTimeseries(i=1, save=False):
    if Datatype=='Data':
        y= LoadData(location)["Bolo{}".format(i)]
        time = LoadData(location)['Zeit [ms]'] / 1000
        title='Shot n° {s} // Channel "Bolo {n}" \n {e}'.format(s=shotnumber, n=i, e=extratitle)
    elif Datatype=='Source':
        time=np.genfromtxt(str(source), usecols=(0), unpack=True, skip_footer=200)
        y=np.genfromtxt(str(source), usecols=(i), unpack=True, skip_footer=200)
        title='Raw signal data of {s} // Channeln° {n}\n {e}'.format(s=sourcetitle, n=i, e=extratitle)
    
    plt.figure(figsize=(10,5))
    plt.plot(time, y)
    plt.suptitle(title)
    plt.xlabel('Time [s]')
    plt.ylabel('Signal [V]')
    fig1= plt.gcf()
    plt.show()
    if save==True:
        fig1.savefig(str(outfile)+"shot{n}/shot{n}_channel_{c}_raw_signal.pdf".format(n=shotnumber, c=i), bbox_inches='tight')
    return time,y

def MotorAndBoloData(i=1):
    x,a,p =np.genfromtxt(motordata, unpack=True)    #x is the position data in mm, a is the "amplitude" data stored and processed by the software, p is the "Phase" data stored and processed by the software
    x_=np.arange(x[0],x[-1],0.00001)
    fit=pchip_interpolate(x,a,x_)
    # amp=list(i+20 for i in fit)
    y= LoadData(location)[cut:]["Bolo{}".format(i)]
    time = LoadData(location)['Zeit [ms]'][cut:] / 1000
    
    print(len(time),len(x),len(x_))


#%%
motordata='/home/gediz/Measurements/Lines_of_sight/motor_data/shot60030_bolo1_y.dat'
motordatatitle='y-Sweep of all channels with green laser and motor // no vacuum'
motordataoutfile='/home/gediz/Results/Lines_of_sight/motor_data/'
path,filename=os.path.split(motordata)

#for the bolo_ratdiation functions:
Datatype='Data'
shotnumber=60038
location='/home/gediz/Measurements/Lines_of_sight/shot_data/shot{}.dat'.format(shotnumber)
outfile='/home/gediz/Results/Lines_of_sight/shot_data/'
extratitle=motordatatitle
if not os.path.exists(str(outfile)+'shot{}'.format(shotnumber)):
    os.makedirs(str(outfile)+'shot{}'.format(shotnumber))


#PlotSingleTimeseries(8, save=True)
#MotorData(save=True)
#MotorAndBoloData(1)
#BoloDataWidths(8)#,save=True)
BoloDataWholeSweep(save=True)
# %%
