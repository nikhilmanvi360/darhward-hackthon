"""
Camera module for capturing images and video feed
Handles OpenCV webcam operations
"""

import cv2
import time

class Camera:
    """Webcam handler class"""
    
    def __init__(self, camera_index=0):
        """
        Initialize camera
        
        Args:
            camera_index: Camera device index (default 0)
        """
        self.camera_index = camera_index
        self.cap = None
    
    def start(self):
        """Start camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                print("❌ Failed to open camera")
                return False
            
            # Set camera properties for better quality
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            print("✅ Camera started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error starting camera: {e}")
            return False
    
    def read_frame(self):
        """
        Read a single frame from camera
        
        Returns:
            frame: Image array or None if failed
        """
        if self.cap is None or not self.cap.isOpened():
            print("❌ Camera not started")
            return None
        
        ret, frame = self.cap.read()
        
        if ret:
            return frame
        else:
            print("❌ Failed to read frame")
            return None
    
    def capture_images(self, num_images=25, delay=0.1):
        """
        Capture multiple images for face registration
        
        Args:
            num_images: Number of images to capture
            delay: Delay between captures in seconds
        
        Returns:
            list: List of captured image frames
        """
        images = []
        
        if not self.start():
            return images
        
        print(f"📸 Capturing {num_images} images...")
        print("Please move your face slightly for different angles")
        
        # Warm up camera
        for _ in range(5):
            self.read_frame()
            time.sleep(0.1)
        
        for i in range(num_images):
            frame = self.read_frame()
            
            if frame is not None:
                images.append(frame.copy())
                print(f"Captured {i+1}/{num_images}")
                
                # Show preview
                cv2.imshow('Registration - Press Q to cancel', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("⚠️ Capture cancelled by user")
                    break
                
                time.sleep(delay)
        
        self.stop()
        cv2.destroyAllWindows()
        
        print(f"✅ Captured {len(images)} images")
        return images
    
    def live_recognition(self, process_frame_callback):
        """
        Start live face recognition feed
        
        Args:
            process_frame_callback: Function to process each frame
                                  Should return (processed_frame, recognized_name, confidence)
        
        Returns:
            str: Name of recognized person or None
        """
        if not self.start():
            return None
        
        print("🎥 Starting live recognition...")
        print("Press 'Q' to quit")
        
        recognized_person = None
        recognition_count = 0
        required_recognitions = 3  # Require 3 consecutive recognitions
        
        while True:
            frame = self.read_frame()
            
            if frame is None:
                break
            
            # Process frame with callback
            processed_frame, name, confidence = process_frame_callback(frame)
            
            # Display instructions
            cv2.putText(processed_frame, "Press 'Q' to quit", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('AI Attendance System - Live Recognition', processed_frame)
            
            # Track consecutive recognitions
            if name and confidence > 0.6:
                if name == recognized_person:
                    recognition_count += 1
                else:
                    recognized_person = name
                    recognition_count = 1
                
                # Auto-close after successful recognition
                if recognition_count >= required_recognitions:
                    print(f"✅ Recognized: {recognized_person} (Confidence: {confidence*100:.1f}%)")
                    time.sleep(1)  # Show result briefly
                    break
            else:
                recognition_count = 0
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("⚠️ Recognition cancelled by user")
                recognized_person = None
                break
        
        self.stop()
        cv2.destroyAllWindows()
        
        return recognized_person
    
    def stop(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            print("✅ Camera stopped")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.stop()

def test_camera():
    """Test camera functionality"""
    cam = Camera()
    
    if cam.start():
        print("Camera test successful!")
        
        for i in range(30):
            frame = cam.read_frame()
            if frame is not None:
                cv2.imshow('Camera Test - Press Q to quit', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        cam.stop()
        cv2.destroyAllWindows()
    else:
        print("Camera test failed!")

if __name__ == "__main__":
    test_camera()
