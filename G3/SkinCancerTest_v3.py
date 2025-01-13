import tensorflow as tf
from tkinter import Tk, Label, Button, filedialog, Canvas, Frame, StringVar
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import pandas as pd
import cv2

# Carica il modello TFLite
interpreter = tf.lite.Interpreter(model_path= r"C:\Users\david\OneDrive\Desktop\G3\skin_cancer_best_model.tflite")
interpreter.allocate_tensors()

# Ottieni dettagli sui tensori
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Definisce le classi del modello
class_labels = ['Actinic Keratoses and\n Intraepithelial Carcinoma', 'Basal Cell Carcinoma', 
                'Benign Keratosis-like Lesions', 'Dermatofibroma', 'Melanoma', 
                'Melanocytic Nevi (nei)', 'Vascular Lesions']

# Variabile globale per l'immagine catturata
captured_image = None
captured_frame = None
camera_running = False

# Funzione per preprocessare l'immagine
def preprocess_image(image):
    image = Image.fromarray(image).convert("RGB")
    image = image.resize((224, 224))  # Dimensione usata per il training
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0).astype(np.float32)  # Aggiunge dimensione batch
    return image_array

# Funzione per fare la previsione e visualizzare i risultati per l'immagine caricata
def classify_image():
    global captured_image
    image_path = filedialog.askopenfilename()
    if image_path:
        # Preprocessa l'immagine
        image = Image.open(image_path).convert("RGB")
        image_array = preprocess_image(np.array(image))
        
        # Imposta l'input per l'interprete
        interpreter.set_tensor(input_details[0]['index'], image_array)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_details[0]['index'])[0]
        
        # Visualizza immagine
        img = image.resize((500, 500))
        img_tk = ImageTk.PhotoImage(img)
        canvas.itemconfig(image_container, image=img_tk)
        canvas.image = img_tk  # Evita che l'immagine venga garbage-collected
        captured_image = img_tk
        
        # Mostra i risultati
        result_text = "Classificazione:\n"
        for label, prob in zip(class_labels, predictions):
            result_text += f"{label}: {prob*100:.2f}%\n"
        
        result_label.config(text=result_text)
        
        # Salva i risultati in un CSV
        results_df = pd.DataFrame({'Class': class_labels, 'Probability': predictions * 100})
        results_df.to_csv('classification_results.csv', index=False)

# Funzione per fare la previsione e visualizzare i risultati per ogni fotogramma
def classify_frame(frame):
    image_array = preprocess_image(frame)
    interpreter.set_tensor(input_details[0]['index'], image_array)
    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0]['index'])[0]
    
    result_text = "Classificazione:\n"
    for label, prob in zip(class_labels, predictions):
        result_text += f"{label}: {prob * 100:.2f}%\n"
    
    result_label.config(text=result_text)

# Funzione per catturare un'immagine dalla videocamera
def capture_image():
    global captured_image, captured_frame, camera_running
    camera_running = False  # Ferma il flusso della videocamera
    selected_camera = int(camera_selection.get())
    cap = cv2.VideoCapture(selected_camera)
    ret, frame = cap.read()
    if ret:
        captured_frame = frame  # Memorizza il frame catturato
        cv2.imwrite("captured_image.jpg", frame)
        print("Immagine catturata e salvata come 'captured_image.jpg'")
        # Mostra l'immagine catturata
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((500, 500))
        img_tk = ImageTk.PhotoImage(img)
        canvas.itemconfig(image_container, image=img_tk)
        canvas.image = img_tk
        captured_image = img_tk
    cap.release()

# Funzione per avviare la videocamera
def start_camera():
    global captured_image, captured_frame, camera_running
    camera_running = True  # Imposta lo stato della videocamera
    selected_camera = int(camera_selection.get())
    captured_image = None  # Resetta l'immagine catturata
    captured_frame = None  # Resetta il frame catturato
    cap = cv2.VideoCapture(selected_camera)
    
    while cap.isOpened() and camera_running:
        ret, frame = cap.read()
        if ret:
            # Ridimensiona e visualizza il frame in Tkinter solo se non c'è un'immagine catturata
            if captured_image is None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img = img.resize((500, 500))
                img_tk = ImageTk.PhotoImage(img)
                canvas.itemconfig(image_container, image=img_tk)
                canvas.image = img_tk
                
                # Effettua la classificazione
                classify_frame(frame_rgb)
            
            root.update_idletasks()
            root.update()
        else:
            break
    
    cap.release()

# Imposta l'interfaccia grafica con layout diviso
root = Tk()
root.title("Skin Cancer Classification")
root.geometry("1200x700")
style = ttk.Style()
style.theme_use("clam")

# Stile per pulsanti e etichette
style.configure("TButton", font=("Arial", 8), padding=3)
style.configure("TLabel", font=("Arial", 10), padding=3, background="#f0f0f0")

# Frame principale
main_frame = Frame(root, bg="#e6e6e6")
main_frame.pack(fill="both", expand=True)

# Frame sinistro per l'immagine
left_frame = Frame(main_frame, bg="#e6e6e6", width=600)
left_frame.pack(side="left", fill="both", expand=True)

canvas = Canvas(left_frame, width=500, height=500, bg="#d9d9d9", bd=0)
canvas.pack(pady=20)
image_container = canvas.create_image(0, 0, anchor="nw")

# Frame destro per i tasti e risultati
right_frame = Frame(main_frame, bg="#f0f0f0")
right_frame.pack(side="right", fill="both", expand=True)

camera_selection = StringVar(value="0")
camera_dropdown_label = Label(right_frame, text="Seleziona Videocamera:", bg="#f0f0f0", font=("Arial", 10))
camera_dropdown_label.pack(pady=5)
camera_dropdown = ttk.Combobox(right_frame, textvariable=camera_selection, values=["0", "1", "2"], state="readonly")
camera_dropdown.pack(pady=5)

btn_camera = ttk.Button(right_frame, text="Avvia Videocamera", command=start_camera)
btn_camera.pack(pady=5)

btn_load_image = ttk.Button(right_frame, text="Carica Immagine", command=classify_image)
btn_load_image.pack(pady=5)

btn_capture_image = ttk.Button(right_frame, text="Cattura Immagine", command=capture_image)
btn_capture_image.pack(pady=5)

result_label = ttk.Label(right_frame, text="Classificazione:", justify="left", background="#f0f0f0", anchor="n", font=("Arial", 12, "bold"))
result_label.pack(pady=10, padx=10, fill="both", expand=True)

root.mainloop()
