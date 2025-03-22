import os
import cv2
import numpy as np
import face_recognition
import base64
import time
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
CONFIDENCE_THRESHOLD = 0.6

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class FaceVerifier:
    def __init__(self, confidence_threshold=CONFIDENCE_THRESHOLD):
        """Initialize face verification system with confidence threshold."""
        self.confidence_threshold = confidence_threshold
        self.log_file = os.path.join(UPLOAD_FOLDER, "verification_log.txt")
        
    def log_verification_attempt(self, result, confidence, user_id="anonymous"):
        """Log verification attempts with timestamp, result, and confidence score."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp} - {user_id} - {'SUCCESS' if result else 'FAILED'} - Confidence: {confidence:.4f}\n")
    
    def verify_faces(self, reference_image, verify_image):
        """
        Compare faces in two images and determine if they match.
        
        Args:
            reference_image: Image containing the reference face
            verify_image: Image to verify against the reference
            
        Returns:
            dict: Result with match status and confidence score
        """
        # Find faces in reference image
        ref_face_locations = face_recognition.face_locations(reference_image)
        
        if not ref_face_locations:
            return {
                "success": False,
                "error": "No face detected in reference image",
                "is_match": False,
                "confidence": 0.0
            }
        
        # Get the largest face in reference image
        ref_face_location = self._get_largest_face(ref_face_locations, reference_image)
        ref_encoding = face_recognition.face_encodings(reference_image, [ref_face_location])[0]
        
        # Find faces in verification image
        verify_face_locations = face_recognition.face_locations(verify_image)
        
        if not verify_face_locations:
            return {
                "success": False,
                "error": "No face detected in verification image",
                "is_match": False,
                "confidence": 0.0
            }
        
        # Get the largest face in verification image
        verify_face_location = self._get_largest_face(verify_face_locations, verify_image)
        verify_encoding = face_recognition.face_encodings(verify_image, [verify_face_location])[0]
        
        # Calculate face distance (lower = more similar)
        face_distances = face_recognition.face_distance([ref_encoding], verify_encoding)
        match_score = 1 - face_distances[0]  # Convert distance to similarity score
        
        # Determine if it's a match
        is_match = match_score >= self.confidence_threshold
        confidence_percentage = float(match_score * 100)
        
        # Log the verification attempt
        self.log_verification_attempt(is_match, match_score)
        
        return {
            "success": True,
            "is_match": is_match,
            "confidence": confidence_percentage
        }
    
    def _get_largest_face(self, face_locations, image):
        """Find the largest face in the image by area."""
        if len(face_locations) == 1:
            return face_locations[0]
            
        largest_area = 0
        largest_face = face_locations[0]
        
        for face_location in face_locations:
            top, right, bottom, left = face_location
            area = (bottom - top) * (right - left)
            
            if area > largest_area:
                largest_area = area
                largest_face = face_location
                
        return largest_face
        
    def _annotate_image(self, image, face_location, is_match):
        """Annotate image with face detection and verification result."""
        # Create a copy of the image
        annotated = image.copy()
        
        # Convert from RGB to BGR for OpenCV
        annotated = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
        
        # Extract face location
        top, right, bottom, left = face_location
        
        # Set color based on match result (green for match, red for no match)
        color = (0, 255, 0) if is_match else (0, 0, 255)
        
        # Draw rectangle around face
        cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)
        
        # Add label
        text = "VERIFIED" if is_match else "NOT VERIFIED"
        cv2.putText(annotated, text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return annotated

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def decode_base64_image(base64_string):
    """Decode a base64 image string to OpenCV format."""
    # Check if the string contains a data URL prefix
    if "data:image" in base64_string and ";base64," in base64_string:
        # Remove the data URL prefix
        base64_string = re.sub(r'data:image/[^;]+;base64,', '', base64_string)
    
    # Decode base64 string
    image_data = base64.b64decode(base64_string)
    
    # Convert to numpy array
    nparr = np.frombuffer(image_data, np.uint8)
    
    # Decode image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Convert from BGR to RGB (face_recognition uses RGB)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    return image_rgb

@app.route('/api/verify-face', methods=['POST'])
def verify_face():
    """API endpoint to verify faces in two images."""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Check if required fields are present
        if 'reference' not in data or 'verify' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required fields: 'reference' and 'verify'"
            }), 400
        
        # Get base64 image strings
        reference_base64 = data['reference']
        verify_base64 = data['verify']
        
        # Decode base64 images
        try:
            reference_image = decode_base64_image(reference_base64)
            verify_image = decode_base64_image(verify_base64)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to decode images: {str(e)}"
            }), 400
        
        # Initialize face verifier
        verifier = FaceVerifier()
        
        # Perform verification
        result = verifier.verify_faces(reference_image, verify_image)
        
        return jsonify(result)
    
    except Exception as e:
        # Log the error
        print(f"Error in verification: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Verification failed: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

# For testing purposes
@app.route('/', methods=['GET'])
def index():
    return """
    <html>
        <head>
            <title>Face Verification API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #4361ee; }
                code { background-color: #f5f5f5; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>Face Verification API</h1>
            <p>Use the <code>/api/verify-face</code> endpoint to verify faces.</p>
            <p>Send a POST request with the following JSON structure:</p>
            <pre>{
    "reference": "base64_encoded_reference_image",
    "verify": "base64_encoded_verification_image"
}</pre>
            <p>Check the <code>/api/health</code> endpoint to verify the API is running.</p>
        </body>
    </html>
    """

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)