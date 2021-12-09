# import os
# from glob import glob
# import json
# import csv
import matplotlib.pyplot as plt
from itertools import groupby, chain
from datetime import datetime
import math
import os
import json

samsung_base_dir = os.path.join('.','samsunghealth_marco.bresson_202103220935','jsons')
# categories = ["activity.day_summary","sleep_data","step_daily_trend","tracker.heart_rate","tracker.pedometer_day_summary"]


def recherche_json(categorie,suffixe): #recherche tous les fichiers json dans un répertoire
    print("récupération des données")
    json_chemins = glob(os.path.join(samsung_base_dir, '*'+categorie+'*', '*',  '*'+suffixe+'.json'))
    print(len(json_chemins), 'fichiés trouvés')
    json_donnees = [json.load(open(fichier, 'r')) for fichier in json_chemins]
    return list(chain(*json_donnees)) if isinstance(json_donnees[0], list) else json_donnees

def lisser_tableau(tableau, lissage, arrondi=0, boucle=False): #lisse un tableau et arrondie les valeurs #boucle=True si la fin du tableau est liée au début (freq car sur une journee)
    tableau_lisse = []
    multiplicateur=1
    if boucle:
        multiplicateur=0
    for i in range(lissage*multiplicateur,len(tableau)): #commence à 0 si boucle=True
        valeur = 0
        for ii in range(lissage):
            valeur += tableau[i-ii]
        tableau_lisse.append(round(valeur/lissage,arrondi))
    return tableau_lisse

def enregistrer_csv(donnees,labels=[]):#[xx,yy,zz,aa,..],labels
    f = open("donnees.csv","w+")
    ligne = []
    for i in range(len(labels)): #pour chaque categorie
        ligne.append(labels[i])
    f.write(";".join(ligne)+"\n")
    for i in range(len(donnees[0])): #nombre de valeur
        ligne = []
        for ii in range(len(donnees)): #pour chaque categorie
            try:
                ligne.append(str(donnees[ii][i]))
            except:
                ligne.append("")
        f.write(";".join(ligne)+"\n")
    f.close()

def n_derniers_max(tableau,n,clé=""):
    if type(tableau)==list:
        table = set(zip(*sorted(zip(*tableau),reverse=True)))
        tables = [list(x) for x in table]
        tableau=[]
        for x in range(len(tables[0])):
            ligne=[]
            for y in range(len(tables)):
                ligne.append(tables[y][x])
            tableau.append(ligne)
        return tableau[:n]
    else:#si c est un dictionnaire
        tableau = {k: v for k, v in sorted(tableau.items(), key=lambda item: item[1][clé], reverse=True)}
        maxima=[]
        compteur=0
        for i in range(tableau):
            compteur+=1
            maxima.append(tableau[i])
            if n<=compteur:
                break
            
        return maxima

def n_derniers_min(tableau,n,clé=""):
    if type(tableau)==list:
        table = set(zip(*sorted(zip(*tableau))))
        tables = [list(x) for x in table]
        tableau=[]
        for x in range(len(tables[0])):
            ligne=[]
            for y in range(len(tables)):
                ligne.append(tables[y][x])
            tableau.append(ligne)
        return tableau[:n]
    else:#si c est un dictionnaire
        tableau = {k: v for k, v in sorted(tableau.items(), key=lambda item: item[1][clé])}
        minima=[]
        compteur=0
        for i in range(tableau):
            compteur+=1
            minima.append(tableau[i])
            if n<=compteur:
                break
            
        return minima

def compte_device_uuid(fichier_csv):
    devices_uuid = {}
    with open(fichier_csv, mode='r') as donnees:
        reader = csv.reader(donnees)
        next(reader,None)
        next(reader,None)
        for rows in reader:
            if rows[7] in devices_uuid: #compte le nombre de donnees associees a une uuid
                devices_uuid[rows[7]]+=1
            else:
                devices_uuid[rows[7]]=0






#===================== SOMMEIL

donnees_sommeil = {}
def lecture_json_sommeil():
    global donnees_sommeil
    with open('donnees_sommeil.json') as fichier:
        donnees_sommeil = json.load(fichier)
lecture_json_sommeil()

