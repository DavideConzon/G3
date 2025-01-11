import tkinter as tk
from tkinter import Tk, Canvas, Frame, PhotoImage, filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import tensorflow as tf
import numpy as np
import os
import csv
import hashlib
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import hashlib
import pandas as pd



# Percorso del modello salvato
MODEL_PATH = r"C:\Users\david\OneDrive\Desktop\G3\skin_cancer_best_model.h5"
# Predefined user roles
PREDEFINED_ROLES = ['Admin', 'Medico', 'User', 'Guest']

# Caricamento del modello
model = tf.keras.models.load_model(MODEL_PATH)

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

    back_button = tk.Button(medico_admin_frame, text="Torna alla home", command=show_welcome_screen, bg='#0078D7', fg='#ffffff')
    back_button.pack(pady=10)

def start_camera():
    global cap
    cap = cv2.VideoCapture(0)  # Usa la fotocamera predefinita
    if not cap.isOpened():
        messagebox.showerror("Errore", "Non è stato possibile accedere alla fotocamera!")
        return

    show_camera_feed()

def show_camera_feed():
    global cap, camera_label  # Dichiarazione globale
    ret, frame = cap.read()
    if ret:
        # Converti il frame da BGR (OpenCV) a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Crea un'immagine PIL a partire dal frame
        img = Image.fromarray(frame_rgb)
        
        # Ridimensiona l'immagine per adattarla alla finestra di Tkinter
        img = img.resize((640, 480), Image.ANTIALIAS)
        
        # Converte l'immagine PIL in un oggetto ImageTk per poterlo visualizzare su Tkinter
        img_tk = ImageTk.PhotoImage(img)
        
        # Mostra l'immagine nella finestra
        if camera_label:  # Se 'camera_label' esiste
            camera_label.config(image=img_tk)
            camera_label.image = img_tk
        else:
            # Se 'camera_label' non esiste, crea la label per visualizzare il feed video
            camera_label = tk.Label(root, image=img_tk)
            camera_label.image = img_tk
            camera_label.pack(pady=10)
        
        # Continua a mostrare il feed video ogni 10ms
        root.after(10, show_camera_feed)
    else:
        messagebox.showerror("Errore", "Impossibile catturare il frame dalla fotocamera!")

def stop_camera():
    global cap
    if cap and cap.isOpened():
        cap.release()  # Rilascia la fotocamera
    cv2.destroyAllWindows()

# Setup della finestra principale
root = tk.Tk()
root.title("Sistema Gestione Pazienti")
root.geometry("800x600")
root.config(bg='#f0f0f0')

# Avvia la schermata di benvenuto
show_welcome_screen()

# Avvia il loop principale
root.mainloop()
