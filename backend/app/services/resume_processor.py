from app.services.pdf_extractor import extract_text_from_pdf


def process_resume(file_data: bytes) -> str:
    """
    Extract readable text from a resume PDF.
    """

    try:
        text = extract_text_from_pdf(file_data)

    except ValueError:
        raise

    except Exception as e:
        raise ValueError(
            f"Failed to process resume: {str(e)}"
        )

    return text