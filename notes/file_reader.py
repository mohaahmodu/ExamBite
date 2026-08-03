import PyPDF2
from docx import Document


def clean_text(text):
    if not text:
        return ""

    # Remove invalid Unicode characters
    text = text.encode("utf-8", "ignore").decode("utf-8", "ignore")

    # Remove surrogate characters that can crash Gemini
    text = "".join(
        ch for ch in text
        if not (0xD800 <= ord(ch) <= 0xDFFF)
    )

    return text


def read_pdf(path):
    text = ""

    with open(path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    return clean_text(text)


def read_docx(path):
    doc = Document(path)
    text = "\n".join(p.text for p in doc.paragraphs)

    return clean_text(text)


def read_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as file:
        text = file.read()

    return clean_text(text)