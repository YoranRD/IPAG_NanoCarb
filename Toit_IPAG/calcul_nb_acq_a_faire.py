# -*- coding: utf-8 -*-
"""
Created on Tue May  2 16:54:06 2023

@author: raynaudy
"""
mesures_par_heure = float(input("Entrez le nombre de mesures par heure : "))
temps_total_acquisition = float(input("Entrez le temps total d'acquisition (en heures) : "))

# Calcul du nombre total de mesures
nombre_total_mesures = int(mesures_par_heure * temps_total_acquisition)

# Calcul du temps d'attente entre chaque mesure
temps_attente_entre_mesures_sec = 3600 / mesures_par_heure
temps_attente_entre_mesures_ms = temps_attente_entre_mesures_sec * 1e3

# Affichage des résultats
print("Nombre total de mesures : ", nombre_total_mesures)
print("Temps d'attente entre chaque mesure (en millisecondes) : ", temps_attente_entre_mesures_ms)

