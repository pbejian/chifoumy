import time
import streamlit as st
import mediapipe as mp
#import cv2
import pandas as pd
import numpy as np
from PIL import Image
import numpy as np
# from chifoumy.ml_logic.registry import load_pipeline
# from chifoumy.ml_logic.params import LOCAL_IMAGES_PATH

#-------------------------------------------------------------------------------

def create_key():
    """
    Return an unique integer key (int) based on time in ms.
    """
    t = time.perf_counter_ns()
    #timestamp = time.strftime("%Y%m%d-%H%M%S")
    return t

#-------------------------------------------------------------------------------

def espace(n):
    """
    Cette fonction ne renvoie rien mais affiche n lignes vides
    dans une application streamlit.
    """
    for _ in range(n):
        st.write("")
    return None

#-------------------------------------------------------------------------------

def picture_to_df(picture):
    """
    This function take a picture of an hand as argument (created with
    streamlit.camera_input) and return a DataFrame which contains
    the mediapipe data of this hand.
    Do not forget to scale the dataframe after that
    """
    hand_list = []
    mp_hands = mp.solutions.hands
    with mp_hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5) as hands:
        img = Image.open(picture)
        img_array = np.array(img)
        # image = cv2.flip(img_array, 1)
        image = img_array
        results = hands.process(image)
        if not results.multi_hand_landmarks:
            return "No hand in this picture!"
        for hand_landmarks in results.multi_hand_landmarks:
            fingers = {}
            for i, finger in enumerate(hand_landmarks.landmark, start=1):
                fingers[f'{i}x'] = (finger.x)
                fingers[f'{i}y'] = (finger.y)
                fingers[f'{i}z'] = (finger.z)
            hand_list.append(fingers)
        return pd.DataFrame(hand_list)
