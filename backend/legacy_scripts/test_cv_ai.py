from app.services.ai_analysis_service import analyze_cv_text


cv_text = """
Muhammad Shadman

Python Backend Developer

Email:
muhammad@example.com

Location:
Pakistan

Professional Summary:
Python developer interested in backend development
and AI automation.

Skills:
Python
FastAPI
PostgreSQL
Supabase
SQLAlchemy
REST APIs

Experience:

Backend Developer
ABC Software
2024 - 2026

Worked on FastAPI applications, PostgreSQL databases
and REST APIs.

Education:

BS Computer Science
ABC University
2020 - 2024

Certifications:
Python Programming

Languages:
English
Urdu
"""


result = analyze_cv_text(cv_text)

print("\n========== CV AI ANALYSIS ==========\n")

for key, value in result.items():
    print(f"{key}: {value}")

print("\n====================================")