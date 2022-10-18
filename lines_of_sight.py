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
from scipy.signal import savgol_filter
#from bolo_radiation import LoadData, PlotAllTimeseries, PlotAllTimeseriesTogether, PlotSingleTimeseries

#%%

def MotorData(save=False):
    x,a,p =np.genfromtxt(motordata, unpack=True)    #x is the position data in mm, a is the "amplitude" data stored and processed by the software, p is the "Phase" data stored and processed by the software
    x_=np.arange(x[0],x[-1],0.00001)
    fit=pchip_interpolate(x,a,x_)
    amp=list(i-min(a) for i in fit)
   # amp=savgol_filter(amp0,1000,3)
    plt.plot(x_,amp,'r.--', label='Interpolated signal "Amplitude"', alpha=0.5)
    #plt.plot(x_,amp,'r.--')
    signal_edge_list=[np.argwhere(amp>max(amp)/np.e)]#, np.argwhere(amp>max(amp)/10)]
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


def SmoothSignal(i=1):
    cut=0
    y= LoadData(location)["Bolo{}".format(i)][cut:]        #aprox. the first 10 seconds are ignored because due to the motormovement a second peak appeared there
    time = LoadData(location)['Zeit [ms]'][cut:] 
    title='Shot n° {s} // Channel "Bolo {n}" \n {e}'.format(s=shotnumber, n=i, e=extratitle)

    y_smooth=savgol_filter(y,1000,3)

    steps=[]
    for j in np.arange(cut, len(y_smooth)-1000):
        step= (y_smooth[j]-y_smooth[j+1000])
        steps.append(abs(step))
    #start=(np.argwhere(np.array([steps])>0.005)[0][1]+cut)
    #stop=(np.argwhere(np.array([steps])>0.005)[-1][1]+cut)
    #print(start,stop)
    plt.plot(np.arange(0,len(steps)),steps,'bo')
    plt.hlines(0.005,0,len(steps))
    #plt.plot([start-cut,start-cut],[steps[start-cut],steps[start-cut]],'ro')
    #plt.plot([stop-cut,stop-cut],[steps[stop-cut],steps[stop-cut]],'ro')
    plt.show()

    #print(start,stop)
    plt.plot(time, y,color='red', alpha=0.5)
    plt.plot(time,y_smooth)
    #plt.plot(time[start],y_smooth[start],'bo')
    #plt.plot(time[stop],y_smooth[stop],'ro')
    #plt.plot(time[stop],y[stop],'go')
    #print(time[stop], y_smooth[stop],y[stop])
    print(len(y),len(y_smooth),len(steps))
    plt.show()
    return (y_smooth)



#This function takes one channelsignal aquired during a sweep with a lightsource across it and determines
#The width of the signal at different heights after inverting it and substracting the backgroundsignal
def BoloDataWidths(i=1, save=False):
    cut=0
    y0= LoadData(location)["Bolo{}".format(i)][cut:]    #aprox. the first 10 seconds are ignored because due to the motormovement a second peak appeared there
    y=savgol_filter(y0,1000,3)
    time = LoadData(location)['Zeit [ms]'][cut:] / 1000
    title='Shot n° {s} // Channel "Bolo {n}" \n {e}'.format(s=shotnumber, n=i, e=extratitle)

    ##finding background mean value:
    steps=[]
    def lin (x,a,b):
        return a*x + b
    for j in np.arange(cut, len(y)-1000):
        step= (y[j]-y[j+1000])
        steps.append(abs(step))
    start=(np.argwhere(np.array([steps])>0.005)[0][1]+cut)
    stop=(np.argwhere(np.array([steps])>0.005)[-1][1]+cut)
    background_x = np.concatenate((time[0:start-cut],time[stop-cut:-1]))
    background_y=np.concatenate((y[0:start-cut],y[stop-cut:-1]))
    popt,pcov=curve_fit(lin,background_x,background_y)
    amp=list((y[j]-lin(time[j],*popt))*(-1) for j in np.arange(cut,len(y)))

    ##enable these plots to see how the signal was manipulated
    plt.plot(time, y0,color='red', alpha=0.5)
    plt.plot(time,y,color='red')
    plt.plot(time, lin (time,*popt), color='black')
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
    plt.plot(time,amp,color='blue',alpha=0.5)
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
    cut=0
    time = LoadData(location)['Zeit [ms]'][cut:] / 1000
    width=[]
    height=[]
    position=[]
    c=[6,7,8]
    color=['blue','red','green','orange','magenta','gold','darkcyan','blueviolet']
    def lin (x,a,b):
        return a*x + b
    for (i,b) in zip(c,color):
        y0= LoadData(location)["Bolo{}".format(i)][cut:]    #aprox. the first 10 seconds are ignored because due to the motormovement a second peak appeared there
        y=savgol_filter(y0,1000,3)
        steps=[]
        for j in np.arange(cut, len(y)-1000):
            step= (y[j]-y[j+1000])
            steps.append(abs(step))
        start=(np.argwhere(np.array([steps])>0.005)[0][1]+cut)
        stop=(np.argwhere(np.array([steps])>0.005)[-1][1]+cut)
        background_x = np.concatenate((time[0:start-cut],time[stop-cut:-1]))
        background_y=np.concatenate((y[0:start-cut],y[stop-cut:-1]))
        popt,pcov=curve_fit(lin,background_x,background_y)
        amp_origin=list((y[j]-lin(time[j],*popt))*(-1) for j in np.arange(cut,len(y)))
        maximum=max(amp_origin)
        amp=list(amp_origin[j]/maximum for j in np.arange(0,len(y)))
        plt.plot(time,  amp, label="Bolo{}".format(i),color=b,alpha=0.7 )
        
        signal_edge=np.argwhere(amp>max(amp)/np.e)
        fwhm1, fwhm2=time[cut+int(signal_edge[0])],time[cut+int(signal_edge[-1])]
        plt.plot(fwhm1,amp[int(signal_edge[0])],'o',color=b)
        plt.plot(fwhm2,amp[int(signal_edge[-1])],'o',color=b)
        fwhm=float(fwhm2-fwhm1)
        plt.plot([fwhm1,fwhm2],[amp[int(signal_edge[0])],amp[int(signal_edge[-1])]], color=b, label='Width of channel: {} s'.format(float(f'{fwhm:.4f}')))
        plt.plot(time[int(np.argwhere(amp==max(amp))[0])+cut], max(amp),'o',color=b, label='Maximum: {} V'.format(float(f'{max(amp_origin):.4f}')))
        width.append(fwhm)
        position.append(time[int(np.argwhere(amp==max(amp))[0])+cut])
        height.append(max(amp_origin))
    print(height,width,position)
    plt.xlabel('Time [s]')
    plt.ylabel('Signal [V]/ Maximum')
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


