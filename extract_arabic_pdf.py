import os
import re
import pytesseract
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
import arabic_reshaper
from bidi.algorithm import get_display

INPUT_FOLDER = "pdfs"
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')

def fix_arabic_text(text):
    # تصحيح شكل الحروف واتجاهها
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def extract_arabic_lines(text):
    lines = text.split("\n")
    arabic_lines = []
    for line in lines:
        if arabic_pattern.search(line):
            # نقوم بتصحيح السطر هنا
            arabic_lines.append(fix_arabic_text(line.strip()))
    return arabic_lines

def extract_pdf_text(pdf):
    try:
        return extract_text(pdf)
    except:
        return ""

def extract_scanned_text(pdf):
    pages = convert_from_path(pdf)
    text = ""
    for page in pages:
        # استخدام ara للتحدث مع تيسيراكت
        page_text = pytesseract.image_to_string(page, lang="ara")
        text += page_text + "\n"
    return text

for file in os.listdir(INPUT_FOLDER):
    if not file.endswith(".pdf"): continue
    
    pdf_path = os.path.join(INPUT_FOLDER, file)
    print(f"Processing: {file}")

    text = extract_pdf_text(pdf_path)
    if len(text.strip()) < 200:
        print("Using OCR...")
        text = extract_scanned_text(pdf_path)

    arabic_lines = extract_arabic_lines(text)
    base = os.path.splitext(file)[0]
    
    # حفظ TXT
    txt_file = os.path.join(OUTPUT_FOLDER, base + "_arabic.txt")
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("\n".join(arabic_lines))

    # حفظ DOCX مع تنسيق اليمين لليسار
    docx_file = os.path.join(OUTPUT_FOLDER, base + "_arabic.docx")
    doc = Document()
    for line in arabic_lines:
        p = doc.add_paragraph(line)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT # محاذاة لليمين
    
    doc.save(docx_file)
    print(f"Saved: {base}")

print("Done!")
