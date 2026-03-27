import sqlite3

DB_PATH = '../data/brevets_innovation.db'

def nettoyer_base():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🧹 Nettoyage des anciennes analyses...")
    cursor.execute("DELETE FROM Mots_Cles")
    cursor.execute("DELETE FROM Points_Innovation")
    cursor.execute("DELETE FROM Brevets")
    
    conn.commit()
    conn.close()
    print("✅ Tables vidées ! La base est prête pour la nouvelle IA.")

if __name__ == '__main__':
    nettoyer_base()