def traitement_sommeil():
    donnees_efficacite=[0]*len(donnees_sommeil)
    donnees_duree=[0]*len(donnees_sommeil)
    fin_timestamp=[0]*len(donnees_sommeil)
    for compteur,i in enumerate(donnees_sommeil):
        donnees_efficacite[compteur]=donnees_sommeil[i]["eff"]
        donnees_duree[compteur]=int(donnees_sommeil[i]["fin"])-int(donnees_sommeil[i]["deb"])
        fin_timestamp[compteur]=donnees_sommeil[i]["fin"]
    efficacite_lissee = lisser_tableau(donnees_efficacite,10,2)
    duree_lissee = lisser_tableau(donnees_duree,10,2)

    enregistrer_csv([donnees_efficacite,donnees_duree,fin_timestamp,efficacite_lissee,duree_lissee])
    # plot :
    # dates_xtick = [datetime.fromtimestamp(fin_timestamp[int((len(donnees)-1)/30*x)]).strftime("%Y-%m-%d") for x in range(31)]
    # plt.xticks([len(donnees)/30*x for x in range(31)],[dates_xtick[x] for x in range(31)])
    # plt.xticks(rotation=90)
    # plt.ylim(ymin=0)
    # if categorie == "efficacite":
    #     plt.ylim(ymax=100)
    # plt.show()
traitement_sommeil()
def sommeil_par_jour(): 
    [donnees_efficacite,donnees_duree,fin_timestamp] = lecture_csv_sommeil()
    
    resultat = [[0 for x in range(7)] for y in range(2)]
    compteur = [0]*7
    for i in range(len(fin_timestamp)): # on cumule pour chaque jour de la semaine
        jour = int(datetime.fromtimestamp(fin_timestamp[i]).strftime("%w"))
        resultat[0][jour]+=donnees_efficacite[i]
        resultat[1][jour]+=donnees_duree[i]
        compteur[jour]+=1
    for i in range(7): # on pondère les données
        resultat[0][i]=round(resultat[0][i]/compteur[i],2)
        resultat[1][i]=round(resultat[1][i]/compteur[i],2)
    
    enregistrer_csv(resultat)
    # plt.plot(donnees)
    # plt.xticks([x for x in range(7)],["dimanche","lundi","mardi","mercredi","jeudi","vendredi","samedi"])
    # plt.ylim(ymin=60)
    # if categorie == "efficacite":
    #     plt.ylim(ymax=100)
    # plt.show()


#PAS ---------------------------------------
donnees_pas = {}
donnees_pas_detail = {}
def lecture_json_pas(detail=False):
    global donnees_pas,donnees_pas_detail
    if detail:
        with open('donnees_pas_detail.json') as fichier:
            donnees_pas_detail = json.load(fichier)
    else:
        with open('donnees_pas.json') as fichier:
            donnees_pas = json.load(fichier)

