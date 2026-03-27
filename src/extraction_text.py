import os
import sqlite3
from docx import Document
import pdfplumber

# Chemins relatifs
DB_PATH = '../data/brevets_innovation.db'
PATENT_DIR = '../data/7 - Patent' 

def extraire_texte_docx(chemin_fichier):
    """Ouvre un fichier Word et extrait tout son texte."""
    try:
        doc = Document(chemin_fichier)
        texte_complet = []
        for para in doc.paragraphs:
            if para.text.strip():
                texte_complet.append(para.text.strip())
        return '\n'.join(texte_complet)
    except Exception as e:
        print(f"Erreur Word pour {chemin_fichier}: {e}")
        return None

def extraire_texte_pdf(chemin_fichier):
    """Ouvre un fichier PDF et extrait tout son texte en recollant les lignes."""
    try:
        texte_complet = []
        with pdfplumber.open(chemin_fichier) as pdf:
            for page in pdf.pages:
                texte_page = page.extract_text()
                if texte_page:
                    # Correction des césures de ligne PDF : remplacer \n par espace si ce n'est pas une fin de paragraphe
                    # On assume qu'un vrai paragraphe finit par . ou : ou ! ou ?
                    lignes = texte_page.split('\n')
                    texte_propre = ""
                    for ligne in lignes:
                        ligne = ligne.strip()
                        if not ligne: continue
                        
                        if texte_propre and not texte_propre.endswith(('.', ':', '!', '?', ';')):
                            texte_propre += " " + ligne
                        else:
                            texte_propre += "\n" + ligne
                            
                    texte_complet.append(texte_propre.strip())
        return '\n'.join(texte_complet)
    except Exception as e:
        print(f"Erreur PDF pour {chemin_fichier}: {e}")
        return None

def peupler_base_de_donnees():
    print("Démarrage de l'extraction des documents (Word et PDF)...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    compteur = 0
    
    for dossier_racine, sous_dossiers, fichiers in os.walk(PATENT_DIR):
        for fichier in fichiers:
            # On vérifie si c'est un Word ou un PDF
            if fichier.endswith('.docx') or fichier.endswith('.pdf'):
                chemin_complet = os.path.join(dossier_racine, fichier)
                domaine = os.path.basename(dossier_racine)
                
                # Déduction du type de document
                if 'Description' in fichier:
                    type_doc = 'Description'
                elif 'Revendications' in fichier:
                    type_doc = 'Revendications'
                elif fichier.endswith('.pdf'):
                    type_doc = 'PDF Complet' # Les PDF contiennent souvent tout
                else:
                    type_doc = 'Autre'
                
                # Vérification si le fichier existe déjà dans la base pour éviter les doublons
                cursor.execute("SELECT 1 FROM Brevets WHERE nom_fichier = ?", (fichier,))
                if cursor.fetchone():
                    continue # On passe au fichier suivant s'il est déjà là
                
                print(f"Traitement de : {fichier}...")
                
                # Extraction selon l'extension
                if fichier.endswith('.docx'):
                    contenu = extraire_texte_docx(chemin_complet)
                else:
                    contenu = extraire_texte_pdf(chemin_complet)
                
                # Insertion si du texte a été trouvé
                if contenu:
                    try:
                        cursor.execute('''
                            INSERT INTO Brevets (nom_fichier, domaine, type_document, contenu_texte)
                            VALUES (?, ?, ?, ?)
                        ''', (fichier, domaine, type_doc, contenu))
                        compteur += 1
                    except sqlite3.Error as e:
                        print(f"Erreur SQL pour {fichier}: {e}")
                        
    conn.commit()
    conn.close()
    print(f"\n✅ Terminé ! {compteur} nouveaux documents ont été insérés dans la base de données.")

if __name__ == '__main__':
    peupler_base_de_donnees()