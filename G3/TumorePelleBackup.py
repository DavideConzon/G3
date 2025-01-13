import tkinter as tk
from tkinter import Tk, Canvas, Frame, PhotoImage, filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import csv
import hashlib
from tensorflow.keras.preprocessing import image
import pandas as pd
import tensorflow as tf
from tensorflow.keras.metrics import top_k_categorical_accuracy
import threading

# If `top_2` is actually top_k_categorical_accuracy with k=2
def top_2(y_true, y_pred):
    return top_k_categorical_accuracy(y_true, y_pred, k=2)

# Path to the model
MODEL_PATH = r"C:\Users\david\OneDrive\Desktop\G3\skin_cancer_best_model.h5"
#Path del modello lite
#MODEL_PATH = r"C:\Users\david\OneDrive\Desktop\G3\skin_cancer_best_model.tflite"
# Predefined user roles
PREDEFINED_ROLES = ['Admin', 'Medico', 'User', 'Guest']

# Caricamento del modello
model = tf.keras.models.load_model(MODEL_PATH, custom_objects={'top_2': top_2})

# Variabili globali
cap = None
camera_label = None

# CLASSE PAZIENTE
class Paziente:
    def __init__(self, nome, cognome, data_nascita, sesso, codice_fiscale, indirizzo, telefono, email, patologie_precedenti, farmaci_assunti):
        self.nome = nome
        self.cognome = cognome
        self.data_nascita = data_nascita
        self.sesso = sesso
        self.codice_fiscale = codice_fiscale
        self.indirizzo = indirizzo
        self.telefono = telefono
        self.email = email
        self.patologie_precedenti = patologie_precedenti
        self.farmaci_assunti = farmaci_assunti

    def visualizza_anagrafica(self):
        return f"Nome: {self.nome} {self.cognome}\nEmail: {self.email}\nTelefono: {self.telefono}"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def show_welcome_screen():
    for widget in root.winfo_children():
        widget.destroy()

    welcome_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
    welcome_frame.pack(fill=tk.BOTH, expand=True)

    welcome_label = tk.Label(welcome_frame, text="Benvenuto! Scegli un'opzione", font=("Arial", 16), bg='#f0f0f0', fg="#333")
    welcome_label.pack(pady=20)

    login_button = tk.Button(welcome_frame, text="Accedi", command=show_login_screen, bg='#0078D7', fg='#ffffff')
    login_button.pack(pady=10)

    register_button = tk.Button(welcome_frame, text="Registrati", command=show_register_screen, bg='#0078D7', fg='#ffffff')
    register_button.pack(pady=10)

def show_register_screen():
    for widget in root.winfo_children():
        widget.destroy()

    register_frame = tk.Frame(root, bg='#ffffff', relief=tk.RAISED, bd=2)
    register_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

    tk.Label(register_frame, text="Registrazione Utente", font=("Arial", 16), bg='#ffffff', fg="#333").pack(pady=10)

    tk.Label(register_frame, text="Nome:", bg='#ffffff', fg="#333").pack(pady=5)
    nome_entry = tk.Entry(register_frame, width=30)
    nome_entry.pack(pady=5)

    tk.Label(register_frame, text="Cognome:", bg='#ffffff', fg="#333").pack(pady=5)
    cognome_entry = tk.Entry(register_frame, width=30)
    cognome_entry.pack(pady=5)

    tk.Label(register_frame, text="Ruolo:", bg='#ffffff', fg="#333").pack(pady=5)
    ruolo_combobox = ttk.Combobox(register_frame, values=PREDEFINED_ROLES, width=28)
    ruolo_combobox.set(PREDEFINED_ROLES[0])
    ruolo_combobox.pack(pady=5)

    tk.Label(register_frame, text="Email:", bg='#ffffff', fg="#333").pack(pady=5)
    email_entry = tk.Entry(register_frame, width=30)
    email_entry.pack(pady=5)

    tk.Label(register_frame, text="Telefono:", bg='#ffffff', fg="#333").pack(pady=5)
    telefono_entry = tk.Entry(register_frame, width=30)
    telefono_entry.pack(pady=5)

    tk.Label(register_frame, text="Password:", bg='#ffffff', fg="#333").pack(pady=5)
    password_entry = tk.Entry(register_frame, show="*", width=30)
    password_entry.pack(pady=5)

    feedback_label = tk.Label(register_frame, text="", bg='#ffffff', font=('Arial', 10, 'italic'))
    feedback_label.pack(pady=5)

    register_button = tk.Button(register_frame, text="Registra", command=lambda: register_callback(nome_entry, cognome_entry, ruolo_combobox, email_entry, telefono_entry, password_entry, feedback_label), bg='#0078D7', fg='#ffffff')
    register_button.pack(pady=10)

    back_button = tk.Button(register_frame, text="Torna alla home", command=show_welcome_screen, bg='#0078D7', fg='#ffffff')
    back_button.pack(pady=10)