def VisualizeLinesOfSight():
    y0,y1,y2,y3,y4,y5,y6,y7,y8=np.genfromtxt('/home/gediz/Results/Lines_of_sight/lines_of_sight_data_y.txt', unpack=True)
    x0,x1,x2,x3,x4,x5,x6,x7,x8=np.genfromtxt('/home/gediz/Results/Lines_of_sight/lines_of_sight_data_x.txt', unpack=True)
    x=[x2,x3,x4,x5,x6,x7,x8]
    plt.plot(x0,list(h/2 for h in x1),'ro--',label='horizontal line of sight')
    for i in x:
        plt.plot(x0,list(h/2 for h in i),'ro--',alpha=0.5)
        plt.plot(x0,list(-h/2 for h in i),'ro--',alpha=0.5)
    y=[y2,y3,y4,y5,y6,y7,y8]
    plt.plot(y0,list(h/2 for h in y1),'bo--',label='vertical line of sight')
    for j in y:
        plt.plot(y0,list(h/2 for h in j),'bo--',alpha=0.5)
        plt.plot(y0,list(-h/2 for h in j),'bo--',alpha=0.5)
    plt.xlabel('Distance from slit [cm]')
    plt.ylabel('line of sight widht [mm]')
    plt.legend()
    plt.suptitle('Widhts of the lines of sight from all 8 channels, vertical and horizontal')
    plt.show()

#%%
motordata='/home/gediz/Measurements/Lines_of_sight/motor_data/shot60078_x_scan_UV_Lamp_lines_of_sight_channel_1.dat'
motordatatitle='Motordata of shot60078 // Lines of Sight measurement //channel 1'
motordataoutfile='/home/gediz/Results/Lines_of_sight/motor_data/'
path,filename=os.path.split(motordata)

#for the bolo_ratdiation functions:
Datatype='Data'
shotnumber=60080
#location='/home/gediz/Measurements/Calibration/Calibration_Bolometer_September_2022/Bolometer_calibration_vacuum_and_air_different_sources_09_2022/shot{name}.dat'.format(name=shotnumber) #location of calibration measurement
location='/home/gediz/Measurements/Lines_of_sight/shot_data/shot{}_cropped.dat'.format(shotnumber)
outfile='/home/gediz/Results/Lines_of_sight/shot_data/'
extratitle='Lines of sight // air // UV-Lamp x-scan//distance~3.5cmcm// amplif. x5, x100'
if not os.path.exists(str(outfile)+'shot{}'.format(shotnumber)):
    os.makedirs(str(outfile)+'shot{}'.format(shotnumber))


#PlotSingleTimeseries(8, save=True)
#MotorData(save=True)
#MotorAndBoloData(1)
#for i in (6,7,8):
#    BoloDataWidths(i)#,save=True)
#BoloDataWidths(4)
#BoloDataWholeSweep(save=True)
#SmoothSignal(1)
#MotorData(save=True)
VisualizeLinesOfSight()

# %%
