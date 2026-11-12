# ===============================================================================

import hashlib
import pickle
import random
from pathlib import Path

import streamlit as st

from include import picture_to_df

# ===============================================================================
# Chemins : calculés à partir de ce fichier, pour que l'app se lance
# quel que soit le dossier courant.

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
IMAGES_DIR = BASE_DIR / "images"
RULES_IMAGE = BASE_DIR / "RPSLS.png"

MAX_SCORE = 3

# ===============================================================================
# Les gestes et les règles

NOMS = {0: "PIERRE", 1: "FEUILLE", 2: "CISEAUX", 3: "LÉZARD", 4: "SPOCK"}
LOGOS = {0: "logo_rock", 1: "logo_paper", 2: "logo_scissors",
         3: "logo_python", 4: "logo_spock"}

# (gagnant, perdant) : verbe
REGLES = {
    (0, 2): "écrase",
    (0, 3): "assomme",
    (1, 0): "recouvre",
    (1, 4): "réfute",
    (2, 1): "découpent",
    (2, 3): "décapitent",
    (3, 1): "mange",
    (3, 4): "empoisonne",
    (4, 0): "vaporise",
    (4, 2): "casse",
}


def scoring_spock(machine_gesture, user_gesture):
    """
    Renvoie "null", "user" ou "machine".
    0: pierre, 1: feuille, 2: ciseaux, 3: python, 4: spock
    """
    if user_gesture == machine_gesture:
        return "null"
    elif (user_gesture, machine_gesture) in REGLES:
        return "user"
    else:
        return "machine"


def description(machine_gesture, user_gesture):
    """
    Renvoie la phrase qui explique le résultat de la manche.
    """
    if user_gesture == machine_gesture:
        return "Match nul !"
    elif (user_gesture, machine_gesture) in REGLES:
        verbe = REGLES[(user_gesture, machine_gesture)]
        return f"Gagné : {NOMS[user_gesture]} {verbe} {NOMS[machine_gesture]}"
    else:
        verbe = REGLES[(machine_gesture, user_gesture)]
        return f"Perdu : {NOMS[machine_gesture]} {verbe} {NOMS[user_gesture]}"


def carte(titre, image, legende, score=None):
    """
    Affiche une colonne du résultat : titre, image, légende et score,
    tous centrés sur le même axe.
    """
    st.markdown(f"<h3 style='text-align: center;'>{titre}</h3>",
                unsafe_allow_html=True)
    with st.container(horizontal_alignment="center"):
        st.image(str(image), width=200)
    # &nbsp; garde une ligne vide quand il n'y a pas de légende,
    # pour que les trois colonnes restent à la même hauteur
    st.markdown(f"<p style='text-align: center; color: gray;'>"
                f"{legende or '&nbsp;'}</p>",
                unsafe_allow_html=True)
    if score is not None:
        st.markdown(f"<p style='text-align: center;'>Score<br>"
                    f"<span style='font-size: 2.5rem;'>{score}</span></p>",
                    unsafe_allow_html=True)

# ===============================================================================
# Chargement des modèles (une seule fois)

@st.cache_resource
def load_models():
    with open(MODELS_DIR / "scaler_spock.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open(MODELS_DIR / "model_spock.pkl", "rb") as f:
        model = pickle.load(f)
    return scaler, model

# ===============================================================================
# Scores : propres à chaque joueur (session), et non plus dans un fichier
# partagé par tous les visiteurs.

if "user_score" not in st.session_state:
    st.session_state.user_score = 0
    st.session_state.machine_score = 0
    st.session_state.last_photo = None
    st.session_state.last_round = None

# ===============================================================================

st.title(":primary[Chifoumy]", anchor=False)

st.subheader("Pierre-feuille-ciseaux-lézard-Spock", anchor=False)
#st.subheader(":primary[Pierre-feuille-ciseaux-lézard-Spock]", anchor=False)

st.write("""
Pierre, feuille, ciseaux, lézard et Spock ! Fais un geste devant ta webcam
et prends la photo : le modèle reconnaît ton geste, la machine joue au hasard.
Le premier à 3 points gagne la partie.
""")

# with st.expander("📜 Les règles"):
#     st.image(str(RULES_IMAGE), width=600)

with st.expander("📜 Les règles"):
    with st.container(horizontal_alignment="center"):
        st.image(str(RULES_IMAGE), width=500)

# -------------------------------------------------------------------------------

picture = st.camera_input("Ton geste")

if picture:
    # Une même photo ne doit compter qu'une seule fois (Streamlit relance
    # tout le script à chaque interaction).
    photo_id = hashlib.md5(picture.getvalue()).hexdigest()
    if photo_id != st.session_state.last_photo:
        st.session_state.last_photo = photo_id

        df = picture_to_df(picture)
        if df is None:
            st.session_state.last_round = None
            st.warning("Aucune main détectée sur la photo. Recommence !")
        else:
            # Nouvelle partie si la précédente était terminée
            if MAX_SCORE in (st.session_state.user_score,
                             st.session_state.machine_score):
                st.session_state.user_score = 0
                st.session_state.machine_score = 0

            scaler, model = load_models()
            X_new_scaled = scaler.transform(df)
            target = int(model.predict(X_new_scaled)[0])

            machine_play = random.randint(0, 4)

            result = scoring_spock(machine_play, target)
            if result == "machine":
                st.session_state.machine_score += 1
            elif result == "user":
                st.session_state.user_score += 1

            st.session_state.last_round = (target, machine_play)
            if st.session_state.user_score == MAX_SCORE:
                st.balloons()

# -------------------------------------------------------------------------------
# Affichage de la dernière manche

if st.session_state.last_round is not None:
    target, machine_play = st.session_state.last_round
    user_score = st.session_state.user_score
    machine_score = st.session_state.machine_score

    if machine_score == MAX_SCORE:
        image_vainqueur = "machine.png"
        text_vainqueur = "Machine"
    elif user_score == MAX_SCORE:
        image_vainqueur = "human.png"
        text_vainqueur = "Humain"
    else:
        image_vainqueur = "unknown.png"
        text_vainqueur = ""

    col1, col2, col3 = st.columns(3)
    with col1:
        carte("Humain", IMAGES_DIR / f"{LOGOS[target]}_human.png",
              NOMS[target], user_score)
    with col2:
        carte("Machine", IMAGES_DIR / f"{LOGOS[machine_play]}_machine.png",
              NOMS[machine_play], machine_score)
    with col3:
        carte("Vainqueur", IMAGES_DIR / image_vainqueur, text_vainqueur)

    st.subheader(description(machine_play, target))

    if machine_score == MAX_SCORE:
        st.error("➡️ Victoire de la machine ! Reprends une photo pour rejouer.")
    elif user_score == MAX_SCORE:
        st.success("➡️ Victoire de l'humain ! Reprends une photo pour rejouer.")
