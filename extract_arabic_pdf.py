import os
import pytesseract
from pdf2image import convert_from_path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

# المجلدات
INPUT_FOLDER = "pdfs"
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def process_pdf_with_ocr(pdf_path):
    """
    هذا التابع بيحول الـ PDF لصور وبيقرأها كأنها عيون بشرية
    وهاد هو الحل الوحيد للملفات اللي نصها الداخلي مشوه
    """
    print(f"جاري المعالجة البصرية (OCR) لملف: {os.path.basename(pdf_path)}")
    
    # تحويل الصفحات لصور بدقة عالية (300 DPI)
    pages = convert_from_path(pdf_path, dpi=300)
    
    extracted_lines = []
    for page in pages:
        # استخدام Tesseract لقراءة الصورة باللغة العربية
        page_text = pytesseract.image_to_string(page, lang="ara")
        
        # تنظيف النص المستخرج
        for line in page_text.split('\n'):
            clean_line = line.strip()
            if clean_line:
                extracted_lines.append(clean_line)
                
    return extracted_lines

# دورة المعالجة الرئيسية
for file in os.listdir(INPUT_FOLDER):
    if not file.endswith(".pdf"):
        continue
    
    pdf_path = os.path.join(INPUT_FOLDER, file)
    base_name = os.path.splitext(file)[0]

    # استخراج النص عبر الصور حصراً لضمان عدم تشوه الحروف
    lines = process_pdf_with_ocr(pdf_path)

    # 1. حفظ ملف Word (الأفضل للعربي)
    doc = Document()
    for line in lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT # محاذاة لليمين
        run = p.add_run(line)
        run.font.size = Pt(13)
        
    docx_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_clean.docx")
    doc.save(docx_path)

    # 2. حفظ ملف نصي TXT
    txt_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_clean.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"تم الحفظ بنجاح: {base_name}_clean")

print("\nانتهت العملية! جرب تفتح ملف الـ Word الآن.")
