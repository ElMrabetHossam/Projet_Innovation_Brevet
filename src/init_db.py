import sqlite3
import os

# Chemins relatifs vers nos dossiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'data', 'brevets_innovation.db'))
SCHEMA_PATH = os.path.abspath(os.path.join(BASE_DIR, 'schema_db.sql'))

def initialiser_base_de_donnees():
    print("Création de la base de données SQLite...")
    
    # Connexion à la base (cela crée le fichier .db s'il n'existe pas)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Lecture du fichier SQL
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        
    # Exécution du script SQL
    cursor.executescript(schema_sql)
    
    # Sauvegarde et fermeture
    conn.commit()
    conn.close()
    
    print(f"Succès ! La base de données est prête dans : {DB_PATH}")

if __name__ == '__main__':
    initialiser_base_de_donnees()