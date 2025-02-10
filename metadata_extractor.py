import os
import base64
import mutagen
import magic
import mimetypes
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
from PyPDF2 import PdfFileReader
from docx import Document
import docx
import openpyxl
import json
import ffmpeg
import pikepdf
import tkinter as tk
from tkinter import filedialog, messagebox, Text, ttk,scrolledtext
from datetime import datetime
from mutagen import File
from mutagen.easyid3 import EasyID3
from PyPDF2 import PdfReader
from PIL.ExifTags import TAGS, GPSTAGS
from PIL.TiffImagePlugin import IFDRational
from pptx import Presentation
import warnings
# import win32com.client
#import olefile
from openpyxl import load_workbook
from datetime import datetime
import hashlib
import csv
from collections import Counter
import logging
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt



# NPO
def convert_json_to_csv(path_to_json):
    # input_file_path = "/home/nico/Dropbox/python/repo_git/Utt-Py-S4-metadata_analyzer/metadata_results_20250126_191931.json"
    input_file_path = path_to_json
    output_file_path = input_file_path.replace(".json", ".csv")

    try:
        with open(input_file_path, "r") as json_file:
            data = json.load(json_file)
            
        # NPO le format json n'est pas un json correct car il ne respecte pas le fait qu'un json est une liste de dictionnaire
        # # Vérifier que le JSON est une liste de dictionnaires
        # if not isinstance(data, list):
        #     raise ValueError("Le fichier JSON doit contenir une liste de dictionnaires.")


        # Flatten the data if necessary and write to a CSV file
        with open(output_file_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            # Write headers
            # writer.writerow(["Key", "Value"])
            # Write rows
            for key, value in data.items():
                writer.writerow([key, value])
    
        # Afficher un message de succès
        messagebox.showinfo("Succès", f"Fichier CSV enregistré avec succès :\n{output_file_path}")
        print(f"fichier {path_to_json} converti en {output_file_path}")
        
    except json.JSONDecodeError:
        messagebox.showerror("Erreur", "Le fichier JSON sélectionné est invalide.")
    except ValueError as ve:
        messagebox.showerror("Erreur", str(ve))
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur inattendue est survenue : {e}")



# Fonction pour convertir les métadonnées
# Convertit les données complexes en types sérialisables JSON.

def convert_to_serializable(data):
   
    if isinstance(data, dict):  # Si c'est un dictionnaire
        return {key: convert_to_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):  # Si c'est une liste
        return [convert_to_serializable(item) for item in data]
    elif isinstance(data, tuple):  # Si c'est un tuple
        return tuple(convert_to_serializable(item) for item in data)
    elif isinstance(data, IFDRational):  # Si c'est un objet IFDRational
        return float(data)  # Convertir en float
    elif "IndirectObject" in str(type(data)):  # Si c'est un IndirectObject
        return str(data)  # Convertir en chaîne
    elif isinstance(data, bytes):  # Si c'est un objet bytes
        # Convertir les bytes en chaîne encodée Base64
        return base64.b64encode(data).decode("utf-8")
    elif isinstance(data, datetime):  # Si c'est un objet datetime
        return data.isoformat()  # Convertir datetime en chaîne ISO 8601
    elif hasattr(data, "text"):  # Si l'objet a une propriété .text
        return data.text
    else:  # Tout autre type de données
        return data
      
    
    
    

    #Calcule le hash d'un fichier en utilisant l'algorithme spécifié.
    #param file_path: Chemin complet du fichier à hacher.
    #param algorithm: Algorithme de hachage à utiliser (par exemple, 'md5', 'sha1', 'sha256').
    #return: Le hash du fichier sous forme de chaîne hexadécimale.
      
def calculate_file_hash(file_path, algorithm="sha256"):
    
    try:
        # Initialiser l'objet de hachage pour l'algorithme spécifié
        hash_func = hashlib.new(algorithm)
        
        # Lire le fichier par blocs pour éviter de surcharger la mémoire
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        # Retourner le hash sous forme hexadécimale
        return hash_func.hexdigest()
    except FileNotFoundError:
        return f"Erreur : Le fichier '{file_path}' n'existe pas."
    except ValueError:
        return f"Erreur : L'algorithme '{algorithm}' n'est pas supporté."
    except Exception as e:
        return f"Erreur : {str(e)}"
#    Retourne le type MIME d'un fichier en utilisant python-magic (basé sur le contenu binaire).
#    Si python-magic échoue, utilise mimetypes comme fallback.
def get_mime_type(file_path):
    try:
        mime = magic.Magic(mime=True)  # Initialiser l'analyse MIME
        return mime.from_file(file_path)  # Détecter le type MIME via le contenu
    except Exception:
        # Fallback avec mimetypes si python-magic échoue
        type_mime, _ = mimetypes.guess_type(file_path)
        type_mime, _ = mimetypes.guess_type(file_path)
        return type_mime or "unknown"
        
  
# Fonction pour extraire les métadonnées des images 
def get_image_metadata(image_path):
    try:
        # Ouvrir l'image
        image = Image.open(image_path)
     
        # Métadonnées générales
        metadata = {
            "Format": image.format,
            "Mode": image.mode,
            "Taille (pixels)": image.size,
        }

        # Extraction des métadonnées EXIF
        exif_data = image._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                # Ignorer la partie MakerNote
                if tag_name == "MakerNote":
                    continue
                if tag_name == "GPSInfo":
                    # Extraire les informations GPS en détail
                    gps_data = {}
                    for gps_id, gps_value in value.items():
                        gps_name = GPSTAGS.get(gps_id, gps_id)
                        gps_data[gps_name] = gps_value
                    metadata["GPSInfo"] = gps_data
                else:
                    metadata[tag_name] = value
        
        return metadata

    except Exception as e:
        return {"Erreur": str(e)}

# Fonctions pour extraire des métadonnées audio MP3, FLAC, WAV, AAC, et OGG.
def get_audio_metadata(file_path):
    audio = File(file_path)
    if not audio:
        return "Fichier audio non pris en charge."
    
      
    metadata = {
        "Titre": audio.get("TIT2", "Inconnu"),
        "Artiste": audio.get("TPE1", "Inconnu"),
        "Album": audio.get("TALB", "Inconnu"),
        "Durée (s)": audio.info.length if audio.info else "Inconnue",
        "Bitrate (kbps)": audio.info.bitrate // 1000 if audio.info and hasattr(audio.info, "bitrate") else "Inconnu"
    }
    return metadata

# Fonction pour obtenir les métadonnées d'un PDF
def get_pdf_metadata(file_path):
    try:
        reader = PdfReader(file_path)
        metadata = reader.metadata
        return {
            "Titre": metadata.title if metadata.title else "Inconnu",
            "Auteur": metadata.author if metadata.author else "Inconnu",
            "Sujet": metadata.subject if metadata.subject else "Inconnu",
            "Producteur": metadata.producer if metadata.producer else "Inconnu",
            "Création": metadata.get("/CreationDate", "Inconnue"),
            "Modification": metadata.get("/ModDate", "Inconnue"),
        }
    except Exception as e:
        return {"Erreur": str(e)}

# Fonction pour obtenir les métadonnées d'un doc
#    Extrait les métadonnées des fichiers Microsoft Office (.docx, .pptx, .xlsx, .doc, .xls, .ppt).
#    
#    :param file_path: Chemin complet vers le fichier Office.
#    :param ext: Extension du fichier (par exemple, .docx, .pptx, .xlsx).
#    :return: Dictionnaire contenant les métadonnées extraites.

def extract_ms_office_metadata(file_path, ext):
    metadata = {}

    try:
        if ext == ".docx":  # Traitement pour les fichiers Word modernes (.docx)
            doc = Document(file_path)
            core_properties = doc.core_properties
            metadata = {
                "Author": core_properties.author,
                "Title": core_properties.title,
                "Created Date": core_properties.created,
                "Last Modified Date": core_properties.modified,
                "Last Modified By": core_properties.last_modified_by,
                "Category": core_properties.category,
                "Keywords": core_properties.keywords,
                "Comments": core_properties.comments,
                "Revision": core_properties.revision,
                "Content Status": core_properties.content_status,
                "Identifier": core_properties.identifier,
                "Language": core_properties.language,
                "Version": core_properties.version
            }

        elif ext == ".pptx":  # Traitement pour les fichiers PowerPoint modernes (.pptx)
            ppt = Presentation(file_path)
            core_properties = ppt.core_properties
            metadata = {
                "Author": core_properties.author,
                "Title": core_properties.title,
                "Created Date": core_properties.created,
                "Last Modified Date": core_properties.modified,
                "Last Modified By": core_properties.last_modified_by,
                "Category": core_properties.category,
                "Keywords": core_properties.keywords,
                "Comments": core_properties.comments,
                "Revision": core_properties.revision,
                "Content Status": core_properties.content_status,
                "Identifier": core_properties.identifier,
                "Language": core_properties.language,
                "Version": core_properties.version
            }

        elif ext == ".xlsx":  # Traitement pour les fichiers Excel modernes (.xlsx)
            wb = load_workbook(file_path)
            properties = wb.properties
            metadata = {
                "Title": properties.title,
                "Subject": properties.subject,
                "Author": properties.creator,
                "Last Modified By": properties.lastModifiedBy,
                "Created Date": properties.created,
                "Last Modified Date": properties.modified,
                "Category": properties.category,
                "Keywords": properties.keywords,
                "Description": properties.description,
                "Version": properties.version,
                "Identifier": properties.identifier
            }

        elif ext in [".doc", ".xls", ".ppt"]:  # Traitement pour les fichiers Office anciens via COM
            app_type = {"doc": "Word", "xls": "Excel", "ppt": "PowerPoint"}[ext[1:]]
            app = win32com.client.Dispatch(f"{app_type}.Application")

            # Ouvrir le fichier (Word, Excel ou PowerPoint)
            if app_type == "Word":
                doc = app.Documents.Open(file_path)
                metadata = {prop.Name: prop.Value for prop in doc.BuiltInDocumentProperties}
                doc.Close()
            elif app_type == "Excel":
                wb = app.Workbooks.Open(file_path)
                metadata = {prop.Name: prop.Value for prop in wb.BuiltinDocumentProperties}
                wb.Close()
            elif app_type == "PowerPoint":
                pres = app.Presentations.Open(file_path)
                metadata = {prop.Name: prop.Value for prop in pres.BuiltInDocumentProperties}
                pres.Close()

            # Quitter l'application
            app.Quit()

        else:  # Fichier non pris en charge
            metadata = {"Erreur": f"Type de fichier non pris en charge : {ext}"}

    except Exception as e:
        metadata = {"Erreur": f"Erreur lors du traitement de {file_path} : {str(e)}"}

    return metadata
 
 
def extract_text_metadata(file_path):
    metadata = {}
  
    try:
        file_stats = os.stat(file_path)    
        metadata = {
            "Size (bytes)": file_stats.st_size,
            "Creation Time": datetime.fromtimestamp(file_stats.st_ctime),
            "Last Modified Time": datetime.fromtimestamp(file_stats.st_mtime),
            "Last Accessed Time": datetime.fromtimestamp(file_stats.st_atime)
        }
    except Exception as e:
        metadata = {"Erreur": f"Erreur lors du traitement de {file_path} : {str(e)}"}
    return metadata 

  
    
# Fonction pour extraire les métadonnées
def extract_metadata(directory, selected_types, selectionsGloabale, deep_search=False):
    metadata_results = {}
    if deep_search:
        all_files = [os.path.join(root, file) 
                     for root, _, files in os.walk(directory) for file in files]
    
        all_files = [os.path.join(root, file)   
                     for root, _, files in os.walk(directory) 
                        for file in files if os.path.splitext(file)[1] in selectionsGloabale]
    else:
        all_files = [os.path.join(directory, file) for file in os.listdir(directory)]
    
    num_files = len(all_files)
    if num_files == 0:
        return {"Erreur": "Aucun fichier trouvé."}
    
    for index, file_path in enumerate(all_files):
        if os.path.isfile(file_path):
            filename = os.path.basename(file_path)
            #print("Le type MIME de %s est : %s" % (file_path, get_mime_type(file_path)))
            ext = os.path.splitext(filename)[1].lower()  # Obtenir l'extension
            mime_type = get_mime_type(file_path)  # Obtenir le type MIME via python-magic
            # ajouter le calcul de has_key
            has_code= calculate_file_hash(file_path)
            try:
                
                metadata_results[filename] = {
                    "extension": ext,
                    "mime_type": mime_type,
                    "hash_code":has_code,
                    "metadata": None
                }
                if ("audio" in mime_type and "audio" in selected_types):
                    metadata_results[filename]["metadata"] = get_audio_metadata(file_path)
                elif ("image" in mime_type or "octet-stream" in mime_type and "image" in selected_types):
                    metadata_results[filename]["metadata"] = get_image_metadata(file_path)
                elif ("pdf" in mime_type and "pdf" in selected_types):
                    metadata_results[filename]["metadata"] = get_pdf_metadata(file_path)
                elif ("word" in mime_type and "word" in selected_types):
                    metadata_results[filename]["metadata"] = extract_ms_office_metadata(file_path,ext)
                elif ("excel" in mime_type or ext==".xlsx" and "excel" in selected_types):
                    #print("Le type MIME de %s est : %s et exten %s" % (file_path, get_mime_type(file_path),ext))
                    metadata_results[filename]["metadata"] = extract_ms_office_metadata(file_path,ext)
                elif ("presentation" in mime_type and ext == ".pptx" and "powerpoint" in selected_types):
                    #print("Le type MIME de %s est : %s et exten %s" % (file_path, get_mime_type(file_path),ext))
                    metadata_results[filename]["metadata"] = extract_ms_office_metadata(file_path,ext)
                elif ("video" in mime_type and "video" in selected_types):
                    metadata_results[filename]["metadata"] = get_video_metadata(file_path)
                elif ("text" in mime_type and "text" in selected_types):
                    metadata_results[filename]["metadata"] = extract_text_metadata(file_path)
                    #print("Le type MIME de %s est : %s et exten %s" % (file_path, get_mime_type(file_path),ext))
                else:
                    metadata_results[filename]["metadata"] = {"Erreur": "Format non pris en charge"}
            except Exception as e:
                metadata_results[filename]["metadata"] = f"Erreur : {str(e)}"
            
        progress_var.set((index + 1) / num_files * 100)
        app.update_idletasks()
    
    return metadata_results

# verfieir si n'est pas vide 
def is_notempty():
    content = results_text.get("1.0", tk.END).strip()  # Récupérer tout le contenu du widget et supprimer les espaces inutiles
    return bool(content) 
    
    
# Fonction pour sauvegarder les métadonnées
def save_metadata(metadata):
    
    if not is_notempty():
        messagebox.showwarning("Attention", "Aucun résultat à enregistrer. La liste est vide.")
        save_button.config(state="disabled")  # Désactive le bouton "Enregistrer"
    else:
        save_button.config(state="normal")  # Active le bouton "Enregistrer"
    
        try:
            # Générer un nom de fichier horodaté
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"metadata_results_{timestamp}.json"
        
            metadata1 = convert_to_serializable(metadata)
            # Enregistrer les métadonnées dans le fichier
            with open(output_file, 'w') as f:
                json.dump(metadata1, f, indent=4)
                messagebox.showinfo("Succès", f"Les métadonnées ont été enregistrées dans {output_file}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde des métadonnées : {str(e)}")
    # NPO return the path to json file in case we need to export it to csv
        return output_file

# Liste des extensions disponibles dans le dossier selectionner 
def lister_extensions(repertoire):
    extensions = set()
    for racine, _, fichiers in os.walk(repertoire):
        for fichier in fichiers:
            ext = os.path.splitext(fichier)[1].lower()
            if ext:
                extensions.add(ext)
    return sorted(extensions)


def fenetre_filtre(extensions, app, selectionsGloabale):
    if not extensions:
        return  # Ne pas ouvrir la fenêtre si aucune extension

    # ✅ Création de la fenêtre enfant
    fenetre_extensions = tk.Toplevel(app)
    fenetre_extensions.title("Sélectionner les extensions")
    fenetre_extensions.geometry("300x400")
    fenetre_extensions.grab_set()  # Bloque l'interaction avec la fenêtre principale

    # ✅ Frame principale avec couleur grise
    frame_principal = tk.Frame(fenetre_extensions, bg="lightgray")
    frame_principal.pack(fill="both", expand=True, padx=10, pady=10)

    # ✅ Label d'instruction
    label = tk.Label(frame_principal, text="Choisissez les extensions :", bg="lightgray")
    label.pack(pady=5)

    # ✅ Création d'un cadre avec `Canvas` et `Scrollbar`
    frame_canvas = tk.Frame(frame_principal, bg="lightgray")
    frame_canvas.pack(fill="both", expand=True, padx=5, pady=5)

    canvas = tk.Canvas(frame_canvas, bg="lightgray")
    scrollbar = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
    frame_extensions = tk.Frame(canvas, bg="lightgray")  # ✅ Conteneur des checkboxes

    # ✅ Configurer le canvas pour fonctionner avec la `Scrollbar`
    frame_extensions.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame_extensions, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # ✅ Placement du `Canvas` et de la `Scrollbar`
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ✅ Ajout des cases à cocher (Checkboxes)
    var_extensions = {ext: tk.BooleanVar(value=True) for ext in extensions}
    for ext, var in var_extensions.items():
        chk = ttk.Checkbutton(frame_extensions, text=ext, variable=var)
        chk.pack(anchor="w", padx=10, pady=2)

    # ✅ Fonction pour récupérer les extensions sélectionnées
    def valider_selection():
        selections = [ext for ext, var in var_extensions.items() if var.get()]
        selectionsGloabale.clear()
        selectionsGloabale.extend(selections)
       # label_resultat.config(text="Sélection : " + ", ".join(selections))  # ✅ Mise à jour de l'affichage
        fenetre_extensions.destroy()  # ✅ Ferme la fenêtre après validation

    # ✅ Fonction pour tout sélectionner
    def tout_selectionner():
        for var in var_extensions.values():
            var.set(True)

    # ✅ Fonction pour tout désélectionner
    def tout_deselectionner():
        for var in var_extensions.values():
            var.set(False)

    # ✅ Frame pour les boutons d'actions
    frame_boutons = tk.Frame(frame_principal, bg="lightgray")
    frame_boutons.pack(pady=10)

    # ✅ Boutons de sélection/désélection
    btn_tout_selectionner = ttk.Button(frame_boutons, text="Tout sélectionner", command=tout_selectionner)
    btn_tout_selectionner.pack(side="left", padx=5)

    btn_tout_deselectionner = ttk.Button(frame_boutons, text="Tout désélectionner", command=tout_deselectionner)
    btn_tout_deselectionner.pack(side="left", padx=5)

    # ✅ Bouton "Valider"
    bouton_valider = ttk.Button(frame_principal, text="Valider", command=valider_selection)
    bouton_valider.pack(pady=5)

    # ✅ Label pour afficher les extensions sélectionnées
    #label_resultat = tk.Label(frame_principal, text="Aucune sélection", bg="lightgray")
    #label_resultat.pack(pady=5)

    # ✅ Attendre la fermeture de la fenêtre avant de continuer
    fenetre_extensions.wait_window()
    
# Fonction pour sélectionner un répertoire
def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        label_repertoire.config(text=f"Répertoire choisi : {directory}")
        if not os.listdir(directory):
            messagebox.showerror("Erreur", "Le répertoire sélectionné est vide.")
            return
        else : 
            extensions = lister_extensions(directory)
            print("La liste des extensions est : %s " % (extensions))
            fenetre_filtre(extensions, app, selectionsGloabale)
            print("Extensions sélectionnées  selectinons :", selectionsGloabale)
        
        selected_types = []
        #if audio_var.get():
        selected_types.append("audio")
        #if image_var.get():
        selected_types.append("image")
        #if pdf_var.get():
        selected_types.append("pdf")
        #if word_var.get():
        selected_types.append("word")
        selected_types.append("powerpoint")
        #if excel_var.get():
        selected_types.append("excel")
        #if video_var.get():
        selected_types.append("video")
        #selected_types = []
        #if audio_var.get():
        selected_types.append("audio")
        selected_types.append("text")
                
        deep_search = deep_search_var.get()
        metadata = extract_metadata(directory, selected_types, selectionsGloabale, deep_search)
        results_text.config(state="normal")
        results_text.delete(1.0, tk.END)
        for filename, meta in metadata.items():
            results_text.insert(tk.END, f"{filename}:\n{meta}\n\n")
        save_button.config(state="normal")
        global current_metadata
        current_metadata = metadata
        file_menu.entryconfig("Ouvrir un répertoire", state=tk.DISABLED)
    results_text.config(state="disabled")        


        
# Fonction pour lancer une nouvelle analyse 
def nouvelle_analyse():
    label_repertoire.config(text="Aucun répertoire sélectionné")  # Effacer le répertoire affiché
    results_text.config(state="normal")
    # Effacer le contenu du widget Text
    results_text.delete(1.0, tk.END)
    file_menu.entryconfig("Ouvrir un répertoire", state=tk.NORMAL)
    # Afficher un message dans la console
    print("Nouvelle analyse déclenchée.")
    
    # Ajouter un texte par défaut dans le widget
    #results_text.insert(tk.END, "Analyse réinitialisée.\n")
    
    # Réinitialiser d'autres widgets si nécessaire
    #autre_widget.set("")  # Par exemple, pour un Entry ou une variable associée
    results_text.config(state="disabled")
    progress_var.set(0)
    # NPO
    # desactiver l'export csv
    menu_export.entryconfig("CSV", state="disabled")
    app.update_idletasks()
    
    
    
# Fonction export csv 
# Fonction export csv 
# NPO
# Fonction export csv
def export_csv():
    # messagebox.showwarning("en construction", "Fonction en cours de construction ")
    # Load the JSON data
    if path_to_json != "":
        convert_json_to_csv(path_to_json)
    else:
        print("Le fichier json doit etre enregistré avant de le convertir en csv")
    
   
# Fonction chargement des données depuis json  
# Fonction chargement des données depuis json  
# NPO
# Fonction chargement des données depuis json
def chargement():
    global path_to_json 
    file_path = filedialog.askopenfilename(
        title="Sélectionner un fichier JSON",
        filetypes=[("Fichiers JSON", "*.json")]
    )
    if not file_path:
        return  # L'utilisateur a annulé

    try:
        # Nettoyer le contenu actuel du widget Text
        results_text.config(state="normal")    
        results_text.delete("1.0", tk.END)
        
        # Ouvrir et lire le fichier ligne par ligne
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                results_text.insert(tk.END, line)  # Insérer chaque ligne dans le Text
            
        
        
        # # Charger le contenu du fichier JSON
        # with open(file_path, "r", encoding="utf-8") as file:
        #     data = json.load(file)



        # # Afficher les données JSON dans le widget Text
        # formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
        # results_text.insert(tk.END, formatted_json)
        path_to_json = file_path
        results_text.config(state="disabled")    

        print(f"fichier .json sélectionné : {path_to_json} chargé")
        
        # activer l'export csv
        menu_export.entryconfig("CSV", state="normal")
        app.update_idletasks()
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de lire le fichier JSON : {e}")

# Fonction comparer entre deux resultats 
 
#    Compare deux fichiers JSON contenant des métadonnées et affiche les différences.
#    L'utilisateur sélectionne les deux fichiers en une seule fois.
 

def compare_analyses():
    files = filedialog.askopenfilenames(title="Sélectionnez deux fichiers JSON",
                                        filetypes=[("Fichiers JSON", "*.json")])

    # Vérifier que l'utilisateur a sélectionné exactement 2 fichiers
    if len(files) != 2:
        messagebox.showerror("Erreur", "Veuillez sélectionner exactement deux fichiers JSON.")
        return

    file1, file2 = files  # Récupération des deux fichiers sélectionnés

    try:
        # Charger les métadonnées des deux fichiers
        with open(file1, "r", encoding="utf-8") as f1, open(file2, "r", encoding="utf-8") as f2:
            metadata1 = json.load(f1)
            metadata2 = json.load(f2)

        # Identifier les fichiers ajoutés, supprimés et modifiés
        added_files = set(metadata2.keys()) - set(metadata1.keys())  # Nouveaux fichiers
        removed_files = set(metadata1.keys()) - set(metadata2.keys())  # Fichiers supprimés
        modified_files = {}
        renamed_files = []  # Stocker les fichiers renommés

        common_files = set(metadata1.keys()) & set(metadata2.keys())  # Fichiers présents dans les deux analyses

        # Créer des dictionnaires de hash pour détecter les renommages
        hash_dict1 = {metadata1[file]["hash_code"]: file for file in metadata1 if "hash_code" in metadata1[file]}
        hash_dict2 = {metadata2[file]["hash_code"]: file for file in metadata2 if "hash_code" in metadata2[file]}

        # Détecter les fichiers renommés
        for hash_code, file1_name in hash_dict1.items():
            if hash_code in hash_dict2 and file1_name != hash_dict2[hash_code]:
                renamed_files.append((file1_name, hash_dict2[hash_code]))

        for file in common_files:
            diff_fields = {}
            meta1 = metadata1.get(file, {})
            meta2 = metadata2.get(file, {})

            for key in set(meta1.keys()).union(set(meta2.keys())):  # Comparer tous les champs
                if meta1.get(key) != meta2.get(key):
                    diff_fields[key] = {
                        "Ancienne valeur": meta1.get(key, "Absent"),
                        "Nouvelle valeur": meta2.get(key, "Absent")
                    }

            if diff_fields:
                modified_files[file] = diff_fields

        # Afficher les résultats dans une nouvelle fenêtre Tkinter
        show_results_window(file1, file2, added_files, removed_files, modified_files, renamed_files)

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la comparaison : {str(e)}")


def show_results_window(file1, file2, added_files, removed_files, modified_files, renamed_files):
    """Affiche les résultats dans une nouvelle fenêtre Tkinter."""
    result_window = tk.Toplevel(app)
    result_window.title("Résultats de la comparaison")
    result_window.geometry("700x500")
    result_window.grab_set()  # Bloque l'interaction avec la fenêtre principale

    text_area = scrolledtext.ScrolledText(result_window, wrap="word", height=25, width=80)
    text_area.pack(expand=True, fill="both", padx=10, pady=10)

    text_area.insert(tk.END, f"📌 Comparaison entre :\n{file1}\n{file2}\n\n")

    if added_files:
        text_area.insert(tk.END, "✅ Fichiers ajoutés :\n" + "\n".join(added_files) + "\n\n")

    if removed_files:
        text_area.insert(tk.END, "❌ Fichiers supprimés :\n" + "\n".join(removed_files) + "\n\n")

    if modified_files:
        text_area.insert(tk.END, "🔄 Fichiers modifiés :\n")
        for file, changes in modified_files.items():
            text_area.insert(tk.END, f"📂 {file}\n")
            for key, value in changes.items():
                text_area.insert(tk.END, f"   🔹 {key} :\n")
                text_area.insert(tk.END, f"      ➖ Ancienne valeur : {value['Ancienne valeur']}\n")
                text_area.insert(tk.END, f"      ➕ Nouvelle valeur : {value['Nouvelle valeur']}\n\n")

    if renamed_files:
        text_area.insert(tk.END, "🔀 Fichiers renommés :\n")
        for old_name, new_name in renamed_files:
            text_area.insert(tk.END, f"   🔄 {old_name} → {new_name}\n")
        text_area.insert(tk.END, "\n")

    if not (added_files or removed_files or modified_files or renamed_files):
        text_area.insert(tk.END, "✅ Aucune différence détectée.\n")

    text_area.config(state="disabled")

    # Bouton pour exporter en CSV
    export_button = tk.Button(result_window, text="Exporter en CSV",
                              command=lambda: export_to_csv(added_files, removed_files, modified_files, renamed_files))
    export_button.pack(pady=10)


def show_results_window_stat(file1, file2):
    """Affiche les résultats dans une nouvelle fenêtre Tkinter."""
    result_window = tk.Toplevel(app)
    result_window.title("Résultats de la comparaison")
    result_window.geometry("700x500")
    result_window.grab_set()  # Bloque l'interaction avec la fenêtre principale

    text_area = scrolledtext.ScrolledText(result_window, wrap="word", height=25, width=80)
    text_area.pack(expand=True, fill="both", padx=10, pady=10)

    text_area.insert(tk.END, f"📌 Comparaison entre :\n{file1}\n{file2}\n\n")

    if added_files:
        text_area.insert(tk.END, "✅ Fichiers ajoutés :\n" + "\n".join(added_files) + "\n\n")

    if removed_files:
        text_area.insert(tk.END, "❌ Fichiers supprimés :\n" + "\n".join(removed_files) + "\n\n")

    if modified_files:
        text_area.insert(tk.END, "🔄 Fichiers modifiés :\n")
        for file, changes in modified_files.items():
            text_area.insert(tk.END, f"📂 {file}\n")
            for key, value in changes.items():
                text_area.insert(tk.END, f"   🔹 {key} :\n")
                text_area.insert(tk.END, f"      ➖ Ancienne valeur : {value['Ancienne valeur']}\n")
                text_area.insert(tk.END, f"      ➕ Nouvelle valeur : {value['Nouvelle valeur']}\n\n")

    if renamed_files:
        text_area.insert(tk.END, "🔀 Fichiers renommés :\n")
        for old_name, new_name in renamed_files:
            text_area.insert(tk.END, f"   🔄 {old_name} → {new_name}\n")
        text_area.insert(tk.END, "\n")

    if not (added_files or removed_files or modified_files or renamed_files):
        text_area.insert(tk.END, "✅ Aucune différence détectée.\n")

    text_area.config(state="disabled")

    # Bouton pour exporter en CSV
    export_button = tk.Button(result_window, text="Exporter en CSV",
                              command=lambda: export_to_csv(added_files, removed_files, modified_files, renamed_files))
    export_button.pack(pady=10)


def export_to_csv(added, removed, modified, renamed):
    """Exporte les résultats de la comparaison en CSV."""
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("Fichiers CSV", "*.csv")],
                                             title="Enregistrer le fichier CSV")

    if not file_path:
        return  # L'utilisateur a annulé l'enregistrement

    try:
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(["Type de modification", "Fichier", "Ancien nom", "Nouveau nom"])

            for file in added:
                writer.writerow(["Ajouté", file, "", ""])
            for file in removed:
                writer.writerow(["Supprimé", file, "", ""])
            for file, changes in modified.items():
                writer.writerow(["Modifié", file, "", ""])
                for key, value in changes.items():
                    writer.writerow(["", "", key, value["Ancienne valeur"], value["Nouvelle valeur"]])
            for old, new in renamed:
                writer.writerow(["Renommé", "", old, new])

        messagebox.showinfo("Export réussi", f"Les différences ont été enregistrées dans {file_path}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'export en CSV : {str(e)}")


