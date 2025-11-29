"""
Liveness Detection Module using OpenCV
Simplified approach: Time-based verification with face quality check
"""

import cv2
import numpy as np
import time

class LivenessDetector:
    def __init__(self):
        # State variables
        self.verification_start_time = None
        self.is_verified = False
        self.required_duration = 2.0  # 2 seconds of stable face detection
        
    def check_face_quality(self, face_roi):
        """
        Check if face is real using Laplacian Variance (Blur detection)
        Real faces usually have more high-frequency detail than screens/photos
        """
        try:
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Thresholds: >50 is likely real
            return variance > 50
        except:
            return True

    def verify_liveness(self, face_roi):
        """
        Simplified verification: Just maintain face in frame for 2 seconds
        Returns: (status_message, is_verified)
        """
        # Check face quality
        if not self.check_face_quality(face_roi):
            self.verification_start_time = None
            return "⚠️ Face quality too low", False

        current_time = time.time()
        
        # Start timer if not already started
        if self.verification_start_time is None:
            self.verification_start_time = current_time
            return "👤 Hold still...", False
        
        # Check if enough time has passed
        elapsed = current_time - self.verification_start_time
        
        if elapsed >= self.required_duration:
            self.is_verified = True
            return "✅ Verified!", True
        else:
            remaining = self.required_duration - elapsed
            return f"👤 Hold still... {remaining:.1f}s", False

    def reset(self):
        """Reset verification state"""
        self.verification_start_time = None
        self.is_verified = False

# Global instance
liveness_detector = LivenessDetector()
