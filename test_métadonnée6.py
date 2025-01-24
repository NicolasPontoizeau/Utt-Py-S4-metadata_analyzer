import os
import hashlib
import csv
from collections import Counter, defaultdict  # Pour les statistiques avancées

# Chemin pour stocker les hachages
HASH_FILE = "hash_registry.csv"

# Magic bytes pour identifier différents types de fichiers
MAGIC_BYTES = {
    b'\xFF\xD8\xFF': 'JPEG Image',  # Magic byte pour les fichiers JPEG
    b'\x89PNG': 'PNG Image',        # Magic byte pour les fichiers PNG
    b'GIF87a': 'GIF Image',         # Magic byte pour les fichiers GIF (format GIF87a)
    b'GIF89a': 'GIF Image',         # Magic byte pour les fichiers GIF (format GIF89a)
    b'\x00\x00\x00\x18ftypmp42': 'MP4 Video',  # Magic byte pour les fichiers MP4
    b'\x1A\x45\xDF\xA3': 'MKV Video',          # Magic byte pour les fichiers MKV
    b'MZ': 'Executable or DLL',               # Magic byte pour les fichiers exécutables ou DLL
    b'\x7FELF': 'Linux Executable (ELF)',     # Magic byte pour les fichiers exécutables ELF
}

# Extensions des fichiers à analyser
EXTENSIONS = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],  # Extensions des images
    'videos': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm'],    # Extensions des vidéos
    'system': ['.sys', '.dll', '.exe', '.bat', '.sh']                       # Extensions des fichiers système
}

# Charge les hachages existants à partir du fichier CSV
def load_hash_registry():
    hash_registry = {}
    if os.path.exists(HASH_FILE):  # Vérifie si le fichier existe
        with open(HASH_FILE, 'r', newline='') as file:
            reader = csv.reader(file)  # Lit le fichier CSV
            for row in reader:
                if len(row) == 2:  # Vérifie que chaque ligne contient deux colonnes
                    hash_registry[row[0]] = row[1]  # Ajoute le hachage et le fichier au dictionnaire
    return hash_registry

# Sauvegarde les hachages dans le fichier CSV
def save_hash_registry(hash_registry):
    with open(HASH_FILE, 'w', newline='') as file:
        writer = csv.writer(file)  # Prépare un écrivain pour le fichier CSV
        for file_hash, file_name in hash_registry.items():
            writer.writerow([file_hash, file_name])  # Écrit chaque hachage et fichier associé

# Calcule le hash SHA-256 d'un fichier
def calculate_hash(file_path):
    try:
        hasher = hashlib.sha256()  # Initialise le calculateur de hachage
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):  # Lit le fichier par blocs (8192 octets)
                hasher.update(chunk)  # Ajoute chaque bloc au calcul du hachage
        return hasher.hexdigest()  # Retourne le hachage calculé
    except Exception as e:
        return f"Error: {e}"  # En cas d'erreur, retourne un message descriptif

# Vérifie si un fichier a une extension supportée (images, vidéos, ou fichiers système)
def is_media_or_system_file(file_name):
    _, ext = os.path.splitext(file_name.lower())  # Sépare le nom et l'extension
    return (
        ext in EXTENSIONS['images'] or 
        ext in EXTENSIONS['videos'] or 
        ext in EXTENSIONS['system']
    )

# Identifie le type de fichier en utilisant les magic bytes
def identify_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            header = file.read(16)  # Lit les 16 premiers octets du fichier
            for magic, file_type in MAGIC_BYTES.items():
                if header.startswith(magic):  # Compare avec les magic bytes connus
                    return file_type
        return "Unknown"  # Retourne "Inconnu" si aucun type n'est reconnu
    except Exception as e:
        return f"Error: {e}"  # En cas d'erreur, retourne un message descriptif

# Parcourt un répertoire pour identifier et analyser les fichiers
def list_files_with_hash(directory, hash_registry):
    new_files = []  # Liste des nouveaux fichiers trouvés
    metadata_counter = Counter()  # Compteur pour les types de fichiers
    extension_counter = Counter()  # Compteur pour les extensions
    size_tracker = defaultdict(int)  # Dictionnaire pour suivre la taille par type de fichier
    total_size = 0  # Variable pour la taille totale de tous les fichiers

    for root, _, files in os.walk(directory):  # Parcourt récursivement les sous-répertoires
        for file in files:
            file_path = os.path.join(root, file)  # Chemin complet du fichier
            if is_media_or_system_file(file) or identify_file(file_path) != "Unknown":
                file_hash = calculate_hash(file_path)  # Calcule le hachage du fichier
                if file_hash in hash_registry:  # Vérifie si le hachage existe déjà
                    print(f"Fichier déjà existant : {file} - Hash: {file_hash}")
                    continue

                file_type = identify_file(file_path)  # Identifie le type du fichier
                file_size = os.path.getsize(file_path)  # Taille du fichier
                total_size += file_size  # Ajoute la taille au total
                size_tracker[file_type] += file_size  # Ajoute la taille au type correspondant

                hash_registry[file_hash] = file  # Ajoute le hachage au registre
                new_files.append((file, file_type, file_hash, file_size))  # Ajoute à la liste des nouveaux fichiers

                metadata_counter[file_type] += 1  # Met à jour les statistiques des types
                _, ext = os.path.splitext(file.lower())  # Récupère l'extension
                extension_counter[ext] += 1  # Met à jour les statistiques des extensions

    return new_files, metadata_counter, extension_counter, size_tracker, total_size

if __name__ == "__main__":
    hash_registry = load_hash_registry()  # Charger les hachages existants
    directory = input("Entrez le chemin du répertoire à analyser : ")  # Demander à l'utilisateur un répertoire
    new_files, metadata_counter, extension_counter, size_tracker, total_size = list_files_with_hash(directory, hash_registry)

    if new_files:
        print("\nNouveaux fichiers trouvés :")
        for file, file_type, file_hash, file_size in new_files:
            print(f"{file} - {file_type} - Hash: {file_hash} - Taille: {file_size} octets")

        save_hash_registry(hash_registry)  # Sauvegarder les nouveaux hachages

        print("\nStatistiques des types de fichiers identifiés :")
        for file_type, count in metadata_counter.items():
            percentage = (count / sum(metadata_counter.values())) * 100
            print(f"{file_type}: {count} fichiers ({percentage:.2f}%)")

        print("\nStatistiques des extensions de fichiers :")
        for ext, count in extension_counter.items():
            print(f"{ext}: {count} fichiers")

        print("\nTaille totale des fichiers par type :")
        for file_type, size in size_tracker.items():
            print(f"{file_type}: {size} octets")

        print(f"\nTaille totale de tous les fichiers analysés : {total_size} octets")
    else:
        print("Aucun nouveau fichier trouvé.")
