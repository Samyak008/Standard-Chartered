# Virtual Branch Manager

This project is an AI-powered Virtual Branch Manager designed to assist users with personal credit management. It features a backend built with Python (using FastAPI or Flask) and a frontend developed in React. The application includes functionalities for user authentication, document uploads for OCR processing, and AI-driven eligibility checks.

## Team Algonomics (Team ZOZO presents Loan Genie)
- Aagam Chhajer   (RA2211047010110)
- Abha Shukla     (RA2211003011829)
- Srivathsan B    (RA2211003011199)
- Tamanna Grover  (RA2211003010376)
- Samyak Varia    (RA2211003011202)
- Shivnarayan S   (RA2211003011216)

## Demo Video

[![Watch the video](https://img.youtube.com/vi/ijWl9wbVsyI/0.jpg)](https://www.youtube.com/watch?v=ijWl9wbVsyI)
GDrive Link 
https://drive.google.com/file/d/1b3MNtTZ29jtb5XrJIY12m6fLqrrxoWd_/view?usp=sharing


## Project Structure

```
standard-chartered/
├── backend/
│   ├── app.py                 # Main FastAPI application
│   ├── controllers/
│   │   ├── user_controller.py
│   │   ├── loan_controller.py
│   │   └── video_kyc_controller.py
│   ├── models/
│   │   ├── user.py
│   │   ├── loan.py
│   │   └── kyc.py
│   ├── services/
│   │   ├── ocr_service.py
│   │   ├── ai_service.py
│   │   └── webrtc_service.py
│   ├── ml_models/
│   │   ├── loan_predictor.py
│   │   └── face_detector.py
│   └── utils/
│       └── helpers.py
│
├── next-frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── admin-dashboard/
│   │   │   ├── user-dashboard/
│   │   │   │   ├── kyc/
│   │   │   │   └── loan/
│   │   │   └── layout.js
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   ├── loan/
│   │   │   └── kyc/
│   │   └── services/
│   │       └── api.js
│   ├── public/
│   └── package.json
│
├── loan_approval/
│   ├── model_building.ipynb
│   ├── app.py
│   └── requirements.txt
│
├── database/
│   └── schema.sql
│
├── docker-compose.yml
└── README.md
```

### Key Directories

- `/backend`: FastAPI server with ML model integration
- `/next-frontend`: Next.js frontend application
- `/loan_approval`: Loan prediction model and training
- `/database`: Database schemas and migrations

### Technology Stack

- **Backend**: FastAPI, Python
- **Frontend**: Next.js, React
- **ML**: XGBoost, scikit-learn
- **Database**: PostgreSQL
- **DevOps**: Docker, Docker Compose

## Setup Instructions

### Backend

1. Navigate to the `backend` directory.
2. Install the required dependencies listed in `requirements.txt`.
3. Run the application using the command: `python app.py`.

### Frontend

1. Navigate to the `frontend` directory.
2. Install the necessary packages using `npm install`.
3. Start the React application with the command: `npm start`.

### Database

1. Execute the SQL statements in `schema.sql` to set up the database schema.

### Docker

To run the application using Docker, use the `docker-compose.yml` file to build and start all services.

## Usage Guidelines

- Users can register and log in to access their dashboard.
- Document uploads for OCR processing can be done through the OCR upload component.
- The application provides AI-driven insights based on user data and uploaded documents.

## Workflow

![Workflow](assets/base_workflow.png)

The workflow of the Virtual Branch Manager is as follows:

1. **User Registration and Authentication**: Users register and log in to the application.
2. **Document Upload**: Users upload documents through the OCR upload component.
3. **OCR Processing**: The backend processes the uploaded documents using OCR to extract relevant information.
4. **AI Eligibility Check**: The extracted information is analyzed by the AI service to determine user eligibility for various financial products.
5. **Dashboard**: Users can view their eligibility results and other insights on their dashboard.

## Features

### Loan Advisor Bot
- AI-powered chatbot for loan consultation
- Real-time eligibility assessment
- Document verification (Aadhar, PAN)
- Income assessment
- Available loan products information
- Interactive conversation interface

### Database Schema
- User management with detailed profile information
- Loan application tracking
- Employment and income verification
- Timestamp-based tracking for all records

### Key Components

1. **User Authentication & Profile**
   - Personal details storage
   - Income and employment verification
   - Document management (Aadhar, PAN)

2. **Loan Management**
   - Multiple loan product options
   - Real-time application status tracking
   - Automated eligibility assessment
   - Interest rate information

3. **Chat Interface**
   - Interactive conversation with AI bot
   - Context-aware responses
   - Document verification assistance
   - Loan product recommendations

## Technical Requirements

### Backend Dependencies
```python
# Core Dependencies
fastapi
python-dotenv
streamlit
langchain_core
langchain_groq

# ML & Data Processing
numpy
pandas
scikit-learn
xgboost
scipy
imbalanced-learn

# WebSocket & API
websockets
python-multipart
uvicorn

# Database
sqlalchemy
psycopg2-binary
```

## Machine Learning Model

The loan approval system uses an XGBoost classifier trained on the following features:

### Features Used
- Numerical Features:
  - Person age
  - Person income
  - Employment length
  - Loan amount
  - Loan interest rate
  - Loan percent income

- Categorical Features:
  - Person home ownership
  - Loan intent
  - Loan grade
  - Person default history

### Model Performance
- The model achieves high accuracy in predicting loan approvals
- Uses SMOTE for handling imbalanced data
- Includes feature importance analysis
- Implements hyperparameter tuning via GridSearchCV

### Model Pipeline
1. Data Preprocessing
   - Standardization of numerical features
   - One-hot encoding of categorical features
   - Outlier detection and removal
   - Missing value handling

2. Feature Engineering
   - Feature scaling
   - Categorical encoding
   - Feature selection based on importance

3. Model Training
   - Cross-validation
   - Hyperparameter optimization
   - Model evaluation using classification metrics

## API Endpoints

### FastAPI Backend

```python
# Main endpoints
GET / - Welcome message
POST /predict/ - Loan prediction endpoint
WS /ws/kyc/{session_id} - WebSocket for KYC process
```

### WebSocket Features
- Real-time chat functionality
- KYC verification process
- Document validation
- Loan eligibility checks
- AI-powered conversation flow

### Session Management
- Secure user sessions
- Real-time updates
- Document processing status
- Loan application tracking

## Video KYC Integration

The system includes a video KYC feature with:
- Real-time video streaming
- Document verification
- Face matching
- Identity validation
- Secure WebSocket communication

### WebRTC Features
- Peer-to-peer video calls
- Document capture
- Face detection
- Real-time chat during KYC
- Session recording capabilities

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.
