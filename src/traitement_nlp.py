import sqlite3
from langdetect import detect, DetectorFactory
from extraction_mots_cles_hybride import ExtracteurMotsClesHybride

# Pour avoir des résultats de détection de langue constants
DetectorFactory.seed = 0

DB_PATH = '../data/brevets_innovation.db'

def analyser_brevets():
    """
    Analyse avancée des brevets avec extraction hybride de mots-clés
    Combine TF-IDF + YAKE + KeyBERT + spaCy pour des résultats optimaux
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # On récupère tous les brevets qui n'ont pas encore de points d'innovation
    cursor.execute('''
        SELECT id_brevet, nom_fichier, contenu_texte
        FROM Brevets
        WHERE id_brevet NOT IN (SELECT DISTINCT id_brevet FROM Points_Innovation)
    ''')
    brevets = cursor.fetchall()

    print(f"\n{'='*70}")
    print(f"📊 {len(brevets)} brevets trouvés à analyser")
    print(f"{'='*70}\n")

    # Initialisation des extracteurs (cache pour ne pas recharger les modèles à chaque fichier)
    extracteurs_cache = {}

    for idx, (id_brevet, nom_fichier, texte) in enumerate(brevets, 1):
        # 1. Vérification de base
        if not texte or len(texte) < 50:
            print(f"[{idx}/{len(brevets)}] ⏭️  Ignoré (texte trop court) : {nom_fichier}")
            continue

        # 2. Détection de la langue
        langue = 'en' # Par défaut
        try:
            langue = detect(texte)
            print(f"[{idx}/{len(brevets)}] 🌍 Langue détectée : {langue} pour {nom_fichier}")
        except:
            print(f"[{idx}/{len(brevets)}] ⚠️  Erreur détection langue, utilisation par défaut (en) : {nom_fichier}")
        
        # 3. Récupération ou création de l'extracteur pour cette langue
        if langue not in extracteurs_cache:
            print(f"   ⚙️ Initialisation du moteur pour la langue : {langue}")
            extracteurs_cache[langue] = ExtracteurMotsClesHybride(langue=langue)
        
        extracteur = extracteurs_cache[langue]

        print(f"\n{'─'*70}")
        print(f"[{idx}/{len(brevets)}] 🔬 Analyse hybride ({langue}) : {nom_fichier}")
        print(f"{'─'*70}")

        # 4. EXTRACTION HYBRIDE : Points d'innovation + Mots-clés
        points_innovation = extracteur.extraire_points_innovation_et_mots_cles(
            texte,
            max_points=5,      # Maximum 5 points d'innovation
            mots_par_point=8   # 8 mots-clés par point
        )

        points_inseres = 0
        mots_inseres = 0

        # 4. Insertion dans la base de données
        for point in points_innovation:
            # Insertion du point d'innovation
            cursor.execute(
                "INSERT INTO Points_Innovation (id_brevet, description_point) VALUES (?, ?)",
                (id_brevet, point['phrase'])
            )
            id_innovation = cursor.lastrowid
            points_inseres += 1

            # Insertion des mots-clés avec leur score
            for mot_cle, score in point['mots_cles']:
                cursor.execute(
                    "INSERT INTO Mots_Cles (id_innovation, mot_cle) VALUES (?, ?)",
                    (id_innovation, mot_cle)
                )
                mots_inseres += 1

            # Affichage des mots-clés trouvés
            mots_affichage = ", ".join([f"{mot} ({score:.2f})" for mot, score in point['mots_cles'][:5]])
            print(f"   ✓ Point {points_inseres}: {mots_affichage}...")

        print(f"   {'─'*66}")
        print(f"   📝 Résumé: {points_inseres} points, {mots_inseres} mots-clés insérés")

        # Commit après chaque brevet pour éviter les pertes
        conn.commit()

    conn.close()

    print(f"\n{'='*70}")
    print(f"✅ ANALYSE TERMINÉE !")
    print(f"{'='*70}")
    print(f"📊 Les tables Points_Innovation et Mots_Cles sont maintenant")
    print(f"   remplies avec des données de HAUTE QUALITÉ extraites par")
    print(f"   le système hybride (TF-IDF + YAKE + KeyBERT + spaCy)")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    analyser_brevets()
