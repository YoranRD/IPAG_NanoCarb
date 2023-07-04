# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 15:52:06 2023

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
    return(wvl_abs,int_abs)




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
        
    

def get_pic_absorbance(pics):
    """
    Retounre la valeur des pics d'absorption et leur index
    La variable pics que l'on indique à la fonction correspond au nombre de pics que l'on veut avoir en liste
    Deux problemes :
            Faire la même fonction avec les minimums locaux : absorption correspond à min, pas à max
            Prend des valeurs sur même pics, on doit le forcer à trouver des pics différents
    
    """
    absorbance, transmittance, concentration, pression = get_pression()
    maxs, index_maxs=[],[]
    for i in range(0, pics):
        maxs.append(np.max(absorbance))
        index_maxs.append(absorbance.index(np.max(absorbance)))
        absorbance.remove(np.max(absorbance))
    return(maxs, index_maxs)

    

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
    
def check_stability_no_path_needed(intensity_with_CH4, wavelengths_with_CH4, io_source_with_CH4, power_meter_with_CH4, \
    temperatures_with_CH4, dates_with_CH4, wavelengths_lambda_with_CH4):
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
        # Tri des valeurs aberrantes avec la médiane des valeurs environnantes
        #median_filtered = medfilt(wavelengths, kernel_size=11)

        ax1.plot(wavelengths_with_CH4, intensity_with_CH4, color=colors[i % len(colors)], label=spec)
        ax2.set_xlabel('Longueur d\'onde (en cm^-1)')
        ax1.set_ylabel('Intensité de la caméra')
        ax1.set_title('Intensité en fonction de la longueur d\'onde')
        #ax1.set_ylim(ymin=11000) 
        ax2.plot(wavelengths_with_CH4, intensity_with_CH4, color=colors[i % len(colors)], label=spec)
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
    #Experience : T = 296K (22°C)    P = 1 atm   L = 10cm
    #               
    #◘ Loi de Beer Lambert : C = A / (epsilon x l)
    # C concentration, A absorbance, Epsilon coefficient d'extinction molaire, l largeur cuve
    #c = A/sv*l
    
    volume = volume_cellule()
    temperature = 22 + 273.15
    path_length = 10
    molar_absorptivity = 1
    R_gas = 8.314 
    
    intensity_with_CH4, wavelengths_with_CH4, io_source_with_CH4, power_meter_with_CH4, \
        temperatures_with_CH4, dates_with_CH4, wavelengths_lambda_with_CH4 = get_data(path_ch4, specific_ch4)
    intensity_without_CH4, wavelengths_without_CH4, io_source_without_CH4, power_meter_without_CH4, \
        temperatures_without_CH4, dates_without_CH4, wavelengths_lambda_without_CH4 = get_data(path_without_ch4, specific_without_ch4)
    
    # Vérification de la taille des listes
    if len(intensity_with_CH4) != len(intensity_without_CH4):
        min_length = min(len(intensity_with_CH4), len(intensity_without_CH4))
        intensity_with_CH4 = intensity_with_CH4[:min_length]
        intensity_without_CH4 = intensity_without_CH4[:min_length]
    
    # Initialisation des listes
    absorbance = []
    transmittance = []
    concentration = []
    pression = []
    
    for i in range(len(intensity_with_CH4)):
        # Calcul de l'absorbance
        abs_val = -math.log10(intensity_with_CH4[i] / intensity_without_CH4[i])
        absorbance.append(abs_val)
    
        # Calcul de la transmittance
        trans_val = intensity_with_CH4[i] / intensity_without_CH4[i]
        transmittance.append(trans_val)
    
        # Estimation de la concentration de CH4 avec Beer-Lambert
        conc_val = -abs_val / (molar_absorptivity * path_length)
        concentration.append(conc_val)
    
        # Calcul de la pression avec l'équation des gaz parfaits
        press_val = (conc_val * R_gas * temperature) / volume
        pression.append(press_val)
    
    
    """
    # Calcul de l'absorbance
    absorbance = -np.log10(intensity_with_CH4 / intensity_without_CH4)
    
    # Calcul de la transmittance
    transmittance = intensity_with_CH4 / intensity_without_CH4
    
    # Estimation de la concentration de CH4 avec Beer-Lambert
    concentration = -absorbance / (molar_absorptivity * path_length)
    
    # Calcul de la pression avec l'équation des gaz parfaits
    pression = (concentration * R_gas * temperature) / volume
    """
    
    print('Pression = ', pression)
    return (absorbance, transmittance, concentration, pression, intensity_with_CH4, wavelengths_with_CH4, io_source_with_CH4, power_meter_with_CH4, \
        temperatures_with_CH4, dates_with_CH4, wavelengths_lambda_with_CH4 )


