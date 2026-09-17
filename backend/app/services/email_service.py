import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


# =========================================================
# SEND EMAIL
# =========================================================

def sanitize_email_header(header: str) -> str:
    """Strip carriage returns and newlines to prevent SMTP header injection."""
    return str(header or "").replace("\r", "").replace("\n", "").strip()


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
) -> None:
    """
    Send an HTML email using SMTP.
    """

    message = MIMEMultipart("alternative")

    safe_subject = sanitize_email_header(subject)

    message["From"] = (
        f"{settings.SMTP_FROM_NAME} "
        f"<{settings.SMTP_FROM_EMAIL}>"
    )

    message["To"] = to_email.strip()
    message["Subject"] = safe_subject

    html_part = MIMEText(
        html_content,
        "html",
    )

    message.attach(html_part)

    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
        ) as server:

            server.starttls()

            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            )

            server.sendmail(
                settings.SMTP_FROM_EMAIL,
                to_email,
                message.as_string(),
            )

    except Exception as e:
        raise RuntimeError(
            f"Failed to send email: {str(e)}"
        )


# =========================================================
# SEND OFFER EMAIL
# =========================================================

def send_offer_email(
    recipient_email: str,
    candidate_name: str,
    job_title: str,
    salary: str,
    currency: str,
    start_date: str,
    expiration_date: str,
) -> None:
    """
    Send a job offer email to the candidate.
    """
    import html

    safe_candidate = html.escape(str(candidate_name or "Candidate"))
    safe_job = html.escape(str(job_title or "Position"))
    safe_salary = html.escape(str(salary or ""))
    safe_currency = html.escape(str(currency or "USD"))
    safe_start = html.escape(str(start_date or ""))
    safe_exp = html.escape(str(expiration_date or ""))

    subject = f"Job Offer - {safe_job}"

    body = f"""
    <html>
        <body>
            <p>Hello {safe_candidate},</p>

            <p>
                <strong>Congratulations!</strong>
            </p>

            <p>
                We are pleased to offer you the position of:
            </p>

            <h3>{safe_job}</h3>

            <p>
                <strong>Offer Details:</strong>
            </p>

            <ul>
                <li>
                    <strong>Salary:</strong>
                    {safe_salary} {safe_currency}
                </li>

                <li>
                    <strong>Start Date:</strong>
                    {safe_start}
                </li>

                <li>
                    <strong>Offer Expiration Date:</strong>
                    {safe_exp}
                </li>
            </ul>

            <p>
                Please log in to the recruitment portal
                to review and respond to your offer.
            </p>

            <p>
                Best regards,<br>
                <strong>AI Recruitment SaaS</strong>
            </p>
        </body>
    </html>
    """

    send_email(
        to_email=recipient_email,
        subject=subject,
        html_content=body,
    )