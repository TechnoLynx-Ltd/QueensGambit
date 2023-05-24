import cv2

from hand_detector import HandDetector


def main():
    hand_detector = HandDetector(gesture_classifier_model_path='mp_hand_gesture', draw_result_to_frame=True)

    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        b_h, b_w, is_click, frame = hand_detector.detect(frame_rgb)

        print(b_h, b_w, is_click)
        cv2.imshow("Output", frame)

        if cv2.waitKey(1) == ord('q'):
            break

    # release the webcam and destroy all active windows
    cap.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
