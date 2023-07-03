# -*- coding: utf-8 -*-
"""
Created on Thu May  4 15:01:46 2023

@author: raynaudy
"""

"""
Programe pour analyser les datas de la 1ere manip faites sur le toit vue à l'horizon

1) graph la temperature pour voir quand les caméras ont surchauffé

2) graph 

3 ) afficher les imagettes 

4) determiner concetration C02/CH4



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
    """
    wavelength, intensity, power_meter, temperature, date = [], [], [], [], []
    for i in range(1, len(hdul)):
        wavelength.append(hdul[i].header['LAMBDA'])
        intensity.append(hdul[i].header['HIERARCH INTENSITE'])
        power_meter.append(hdul[i].header['INTENSITY_POWER_METER'])
        temperature.append(hdul[i].header['TEMPERATURE'])
        date.append(hdul[i].header['EXTNAME'])
    return wavelength, intensity, power_meter, temperature, date
  
def to_cm_1(f):
    """
    Cette fonction convertit les longueurs d'onde en inverse centimètres.
    """
    for i in range(len(f)):
        if float(f[i]) != 0:
            f[i] = 10**7 / float(f[i])
    return f


def convert_date_in_seconds(dates):
    #retourne les donnees de l_date du format YMD_HmS_imagenb en seconde
    #utile pour grapher les data de maniere chronologiques
    
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
    wavelengths, io_source, power_meter, temperatures, dates = [], [], [], [], []
    fits_files = get_files(path, specific)
    print(f'Fichiers trouvés : {fits_files}')
    for file in fits_files:
        hdul = fits.open(file)
        w, i, pm, t, d = extract_header_info(hdul)
        wavelengths.extend(w)
        io_source.extend(i)
        power_meter.extend(pm)
        temperatures.extend(t)
        dates.extend(d)
    wavelengths = to_cm_1(wavelengths)
    print('first dates : ' , dates[0])
    dates = convert_date_in_seconds(dates)
    print('second dates : ', dates[0])
    #print(wavelengths, io_source, power_meter, temperatures, dates)
    return(wavelengths, io_source, power_meter, temperatures, dates)

def get_median_pixels(path, specific):
    """
    Retourne la médiane de la valeur de tous les pixels de l'ensemble des images
    Pas très utile pour une caméra hyperspectrales avec plusieurs imagette
    Plus un test qu'autre chose
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
    wavelengths, io_source, power_meter, temperatures, dates = get_data(path, specific)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
    fig.subplots_adjust(hspace=0.4)
    ax1.plot(dates,np.asarray(temperatures, float),color='red',label='mean') 
    ax1.set_xlabel('Date d\'acquistion')
    ax1.set_ylabel('Température (en K)')
    ax1.set_title('Température en fonction de la date d\'acquistion')
    ax2.plot(wavelengths, power_meter, label='Intensité courant power meter')
    ax2.set_xlabel('Longueur d\'onde (en cm^-1)')
    ax2.set_ylabel('Intensité courant (en nA)')
    ax2.set_title('Intensité courant en fonction de la longueur d\'onde')
    plt.show()       

def graph_temperature_both_gas():
    """
    Trace les graph des datas récup, à modif selon envie
    Trace pour les 2 gaz specifiés
    """
    wavelengths_gas_1, io_source_gas_1, power_meter_gas_1, temperatures_gas_1, dates_gas_1 = get_data(path_gas_1, specific_gas_1)
    wavelengths_gas_2, io_source_gas_2, power_meter_gas_2, temperatures_gas_2, dates_gas_2 = get_data(path_gas_2, specific_gas_2)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
    fig.subplots_adjust(hspace=0.4)
    ax1.plot(dates_gas_1,np.asarray(temperatures_gas_1, float),color='red',label='mean') 
    ax1.set_xlabel('Date d\'acquistion')
    ax1.set_ylabel('Température (en K)')
    ax1.set_title('Température en fonction de la date d\'acquistion pour le  {}'.format(gas1))
    ax2.plot(dates_gas_2,np.asarray(temperatures_gas_2, float),color='red',label='mean') 
    ax2.set_xlabel('Date d\'acquistion')
    ax2.set_ylabel('Température (en K)')
    ax2.set_title('Température en fonction de la date d\'acquistion pour le  {}'.format(gas2))
    plt.show()


path = r'C:\Users\raynaudy\Documents\Manip\Toit_IPAG\Horizon\20230503_CH4\20230503'
specific = 'CH4'

path_gas_1 = r'C:\Users\raynaudy\Documents\Manip\Toit_IPAG\Horizon\20230503_CH4\20230503'
specific_gas_1 = 'CH4'
gas1= 'CH4'

path_gas_2 = r'C:\Users\raynaudy\Documents\Manip\Toit_IPAG\Horizon\20230503_CO2\20230503'
specific_gas_2 = 'CO2'
gas2 ='CO2'

#graph_temperature_both_gas()
#get_median_pixels(path, specific)