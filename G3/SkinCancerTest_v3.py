import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv
import hashlib
import cv2
import numpy as np
from PIL import Image, ImageTk
from tkinter import StringVar
import threading
import tensorflow as tf
import pandas as pd  # Importing pandas

# Global variables for camera and model
global result_label, cap, camera_thread, interpreter, camera_selection

result_label = None
cap = None
camera_thread = None
camera_selection = None  # Declare camera_selection globally
# Load the TFLite model
interpreter = tf.lite.Interpreter(model_path=r"C:\Users\david\OneDrive\Desktop\G3\skin_cancer_best_model.tflite")
interpreter.allocate_tensors()

# Get tensor details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Define model classes
class_labels = ['Actinic Keratoses and\n Intraepithelial Carcinoma', 'Basal Cell Carcinoma', 
                'Benign Keratosis-like Lesions', 'Dermatofibroma', 'Melanoma', 
                'Melanocytic Nevi (nei)', 'Vascular Lesions']

# Global variable for captured image
captured_image = None
captured_frame = None
camera_running = False

# Function to preprocess the image
def preprocess_image(image):
    image = Image.fromarray(image).convert("RGB")
    image = image.resize((224, 224))  # Size used for training
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0).astype(np.float32)  # Add batch dimension
    return image_array

# Function to classify and display results for loaded image
def classify_image():
    global captured_image
    image_path = filedialog.askopenfilename()
    if image_path:
        # Preprocess the image
        image = Image.open(image_path).convert("RGB")
        image_array = preprocess_image(np.array(image))
        
        # Set input tensor for interpreter
        interpreter.set_tensor(input_details[0]['index'], image_array)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_details[0]['index'])[0]
        
        # Display image
        img = image.resize((500, 500))
        img_tk = ImageTk.PhotoImage(img)
        canvas.itemconfig(image_container, image=img_tk)
        canvas.image = img_tk  # Avoid image garbage collection
        captured_image = img_tk
        
        # Show results
        result_text = "Classification:\n"
        for label, prob in zip(class_labels, predictions):
            result_text += f"{label}: {prob * 100:.2f}%\n"
        
        result_label.config(text=result_text)
        
        # Save results to CSV
        results_df = pd.DataFrame({'Class': class_labels, 'Probability': predictions * 100})
        results_df.to_csv('classification_results.csv', index=False)

# Function to classify and display results for each frame
def classify_frame(frame):
    image_array = preprocess_image(frame)
    interpreter.set_tensor(input_details[0]['index'], image_array)
    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0]['index'])[0]
    
    result_text = "Classification:\n"
    for label, prob in zip(class_labels, predictions):
        result_text += f"{label}: {prob * 100:.2f}%\n"
    
    result_label.config(text=result_text)

# Function to capture an image from the camera
def capture_image():
    global captured_image, captured_frame, camera_running
    camera_running = False  # Stop camera feed
    selected_camera = int(camera_selection.get())  # Use the global camera_selection
    cap = cv2.VideoCapture(selected_camera)
    ret, frame = cap.read()
    if ret:
        captured_frame = frame  # Store captured frame
        cv2.imwrite("captured_image.jpg", frame)
        print("Captured image saved as 'captured_image.jpg'")
        # Show captured image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((500, 500))
        img_tk = ImageTk.PhotoImage(img)
        canvas.itemconfig(image_container, image=img_tk)
        canvas.image = img_tk
        captured_image = img_tk
    cap.release()

# Declare canvas and image_container globally
canvas = None
image_container = None

# Function to start the camera feed
def start_camera():
    global captured_image, captured_frame, camera_running, canvas, image_container
    camera_running = True  # Set camera state
    selected_camera = int(camera_selection.get())  # Use the global camera_selection
    captured_image = None  # Reset captured image
    captured_frame = None  # Reset captured frame
    cap = cv2.VideoCapture(selected_camera)
    
    def update_frame():
        global canvas, image_container
        if camera_running and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                # Resize and display frame in Tkinter if no image is captured
                if captured_image is None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img = img.resize((500, 500))
                    img_tk = ImageTk.PhotoImage(img)
                    canvas.itemconfig(image_container, image=img_tk)
                    canvas.image = img_tk
                    
                    # Classify frame
                    classify_frame(frame_rgb)
            
            root.after(10, update_frame)  # Update frame every 10 ms
        else:
            cap.release()

    update_frame()  # Start frame update

