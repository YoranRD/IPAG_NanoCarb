# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 15:52:06 2023

@author: raynaudy


Manip :
    Determiner si la cellule à gaz est hermétique ou non 
    
    Materiel :
        Cam nue, Cellule à gaz, Laser Accordable, Sphere integrante, Pwr Meter, Lambdametre, Collimateur IR
    
    Prendre un mesure de référence avec la cam nue et la cellule vide (sans CH4) sur un game spectrale definie (1665 to 1668 nm)
    Injecter du CH4 dans la cellule
    Effectuer des mesures toutes les 45min avec le même montage et sur la même game spectrale que pour la ref 
    
    Avec les dates calculer l'absorbance, transmittance de la cellule => concentration de CH4 pour chaque mesure
    La concentration est elle stable dans le temps ?


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
from scipy.signal import medfilt


def get_files(path, specific):
    """
    Récupère les fichiers FITS que l'on veut analyser et les met dans une liste.
    Les fichiers viennent de 'path', mais on peut rajouter un mot contenu dans les fichiers que l'on veut pour sélectionner ceux voulus.
    """
    files = os.listdir(path)
    fits_files = []
    for name in files:
        if specific in name and '.fits' in name:
            fits_files.append(path+'/'+name)
            print('FILE FOUND ')
        else:
            print('NO MATCH')
    return(fits_files)

    
def extract_header_info(hdul):
    """
    Récupère les informations de l'en-tête FITS.
    ATTENTION !!! Le header INTENSITE_POWER_METER a été changé en INTENSITY_POWER_METER en Mai 2023
    toute manip avant aura le nom INTENSITE_POWER_METER en header, toute manip apres aura INTENSITY_POWER_METER
    """
    wavelength, intensity, power_meter, temperature, date = [], [], [], [], []
    for i in range(1, len(hdul)):
        wavelength.append(hdul[i].header['LAMBDA'])
        intensity.append(hdul[i].header['HIERARCH INTENSITE'])
        power_meter.append(hdul[i].header['INTENSITY_POWER_METER'])
        #power_meter.append(hdul[i].header['INTENSITE_POWER_METER'])
        temperature.append(hdul[i].header['TEMPERATURE'])
        date.append(hdul[i].header['EXTNAME'])
    return wavelength, intensity, power_meter, temperature, date
  
def to_cm_1(f):
    """
    Cette fonction convertit les longueurs d'onde nm en cm-1.
    """
    f_cm=[]
    for i in range(len(f)):
        if float(f[i]) != 0:
            f_cm.append(10**7 / float(f[i]))
    return f_cm


def convert_date_in_seconds(dates):
    """
    retourne les donnees de l_date du format YMD_HmS_imagenb en seconde
    utile pour grapher les data de maniere chronologiques
    """
    # Liste pour stocker les dates en secondes
    dates_sec = []
    
    # Boucle à travers toutes les valeurs de 'EXTNAME' dans la liste 'l_date'
    for extname in dates:
        # Extraire la date et l'heure de l'image à partir du paramètre 'EXTNAME'
        date_str = extname.split(',')[0].rstrip('_')
        #print('date_str = ', date_str)
        date_obj = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
        
        # Convertir la date et l'heure en secondes et l'ajouter à la liste
        date_sec = int(date_obj.timestamp())
        dates_sec.append(date_sec)
            
    # Afficher la liste de dates en secondes
    return(dates_sec)
          
def get_data(path, specific):
    """
    Récupère les informations de l'en-tête FITS et les données de la caméra et du power meter pour chaque fichier FITS dans 'path'.
    """
    medhdul,wavelengths, io_source, power_meter, temperatures, dates = [], [], [], [], [], []
    fits_files = get_files(path, specific)
    print('path       :', path)
    print(f'Fichiers trouvés : {fits_files}')
    for file in fits_files:
        hdul = fits.open(file)
        w, i, pm, t, d = extract_header_info(hdul)
        wavelengths.extend(w)
        io_source.extend(i)
        power_meter.extend(pm)
        temperatures.extend(t)
        dates.extend(d)

        for i in range(1,len(hdul)):
            meddata = []
            data = hdul[i].data
            for j in range(0, len(data)):
                meddata.append(np.median(hdul[i].data[j]))
            medhdul.append(np.median(meddata))
            
    wavelengths_lambda = wavelengths
    wavelengths = to_cm_1(wavelengths)
    #print('first dates : ' , dates[0])
    dates = convert_date_in_seconds(dates)
    #print('second dates : ', dates[0])
    return(medhdul,wavelengths, io_source, power_meter, temperatures, dates,wavelengths_lambda)

