#%%
#Written by: Izel Gediz
#Date of Creation: 01.08.2022
#This code takes Bolometer data in Voltage Form and derives the Power in Watt
#It can Plot Timeseries in different layouts
#It derives the Signal height for each Bolo channel and creates a Bolometerprofile
#You can also compare different Bolometerprofiles


from pdb import line_prefix
from unicodedata import name
from blinker import Signal
from click import style
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import statistics
import os



#%% --------------------------------------------------------------------------------------------------------
# Important Functions 
# (change nothing here)
#Choose a function to create the plot/data you desire

#Parametersettings for all figures plottet

#plt.rc('text',usetex=True)
plt.rc('font',family='serif')
#plt.rc('font',size=14)
#plt.rc('axes',titlesize=11)
#plt.rc('figure', figsize=(10,5))
plt.rc('figure', titlesize=15)

#plt.rc('savefig', pad_inches=0.5)


def LoadData(location):
    with open(location, "r") as f:
        cols = f.readlines()[3]
        cols = re.sub(r"\t+", ';', cols)[:-2].split(';')
    data = pd.read_csv(location, skiprows=4, sep="\t\t", names=cols, engine='python')
    return data

#This Function plots a timeseries of your choosing
#-->use these channelnames: Zeit [ms]		8 GHz power		2 GHz Richtk. forward	I_Bh			U_B			Pressure		2 GHz Richtk. backward	slot1			I_v			Interferometer (Mueller)	Interferometer digital	8 GHz refl. power	Interferometer (Zander)	Bolo_sum		Bolo1			Bolo2			Bolo3			Bolo4			Bolo5			Bolo6			Bolo7			Bolo8			optDiode		r_vh			Coil Temperature
def PlotSingleTimeseries(channelname="", save=False):
    y = LoadData(location)[channelname]
    plt.figure(figsize=(10,5))
    plt.plot(time, y)
    plt.suptitle('Shot n° {s} // Channel "{n}"'.format(s=shotnumber, n=channelname))
    plt.xlabel('Time [s]')
    plt.ylabel('Signal [arb]')
    fig1= plt.gcf()
    plt.show()
    if save==True:
        fig1.savefig(str(outfile)+"shot{n}/shot{n}_channel_{c}_raw_signal.pdf".format(n=shotnumber, c=channelname), bbox_inches='tight')

#This Function plots the Timeseries of All 8 Bolometer Channels in a Grid separately
def PlotAllTimeseries (figheight=None, figwidth=None, save=False):
    if figheight is None:
        print("You didn't choose a figureheight so I set it to 10")
        figheight = 10
    if figwidth is None:
        print("You didn't choose a figurewidth so I set it to 10")
        figwidth=10
    fig, axs = plt.subplots(4,2)
    fig.set_figheight(figheight)
    fig.set_figwidth(figwidth)
    fig.suptitle ('All Bolometer Signals of shot n°{n}. MW used: {m}'.format(n=shotnumber, m=MW))
    for i in [0,1,2,3]:
        bolo_raw_data = LoadData(location)["Bolo{}".format(i+1)]
        axs[i,0].plot(time, bolo_raw_data)
        axs[i,0].set_title ('Bolometerchannel {}'.format(i+1))
        bolo_raw_data = LoadData(location)["Bolo{}".format(i+5)]
        axs[i,1].plot(time, bolo_raw_data)
        axs[i,1].set_title ('Bolometerchannel {}'.format(i+5))
    for ax in axs.flat:
        ax.set(xlabel='Time [s]', ylabel='Signal [V]')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig1= plt.gcf()
    plt.show()
    if save==True:
        fig1.savefig(str(outfile)+"shot{n}/shot{n}_all_bolo_channels_raw_signals.pdf".format(n=shotnumber), bbox_inches='tight')


