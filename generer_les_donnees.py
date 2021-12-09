import os
from glob import glob
import json
import csv

samsung_base_dir = os.path.join('.','samsunghealth_marco.bresson_202103220935','jsons')

def exporter_json(data,nom_fichier):
    with open(nom_fichier, 'w') as fichier:
        json.dump(data, fichier)

def ecriture_json_sommeil():
    sommeil = {}
    with open("./data/com.samsung.shealth.sleep_data.202006152138.csv", mode='r') as donnees_sommeil:
        reader = csv.reader(donnees_sommeil)
        next(reader,None)
        next(reader,None)
        for rows in reader:
            sleep_uuid = rows[7]
            sommeil[sleep_uuid]={"fichier":rows[6],"eff":"","deb":"","fin":"","etat":{}}

    with open("./data/com.samsung.shealth.sleep.202006152138.csv", mode='r') as donnees_sommeil:
        reader = csv.reader(donnees_sommeil)
        next(reader,None)
        next(reader,None)
        compteur=0
        taille_donnees_sommeil=len(sommeil)
        for rows in reader:
            sleep_uuid = rows[12]
            if rows[4]=="1":
                sommeil[sleep_uuid]["eff"]=round(float(rows[0]),2)
                sommeil[sleep_uuid]["deb"]=str(int(int(rows[7])/1000)) #str pour le tri des données
                sommeil[sleep_uuid]["fin"]=str(int(int(rows[14])/1000))
                fichier = glob(os.path.join(samsung_base_dir, '*sleep_data*', '*',  sommeil[sleep_uuid]["fichier"]))
                donnees = json.load(open(fichier[0], 'r'))
                profondeur={}
                for i in donnees:
                    profondeur[int(int(i["start_time"])/1000)]=round(i["status"],2)
                sommeil[sleep_uuid]["etat"]=profondeur
                
                compteur+=1
                if int(compteur/taille_donnees_sommeil*100)!=int((compteur-1)/taille_donnees_sommeil*100):
                    print(str(int(compteur/taille_donnees_sommeil*100))+"%")
                    

    sommeil = {k: v for k, v in sorted(sommeil.items(), key=lambda item: item[1]["deb"])}
    indice_a_pop = []
    for i in sommeil:
        if sommeil[i]["eff"]=="" or sommeil[i]["eff"]=="0.0":
            indice_a_pop.append(i)
    for i in indice_a_pop:
        sommeil.pop(i)

    exporter_json(sommeil,"donnees_sommeil.json")
    #================ differentiation par dates
    # fin_timestamp = []
    # [fin_timestamp.append(int(x[1]["fin"])) for x in sommeil.items()]
    # donnees_efficacite = []
    # donnees_duree = []
    
    # [donnees_efficacite.append(float(x[1]["efficacite"])) for x in sommeil.items()]
    # [donnees_duree.append(float(x[1]["fin"])-float(x[1]["debut"])) for x in sommeil.items()]
    # indice = 0
    # date_precedente="0000-00-00"
    # compteur_moyenne = 1
    # for i in range(len(donnees_duree)):
    #     if(datetime.fromtimestamp(fin_timestamp[i]).strftime("%Y-%m-%d")==date_precedente): #plusieurs sommeil le même jour => on additionne toutes les durées
    #         donnees_efficacite[indice]+=donnees_efficacite[i]
    #         donnees_duree[indice]+=donnees_duree[i]
    #         fin_timestamp[indice]=fin_timestamp[i]
    #         compteur_moyenne += 1
    #     else: #on créer un nouvel indice pour le nouveau sommeil
    #         donnees_efficacite[indice]/=compteur_moyenne #on moyenne l'efficacite
    #         date_precedente=datetime.fromtimestamp(fin_timestamp[i]).strftime("%Y-%m-%d")
    #         compteur_moyenne = 1
    #         indice+=1
    # donnees_efficacite=donnees_efficacite[:indice]
    # donnees_duree=donnees_duree[:indice]
    # fin_timestamp=fin_timestamp[:indice]
    
    # #on index les données sur le timestamp
    # donnees_sommeil_finales = {}
    # for i in range(len(donnees_efficacite)):
    #     donnees_sommeil_finales[fin_timestamp] = {"eff":donnees_efficacite[i],"dur":donnees_duree[i]}

    
def ecriture_json_pas():
    pas = {}
    with open("./data/com.samsung.shealth.tracker.pedometer_day_summary.202006152138.csv", mode='r') as donnees_pas:
        reader = csv.reader(donnees_pas)
        next(reader,None)
        next(reader,None)
        for rows in reader:
            date=int(int(rows[5])/1000)
            creer_remplace=True #creer ou remplace les donnees à l indice date

            if date in pas:
                creer_remplace=False
                if int(rows[3])>pas[date]["nbr_pas"]: #prend les donnees qui correspondent au maximum de pas
                    creer_remplace=True

            if creer_remplace:
                pas[date]={}
                pas[date]["nbr_pas"]=int(rows[3])
                pas[date]["distance"]=float(rows[1])
                pas[date]["temps_actif"]=int(int(rows[8])/1000)
                pas[date]["pas_marches"]=int(rows[12])
                pas[date]["calorie"]=float(rows[15])
                pas[date]["pas_courrus"]=int(rows[16])
                pas[date]["pas_bon_rythme"]=int(rows[18])
                pas[date]["vitesse"]=float(rows[6])
                pas[date]["fichier"]=rows[13]
    
    pas_detail = {}
    categorie = "tracker.pedometer_day_summary"
    compteur=0
    taille_donnees_pas=len(pas)
    for date in pas:
        fichier = glob(os.path.join(samsung_base_dir, '*'+categorie+'*', '*',  pas[date]["fichier"]))
        donnees = json.load(open(fichier[0], 'r'))
        pas_calorie = []
        pas_nombre = []
        pas_distance = []
        pas_vitesse = []
        for i in donnees:
            pas_calorie.append(round(i["mCalorie"],2))
            pas_nombre.append(round(i["mStepCount"],2))
            pas_distance.append(round(i["mDistance"],2))
            pas_vitesse.append(round(i["mSpeed"],2))
        pas_detail[date]={}
        pas_detail[date]["calorie"] = pas_calorie
        pas_detail[date]["nombre"] = pas_nombre
        pas_detail[date]["distance"] = pas_distance
        pas_detail[date]["vitesse"] = pas_vitesse

        compteur+=1
        if int(compteur/taille_donnees_pas*100)!=int((compteur-1)/taille_donnees_pas*100):
            print(str(int(compteur/taille_donnees_pas*100))+"%")
            
    pas = dict(sorted(pas.items()))
    pas_detail = dict(sorted(pas_detail.items()))

    with open('donnees_pas.json', 'w') as fichier:
        json.dump(pas, fichier)
    with open('donnees_pas_detail.json', 'w') as fichier:
        json.dump(pas_detail, fichier)

ecriture_json_sommeil()