# Fonction statistique à édéfinir  
def stat_result():
 # Exécution du script
    file_path = filedialog.askopenfilename(
        title="Sélectionner un fichier JSON",
        filetypes=[("Fichiers JSON", "*.json")]
    )
    files_data, json_file_path = load_json(file_path)
    
    if files_data is not None:
        display_results(files_data, json_file_path)        
    else:
        print(" Erreur lors du chargement du fichier JSON. Arrêt du programme.")
    

# Charger le fichier JSON
def load_json(file_path):  
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file), file_path
    except FileNotFoundError:
        print(f" Fichier introuvable: {file_path}. Vérifiez le chemin et réessayez.")
        return None, None
    except json.JSONDecodeError:
        print(f" Erreur lors du chargement du fichier JSON: {file_path}. Vérifiez qu'il est valide.")
        return None, None
    

from datetime import datetime, timezone
import logging

def parse_date(date_str):
    """Convertit une date ISO 8601 en objet datetime (offset-aware)."""
    try:
        if date_str.endswith("Z"):  # UTC avec 'Z'
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        date_obj = datetime.fromisoformat(date_str)
        if date_obj.tzinfo is None:  # Pas de fuseau horaire
            return date_obj.replace(tzinfo=timezone.utc)
        return date_obj
    except ValueError:
        logging.warning(f"Format de date invalide : {date_str}")
        return None

