import os

from pypdf import PdfReader
from docx import Document


# =====================================================
# PDF TEXT EXTRACTION
# =====================================================

def extract_pdf_text(filepath):

    text = []

    reader = PdfReader(filepath)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text.append(page_text)

    return "\n".join(text)


# =====================================================
# DOCX TEXT EXTRACTION
# =====================================================

def extract_docx_text(filepath):

    document = Document(filepath)

    text = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text)


# =====================================================
# RESUME TEXT EXTRACTION
# =====================================================

def extract_resume_text(filepath):

    extension = os.path.splitext(
        filepath
    )[1].lower()

    if extension == ".pdf":

        return extract_pdf_text(filepath)

    elif extension == ".docx":

        return extract_docx_text(filepath)

    else:

        raise ValueError(
            "Unsupported resume format."
        )


# =====================================================
# TEXT CLEANING
# =====================================================

def clean_resume_text(text):

    if not text:
        return ""

    # Normalize line endings

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    cleaned_lines = []

    for line in text.split("\n"):

        # Remove unnecessary spaces

        line = " ".join(
            line.split()
        )

        if line:

            cleaned_lines.append(line)

    return "\n".join(
        cleaned_lines
    )