from PyPDF2 import PdfReader

def extract(file):
    try:
        pdf_reader = PdfReader(file)
        text = ''

        for page in range(len(pdf_reader.pages)):
            text += " ".join(pdf_reader.pages[page].extract_text().split())
            break

        return text
    except Exception as e:
        return