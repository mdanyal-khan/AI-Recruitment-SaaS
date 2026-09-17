from io import BytesIO
from pypdf import PdfReader


def extract_text_from_pdf(file_data: bytes) -> str:
    if not file_data or not file_data.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF format: file does not match PDF signature.")

    try:
        pdf_file = BytesIO(file_data)
        reader = PdfReader(pdf_file)

        extracted_text = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text)

        result = "\n".join(extracted_text).strip()

        if not result:
            raise ValueError(
                "No readable text found in PDF"
            )

        return result

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")