import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import cv2
import tensorflow as tf
import numpy as np
import os
import csv
from tensorflow.keras.models import load_model

# Percorso del modello salvato
MODEL_PATH = "/Users/davideconzon/Desktop/G3/skin_cancer_best_model.h5"

# Predefined user roles
PREDEFINED_ROLES = ['Admin', 'Medico', 'User', 'Guest']

#CLASSE PAZIENTE 
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


def show_welcome_screen():
    for widget in root.winfo_children():
        widget.destroy()

    welcome_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
    welcome_frame.pack(fill=tk.BOTH, expand=True)

    welcome_label = tk.Label(welcome_frame, text="Benvenuto! Scegli un'opzione", font=("Arial", 16), bg='#f0f0f0')
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

    tk.Label(register_frame, text="Registrazione Utente", font=("Arial", 16), bg='#ffffff').pack(pady=10)

    nome_entry = tk.Entry(register_frame, width=30)
    nome_entry.pack(pady=5)

    cognome_entry = tk.Entry(register_frame, width=30)
    cognome_entry.pack(pady=5)

    ruolo_combobox = ttk.Combobox(register_frame, values=PREDEFINED_ROLES, width=28)
    ruolo_combobox.set(PREDEFINED_ROLES[0])
    ruolo_combobox.pack(pady=5)

    email_entry = tk.Entry(register_frame, width=30)
    email_entry.pack(pady=5)

    telefono_entry = tk.Entry(register_frame, width=30)
    telefono_entry.pack(pady=5)

    password_entry = tk.Entry(register_frame, show="*", width=30)
    password_entry.pack(pady=5)

    feedback_label = tk.Label(register_frame, text="", bg='#ffffff', font=('Arial', 10, 'italic'))
    feedback_label.pack(pady=5)

    register_button = tk.Button(register_frame, text="Registra", command=register_callback, bg='#0078D7', fg='#ffffff')
    register_button.pack(pady=10)

    back_button = tk.Button(register_frame, text="Torna alla home", command=show_welcome_screen, bg='#0078D7', fg='#ffffff')
    back_button.pack(pady=10)

def show_login_screen():
    for widget in root.winfo_children():
        widget.destroy()

    login_frame = tk.Frame(root, bg='#ffffff', relief=tk.RAISED, bd=2)
    login_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

    tk.Label(login_frame, text="Login", font=("Arial", 16), bg='#ffffff').pack(pady=10)

    email_entry = tk.Entry(login_frame, width=30)
    email_entry.pack(pady=5)

    password_entry = tk.Entry(login_frame, show="*", width=30)
    password_entry.pack(pady=5)

    login_button = tk.Button(login_frame, text="Accedi", command=lambda: login_callback(email_entry, password_entry), bg='#0078D7', fg='#ffffff')
    login_button.pack(pady=10)

    back_button = tk.Button(login_frame, text="Torna alla home", command=show_welcome_screen, bg='#0078D7', fg='#ffffff')
    back_button.pack(pady=10)

def login_callback(email_entry, password_entry):
    email = email_entry.get()
    password = password_entry.get()

    if email == "" or password == "":
        messagebox.showerror("Errore", "Email e Password sono obbligatori!")
        return

    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[3] == email and row[5] == password:
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

    patient_label = tk.Label(patient_frame, text=f"Ciao {user_name}, questi sono i tuoi dati", font=("Arial", 16), bg='#f0f0f0')
    patient_label.pack(pady=20)

    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == user_name:
                user_email = row[3]
                user_phone = row[4]
                break
    
    tk.Label(patient_frame, text=f"Email: {user_email}", bg='#f0f0f0').pack(pady=5)
    tk.Label(patient_frame, text=f"Telefono: {user_phone}", bg='#f0f0f0').pack(pady=5)

    back_button = tk.Button(patient_frame, text="Torna alla home", command=show_welcome_screen, bg='#0078D7', fg='#ffffff')
    back_button.pack(pady=20)

def show_medico_or_admin_screen(user_name, user_role):
    for widget in root.winfo_children():
        widget.destroy()

    medico_admin_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
    medico_admin_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(medico_admin_frame, text=f"Ciao {user_name}, ruolo: {user_role}", font=("Arial", 16), bg='#f0f0f0').pack(pady=20)

    search_label = tk.Label(medico_admin_frame, text="Cerca paziente per nome", bg='#f0f0f0')
    search_label.pack(pady=5)
    search_entry = tk.Entry(medico_admin_frame, width=30)
    search_entry.pack(pady=5)
    search_button = tk.Button(medico_admin_frame, text="Cerca", command=lambda: search_patient(search_entry.get()), bg='#0078D7', fg='#ffffff')
    search_button.pack(pady=10)

    start_button = tk.Button(medico_admin_frame, text="Avvia Fotocamera", command=start_camera, bg='#0078D7', fg='#ffffff')
    start_button.pack(pady=10)

    back_button = tk.Button(medico_admin_frame, text="Torna alla Home", command=show_welcome_screen, bg='#0078D7', fg='#ffffff')
    back_button.pack(pady=20)