#This Function plots the Timeseries of all 8 Bolometer Channels together in one Figure
def PlotAllTimeseriesTogether (figheight=None, figwidth=None, save=False):
    if figheight is None:
        print("You didn't choose a figureheight so I set it to 5")
        figheight = 5
    if figwidth is None:
        print("You didn't choose a figurewidth so I set it to 10")
        figwidth=10
    plt.figure(figsize=(figwidth, figheight))
    plt.suptitle ('All Bolometer Signals of shot n°{n} together. MW used: {m}'.format(n=shotnumber, m=MW))
    for i in np.arange(1,9):
        bolo_raw_data = LoadData(location)["Bolo{}".format(i)]
        plt.plot(time,  bolo_raw_data, label="Bolo{}".format(i) )
    plt.xlabel('Time [s]')
    plt.ylabel('Signal [V]')
    plt.legend(loc=1, bbox_to_anchor=(1.2,1) )
    fig1= plt.gcf()
    plt.show()
    if save==True:
        fig1.savefig(str(outfile)+"shot{n}/shot{n}_all_bolo_channels_raw_signals_together.pdf".format(n=shotnumber), bbox_inches='tight')

def CombinedTimeSeries (shot1,shot2,shot3, shot4, shot5, shot6, shot7, shot8, Plot=False, save =False):
    path='/home/gediz/Measurements/Calibration/Calibration_Bolometer_August_2022/Bolometer_calibration_air_different_lamps_17_08_2022/shot{name}.dat'
    a=[shot1,shot2,shot3,shot4,shot5,shot6,shot7,shot8]
    bolo=[[],[],[],[],[],[],[],[]]
    time=[[],[],[],[],[],[],[],[]]
    c=[1,2,3,4,5,6,7,8]
    for (i,j,k,l) in zip(a,bolo,time,c):
        location=path.format(name=i)
        j.extend(LoadData(location)['Bolo{}'.format(l)])
        k.extend(LoadData(location)['Zeit [ms]'])

    time_longest=max(time, key=len)
    time_longest=[x/1000 for x in time_longest]
    for (j,l) in zip(bolo,c):
        length_extend=len(time_longest)-len(j)
        j.extend([j[-1]]*length_extend)
        print(len(j))
        plt.plot(time_longest,j, label='Channel {}'.format(l))
    if Plot==True:
        plt.suptitle('Calibration with green laser \n shots 50018 to 50025')
        plt.legend(loc=1, bbox_to_anchor=(1.4,1))
        plt.xlabel('time [s]')
        plt.ylabel('Signal [V]')
        fig1= plt.gcf()
        plt.show()
    if save==True:
        fig1.savefig('/home/gediz/Results/Calibration/Calibration_Bolometer_August_2022/combined_shots/All_channels_from_shots_{a}_to_{b}.pdf'.format(a=shot1, b=shot8), bbox_inches='tight')
        data = np.column_stack([np.array(time_longest), np.array(bolo[0]), np.array(bolo[1]), np.array(bolo[2]), np.array(bolo[3]), np.array(bolo[4]), np.array(bolo[5]), np.array(bolo[6]), np.array(bolo[7])])
        np.savetxt('/home/gediz/Results/Calibration/Calibration_Bolometer_August_2022/combined_shots/All_channels_from_shots_{a}_to_{b}.txt'.format(a=shot1, b=shot8) , data, delimiter='\t \t', header='Signals of all Bolometerchannels combined from shots {a} to {b}. \n time [s] // Bolo1 //Bolo2 // Bolo3 // Bolo4 //Bolo5 / Bolo6 // Bolo7 // Bolo8'.format(a=shot1, b=shot8))




#This is a Function to derive the Time (indices) in which the Plasma was on
#It needs to be fed the MW Power data.
#-->Channelname can therefore either be '8 GHz' or '2 GHz'
def SignalHighLowTime(Plot= False, save=False):
    if MW == '8 GHz':
        MW_n = '8 GHz power'
    if MW== '2 GHz':
        MW_n= '2 GHz Richtk. forward'
    y= LoadData(location)[MW_n]
    x= LoadData(location)['Zeit [ms]']

    steps=[]
    for i in np.arange(0, len(y)-10):
        step= (y[i]-y[i+10])
        steps.append(abs(step))
    start=np.argwhere(np.array([steps])>0.1)[0][1]
    stop=np.argwhere(np.array([steps])>0.1)[-1][1]
    if Plot== True:
        plt.show()
        plt.plot(time,y)
        plt.plot(time[start], y[start], marker='o', color='red')
        plt.plot(time[stop], y[stop], marker='o', color='red')
        plt.suptitle('The MW Power Data of "{}" with markers on the Signal edges'.format(MW))
        plt.xlabel('Time [s]')
        plt.ylabel('Power [Arb.]')
        fig1= plt.gcf()
        plt.show()
    if save==True:
        fig1.savefig(str(outfile)+"shot{n}/shot{n}_signal_edge_with_{m}.pdf".format(n=shotnumber, m=MW), bbox_inches='tight')
    return start, stop

