# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import matplotlib.pyplot as plt
import astropy
from astropy import units
from astropy.io import fits
import glob
import os
from datetime import datetime
import time
import math
#%matplotlib inline

def get_files():

    path = 'C:/Users/raynaudy/Documents/Manip/CH4/long_onde_1642_to_1654/with_CH4/20230215'
    #path = 'C:/Users/raynaudy/Documents/Manip/tests_synchro_pwrmtr/obstruction_laser/20230215'
    files = os.listdir(path)
    fits_files = []
    specific = 'pas_50_c'
    for name in files:
        if specific in name and '.fits' in name:
            fits_files.append(path+'/'+name)
            print('FILE FOUND ')
        else :
            print('NO MATCH')
    return(fits_files)

def graph_data(wvl,pwrmtr,io,cam):
        fig, (ax1,ax2,ax3) = plt.subplots(3,1,figsize=(8, 8))#,figsize=(8, 6)
        fig.subplots_adjust(hspace=0.3)
        #for i incam = 1/cam   
        ax1.plot(np.asarray(wvl, float),cam,color='red',label='mean') 
        ax1.set_xlabel('$\lambda$ [nm]')
        ax1.set_ylabel('Intensité')  
        ax2.plot(np.asarray(wvl, float),pwrmtr,label='mean') 
        ax2.set_xlabel('$\lambda$ [nm]')
        ax2.set_ylabel('Current Power Meter [nA]')
        ax3.plot(np.asarray(wvl, float),io,label='mean') 
        ax3.set_xlabel('$\lambda$ [nm]')
        ax3.set_ylabel('Current Source [mA]')

def header(f):
    l_onde, l_int, l_pwrmtr, l_temp, l_date = [],[],[],[],[]
    for i in range(1,len(f)):
        l_onde.append(f[i].header['LAMBDA'])
        l_int.append(f[i].header['HIERARCH INTENSITE'])
        l_pwrmtr.append(f[i].header['INTENSITE_POWER_METER'])
        l_temp.append(f[i].header['TEMPERATURE'])
        l_date.append(f[i].header['EXTNAME'])
    return(l_onde, l_int, l_pwrmtr, l_temp, l_date)
        

def to_cm_1(f):
    for i in range(0, len(f)):
        f[i] = 10**7 / float(f[i])
    return(f)    
        
def get_data_both():
    global l_onde, l_int, l_pwrmtr, l_temp, l_date, medhdul
    l_onde, l_int, l_pwrmtr, l_temp, l_date= [],[],[],[],[]

    fits_files = get_files()
    print(fits_files)
    for file in fits_files:
        hdul = fits.open(file)
        l_onde, l_int, l_pwrmtr, l_temp, l_date = header(hdul)
        medhdul = []
        for i in range(1,len(hdul)):
            meddata = []
            data = hdul[i].data
            for j in range(0, len(data)):
                meddata.append(np.median(hdul[i].data[j]))
            medhdul.append(np.median(meddata))
    l_onde = to_cm_1(l_onde)

    #return(l_onde, l_int, l_pwrmtr, l_temp, l_date, medhdul)
    #graph_data(l_onde,l_pwrmtr,l_int,medhdul)
    
    #print(l_pwrmtr, '\n')
    #print(l_onde, '\n')
    #print(medhdul)
    
    a = np.linspace(0,151, num=len(medhdul))
    fig, (ax1,ax2,ax3,ax4) = plt.subplots(4,1,figsize=(10, 10))#,figsize=(8, 6)
    fig.subplots_adjust(hspace=0.3)

    ax1.plot(np.asarray(l_onde, float),medhdul,color='red',label='mean') 
    ax1.set_xlabel('$\lambda$ [cm-1]')
    ax1.set_ylabel('Intensité caméra') 
    ax2.plot(np.asarray(l_onde, float),l_pwrmtr,label='mean') 
    ax2.set_xlabel('$\lambda$ [cm-1]')
    ax2.set_ylabel('PwrMtr')
    ax3.plot(np.asarray(l_onde, float),l_int,label='mean') 
    ax3.set_xlabel('$\lambda$ [cm-1]')
    ax3.set_ylabel('Intensite source [mA]')
    ax4.plot(np.asarray(l_onde, float),medhdul,label='mean') 
    ax4.set_xlabel('$\lambda$ [cm-1]')
    ax4.set_ylabel('l_int')

