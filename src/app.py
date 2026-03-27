import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from moteur_innovation import MoteurInnovation
import time

# Configuration de la page
st.set_page_config(
    page_title="Patent AI - Analyseur d'Innovation",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé pour rendre l'interface "très cool"
st.markdown("""
<style>
    /* Configuration globale */
    .main {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* En-tête stylisé avec dégradé */
    .header-container {
        padding: 2rem;
        border-radius: 15px;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
    }
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }

    /* Bouton d'analyse pulsant */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 12px;
        height: 60px;
        font-weight: 700;
        font-size: 1.2rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 14px rgba(16, 185, 129, 0.4);
    }

    /* Boîtes de résultat */
    .verdict-box {
        padding: 25px;
        border-radius: 15px;
        margin: 25px 0;
        font-size: 1.3em;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .success-verdict {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #064e3b;
        border-left: 8px solid #059669;
    }
    .warning-verdict {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        border-left: 8px solid #d97706;
    }
    .danger-verdict {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        border-left: 8px solid #dc2626;
    }

    /* Cartes de résultats */
    .result-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .result-card:hover {
        transform: scale(1.01);
        border-color: #3b82f6;
    }
    
    /* Zone de texte */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        font-size: 1.1rem;
        padding: 15px;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }

    /* Métriques sidebar */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #1e3a8a;
    }
</style>
""", unsafe_allow_html=True)

import os

# Initialisation du moteur (avec cache pour ne pas recharger à chaque interaction)
@st.cache_resource
def charger_moteur():
    try:
        # Utiliser un chemin absolu pour garantir le fonctionnement sur Streamlit Cloud
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(base_dir, '..', 'data', 'brevets_innovation.db'))
        return MoteurInnovation(db_path=db_path)
    except Exception as e:
        st.error(f"Erreur lors du chargement du moteur : {e}")
        return None

moteur = charger_moteur()

# Sidebar améliorée
with st.sidebar:
    st.markdown("### ⚙️ Control Center")
    
    # Métrique rapide
    if moteur and moteur.points_innovation:
        st.metric("Base de connaissance", f"{len(moteur.points_innovation)} pts")
    
    st.markdown("---")
    
    seuil_similarite = st.slider(
        "🎚️ Sensibilité IA",
        min_value=0.1, max_value=0.9, value=0.35,
        help="Ajustez la sensibilité de détection des similarités."
    )
    
    top_k = st.number_input(
        "📚 Nombre de brevets",
        min_value=1, max_value=20, value=5
    )
    
    st.markdown("---")
    st.markdown("### 📊 Répartition des données")
    if moteur and moteur.points_innovation:
        df_stats = pd.DataFrame(moteur.points_innovation)
        if not df_stats.empty and 'domaine' in df_stats.columns:
            domaines = df_stats['domaine'].value_counts()
            fig = px.pie(names=domaines.index, values=domaines.values, hole=0.6, color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=150)
            st.plotly_chart(fig, use_container_width=True)

    st.info("💡 **Astuce** : Décrivez votre idée comme si vous écriviez le résumé technique d'un brevet.")
    st.markdown("<div style='text-align: center; color: #6b7280; font-size: 0.8rem; margin-top: 20px;'>Patent AI Engine v2.0<br>Powered by BERT & TF-IDF</div>", unsafe_allow_html=True)

# En-tête principal personnalisé
st.markdown("""
<div class="header-container">
    <div class="header-title">Patent AI 🧠</div>
    <div class="header-subtitle">Système d'Analyse de Brevetabilité par Intelligence Artificielle</div>
</div>
""", unsafe_allow_html=True)

# Layout principal
col_input, col_info = st.columns([1.8, 1])

with col_input:
    st.markdown("### 📝 Décrivez votre innovation")
    description_idee = st.text_area(
        label="Description",
        label_visibility="collapsed",
        height=250,
        placeholder="Commencez par : 'Un système qui permet de...' ou 'Un dispositif innovant pour...'\n\nSoyez technique : mentionnez les composants, les procédés et ce qui rend votre idée unique."
    )
    
    # Espace pour centrer le bouton ou le rendre plus large
    st.markdown("<br>", unsafe_allow_html=True)
    analyser_btn = st.button("LANCER L'ANALYSE D'INNOVATION ⚡")

