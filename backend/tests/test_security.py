from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_protected_endpoint_requires_authentication():
    response = client.get("/applications/my")

    assert response.status_code in [401, 403]


def test_candidate_offers_requires_authentication():
    response = client.get("/candidate/offers")

    assert response.status_code in [401, 403]


def test_hr_applications_requires_authentication():
    response = client.get("/hr/applications/jobs/00000000-0000-0000-0000-000000000000")

    assert response.status_code in [401, 403]
