import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model
import os


class HandDetector:
    def __init__(self, gesture_classifier_model_path, detection_confidence=0.7, draw_result_to_frame=False):
        self.hand_detector = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=detection_confidence)
        self.gesture_classifier = load_model(gesture_classifier_model_path)
        with open(os.path.join(os.path.abspath(os.getcwd()), 'gesture.names'), 'r') as f:
            self.gesture_names = f.read().split('\n')
        self.click_gesture_names = ["thumbs up", "thumbs down", "call me", "rock", "fist", "smile"]
        self.mpDraw = mp.solutions.drawing_utils
        self.draw_result_to_frame = draw_result_to_frame

    def detect(self, frame):
        height, width, _ = frame.shape
        height_step = height // 8
        width_step = width // 8

        hands_landmarks = self.hand_detector.process(frame)
        is_click_gesture = False
        landmark_height_bracket = None
        landmark_width_bracket = None
        if hands_landmarks.multi_hand_landmarks:
            landmarks = []
            for landmarks_for_hand in hands_landmarks.multi_hand_landmarks:
                for landmark in landmarks_for_hand.landmark:
                    # print(id, lm)
                    lmx = int(landmark.x * width)
                    lmy = int(landmark.y * height)
                    landmarks.append([lmx, lmy])

                gesture_prediction = self.gesture_classifier.predict([landmarks])
                gesture_prediction_id = np.argmax(gesture_prediction)
                predicted_gesture_name = self.gesture_names[gesture_prediction_id]

                landmark_avg = np.rint(np.average(np.array(landmarks), axis=0))

                landmark_height_bracket = landmark_avg[0]//width_step
                landmark_width_bracket = landmark_avg[1]//height_step
                is_click_gesture = predicted_gesture_name in self.click_gesture_names

                if self.draw_result_to_frame:
                    self.mpDraw.draw_landmarks(frame, landmarks_for_hand, mp.solutions.hands.HAND_CONNECTIONS)
                    cv2.putText(frame, predicted_gesture_name, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    cv2.circle(frame, (int(landmark_avg[0]), int(landmark_avg[1])), radius=5, color=(255, 0, 0), thickness=-1)

        return landmark_height_bracket, landmark_width_bracket, is_click_gesture, frame