def get_median_pixels(path, specific):
    """
    Retourne la médiane de la valeur de tous les pixels de l'ensemble des images
    Pas très utile pour une caméra hyperspectrales avec plusieurs imagette
    Utile pour la caméra nue
    """
    fits_files = get_files(path, specific)
    print(f'Fichiers trouvés : {fits_files}')
    for file in fits_files:
        hdul = fits.open(file)
        medhdul = []
        for i in range(1,len(hdul)):
            meddata = []
            data = hdul[i].data
            for j in range(0, len(data)):
                meddata.append(np.median(hdul[i].data[j]))
            medhdul.append(np.median(meddata))
    print(medhdul)
    return(medhdul)


def graph_temperature():
    """
    Trace les graph des datas récup pour un gaz, à modif selon envie
    """
    medhdul,wavelengths, io_source, power_meter, temperatures, dates,wavelengths_lambda = get_data(path, specific)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
    fig.subplots_adjust(hspace=0.4)
    ax1.plot(wavelengths,temperatures,color='red',label='mean') 
    ax1.set_xlabel('Date d\'acquistion')
    ax1.set_ylabel('Température (en K)')
    ax1.set_title('Température en fonction de la date d\'acquistion')
    ax2.plot(wavelengths, power_meter, label='Intensité courant power meter')
    ax2.set_xlabel('Longueur d\'onde (en cm^-1)')
    ax2.set_ylabel('Intensité courant (en nA)')
    ax2.set_title('Intensité courant en fonction de la longueur d\'onde')
    print(temperatures)
    plt.show()       

def graph_acqui():
    """
    Trace les graph des datas récup pour un gaz, à modif selon envie
    """
    medhdul,wavelengths, io_source, power_meter, temperatures, dates,wavelengths_lambda = get_data(path, specific)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
    fig.subplots_adjust(hspace=0.4)
    ax1.plot(dates,np.asarray(medhdul, float),color='red',label='mean') 
    ax1.set_xlabel('Date d\'acquistion')
    ax1.set_ylabel('Intensite de la caméra')
    ax1.set_title('Intensite en fonction de la longueur donde')
    ax2.plot(wavelengths, power_meter, label='Intensité courant power meter')
    ax2.set_xlabel('Longueur d\'onde (en cm^-1)')
    ax2.set_ylabel('Intensité courant (en nA)')
    ax2.set_title('Intensité courant en fonction de la longueur d\'onde')
    plt.show() 

def get_min(min_io):
    """
    Recupère les valeurs des acquisitions inferieures à un seuil (min_io) et leur index
    Les retourne sous 2 listes wvl_abs,int_abs
    Cela permet de déterminer où se situent les pics d'absorption et les localiser plus tard
    Ca fonctionne mais la logique est pas folle, cette fonction peut être améliorée en étant repensée
    """
    
    #l_onde, l_int, l_pwrmtr, l_temp, l_date, medhdul,wvl_abs,int_abs = [], [], [] ,[],[],[],[],[]
    #l_onde, l_int, l_pwrmtr, l_temp, l_date, medhdul = get_data()
    #medhdul = get_median_pixels(path, specific)
    medhdul,wavelengths, io_source, power_meter, temperatures, dates,wavelengths_lambda = get_data(path, specific)
    wvl_abs,wvl_lambda_abs,int_abs = [], [], []
    for i in range(0,len(medhdul)):
        if medhdul[i]<min_io:
            wvl_abs.append(wavelengths[i])
            wvl_lambda_abs.append(wavelengths_lambda[i])
            int_abs.append(medhdul[i])
    print('wavelengths_lambda : ', wvl_lambda_abs, '\nwvl : ', wvl_abs,'\nintensite : ' , int_abs)
    graph_temperature()
    return(wvl_abs,int_abs)

"""
def get_abs():

    Recupère les zones d'absoprtion et détermine le minimum local (le pic) de chaque zone et leur index respectif
    Les retourne sous 2 listes wvlabs, intabs

    wvl_abs, int_abs = get_min(min_io)
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
  
    
"""




"""
Absorbance A= log10(Io/I)
Beer Lambert : A = e*l*c
    avec 
        A est l’absorbance ou la densité optique de la solution pour une longueur d’onde λ
        c (en mol.L-1) est la concentration de l’espèce absorbante 
        l (en cm) est la longueur du trajet optique
        e epsilon (en mol-1.L.cm-1) est le coefficient d’extinction molaire de l’espèce absorbante en solution.

"""


