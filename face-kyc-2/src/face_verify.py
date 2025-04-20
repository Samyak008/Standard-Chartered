import os
import cv2
import numpy as np
import face_recognition
import base64
import time
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, Response
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
        try:
            # Find faces in both images
            reference_face_locations = face_recognition.face_locations(reference_image)
            verify_face_locations = face_recognition.face_locations(verify_image)
            
            if not reference_face_locations or not verify_face_locations:
                return {
                    "success": True,
                    "is_match": False,
                    "error": "No face detected in one or both images"
                }
            
            # Get the largest face from each image
            reference_face = self._get_largest_face(reference_face_locations, reference_image)
            verify_face = self._get_largest_face(verify_face_locations, verify_image)
            
            # Get face encodings
            reference_encoding = face_recognition.face_encodings(reference_image, [reference_face])[0]
            verify_encoding = face_recognition.face_encodings(verify_image, [verify_face])[0]
            
            # Compare faces
            face_distance = face_recognition.face_distance([reference_encoding], verify_encoding)[0]
            is_match = float(face_distance) < 0.6
            confidence = (1 - float(face_distance)) * 100
            
            # Annotate images
            reference_annotated = self._annotate_image(reference_image, reference_face, is_match)
            verify_annotated = self._annotate_image(verify_image, verify_face, is_match)
            
            # Convert annotated images to base64
            _, ref_buffer = cv2.imencode('.jpg', reference_annotated)
            _, ver_buffer = cv2.imencode('.jpg', verify_annotated)
            
            ref_base64 = base64.b64encode(ref_buffer).decode('utf-8')
            ver_base64 = base64.b64encode(ver_buffer).decode('utf-8')
            
            return {
                "success": True,
                "is_match": bool(is_match),
                "confidence": float(confidence),
                "reference_image": f"data:image/jpeg;base64,{ref_base64}",
                "verify_image": f"data:image/jpeg;base64,{ver_base64}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
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
        if request.content_type.startswith('multipart/form-data'):
            # Handle form data
            if 'reference' not in request.files or 'verify' not in request.files:
                return jsonify({
                    "success": False,
                    "error": "Missing required files: 'reference' and 'verify'"
                }), 400

            reference_file = request.files['reference']
            verify_file = request.files['verify']

            # Read and decode images
            reference_bytes = reference_file.read()
            verify_bytes = verify_file.read()

            # Convert to numpy arrays
            reference_np = np.frombuffer(reference_bytes, np.uint8)
            verify_np = np.frombuffer(verify_bytes, np.uint8)

            # Decode images
            reference_image = cv2.imdecode(reference_np, cv2.IMREAD_COLOR)
            verify_image = cv2.imdecode(verify_np, cv2.IMREAD_COLOR)

            # Convert from BGR to RGB
            reference_image = cv2.cvtColor(reference_image, cv2.COLOR_BGR2RGB)
            verify_image = cv2.cvtColor(verify_image, cv2.COLOR_BGR2RGB)

        else:
            # Handle JSON data
            data = request.get_json()
            if 'reference' not in data or 'verify' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing required fields: 'reference' and 'verify'"
                }), 400

            reference_image = decode_base64_image(data['reference'])
            verify_image = decode_base64_image(data['verify'])

        # Initialize face verifier and perform verification
        verifier = FaceVerifier()
        result = verifier.verify_faces(reference_image, verify_image)
        
        return jsonify(result)

    except Exception as e:
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
    return render_template('index.html')

def gen_frames():
    """Generate video frames from webcam"""
    camera = cv2.VideoCapture(0)
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        camera.release()

@app.route('/video_feed')
def video_feed():
    """Stream video feed from webcam"""
    return Response(
        gen_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)