# Function to show the camera screen after login
def show_camera_screen(user_name, user_role):
    global canvas, image_container
    for widget in root.winfo_children():
        widget.destroy()

    camera_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
    camera_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(camera_frame, text=f"Welcome {user_name}, Role: {user_role}", font=("Arial", 16), bg='#f0f0f0', fg="#333").pack(pady=20)

    global camera_selection
    # Camera selection dropdown
    camera_selection = StringVar(value="0")
    camera_dropdown_label = tk.Label(camera_frame, text="Select Camera:", bg="#ffffff", font=("Arial", 12))
    camera_dropdown_label.pack(pady=5)

    camera_dropdown = ttk.Combobox(camera_frame, textvariable=camera_selection, values=["0", "1", "2"], state="readonly")
    camera_dropdown.pack(pady=10)

    # Buttons for camera actions
    btn_camera = ttk.Button(camera_frame, text="Start Camera", command=start_camera)
    btn_camera.pack(pady=10)

    btn_load_image = ttk.Button(camera_frame, text="Load Image", command=classify_image)
    btn_load_image.pack(pady=10)

    btn_capture_image = ttk.Button(camera_frame, text="Capture Image", command=capture_image)
    btn_capture_image.pack(pady=10)

    stop_camera_button = ttk.Button(camera_frame, text="Stop Camera", command=stop_camera)
    stop_camera_button.pack(pady=10)

    global result_label
    result_label = ttk.Label(camera_frame, text="Classification:", justify="left", background="#ffffff", anchor="n", font=("Arial", 12, "bold"))
    result_label.pack(pady=20, padx=10, fill="both", expand=True)

    # Create a canvas for displaying the image
    canvas = tk.Canvas(camera_frame, width=500, height=500)
    canvas.pack(pady=20)
    image_container = canvas.create_image(250, 250, anchor=tk.CENTER)


# Function to stop the camera
def stop_camera():
    global camera_running
    camera_running = False

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function for user registration
def register_user(name, role, email, password):
    hashed_password = hash_password(password)
    with open('users.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, role, email, hashed_password])
    messagebox.showinfo("Registration", "Registration successful!")

# Login callback function
def login_callback(email_entry, password_entry):
    email = email_entry.get()
    password = password_entry.get()

    if not email or not password:
        messagebox.showerror("Error", "Email and Password are required!")
        return

    hashed_password = hash_password(password)
    
    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[2] == email and row[3] == hashed_password:
                user_role = row[1]
                user_name = row[0]
                show_camera_screen(user_name, user_role)  # Switch to the camera screen
                return
    messagebox.showerror("Error", "Invalid credentials!")


# Function to show the registration screen
def show_registration_screen():
    for widget in root.winfo_children():
        widget.destroy()

    register_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
    register_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(register_frame, text="Registration", font=("Arial", 16), bg='#f0f0f0', fg="#333").pack(pady=20)

    tk.Label(register_frame, text="Name:", bg="#ffffff", font=("Arial", 12)).pack(pady=5)
    name_entry = tk.Entry(register_frame, font=("Arial", 12))
    name_entry.pack(pady=5)

    tk.Label(register_frame, text="Role (Admin/Medico/User/Guest):", bg="#ffffff", font=("Arial", 12)).pack(pady=5)
    role_entry = tk.Entry(register_frame, font=("Arial", 12))
    role_entry.pack(pady=5)

    tk.Label(register_frame, text="Email:", bg="#ffffff", font=("Arial", 12)).pack(pady=5)
    email_entry = tk.Entry(register_frame, font=("Arial", 12))
    email_entry.pack(pady=5)

    tk.Label(register_frame, text="Password:", bg="#ffffff", font=("Arial", 12)).pack(pady=5)
    password_entry = tk.Entry(register_frame, font=("Arial", 12), show="*")
    password_entry.pack(pady=5)

    def register_action():
        name = name_entry.get()
        role = role_entry.get()
        email = email_entry.get()
        password = password_entry.get()
        if name and role and email and password:
            register_user(name, role, email, password)
        else:
            messagebox.showerror("Error", "All fields are required!")

    register_button = ttk.Button(register_frame, text="Register", command=register_action)
    register_button.pack(pady=20)

# Main function to run the application
def main():
    global root
    root = tk.Tk()
    root.title("Skin Cancer Classification")
    root.geometry("800x600")

    login_frame = tk.Frame(root)
    login_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(login_frame, text="Login", font=("Arial", 16), bg='#f0f0f0', fg="#333").pack(pady=20)

    tk.Label(login_frame, text="Email:", bg="#ffffff", font=("Arial", 12)).pack(pady=5)
    email_entry = tk.Entry(login_frame, font=("Arial", 12))
    email_entry.pack(pady=5)

    tk.Label(login_frame, text="Password:", bg="#ffffff", font=("Arial", 12)).pack(pady=5)
    password_entry = tk.Entry(login_frame, font=("Arial", 12), show="*")
    password_entry.pack(pady=5)

    login_button = ttk.Button(login_frame, text="Login", command=lambda: login_callback(email_entry, password_entry))
    login_button.pack(pady=20)

    register_button = ttk.Button(login_frame, text="Register", command=show_registration_screen)
    register_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
