import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.groq import groq_client

from app.models.ai_analysis import AIAnalysis
from app.models.application import Application
from app.models.match_result import MatchResult

from app.schemas.match_result import MatchResult as MatchResultSchema


def match_candidate_to_job(
    cv_analysis: dict,
    job_analysis: dict,
) -> dict:
    """
    Compare a candidate's CV analysis against a job analysis
    using Groq AI.
    """

    if not cv_analysis:
        raise ValueError("CV analysis is required")

    if not job_analysis:
        raise ValueError("Job analysis is required")

    system_prompt = """
You are an expert recruitment matching AI.

Your task is to compare a candidate's CV analysis
against a job description analysis.

Evaluate:

1. Required skills
2. Preferred skills
3. Experience
4. Education
5. Certifications
6. Languages
7. Overall suitability

Important rules:

- Do not invent candidate information.
- Do not invent job requirements.
- Only use information provided in the input.
- Missing information must not be assumed to exist.
- Be objective and consistent.
- match_score must be between 0 and 100.
- Return ONLY valid JSON.
- Use EXACTLY the JSON keys shown below.
- Do not rename any keys.
- Do not add extra keys.

Return this exact JSON structure:

{
    "match_score": 0,
    "recommendation": "",
    "matched_skills": [],
    "missing_required_skills": [],
    "missing_preferred_skills": [],
    "experience_match": false,
    "education_match": false,
    "certification_match": false,
    "language_match": false,
    "strengths": [],
    "weaknesses": [],
    "reasoning": ""
}

Rules for the fields:

- match_score: number between 0 and 100
- recommendation: MUST be exactly one of: "STRONG_MATCH", "GOOD_MATCH", "PARTIAL_MATCH", "WEAK_MATCH", "NOT_A_MATCH"
- matched_skills: skills from the job requirements that the candidate has
- missing_required_skills: required skills the candidate does not have
- missing_preferred_skills: preferred skills the candidate does not have
- experience_match: true if the candidate satisfies the required experience, otherwise false
- education_match: true if the candidate satisfies the education requirement, otherwise false
- certification_match: true if the candidate satisfies certification requirements, otherwise false
- language_match: true if the candidate satisfies language requirements, otherwise false
"""

    user_prompt = f"""
CANDIDATE CV ANALYSIS:

{json.dumps(cv_analysis, indent=2)}

JOB ANALYSIS:

{json.dumps(job_analysis, indent=2)}

Compare the candidate with the job and produce the matching result.
"""

    # -----------------------------------------
    # Call Groq AI
    # -----------------------------------------

    try:
        response = groq_client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0,
            response_format={
                "type": "json_object"
            },
            max_completion_tokens=4096,
        )

    except Exception as e:
        raise RuntimeError(
            f"Failed to generate candidate-job match: {str(e)}"
        )

    # -----------------------------------------
    # Validate Groq response
    # -----------------------------------------

    if not response.choices:
        raise RuntimeError(
            "Groq returned no choices"
        )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "Groq returned an empty response"
        )

    # -----------------------------------------
    # Parse JSON
    # -----------------------------------------

    try:
        result = json.loads(content)

    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Groq returned invalid JSON: {str(e)}"
        )

    # -----------------------------------------
    # Validate AI result with Pydantic
    # -----------------------------------------

    # Normalize recommendation if LLM returned free text
    allowed_recs = ["STRONG_MATCH", "GOOD_MATCH", "PARTIAL_MATCH", "WEAK_MATCH", "NOT_A_MATCH"]
    raw_rec = str(result.get("recommendation", "")).upper()
    if raw_rec not in allowed_recs:
        if "STRONG" in raw_rec:
            result["recommendation"] = "STRONG_MATCH"
        elif "GOOD" in raw_rec:
            result["recommendation"] = "GOOD_MATCH"
        elif "PARTIAL" in raw_rec:
            result["recommendation"] = "PARTIAL_MATCH"
        elif "WEAK" in raw_rec:
            result["recommendation"] = "WEAK_MATCH"
        elif "NOT" in raw_rec or "NO" in raw_rec:
            result["recommendation"] = "NOT_A_MATCH"
        else:
            score = result.get("match_score", 50)
            if score >= 80:
                result["recommendation"] = "STRONG_MATCH"
            elif score >= 60:
                result["recommendation"] = "GOOD_MATCH"
            elif score >= 40:
                result["recommendation"] = "PARTIAL_MATCH"
            else:
                result["recommendation"] = "WEAK_MATCH"

    try:
        validated_result = MatchResultSchema.model_validate(
            result
        )

    except Exception as e:
        raise RuntimeError(
            f"Invalid matching result: {str(e)}"
        )

    return validated_result.model_dump()


