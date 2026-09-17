"""
Comprehensive API Test Suite for AI Recruitment SaaS.
Tests all registered API endpoints systematically.
"""

import sys
import uuid
import os
from starlette.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

results = []

def record(endpoint, method, status_code, expected_status, passed, detail=""):
    results.append({
        "method": method,
        "endpoint": endpoint,
        "status": status_code,
        "expected": expected_status,
        "passed": passed,
        "detail": detail
    })
    mark = "PASS" if passed else "FAIL"
    print(f"[{mark}] {method:6} {endpoint:45} -> {status_code} ({detail})")

def run_tests():
    print("=" * 80)
    print("STARTING FULL BACKEND API SUITE TEST")
    print("=" * 80)

    # -------------------------------------------------------------
    # 1. Health & Root APIs
    # -------------------------------------------------------------
    res = client.get("/")
    record("/", "GET", res.status_code, 200, res.status_code == 200)

    res = client.get("/health")
    record("/health", "GET", res.status_code, 200, res.status_code == 200)

    res = client.get("/health/database")
    record("/health/database", "GET", res.status_code, 200, res.status_code == 200)

    res = client.get("/test/supabase")
    record("/test/supabase", "GET", res.status_code, 200, res.status_code == 200)

    # -------------------------------------------------------------
    # 2. Auth APIs
    # -------------------------------------------------------------
    unique_suffix = str(uuid.uuid4())[:8]
    test_email = f"apitest_{unique_suffix}@example.com"
    test_password = "Password123!"

    # Register
    res = client.post("/auth/register", json={
        "email": test_email,
        "password": test_password,
        "first_name": "API",
        "last_name": "Tester",
        "role": "HR"
    })
    user_created = res.status_code == 200
    record("/auth/register", "POST", res.status_code, 200, user_created)

    # Login
    res = client.post("/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    logged_in = res.status_code == 200 and "access_token" in res.json()
    record("/auth/login", "POST", res.status_code, 200, logged_in)
    
    token = res.json().get("access_token") if logged_in else ""
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # Get Current User (/auth/me)
    res = client.get("/auth/me", headers=headers)
    me_ok = res.status_code == 200 and res.json().get("email") == test_email
    current_user_id = res.json().get("id") if me_ok else None
    record("/auth/me", "GET", res.status_code, 200, me_ok)

    # -------------------------------------------------------------
    # 3. Companies APIs
    # -------------------------------------------------------------
    company_name = f"TestCorp_{unique_suffix}"
    res = client.post("/companies", json={
        "name": company_name,
        "description": "Test Corporation for Automated Tests",
        "industry": "Software",
        "location": "San Francisco, CA"
    }, headers=headers)
    comp_created = res.status_code in [200, 201]
    company = res.json() if comp_created else {}
    company_id = company.get("id")
    record("/companies", "POST", res.status_code, 201, comp_created, f"id={company_id}")

    # List Companies
    res = client.get("/companies", headers=headers)
    record("/companies", "GET", res.status_code, 200, res.status_code == 200)

    # Get Single Company
    if company_id:
        res = client.get(f"/companies/{company_id}", headers=headers)
        record(f"/companies/{{company_id}}", "GET", res.status_code, 200, res.status_code == 200)

        # Update Company
        res = client.put(f"/companies/{company_id}", json={
            "name": f"{company_name} Updated",
            "description": "Updated description"
        }, headers=headers)
        record(f"/companies/{{company_id}}", "PUT", res.status_code, 200, res.status_code == 200)
    else:
        record(f"/companies/{{company_id}}", "GET", 0, 200, False, "Skipped - no company")
        record(f"/companies/{{company_id}}", "PUT", 0, 200, False, "Skipped - no company")

    # -------------------------------------------------------------
    # 4. Company Members APIs
    # -------------------------------------------------------------
    second_email = f"member_{unique_suffix}@example.com"
    res_member_reg = client.post("/auth/register", json={
        "email": second_email,
        "password": test_password,
        "first_name": "Member",
        "last_name": "Two",
        "role": "HR"
    })
    second_user_id = res_member_reg.json().get("id") if res_member_reg.status_code == 200 else None

    if company_id and second_user_id:
        # Add Member
        res = client.post(f"/companies/{company_id}/members", json={
            "user_id": second_user_id,
            "role": "HR"
        }, headers=headers)
        record(f"/companies/{{company_id}}/members", "POST", res.status_code, 201, res.status_code in [200, 201])

        # Get Members
        res = client.get(f"/companies/{company_id}/members", headers=headers)
        record(f"/companies/{{company_id}}/members", "GET", res.status_code, 200, res.status_code == 200)

        # Remove Member
        res = client.delete(f"/companies/{company_id}/members/{second_user_id}", headers=headers)
        record(f"/companies/{{company_id}}/members/{{user_id}}", "DELETE", res.status_code, 204, res.status_code in [200, 204])
    else:
        record(f"/companies/{{company_id}}/members", "POST", 0, 201, False, "Skipped")
        record(f"/companies/{{company_id}}/members", "GET", 0, 200, False, "Skipped")
        record(f"/companies/{{company_id}}/members/{{user_id}}", "DELETE", 0, 204, False, "Skipped")

    # -------------------------------------------------------------
    # 5. Permission & Tenant Test APIs
    # -------------------------------------------------------------
    if company_id:
        # Tenant test
        res = client.get(f"/tenant-test/{company_id}", headers=headers)
        record(f"/tenant-test/{{company_id}}", "GET", res.status_code, 200, res.status_code == 200)

        # Permission tests
        res = client.get(f"/permission-test/{company_id}/owner", headers=headers)
        record(f"/permission-test/{{company_id}}/owner", "GET", res.status_code, 200, res.status_code == 200)

        res = client.get(f"/permission-test/{company_id}/hr", headers=headers)
        record(f"/permission-test/{{company_id}}/hr", "GET", res.status_code, 200, res.status_code == 200)

        res = client.get(f"/permission-test/{company_id}/recruiter", headers=headers)
        record(f"/permission-test/{{company_id}}/recruiter", "GET", res.status_code, 200, res.status_code == 200)

    # -------------------------------------------------------------
    # 6. Jobs APIs
    # -------------------------------------------------------------
    job_id = None
    if company_id:
        # Create Job
        res = client.post(f"/companies/{company_id}/jobs", json={
            "title": "Senior Python Backend Engineer",
            "description": "Develop high-scale APIs with FastAPI, PostgreSQL and Python.",
            "requirements": "Python, FastAPI, Docker, PostgreSQL",
            "location": "Remote",
            "employment_type": "FULL_TIME",
            "experience_level": "SENIOR"
        }, headers=headers)
        job_created = res.status_code in [200, 201]
        job = res.json() if job_created else {}
        job_id = job.get("id")
        record(f"/companies/{{company_id}}/jobs", "POST", res.status_code, 201, job_created, f"id={job_id}")

        # List Jobs
        res = client.get(f"/companies/{company_id}/jobs", headers=headers)
        record(f"/companies/{{company_id}}/jobs", "GET", res.status_code, 200, res.status_code == 200)

        if job_id:
            # Get Single Job
            res = client.get(f"/companies/{company_id}/jobs/{job_id}", headers=headers)
            record(f"/companies/{{company_id}}/jobs/{{job_id}}", "GET", res.status_code, 200, res.status_code == 200)

            # Update Job
            res = client.put(f"/companies/{company_id}/jobs/{job_id}", json={
                "title": "Lead Python Backend Engineer",
                "description": "Updated lead requirements."
            }, headers=headers)
            record(f"/companies/{{company_id}}/jobs/{{job_id}}", "PUT", res.status_code, 200, res.status_code == 200)

            # Publish Job
            res = client.patch(f"/companies/{company_id}/jobs/{job_id}/publish", headers=headers)
            record(f"/companies/{{company_id}}/jobs/{{job_id}}/publish", "PATCH", res.status_code, 200, res.status_code == 200)

            # Close Job
            res = client.patch(f"/companies/{company_id}/jobs/{job_id}/close", headers=headers)
            record(f"/companies/{{company_id}}/jobs/{{job_id}}/close", "PATCH", res.status_code, 200, res.status_code == 200)

            # Archive Job
            res = client.patch(f"/companies/{company_id}/jobs/{job_id}/archive", headers=headers)
            record(f"/companies/{{company_id}}/jobs/{{job_id}}/archive", "PATCH", res.status_code, 200, res.status_code == 200)

    # -------------------------------------------------------------
    # 7. Candidate Profile APIs
    # -------------------------------------------------------------
    candidate_user_email = f"candidate_{unique_suffix}@example.com"
    res_cand_reg = client.post("/auth/register", json={
        "email": candidate_user_email,
        "password": test_password,
        "first_name": "Jane",
        "last_name": "Developer",
        "role": "CANDIDATE"
    })
    cand_user_id = res_cand_reg.json().get("id")
    res_cand_login = client.post("/auth/login", json={
        "email": candidate_user_email,
        "password": test_password
    })
    cand_token = res_cand_login.json().get("access_token")
    cand_headers = {"Authorization": f"Bearer {cand_token}"}

    # Create Candidate Profile
    res = client.post("/candidates/profile", json={
        "title": "Software Engineer",
        "bio": "Passionate backend engineer",
        "years_of_experience": 4,
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "location": "Remote"
    }, headers=cand_headers)
    cand_prof_created = res.status_code in [200, 201]
    candidate_data = res.json() if cand_prof_created else {}
    candidate_id = candidate_data.get("id")
    record("/candidates/profile", "POST", res.status_code, 201, cand_prof_created, f"id={candidate_id}")

    # Get Candidate Profile
    res = client.get("/candidates/profile", headers=cand_headers)
    record("/candidates/profile", "GET", res.status_code, 200, res.status_code == 200)

    # Update Candidate Profile
    res = client.put("/candidates/profile", json={
        "title": "Senior Software Engineer",
        "years_of_experience": 5
    }, headers=cand_headers)
    record("/candidates/profile", "PUT", res.status_code, 200, res.status_code == 200)

    # -------------------------------------------------------------
    # 8. Resume APIs
    # -------------------------------------------------------------
    sample_pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_cv.pdf.pdf")
    resume_id = None
    if os.path.exists(sample_pdf_path):
        with open(sample_pdf_path, "rb") as f:
            pdf_bytes = f.read()
        res = client.post(
            "/candidates/resume",
            files={"file": ("test_resume.pdf", pdf_bytes, "application/pdf")},
            headers=cand_headers
        )
        res_ok = res.status_code in [200, 201]
        resume_obj = res.json() if res_ok else {}
        resume_id = resume_obj.get("id")
        record("/candidates/resume", "POST", res.status_code, 201, res_ok, f"id={resume_id}")
    else:
        record("/candidates/resume", "POST", 0, 201, False, "test_cv.pdf.pdf not found")

    # List Resumes
    res = client.get("/candidates/resumes", headers=cand_headers)
    record("/candidates/resumes", "GET", res.status_code, 200, res.status_code == 200)

    # Download Resume
    if resume_id:
        res = client.get(f"/candidates/resumes/{resume_id}/download", headers=cand_headers)
        record("/candidates/resumes/{resume_id}/download", "GET", res.status_code, 200, res.status_code == 200)
    else:
        # Test 404 behavior or existing resume
        res = client.get(f"/candidates/resumes/{uuid.uuid4()}/download", headers=cand_headers)
        record("/candidates/resumes/{resume_id}/download", "GET", res.status_code, 404, res.status_code == 404, "404 as expected for missing id")

    # -------------------------------------------------------------
    # 9. Matching API
    # -------------------------------------------------------------
    if job_id and candidate_id and company_id:
        res = client.post(
            f"/matching/jobs/{job_id}/candidates/{candidate_id}?company_id={company_id}",
            headers=headers
        )
        matching_ok = res.status_code in [200, 201]
        record("/matching/jobs/{job_id}/candidates/{candidate_id}", "POST", res.status_code, 200, matching_ok, "AI Matching executed")
    else:
        record("/matching/jobs/{job_id}/candidates/{candidate_id}", "POST", 0, 200, False, "Missing job or candidate")

    # -------------------------------------------------------------
    # 10. Delete Company (Cleanup & test DELETE)
    # -------------------------------------------------------------
    if company_id:
        res = client.delete(f"/companies/{company_id}", headers=headers)
        record(f"/companies/{{company_id}}", "DELETE", res.status_code, 200, res.status_code in [200, 204])

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    print(f"Total Tests Run : {total_count}")
    print(f"Passed          : {passed_count}")
    print(f"Failed          : {total_count - passed_count}")
    print("=" * 80)
    
    return total_count - passed_count == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
