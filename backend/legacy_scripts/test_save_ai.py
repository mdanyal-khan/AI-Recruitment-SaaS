from app.core.database import SessionLocal

from app.models.resume import Resume

from app.services.ai_analysis_service import (
    analyze_cv_text,
    save_cv_analysis,
)


cv_text = """
Muhammad Shadman

Python Backend Developer

Skills:
Python
FastAPI
PostgreSQL
Supabase
SQLAlchemy

Experience:
2 years of backend development.

Education:
BS Computer Science
"""


db = SessionLocal()

try:

    # -----------------------------------------
    # 1. Get an existing resume
    # -----------------------------------------

    resume = (
        db.query(Resume)
        .first()
    )

    if not resume:
        print("No resume found in database.")
        print("Upload a resume first.")
        exit()

    print("Using resume:")
    print(resume.id)
    print(resume.file_name)

    # -----------------------------------------
    # 2. Analyze CV
    # -----------------------------------------

    print("\nAnalyzing CV with Groq...\n")

    analysis_result = analyze_cv_text(
        cv_text
    )

    # -----------------------------------------
    # 3. Save analysis
    # -----------------------------------------

    analysis = save_cv_analysis(
        db=db,
        resume_id=resume.id,
        analysis_result=analysis_result,
    )

    print("\nAI analysis saved successfully!")

    print("Analysis ID:")
    print(analysis.id)

    print("\nResult:")
    print(analysis.result_json)

finally:

    db.close()