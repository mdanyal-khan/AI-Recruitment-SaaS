from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.company import router as company_router
from app.api.health import router as health_router
from app.api.company_members import router as company_members_router
from app.api.tenant_test import router as tenant_test_router
from app.api.permission_test import router as permission_test_router
from app.api.jobs import router as jobs_router, public_router as public_jobs_router
from app.api.candidates import router as candidates_router
from app.api.resumes import router as resumes_router
from app.api.matching import router as matching_router
from app.api.applications import router as applications_router
from app.api.interviews import router as interviews_router
from app.api.notifications import router as notifications_router
from app.api import hr_applications
from app.api import screening
from app.api.offers import router as offers_router
from app.api.hiring import router as hiring_router
from app.api.candidate_offers import router as candidate_offers_router

app = FastAPI(
    title="AI Recruitment SaaS API",
    version="1.0.0"
)

# HTTP Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-Company-Id",
    ],
)


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(company_router)
app.include_router(company_members_router)
app.include_router(jobs_router)
app.include_router(public_jobs_router)
app.include_router(candidates_router)
app.include_router(resumes_router)
app.include_router(matching_router)
app.include_router(applications_router)
app.include_router(interviews_router)
app.include_router(notifications_router)
app.include_router(screening.router)
app.include_router(hr_applications.router)
app.include_router(offers_router)
app.include_router(hiring_router)
app.include_router(candidate_offers_router)

# Diagnostic test routes only registered in development/debug mode
if settings.DEBUG and settings.APP_ENV != "production":
    app.include_router(tenant_test_router)
    app.include_router(permission_test_router)

    @app.get("/test/supabase")
    def test_supabase():
        return {
            "message": "Supabase client initialized successfully"
        }

@app.get("/")
def root():
    return {
        "message": "AI Recruitment SaaS API is running"
    }