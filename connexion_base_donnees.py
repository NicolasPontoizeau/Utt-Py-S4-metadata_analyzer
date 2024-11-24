import sqlite3

# Connexion à la base de données (ou création de celle-ci si elle n'existe pas)
conn = sqlite3.connect('example.db')  # Remplace par le chemin vers ta base de données SQLite

# Créer un curseur pour interagir avec la base de données
cursor = conn.cursor()

# Créer une table si elle n'existe pas
cursor.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    age INTEGER NOT NULL)''')

# Insérer des données dans la table
cursor.execute("INSERT INTO utilisateurs (nom, age) VALUES (?, ?)", ('Alice', 30))

# Sauvegarder les changements (commit)
conn.commit()

# Lire des données
cursor.execute("SELECT * FROM utilisateurs")
for row in cursor.fetchall():
    print(row)

# Fermer la connexion à la base de données
conn.close()