def save_match_result(
    db: Session,
    job_id: UUID,
    candidate_id: UUID,
    application_id: UUID | None,
    match_result: dict,
) -> MatchResult:
    """
    Save an AI candidate-job matching result
    into the match_results table.

    The application_id connects the AI match
    directly to the candidate's application.
    """

    if not match_result:
        raise ValueError(
            "Match result is required"
        )

    # -----------------------------------------
    # Collect missing skills
    # -----------------------------------------

    missing_skills = (
        match_result.get(
            "missing_required_skills",
            []
        )
        +
        match_result.get(
            "missing_preferred_skills",
            []
        )
    )

    # -----------------------------------------
    # Create MatchResult
    # -----------------------------------------

    saved_match = MatchResult(
        job_id=job_id,

        candidate_id=candidate_id,

        application_id=application_id,

        overall_score=match_result["match_score"],

        classification=match_result["recommendation"],

        missing_skills=missing_skills,

        explanation={
            "strengths": match_result.get(
                "strengths",
                []
            ),

            "weaknesses": match_result.get(
                "weaknesses",
                []
            ),

            "reasoning": match_result.get(
                "reasoning",
                ""
            ),
        },

        skill_score=(
            100
            if not match_result.get(
                "missing_required_skills"
            )
            else 0
        ),

        experience_score=(
            100
            if match_result.get(
                "experience_match"
            )
            else 0
        ),

        education_score=(
            100
            if match_result.get(
                "education_match"
            )
            else 0
        ),

        keyword_score=(
            100
            if match_result.get(
                "matched_skills"
            )
            else 0
        ),
    )

    # -----------------------------------------
    # Save to database
    # -----------------------------------------

    db.add(saved_match)

    db.commit()

    db.refresh(saved_match)

    return saved_match


def screen_application(
    db: Session,
    application_id: UUID,
) -> dict:
    """
    Screen a candidate application by comparing the candidate's CV analysis
    with the job analysis using Groq AI and saving/updating the match result.
    """
    application = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if not application:
        raise ValueError("Application not found.")

    if not application.resume_id:
        raise ValueError("Application has no associated resume.")

    cv_analysis_record = (
        db.query(AIAnalysis)
        .filter(
            AIAnalysis.entity_type == "RESUME",
            AIAnalysis.entity_id == application.resume_id,
            AIAnalysis.analysis_type == "CV_ANALYSIS",
        )
        .order_by(AIAnalysis.created_at.desc())
        .first()
    )

    if not cv_analysis_record:
        raise ValueError("Resume has not been analyzed yet.")

    job_analysis_record = (
        db.query(AIAnalysis)
        .filter(
            AIAnalysis.entity_type == "JOB",
            AIAnalysis.entity_id == application.job_id,
            AIAnalysis.analysis_type == "JOB_ANALYSIS",
        )
        .order_by(AIAnalysis.created_at.desc())
        .first()
    )

    if not job_analysis_record:
        raise ValueError("Job has not been analyzed yet.")

    # Run AI matching
    match_result = match_candidate_to_job(
        cv_analysis=cv_analysis_record.result_json,
        job_analysis=job_analysis_record.result_json,
    )

    # Check for existing match record
    existing_match = (
        db.query(MatchResult)
        .filter(MatchResult.application_id == application.id)
        .first()
    )

    if existing_match:
        missing_skills = (
            match_result.get("missing_required_skills", [])
            + match_result.get("missing_preferred_skills", [])
        )
        existing_match.overall_score = match_result["match_score"]
        existing_match.classification = match_result["recommendation"]
        existing_match.missing_skills = missing_skills
        existing_match.explanation = {
            "strengths": match_result.get("strengths", []),
            "weaknesses": match_result.get("weaknesses", []),
            "reasoning": match_result.get("reasoning", ""),
        }
        db.commit()
        db.refresh(existing_match)
        saved_match = existing_match
    else:
        saved_match = save_match_result(
            db=db,
            job_id=application.job_id,
            candidate_id=application.candidate_id,
            application_id=application.id,
            match_result=match_result,
        )

    return {
        "application_id": str(application.id),
        "job_id": str(application.job_id),
        "candidate_id": str(application.candidate_id),
        "resume_id": str(application.resume_id),
        "application_status": application.status,
        "match_id": str(saved_match.id),
        "match_score": float(saved_match.overall_score),
        "classification": saved_match.classification,
        "missing_skills": saved_match.missing_skills or [],
        "explanation": saved_match.explanation or {},
    }