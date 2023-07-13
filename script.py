import cv2
import os
import serial
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0)
MOMENTUM = 0.8
DEBUG = os.environ.get("DEBUG", None)
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

def ramp(prev, point):
    if not prev:
        return point
    else:
        return int(MOMENTUM*prev[0]+(1-MOMENTUM)*point[0]), int(MOMENTUM*prev[1]+(1-MOMENTUM)*point[1])
    
def process(hands, ser):
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

        # ripping joints and handedness
        if results.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                hand_type = results.multi_handedness[i].classification[0].label
                j = 8
                pt = mp_drawing._normalized_to_pixel_coordinates(
                        hand_landmarks.landmark[j].x, hand_landmarks.landmark[j].y, WIDTH, HEIGHT)
                if pt:
                    if hand_type == "Left":
                        prev_left = ramp(prev_left, pt) 
                    else:
                        prev_right = ramp(prev_right, pt)

        # TODO: caculating joint angles with inv kinematics
        x = y = z = 0

        # TODO: write destination to serial
        ser.write(f"{x} {y} {z}\n".encode())

        if cv2.waitKey(5) == 27:
            break

def main():
    with mp_hands.Hands(
        min_detection_confidence=0.75,
        min_tracking_confidence=0.5) as hands:

        # start processing loop
        ser = serial.Serial('/dev/ttyUSB0', 9600)  # Replace '/dev/ttyUSB0' with the appropriate serial port
        process(hands, ser)
    cap.release()
    ser.close()

if __name__ == "__main__":
    main()
