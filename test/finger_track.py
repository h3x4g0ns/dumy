import cv2
import os
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0)
MOMENTUM = 0.8
DEBUG = os.environ.get("DEBUG", None)
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
BLANK = np.zeros((HEIGHT, WIDTH, 3))

def ramp(prev, point):
    if not prev:
        return point
    else:
        return int(MOMENTUM*prev[0]+(1-MOMENTUM)*point[0]), int(MOMENTUM*prev[1]+(1-MOMENTUM)*point[1])

with mp_hands.Hands(
    min_detection_confidence=0.75,
    min_tracking_confidence=0.5) as hands:

    # ramping function for smoothing
    prev_left, prev_right = None, None
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image = cv2.flip(image, 1)
        if not DEBUG:
            image.flags.writeable = False # performance
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not DEBUG:
            image = BLANK

        # ripping joints and handedness
        if results.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                hand_type = results.multi_handedness[i].classification[0].label
                j = 8
                pt = mp_drawing._normalized_to_pixel_coordinates(
                        hand_landmarks.landmark[j].x, hand_landmarks.landmark[j].y, WIDTH, HEIGHT)
                if pt:
                    if hand_type == "Left":
                        pt = prev_left = ramp(prev_left, pt) 
                        color = (255, 0, 0)
                    else:
                        pt = prev_right = ramp(prev_right, pt)
                        color = (0, 255, 0)
                    cv2.circle(image, pt, 5, color, -1)

        cv2.imshow('Index finger Tracking', image)
        if cv2.waitKey(5) == 27:
            break

cap.release()

