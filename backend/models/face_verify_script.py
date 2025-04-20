import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import time

class FaceVerificationSystem:
    def __init__(self, reference_image_path, confidence_threshold=0.6):
        """
        Initialize the face verification system.
        
        Args:
            reference_image_path: Path to the reference image for comparison
            confidence_threshold: Threshold for face similarity (lower = more strict)
        """
        self.confidence_threshold = confidence_threshold
        
        # Load reference image and encode face
        self.reference_image = cv2.imread(reference_image_path)
        if self.reference_image is None:
            raise FileNotFoundError(f"Could not load reference image at {reference_image_path}")
        
        # Convert to RGB (face_recognition uses RGB)
        rgb_reference = cv2.cvtColor(self.reference_image, cv2.COLOR_BGR2RGB)
        
        # Get face encodings from reference image
        face_locations = face_recognition.face_locations(rgb_reference)
        if not face_locations:
            raise ValueError("No face detected in the reference image")
        
        self.reference_encoding = face_recognition.face_encodings(rgb_reference, face_locations)[0]
        
        # Prepare logging
        self.log_file = "verification_log.txt"
        
    def log_verification_attempt(self, result, confidence):
        """Log verification attempts with timestamp, result, and confidence score."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp} - {'SUCCESS' if result else 'FAILED'} - Confidence: {confidence:.4f}\n")
    
    def verify_face(self, frame):
        """
        Compare face in the given frame with the reference face.
        
        Args:
            frame: Current video frame to analyze
            
        Returns:
            tuple: (is_match, confidence_score, display_frame)
        """
        # Convert frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find faces in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        
        # Create a copy of the frame for display
        display_frame = frame.copy()
        
        if not face_locations:
            # No face detected
            cv2.putText(display_frame, "No face detected", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return False, 0.0, display_frame
        
        # If multiple faces found, use the largest face (closest to camera)
        if len(face_locations) > 1:
            # Find the largest face by area
            largest_area = 0
            largest_face_idx = 0
            
            for i, (top, right, bottom, left) in enumerate(face_locations):
                area = (bottom - top) * (right - left)
                if area > largest_area:
                    largest_area = area
                    largest_face_idx = i
                    
            face_locations = [face_locations[largest_face_idx]]
            
        # Get face encodings
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        # Get location of the detected face
        top, right, bottom, left = face_locations[0]
        
        # Compare faces
        face_distances = face_recognition.face_distance([self.reference_encoding], face_encodings[0])
        match_score = 1 - face_distances[0]  # Convert distance to similarity score
        
        # Determine if it's a match
        is_match = match_score >= self.confidence_threshold
        
        # Draw rectangles around faces
        if is_match:
            # Green for match
            color = (0, 255, 0)
            result_text = "VERIFIED"
        else:
            # Red for no match
            color = (0, 0, 255)
            result_text = "NOT VERIFIED"
            
        # Draw bounding box
        cv2.rectangle(display_frame, (left, top), (right, bottom), color, 2)
        
        # Display result and confidence
        cv2.putText(display_frame, result_text, (left, top - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(display_frame, f"Confidence: {match_score:.2f}", (left, bottom + 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
        # Log the verification attempt
        self.log_verification_attempt(is_match, match_score)
        
        return is_match, match_score, display_frame
    
    def run_verification(self):
        """
        Run the face verification system on a live video feed.
        Press 'q' to quit.
        """
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        verification_status = "Place your face in the frame"
        last_verification_time = 0
        verification_interval = 1  # Seconds between verifications
        
        while True:
            # Read frame
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            current_time = time.time()
            if current_time - last_verification_time >= verification_interval:
                # Time to verify
                is_match, confidence, display_frame = self.verify_face(frame)
                last_verification_time = current_time
                
                if is_match:
                    verification_status = f"VERIFIED (Confidence: {confidence:.2f})"
                else:
                    verification_status = f"NOT VERIFIED (Confidence: {confidence:.2f})"
            else:
                # Just display the frame with the last verification status
                display_frame = frame.copy()
            
            # Show status on frame
            cv2.putText(display_frame, verification_status, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # Display the frame
            cv2.imshow("Face Verification", display_frame)
            
            # Break loop on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        # Release resources
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Example usage
    reference_image = "reference_image.jpg"  # Path to the user's reference image
    
    # Check if reference image exists
    if not os.path.exists(reference_image):
        print(f"Error: Reference image not found at {reference_image}")
        print("Please place a clear frontal face image named 'reference_image.jpg' in the same directory")
        exit(1)
    
    try:
        # Initialize and run the verification system
        verifier = FaceVerificationSystem(reference_image, confidence_threshold=0.3)
        print("Face verification system started. Press 'q' to quit.")
        verifier.run_verification()
    except Exception as e:
        print(f"Error: {str(e)}")