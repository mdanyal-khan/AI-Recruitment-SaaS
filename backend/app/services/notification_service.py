from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.services.email_service import send_email


def send_notification_email(
    db: Session,
    notification: Notification,
    recipient_email: str,
) -> Notification:

    try:
        send_email(
            to_email=recipient_email,
            subject=notification.subject or "",
            html_content=notification.message or "",
        )

        notification.status = "SENT"
        notification.sent_at = datetime.utcnow()

        db.commit()
        db.refresh(notification)

        return notification

    except Exception as e:

        notification.status = "FAILED"

        db.commit()
        db.refresh(notification)

        raise RuntimeError(
            f"Notification email failed: {str(e)}"
        )

def create_notification(
    db: Session,
    user_id: UUID,
    notification_type: str,
    channel: str,
    subject: str,
    message: str,
) -> Notification:

    notification = Notification(
        user_id=user_id,
        type=notification_type,
        channel=channel,
        subject=subject,
        message=message,
        status="PENDING",
    )

    db.add(notification)

    db.commit()

    db.refresh(notification)

    return notification