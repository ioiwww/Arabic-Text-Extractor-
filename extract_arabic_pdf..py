import os
import re
import pytesseract
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
from docx import Document


# folders
INPUT_FOLDER = "pdfs"
OUTPUT_FOLDER = "output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)



# Arabic Unicode detection
arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')


def extract_arabic_lines(text):
    lines = text.split("\n")
    arabic_lines = []

    for line in lines:
        if arabic_pattern.search(line):
            arabic_lines.append(line.strip())

    return arabic_lines


def extract_pdf_text(pdf):
    try:
        text = extract_text(pdf)
        return text
    except:
        return ""


def extract_scanned_text(pdf):
    pages = convert_from_path(pdf)
    text = ""

    for page in pages:
        page_text = pytesseract.image_to_string(page, lang="ara")
        text += page_text + "\n"

    return text





for file in os.listdir(INPUT_FOLDER):

    if not file.endswith(".pdf"):
        continue

    pdf_path = os.path.join(INPUT_FOLDER, file)

    print("Processing:", file)

    text = extract_pdf_text(pdf_path)

    if len(text.strip()) < 200:
        print("Using OCR...")
        text = extract_scanned_text(pdf_path)

    arabic_lines = extract_arabic_lines(text)

    # optional translation
    translated = arabic_lines
    base = os.path.splitext(file)[0]

    txt_file = os.path.join(OUTPUT_FOLDER, base + "_arabic.txt")
    docx_file = os.path.join(OUTPUT_FOLDER, base + "_arabic.docx")

    # save TXT
    with open(txt_file, "w", encoding="utf-8") as f:
        for line in translated:
            f.write(line + "\n")

    # save DOCX
    doc = Document()

    for line in translated:
        doc.add_paragraph(line)

    doc.save(docx_file)

    print("Saved:", txt_file)
    print("Saved:", docx_file)

print("Finished processing all PDFs")