def register_callback(nome_entry, cognome_entry, ruolo_combobox, email_entry, telefono_entry, password_entry, feedback_label):
    nome = nome_entry.get()
    cognome = cognome_entry.get()
    ruolo = ruolo_combobox.get()
    email = email_entry.get()
    telefono = telefono_entry.get()
    password = password_entry.get()

    if not nome or not cognome or not email or not telefono or not password:
        feedback_label.config(text="Tutti i campi sono obbligatori", fg="red")
        return

    if '@' not in email:
        feedback_label.config(text="Email non valida", fg="red")
        return

    hashed_password = hash_password(password)
    
    with open('users.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([nome, cognome, ruolo, email, telefono, hashed_password])

    feedback_label.config(text="Registrazione completata", fg="green")

def show_login_screen():
    for widget in root.winfo_children():
        widget.destroy()

    login_frame = tk.Frame(root, bg='#ffffff', relief=tk.RAISED, bd=2)
    login_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

    tk.Label(login_frame, text="Login", font=("Arial", 16), bg='#ffffff', fg="#333").pack(pady=10)

    tk.Label(login_frame, text="Email:", bg='#ffffff', fg="#333").pack(pady=5)
    email_entry = tk.Entry(login_frame, width=30)
    email_entry.pack(pady=5)

    tk.Label(login_frame, text="Password:", bg='#ffffff', fg="#333").pack(pady=5)
    password_entry = tk.Entry(login_frame, show="*", width=30)
    password_entry.pack(pady=5)

    login_button = tk.Button(login_frame, text="Accedi", command=lambda: login_callback(email_entry, password_entry), bg='#0078D7', fg='#ffffff')
    login_button.pack(pady=10)

    back_button = tk.Button(login_frame, text="Torna alla home", command=show_welcome_screen, bg='#0078D7', fg='#ffffff')
    back_button.pack(pady=10)

def login_callback(email_entry, password_entry):
    email = email_entry.get()
    password = password_entry.get()

    if not email or not password:
        messagebox.showerror("Errore", "Email e Password sono obbligatori!")
        return

    hashed_password = hash_password(password)
    
    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[3] == email and row[5] == hashed_password:
                user_role = row[2]
                user_name = row[0]

                if user_role == 'User':
                    show_patient_screen(user_name)
                elif user_role in ['Admin', 'Medico']:
                    show_medico_or_admin_screen(user_name, user_role)
                return
    messagebox.showerror("Errore", "Credenziali non valide!")

def show_patient_screen(user_name):
    for widget in root.winfo_children():
        widget.destroy()

    patient_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
    patient_frame.pack(fill=tk.BOTH, expand=True)

    patient_label = tk.Label(patient_frame, text=f"Ciao {user_name}, questi sono i tuoi dati", font=("Arial", 16), bg='#f0f0f0', fg="#333")
    patient_label.pack(pady=20)

    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == user_name:
                user_email = row[3]
                user_phone = row[4]
                break
    
    tk.Label(patient_frame, text=f"Email: {user_email}", bg='#f0f0f0', fg="#333").pack(pady=5)
    tk.Label(patient_frame, text=f"Telefono: {user_phone}", bg='#f0f0f0', fg="#333").pack(pady=5)

    back_button = tk.Button(patient_frame, text="Torna alla home", command=show_welcome_screen, bg='#0078D7', fg='#ffffff')
    back_button.pack(pady=20)

def show_medico_or_admin_screen(user_name, user_role):
    for widget in root.winfo_children():
        widget.destroy()

    medico_admin_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
    medico_admin_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(medico_admin_frame, text=f"Ciao {user_name}, ruolo: {user_role}", font=("Arial", 16), bg='#f0f0f0', fg="#333").pack(pady=20)

    search_label = tk.Label(medico_admin_frame, text="Cerca paziente per nome", bg='#f0f0f0', fg="#333")
    search_label.pack(pady=5)
    search_entry = tk.Entry(medico_admin_frame, width=30)
    search_entry.pack(pady=5)
    search_button = tk.Button(medico_admin_frame, text="Cerca", command=lambda: search_patient(search_entry.get(), user_role, user_name), bg='#0078D7', fg='#ffffff')
    search_button.pack(pady=10)

    start_button = tk.Button(medico_admin_frame, text="Avvia Fotocamera", command=start_camera, bg='#0078D7', fg='#ffffff')
    start_button.pack(pady=10)

    stop_button = tk.Button(medico_admin_frame, text="Ferma Fotocamera", command=stop_camera, bg='#0078D7', fg='#ffffff')
    stop_button.pack(pady=10)

    # Aggiungi il label per il video
    global camera_label
    camera_label = tk.Label(medico_admin_frame)
    camera_label.pack(pady=10)

    # Add a label to show the prediction result
    global prediction_label
    prediction_label = tk.Label(medico_admin_frame, text="Predizione: ", font=("Arial", 14), bg='#f0f0f0', fg="blue")
    prediction_label.pack(pady=10)

    back_button = tk.Button(medico_admin_frame, text="Torna alla home", command=show_welcome_screen, bg='#0078D7', fg='#ffffff')
    back_button.pack(pady=10)

def classify_frame(frame, class_labels):
    # Preprocess the frame
    img_array = preprocess_image(frame)

    # Get the model's prediction
    predictions = model.predict(img_array)

    # Get the class label with the highest score
    max_score_index = np.argmax(predictions)
    max_score = predictions[0, max_score_index]
    class_label = list(class_labels.keys())[max_score_index]

    # Display the class label and score on the frame
    cv2.putText(frame, f"{class_label} ({max_score:.2f})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Update the prediction label in the UI
    if prediction_label:
        prediction_label.config(text=f"Predizione: {class_label} ({max_score:.2f})")
    
    # Update the camera label with the new frame (to continuously show the updated video frame)
    if camera_label:
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        camera_label.config(image=photo)
        camera_label.image = photo

    # Continue capturing frames from the camera (recursively call update_frame to create a loop)
    root.after(10, update_frame, class_labels)  # Use root.after to keep the loop going


# Update the start_camera function to pass class_labels to classify_frame
def start_camera():
    global cap
    cap = cv2.VideoCapture(0)

    # Define the class labels
    class_labels = {
        'Actinic Keratoses and\n Intraepithelial Carcinoma': 0,
        'Basal Cell Carcinoma': 1,
        'Benign Keratosis-like Lesions': 2,
        'Dermatofibroma': 3,
        'Melanoma': 4,
        'Melanocytic Nevi(nei)': 5,
        'Vascular Lesions': 6
    }

    # Start the video stream and update frames
    update_frame(class_labels)

# Modify update_frame to pass class_labels to classify_frame
def update_frame(class_labels):
    ret, frame = cap.read()
    if ret:
        # Preprocess and classify the frame
        classify_frame(frame, class_labels)  # Pass class_labels here

        # Convert the frame to RGB for Tkinter compatibility
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_tk = ImageTk.PhotoImage(Image.fromarray(frame_rgb))
        
        # Update the label with the new image
        camera_label.config(image=img_tk)
        camera_label.image = img_tk
    
    # Call the function again to continuously update the video feed
    root.after(10, update_frame, class_labels)


def stop_camera():
    global cap
    if cap:
        cap.release()
    camera_label.config(image=None)


def preprocess_image(frame):
    # Converte il frame in RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Ridimensiona l'immagine alle dimensioni richieste dal modello
    frame_resized = cv2.resize(frame_rgb, (224, 224))  # Modifica se la forma desiderata è diversa
    
    # Converte l'immagine in un array numpy
    img_array = np.array(frame_resized)

    # Aggiungi una dimensione extra per batch: la forma diventa (1, 1280, 1280, 3)
    img_array = np.expand_dims(img_array, axis=0)

    # Normalizza l'immagine (se il modello richiede normalizzazione)
    img_array = img_array / 255.0

    return img_array


root = Tk()
root.title("Sistema di Gestione Pazienti")
root.geometry("600x500")

show_welcome_screen()

root.mainloop()