#This function derives the signal heights without fits to account for the drift
#It just takes the right edge of the signal and the mean value of 100 datapoints to the left and right to derive the Signalheight
#It is useful for noisy measurements where the fits don't work or for calibrationmeasurements with no reference MW data
def SignalHeight_rough(Type='', i=1, Plot=False, save=False):
    Type_types =['Bolo', 'Power', 'Cali']
    if Type not in Type_types:
        raise ValueError("Invalid Type input. Insert one of these arguments {}".format(Type_types))
    if Type == 'Bolo':
        y= LoadData(location)["Bolo{}".format(i)]
        time= LoadData(location)['Zeit [ms]']
        ylabel= 'Signal [V]'
        unit = 'V'
    if Type == 'Power':
        y= PowerTimeSeries(i)
        time= LoadData(location)['Zeit [ms]']
        ylabel= 'Power [\u03bcW]'
        unit='\u03bcW'
    if Type=='Cali':
        time,y=np.loadtxt(str(infile), usecols=(0,i), unpack=True)
        ylabel= 'Signal [V]'
        unit = 'V'
        

    jump=((max(y)-min(y))/2)
    

    steps=[]
    for s in np.arange(0, len(y)-50):
        step= (y[s]-y[s+50])
        steps.append(abs(step))
    start=np.argwhere(np.array([steps])>jump)[0][1]
    stop=np.argwhere(np.array([steps])>jump)[-1][1]
    #print(jump, start, stop)
    signal_off=np.mean(list(y[-100:-1]))
    signal_on=np.mean(list(y[stop-200:stop-50]))
    div=signal_off-signal_on
    print(div)
    if Plot== True:
        plt.show()
        plt.plot(time,y, alpha=0.5)
        plt.plot(time[start], y[start],'bo')
        plt.plot(time[stop], y[stop], 'bo')
        plt.plot(time[-100:-99], y[-100:-99], marker='o', color='green')
        plt.plot(time[-1:], y[-1:], marker='o', color='green')
        plt.plot(time[stop-50], y[stop-50], marker='o', color='red')
        plt.plot(time[stop-200], y[stop-200], marker='o', color='red')
        plt.suptitle('Bolometerdata channel {} with markers for the signal height data'.format(i))
        plt.xlabel('Time [s]')
        fig1= plt.gcf()
        plt.show()
    if save==True:
        fig1.savefig(str(outfile)+"shot{n}/shot{n}_signal_edge_with_{m}.pdf".format(n=shotnumber, m=MW), bbox_inches='tight')

    return (div, jump)

#This is a Function that takes one Bolometersignal (i) and gives you the Signal Height Difference
#It takes the SignalHighLowTime indices to split the Timeseries into two parts
#Two fits are made to the part of the signal with and without  Plasma respectively
#The difference of these Linear fits is determined
#-->Type is either 'Bolo' or 'Power' depending on if you want to plot raw Voltage data or Power data
#--> i is the number of the Bolometerchannel

