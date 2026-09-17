from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.interview import Interview


def validate_interview_time(
    start_time: datetime,
    end_time: datetime,
) -> None:

    if end_time <= start_time:
        raise ValueError(
            "Interview end time must be after start time."
        )

    now = datetime.now(timezone.utc)

    if start_time <= now:
        raise ValueError(
            "Interview must be scheduled for a future time."
        )


def check_time_conflict(
    db: Session,
    start_time: datetime,
    end_time: datetime,
    scheduled_by: UUID | None = None,
) -> bool:

    query = db.query(Interview).filter(
        Interview.status.in_(
            [
                "SCHEDULED",
                "CONFIRMED",
            ]
        ),
        Interview.start_time < end_time,
        Interview.end_time > start_time,
    )

    if scheduled_by:
        query = query.filter(
            Interview.scheduled_by == scheduled_by
        )

    return query.first() is not None