def routine():
    check_cellule_stability()
    absorbance, transmittance, concentration, pression, intensity_with_CH4, wavelengths_with_CH4, io_source_with_CH4, power_meter_with_CH4, \
        temperatures_with_CH4, dates_with_CH4, wavelengths_lambda_with_CH4 = get_pression()
        
    
    fig, (ax1,ax2,ax3,ax4) = plt.subplots(4,1,figsize=(16, 16))#,figsize=(8, 6)
    fig.subplots_adjust(hspace=0.6)
    #for i incam = 1/cam 
    
    ax1.plot(np.asarray(wavelengths_with_CH4, float),absorbance,color='red',label='mean') 
    ax1.set_xlabel('$\lambda$ [cm-1]')
    ax1.set_ylabel('Absorbance ')
    ax1.set_title('Absorbance calculée de la cellule à gaz en fonction de la longueur donde')
    
    ax2.plot(np.asarray(wavelengths_with_CH4, float), transmittance,color='green',label='mean')
    ax2.set_ylim(bottom=0)
    ax2.set_xlabel('$\lambda$ [cm-1]')
    ax2.set_ylabel('Transmittance') 
    ax2.set_title('Transmittance calculée de la cellule à gaz en fonction de la longueur donde')
                  
    ax3.plot(np.asarray(wavelengths_with_CH4, float),concentration,label='mean') 
    ax3.set_xlabel('$\lambda$ [cm-1]')
    ax3.set_ylabel('Concentration')
    ax3.set_title('Concentration calculée de la cellule à gaz en fonction de la longueur donde')
    
    ax4.plot(np.asarray(wavelengths_with_CH4, float),pression,label='mean') 
    ax4.set_xlabel('$\lambda$ [cm-1]')
    ax4.set_ylabel('Pression')
    ax4.set_title('Pression calculée de la cellule à gaz en fonction de la longueur donde')    

    plt.show()
    

global wvl_v1, wvl_v2, wvl_v3, wvl_v4

global v1,v2,v3,v4,v5
v1,v2,v3,v4,v5 = 6046.93, 6057.03, 6066.98, 6077, 6086.79

global wl1, wl2, wl3, wl4, wl5
wl1, wl2, wl3, wl4, wl5 = 1/v1*10000000, 1/v2*10000000, 1/v3*10000000, 1/v4*10000000, 1/v5*10000000

global sv1, sv2, sv3, sv4, sv5
sv1, sv2, sv3, sv4, sv5 = 2.2*10**-20, 4.6*10**-20, 7.5*10**-20, 1.8*10**-20, 3.9*10**-20


path = r'C:\Users\raynaudy\Documents\Manip\deuxieme_cellule_a_gaz\cam_nue\ref_avec_ch4\20230608'
path_ch4 = r'C:\Users\raynaudy\Documents\Manip\deuxieme_cellule_a_gaz\cam_nue\ref_avec_ch4\20230608'
path_without_ch4 = r'C:\Users\raynaudy\Documents\Manip\deuxieme_cellule_a_gaz\cam_nue\ref_sans_ch4\20230605'
specific, specific_ch4, specific_without_ch4 = 'H+0', 'H+0', 'pas_350'
specific_multi = ['H+0m','H+45m','H+90m','H+135m']
min_io = 1500

#graph_temperature_both_gas()
#get_median_pixels(path, specific)
#get_files_absorb(path_ch4,path_without_ch4,specific)
#get_min(1500)
#get_abs()
#get_concentration()

#graph_acqui()
#check_cellule_stability()
#get_pression()
#graph_temperature()

routine()