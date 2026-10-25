"""Extract text from a user-supplied PDF entirely in memory."""
import pymupdf

MAX_PDF_BYTES = 5 * 1024 * 1024
MAX_EXTRACTED_CHARS = 18000

class CVError(ValueError):
    pass


def extract_pdf_text(raw: bytes) -> str:
    if not raw or len(raw) > MAX_PDF_BYTES or not raw.startswith(b"%PDF-"):
        raise CVError("Please upload a valid text-based PDF under 5 MB.")
    try:
        with pymupdf.open(stream=raw, filetype="pdf") as doc:
            if doc.is_encrypted:
                raise CVError("Encrypted PDFs are not supported.")
            if len(doc) > 20:
                raise CVError("Please upload a CV with 20 pages or fewer.")
            text = "\n".join(page.get_text("text", sort=True) for page in doc)
    except CVError:
        raise
    except Exception as exc:
        raise CVError("The PDF could not be read. Please export a text-based PDF.") from None
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if len(text) < 60:
        raise CVError("No readable text was found. Scanned/image-only PDFs need OCR and are not supported.")
    return text[:MAX_EXTRACTED_CHARS]
