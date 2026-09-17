from app.services.ai_analysis_service import analyze_cv_text


cv_text = """
Muhammad Shadman

Python Developer

Skills:
Python
FastAPI
PostgreSQL
Supabase

Experience:
2 years
"""

result = analyze_cv_text(cv_text)

print("========== AI ANALYSIS ==========")
print(result)
print("=================================")
