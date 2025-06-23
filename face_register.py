import cv2
import os

def create_dataset(name):
    dataset_path = "dataset"
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)

    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            face = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            file_path = os.path.join(dataset_path, f"{name}_{count}.jpg")
            cv2.imwrite(file_path, face)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Capturing {count}/50", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        cv2.imshow("Capturing Face", frame)

        if cv2.waitKey(1) == 13 or count >= 50:  # Enter key (13) or 50 images
            break

    cap.release()
    cv2.destroyAllWindows()


def delete_user_images(name, dataset_path="dataset"):
    if not os.path.exists(dataset_path):
        return

    for filename in os.listdir(dataset_path):
        if filename.startswith(name + "_"):
            os.remove(os.path.join(dataset_path, filename))
