# Face Verification System

This project implements a face verification system using Flask and facial recognition technology. It allows users to upload reference images and verification images, and it provides an API for verifying the identity based on facial recognition.

## Project Structure

```
face-kyc
├── src
│   ├── face_verify.py          # Main logic for the face verification system
│   ├── templates
│   │   └── index.html          # Main HTML template for the application
│   └── static
│       ├── js
│       │   ├── video-feed.js    # Handles video feed functionality
│       │   └── face-verify.js    # JavaScript functions for face verification
│       └── css
│           └── styles.css       # Styles for the application
├── uploads                      # Directory for storing uploaded images and logs
├── requirements.txt             # Python dependencies for the project
└── README.md                    # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd face-kyc
   ```

2. **Install dependencies:**
   Make sure you have Python and pip installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   Start the Flask server by running:
   ```bash
   python src/face_verify.py
   ```

4. **Access the application:**
   Open your web browser and go to `http://localhost:5000` to access the face verification system.

## Usage

- Upload a clear photo of your face to use as a reference.
- Upload a current photo to verify against the reference.
- You can also use the video feed functionality to capture your face in real-time for verification.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.