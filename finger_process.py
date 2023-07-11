import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image = cv2.flip(image, 1)
        # image.flags.writeable = False # performance
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_height, image_width, _ = image.shape

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                finger_points = []
                # joints
                for i in range(5, 9):
                    landmark_px = mp_drawing._normalized_to_pixel_coordinates(
                        hand_landmarks.landmark[i].x, hand_landmarks.landmark[i].y, image_width, image_height)
                    if landmark_px:
                        cv2.circle(image, landmark_px, 5, (0, 255, 0), -1)
                        finger_points.append(landmark_px)
                # connections 
                for i in range(len(finger_points)-1):
                        cv2.line(image, finger_points[i], finger_points[i+1], (255, 0, 0), 2)

        cv2.imshow('Index finger Tracking', image)
        if cv2.waitKey(5) == 27:
            break

cap.release()

