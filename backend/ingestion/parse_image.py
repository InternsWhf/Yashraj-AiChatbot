import io
from google.cloud import vision
from PIL import Image

client = vision.ImageAnnotatorClient()

def extract_text_from_image(file_path):
    with io.open(file_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    return response.full_text_annotation.text if response.full_text_annotation.text else ""

def parse_image(file_path):
    """Parse image file and extract text content using OCR"""
    try:
        return extract_text_from_image(file_path)
    except Exception as e:
        print(f"Error parsing image {file_path}: {e}")
        return ""