def search_patient(name, user_role, user_name):
    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0].lower() == name.lower():
                # Se è un medico, permette di compilare i dati del paziente
                if user_role == "Medico":
                    paziente = Paziente(nome=row[0], cognome=row[1], data_nascita=row[6], sesso=row[7], 
                                        codice_fiscale=row[8], indirizzo="", telefono="", email=row[9],
                                        patologie_precedenti="", farmaci_assunti="")
                    # Associa i campi vuoti per il medico
                    show_paziente_form(paziente, user_name)
                else:
                    # Se è un paziente o un altro utente, solo la visualizzazione dei dati
                    messagebox.showinfo("Dati Paziente", paziente.visualizza_anagrafica())
                return
    messagebox.showerror("Errore", "Paziente non trovato!")

def show_paziente_form(paziente, user_name):
    for widget in root.winfo_children():
        widget.destroy()

    form_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
    form_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(form_frame, text=f"Compila i dati per {paziente.nome} {paziente.cognome}", font=("Arial", 16), bg='#f0f0f0').pack(pady=20)

    # Creazione dei campi per compilare i dati del paziente
    entry_indirizzo = tk.Entry(form_frame)
    entry_indirizzo.insert(0, paziente.indirizzo)
    entry_indirizzo.pack(pady=5)
    
    entry_telefono = tk.Entry(form_frame)
    entry_telefono.insert(0, paziente.telefono)
    entry_telefono.pack(pady=5)
    
    entry_email = tk.Entry(form_frame)
    entry_email.insert(0, paziente.email)
    entry_email.pack(pady=5)
    
    entry_patologie = tk.Entry(form_frame)
    entry_patologie.insert(0, paziente.patologie_precedenti)
    entry_patologie.pack(pady=5)

    entry_farmaci = tk.Entry(form_frame)
    entry_farmaci.insert(0, paziente.farmaci_assunti)
    entry_farmaci.pack(pady=5)

    btn_salva = tk.Button(form_frame, text="Salva Dati", command=lambda: salva_dati_paziente(paziente, 
                                                                                        entry_indirizzo.get(),
                                                                                        entry_telefono.get(),
                                                                                        entry_email.get(),
                                                                                        entry_patologie.get(),
                                                                                        entry_farmaci.get()))
    btn_salva.pack(pady=10)

    back_button = tk.Button(form_frame, text="Torna alla home", command=show_welcome_screen, bg='#0078D7', fg='#ffffff')
    back_button.pack(pady=20)

def salva_dati_paziente(paziente, indirizzo, telefono, email, patologie_precedenti, farmaci_assunti):
    paziente.indirizzo = indirizzo
    paziente.telefono = telefono
    paziente.email = email
    paziente.patologie_precedenti = patologie_precedenti
    paziente.farmaci_assunti = farmaci_assunti

    # Salva i dati del paziente nel file
    with open('patients.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([paziente.nome, paziente.cognome, paziente.data_nascita, paziente.sesso, paziente.codice_fiscale, paziente.indirizzo, paziente.telefono, paziente.email, paziente.patologie_precedenti, paziente.farmaci_assunti])

    messagebox.showinfo("Dati Salvati", "Dati del paziente salvati correttamente!")
    print(paziente.visualizza_anagrafica())


def start_camera():
    global camera, canvas, image_container, result_label
    camera = cv2.VideoCapture(0)
    show_frame()

def show_frame():
    ret, frame = camera.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(img)
        canvas.itemconfig(image_container, image=img)
        canvas.image = img
        canvas.after(10, show_frame)

def classify_image():
    global camera, canvas, result_label
    ret, frame = camera.read()
    if ret:
        frame_resized = cv2.resize(frame, (224, 224))
        frame_normalized = frame_resized / 255.0
        frame_expanded = np.expand_dims(frame_normalized, axis=0)
        prediction = model.predict(frame_expanded)
        if prediction[0][0] > 0.5:
            result_label.config(text="Classificazione: Cancro della pelle Rilevato", fg='red')
        else:
            result_label.config(text="Classificazione: Non Cancro della pelle", fg='green')

def load_skin_cancer_model():
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        return model
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel caricamento del modello: {str(e)}")
        return None

def create_gui():
    global root, model
    root = tk.Tk()
    root.title("Skin Cancer Detection")

    model = load_skin_cancer_model()
    if model is None:
        messagebox.showerror("Errore", "Impossibile caricare il modello")
        return

    button_frame = tk.Frame(root)
    button_frame.pack()

    login_button = tk.Button(button_frame, text="Login", command=show_login_screen)
    login_button.pack(side=tk.LEFT)

    register_button = tk.Button(button_frame, text="Registrati", command=show_register_screen)
    register_button.pack(side=tk.LEFT)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
