"""
Main module for body tracking:
- obtains landmarks from the camera input
- sends OSC messages with right habnd and left hand to the receiver
  (e.g.SuperCollider)
- sends landmarks to visualization module.
"""

import argparse

import cv2
import mediapipe as mp
from pythonosc import udp_client


CLIENT_IP = '127.0.0.1'
CLIENT_PORT = 57120

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
pose_lmark = mp_holistic.PoseLandmark


def send_messages(client, body, _id=1):
    def _do_send_osc(joint, lmark):
        try:
            message = [joint, _id, lmark.x, lmark.y, lmark.z]
        except Exception as err:
            print("{}: {}".format(type(err).__name, err))
        else:
            client.send_message('/joint', message)

    # info: https://google.github.io/mediapipe/solutions/hands.html
    try:
        lmark = body.pose_landmarks.landmark
    except Exception as err:
        print("{}: {}".format(type(err).__name__, err))
        return

    _do_send_osc('head', lmark[pose_lmark.NOSE])
    _do_send_osc('neck', lmark[pose_lmark.NOSE])
    _do_send_osc('l_ear', lmark[pose_lmark.LEFT_EAR])
    _do_send_osc('r_ear', lmark[pose_lmark.RIGHT_EAR])
    _do_send_osc('r_shoulder', lmark[pose_lmark.RIGHT_SHOULDER])
    _do_send_osc('r_elbow', lmark[pose_lmark.RIGHT_ELBOW])
    _do_send_osc('l_shoulder', lmark[pose_lmark.LEFT_SHOULDER])
    _do_send_osc('l_elbow', lmark[pose_lmark.LEFT_ELBOW])
    _do_send_osc('r_hip', lmark[pose_lmark.RIGHT_HIP])
    _do_send_osc('r_knee', lmark[pose_lmark.RIGHT_KNEE])
    _do_send_osc('r_ankle', lmark[pose_lmark.RIGHT_ANKLE])
    _do_send_osc('r_foot', lmark[pose_lmark.RIGHT_FOOT_INDEX])
    _do_send_osc('l_hip', lmark[pose_lmark.LEFT_HIP])
    _do_send_osc('l_knee', lmark[pose_lmark.LEFT_KNEE])
    _do_send_osc('l_ankle', lmark[pose_lmark.LEFT_ANKLE])
    _do_send_osc('l_foot', lmark[pose_lmark.LEFT_FOOT_INDEX])

    # Alternative: body.right_hand_landmarks.landmark[mp_holistic.HandLandmark.MIDDLE_FINGER_MCP]
    _do_send_osc('r_hand', lmark[pose_lmark.RIGHT_WRIST])
    _do_send_osc('l_hand', lmark[pose_lmark.LEFT_WRIST])


def main(**kwargs):
    video_capture = kwargs.get("video_input", 0)
    flip = bool(kwargs.get("flip", 1))
    ip_address = kwargs.get("ip_address", CLIENT_IP)
    port = kwargs.get("port", CLIENT_PORT)

    client = udp_client.SimpleUDPClient(ip_address, port)

    is_file = False
    try:
        video_capture = int(video_capture)
    except ValueError:
        is_file = True

    skel_id = 1
    client.send_message('/new_skel', skel_id)

    cap = cv2.VideoCapture(video_capture)
    with mp_holistic.Holistic(min_detection_confidence=0.5,
                              min_tracking_confidence=0.5) \
                              as holistic:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")

                # If loading a video, use 'break' instead of 'continue'.
                if is_file:
                    break

                continue

            # Flip the image horizontally for a later selfie-view display.
            if flip:
                image = cv2.flip(image, 1)

            # Convert the image the BGR image to RGB.
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # To improve performance, optionally mark the image as not
            # writeable to pass by reference.
            image.flags.writeable = False
            results = holistic.process(image)

            # Draw landmark annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(image,
                                      results.face_landmarks,
                                      mp_holistic.FACEMESH_TESSELATION)
            mp_drawing.draw_landmarks(image,
                                      results.left_hand_landmarks,
                                      mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(image,
                                      results.right_hand_landmarks,
                                      mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(image,
                                      results.pose_landmarks,
                                      mp_holistic.POSE_CONNECTIONS)
            cv2.imshow('MediaPipe Holistic', image)
            send_messages(client, results, _id=skel_id)

            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='display')
    parser.add_argument('--input',
                        type=str,
                        required=True,
                        metavar='VIDEO_INPUT',
                        dest='video_input',
                        help='Video capture index (webcam, external cam, etc.) or mp4 filename')
    parser.add_argument('--flip',
                        type=int,
                        metavar='FLIP',
                        dest='flip',
                        default=1,
                        help='Flip the image horizontally for a selfie-view display (default)')
    parser.add_argument('--ipaddress',
                        type=str,
                        metavar='IP_ADDRESS',
                        dest='ip_address',
                        default=CLIENT_IP,
                        help='Client IP address.\nDefault: %(default)s')
    parser.add_argument('--port',
                        type=int,
                        metavar='IP_PORT',
                        dest='port',
                        default=CLIENT_PORT,
                        help='Client port.\nDefault: %(default)s')
    args = parser.parse_args()
    main(**vars(args))