#get_data_both()  
    
  
#prend les mins sous une certaine intensite recu
#ca fonctionne mais logique bancale, pas belle, a modif
def get_min():
    min_io = 1500
    #l_onde, l_int, l_pwrmtr, l_temp, l_date, medhdul,wvl_abs,int_abs = [], [], [] ,[],[],[],[],[]
    #l_onde, l_int, l_pwrmtr, l_temp, l_date, medhdul = get_data()
    wvl_abs,int_abs = [], []
    for i in range(0,len(medhdul)):
        if medhdul[i]<min_io:
            wvl_abs.append(l_onde[i])
            int_abs.append(medhdul[i])
    print('wvl : ', wvl_abs,'\n intensite : ' , int_abs)
    return(wvl_abs,int_abs)
#get_min()

def get_abs():
    wvl_abs, int_abs = get_min()
    wvlmin, intmin, wvlabs, intabs = [],[],[],[]
    i=0
    #for i in range(0,len(wvl_abs)-1):
    while i< len(wvl_abs):
        while float(wvl_abs[i])<float(wvl_abs[i+1])+0.5:
            wvlmin.append(wvl_abs[i])
            intmin.append(int_abs[i])
            i+=1
            #print('test 2   ', i)
        wvlmin.append(wvl_abs[i])
        intmin.append(int_abs[i])
        y = intmin.index(np.min(intmin))
        wvlabs.append(wvlmin[y])
        intabs.append(intmin[y])
        print('test 3   ', i)
        i+=1
        
        print('wvl abs = ', wvlabs, '\nint abs = ', intabs)    
  
    


global v1,v2,v3,v4,v5
v1,v2,v3,v4,v5 = 6046.93, 6057.03, 6066.98, 6077, 6086.79

global wl1, wl2, wl3, wl4, wl5
wl1, wl2, wl3, wl4, wl5 = 1/v1*10000000, 1/v2*10000000, 1/v3*10000000, 1/v4*10000000, 1/v5*10000000

global sv1, sv2, sv3, sv4, sv5
sv1, sv2, sv3, sv4, sv5 = 2.2*10**-20, 4.6*10**-20, 7.5*10**-20, 1.8*10**-20, 3.9*10**-20
#print('\n', wl1,'\n', wl2,'\n', wl3,'\n', wl4,'\n', wl5)








"""
Absorbance A= log10(Io/I)
Beer Lambert : A = e*l*c
    avec 
        A est l’absorbance ou la densité optique de la solution pour une longueur d’onde λ
        c (en mol.L-1) est la concentration de l’espèce absorbante 
        l (en cm) est la longueur du trajet optique
        e epsilon (en mol-1.L.cm-1) est le coefficient d’extinction molaire de l’espèce absorbante en solution.

"""


def graph_absorb(wvl,T ,A, cam):
        fig, (ax1,ax2,ax3) = plt.subplots(3,1,figsize=(8, 8))#,figsize=(8, 6)
        fig.subplots_adjust(hspace=0.3)
        #for i incam = 1/cam   
        ax1.plot(np.asarray(wvl, float),cam,color='red',label='mean') 
        ax1.set_xlabel('$\lambda$ [cm-1]')
        ax1.set_ylabel('Intensité')  
        ax2.plot(np.asarray(wvl, float),T,label='mean') 
        ax2.set_xlabel('$\lambda$ [cm-1]')
        ax2.set_ylabel('Transmittance')
        ax3.plot(np.asarray(wvl, float),A,label='mean') 
        ax3.set_xlabel('$\lambda$ [cm-1]')
        ax3.set_ylabel('Absorbance ')

def get_files_absorb():
    specific = '337pas'
    path_ch4 = 'C:/Users/raynaudy/Documents/Manip/CH4/long_onde_1642_to_1654/with_CH4/20230207'
    path_without_ch4 = 'C:/Users/raynaudy/Documents/Manip/CH4/long_onde_1642_to_1654/without_CH4/20230207'
    #path = 'C:/Users/raynaudy/Documents/Manip/tests_synchro_pwrmtr/obstruction_laser/20230215'
    files_ch4 = os.listdir(path_ch4)
    files_without_ch4 = os.listdir(path_without_ch4)
    fits_files_ch4, fits_files_without_ch4 = [], []
    
    for name in files_ch4 :
        if specific in name and '.fits' in name:
            fits_files_ch4.append(path_ch4+'/'+name)
            print('FILE FOUND ')
            
    for name in files_without_ch4 :
        if specific in name and '.fits' in name:
            fits_files_without_ch4.append(path_without_ch4+'/'+name)
            print('FILE FOUND ')
        
    return(fits_files_ch4, fits_files_without_ch4)