def SignalHeight(Type="", i=1,  Plot=False, save=False):
    def lin (x,a,b):
        return a*x + b
    x=time

    Type_types =['Bolo', 'Power']
    if Type not in Type_types:
        raise ValueError("Invalid Type input. Insert one of these arguments {}".format(Type_types))
    if Type == 'Bolo':
        y= LoadData(location)["Bolo{}".format(i)]
        ylabel= 'Signal [V]'
        unit = 'V'
    if Type == 'Power':
        y= PowerTimeSeries(i)
        ylabel= 'Power [\u03bcW]'
        unit='\u03bcW'


    start= SignalHighLowTime(Plot=False)[0]
    stop= SignalHighLowTime(Plot= False)[1]
    x1 = x[start+1000:stop]
    y1 = y[start+1000:stop]
    x2 = np.concatenate((x[0:start],x[stop:-1]))
    y2 = np.concatenate((y[0:start],y[stop:-1]))
    
    popt1, pcov1 = curve_fit(lin,x1,y1)
    popt2, pcov2 = curve_fit(lin,x2,y2)
    div1 = popt2[1]-popt1[1]            #Takes the Signal height based on the axial intercept of the fit
    div2 = lin(x[stop-1000], *popt2)-lin(x[stop-1000], *popt1)        #Takes the Signal height a 1000 points in front of the falling Signal edge
    div_avrg = float(f'{(div1+div2)/2:.4f}')        #Takes amean value for the Signal height based on the two linear fits

    if Plot==True:
        plt.plot(time, y, alpha=0.5, label='Bolometerdata of channel {c} shot n°{s}'.format(c=i, s= shotnumber))
        plt.plot(x, lin(x, *popt1), color='orange', label= 'Fit to the values with Plasma')
        plt.plot(x, lin(x, *popt2), color='green', label= 'Fit to the values without Plasma')
        plt.plot(1,popt2[1], marker='o', color='blue')
        plt.plot(1, popt1[1], marker='o', color='blue')
        plt.plot(x[stop-1000],lin(x[stop-1000], *popt1), marker='o', color='blue')
        plt.plot(x[stop-1000], lin(x[stop-1000], *popt2), marker='o', color='blue')
        plt.plot([1,1],[popt1[1],popt2[1]], color='blue', label='Height Difference of the \n Signal with and without Plasma')
        plt.plot([x[stop-1000],x[stop-1000] ], [lin(x[stop-1000], *popt1), lin(x[stop-1000], *popt2)], color='blue')
        plt.annotate(float(f'{div1:.4f}'), (1, popt1[1]+div1/2), color='blue')
        plt.annotate(float(f'{div2:.4f}'), (x[stop-1000], lin(x[stop-1000], *popt1)+div2/2), color='blue')
        plt.plot(x[start], y[start], marker='o', color='red')
        plt.plot(x[stop], y[stop], marker='o', color='red', label='signal edge, derived using the {} Data'.format(MW))
        plt.legend(loc=1, bbox_to_anchor=(1.8,1))
        plt.xlabel('Time (s)')
        plt.ylabel(ylabel)
        plt.suptitle('Linear Fits to determine the Signal Height \n The average signal height is {v}{u}'.format(v=abs(div_avrg), u=unit))
        fig1= plt.gcf()
        plt.show()
    if save==True:
        fig1.savefig(str(outfile)+"shot{n}/shot{n}_signal_height_channel_Bolo{c}.pdf".format(n=shotnumber, c=1), bbox_inches='tight')
            
    return (div1 , div2, (div1+div2)/2)

#This function derives the Power time series from the raw Bolometer Voltage Time Series of your choosing
#It uses the formula (4.21) of Anne Zilchs Diploma Thesis 'Untersuchung von Strahlungsverlusten mittels Bolometrie an einem toroidalen Niedertemperaturplasma' from 2011
#--> i is the number of the Bolometerchannel

def PowerTimeSeries(i=1, Plot=False, save=False):
    def power(g,k,U_ac, t, U_Li):
        return (np.pi/g) * (2*k/U_ac) * (t* np.gradient(U_Li,LoadData(location)['Zeit [ms]'] )+U_Li)
    kappa =  [ 4.2813209E-01,  4.3431544E-01,  4.2536712E-01,  4.5481977E-01, 4.5481977E-01*1.4397, 4.2536712E-01*1.2147, 4.3431544E-01*1.2493, 4.2813209E-01*1.17938]
    #kappa =  [ 4.2813209E-01,  4.3431544E-01,  4.2536712E-01,  4.5481977E-01, 4.5481977E-01, 4.2536712E-01, 4.3431544E-01, 4.2813209E-01]
    tau = [0.102900,     0.111500,     0.114500,     0.115400,    0.0736000,  0.0814000,    0.0704000,    0.0709000]
    g1= (10,30,50)
    g2= (20,100,250)
    g3= (1,2,5)
    g=2*g1[1]*g2[1]*g3[2]
    U_ac=8
    k= kappa[i-1]
    t = tau[i-1]
    U_Li= LoadData(location)["Bolo{}".format(i)]
    if Plot==True:
        plt.figure(figsize=(10,5))
        plt.plot(time, power(g,k,U_ac, t, U_Li)*1000000)
        plt.suptitle('Power data of Shot n° {s} // Channel "Bolo{n}"'.format(s=shotnumber, n=i))
        plt.xlabel('Time [s]')
        plt.ylabel('Power [\u03bcW]')
        fig1= plt.gcf()
        plt.show()
    if save==True:
        fig1.savefig(str(outfile)+"shot{n}/shot{n}_channel_Bolo{c}_power_signal.pdf".format(n=shotnumber, c=i), bbox_inches='tight')
    return power(g,k,U_ac, t, U_Li)*1000000

