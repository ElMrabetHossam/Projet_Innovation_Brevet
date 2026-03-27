# 🚀 Guide d'Exécution du Projet Innovation & Brevets

Ce document explique l'ordre exact dans lequel exécuter les scripts Python pour faire fonctionner le système d'analyse de brevetabilité.

---

## 🛠️ Étape 0 : Pré-requis

Assurez-vous d'avoir installé toutes les dépendances :

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
python -m spacy download fr_core_news_lg
```

---

## 🏗️ Étape 1 : Initialisation de la Base de Données

Ce script crée le fichier `brevets_innovation.db` vide avec la structure nécessaire (tables `Brevets`, `Points_Innovation`, `Mots_Cles`).

```bash
cd src
python init_db.py
```

✅ **Résultat attendu :** Un message "Succès ! La base de données est prête".

---

## 📥 Étape 2 : Extraction et Importation des Documents

Ce script parcourt votre dossier `data/7 - Patent`, lit tous les fichiers PDF et Word (.docx), nettoie le texte (recolle les paragraphes coupés) et les insère dans la base de données.

```bash
python extraction_text.py
```

✅ **Résultat attendu :** Une liste de fichiers traités et le message "Terminé ! X documents insérés".

---

## 🧠 Étape 3 : Analyse Sémantique et Extraction de Mots-Clés (Le Cœur du Système)

Ce script est le plus long à exécuter. Il :

1. Détecte la langue de chaque brevet (FR, EN, ZH...).
2. Utilise une approche hybride (TF-IDF + YAKE + KeyBERT + spaCy) pour extraire les concepts clés.
3. Identifie les "points d'innovation" (phrases clés) et les stocke en base.

```bash
python traitement_nlp.py
```

✅ **Résultat attendu :** Une barre de progression par fichier, avec le résumé des points d'innovation trouvés.

---

## 🧪 Étape 4 : Test du Moteur d'Innovation (Ligne de Commande)

Ce script charge le modèle vectoriel (Sentence-Transformers) et teste la recherche de similarité sur 3 exemples d'idées prédéfinies.

```bash
python moteur_innovation.py
```

✅ **Résultat attendu :** Des scores de similarité et un verdict mathématique pour chaque idée testée.

---

## 🌐 Étape 5 : Lancement de l'Interface Utilisateur (Web App)

C'est l'étape finale ! Lancez l'interface graphique moderne pour interagir avec votre moteur.

```bash
streamlit run app.py
```

✅ **Résultat attendu :** Une page web s'ouvre dans votre navigateur (http://localhost:8501). Vous pouvez tester vos propres idées en temps réel !

---

## ⚠️ En cas d'erreur ou de mise à jour des données

Si vous ajoutez de nouveaux brevets dans le dossier `data` ou si vous voulez recommencer à zéro :

1. Supprimez le fichier `data/brevets_innovation.db`.
2. Reprenez depuis l'**Étape 1**.