with col_info:
    st.markdown("### 🎯 Guide de rédaction")
    with st.expander("Comment obtenir un bon score ?", expanded=True):
        st.markdown("""
        1. **Précision** : Évitez les termes vagues ("meilleur", "super").
        2. **Technique** : Décrivez le *comment* ça marche.
        3. **Nouveauté** : Insistez sur ce qui n'existait pas avant.
        """)
        st.caption("Exemple : *Un drone utilisant un capteur LiDAR couplé à un réseau de neurones pour la cartographie souterraine autonome.*")

# Logique d'analyse
if analyser_btn:
    if not description_idee:
         st.warning("⚠️ Veuillez saisir une description avant de lancer l'analyse.")
    elif not moteur:
        st.error("❌ Le moteur d'IA n'est pas disponible. Vérifiez la base de données.")
    else:
        # Zone de résultats
        st.markdown("---")
        
        with st.spinner("🔄 Analyse sémantique vectorielle en cours..."):
            time.sleep(1.2) # Petit effet pour l'UX
            
            # Appel au moteur
            similaires = moteur.rechercher_similarite(description_idee, seuil_similarite=seuil_similarite, top_k=top_k)
            resultats_math = moteur.calculer_nouveaute_mathematique(similaires)
            
            score_S = resultats_math['S']
            n_similaires = resultats_math['n']
            
            # Layout des résultats
            res_col1, res_col2 = st.columns([1, 2])
            
            with res_col1:
                st.markdown("### 📈 Score de Nouveauté")
                # Jauge de score stylisée
                # Cas spécial : Si S = -1 (n=0, idée 100% nouvelle), c'est le TOP absolu !
                if score_S == -1:
                    gauge_color = "#3b82f6" # Bleu roi (Diamant)
                    gauge_value = 10 # On triche visuellement pour remplir la jauge au max
                    gauge_title = "MAX (Inédit)"
                else:
                    gauge_color = "#10b981" if score_S > 2 else "#f59e0b" if score_S >= 0 else "#ef4444"
                    gauge_value = score_S
                    gauge_title = str(score_S)
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = gauge_value,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    number = {'font': {'size': 50, 'color': gauge_color}, 'suffix': "" if score_S != -1 else " 💎"},
                    gauge = {
                        'axis': {'range': [-5, 10], 'tickwidth': 1},
                        'bar': {'color': gauge_color},
                        'bgcolor': "white",
                        'borderwidth': 0,
                        'steps': [
                            {'range': [-5, 0], 'color': '#fee2e2'},
                            {'range': [0, 2], 'color': '#fef3c7'},
                            {'range': [2, 10], 'color': '#d1fae5'}
                        ],
                    }
                ))
                fig_gauge.update_layout(height=250, margin=dict(t=30, b=10, l=30, r=30))
                st.plotly_chart(fig_gauge, use_container_width=True)
                
            with res_col2:
                st.markdown("### ⚖️ Verdict de l'IA")
                verdict_class = "success-verdict" if score_S > 0 else "danger-verdict"
                if score_S == 0: verdict_class = "warning-verdict"
                
                icon = "🌟" if score_S > 0 else "⚠️" if score_S == 0 else "⛔"
                
                st.markdown(f"""
                <div class="verdict-box {verdict_class}">
                    {icon} {resultats_math['verdict']}
                </div>
                """, unsafe_allow_html=True)
                
                col_m, col_n = st.columns(2)
                col_m.metric("Technologies similaires (n)", f"{resultats_math['n']}")
                col_n.metric("Combinaisons existantes (m)", f"{resultats_math['m']}")

            # Détail des similarités trouvées
            st.markdown("### 🔍 Analyse de l'Art Antérieur")
            
            if n_similaires == 0:
                st.success("✅ **Aucune antériorité directe trouvée !** Votre idée semble unique par rapport à la base de connaissance actuelle.")
                st.balloons()
            else:
                st.caption(f"Nous avons trouvé {n_similaires} brevets partageant des concepts similaires :")
                for i, res in enumerate(similaires):
                    score_pct = res['score']*100
                    color_bar = "red" if score_pct > 70 else "orange" if score_pct > 50 else "blue"
                    
                    with st.expander(f"📄 #{i+1} : {res['source']} ({score_pct:.1f}% de similarité)"):
                        st.markdown(f"**Domaine technologique :** `{res['domaine']}`")
                        st.markdown(f"**Passage identifié :**")
                        st.info(f"❝ {res['texte']} ❞")
                        st.progress(float(res['score']), text=f"Similitude sémantique : {score_pct:.1f}%")