def sort_by_date(files):
    """Trie les fichiers par date de modification (offset-aware)."""
    file_data = []

    for name, info in files.items():
        metadata = info.get("metadata", {})
        if not isinstance(metadata, dict):
            continue  # Ignorer si metadata n'est pas un dictionnaire

        date_str = metadata.get("Last Modified Date") or metadata.get("Last Modified Time")
        if date_str:
            date_obj = parse_date(date_str)
            if date_obj:
                file_data.append({
                    "name": name,
                    "extension": info["extension"],
                    "date": date_obj
                })

    # Trier par date
    return sorted(file_data, key=lambda x: x["date"])


# Calculer la composition des fichiers par extension
def calculate_file_distribution(files):
    total_files = len(files)
    type_counts = Counter(info["extension"] for info in files.values() if "extension" in info)
    percentage_distribution = {ext: round((count / total_files) * 100, 2) for ext, count in type_counts.items()}
    return type_counts, percentage_distribution

# Afficher les résultats
def display_results(files, file_path):
    sorted_files = sort_by_date(files)
    
    if not sorted_files:
        print(" Aucun fichier valide trouvé avec des dates de modification.")
        return
    
    # 3 plus anciens et 3 plus récents fichiers
    oldest_files = sorted_files[:3]
    newest_files = sorted_files[-3:]

    # Distribution des fichiers
    type_counts, percentage_distribution = calculate_file_distribution(files)

    print(f"\n **Statistiques pour le fichier : {file_path}**")
    show_results_window_stat(oldest_files, newest_files,type_counts,percentage_distribution,file_path)
