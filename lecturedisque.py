import os

def lister_fichiers(racine):
    # Lister tous les fichiers dans un répertoire donné
    for dossier, sous_dossiers, fichiers in os.walk(racine):
        for fichier in fichiers:
            print(os.path.join(dossier, fichier))

# Exemple d'utilisation : lister les fichiers à partir de la racine d'un disque ou d'un répertoire
racine = "C:/"  # Remplace par le chemin de ton disque ou répertoire sur ton système
lister_fichiers(racine)