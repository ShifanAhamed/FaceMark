"""
Face Recognition Utilities
Handles face encoding, recognition, and student management
"""

import cv2
import pickle
import os
import numpy as np

class FaceUtils:
    def __init__(self):
        """Initialize face recognition utilities"""
        self.known_face_images = []
        
        self.known_face_names = []
        self.encodings_file = os.path.join("face_encodings", "face_data.pkl")
        
        # ✅ Use OpenCV's built-in haarcascade path (cross-platform safe)
        self.face_cascade = cv2.CascadeClassifier(
            os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        )

        # Ensure directories exist
        os.makedirs("face_encodings", exist_ok=True)
        os.makedirs("student_images", exist_ok=True)

    def load_encodings(self):
        """Load face data from file"""
        try:
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_images = data.get('images', [])
                    self.known_face_names = data.get('names', [])
                print(f"📂 Loaded {len(self.known_face_names)} known faces")
            else:
                print("ℹ️ No existing face data found")
        except Exception as e:
            print(f"❌ Error loading face data: {e}")
            self.known_face_images = []
            self.known_face_names = []

    def save_encodings(self):
        """Save face data to file"""
        try:
            os.makedirs(os.path.dirname(self.encodings_file), exist_ok=True)
            data = {
                'images': self.known_face_images,
                'names': self.known_face_names
            }
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(data, f)
            print("💾 Face data saved successfully")
        except Exception as e:
            print(f"❌ Error saving face data: {e}")

    def add_known_face(self, name, face_image):
        """Add a new known face to the system"""
        try:
            if name in self.known_face_names:
                print(f"⚠️ Student {name} already exists")
                return False

            # Convert face image to grayscale & resize
            gray_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            resized_face = cv2.resize(gray_face, (100, 100))

            # Store
            self.known_face_images.append(resized_face)
            self.known_face_names.append(name)

            # Save student image
            student_image_path = os.path.join("student_images", f"{name}.jpg")
            cv2.imwrite(student_image_path, face_image)

            # Save encodings
            self.save_encodings()

            print(f"✅ Added new student: {name}")
            return True

        except Exception as e:
            print(f"❌ Error adding known face: {e}")
            return False

    def recognize_face(self, face_region, threshold=30.0):
        """
        Recognize a face by comparing with known faces using template matching.
        Returns recognized name or "Unknown".
        threshold: lower = stricter matching
        """
        try:
            if len(self.known_face_images) == 0:
                return "Unknown"

            # Convert to grayscale & resize
            gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            resized_face = cv2.resize(gray_face, (100, 100))

            best_match_score = float('inf')
            best_match_name = "Unknown"

            # Compare with each known face
            for i, known_face in enumerate(self.known_face_images):
                diff = cv2.absdiff(resized_face, known_face)
                score = np.mean(diff)  # mean pixel difference

                if score < best_match_score:
                    best_match_score = score
                    best_match_name = self.known_face_names[i]

            # ✅ threshold tuned for pixel-diff (30–50 usually works)
            if best_match_score < threshold:
                return best_match_name
            else:
                return "Unknown"

        except Exception as e:
            print(f"❌ Error in face recognition: {e}")
            return "Unknown"

    def get_enrolled_students(self):
        """Get list of all enrolled students"""
        return self.known_face_names.copy()

    def delete_student(self, student_name):
        """Delete a student from the system"""
        try:
            if student_name in self.known_face_names:
                index = self.known_face_names.index(student_name)

                # Remove
                self.known_face_names.pop(index)
                self.known_face_images.pop(index)

                # Save updated data
                self.save_encodings()

                # Delete stored image
                image_path = os.path.join("student_images", f"{student_name}.jpg")
                if os.path.exists(image_path):
                    os.remove(image_path)

                print(f"🗑️ Deleted student: {student_name}")
                return True
            else:
                print(f"⚠️ Student {student_name} not found")
                return False

        except Exception as e:
            print(f"❌ Error deleting student: {e}")
            return False

    def update_student_image(self, student_name, new_face_image):
        """Update face image for existing student"""
        try:
            if student_name in self.known_face_names:
                index = self.known_face_names.index(student_name)

                # Process new image
                gray_face = cv2.cvtColor(new_face_image, cv2.COLOR_BGR2GRAY)
                resized_face = cv2.resize(gray_face, (100, 100))

                self.known_face_images[index] = resized_face

                # Save image
                student_image_path = os.path.join("student_images", f"{student_name}.jpg")
                cv2.imwrite(student_image_path, new_face_image)

                # Save encodings
                self.save_encodings()
                print(f"🔄 Updated image for student: {student_name}")
                return True
            else:
                print(f"⚠️ Student {student_name} not found")
                return False

        except Exception as e:
            print(f"❌ Error updating student image: {e}")
            return False
