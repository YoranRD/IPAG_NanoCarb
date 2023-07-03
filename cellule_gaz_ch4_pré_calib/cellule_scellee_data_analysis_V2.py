# -*- coding: utf-8 -*-
"""
Created on Thu May  4 15:01:46 2023

@author: raynaudy
"""

"""


Objectif :
   	Déterminer la concentration en CH4 de la cellule
   Déterminer la pression?
	Tester nos caméras Nanocarb
	Tester nos codes


Manip 1 : CAMERA NUE

	Materiel : 	Caméra nue, Cellule à gaz précalibrée, Laser Accordable, Sphere integrante, 
			Pwr Meter, Lambdametre, Collimateur IR


Protocole :
	Faire une acquisition de ref sans la cellule à gaz sur un game spectrale avec le LA
	Faire une autre acquisition sur meme game spectrale avec la cellule à gaz

	Calculer avec Beer Lambert la concentration etc ...

PROBLEME :
	Nous n'avons pas de cellule à gaz identique de même taille mais vide
	Donc la référence n'est aps de qualité car le trajet optique n'est pas le même
	Pas de trajet à travers de surface de verre comme l'acquisition avec la cellule optique



"""
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import os
from datetime import datetime
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
            print('FILE FOUND \n', path+'/'+name )

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
        power_meter.append(hdul[i].header['INTENSITE_POWER_METER'])
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
          
def get_data(fits_files):
    """
    Récupère les informations de l'en-tête FITS et les données de la caméra et du power meter pour chaque fichier FITS dans 'path'.
    """
    medhdul,wavelengths, io_source, power_meter, temperatures, dates = [], [], [], [], [], []

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
    dates = convert_date_in_seconds(dates)
    return(medhdul,wavelengths, io_source, power_meter, temperatures, dates,wavelengths_lambda)

def get_data_path(fits_files):
    """
    Récupère les informations de l'en-tête FITS et les données de la caméra et du power meter pour chaque fichier FITS dans 'path'.
    """
    medhdul,wavelengths, io_source, power_meter, temperatures, dates = [], [], [], [], [], []

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
    print('first dates : ' , dates[0])
    dates = convert_date_in_seconds(dates)
    print('second dates : ', dates[0])
    return(medhdul,wavelengths, io_source, power_meter, temperatures, dates,wavelengths_lambda)

def get_median_pixels(fits_files):
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
    fits_files = get_files(path, specific)
    medhdul,wavelengths, io_source, power_meter, temperatures, dates,wavelengths_lambda = get_data(fits_files)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
    fig.subplots_adjust(hspace=0.4)
    ax1.plot(wavelengths,np.asarray(medhdul, float),color='red',label='mean') 
    ax1.set_xlabel('Date d\'acquistion')
    ax1.set_ylabel('Température (en K)')
    ax1.set_title('Température en fonction de la date d\'acquistion')
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
    medhdul,wavelengths, io_source, power_meter, temperatures, dates,wavelengths_lambda = get_data_path(path, specific)
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
    
    """
    Trace les graph des datas récup
    
    """
    
    
    fits_files_CH4 = get_files(path_CH4, specific)
    fits_files_without_CH4 = get_files(path_without_CH4, specific)
    
    intensity_with_CH4,wavelengths_with_CH4, io_source_with_CH4, power_meter_with_CH4,\
        temperatures_with_CH4, dates_with_CH4,wavelengths_lambda_with_CH4 \
            = get_data(fits_files_CH4) 

    intensity_without_CH4,wavelengths_without_CH4, io_source_without_CH4, power_meter_without_CH4,\
        temperatures_without_CH4, dates_without_CH4,wavelengths_lambda_without_CH4 \
            = get_data(fits_files_without_CH4) 
    
    #wavelengths_without_CH4= get_data(path_without_CH4, specific)[1]
    #intensity_without_CH4 = get_data(path_without_CH4, specific)[0]
    
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
    ax4.set_title('Transmittance calculée de la cellule à gaz e fonctionb de la longueur donde')    

    plt.show()
   




def get_i_io():    
    """
    Recupere I (intensite avec ch4) et Io (intensite sans ch4)
    """
    l_i, l_io, l_onde, medhdul = [],[],[],[]
    
    fits_files_CH4 = get_files(path_CH4, specific)
    fits_files_without_CH4 = get_files(path_without_CH4,specific)

    for file in fits_files_CH4:
        hdul = fits.open(file)
        for i in range(1,len(hdul)):
            l_i.append(hdul[i].header['INTENSITE_POWER_METER'])
            l_onde.append(hdul[i].header['LAMBDA'])
            meddata = []
            data = hdul[i].data
            for j in range(0, len(data)):
                meddata.append(np.median(hdul[i].data[j]))
            medhdul.append(np.median(meddata))

    for file in fits_files_without_CH4:
        hdul = fits.open(file)
        for i in range(1,len(hdul)):
            l_io.append(hdul[i].header['INTENSITE_POWER_METER'])

    return(l_i,l_io,l_onde,medhdul)

    