#This function derives the Signal height of all 8 Time Series using the SignalHeight function
#It then Plots the Height Values in a row to show the Bolometerprofile
#Tipp: This Routine doesn't show you the Fit Plots of SignalHeight that were used to derive the signal heights. 
#      So if you want to make sure the code used the good Fits to derive the signal heights change 'Plot' to 'True' at the --><--
#-->Type is either 'Bolo' or 'Power' depending on if you want to plot the signal heights of raw Voltage data or Power data
def BolometerProfile(Type="", save=False):
    print('This could take a second')
    x=[]
    y=[]
    
    #Activate the parts with z to compare your data with Annes Data of the same shot
    #z= np.loadtxt('/scratch.mv3/koehn/backup_Anne/zilch/results/7680/7680_BCh_jump.dat', usecols=(1,))*1000000
    Type_types =['Bolo', 'Power', 'Cali']
    if Type not in Type_types:
        raise ValueError("Invalid Type input. Insert one of these arguments {}".format(Type_types))
    for i in [1,2,3,4,5,6,7,8]:
        x.append(i)
        y.append(abs(SignalHeight_rough(Type,i,Plot=True)[0]))  
        #y.append(abs(SignalHeight(Type, i, Plot=False)[2])) #--><--
    if Type == 'Bolo':
        ylabel1= 'Signal [V]'
        name='raw data'
    if Type == 'Power':
        ylabel1= 'Power [\u03bcW]'
        name= 'radiation powers'
    if Type =='Cali':
        ylabel1='Signal [V]'
        name='raw data'
    plt.figure(figsize=(10,5))
    plt.plot(x,y, marker='o', linestyle='None')
    #plt.plot(x,z, marker='x', linestyle='None', label='Annes Daten zum Vergleich')
    plt.ylabel(ylabel1)
    plt.xlabel('Bolometerchannel')
    plt.suptitle('Signals of the Bolometerchannels from {n} of shot n°{s} \n MW used: {m}'.format(n=name, s= shotnumber, m=MW))
    plt.legend()
    fig1 = plt.gcf()
    plt.show()
    if save == True:
        data = np.column_stack([np.array(x), np.array(y)])#, np.array(z), np.array(abs(y-z))])
        datafile_path = str(outfile)+"shot{n}/shot{n}_bolometerprofile.txt".format(n=shotnumber)
        np.savetxt(datafile_path , data, delimiter='\t \t', fmt=['%d', '%10.3f'], header='Signals of the Bolometerchannels from {n} of shot n°{s}. MW Power was {m} \n Label for plot \n Data of shot n°{s} with MW power {m}\nchanneln° \t Power I derived [\u03bcW]'.format(n=name, s= shotnumber, m=MW))
        #np.savetxt(datafile_path , data, delimiter='\t \t', fmt=['%d', '%10.3f', '%10.3f', '%10.3f'], header='Signals of the Bolometerchannels from {n} of shot n°{s}. MW Power was {m} \n channeln° \t Power I derived [\u03bcW]\t Power Anne derived [\u03bcW] \t Difference [\u03bcW]'.format(n=name, s= shotnumber, m=MW))
        fig1.savefig(str(outfile)+"shot{n}/shot{n}_bolometerprofile.pdf".format(n=shotnumber), bbox_inches='tight')
    return x, y#, z, y-z

