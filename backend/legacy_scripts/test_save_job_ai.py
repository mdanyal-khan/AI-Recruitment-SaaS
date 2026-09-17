from app.core.database import SessionLocal
from app.models.job import Job
from app.services.ai_analysis_service import (
    analyze_job_text,
    save_job_analysis,
)


job_text = """
Python Backend Developer

We are looking for a Python Backend Developer
with at least 2 years of experience.

Required:
Python
FastAPI
PostgreSQL
REST APIs
BS Computer Science

Preferred:
Supabase
Docker
Git

Responsibilities:
Build REST APIs.
Develop backend services.
Work with PostgreSQL.
Maintain backend systems.
"""


db = SessionLocal()

try:

    job = db.query(Job).first()

    if not job:
        print("No job found in database.")
        print("Create a job first.")
        exit()

    print("Using job:")
    print(job.id)
    print(job.title)

    print("\nAnalyzing job with Groq...\n")

    analysis_result = analyze_job_text(
        job_text
    )

    print("AI analysis completed.")

    analysis = save_job_analysis(
        db=db,
        job_id=job.id,
        analysis_result=analysis_result,
    )

    print("\nAI job analysis saved successfully!")

    print("Analysis ID:")
    print(analysis.id)

    print("\nResult:")
    print(analysis.result_json)

finally:

    db.close()
    