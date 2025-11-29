"""
Face recognition utilities using OpenCV LBPH
Compatible with Python 3.13 and no heavy dependencies
"""

import cv2
import numpy as np
import os

class FaceSystem:
    def __init__(self):
        # Load Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Initialize LBPH Face Recognizer
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.is_trained = False
        self.names_map = {}

    def detect_faces(self, img):
        """Detect faces in image and return coordinates"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        return faces, gray

    def train(self, faces, ids, names_map):
        """Train the recognizer with face images"""
        if len(faces) == 0:
            print("⚠️ No training data available")
            return
            
        print(f"🧠 Training on {len(faces)} faces...")
        self.recognizer.train(faces, np.array(ids))
        self.names_map = names_map
        self.is_trained = True
        print("✅ Training complete!")

    def recognize(self, img):
        """Recognize face in image"""
        if not self.is_trained:
            return img, None, 0

        faces, gray = self.detect_faces(img)
        
        recognized_name = None
        confidence_score = 0
        
        for (x, y, w, h) in faces:
            # Predict
            roi_gray = gray[y:y+h, x:x+w]
            try:
                id_, confidence = self.recognizer.predict(roi_gray)
                
                # LBPH confidence: 0 is perfect match, >100 is bad
                # We convert it to a 0-100% score
                if confidence < 100:
                    name = self.names_map.get(id_, "Unknown")
                    confidence_score = round(100 - confidence)
                    
                    if confidence_score > 40:  # Threshold
                        recognized_name = name
                        color = (0, 255, 0)
                        label = f"{name} ({confidence_score}%)"
                    else:
                        color = (0, 0, 255)
                        label = "Unknown"
                else:
                    color = (0, 0, 255)
                    label = "Unknown"
                
                # Draw box
                cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
                cv2.putText(img, label, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
                
            except Exception as e:
                print(f"Prediction error: {e}")

        return img, recognized_name, confidence_score

# Global instance
face_system = FaceSystem()

def detect_and_draw_faces(frame):
    """Wrapper for app.py"""
    return face_system.recognize(frame)

def train_model(faces, ids, names_map):
    """Wrapper for training"""
    face_system.train(faces, ids, names_map)

def get_face_for_registration(img):
    """Extract face for registration"""
    faces, gray = face_system.detect_faces(img)
    if len(faces) == 1:
        (x, y, w, h) = faces[0]
        return gray[y:y+h, x:x+w]
    return None
