import json
from collections import Counter
from datetime import datetime

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
    
# Trier les fichiers par date de modification
def sort_by_date(files):
    file_data = []
    for name, info in files.items():
        metadata = info.get("metadata", {})

        # Vérifier si metadata est un dictionnaire avant d'extraire les dates
        if not isinstance(metadata, dict):
            continue  # Ignorer si ce n'est pas un dictionnaire
        
        date_str = metadata.get("Last Modified Date") or metadata.get("Last Modified Time")
        
        if date_str:
            try:
                file_data.append({
                    "name": name,
                    "extension": info["extension"],
                    "date": datetime.fromisoformat(date_str.replace("Z", ""))
                })
            except ValueError:
                continue  # Ignorer les erreurs de conversion
        
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
    
    print("\n **3 Fichiers les Plus Anciens**")
    for f in oldest_files:
        print(f" {f['name']} - {f['date']}")

    print("\n **3 Fichiers les Plus Récents**")
    for f in newest_files:
        print(f" {f['name']} - {f['date']}")

    print("\n **Composition Totale des Fichiers**")
    for ext, count in type_counts.items():
        print(f" {ext}: {count} fichiers ({percentage_distribution[ext]}%)")

# Exécution du script
if __name__ == "__main__":
    file_path = input(" Entrez le chemin du fichier JSON : ").strip()
    files_data, json_file_path = load_json(file_path)
    
    if files_data is not None:
        display_results(files_data, json_file_path)
    else:
        print(" Erreur lors du chargement du fichier JSON. Arrêt du programme.")
