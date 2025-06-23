import cv2
import os
import numpy as np

recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def train_faces():
    dataset_path = "dataset"
    if not os.path.exists(dataset_path):
        print("Dataset folder not found!")
        return

    faces = []
    labels = []
    label_map = {}
    current_id = 0

    # Rebuild label map from dataset directory
    images = [f for f in os.listdir(dataset_path) if f.endswith(".jpg")]
    unique_names = sorted(set(img.split("_")[0] for img in images))

    for name in unique_names:
        label_map[name] = current_id
        current_id += 1

    for image_file in images:
        name = image_file.split("_")[0]
        label = label_map[name]
        img_path = os.path.join(dataset_path, image_file)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        # Optional: detect and crop face for better results
        faces_detected = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)
        for (x, y, w, h) in faces_detected:
            face_roi = img[y:y+h, x:x+w]
            faces.append(face_roi)
            labels.append(label)

    if faces and labels:
        recognizer.train(faces, np.array(labels))
        recognizer.write("trainer.yml")
        with open("label_map.npy", "wb") as f:
            np.save(f, label_map)
        print("Model trained and saved.")
    else:
        print("No face data found for training.")
