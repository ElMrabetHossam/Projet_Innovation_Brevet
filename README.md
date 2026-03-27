# Patent AI – Analyseur d'Innovation & Brevets

Projet d'analyse de brevetabilité basé sur l'intelligence artificielle.
L'objectif est d'aider à évaluer le caractère nouveau d'une idée d'innovation à partir d'une base de brevets existants, en combinant NLP avancé, recherche sémantique vectorielle et un modèle mathématique d'exhaustion.

---

## 🎯 Objectif du projet

- Centraliser un corpus de brevets (PDF, DOCX) dans une base SQLite.
- Extraire automatiquement les **points d'innovation** et **mots-clés** pertinents (FR/EN, autres langues possibles).
- Représenter chaque point d'innovation comme un vecteur sémantique (Sentence-Transformers).
- Comparer une nouvelle idée aux brevets existants et calculer un **score de nouveauté**.
- Proposer une interface web moderne (Streamlit) pour tester des idées en temps réel.

---

## 🧩 Fonctionnalités principales

- Import automatique de documents de brevets depuis `data/7 - Patent`.
- Nettoyage et normalisation du texte (suppression des coupures, etc.).
- Détection de langue des brevets (via `langdetect`).
- Extraction **hybride** des mots-clés et points d'innovation :
  - TF-IDF
  - YAKE
  - KeyBERT
  - spaCy (FR/EN)
- Enregistrement structuré dans une base SQLite :
  - Table `Brevets`
  - Table `Points_Innovation`
  - Table `Mots_Cles`
- Moteur de similarité sémantique (`SentenceTransformer` – `all-MiniLM-L6-v2`).
- Calcul du score d'innovation à partir d'une formule inspirée d'un brevet d'exhaustion :
  \( S = 2^n - n - 1 - m \)
- Interface Streamlit :
  - Zone de saisie pour décrire une idée d'innovation.
  - Paramètres (sensibilité, nombre de brevets retournés).
  - Visualisations (score, antériorités, statistiques de domaines).

---

## 🏗️ Architecture générale

- `data/`
  - Dossiers de brevets bruts (`7 - Patent/…`).
  - Base SQLite : `brevets_innovation.db` (générée par les scripts).
- `src/`
  - `init_db.py` : création du schéma de base de données.
  - `extraction_text.py` : import et nettoyage de tous les brevets.
  - `traitement_nlp.py` : extraction hybride des points d'innovation / mots-clés.
  - `extraction_mots_cles_hybride.py` : logique d'extraction NLP avancée.
  - `moteur_innovation.py` : moteur d'IA (embeddings + calcul de nouveauté).
  - `app.py` : interface utilisateur Streamlit.
  - `schema_db.sql` : définition SQL du schéma.
- `ORDRE_EXECUTION.md` : guide d'exécution pas à pas des scripts.

---

## ✅ Prérequis

- Python 3.10+ (idéalement même version que l'environnement virtuel `env/`).
- Environnement virtuel activé (déjà présent dans le projet).
- Modules Python nécessaires, par exemple :
  - `streamlit`, `pandas`, `plotly`
  - `spacy`, `langdetect`, `yake`, `keybert`
  - `sentence-transformers`, `scipy`, etc.

Installez les dépendances (si un `requirements.txt` est présent) :

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
python -m spacy download fr_core_news_lg
```

> Voir également les indications dans `ORDRE_EXECUTION.md`.

---

## 🚀 Mise en route rapide

1. **Activer l'environnement virtuel** (déjà fait si vous travaillez depuis VS Code avec l'env du projet) :

```bash
cd Projet_Innovation_Brevet
env\Scripts\activate  # sous Windows PowerShell / CMD
```

2. **Initialiser la base de données** :

```bash
cd src
python init_db.py
```

3. **Importer et nettoyer les brevets** :

```bash
python extraction_text.py
```

4. **Lancer l'analyse NLP et remplir les tables Points_Innovation / Mots_Cles** :

```bash
python traitement_nlp.py
```

5. **Tester le moteur d'innovation en ligne de commande (optionnel)** :

```bash
python moteur_innovation.py
```

6. **Lancer l'interface web (Streamlit)** :

```bash
streamlit run app.py
```

Une page web s'ouvrira sur `http://localhost:8501` avec l'interface **Patent AI**.

---

## 🌐 Utilisation de l'interface Patent AI

- Décrivez votre idée d'innovation dans la zone de texte principale (niveau technique suffisant : composants, procédés, cas d'usage).
- Ajustez :
  - la **sensibilité IA** (seuil de similarité),
  - le **nombre de brevets** à afficher.
- Lancez l'analyse pour obtenir :
  - un **score de nouveauté** visuel,
  - la liste des points d'innovation similaires,
  - un verdict (idée inédite, combinée, ou risquée en termes d'antériorité).

---

## 🔁 Remise à zéro / Mise à jour des données

En cas d'ajout de nouveaux brevets dans `data/7 - Patent` ou si vous souhaitez repartir à zéro :

1. Supprimer le fichier de base :

```bash
rm data/brevets_innovation.db  # ou suppression manuelle sous Windows
```

2. Reprendre le pipeline à partir de :
   - `init_db.py`, puis
   - `extraction_text.py`,
   - `traitement_nlp.py`.

---

## 📌 Limites actuelles & pistes d'amélioration

- Qualité dépendante du corpus de brevets chargé.
- Seuils et paramètres d'extraction/embedding à ajuster selon les domaines.
- Interface actuellement centrée sur la saisie textuelle (possibles évolutions : upload de PDF, fiches projet, etc.).

---

## 👤 Auteurs / Contributeurs

Projet développé dans le cadre d'un module de **management / innovation & brevets** (année 2025‑2026).

Hossam El Mrabet
Version 01
