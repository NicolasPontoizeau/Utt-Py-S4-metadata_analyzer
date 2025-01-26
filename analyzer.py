import os
import mimetypes
import csv

data = {}

# Spécifiez la racine du disque à parcourir
root_path = "/home/nico/ciso"

for root, dirs, files in os.walk(root_path):
    for f in files:
        file_path = os.path.join(root, f)
        mime_type, encoding = mimetypes.guess_type(file_path)
        if not mime_type:
            continue
        if mime_type not in data:
            data[mime_type] = []
        data[mime_type].append(file_path)

# Écriture des données dans un fichier CSV
csv_cols = ["mime_type", "file_paths"]
with open("mime_file_paths.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(csv_cols)
    for mime_type, file_paths in data.items():
        writer.writerow([mime_type, ";".join(file_paths)])

print(data)