import os
import mutagen
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
from PyPDF2 import PdfFileReader
import docx
import openpyxl
import json
import ffmpeg
import pikepdf
import tkinter as tk
from tkinter import filedialog, messagebox, Text, ttk
from datetime import datetime
from mutagen import File
from PyPDF2 import PdfReader
from PIL.ExifTags import TAGS, GPSTAGS


# Fonctions d'extraction des métadonnées
# (Les fonctions `get_audio_metadata`, `get_image_metadata`, etc., restent les mêmes)


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


# Fonction pour extraire les métadonnées
def extract_metadata(directory, selected_types, deep_search=False):
    metadata_results = {}
    if deep_search:
        all_files = [os.path.join(root, file) 
                     for root, _, files in os.walk(directory) for file in files]
    else:
        all_files = [os.path.join(directory, file) for file in os.listdir(directory)]
    
    num_files = len(all_files)
    if num_files == 0:
        return {"Erreur": "Aucun fichier trouvé."}
    
    for index, file_path in enumerate(all_files):
        if os.path.isfile(file_path):
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()
            try:
                if (ext in ['.mp3', '.wav', '.flac'] and "audio" in selected_types):
                    metadata_results[filename] = get_audio_metadata(file_path)
                elif (ext in ['.jpg', '.jpeg', '.png', '.tiff'] and "image" in selected_types):
                    metadata_results[filename] = get_image_metadata(file_path)
                elif (ext == '.pdf' and "pdf" in selected_types):
                    metadata_results[filename] = get_pdf_metadata(file_path)
                elif (ext == '.docx' and "word" in selected_types):
                    metadata_results[filename] = get_docx_metadata(file_path)
                elif (ext == '.xlsx' and "excel" in selected_types):
                    metadata_results[filename] = get_excel_metadata(file_path)
                elif (ext in ['.mp4', '.mov', '.avi'] and "video" in selected_types):
                    metadata_results[filename] = get_video_metadata(file_path)
                else:
                    metadata_results[filename] = "Format non pris en charge"
            except Exception as e:
                metadata_results[filename] = f"Erreur : {str(e)}"

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
        
            # Enregistrer les métadonnées dans le fichier
            with open(output_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                messagebox.showinfo("Succès", f"Les métadonnées ont été enregistrées dans {output_file}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde des métadonnées : {str(e)}")

# Fonction pour sélectionner un répertoire
def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        if not os.listdir(directory):
            messagebox.showerror("Erreur", "Le répertoire sélectionné est vide.")
            return
        
        selected_types = []
        #if audio_var.get():
        selected_types.append("audio")
        #if image_var.get():
        selected_types.append("image")
        #if pdf_var.get():
        #    selected_types.append("pdf")
        #if word_var.get():
        #    selected_types.append("word")
        #if excel_var.get():
        #    selected_types.append("excel")
        #if video_var.get():
        selected_types.append("video")
        #selected_types = []
        #if audio_var.get():
        selected_types.append("audio")
        #if image_var.get():
        selected_types.append("image")
        #if pdf_var.get():
        selected_types.append("pdf")
        #if word_var.get():
        #    selected_types.append("word")
        #if excel_var.get():
        #    selected_types.append("excel")
        #if video_var.get():
        #    selected_types.append("video")
        
        
        deep_search = deep_search_var.get()
        metadata = extract_metadata(directory, selected_types, deep_search)
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
    app.update_idletasks()
    
    

# Ajouter la commande au menu
#file_menu.add_command(label="Nouvelle analyse", command=nouvelle_analyse)


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

# Menu "Données"
data_menu = tk.Menu(menu_bar, tearoff=0)
data_menu.add_command(label="Charger ...", command="")
data_menu.add_command(label="Comparer ...", command="")
data_menu.add_separator()
data_menu.add_command(label="Statistique", command="")
menu_bar.add_cascade(label="Données", menu=data_menu)

menu_export=tk.Menu(data_menu, tearoff=0)
menu_export.add_command(label="CSV", command="")
menu_export.add_command(label="DUMP", command="")
data_menu.add_cascade(label="Export",menu = menu_export)


# Menu "Aide"
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="À propos", command=lambda: messagebox.showinfo(
    "À propos", "Cette application permet d'extraire les métadonnées des fichiers dans un répertoire donné."))
menu_bar.add_cascade(label="Aide", menu=help_menu)

# Appliquer le menu à la fenêtre principale
app.config(menu=menu_bar)


options_frame = tk.Frame(app)
options_frame.pack(pady=5)

audio_var = tk.BooleanVar()
image_var = tk.BooleanVar()
pdf_var = tk.BooleanVar()
word_var = tk.BooleanVar()
excel_var = tk.BooleanVar()
video_var = tk.BooleanVar()
deep_search_var = tk.BooleanVar(value = True)
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

def on_save():
    save_metadata(current_metadata)

save_button = tk.Button(app, text="Enregistrer", command=on_save, state="disabled")
save_button.pack(pady=5)

app.mainloop()
