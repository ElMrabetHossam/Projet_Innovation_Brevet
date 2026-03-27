import os
import sqlite3
import warnings
import numpy as np

# Reduce noisy startup logs from transformers/sentence-transformers in Streamlit.
os.environ.setdefault('TRANSFORMERS_VERBOSITY', 'error')
os.environ.setdefault('TRANSFORMERS_NO_ADVISORY_WARNINGS', '1')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')

warnings.filterwarnings(
    'ignore',
    message=r"Accessing `__path__` from `\\.models\\..*`\\. Returning `__path__` instead\\. Behavior may be different and this alias will be removed in future versions\\.",
)
warnings.filterwarnings(
    'ignore',
    message=r'.*alias will be removed in future versions\\.',
)

from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
import time

try:
    from transformers.utils import logging as hf_logging

    hf_logging.set_verbosity_error()
except Exception:
    # If transformers logging API changes, keep app startup resilient.
    pass

class MoteurInnovation:
    """
    Moteur d'intelligence artificielle pour l'évaluation de la nouveauté brevetable.
    Combine recherche sémantique vectorielle et modèle mathématique d'exhaustion.
    """
    def __init__(self, db_path='../data/brevets_innovation.db'):
        self.db_path = db_path
        print("🚀 Initialisation du Moteur d'Innovation...")
        
        # Modèle d'embedding très rapide et performant pour la similarité sémantique
        print("   ⏳ Chargement du modèle vectoriel (Sentence-Transformers)...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Cache en mémoire
        self.points_innovation = []
        self.embeddings = None
        self._charger_base_de_donnees()

    def _charger_base_de_donnees(self):
        """Charge les points d'innovation et pré-calcule leurs vecteurs mathématiques (Embeddings)"""
        print("   ⏳ Vectorisation de la base de données de brevets...")
        start_time = time.time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # On récupère le point d'innovation et les infos de son brevet parent
        cursor.execute('''
            SELECT p.id_innovation, p.description_point, b.nom_fichier, b.domaine 
            FROM Points_Innovation p
            JOIN Brevets b ON p.id_brevet = b.id_brevet
        ''')
        resultats = cursor.fetchall()
        conn.close()

        if not resultats:
            print("   ⚠️ Attention : La table Points_Innovation est vide !")
            return

        textes_a_vectoriser = []
        for row in resultats:
            self.points_innovation.append({
                'id': row[0],
                'texte': row[1],
                'brevet_source': row[2],
                'domaine': row[3]
            })
            textes_a_vectoriser.append(row[1])

        # Transformation de tout le texte en vecteurs (matrice mathématique)
        self.embeddings = self.encoder.encode(textes_a_vectoriser)
        
        print(f"   ✓ {len(self.points_innovation)} points d'innovation vectorisés en {time.time() - start_time:.2f}s")
        print("✅ Moteur prêt !\n")

    def rechercher_similarite(self, idee_utilisateur, seuil_similarite=0.4, top_k=5):
        """
        Recherche les brevets les plus proches sémantiquement de l'idée de l'utilisateur.
        """
        # 1. On vectorise l'idée de l'utilisateur
        vecteur_idee = self.encoder.encode(idee_utilisateur)
        
        resultats_similaires = []
        
        # 2. On calcule la distance cosinus entre l'idée et TOUTE la base de données
        for idx, vecteur_brevet in enumerate(self.embeddings):
            # 1 - distance cosinus = similarité cosinus (score de 0 à 1)
            similarite = 1 - cosine(vecteur_idee, vecteur_brevet)
            
            if similarite >= seuil_similarite:
                point = self.points_innovation[idx]
                resultats_similaires.append({
                    'score': similarite,
                    'texte': point['texte'],
                    'source': point['brevet_source'],
                    'domaine': point['domaine']
                })
                
        # 3. Tri par score décroissant et limite au Top K
        resultats_similaires = sorted(resultats_similaires, key=lambda x: x['score'], reverse=True)[:top_k]
        return resultats_similaires

    def calculer_nouveaute_mathematique(self, resultats_similaires):
        """
        Implémente la formule du brevet LU_502887 : S = 2^n - n - 1 - m
        Évalue mathématiquement si l'idée est brevetable.
        """
        # n = nombre de points d'innovation existants similaires trouvés
        n = len(resultats_similaires)
        
        if n == 0:
            return {
                "S": -1, "n": 0, "m": 0, 
                "verdict": "Idée totalement inédite ! Aucun art antérieur trouvé. Brevetabilité maximale."
            }
        elif n == 1:
            return {
                "S": 0, "n": 1, "m": 0, 
                "verdict": "Idée nouvelle dans une certaine mesure, mais s'appuie sur 1 technologie existante. Fort potentiel d'innovation."
            }

        # Pour m, on regarde si les points similaires proviennent du MÊME brevet source (combinaison déjà existante)
        sources = [res['source'] for res in resultats_similaires]
        # Si un brevet apparaît plusieurs fois, ça veut dire que ses points sont déjà combinés
        m = len(sources) - len(set(sources)) 
        
        # Formule d'exhaustion
        S = (2**n) - n - 1 - m
        
        if S >= 1:
            verdict = f"Combinaison INÉDITE. Bien que les briques existent séparément, cette combinaison génère {S} nouvelles opportunités. Brevetable."
        else:
            verdict = "Risque d'antériorité ÉLEVÉ. Cette combinaison de technologies existe déjà dans les brevets identifiés."
            
        return {"S": S, "n": n, "m": m, "verdict": verdict}

    def evaluer_idee(self, description_idee):
        """Fonction principale qui génère le rapport complet d'innovation."""
        print(f"{'='*80}")
        print(f"🧠 ANALYSE D'INNOVATION : '{description_idee[:50]}...'")
        print(f"{'='*80}")
        
        # 1. Recherche
        similaires = self.rechercher_similarite(description_idee, seuil_similarite=0.3, top_k=4)
        
        if not similaires:
            print("\n🟢 RÉSULTAT : Aucune technologie similaire trouvée dans la base.")
            print("   L'idée semble totalement nouvelle !")
            return
            
        # 2. Affichage des antériorités
        print(f"\n🔍 ANTÉRIORITÉS DÉTECTÉES ({len(similaires)} points proches) :")
        for i, res in enumerate(similaires, 1):
            print(f"   [{i}] Score: {res['score']*100:.1f}% | Source: {res['source']}")
            print(f"       Extrait: {res['texte'][:100]}...\n")
            
        # 3. Calcul de nouveauté
        print(f"📐 CALCUL MATHÉMATIQUE DE NOUVEAUTÉ (Formule: S = 2^n - n - 1 - m)")
        math_eval = self.calculer_nouveaute_mathematique(similaires)
        print(f"   • Variables : n={math_eval['n']}, m={math_eval['m']}")
        print(f"   • Score d'innovation (S) : {math_eval['S']}")
        print(f"   • VERDICT : {math_eval['verdict']}")
        print(f"{'='*80}\n")

# ==========================================
# TEST DU MOTEUR
# ==========================================
if __name__ == '__main__':
    moteur = MoteurInnovation()
    
    # Test 1 : Une idée qui devrait matcher avec le brevet de collaboration (CN110675118A)
    idee_1 = "A software platform that uses artificial intelligence to help project members collaborate and track the progress of their business objectives in real-time."
    moteur.evaluer_idee(idee_1)
    
    # Test 2 : Une idée avec de la blockchain et des contrats intelligents (devrait matcher avec tes brevets Blockchain)
    idee_2 = "A decentralized system using blockchain to manage smart contracts and intellectual property rights for inventors."
    moteur.evaluer_idee(idee_2)
    
    # Test 3 : Une idée totalement folle (pour tester le cas où S = -1)
    idee_3 = "A biological quantum computer built from engineered DNA sequences to calculate the mass of dark matter."
    moteur.evaluer_idee(idee_3)