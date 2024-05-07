from pdf2image import convert_from_path
import pytesseract
from io import BytesIO
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"F:\tesseract\tesseract.exe"

def extract_text_from_pdf(pdf_path):
    extracted_text = []

    # Convert each page of the PDF to PIL Image and extract text
    images = convert_from_path(pdf_path,poppler_path=r"E:\poppler-24.02.0\Library\bin")
    for image in images:
        # Convert PIL Image to bytes
        with BytesIO() as byte_io:
            image.save(byte_io, format='PNG')
            byte_io.seek(0)
            img_pil = Image.open(byte_io)

            # Perform OCR on the image
            text = pytesseract.image_to_string(img_pil, lang='eng')
            extracted_text.append(text)

    return "\n".join(extracted_text)