def graph_absorb(T ,A):
    
    intensity_with_CH4,wavelengths_with_CH4, io_source_with_CH4, power_meter_with_CH4,\
        temperatures_with_CH4, dates_with_CH4,wavelengths_lambda_with_CH4 \
            =get_data(path_ch4, specific) 
    intensity_without_CH4,wavelengths_without_CH4, io_source_without_CH4, power_meter_without_CH4,\
        temperatures_without_CH4, dates_without_CH4,wavelengths_lambda_without_CH4\
            = get_data(path_without_ch4, specific)    
    
    fig, (ax1,ax2,ax3,ax4) = plt.subplots(4,1,figsize=(16, 16))#,figsize=(8, 6)
    fig.subplots_adjust(hspace=0.6)
    #for i incam = 1/cam 
    
    ax1.plot(np.asarray(wavelengths_with_CH4, float),intensity_with_CH4,color='red',label='mean') 
    ax1.set_xlabel('$\lambda$ [cm-1]')
    ax1.set_ylabel('Intensité de la caméra (avec CH4)')  
    ax1.set_title('Intensité de la caméra en fonction de la longueur donde avec la cellule à gaz remplis de CH4')
    
    ax2.plot(np.asarray(wavelengths_without_CH4, float), intensity_without_CH4,color='green',label='mean')
    ax2.set_ylim(bottom=0)
    ax2.set_xlabel('$\lambda$ [cm-1]')
    ax2.set_ylabel('Intensité de la caméra (sans CH4)') 
    ax2.set_title('Intensité de la caméra en fonction de la longueur donde sans la cellule à gaz remplis de CH4')
                  
    ax3.plot(np.asarray(wavelengths_with_CH4, float),A,label='mean') 
    ax3.set_xlabel('$\lambda$ [cm-1]')
    ax3.set_ylabel('Absorbance ')
    ax3.set_title('Absorbance calculée de la cellule à gaz e fonctionb de la longueur donde')
    
    ax4.plot(np.asarray(wavelengths_with_CH4, float),T,label='mean') 
    ax4.set_xlabel('$\lambda$ [cm-1]')
    ax4.set_ylabel('Transmittance')
    ax4.set_title('Absorbance calculée de la cellule à gaz e fonctionb de la longueur donde')    

    plt.show()
   


def get_files_absorb(path_ch4,path_without_ch4,specific):

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




def get_i_io():    
    l_i, l_io, l_onde, medhdul = [],[],[],[]

    ff_ch4, ff_without_ch4 = get_files_absorb(path_ch4,path_without_ch4,specific)
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
    graph_absorb(transmittance,absorbance)
    l_onde = to_cm_1(l_onde)
    index = get_index_wvl(v2, l_onde)
    return (l_onde,transmittance,absorbance,medhdul,index)



    
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
    l = 5
    l_onde,t,a,medhdul, index = get_absorbance()
    maxs, index_maxs = get_pic_absorbance(pics)
    print('index : ', index, 'l_onde : ', l_onde[index], 'absorbance :' , a[index])
    print(np.max(a))
    c = a[index_maxs[3]] / (sv2 * l)
    print('concentration en CH4 ' , c, ' molecules par cm3')


    
    #calcul de la concentration via une courbe d'etallonage
    
    
