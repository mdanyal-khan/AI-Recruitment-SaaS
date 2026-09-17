from pathlib import Path

from app.services.pdf_extractor import extract_text_from_pdf


pdf_path = Path(r"C:\Users\Muhammad Shadman\Desktop\AI-Recruitment-SaaS\backend\test_cv.pdf.pdf")

file_data = pdf_path.read_bytes()

text = extract_text_from_pdf(file_data)

print("========== EXTRACTED TEXT ==========")
print(text)
print("=====================================")