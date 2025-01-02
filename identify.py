import cv2
import face_recognition
import sqlite3
import numpy as np


class DatabaseFaceRecognition:
    def __init__(self, db_path='face_recognition.db'):
        self.known_face_encodings = []
        self.known_face_metadata = []
        self.load_database(db_path)

    def load_database(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, age, encoding FROM users")
        users = cursor.fetchall()

        for user in users:
            name, age, db_encoding = user
            face_encoding = np.frombuffer(db_encoding, dtype=np.float64)
            self.known_face_encodings.append(face_encoding)
            self.known_face_metadata.append({
                'name': name,
                'age': age
            })
        conn.close()

    def get_user_info(self, frame, tolerance=0.6):
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        detected_users = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=tolerance)
            user_info = {'name': 'Unknown', 'age': 'N/A'}

            if True in matches:
                first_match_index = matches.index(True)
                user_info = self.known_face_metadata[first_match_index]
                detected_users.append(user_info)

        return detected_users, [(top * 4, right * 4, bottom * 4, left * 4) for (top, right, bottom, left) in
                                face_locations]


def identify_user():
    sfr = DatabaseFaceRecognition()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera")
        return None

    print("Looking for face... Press ESC to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Get user info and face locations from the frame
        users, face_locations = sfr.get_user_info(frame)

        # Draw rectangles around faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 200), 2)

        # Show the frame
        cv2.imshow("Face Recognition", frame)

        # If we found a matching user, return their info
        if users and users[0]['name'] != 'Unknown':
            cap.release()
            cv2.destroyAllWindows()
            return users[0]

        # Check for ESC key
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return {"name": "Unknown", "age": "N/A"}


if __name__ == "__main__":
    user_info = identify_user()
    if user_info:
        print("\nUser Information:")
        print(f"Name: {user_info['name']}")
        print(f"Age: {user_info['age']}")
    else:
        print("No face detected or error occurred.")