def check_cellule_stability():
    """
    Vérifie la stabilité des cellules en analysant les fichiers FITS du dossier 'path'
    qui contiennent l'un des mots de la liste 'specific_multi'.
    Exporte les données et les graphiques de chaque élément sur le même graphique avec un code couleur.
    Les paramètres à afficher sur le graphique sont les mêmes que ceux de la fonction graph_acqui().
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
    fig.subplots_adjust(hspace=0.4)
    colors = ['red', 'blue', 'green', 'orange', 'purple']  # Liste de couleurs pour les éléments

    for i, spec in enumerate(specific_multi):
        medhdul, wavelengths, io_source, power_meter, temperatures, dates, wavelengths_lambda = get_data(path, spec)
        # Tri des valeurs aberrantes avec la médiane des valeurs environnantes
        #median_filtered = medfilt(wavelengths, kernel_size=11)

        ax1.plot(wavelengths, medhdul, color=colors[i % len(colors)], label=spec)
        ax2.set_xlabel('Longueur d\'onde (en cm^-1)')
        ax1.set_ylabel('Intensité de la caméra')
        ax1.set_title('Intensité en fonction de la longueur d\'onde')
        #ax1.set_ylim(ymin=11000) 
        ax2.plot(wavelengths, medhdul, color=colors[i % len(colors)], label=spec)
        ax2.set_xlabel('Date d\'acquisition')
        ax2.set_ylabel('Intensité courant (en nA)')
        ax2.set_title('Intensité courant en fonction de la longueur d\'onde')
    ax1.legend()
    plt.show()
    
    
def volume_cellule():
    rayon, hauteur = 5,10
    volume = math.pi * rayon ** 2 * hauteur
    return volume    

def get_pression():
    volume = volume_cellule()
    temperature = 22 + 273.15
    path_length = 10
    molar_absorptivity = 1
    R_gas = 8.314 
    
    intensity_with_CH4, wavelengths_with_CH4, io_source_with_CH4, power_meter_with_CH4, \
        temperatures_with_CH4, dates_with_CH4, wavelengths_lambda_with_CH4 = get_data(path_ch4, specific)
    intensity_without_CH4, wavelengths_without_CH4, io_source_without_CH4, power_meter_without_CH4, \
        temperatures_without_CH4, dates_without_CH4, wavelengths_lambda_without_CH4 = get_data(path_without_ch4, specific)
    
    # Calcul de l'absorbance
    absorbance = -np.log10(intensity_with_CH4 / intensity_without_CH4)
    
    # Calcul de la transmittance
    transmittance = intensity_with_CH4 / intensity_without_CH4
    
    # Estimation de la concentration de CH4 avec Beer-Lambert
    concentration = -absorbance / (molar_absorptivity * path_length)
    
    # Calcul de la pression avec l'équation des gaz parfaits
    pressure = (concentration * R_gas * temperature) / volume
    
    return pressure


    
    """
    for spec in specific_multi:

        medhdul,wavelengths, io_source, power_meter, temperatures, dates,\
            wavelengths_lambda = get_data(path, spec)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        fig.subplots_adjust(hspace=0.4)
        ax1.plot(dates,np.asarray(medhdul, float),color='red',label='mean') 
        ax1.set_xlabel('Date d\'acquistion')
        ax1.set_ylabel('Intensite de la caméra')
        ax1.set_title('Intensite en fonction de la longueur donde')
        ax2.plot(wavelengths, power_meter, label='Intensité courant power meter')
        ax2.set_xlabel('Longueur d\'onde (en cm^-1)')
        ax2.set_ylabel('Intensité courant (en nA)')
        ax2.set_title('Intensité courant en fonction de la longueur d\'onde')
        plt.show() 

    """
global wvl_v1, wvl_v2, wvl_v3, wvl_v4

global v1,v2,v3,v4,v5
v1,v2,v3,v4,v5 = 6046.93, 6057.03, 6066.98, 6077, 6086.79

global wl1, wl2, wl3, wl4, wl5
wl1, wl2, wl3, wl4, wl5 = 1/v1*10000000, 1/v2*10000000, 1/v3*10000000, 1/v4*10000000, 1/v5*10000000

global sv1, sv2, sv3, sv4, sv5
sv1, sv2, sv3, sv4, sv5 = 2.2*10**-20, 4.6*10**-20, 7.5*10**-20, 1.8*10**-20, 3.9*10**-20
#print('\n', wl1,'\n', wl2,'\n', wl3,'\n', wl4,'\n', wl5)


#path = r'C:\Users\raynaudy\Documents\Manip\manip_laser_accordable\CH4\long_onde_1642_to_1654\with_CH4\20230207'
#path = r'C:\Users\raynaudy\Documents\cellue_gaz_ch4_bombone\cam_nue\ref_avec_ch4\20230605'
path = r'C:\Users\raynaudy\Documents\Manip\cellule_gaz_ch4_bombone\cam_nue\ref_avec_ch4\20230608'
path_ch4 = r'C:\Users\raynaudy\Documents\Manip\manip_laser_accordable\CH4\long_onde_1642_to_1654\with_CH4\20230207'
path_without_ch4 = r'C:\Users\raynaudy\Documents\Manip\manip_laser_accordable\CH4\long_onde_1642_to_1654\without_CH4\20230207'
specific = 'H+0'
specific_multi = ['H+45m','H+90m','H+135m']
min_io = 1500

#graph_temperature_both_gas()
#get_median_pixels(path, specific)
#get_files_absorb(path_ch4,path_without_ch4,specific)
#get_min(1500)
#get_abs()
#get_concentration()

#graph_acqui()
check_cellule_stability()

#graph_temperature()