def pas_freq_jour_semaine(frequence="dizaine_minute",B_separer_jour_semaine=True,type_categorie="nombre",enregistrer=True):
    pas_detail = lecture_json_pas(True)
    tailles = {"heure":24,"dizaine_minute":144}
    if B_separer_jour_semaine:
        coef = 7 #7 jours dans 1 semaine
    else:
        coef = 1 #moyenne sur la semaine
    resultat = [[0 for i in range(tailles[frequence])] for ii in range(coef)]
    compteur = [0]*coef
    for date in pas_detail: #pour chaque date ...
        if B_separer_jour_semaine:
            jour = int(datetime.fromtimestamp(int(date)).strftime("%w"))
        else:
            jour = 0
        for ii in range(144):
            resultat[jour][ii//int((144/tailles[frequence]))]+=pas_detail[date][type_categorie][ii]
        compteur[jour]+=1
    for i in range(coef):
        for ii in range(len(resultat[0])):
            resultat[i][ii]/=compteur[i]
    if enregistrer:
        enregistrer_csv(resultat)
    else:
        for i in range(len(resultat)):
            plt.plot(resultat[i])
        plt.show()


def pas_moy_semaine(type_categorie="nbr_pas",debut_semaine=1,enregistrer=True):
    pas = lecture_json_pas(False)
    resultat = []
    somme=0
    compteur=0
    indice = 0
    for date in pas: #pour chaque date ...
        if int(datetime.fromtimestamp(date).strftime("%w"))==debut_semaine:
            if compteur==7:
                indice+=1
                resultat.append(somme)
            compteur=0
        somme+=pas[date][type_categorie]
        compteur+=1

    resultat = lisser_tableau(resultat,3,0)
    if enregistrer:
        enregistrer_csv([resultat])
    else:
        plt.plot(resultat)
        plt.show()


def pas_moy_jour(type_categorie="nbr_pas",enregistrer=True):
    pas = lecture_json_pas(False)
    resultat = []
    for date in pas: #pour chaque date ...
        resultat.append(pas[date][type_categorie])
        
    resultat = lisser_tableau(resultat,15,0)
    if enregistrer:
        enregistrer_csv([resultat])
    else:
        plt.plot(resultat)
        plt.show()





#CARDIAQUE ---------------------------------------

card_max_frequences = []
card_min_frequences = []
card_frequences = []
card_date_debut = []
card_date_fin = []
def traitement_coeur():
    print("analyse de la fréquence cardiaque")
    donnees = recherche_json("tracker.heart_rate","binning_data")

    for donnee_session in donnees:
        if math.floor(donnee_session["heart_rate"])>20:
            card_max_frequences.append(donnee_session["heart_rate_max"])
            card_min_frequences.append(donnee_session["heart_rate_min"])
            card_frequences.append(donnee_session["heart_rate"])
            card_date_debut.append(round(donnee_session["start_time"]/1000))
            card_date_fin.append(round(donnee_session["end_time"]/1000))


def cardiaque_graph_moyenne_quotidien():
    freq_triees = [x for _,x in sorted(zip(card_date_debut,card_frequences))]
    card_date_debut.sort()
    freq_lissees = []
    dates_timestamp = []
    dates = ["0000-00-00"]
    compteur = 0
    freq_cumul = 0
    for i in range(len(card_date_debut)):
        if(datetime.fromtimestamp(card_date_debut[i]).strftime("%Y")=="2020"):
            if(datetime.fromtimestamp(card_date_debut[i]).strftime("%Y-%m-%d")==dates[-1]):
                freq_cumul += freq_triees[i]
                compteur += 1
            else :
                print(datetime.fromtimestamp(card_date_debut[i]).strftime("%Y-%m-%d"))
                if(compteur!=0):
                    freq_lissees.append(round(freq_cumul/compteur,2))
                else :
                    freq_lissees.append(0)
                dates_timestamp.append(card_date_debut[i])
                dates.append(datetime.fromtimestamp(card_date_debut[i]).strftime("%Y-%m-%d"))
                compteur = 0
                freq_cumul = 0
    indice_max = len(freq_lissees)
    i=0
    while i < indice_max:
        if freq_lissees[i]<20:
            freq_lissees.pop(i)
            dates_timestamp.pop(i)
            i-=1
            indice_max-=1
        i+=1
    plt.plot(dates_timestamp,freq_lissees, 'bo')
    plt.show()

def cardiaque_par_frequence(frequence): #jour, heure, minute
    tailles = {"jour":7,"heure":24,"minute":1440}
    freq = [0]*tailles[frequence]
    freq_cumul = [0]*tailles[frequence]
    compteur = [0]*tailles[frequence]
    for i in range(len(card_date_debut)):
        if frequence=="jour":
            decoupage = int(datetime.fromtimestamp(card_date_debut[i]).strftime("%w"))
        elif frequence=="heure":
            decoupage = int(datetime.fromtimestamp(card_date_debut[i]).strftime("%H"))
        elif frequence=="minute":
            heure = int(datetime.fromtimestamp(card_date_debut[i]).strftime("%H"))
            decoupage = heure*60 + int(datetime.fromtimestamp(card_date_debut[i]).strftime("%M"))
        freq_cumul[decoupage]+=card_frequences[i]
        compteur[decoupage]+=1
    for i in range(tailles[frequence]):
        if compteur[i]==0:
            compteur[i]=1
        freq[i]=round(freq_cumul[i]/compteur[i],2)
    
    freq = lisser_tableau(freq,5,2,True)
    enregistrer_csv([freq])
    
    return freq
    plt.bar(freq)
    plt.xticks([1440/24*x for x in range(25)],[str(x)+"h" for x in range(25)])
    plt.ylim(ymin=0)