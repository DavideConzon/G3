import sqlite3
from hashlib import sha256

class Database:
    def __init__(self, db_path="app_data.db"):
        """
        Initialize the database connection and create necessary tables.
        """
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """
        Create the database tables if they do not already exist.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create the users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """)
        
        # Create the patients table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            data_nascita TEXT,
            sesso TEXT,
            codice_fiscale TEXT UNIQUE,
            indirizzo TEXT,
            telefono TEXT,
            email TEXT,
            patologie_precedenti TEXT,
            farmaci_assunti TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        
        conn.commit()
        conn.close()

    @staticmethod
    def _hash_password(password):
        """
        Hash the given password using SHA-256.
        """
        return sha256(password.encode("utf-8")).hexdigest()

    def register_user(self, name, role, email, password):
        """
        Register a new user in the database.
        Returns True if successful, False if email already exists.
        """
        try:
            hashed_password = self._hash_password(password)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, role, email, password) VALUES (?, ?, ?, ?)", 
                           (name, role, email, hashed_password))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, email, password):
        """
        Authenticate a user by email and password.
        Returns user details (name, role) if authentication is successful, None otherwise.
        """
        hashed_password = self._hash_password(password)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, role FROM users WHERE email = ? AND password = ?", 
                       (email, hashed_password))
        user = cursor.fetchone()
        conn.close()
        return user

    def add_patient(self, nome, cognome, data_nascita, sesso, codice_fiscale, indirizzo, telefono, email, patologie_precedenti, farmaci_assunti, user_id):
        """
        Add a new patient to the database and associate it with an existing user.
        Returns True if successful, False if codice_fiscale already exists.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO patients (nome, cognome, data_nascita, sesso, codice_fiscale, indirizzo, telefono, email, patologie_precedenti, farmaci_assunti, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, cognome, data_nascita, sesso, codice_fiscale, indirizzo, telefono, email, patologie_precedenti, farmaci_assunti, user_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_users(self):
        """
        Retrieve all users from the database.
        Returns a list of tuples containing user id and name.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users")
        users = cursor.fetchall()
        conn.close()
        return users

    def get_patients_by_user(self, user_id):
        """
        Retrieve all patients associated with a specific user.
        Returns a list of patient details.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,))
        patients = cursor.fetchall()
        conn.close()
        return patients
