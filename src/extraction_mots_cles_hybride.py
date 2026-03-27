"""
Module d'extraction hybride de mots-clés pour brevets d'innovation
Combine plusieurs algorithmes avancés avec pondération intelligente
"""

import spacy
import yake
from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict, Counter
import re
import numpy as np


class ExtracteurMotsClesHybride:
    """
    Système d'extraction hybride combinant:
    - TF-IDF pour l'importance statistique
    - YAKE pour l'extraction sans supervision
    - KeyBERT pour l'analyse contextuelle (embeddings)
    - spaCy pour les entités nommées et chunks
    - Scoring pondéré intelligent
    """

    def __init__(self, langue="en"):
        """
        Initialise les extracteurs pour la langue spécifiée
        Langues supportées : 'en' (anglais), 'fr' (français)
        Pour les autres langues, utilise une configuration générique multilingue
        """
        self.langue = langue
        print(f"🚀 Chargement des modèles d'IA pour la langue : {langue}...")

        # Configuration des modèles Spacy selon la langue
        spacy_models = {
            "en": "en_core_web_lg",
            "fr": "fr_core_news_lg",
            "zh-cn": "zh_core_web_lg", # Chinois
            "ja": "ja_core_news_lg"    # Japonais
        }
        
        model_name = spacy_models.get(langue, "xx_ent_wiki_sm") # Multilingue par défaut
        
        try:
            self.nlp = spacy.load(model_name)
            print(f"   ✓ spaCy {model_name} chargé")
        except:
            print(f"   ⚠ {model_name} non trouvé. Tentative de chargement du modèle small...")
            try:
                # Fallback sur les modèles "sm" (small)
                fallback_name = model_name.replace("_lg", "_sm")
                self.nlp = spacy.load(fallback_name)
                print(f"   ✓ spaCy {fallback_name} chargé")
            except:
                print(f"   ⚠ Aucun modèle spaCy trouvé pour {langue}. L'extraction d'entités sera limitée.")
                self.nlp = None

        # YAKE (Yet Another Keyword Extractor)
        # YAKE supporte nativement beaucoup de langues via le code ISO 2 lettres
        yake_lang = langue.split('-')[0] if '-' in langue else langue
        self.yake_extractor = yake.KeywordExtractor(
            lan=yake_lang,
            n=3,
            dedupLim=0.7,
            dedupFunc='seqm',
            windowsSize=1,
            top=20
        )
        print(f"   ✓ YAKE initialisé ({yake_lang})")

        # KeyBERT avec modèle multilingue
        # 'paraphrase-multilingual-MiniLM-L12-v2' supporte 50+ langues dont FR, EN, ZH, JA...
        self.keybert_model = KeyBERT(model='paraphrase-multilingual-MiniLM-L12-v2')
        print("   ✓ KeyBERT Multilingue initialisé")

        # Blacklist multilingue enrichie
        self.blacklist = {
            # Anglais
            "invention", "method", "system", "device", "embodiment", "aspect",
            "summary", "problem", "implementation", "manner", "step", "process",
            "apparatus", "feature", "example", "manager", "objective", "member",
            "team", "action", "project", "event", "time", "stage", "progress",
            "goal", "indicator", "description", "requirement", "claim", "number",
            "people", "person", "information", "module", "following", "large",
            "new", "present", "datum", "data", "figure", "table", "plurality",
            "result", "object", "type", "form", "value", "level", "unit", "say",
            "said", "according", "thereof", "wherein", "thereby", "means",
            "includes", "comprising", "comprise", "include", "configured",
            "arrangement", "portion", "section", "part", "component", "element",
            
            # Français
            "invention", "méthode", "système", "dispositif", "mode", "réalisation",
            "aspect", "résumé", "problème", "mise", "œuvre", "étape", "procédé",
            "appareil", "caractéristique", "exemple", "gestionnaire", "objectif",
            "membre", "équipe", "action", "projet", "événement", "temps", "phase",
            "progrès", "but", "indicateur", "description", "exigence", "revendication",
            "nombre", "personne", "information", "module", "suivant", "grand",
            "nouveau", "présent", "donnée", "données", "figure", "tableau", "plusieurs",
            "résultat", "objet", "type", "forme", "valeur", "niveau", "unité", "dire",
            "dit", "selon", "celui-ci", "dans", "lequel", "moyen", "moyens",
            "inclut", "comprenant", "comprend", "inclure", "configuré",
            "agencement", "partie", "section", "composant", "élément",
            "caractérisé", "permettant", "destiné"
        }

        print("✅ Tous les modèles sont prêts!\n")


    def extraire_avec_tfidf(self, texte, top_n=15):
        """
        Extraction TF-IDF : identifie les termes statistiquement importants
        """
        try:
            if not self.nlp:
                return {} # Pas de Spacy = pas de lemmatisation efficace

            # Tokenisation avec spaCy pour avoir des n-grams intelligents
            doc = self.nlp(texte[:50000])  # Limite pour performance

            # Création de n-grams (1 à 3 mots)
            ngrams = []
            
            # Utilisation de noun_chunks seulement si disponible (anglais/français/allemand...)
            if doc.has_annotation("DEP"):
                for chunk in doc.noun_chunks:
                    clean_chunk = " ".join([token.lemma_.lower() for token in chunk
                                           if not token.is_stop and token.is_alpha])
                    if clean_chunk and len(clean_chunk) > 3:
                        ngrams.append(clean_chunk)
            
            # Si pas assez de chunks ou langue sans noun_chunks (ex: chinois parfois), utiliser des tokens simples
            if len(ngrams) < 10:
                ngrams.extend([token.lemma_.lower() for token in doc
                              if not token.is_stop and token.is_alpha and len(token.lemma_) > 2])

            # Vectorisation TF-IDF
            if len(ngrams) < 2:
                return {}

            vectorizer = TfidfVectorizer(max_features=top_n, ngram_range=(1, 3))
            tfidf_matrix = vectorizer.fit_transform([" ".join(ngrams)])

            # Récupération des scores
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            # Dictionnaire {mot: score}
            tfidf_keywords = {feature_names[i]: scores[i] for i in range(len(scores)) if scores[i] > 0}

            return tfidf_keywords
        except Exception as e:
            print(f"   ⚠ Erreur TF-IDF: {e}")
            return {}


    def extraire_avec_yake(self, texte, top_n=15):
        """
        Extraction YAKE : algorithme sans supervision, efficace pour textes techniques
        """
        try:
            keywords = self.yake_extractor.extract_keywords(texte[:50000])
            # YAKE renvoie (mot, score) où score plus bas = meilleur
            # On inverse pour avoir score élevé = meilleur
            yake_keywords = {kw: 1/(score + 0.0001) for kw, score in keywords[:top_n]}
            return yake_keywords
        except Exception as e:
            print(f"   ⚠ Erreur YAKE: {e}")
            return {}


    def extraire_avec_keybert(self, texte, top_n=15):
        """
        Extraction KeyBERT : utilise les embeddings pour capturer le contexte sémantique
        """
        try:
            keywords = self.keybert_model.extract_keywords(
                texte[:50000],
                keyphrase_ngram_range=(1, 3),
                stop_words='english',
                top_n=top_n,
                diversity=0.5  # Diversité pour éviter les redondances
            )
            # KeyBERT renvoie (mot, score de similarité)
            keybert_keywords = {kw: score for kw, score in keywords}
            return keybert_keywords
        except Exception as e:
            print(f"   ⚠ Erreur KeyBERT: {e}")
            return {}


    def extraire_avec_spacy_entities(self, texte):
        """
        Extraction des entités nommées techniques avec spaCy
        """
        try:
            if not self.nlp:
                return {}
                
            doc = self.nlp(texte[:50000])
            entities = {}

            # On cible les entités techniques pertinentes
            # Labels peuvent varier selon le modèle/langue, on garde les plus courants
            relevant_labels = {'PRODUCT', 'ORG', 'GPE', 'FAC', 'NORP', 'LOC', 'WORK_OF_ART', 'EVENT'}

            for ent in doc.ents:
                if ent.label_ in relevant_labels:
                    clean_ent = ent.text.lower().strip()
                    # Filtre longueur minimale (adapté pour chinois/japonais où les mots sont courts)
                    min_len = 1 if self.langue in ['zh-cn', 'ja', 'ko'] else 3
                    
                    if len(clean_ent) > min_len:
                        entities[clean_ent] = entities.get(clean_ent, 0) + 1

            # Normalisation des scores (fréquence)
            if entities:
                max_freq = max(entities.values())
                entities = {k: v/max_freq for k, v in entities.items()}

            return entities
        except Exception as e:
            print(f"   ⚠ Erreur spaCy entities: {e}")
            return {}


    def filtrer_mots_cles(self, mot_cle):
        """
        Filtre intelligent pour éliminer les mots non pertinents
        """
        # Nettoyage basique
        mot_cle = mot_cle.strip().lower()

        # Règles de filtrage
        if len(mot_cle) < 3:
            return False

        # Vérifie si le mot contient un élément de la blacklist
        mots_dans_cle = set(mot_cle.split())
        if mots_dans_cle.intersection(self.blacklist):
            return False

        # Rejette les mots purement numériques ou avec trop de chiffres
        if re.match(r'^\d+$', mot_cle) or sum(c.isdigit() for c in mot_cle) > len(mot_cle) * 0.5:
            return False

        # Rejette les mots avec des caractères spéciaux excessifs
        if sum(not c.isalnum() and not c.isspace() for c in mot_cle) > 2:
            return False

        return True


    def combiner_scores(self, tfidf_kw, yake_kw, keybert_kw, spacy_entities):
        """
        Combine les scores de tous les extracteurs avec pondération intelligente

        Pondération optimisée pour les brevets:
        - TF-IDF: 20% (importance statistique de base)
        - YAKE: 25% (bon pour termes techniques)
        - KeyBERT: 35% (meilleur pour contexte sémantique)
        - spaCy Entities: 20% (entités techniques spécifiques)
        """
        scores_combines = defaultdict(float)

        # Pondération
        poids = {
            'tfidf': 0.20,
            'yake': 0.25,
            'keybert': 0.35,
            'entities': 0.20
        }

        # Normalisation de chaque extracteur (score max = 1)
        def normaliser(dico):
            if not dico:
                return {}
            max_score = max(dico.values()) if dico else 1
            return {k: v/max_score for k, v in dico.items()}

        tfidf_norm = normaliser(tfidf_kw)
        yake_norm = normaliser(yake_kw)
        keybert_norm = normaliser(keybert_kw)
        entities_norm = normaliser(spacy_entities)

        # Combinaison pondérée
        for mot, score in tfidf_norm.items():
            if self.filtrer_mots_cles(mot):
                scores_combines[mot] += score * poids['tfidf']

        for mot, score in yake_norm.items():
            if self.filtrer_mots_cles(mot):
                scores_combines[mot] += score * poids['yake']

        for mot, score in keybert_norm.items():
            if self.filtrer_mots_cles(mot):
                scores_combines[mot] += score * poids['keybert']

        for mot, score in entities_norm.items():
            if self.filtrer_mots_cles(mot):
                scores_combines[mot] += score * poids['entities']

        # Tri par score décroissant
        scores_tries = sorted(scores_combines.items(), key=lambda x: x[1], reverse=True)

        return scores_tries


    def extraire_mots_cles_optimaux(self, texte, top_n=10):
        """
        Méthode principale : extraction hybride optimale

        Args:
            texte: Le texte du brevet
            top_n: Nombre de mots-clés à retourner

        Returns:
            Liste de tuples (mot_cle, score) triée par pertinence
        """
        if not texte or len(texte) < 50:
            return []

        print("   🔍 Extraction TF-IDF...")
        tfidf_kw = self.extraire_avec_tfidf(texte)

        print("   🔍 Extraction YAKE...")
        yake_kw = self.extraire_avec_yake(texte)

        print("   🔍 Extraction KeyBERT...")
        keybert_kw = self.extraire_avec_keybert(texte)

        print("   🔍 Extraction Entités spaCy...")
        entities = self.extraire_avec_spacy_entities(texte)

        print("   🧮 Combinaison et scoring...")
        resultats = self.combiner_scores(tfidf_kw, yake_kw, keybert_kw, entities)

        # Retourne les top_n meilleurs
        return resultats[:top_n]


    def extraire_points_innovation_et_mots_cles(self, texte, max_points=5, mots_par_point=8):
        """
        Extrait les points d'innovation avec leurs mots-clés optimisés
        Support multilingue (FR/EN)
        """
        if not texte or len(texte) < 50:
            return []
            
        points_innovation = []

        # Utilisation de phrases clés selon la langue
        mots_declencheurs = []
        if self.langue == 'fr':
            mots_declencheurs = [
                "comprend", "inclut", "consiste en", "caractérisé par", "caractérisée par",
                "nouveau", "innovant", "dans lequel", "permet de", "permet d'",
                "améliore", "fournit", "revendication", "invention", "dispositif"
            ]
        elif self.langue == 'en':
            mots_declencheurs = [
                "comprises", "includes", "configured to", "consists of",
                "novel", "innovative", "characterized by", "wherein",
                "provides", "enables", "achieves", "improves"
            ]
        else:
            # Pour les autres langues (ex: asiatiques), on prend tout ou on se base sur la ponctuation
            # Si pas de mots déclencheurs définis, on considère toutes les phrases longues comme candidates
            pass

        if self.nlp:
            doc = self.nlp(texte[:100000])
            sentences = doc.sents
        else:
            # Fallback simple si pas de Spacy (découpage par points/retours ligne)
            import re
            sentences_text = re.split(r'[.!?\n]+', texte[:100000])
            # On simule des objets phrases
            class SimpleSentence:
                def __init__(self, t): self.text = t
            sentences = [SimpleSentence(s) for s in sentences_text if len(s) > 20]

        # Extraction des phrases clés (points d'innovation)
        for phrase in sentences:
            phrase_texte = phrase.text.strip().lower()
            
            # Si on a des mots déclencheurs, on filtre. Sinon on prend les phrases significatives
            est_pertinent = False
            if mots_declencheurs:
                if any(mot in phrase_texte for mot in mots_declencheurs):
                    est_pertinent = True
            else:
                # Pour les langues sans liste (ex: chinois), on prend les phrases longues (>10 chars)
                if len(phrase_texte) > 10: 
                    est_pertinent = True

            if est_pertinent:
                # Extraction des mots-clés pour CETTE phrase spécifique
                mots_cles = self.extraire_mots_cles_optimaux(phrase.text, top_n=mots_par_point)

                if mots_cles:  # Seulement si des mots-clés pertinents sont trouvés
                    points_innovation.append({
                        'phrase': phrase.text.strip(),
                        'mots_cles': mots_cles
                    })

            if len(points_innovation) >= max_points:
                break
        
        # Si aucune phrase "spéciale" trouvée (peut arriver sur des textes courts ou mal formés),
        # on prend les premières phrases
        if not points_innovation and sentences:
             for i, phrase in enumerate(sentences):
                if i >= max_points: break
                if len(phrase.text) > 30:
                    mots_cles = self.extraire_mots_cles_optimaux(phrase.text, top_n=mots_par_point)
                    if mots_cles:
                        points_innovation.append({
                            'phrase': phrase.text.strip(),
                            'mots_cles': mots_cles
                        })

        return points_innovation
