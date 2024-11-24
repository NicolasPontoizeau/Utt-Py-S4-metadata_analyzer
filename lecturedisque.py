import os
import mimetypes
import magic # type: ignore

def lister_fichiers(racine):
    # Lister tous les fichiers dans un répertoire donné
    for dossier, sous_dossiers, fichiers in os.walk(racine):
        for fichier in fichiers:
            f=os.path.join(dossier, fichier)
            # print(f)

            # MIME type (based on extension)
            mime_type, _ = mimetypes.guess_type(f)

            if mime_type == "application/pdf":
                print("According MIME Type extension here is a pdf:" + f)
                # MIME type (based on content)
                mime = magic.Magic(mime=True)
                content_type = mime.from_file(f)
                print(f"MIME Type (Content-Based): {content_type}")
                
            
# Exemple d'utilisation : lister les fichiers à partir de la racine d'un disque ou d'un répertoire
# racine = "C:/"  # Remplace par le chemin de ton disque ou répertoire sur ton système
lister_fichiers(os.getcwd())