#This function can compare the Bolometerprofiles of 4 different shots
#There must already be a .txt file with the Signals for each channel as created with the function BolometerProfile()
def CompareBolometerProfiles(shot_number_1, shot_number_2, shot_number_3, shot_number_4, save=False):
    x=[1,2,3,4,5,6,7,8]
    z=[8,7,6,5,4,3,2,1]
    shot1=np.loadtxt(str(outfile)+"shot{n}/shot{n}_bolometerprofile.txt".format(n=shot_number_1),usecols=1)
    shot2=np.loadtxt(str(outfile)+"shot{n}/shot{n}_bolometerprofile.txt".format(n=shot_number_2),usecols=1)
    shot3=np.loadtxt(str(outfile)+"shot{n}/shot{n}_bolometerprofile.txt".format(n=shot_number_3),usecols=1)
    shot4=np.loadtxt(str(outfile)+"shot{n}/shot{n}_bolometerprofile.txt".format(n=shot_number_4),usecols=1)
    plt.plot(x,shot1, marker='o', linestyle='dashed', label=open(str(outfile)+"shot{n}/shot{n}_bolometerprofile.txt".format(n=shot_number_1), 'r').readlines()[2][3:-1])
    plt.plot(z,shot2, marker='o', linestyle='dashed', label=open(str(outfile)+"shot{n}/shot{n}_bolometerprofile.txt".format(n=shot_number_2), 'r').readlines()[2][3:-1])
    plt.plot(x,shot3, marker='o', linestyle='dashed', label=open(str(outfile)+"shot{n}/shot{n}_bolometerprofile.txt".format(n=shot_number_3), 'r').readlines()[2][3:-1])
    plt.plot(z,shot4, marker='o', linestyle='dashed', label=open(str(outfile)+"shot{n}/shot{n}_bolometerprofile.txt".format(n=shot_number_4), 'r').readlines()[2][3:-1])
    plt.xlabel('Bolometerchannel')
    plt.ylabel('Power [\u03bcW]')
    plt.suptitle('Comparison of the Bolometerprofiles from Shots \n {a}, {b}, {c}, and {d}'.format(a=shot_number_1, b=shot_number_2, c=shot_number_3, d=shot_number_4))
    plt.legend(loc=1, bbox_to_anchor=(1.7,1) )
    fig1= plt.gcf()
    plt.show()
    if save==True:
        fig1.savefig(str(outfile)+"comparisons_of_shots/comparison_{a}_{b}_{c}_{d}.pdf".format(a=shot_number_1, b=shot_number_2, c=shot_number_3, d=shot_number_4), bbox_inches='tight')
    
    
#%% -------------------------------------------------------------------------------------------------------- 
# Important Variables 
# You should not change anything except the shotnumber. 
# Enter a Shot number of the form 'xxxxx'

if __name__ == "__main__":
    #shotnumber = str(input('Enter a shotnumber here: '))
    shotnumber=50025

    #location ='/data6/shot{name}/interferometer/shot{name}.dat'.format(name=shotnumber)
    location='/home/gediz/Measurements/Calibration/Calibration_Bolometer_August_2022/Bolometer_calibration_air_different_lamps_17_08_2022/shot{name}.dat'.format(name=shotnumber) #location of calibration measurement
    time = LoadData(location)['Zeit [ms]'] / 1000 # s
    infile= '/home/gediz/Results/Calibration/Calibration_Bolometer_August_2022/combined_shots/All_channels_from_shots_50025_to_50018.txt'
    outfile='/home/gediz/Results/Calibration/Calibration_Bolometer_August_2022/'
    #outfile = '/home/gediz/Results/Bolometer_Profiles/'
    z= LoadData(location)['2 GHz Richtk. forward']
    height_z = abs(max(z)-min(z))
    if height_z <= 0.21:
        MW = '8 GHz'
    else: 
        MW = '2 GHz'

    if not os.path.exists(str(outfile)+'shot{}'.format(shotnumber)):
        os.makedirs(str(outfile)+'shot{}'.format(shotnumber))

    #SignalHeight_rough('Cali', 1, Plot=True, save=False)
    #PlotAllTimeseriesTogether(save=True)
    #CombinedTimeSeries('50025','50024','50023','50022','50021','50020','50019','50018', Plot=True, save=True)
    BolometerProfile('Cali')
    #CompareBolometerProfiles(50012, 50013,50001, 50013, save=True)

    # x,y=np.loadtxt('/home/gediz/Results/Calibration/Calibration_Bolometer_August_2022/combined_shots/calibration_with_green_laser_signal_heights.txt', unpack=True)
    # plt.plot(x,y,'bo')
    # plt.xlabel('Bolometerchannel')
    # plt.ylabel('Signal [V]')
    # plt.suptitle('Green laser on each channel in different measurements \n shots 50018 to 50025')
    # fig1= plt.gcf()
    # plt.show()
    # fig1.savefig('/home/gediz/Results/Calibration/Calibration_Bolometer_August_2022/combined_shots/calibration_with_green_laser_signal_heights.pdf', bbox_inches='tight')




# %%
