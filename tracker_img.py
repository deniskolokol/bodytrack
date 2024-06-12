"""
Body tracker for static images.
"""

import argparse

from operator import itruediv
import os
from tkinter import N
from unittest import result

import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic


def open_img(fname):
    result = {
        'image': None,
        'file': None,
        'height': 0,
        'width': 0,
        'error': None,
        }
    result.update(file=os.path.abspath(fname))
    result.update(image=cv2.imread(result['file']))
    try:
        height, width, _ = result['image'].shape
    except AttributeError:
        result.update(error='Cannot open/read file: check file path/integrity')
    else:
        result.update(height=height, width=width)

    return result


def main(**kwargs):
    with mp_holistic.Holistic(static_image_mode=True, model_complexity=2) as holistic:
        for idx, img_file in enumerate(kwargs['files']):
            image_data = open_img(img_file)
            if image_data['error']:
                print('ERROR: {error}\nFILE: {file}'.format(**image_data))
                continue

            # Convert the BGR image to RGB before processing.
            results = holistic.process(cv2.cvtColor(
                image_data['image'], cv2.COLOR_BGR2RGB))

            if results.pose_landmarks:
                print(
                    f'Nose coordinates: ('
                    f'{results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].x}, '
                    f'{results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].y}, '
                    f'{results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].z})'
                )

            # Draw pose, left and right hands, and face landmarks on the image.
            annotated_image = image_data['image'].copy()
            mp_drawing.draw_landmarks(annotated_image,
                                      results.face_landmarks,
                                      mp_holistic.FACEMESH_TESSELATION)
            mp_drawing.draw_landmarks(annotated_image,
                                      results.left_hand_landmarks,
                                      mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(annotated_image,
                                      results.right_hand_landmarks,
                                      mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(annotated_image,
                                      results.pose_landmarks,
                                      mp_holistic.POSE_CONNECTIONS)

            img_path = os.path.dirname(image_data['file'])
            fname, ext = os.path.splitext(os.path.basename(image_data['file']))
            new_path = f'{img_path}/{fname}_annotated{ext}'
            cv2.imwrite(new_path, annotated_image)
            print(f'INFO: annotated image {new_path}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='display')
    parser.add_argument(nargs='+', dest='files', help='<Required> picture file(s)')
    args = parser.parse_args()
    main(**vars(args))
