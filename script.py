import cv2
import os
import serial
import mediapipe as mp
import numpy as np
import freenect

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
MOMENTUM = 0.8
DEBUG = os.environ.get("DEBUG", None)
WIDTH = 1280
HEIGHT = 720

# smoothing function from t to t+1
def ramp(prev, point):
    if not prev:
        return point
    else:
        return int(MOMENTUM*prev[0]+(1-MOMENTUM)*point[0]), int(MOMENTUM*prev[1]+(1-MOMENTUM)*point[1])

# Function to get the depth data from the Kinect sensor
def get_depth():
    depth = freenect.sync_get_depth()[0]
    return depth

# Function to get the video stream from the Kinect sensor
def get_video():
    video = freenect.sync_get_video()[0]
    return video
    
def process(hands, ser):
    # ramping function for smoothing
    pos = None
    while True:
        depth, image = get_depth(), get_video()
        image = cv2.flip(image, 1)
        if not DEBUG:
            image.flags.writeable = False # performance
        results = hands.process(image)

        # ripping joints and handedness
        left_present = False
        if results.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                hand_type = results.multi_handedness[i].classification[0].label
                j = 8
                pt = mp_drawing._normalized_to_pixel_coordinates(
                        hand_landmarks.landmark[j].x, hand_landmarks.landmark[j].y, WIDTH, HEIGHT)
                if pt:
                    if hand_type == "Left":
                        left_present = True
                    else:
                        pos = ramp(pos, pt)

        # only register hand if left hand is also present
        if not left_present:
            continue
        
        # x: left-right, y: up-down, z: forward-backward
        x, y = pos
        z = depth[y][x]

        # TODO: caculating joint angles with inv kinematics
        # x = y = z = 0

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
    cv2.destroyAllWindows()
    freenect.sync_stop()

if __name__ == "__main__":
    main()
