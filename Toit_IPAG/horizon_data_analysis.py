# -*- coding: utf-8 -*-
"""
Created on Thu May  4 09:56:29 2023

@author: raynaudy
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
    #recupere les fichiers fits que l'on veut analyser et les met dans une liste
    #les fichiers viennent de path mais dans specific on peut rajouter un mot contenu dans les fichiers que l'on veut pour selectionner que ceux voulu
    path = r'C:\Users\raynaudy\Documents\Manip\Toit_IPAG\Horizon\20230503_CH4\20230503'
    #path = 'C:/Users/raynaudy/Documents/Manip/tests_synchro_pwrmtr/obstruction_laser/20230215'
    files = os.listdir(path)
    fits_files = []
    specific = 'CH4'
    for name in files:
        if specific in name and '.fits' in name:
            fits_files.append(path+'/'+name)
            print('FILE FOUND ')
        else :
            print('NO MATCH')
    return(fits_files)

def graph_data(wvl,pwrmtr,io,cam):
    #graph les wvl en focntion du retour de chaque image, du io_pwrmtr (nA) et io source 
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
    #recup les wvl io_source, io_pwrmtr, temperature et la date de chaque image
    l_onde, l_int, l_pwrmtr, l_temp, l_date = [],[],[],[],[]
    for i in range(1,len(f)):
        l_onde.append(f[i].header['LAMBDA'])
        l_int.append(f[i].header['HIERARCH INTENSITE'])
        l_pwrmtr.append(f[i].header['INTENSITY_POWER_METER'])
        l_temp.append(f[i].header['TEMPERATURE'])
        l_date.append(f[i].header['EXTNAME'])
    return(l_onde, l_int, l_pwrmtr, l_temp, l_date)

def to_cm_1(f):
    for i in range(0, len(f)):
        if float(f[i]) != 0:
            f[i] = 10**7 / float(f[i])
    return(f)    

def get_date_in_secondes_from_header():
    fits_files = get_files()
    print(fits_files)
    for file in fits_files:
        hdul = fits.open(file)    
        
    # Boucle sur toutes les images du fichier FITS
        for i in range(len(hdul)):
            # Extraire l'EXTNAME du header de l'image
            extname = hdul[i].header['EXTNAME']
            # Extraire la date et l'heure du nom de l'image
            date_string = extname.split('_')[0]
            time_string = extname.split('_')[1]
            # Convertir la date et l'heure en un objet datetime
            date_time_obj = datetime.datetime.strptime(date_string + time_string, '%Y%m%d%H%M%S')
            # Calculer le temps en secondes depuis le début de l'année
            time_in_seconds = (date_time_obj - datetime.datetime(date_time_obj.year, 1, 1)).total_seconds()
            print("L'image %d a été prise le %s à %s. Temps écoulé depuis le début de l'année : %d secondes." % (i, date_string, time_string, time_in_seconds))
        
    # Fermer le fichier FITS
    hdul.close()
    
    
def get_date_in_secondes_from_list(l_date):
    #retourne les donnees de l_date du format YMD_HmS_imagenb en seconde
    #utile pour grapher les data de maniere chronologiques
    
    # Liste pour stocker les dates en secondes
    dates_sec = []
    
    # Boucle à travers toutes les valeurs de 'EXTNAME' dans la liste 'l_date'
    for extname in l_date:
        # Extraire la date et l'heure de l'image à partir du paramètre 'EXTNAME'
        date_str = extname.split(',')[0].rstrip('_')
        #print('date_str = ', date_str)
        date_obj = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
        
        # Convertir la date et l'heure en secondes et l'ajouter à la liste
        date_sec = int(date_obj.timestamp())
        dates_sec.append(date_sec)
            
    # Afficher la liste de dates en secondes
    return(dates_sec)
            
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
    print('l_onde = :' , l_onde, '\n' )
    l_onde = to_cm_1(l_onde)

    #return(l_onde, l_int, l_pwrmtr, l_temp, l_date, medhdul)
    #graph_data(l_onde,l_pwrmtr,l_int,medhdul)
    dates_sec = get_date_in_secondes_from_list(l_date)
    print('l_date : ', l_date, '\n')
    print('dates_sec : ', dates_sec, '\n')
    print('medhdul : ', medhdul)
    
    a = np.linspace(0,151, num=len(medhdul))
    fig, (ax1,ax2,ax3,ax4) = plt.subplots(4,1,figsize=(10, 10))#,figsize=(8, 6)
    fig.subplots_adjust(hspace=0.3)

    ax1.plot(dates_sec,np.asarray(l_temp, float),color='red',label='mean') 
    ax1.set_xlabel('Date de lacquistion')
    ax1.set_ylabel('Température (en K)') 
    ax2.plot(np.asarray(l_onde, float),l_pwrmtr,label='mean') 
    ax2.set_xlabel('$\lambda$ [cm-1]')
    ax2.set_ylabel('PwrMtr')
    ax3.plot(np.asarray(l_onde, float),l_int,label='mean') 
    ax3.set_xlabel('$\lambda$ [cm-1]')
    ax3.set_ylabel('Intensite source [mA]')
    ax4.plot(np.asarray(l_onde, float),medhdul,label='mean') 
    ax4.set_xlabel('$\lambda$ [cm-1]')
    ax4.set_ylabel('l_int')

get_data_both()  
    
  
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