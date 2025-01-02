import cv2
import face_recognition
import sqlite3
import os
from datetime import datetime

def register_user(name, age, image_path, email=None, phone=None):
    try:
        # Load and encode the face
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        
        if not face_encodings:
            print(f"No face found in the image for {name}")
            return False
            
        face_encoding = face_encodings[0]

        # Connect to database
        conn = sqlite3.connect('face_recognition.db')
        cursor = conn.cursor()

        # Insert user data with new fields
        cursor.execute('''
            INSERT INTO users 
            (name, age, email, phone, image_path, face_encoding)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            name,
            age,
            email,
            phone,
            image_path,
            face_encoding.tobytes()
        ))
        
        conn.commit()
        conn.close()
        
        print(f"Successfully registered {name}")
        return True
        
    except Exception as e:
        print(f"Error registering {name}: {str(e)}")
        return False

def register_sample_users():
    # Create images directory if it doesn't exist
    if not os.path.exists('images'):
        os.makedirs('images')
        print("Please add user images to the 'images' folder")
        return

    # Register sample users with additional information
    users = [
        {
            "name": "Ndamulelo",
            "age": 20,
            "image_path": "images/ndamu.jpg",
            "email": "ndamu@example.com",
            "phone": "+1234567890"
        },
        {
            "name": "Pfano",
            "age": 18,
            "image_path": "images/pfano.jpg",
            "email": "pfano@example.com",
            "phone": "+0987654321"
        }
    ]

    for user in users:
        if os.path.exists(user["image_path"]):
            register_user(
                name=user["name"],
                age=user["age"],
                image_path=user["image_path"],
                email=user["email"],
                phone=user["phone"]
            )
        else:
            print(f"Image not found: {user['image_path']}")

if __name__ == "__main__":
    register_sample_users()