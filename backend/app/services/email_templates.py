import html


def interview_invitation_email(
    candidate_name: str,
    job_title: str,
    start_time: str,
    end_time: str,
    timezone: str,
    mode: str,
    meeting_url: str | None = None,
    location: str | None = None,
) -> str:
    safe_candidate = html.escape(str(candidate_name or "Candidate"))
    safe_job = html.escape(str(job_title or "Position"))
    safe_start = html.escape(str(start_time or ""))
    safe_end = html.escape(str(end_time or ""))
    safe_tz = html.escape(str(timezone or "UTC"))
    safe_mode = html.escape(str(mode or "ONLINE"))

    interview_details = ""

    if mode == "ONLINE" and meeting_url:
        safe_url = html.escape(str(meeting_url))
        interview_details = f"""
        <p>
            <strong>Meeting Link:</strong>
            <a href="{safe_url}">
                Join Interview
            </a>
        </p>
        """

    elif mode == "IN_PERSON" and location:
        safe_loc = html.escape(str(location))
        interview_details = f"""
        <p>
            <strong>Location:</strong>
            {safe_loc}
        </p>
        """

    elif mode == "PHONE":
        interview_details = """
        <p>
            <strong>Mode:</strong>
            Phone Interview
        </p>
        """

    return f"""
    <html>
        <body>
            <h2>Interview Invitation</h2>
            <p>Dear {safe_candidate},</p>
            <p>
                We are pleased to inform you that you have been shortlisted for the position of
                <strong>{safe_job}</strong>.
            </p>
            <p>You have been invited to an interview.</p>
            <h3>Interview Details</h3>
            <p><strong>Start:</strong> {safe_start}</p>
            <p><strong>End:</strong> {safe_end}</p>
            <p><strong>Timezone:</strong> {safe_tz}</p>
            <p><strong>Mode:</strong> {safe_mode}</p>
            {interview_details}
            <p>Please make sure you are available at the scheduled time.</p>
            <p>Best regards,<br>AI Recruitment Team</p>
        </body>
    </html>
    """


def shortlist_email(
    candidate_name: str,
    job_title: str,
) -> str:
    safe_candidate = html.escape(str(candidate_name or "Candidate"))
    safe_job = html.escape(str(job_title or "Position"))

    return f"""
    <html>
        <body>
            <h2>Application Update</h2>
            <p>Dear {safe_candidate},</p>
            <p>Congratulations!</p>
            <p>
                Your application for <strong>{safe_job}</strong> has been shortlisted.
            </p>
            <p>Our recruitment team will contact you regarding the next step.</p>
            <p>Best regards,<br>AI Recruitment Team</p>
        </body>
    </html>
    """


def rejection_email(
    candidate_name: str,
    job_title: str,
) -> str:
    safe_candidate = html.escape(str(candidate_name or "Candidate"))
    safe_job = html.escape(str(job_title or "Position"))

    return f"""
    <html>
        <body>
            <h2>Application Update</h2>
            <p>Dear {safe_candidate},</p>
            <p>
                Thank you for applying for the <strong>{safe_job}</strong> position.
            </p>
            <p>
                After careful consideration, we will not be moving forward with your application at this time.
            </p>
            <p>We appreciate your interest and wish you success in your future opportunities.</p>
            <p>Best regards,<br>AI Recruitment Team</p>
        </body>
    </html>
    """