import numpy as np
import pandas as pd
import mediapipe as mp
import streamlit as st
from PIL import Image


@st.cache_resource
def get_hands_detector():
    """
    Crée une seule fois le détecteur de mains MediaPipe
    (il est ensuite réutilisé à chaque photo).
    """
    return mp.solutions.hands.Hands(static_image_mode=True,
                                    max_num_hands=2,
                                    min_detection_confidence=0.5)


def picture_to_df(picture):
    """
    Prend une photo de main (créée avec st.camera_input) et renvoie
    un DataFrame contenant les 21 points MediaPipe de la main
    (63 colonnes : 1x, 1y, 1z, ..., 21x, 21y, 21z).
    Renvoie None si aucune main n'est détectée.
    Ne pas oublier de mettre le DataFrame à l'échelle ensuite.
    """
    image = np.array(Image.open(picture).convert("RGB"))
    results = get_hands_detector().process(image)
    if not results.multi_hand_landmarks:
        return None
    hand_list = []
    for hand_landmarks in results.multi_hand_landmarks:
        fingers = {}
        for i, finger in enumerate(hand_landmarks.landmark, start=1):
            fingers[f'{i}x'] = finger.x
            fingers[f'{i}y'] = finger.y
            fingers[f'{i}z'] = finger.z
        hand_list.append(fingers)
    return pd.DataFrame(hand_list)
