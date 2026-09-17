from app.services.matching_service import match_candidate_to_job


cv_analysis = {
    "full_name": "John Doe",
    "professional_summary": "Backend developer with Python experience",
    "skills": [
        "Python",
        "FastAPI",
        "PostgreSQL",
        "Git",
    ],
    "experience_years": 2.0,
    "job_titles": [
        "Backend Developer",
    ],
    "education": [
        {
            "degree": "BS",
            "institution": "ABC University",
            "field_of_study": "Computer Science",
            "start_year": 2020,
            "end_year": 2024,
        }
    ],
    "experience": [
        {
            "job_title": "Backend Developer",
            "company": "Tech Company",
            "start_date": "2024",
            "end_date": "2026",
            "description": "Developed APIs using Python and FastAPI.",
        }
    ],
    "certifications": [],
    "languages": [
        "English",
    ],
    "location": "Lahore",
    "email": "john@example.com",
    "phone": "03000000000",
}


job_analysis = {
    "job_title": "Python Backend Developer",
    "summary": "Backend developer responsible for building APIs.",
    "required_skills": [
        "Python",
        "FastAPI",
        "PostgreSQL",
    ],
    "preferred_skills": [
        "Docker",
    ],
    "required_experience_years": 1.0,
    "preferred_experience_years": 2.0,
    "education_requirements": [
        "Computer Science",
    ],
    "responsibilities": [
        "Build backend APIs",
        "Work with PostgreSQL",
    ],
    "employment_type": "FULL_TIME",
    "location": "Lahore",
    "certifications": [],
    "languages": [
        "English",
    ],
}


result = match_candidate_to_job(
    cv_analysis=cv_analysis,
    job_analysis=job_analysis,
)


print("\n========== MATCH RESULT ==========")
print("Match Score:", result["match_score"])
print("Recommendation:", result["recommendation"])
print("Matched Skills:", result["matched_skills"])
print("Missing Required:", result["missing_required_skills"])
print("Missing Preferred:", result["missing_preferred_skills"])
print("Experience Match:", result["experience_match"])
print("Education Match:", result["education_match"])
print("Strengths:", result["strengths"])
print("Weaknesses:", result["weaknesses"])
print("Reasoning:", result["reasoning"])

print("\n========== ERROR TESTS ==========")

# Test 1: Missing CV analysis
try:
    match_candidate_to_job(
        cv_analysis={},
        job_analysis=job_analysis,
    )
except ValueError as e:
    print("Missing CV test: PASSED")
    print("Error:", e)


# Test 2: Missing Job analysis
try:
    match_candidate_to_job(
        cv_analysis=cv_analysis,
        job_analysis={},
    )
except ValueError as e:
    print("Missing Job test: PASSED")
    print("Error:", e)