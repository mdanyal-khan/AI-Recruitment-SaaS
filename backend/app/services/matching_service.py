import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.match_result import MatchResult
from app.core.config import settings
from app.core.groq import groq_client
from app.schemas.match_result import MatchResult as MatchResultSchema


def match_candidate_to_job(
    cv_analysis: dict,
    job_analysis: dict,
) -> dict:
    """
    Match a candidate's CV analysis against a job analysis using Groq AI.
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
- recommendation: MUST be one of: "STRONG_MATCH", "GOOD_MATCH", "PARTIAL_MATCH", "WEAK_MATCH", "NOT_A_MATCH"
- matched_skills: skills from the job requirements that the candidate has
- missing_required_skills: required skills the candidate does not have
- missing_preferred_skills: preferred skills the candidate does not have
- experience_match: true if the candidate satisfies the required experience
- education_match: true if the candidate satisfies the education requirement
- certification_match: true if the candidate satisfies the certification requirements
- language_match: true if the candidate satisfies the language requirements
- strengths: list of reasons the candidate matches
- weaknesses: list of reasons the candidate does not match
- reasoning: concise explanation of the overall decision

Return JSON only.
"""

    user_prompt = f"""
CANDIDATE CV ANALYSIS:

{json.dumps(cv_analysis, indent=2)}


JOB ANALYSIS:

{json.dumps(job_analysis, indent=2)}


Compare the candidate with the job and produce the matching result.
"""

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

    if not response.choices:
        raise RuntimeError(
            "Groq returned no choices"
        )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "Groq returned an empty response"
        )

    try:
        result = json.loads(content)

    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Groq returned invalid JSON: {str(e)}"
        )

    try:
        validated_result = MatchResultSchema.model_validate(result)

    except Exception as e:
        raise RuntimeError(
            f"Invalid matching result: {str(e)}"
        )

    return validated_result.model_dump()


# Maps unexpected AI values to valid DB values
_CLASSIFICATION_MAP = {
    "STRONG_MATCH": "STRONG_MATCH",
    "GOOD_MATCH": "GOOD_MATCH",
    "PARTIAL_MATCH": "PARTIAL_MATCH",
    "WEAK_MATCH": "WEAK_MATCH",
    "NOT_A_MATCH": "NOT_A_MATCH",
    # Common AI fallbacks
    "MEDIUM_MATCH": "PARTIAL_MATCH",
    "AVERAGE_MATCH": "PARTIAL_MATCH",
    "LOW_MATCH": "WEAK_MATCH",
    "NO_MATCH": "NOT_A_MATCH",
    "REJECT": "NOT_A_MATCH",
    "EXCELLENT_MATCH": "STRONG_MATCH",
}


def save_match_result(
    db: Session,
    job_id: UUID,
    candidate_id: UUID,
    match_result: dict,
    application_id: UUID | None = None,
) -> MatchResult:
    """
    Save an AI-generated candidate-job match result
    into the match_results table.
    """

    if not match_result:
        raise ValueError("Match result is required")

    missing_skills = (
        match_result.get("missing_required_skills", [])
        + match_result.get("missing_preferred_skills", [])
    )

    explanation = {
        "matched_skills": match_result.get(
            "matched_skills",
            [],
        ),
        "strengths": match_result.get(
            "strengths",
            [],
        ),
        "weaknesses": match_result.get(
            "weaknesses",
            [],
        ),
        "reasoning": match_result.get(
            "reasoning",
            "",
        ),
        "experience_match": match_result.get(
            "experience_match",
            False,
        ),
        "education_match": match_result.get(
            "education_match",
            False,
        ),
        "certification_match": match_result.get(
            "certification_match",
            False,
        ),
        "language_match": match_result.get(
            "language_match",
            False,
        ),
    }

    overall_score = float(
        match_result.get("match_score", 0)
    )

    skill_score = (
        100.0
        if not match_result.get("missing_required_skills")
        else 0.0
    )

    experience_score = (
        100.0
        if match_result.get("experience_match")
        else 0.0
    )

    education_score = (
        100.0
        if match_result.get("education_match")
        else 0.0
    )

    keyword_score = (
        100.0
        if match_result.get("matched_skills")
        else 0.0
    )

    db_match = MatchResult(
        job_id=job_id,
        candidate_id=candidate_id,
        application_id=application_id,
        overall_score=overall_score,
        skill_score=skill_score,
        experience_score=experience_score,
        education_score=education_score,
        keyword_score=keyword_score,
        classification=_CLASSIFICATION_MAP.get(
            match_result.get("recommendation", ""),
            "PARTIAL_MATCH",  # safe default
        ),
        explanation=explanation,
        missing_skills=missing_skills,
    )

    db.add(db_match)
    db.commit()
    db.refresh(db_match)

    return db_match