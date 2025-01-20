import os
import hashlib
import csv

# Chemin pour stocker les hachages
HASH_FILE = "hash_registry.csv"

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
    Charge les hachages depuis un fichier CSV.
    Retourne un dictionnaire où les clés sont les hachages et les valeurs sont les noms de fichiers.
    """
    hash_registry = {}
    if os.path.exists(HASH_FILE):  # Vérifie si le fichier CSV existe
        with open(HASH_FILE, 'r', newline='') as file:
            reader = csv.reader(file)  # Lit le fichier CSV
            for row in reader:
                if len(row) == 2:  # Vérifie le format correct (hash, fichier)
                    hash_registry[row[0]] = row[1]
    return hash_registry

def save_hash_registry(hash_registry):
    """
    Sauvegarde les hachages et les noms de fichiers dans un fichier CSV.
    Écrase le fichier précédent avec les données mises à jour.
    """
    with open(HASH_FILE, 'w', newline='') as file:
        writer = csv.writer(file)  # Prépare un écrivain pour le fichier CSV
        for file_hash, file_name in hash_registry.items():
            writer.writerow([file_hash, file_name])  # Écrit chaque hachage et fichier associé

def calculate_hash(file_path):
    """
    Calcule le hash SHA-256 d'un fichier.
    Retourne le hash sous forme de chaîne de caractères.
    """
    try:
        hasher = hashlib.sha256()  # Initialise le calculateur SHA-256
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):  # Lire par blocs (8192 octets)
                hasher.update(chunk)  # Ajoute chaque bloc au calcul du hash
        return hasher.hexdigest()  # Retourne le hash final
    except Exception as e:
        return f"Error: {e}"  # Retourne un message d'erreur en cas de problème

def is_media_or_system_file(file_name):
    """
    Vérifie si un fichier a une extension correspondant à une image, une vidéo ou un fichier système.
    Retourne True si l'extension est prise en charge, sinon False.
    """
    _, ext = os.path.splitext(file_name.lower())  # Sépare le nom et l'extension
    return (
        ext in EXTENSIONS['images'] or 
        ext in EXTENSIONS['videos'] or 
        ext in EXTENSIONS['system']
    )

def identify_file(file_path):
    """
    Identifie le type de fichier en utilisant les magic bytes.
    Retourne le type de fichier ou "Unknown" si aucun type n'est reconnu.
    """
    try:
        with open(file_path, 'rb') as file:
            header = file.read(16)  # Lit les 16 premiers octets du fichier
            for magic, file_type in MAGIC_BYTES.items():
                if header.startswith(magic):  # Compare avec les magic bytes connus
                    return file_type
        return "Unknown"  # Retourne "Inconnu" si aucun magic byte ne correspond
    except Exception as e:
        return f"Error: {e}"  # Retourne un message d'erreur en cas de problème

def list_files_with_hash(directory, hash_registry):
    """
    Parcourt un répertoire pour lister les fichiers à analyser.
    Identifie les fichiers, calcule leurs hachages et vérifie s'ils sont nouveaux ou existants.
    Retourne une liste des nouveaux fichiers trouvés.
    """
    new_files = []  # Liste pour stocker les nouveaux fichiers trouvés
    for root, _, files in os.walk(directory):  # Parcourt récursivement les répertoires
        for file in files:
            file_path = os.path.join(root, file)  # Chemin complet du fichier
            # Vérifie si le fichier est une image, une vidéo ou un fichier système
            if is_media_or_system_file(file) or identify_file(file_path) != "Unknown":
                file_hash = calculate_hash(file_path)  # Calcule le hash du fichier
                
                # Vérifie si le hachage existe déjà
                if file_hash in hash_registry:
                    print(f"Fichier déjà existant : {file} - Hash: {file_hash}")
                    continue  # Passe au fichier suivant
                
                file_type = identify_file(file_path)  # Identifie le type du fichier
                hash_registry[file_hash] = file  # Ajoute le hachage au registre
                new_files.append((file, file_type, file_hash))  # Ajoute à la liste des nouveaux fichiers
    return new_files

if __name__ == "__main__":
    # Charger les hachages existants depuis le fichier CSV
    hash_registry = load_hash_registry()

    # Demande à l'utilisateur le répertoire à analyser
    directory = input("Entrez le chemin du répertoire à analyser : ")
    new_files = list_files_with_hash(directory, hash_registry)

    if new_files:
        print("\nNouveaux fichiers trouvés :")
        for file, file_type, file_hash in new_files:
            print(f"{file} - {file_type} - Hash: {file_hash}")
        # Sauvegarde les nouveaux hachages dans le fichier CSV
        save_hash_registry(hash_registry)
    else:
        print("Aucun nouveau fichier trouvé.")
