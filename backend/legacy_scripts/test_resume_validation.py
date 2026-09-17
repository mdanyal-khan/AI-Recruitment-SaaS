import pytest

from app.services.resume_processor import validate_resume_upload


def test_validate_resume_upload_accepts_real_pdf_payload():
    payload = b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF'
    result = validate_resume_upload(payload, "application/pdf")

    assert result == payload


def test_validate_resume_upload_rejects_non_pdf_content_type():
    payload = b"hello"

    with pytest.raises(ValueError, match="Only PDF files are allowed"):
        validate_resume_upload(payload, "text/plain")


def test_validate_resume_upload_rejects_empty_payload():
    with pytest.raises(ValueError, match="Uploaded file is empty"):
        validate_resume_upload(b"", "application/pdf")
