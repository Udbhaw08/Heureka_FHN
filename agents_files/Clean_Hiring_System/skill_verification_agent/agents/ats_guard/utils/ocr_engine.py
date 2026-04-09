import pytesseract

def extract_text_tesseract(images):
    full_text = []

    for img in images:
        text = pytesseract.image_to_string(img)
        full_text.append(text)

    return "\n".join(full_text)
