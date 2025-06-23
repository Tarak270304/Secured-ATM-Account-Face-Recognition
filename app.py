from flask import Flask, render_template, request, redirect, url_for, session, flash
import threading
from face_register import create_dataset, delete_user_images
from face_train import train_faces
from face_recognition_atm import recognize_face
from db_handler import (
    init_db, register_user, verify_pin,
    get_balance, update_balance, delete_user, get_account_number
)
import os
import numpy as np

app = Flask(__name__)
app.secret_key = 'supersecretkey'

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        pin = request.form["pin"]
        account_number = request.form["account_number"]

        if not name or not pin or not account_number:
            flash("All fields are required.")
            return redirect(url_for("register"))

        if register_user(name, pin, account_number):  # Pass account_number
            threading.Thread(target=create_dataset, args=(name,), daemon=True).start()
            flash("Registration successful! Please look at the camera to record your face.")
            return redirect(url_for("index"))
        else:
            flash("User already exists.")
            return redirect(url_for("register"))

    return render_template("register.html")

@app.route('/train')
def train():
    train_faces()
    flash('Model trained successfully')
    return redirect(url_for('index'))

@app.route('/login')
def login():
    user = recognize_face()
    if user == "Unknown":
        flash("Face not recognized")
        return redirect(url_for('index'))
    session['user'] = user
    return redirect(url_for('pin'))

@app.route('/pin', methods=['GET', 'POST'])
def pin():
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))
    if request.method == 'POST':
        pin = request.form['pin']
        if verify_pin(user, pin):
            return redirect(url_for('menu'))
        else:
            flash('Invalid PIN')
            return redirect(url_for('index'))
    return render_template('pin.html', user=user)

@app.route('/menu')
def menu():
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))
    
    account_number = get_account_number(user)
    return render_template('menu.html', user=user, account_number=account_number)

@app.route('/balance')
def balance():
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))
    balance = get_balance(user)
    flash(f"Your balance is ${balance:.2f}")
    return redirect(url_for('menu'))

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            current_balance = get_balance(user)
            if amount <= 0 or amount > current_balance:
                flash('Invalid or insufficient amount')
            else:
                update_balance(user, amount)
                flash(f"${amount:.2f} withdrawn")
                return redirect(url_for('menu'))
        except ValueError:
            flash('Enter a valid number')
    return render_template('withdraw.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route("/delete_user", methods=["GET", "POST"])
def delete_user_route():
    if request.method == "POST":
        name = request.form["name"]
        delete_user(name)
        delete_user_images(name)

        # Clean up empty trainer if no dataset remains
        remaining_files = [f for f in os.listdir("dataset") if f.endswith(".jpg")]
        if remaining_files:
            train_faces()
        else:
            if os.path.exists("trainer.yml"):
                os.remove("trainer.yml")
            if os.path.exists("label_map.npy"):
                os.remove("label_map.npy")
        flash(f"User {name} deleted successfully.")
        return redirect(url_for("index"))

    return render_template("delete_user.html")

if __name__ == '__main__':
    app.run(debug=True)



face_register.py
import cv2
import os
import numpy as np

def create_dataset(name):
    dataset_path = "dataset"
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)
    count = 0

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            face_img = gray[y:y+h, x:x+w]
            file_name = f"{dataset_path}/{name}_{count}.jpg"
            cv2.imwrite(file_name, face_img)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow('Recording Face Data - Press Q to Exit', frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or count >= 30:
            break

    cap.release()
    cv2.destroyAllWindows()

def delete_user_images(name, dataset_path="dataset"):
    for filename in os.listdir(dataset_path):
        if filename.startswith(name + "_"):
            os.remove(os.path.join(dataset_path, filename))

