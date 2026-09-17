import pytest
from pydantic import ValidationError
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.auth import RegisterRequest
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.email_templates import interview_invitation_email
from app.services.email_service import sanitize_email_header
from app.core.rate_limiter import InMemoryRateLimiter


client = TestClient(app)


# =======================================================
# 1. Security Headers Tests (SEC-003 & SEC-006)
# =======================================================
def test_security_headers_present_in_response():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "Strict-Transport-Security" in response.headers


# =======================================================
# 2. Authentication & Password Policy Tests (SEC-001)
# =======================================================
def test_password_policy_rejects_weak_passwords():
    # Password too short (< 8 chars)
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="test@example.com",
            password="123",
            first_name="Test",
            last_name="User",
            role="CANDIDATE"
        )

    # Password without numbers
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="test@example.com",
            password="onlyletterssecret",
            first_name="Test",
            last_name="User",
            role="CANDIDATE"
        )

    # Password without letters
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="test@example.com",
            password="1234567890123",
            first_name="Test",
            last_name="User",
            role="CANDIDATE"
        )


def test_email_normalization():
    req = RegisterRequest(
        email="  Test.USER+Tag@Example.COM  ",
        password="ValidPassword123!",
        first_name="Test",
        last_name="User",
        role="CANDIDATE"
    )
    assert req.email == "test.user+tag@example.com"


# =======================================================
# 3. PDF Magic Byte Validation Tests (SEC-005)
# =======================================================
def test_pdf_magic_byte_rejects_fake_pdf():
    fake_pdf_data = b"This is a text file masquerading as a PDF."
    with pytest.raises((ValueError, HTTPException)) as exc_info:
        extract_text_from_pdf(fake_pdf_data)
    error_msg = str(exc_info.value).lower()
    assert "pdf" in error_msg


# =======================================================
# 4. Email HTML Escaping & Injection Tests (SEC-004)
# =======================================================
def test_email_template_escapes_html_entities():
    xss_payload = "<script>alert('xss')</script>"
    html_content = interview_invitation_email(
        candidate_name=xss_payload,
        job_title="Software Engineer",
        start_time="2026-10-01 10:00",
        end_time="2026-10-01 11:00",
        timezone="UTC",
        mode="ONLINE",
        meeting_url="https://meet.google.com/abc-defg-hij",
    )
    # The raw script tag must NOT exist in the rendered HTML output
    assert "<script>" not in html_content
    assert "&lt;script&gt;" in html_content


def test_sanitize_email_header_strips_crlf_injection():
    malicious_subject = "Interview Invitation\r\nBcc: victim@example.com\r\n"
    cleaned = sanitize_email_header(malicious_subject)
    assert "\r" not in cleaned
    assert "\n" not in cleaned
    assert "\nBcc:" not in cleaned


# =======================================================
# 5. Rate Limiting Tests (SEC-008)
# =======================================================
def test_in_memory_rate_limiter():
    limiter = InMemoryRateLimiter(requests_per_window=3, window_seconds=60)
    key = "test-client-ip"

    # 3 allowed requests
    limiter.check(key)
    limiter.check(key)
    limiter.check(key)

    # 4th request must raise 429
    with pytest.raises(HTTPException) as exc_info:
        limiter.check(key)
    assert exc_info.value.status_code == 429


def test_auth_login_rate_limit_enforced():
    # Make requests until rate limit trips (15 req/min configured)
    hit_429 = False
    for _ in range(20):
        res = client.post(
            "/auth/login",
            json={"email": "nonexistent@example.com", "password": "AnyPassword123"}
        )
        if res.status_code == 429:
            hit_429 = True
            break
    assert hit_429 is True