#####################################

def show_results_window_stat(oldest_files, newest_files, type_counts, percentage_distribution, file_path):
    """Affiche les résultats avec un histogramme montrant les 20 premières valeurs triées."""
    stat_window = tk.Toplevel(app)
    stat_window.title("Statistique de fichier")
    stat_window.geometry("800x600")
    stat_window.grab_set()  # Bloque l'interaction avec la fenêtre principale

    # Zone de texte avec défilement
    text_area = scrolledtext.ScrolledText(stat_window, wrap="word", height=15, width=80)
    text_area.pack(expand=True, fill="both", padx=10, pady=10)

    # Titre du fichier analysé
    text_area.insert(tk.END, f"\n **Statistiques pour le fichier : {file_path}**\n")

    # Affichage des 3 fichiers les plus anciens
    text_area.insert(tk.END, "\n **3 Fichiers les Plus Anciens**\n\n")
    for file in oldest_files:
        try:
            text_area.insert(tk.END, f" {file['name']} - {file['date']}\n")
        except KeyError:
            text_area.insert(tk.END, " Erreur: Informations manquantes pour un fichier.\n")

    # Affichage des 3 fichiers les plus récents
    text_area.insert(tk.END, "\n **3 Fichiers les Plus Récents**\n\n")
    for file in newest_files:
        try:
            text_area.insert(tk.END, f" {file['name']} - {file['date']}\n")
        except KeyError:
            text_area.insert(tk.END, " Erreur: Informations manquantes pour un fichier.\n")

    # Composition totale des fichiers (triée par ordre décroissant)
    text_area.insert(tk.END, "\n **Composition Totale des Fichiers (Triée)**\n\n")
    sorted_type_counts = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)  # Tri par nombre décroissant

    # Limiter à 20 éléments
    top_20_type_counts = sorted_type_counts[:20]

    for ext, count in top_20_type_counts:
        percentage = percentage_distribution.get(ext, 0)
        text_area.insert(tk.END, f" {ext}: {count} fichiers ({percentage}%)\n")

    # Désactiver la zone de texte pour éviter les modifications
    text_area.config(state="disabled")

    # Création de l’histogramme avec Matplotlib
    fig, ax = plt.subplots(figsize=(6, 4))
    extensions = [ext for ext, _ in top_20_type_counts]  # Extensions des 20 premiers
    counts = [count for _, count in top_20_type_counts]  # Nombres des 20 premiers
    percentages = [percentage_distribution[ext] for ext in extensions]

    bars = ax.bar(extensions, counts, color="skyblue")
    ax.set_title("Top 20 Types de Fichiers")
    ax.set_xlabel("Extensions de fichiers")
    ax.set_ylabel("Nombre de fichiers")
    ax.tick_params(axis="x", rotation=45)

    # Ajouter les pourcentages directement sur les barres
    for bar, percentage in zip(bars, percentages):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # Position X (au centre de la barre)
            height / 2,  # Position Y (au milieu de la barre)
            f"{percentage:.1f}%",  # Texte affiché
            ha="center", va="center", fontsize=10, color="white"  # Texte centré et blanc
        )

    # Intégrer l’histogramme dans la fenêtre Tkinter
    canvas = FigureCanvasTkAgg(fig, master=stat_window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(expand=True, fill="both", padx=10, pady=10)
    canvas.draw()

    # Bouton pour exporter en CSV
    export_button = tk.Button(
        stat_window,
        text="Exporter en CSV",
        command=lambda: export_to_csv(oldest_files, newest_files, type_counts, percentage_distribution)
    )
    export_button.pack(pady=10)
  
##################################################################    
def on_save():
    #l(current_metadata)
    # NPO
    global path_to_json
    path_to_json = save_metadata(current_metadata)




# Ajouter la commande au menu
#file_menu.add_command(label="Nouvelle analyse", command=nouvelle_analyse)
selectionsGloabale = []
OUVdata = {}

# Interface Tkinter
app = tk.Tk()
app.title("Extracteur de Métadonnées")
app.geometry("800x550")

# Menu principal
menu_bar = tk.Menu(app)

# Menu "Fichier"
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Nouvelle analyse", command=nouvelle_analyse)
file_menu.add_command(label="Ouvrir un répertoire", command=select_directory)
file_menu.add_separator()
file_menu.add_command(label="Quitter", command=app.quit)
menu_bar.add_cascade(label="Fichier", menu=file_menu)

#Label pour afficher le répertoire sélectionné
label_repertoire = ttk.Label(app, text="Aucun répertoire sélectionné")
label_repertoire.pack(pady=5)


# Menu "Données"
data_menu = tk.Menu(menu_bar, tearoff=0)
data_menu.add_command(label="Charger ...", command=chargement)
data_menu.add_command(label="Comparer ...", command=compare_analyses)
data_menu.add_separator()
data_menu.add_command(label="Statistique", command=stat_result)
menu_bar.add_cascade(label="Données", menu=data_menu)

menu_export=tk.Menu(data_menu, tearoff=0)
menu_export.add_command(label="CSV", command=export_csv)
#menu_export.add_command(label="DUMP", command=export_dump)
data_menu.add_cascade(label="Export CSV...",menu = menu_export)


# Menu "Aide"
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="À propos", command=lambda: messagebox.showinfo(
    "À propos", "Cette application permet d'extraire les métadonnées des fichiers dans un répertoire donné."))
