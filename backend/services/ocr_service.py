from pytesseract import image_to_string
from PIL import Image
import re

def extract_details_from_image(image_path):
    """
    Extracts key details from the provided image using OCR.

    Args:
        image_path (str): The path to the image file.

    Returns:
        dict: A dictionary containing extracted details such as Name, DOB, and Income.
    """
    # Load the image from the specified path
    image = Image.open(image_path)
    
    # Perform OCR on the image
    text = image_to_string(image)

    # Initialize a dictionary to hold extracted details
    details = {
        'Name': None,
        'DOB': None,
        'Income': None
    }

    # Use regular expressions to find the required details in the OCR text
    name_match = re.search(r'Name:\s*(.*)', text)
    dob_match = re.search(r'DOB:\s*(\d{2}/\d{2}/\d{4})', text)
    income_match = re.search(r'Income:\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', text)

    if name_match:
        details['Name'] = name_match.group(1).strip()
    if dob_match:
        details['DOB'] = dob_match.group(1).strip()
    if income_match:
        details['Income'] = income_match.group(1).strip()

    return details

def process_uploaded_document(file):
    """
    Processes the uploaded document for OCR and extracts details.

    Args:
        file (File): The uploaded file object.

    Returns:
        dict: A dictionary containing extracted details or an error message.
    """
    try:
        # Save the uploaded file temporarily
        image_path = f'temp/{file.filename}'
        file.save(image_path)

        # Extract details from the image
        extracted_details = extract_details_from_image(image_path)

        return extracted_details
    except Exception as e:
        return {'error': str(e)}