get_files_absorb()


def get_i_io():    
    l_i, l_io, l_onde, medhdul = [],[],[],[]

    ff_ch4, ff_without_ch4 = get_files_absorb()
    #print(ff_ch4)
    for file in ff_ch4:
        hdul = fits.open(file)
        for i in range(1,len(hdul)):
            l_i.append(hdul[i].header['INTENSITE_POWER_METER'])
            l_onde.append(hdul[i].header['LAMBDA'])
            meddata = []
            data = hdul[i].data
            for j in range(0, len(data)):
                meddata.append(np.median(hdul[i].data[j]))
            medhdul.append(np.median(meddata))

    for file in ff_without_ch4:
        hdul = fits.open(file)
        for i in range(1,len(hdul)):
            l_io.append(hdul[i].header['INTENSITE_POWER_METER'])
    #print('\n l_i :  \n ', l_i, '\n l_io :  \n ', l_io)
    return(l_i,l_io,l_onde,medhdul)
    
#get_i_io()
    
def get_index_wvl(wvl, liste):
    closest_index = 0
    closest_distance = abs(wvl - liste[0])
    for i in range (1, len(liste)):
        #liste[i]= float(liste[i])
        distance = abs(wvl - liste[i])
        if distance < closest_distance:
            closest_index = i
            closest_distance = distance
    return(closest_index)
        
def get_absorbance():
    #global transmittance, absorbance
    #c = coeff correction des nan (pourcentage valeurs i-1 à prendre)
    c=0.4
    absorbance, transmittance, ttt = [],[], []
    l_i,l_io, l_onde, medhdul = get_i_io()
    l_i = [float(i) for i in l_i]
    #print(l_i)
    l_io = [float(i) for i in l_io]
    for i in range(0, len(l_i)):
        if l_i[i]<=0:
            l_i[i]=l_i[i-1]*c
    for i in range(0,len(l_io)):
        tt = l_i[i] / (l_io[i])
        aa = -math.log10(tt)
        #aa = math.log10(l_i[i] / (l_io[i]))
        absorbance.append(aa)
        transmittance.append(tt)
    graph_absorb(l_onde,transmittance,absorbance,medhdul)
    l_onde = to_cm_1(l_onde)
    index = get_index_wvl(v2, l_onde)
    return (l_onde,transmittance,absorbance,medhdul,index)

get_absorbance()


    
"""
try:
    a = math.log10(l_io[i]/l_i[i]*10**6)
    t = 10**-(a)*100
    tt = l_i[i] / (l_io[i]*10**6)
    aa = math.log10(tt)
except:
    a = 0
    t = 10**-(a)*100
    tt = 0
    absorbance.append(a)
    transmittance.append(t)
    ttt.append(tt)
else:
    absorbance.append(aa)
    transmittance.append(t)
    ttt.append(tt)
            """
def get_pic_absorbance(pics):
    l_onde,t,a,medhdul, index = get_absorbance()
    maxs, index_maxs=[],[]
    for i in range(0, pics):
        maxs.append(np.max(a))
        index_maxs.append(a.index(np.max(a)))
        a.remove(np.max(a))
    return(maxs, index_maxs)


def get_concentration():
    pics = 5
    #Experience : T = 296K (22°C)    P = 1 atm   L = 10cm
    #               
    #◘ Loi de Beer Lambert : C = A / (epsilon x l)
    # C concentration, A absorbance, Epsilon coefficient d'extinction molaire, l largeur cuve
    #c = A/sv*l
    l = 10
    l_onde,t,a,medhdul, index = get_absorbance()
    maxs, index_maxs = get_pic_absorbance(pics)
    print('index : ', index, 'l_onde : ', l_onde[index], 'absorbance :' , a[index])
    print(np.max(a))
    c = a[index_maxs[3]] / (sv2 * l)
    print('concentration en CH4 ' , c, ' molecules par cm3')

get_concentration()
    
    #calcul de la concentration via une courbe d'etallonage
    
    
#get_concentration()   
    
    