menu_bar.add_cascade(label="Aide", menu=help_menu)

# Appliquer le menu à la fenêtre principale
app.config(menu=menu_bar)


options_frame = tk.Frame(app)
options_frame.pack(pady=5)

deep_search_var = tk.BooleanVar(value = True)
# NPO cette variable conserve le chemin du fichier json en cours une fois cliqué sur le bouton enregistré
path_to_json=""
tk.Checkbutton(options_frame, text="Activer la recherche approfondie", variable=deep_search_var)
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, variable=progress_var, maximum=100)
progress_bar.pack(side ="bottom", fill="x", padx=10, pady=10)

progress_label = tk.Label(app, text="Progression : 0 %")
progress_label.pack(side="bottom", pady=5)

progress_var.trace("w", lambda *args: progress_label.config(
    text=f"Progression : {int(progress_var.get())} %"
))

results_text = Text(app, wrap="word", height=10)
results_text.pack(expand=True, fill="both", padx=10, pady=10)
scrollbar = tk.Scrollbar(app, orient="vertical", command=results_text.yview)
scrollbar.pack(side="right", fill="y")
results_text.config(yscrollcommand=scrollbar.set)
results_text.config(state="disabled")


save_button = tk.Button(app, text="Enregistrer", command=on_save, state="disabled")
save_button.pack(pady=5)

app.mainloop()