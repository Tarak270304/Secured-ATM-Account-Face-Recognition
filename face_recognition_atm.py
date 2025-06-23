import cv2
import numpy as np
import os

def recognize_face():
    if not os.path.exists("trainer.yml") or not os.path.exists("label_map.npy"):
        print("Trained model or label map not found. Please train the model first.")
        return "Unknown"

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainer.yml")
    label_map = np.load("label_map.npy", allow_pickle=True).item()
    rev_label_map = {v: k for k, v in label_map.items()}

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)

    recognized_user = "Unknown"
    confidence_threshold = 60
    attempts = 0

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            label, confidence = recognizer.predict(roi)

            if confidence < confidence_threshold:
                recognized_user = rev_label_map[label]
                cap.release()
                cv2.destroyAllWindows()
                return recognized_user
            else:
                attempts += 1

        cv2.imshow("Recognizing Face - Press Q to Cancel", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or attempts > 100:
            break

    cap.release()
    cv2.destroyAllWindows()
    return recognized_user
