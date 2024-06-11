"""
Body tracker for static images.
"""

from operator import itruediv
import os

import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# For static images
IMAGE_FILES = [
    "./media/example.jpg",
]
with mp_holistic.Holistic(static_image_mode=True, model_complexity=2) as holistic:
    for idx, img_file in enumerate(IMAGE_FILES):
        image = cv2.imread(img_file)
        image_height, image_width, _ = image.shape
        # Convert the BGR image to RGB before processing.
        results = holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if results.pose_landmarks:
            print(
                f'Nose coordinates: ('
                f'{results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].x}, '
                f'{results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].y}, '
                f'{results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].z})'
            )

        # Draw pose, left and right hands, and face landmarks on the image.
        annotated_image = image.copy()
        mp_drawing.draw_landmarks(
            annotated_image, results.face_landmarks, mp_holistic.FACE_CONNECTIONS)
        mp_drawing.draw_landmarks(
            annotated_image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_drawing.draw_landmarks(
            annotated_image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_drawing.draw_landmarks(
            annotated_image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

        img_path = os.path.dirname(os.path.abspath(img_file))
        img_filename, img_ext = os.path.splitext(os.path.basename(img_file))
        cv2.imwrite(f'{img_path}/{img_filename}_annotated{img_ext}', annotated_image)
