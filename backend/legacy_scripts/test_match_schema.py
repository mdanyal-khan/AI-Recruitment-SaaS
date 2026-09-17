from app.schemas.match_result import MatchResult


result = MatchResult(
    match_score=87.5,
    recommendation="STRONG_MATCH",
    matched_skills=[
        "Python",
        "FastAPI",
        "PostgreSQL",
    ],
    missing_required_skills=[],
    missing_preferred_skills=[
        "Docker",
    ],
    experience_match=True,
    education_match=True,
    certification_match=False,
    language_match=True,
    strengths=[
        "Strong backend development experience",
        "Good Python skills",
    ],
    weaknesses=[
        "No Docker experience",
    ],
    reasoning=(
        "The candidate has most of the required technical skills "
        "and meets the experience and education requirements."
    ),
)

print(result)
print("\nMatch score:", result.match_score)
print("Recommendation:", result.recommendation)