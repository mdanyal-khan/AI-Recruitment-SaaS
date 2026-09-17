from app.services.ai_analysis_service import analyze_job_text


job_text = """
Python Backend Developer

We are looking for a Python Backend Developer
to build and maintain backend APIs.

Requirements:

- 2+ years of backend development experience
- Strong Python skills
- FastAPI experience
- PostgreSQL experience
- REST API development
- BS Computer Science or related degree

Preferred:

- Supabase experience
- Docker experience
- Git experience

Responsibilities:

- Build REST APIs
- Develop backend services
- Work with PostgreSQL
- Maintain existing backend systems
"""


print("Analyzing job description with Groq...\n")


result = analyze_job_text(job_text)


print("========== JOB ANALYSIS ==========")
print(result)
print("==================================")