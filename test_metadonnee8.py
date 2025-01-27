import os
import hashlib
import json
from collections import defaultdict, Counter
from datetime import datetime

# Chemin pour stocker les hachages et les métadonnées
HASH_FILE_JSON = "hash_registry.json"

# Magic bytes pour identifier différents types de fichiers
MAGIC_BYTES = {
    b'\xFF\xD8\xFF': 'JPEG Image',
    b'\x89PNG': 'PNG Image',
    b'GIF87a': 'GIF Image',
    b'GIF89a': 'GIF Image',
    b'\x00\x00\x00\x18ftypmp42': 'MP4 Video',
    b'\x1A\x45\xDF\xA3': 'MKV Video',
    b'MZ': 'Executable or DLL',
    b'\x7FELF': 'Linux Executable (ELF)',
}

# Extensions des fichiers à analyser
EXTENSIONS = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
    'videos': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm'],
    'system': ['.sys', '.dll', '.exe', '.bat', '.sh']
}

def load_hash_registry():
    """
    Charge les hachages existants à partir d'un fichier JSON.
    """
    if os.path.exists(HASH_FILE_JSON):
        with open(HASH_FILE_JSON, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def save_hash_registry(hash_registry):
    """
    Sauvegarde les hachages et les métadonnées dans un fichier JSON.
    """
    with open(HASH_FILE_JSON, 'w', encoding='utf-8') as file:
        json.dump(hash_registry, file, indent=4, ensure_ascii=False)

def calculate_hash(file_path):
    """
    Calcule le hash SHA-256 d'un fichier.
    """
    try:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        return f"Error: {e}"

def is_media_or_system_file(file_name):
    """
    Vérifie si un fichier a une extension supportée (images, vidéos, ou fichiers système).
    """
    _, ext = os.path.splitext(file_name.lower())
    return (
        ext in EXTENSIONS['images'] or 
        ext in EXTENSIONS['videos'] or 
        ext in EXTENSIONS['system']
    )

def identify_file(file_path):
    """
    Identifie le type de fichier en utilisant les magic bytes.
    """
    try:
        with open(file_path, 'rb') as file:
            header = file.read(16)
            for magic, file_type in MAGIC_BYTES.items():
                if header.startswith(magic):
                    return file_type
        return "Unknown"
    except Exception as e:
        return f"Error: {e}"

def list_files_and_metadata(directory, hash_registry):
    """
    Parcourt un répertoire pour lister les fichiers et collecter leurs métadonnées.
    Met à jour le registre des hachages pour éviter les doublons.
    """
    metadata_list = []
    total_size = 0

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            file_hash = calculate_hash(file_path)

            # Vérifie si le fichier existe déjà dans le registre
            if file_hash in hash_registry:
                status = "Duplicate"
            else:
                status = "New"
                hash_registry[file_hash] = file_path

            if is_media_or_system_file(file) or identify_file(file_path) != "Unknown":
                file_type = identify_file(file_path)
            else:
                file_type = "Unknown"

            metadata_list.append({
                "name": file,
                "path": file_path,
                "type": file_type,
                "size": file_size,
                "modification_time": file_mtime,
                "hash": file_hash,
                "status": status
            })

            total_size += file_size

    return metadata_list, total_size

def display_statistics(metadata_list):
    """
    Affiche les statistiques : 3 fichiers les plus récents, 3 plus anciens, pourcentage par extension, et fichiers non supportés.
    """
    # Trier les fichiers par date de modification
    sorted_files = sorted(metadata_list, key=lambda x: x['modification_time'])

    # 3 plus anciens
    print("\nLes 3 fichiers les plus anciens :")
    for file in sorted_files[:3]:
        print(f"{file['name']} - {file['modification_time']}")

    # 3 plus récents
    print("\nLes 3 fichiers les plus récents :")
    for file in sorted_files[-3:]:
        print(f"{file['name']} - {file['modification_time']}")

    # Statistiques par extension
    extension_counter = Counter(file['type'] for file in metadata_list)
    total_files = len(metadata_list)

    print("\nPourcentage des fichiers par type :")
    for ext, count in extension_counter.items():
        percentage = (count / total_files) * 100
        print(f"{ext}: {percentage:.2f}%")

    # Fichiers non supportés
    unsupported_count = sum(1 for file in metadata_list if file['status'] == "Unsupported")
    unsupported_percentage = (unsupported_count / total_files) * 100
    print(f"\nFichiers non supportés : {unsupported_count} ({unsupported_percentage:.2f}%)")

def export_metadata_to_json(metadata_list, output_file):
    """
    Exporte les métadonnées collectées dans un fichier JSON.
    """
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(metadata_list, json_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # Charger le registre des hachages
    hash_registry = load_hash_registry()

    # Chemin du répertoire à analyser
    directory = input("Entrez le chemin du répertoire à analyser : ")

    # Collecte des métadonnées
    metadata_list, total_size = list_files_and_metadata(directory, hash_registry)

    # Exportation des métadonnées dans un fichier JSON
    output_file = "metadata_results.json"
    export_metadata_to_json(metadata_list, output_file)

    # Sauvegarder les hachages mis à jour
    save_hash_registry(hash_registry)

    # Récapitulatif des résultats
    print(f"\nExportation terminée : {output_file}")
    print(f"Nombre total de fichiers : {len(metadata_list)}")
    print(f"Taille totale des fichiers : {total_size} octets")

    # Afficher les statistiques
    display_statistics(metadata_list)