def get_index_wvl(wvl, liste):
    """
    permet de trouver l'index de la valeur de longueur d'onde dans une liste qui est la plus 
    proche de la valeur de longueur d'onde donnée
    Permet notamment de trouver l'index du pic d'absoprtion souhaite
    """
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
    
    """
    initialise une variable c avec une valeur de correction pour les valeurs manquantes (NaN) des transmittances. 
    Cette valeur est utilisée pour prendre en compte un pourcentage des valeurs précédentes 
    lorsqu'une transmittance est nulle ou négative.
    
    Calculs d'absorbance et de transmittance à partir des intensités mesurées et de référence
    Retourne les résultats 
    """
    
    
    c=0.2
    absorbance, transmittance = [],[]
    l_i,l_io, l_onde, medhdul = get_i_io()
    l_i = [float(i) for i in l_i]
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
            
            
def get_pic_absorbance(pics, l_onde,t,a,medhdul, index):
    """
    permet de trouver les pics d'absorption les plus élevés à partir des listes d'absorbances fournies. 
    Elle renvoie les valeurs maximales d'absorbance et leurs indices associés.
    """
    #l_onde,t,a,medhdul, index = get_absorbance()
    maxs, index_maxs=[],[]
    for i in range(0, pics):
        maxs.append(np.max(a))
        index_maxs.append(a.index(np.max(a)))
        a.remove(np.max(a))

    return(maxs, index_maxs)



def find_local_peaks(wavelengths, absorbance, wavelengths_pics_theoriques):
    local_peaks = []
    threshold = 0.6  # Seuil minimal d'absorbance
    for target_wavelength in wavelengths_pics_theoriques:
        # Trouver l'indice du pic local le plus proche de la longueur d'onde cible
        index = np.argmin(np.abs(np.array(wavelengths) - target_wavelength))
        
        # Calculer les dérivées secondes des absorbances
        second_derivatives = np.gradient(np.gradient(absorbance))

        # Chercher les indices des pics locaux dans les dérivées secondes
        peak_indices = np.where((second_derivatives[:-2] < 0) & (second_derivatives[2:] > 0))[0] + 1
        
        # Appliquer le seuil minimal d'absorbance
        peak_indices = [index for index in peak_indices if absorbance[index] > threshold]

        # Trouver l'indice du pic local le plus proche de l'indice initial
        nearest_peak_index = peak_indices[np.argmin(np.abs(peak_indices - index))]

        # Récupérer l'absorbance et la longueur d'onde du pic local
        nearest_peak_absorbance = absorbance[nearest_peak_index]
        nearest_peak_wavelength = wavelengths[nearest_peak_index]

        # Ajouter les résultats à la liste des pics locaux
        local_peaks.append((nearest_peak_wavelength, nearest_peak_absorbance))

    return local_peaks




def get_concentration(wavelengths_pics_theoriques,extinction_coefficients):
    """
    Calcule la concentration à partir de l'absorbance en fonction du pic max d'absorption 
    
    Experience : T = 296K (22°C)    P = 1 atm   L = 10cm
    Loi de Beer Lambert : C = A / (epsilon x l)
    C concentration, A absorbance, Epsilon coefficient d'extinction molaire, l largeur cuve
    c = A/sv*l
    """
    concentration = []
    pics, l = 4, 5
    
    wavelengths,transmittance,absorbance,cam, index = get_absorbance()
    maxs, index_maxs = get_pic_absorbance(pics,wavelengths,transmittance,absorbance,cam, index)
    print('index : ', index, 'l_onde : ', wavelengths[index], 'absorbance :' ,absorbance[index])
    print(np.max(absorbance))
    
    local_peaks = find_local_peaks(wavelengths, absorbance, wavelengths_pics_theoriques)
    i=0
    for peak in local_peaks:
        
        c =  peak[1] /  ( extinction_coefficients[i] * l)
        concentration.append(c)
        print("Pic local d'absorption le plus proche :")
        print("Longueur d'onde : ", peak[0])
        print("Absorbance : ", peak[1])
        print("Concentration : ", c , ' molecules par cm3')
        i+=1

    
    #calcul de la concentration via une courbe d'etallonage
    c = absorbance[index_maxs[3]] / (sv2 * l)
    print('concentration en CH4 ' , c, ' molecules par cm3')
 
    
wavelengths_pics_theoriques = [6046.93, 6057.03, 6066.98, 6077]
extinction_coefficients = [2.2*10**-20, 4.6*10**-20, 7.5*10**-20, 1.8*10**-20, 3.9*10**-20]  # Coefficients d'extinction molaire correspondants
get_concentration(wavelengths_pics_theoriques,extinction_coefficients)




#pics d'absorption type du CH4 sur bande spectrale en cm-1
global v1,v2,v3,v4,v5
v1,v2,v3,v4,v5 = 6046.93, 6057.03, 6066.98, 6077, 6086.79



#pics d'absorption type du CH4 sur bande spectrale en cm-1
global wl1, wl2, wl3, wl4, wl5
wl1, wl2, wl3, wl4, wl5 = 1/v1*10000000, 1/v2*10000000, 1/v3*10000000, 1/v4*10000000, 1/v5*10000000


#coeff d'extinction molaire des pics d'absorption type du CH4 sur bande spectrale en cm-1
global sv1, sv2, sv3, sv4, sv5
sv1, sv2, sv3, sv4, sv5 = 2.2*10**-20, 4.6*10**-20, 7.5*10**-20, 1.8*10**-20, 3.9*10**-20
#print('\n', wl1,'\n', wl2,'\n', wl3,'\n', wl4,'\n', wl5)


path = r'C:\Users\raynaudy\Documents\Manip\cellule_gaz_ch4_pré_calib\calib_cam_nue\avec_cellule\20230530'
path_CH4 = r'C:\Users\raynaudy\Documents\Manip\cellule_gaz_ch4_pré_calib\calib_cam_nue\ref_sans_cellule\20230531'
path_without_CH4 = r'C:\Users\raynaudy\Documents\Manip\cellule_gaz_ch4_pré_calib\calib_cam_nue\avec_cellule\20230530'
specific = '337pas'
min_io = 1500

#graph_temperature_both_gas()
#get_median_pixels(path, specific)
#get_files_absorb(path_CH4,path_without_CH4,specific)
#get_min(1500)
#get_abs()
get_concentration()