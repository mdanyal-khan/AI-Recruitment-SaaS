from typing import Literal

from pydantic import BaseModel


class MatchResult(BaseModel):
    match_score: float

    recommendation: Literal[
        "STRONG_MATCH",
        "GOOD_MATCH",
        "PARTIAL_MATCH",
        "WEAK_MATCH",
        "NOT_A_MATCH",
    ]

    matched_skills: list[str]
    missing_required_skills: list[str]
    missing_preferred_skills: list[str]

    experience_match: bool
    education_match: bool
    certification_match: bool
    language_match: bool

    strengths: list[str]
    weaknesses: list[str]
    reasoning: str