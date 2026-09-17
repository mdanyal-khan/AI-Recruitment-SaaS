from app.services.email_service import send_email


send_email(
    to_email="mshadman701@gmail.com",
    subject="AI Recruitment SaaS Test Email",
    html_content="""
    <html>
        <body>
            <h2>Email Test Successful</h2>

            <p>
                This email was sent from the
                AI Recruitment SaaS backend.
            </p>

            <p>
                Email service is working correctly.
            </p>
        </body>
    </html>
    """,
)

print("Email sent successfully.")