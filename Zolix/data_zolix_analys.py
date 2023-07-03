# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 11:46:26 2023

@author: raynaudy
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from scipy.optimize import curve_fit
import os
import time


#Fonction principale
#On ouvre le fichier, récupère les deux colones de data en zappant le header on retourne les listes wvl et io
#on crée une lorentzienne qu'on applique sur le pic d'intensite du fichier ce qui nous permet de calculer FWHM
def process_file(filename):
    wavelength = []
    intensity = []
    
    with open(filename, "r") as file: 
        for line in file:
            #permet de zapper le header
            if len(line.strip().split("\t")) < 2:
                continue # Passer à la ligne suivante si la ligne ne contient pas suffisamment de colonnes
            column1, column2 = line.strip().split("\t") # séparer les colonnes en utilisant une tabulation comme séparateur
            column1 = column1.replace(",", ".")
            column2 = column2.replace(",", ".")
            #print(column1, column2)
            wavelength.append(float(column1)) # ajouter la première colonne (longueur d'onde) à la liste
            intensity.append(float(column2)) # ajouter la deuxième colonne (intensité) à la liste


    # Convertir les listes en tableaux numpy sinon erreur plus loin dans manipulation de data
    wavelength = np.array(wavelength)
    intensity = np.array(intensity)
    


    # Trouver la raie dabsorption la plus haute
    # Chercher les indices des sommets de toutes les raies dabsorption
    pics, _ = scipy.signal.find_peaks(intensity)
    max_pic_index = np.argmax(intensity[pics])
    max_pic = pics[max_pic_index]
    
    # Appliquer un filtre médian aux données d'intensité
    filtered_intensity = scipy.signal.medfilt(intensity, kernel_size=3)
    
    # Masquer les valeurs filtrées autour des pics d'acquisition
    mask = np.zeros(len(intensity), dtype=bool)
    for index in [max_pic_index]:
        mask[index-5:index+5] = True
    filtered_intensity[mask] = intensity[mask]
    """
    plt.plot(wavelength, filtered_intensity)
    plt.xlabel("Longueur d'onde (nm)")
    plt.ylabel("Intensité")
    plt.title("Graphique de longueur d'onde par rapport à l'intensité")
    plt.show()
    """

    #trouver les indices des points autour du pic d'intensité maximum
    partie_gauche = np.argmin(np.abs(filtered_intensity[max_pic] / 2 - filtered_intensity[:max_pic]))
    partie_droite = np.argmin(np.abs(filtered_intensity[max_pic] / 2 - filtered_intensity[max_pic:]))+ max_pic


    # Estimer la largeur à mi-hauteur
    hm = filtered_intensity[max_pic] / 2
    idx_gauche = np.abs(filtered_intensity[:max_pic] - hm).argmin()
    idx_droite = np.abs(filtered_intensity[max_pic:] - hm).argmin() + max_pic
    fwhm_est = wavelength[idx_droite] - wavelength[idx_gauche]



    def lorentzian(x, a, b, c):
        return (a**2 * (c / 2)**2) / ((x - b)**2 + (c / 2)**2)
        #return a * (c**2 / 4) / ((x - b)**2 + (c / 2)**2)
    #avec a amplitude de la raie, b poisition de la raie en abscisse, c largeur a mi hauteur
    
    

    # Extraire les données pour la lorentzienne
    #x_data sont le wvl autours du pic; y_data les intensité
    x_data = wavelength
    y_data = filtered_intensity
    
       
    # Initialiser les paramètres de la lorentzienne
    a_estime = max(y_data)
    b_estime = x_data[np.argmax(y_data)]
    c_estime = fwhm_est / 2

    # Ajuster la lorentzienne aux données
    #popt est un tableau avec les valeurs optimales des param de la lorentzienne (a,b et c)
    #pcov est la matrice de covariance des parametres de la lorentzienne
    popt, pcov = curve_fit(lorentzian, x_data, y_data, p0=[a_estime, b_estime, c_estime])

    # Calculer la FWHM du pic d'intensité maximum
    FWHM = 2 * popt[2]
    
    if 'S950' in filename :
        
        # Dessiner la lorentzienne ajustée pour visualiser le fit
        #plot data en points
        plt.plot(x_data, y_data, "bo", label = 'Data')
        #plot fit courbe rouge
        plt.plot(x_data, lorentzian(x_data, *popt), "r-", label="Fit")
        plt.xlabel("Longueur d'onde")
        plt.ylabel("Intensite")
        plt.legend()
        plt.show()

    return FWHM

def get_slits(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath=os.path.join(folder_path,filename)
            FWHM = process_file(filepath)
            FWHM_list.append(FWHM)
            
            E_nb, S_nb = filename.split('_')[0][1:], filename.split('_')[1][1:-4]
            entrance_slit.append(float(E_nb)/100)
            exit_slit.append(float(S_nb)/100)     
    return (FWHM_list, entrance_slit, exit_slit)


#crée dictionnaire qui va stocker les valeurs de exit_slit et FHWM pour chaque valeur de entrance_slit
def get_entrance_dict(FWHM_list):
    entrance_dict = {}
    for i in range(len(FWHM_list)):
        #on verif que la valeur actuelle de entrance_slit est dans le dictionnaire
        #si elle n'y est pas on crée une entrée
        if entrance_slit[i] not in entrance_dict:
            entrance_dict[entrance_slit[i]] = [[],[]] # Créer une entrée vide pour chaque taille de fente d'entrée
        #on ajoute la valeur de exit_slit et FWHM pour la même valeur de entrance_slit dans le dictionnaire entrance_dict
        entrance_dict[entrance_slit[i]][0].append(exit_slit[i])
        entrance_dict[entrance_slit[i]][1].append(FWHM_list[i])
    return(entrance_dict)
    

def plot_FWHM(entrance_dict):
    # Tracer chaque entrée séparément avec une couleur différente
    for key in entrance_dict:
        plt.plot(entrance_dict[key][0], entrance_dict[key][1], label='Entrance Slit (mm)' + str(key), marker='x', linestyle='-')
    
    # Paramètres de la figure
    plt.xlabel('Exit Slit (mm)')
    plt.ylabel('FWHM (nm)')
    plt.title('FWHM en fonction de Exit Slit par taille de fente d\'entrée')
    # Modifier la position de la légende
    plt.legend(bbox_to_anchor=(1.05, 0.9), loc='upper left', borderaxespad=0.5)
    # Ajuster la taille de la figure
    plt.figure(figsize=(8,8))
    plt.show()
    time.sleep(1)
    plt.savefig(r'C:\Users\raynaudy\Documents\Manip\Zolix\wvl633\FWHM_slit.jpg')


folder_path = r'C:\Users\raynaudy\Documents\Manip\Zolix\wvl633_step025'
FWHM_list, entrance_slit, exit_slit = [], [], []        
FWHM_list, entrance_slit, exit_slit = get_slits(folder_path)  
      
FWHM_list = [i for i in FWHM_list if i <= 100]
entrance_slit = [entrance_slit[i] for i in range(len(FWHM_list)) if FWHM_list[i] <= 30]
exit_slit = [exit_slit[i] for i in range(len(FWHM_list)) if FWHM_list[i] <= 30]

entrance_dict = get_entrance_dict(FWHM_list)



    
plot_FWHM(entrance_dict)


def mean_fwhm_variation_by_entrance_slit(entrance_dict):

    result = {}
    for key in entrance_dict.keys():
        fwhm_values = [x['fwhm'] for x in entrance_dict[key]]
        mean_variation = np.mean(np.diff(fwhm_values))
        result[key] = mean_variation
    return result


def mean_fwhm_variation_by_exit_slit(exit_dict):
    """
    Calculate the average variation of FWHM for each exit slit value.
    
    Parameters:
    -----------
    exit_dict: dict
        A dictionary containing data for different exit slit values.
    
    Returns:
    --------
    dict
        A dictionary containing the average variation of FWHM for each exit slit value.
    """
    result = {}
    for key in exit_dict.keys():
        fwhm_values = [x['fwhm'] for x in exit_dict[key]]
        mean_variation = np.mean(np.diff(fwhm_values))
        result[key] = mean_variation
    return result


def fwhm_dispersion_by_entrance_and_exit_slit(entrance_dict, exit_dict):
    """
    Calculate the dispersion of FWHM for each combination of entrance and exit slit values.
    
    Parameters:
    -----------
    entrance_dict: dict
        A dictionary containing data for different entrance slit values.
    exit_dict: dict
        A dictionary containing data for different exit slit values.
    
    Returns:
    --------
    dict
        A dictionary containing the dispersion of FWHM for each combination of entrance and exit slit values.
    """
    result = {}
    for e_key in exit_dict.keys():
        for en_key in entrance_dict.keys():
            fwhm_values = [x['fwhm'] for x in exit_dict[e_key] if x['entrance_slit'] == en_key]
            fwhm_dispersion = np.std(fwhm_values)
            key = f"{e_key}-{en_key}"
            result[key] = fwhm_dispersion
    return result




"""
key = entrance_slit  + exit_slit
dict.setdefault(key, []).append(FWHM)
for k, v in dict.items():
     exit_slit = k.split('-')[1]
     mean_variation = np.mean(np.diff(v))
     print(f"Mean variation of FWHM for exit slit {exit_slit}: {mean_variation:.3f}")
         
    
    
       
    for key, value in entrance_dict.items():
        wavelengths = np.array(value["wavelength"])
        growth = np.array(value["growth"])

        # Calculer le pas
        step_size = np.diff(wavelength).mean()

        # Calculer la moyenne de croissance à chaque pas
        mean_growth = []
        for i in range(len(wavelength)-1):
            mean_growth.append((growth[i+1] - growth[i])/step_size)
        mean_growth = np.array(mean_growth)

        # Calculer l'écart-type de la croissance à chaque pas
        std_growth = []
        for i in range(len(wavelength)-1):
            std_growth.append(np.std(growth[i:i+2]))
        std_growth = np.array(std_growth)

        print("Statistics for key:", key)
        print("Step size:", step_size)
        print("Mean growth at each step:", mean_growth)
        print("Standard deviation of growth at each step:", std_growth)

calculate_statistics(entrance_dict)
"""
"""
plt.plot( entrance_slit, FWHM_list, "bo", label = 'Data')
#plot fit courbe rouge
#plt.plot(exit_slit,FWHM_list,  "r-", label="Fit")
plt.xlabel("Slit")
plt.ylabel("FWHM")
plt.legend()
plt.show()

"""