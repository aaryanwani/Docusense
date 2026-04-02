import io
import os
import subprocess
import tempfile

from fastapi import UploadFile, HTTPException

from app.services.text_cleanup import clean_extracted_text


SUPPORTED_EXTENSIONS = (".txt", ".pdf", ".doc", ".docx")


def _extract_office_document_text(filename: str, content_bytes: bytes) -> str:
    suffix = os.path.splitext(filename)[1] or ".docx"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(content_bytes)
        temp_path = temp_file.name

    try:
        result = subprocess.run(
            ["/usr/bin/textutil", "-convert", "txt", "-stdout", temp_path],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(status_code=400, detail="The document took too long to parse.") from exc
    except subprocess.CalledProcessError as exc:
        raise HTTPException(
            status_code=400,
            detail="This .doc or .docx file could not be read. Try exporting it as .docx, .pdf, or .txt.",
        ) from exc
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass

    return result.stdout

def extract_text(file: UploadFile) -> str:
    filename = (file.filename or "").lower()

    if filename.endswith(".txt"):
        # Note: UploadFile.read() is async in the endpoint, so we pass bytes
        raise RuntimeError("Use extract_text_from_bytes for .txt")

    if filename.endswith(".pdf"):
        import pdfplumber
        # We'll read bytes in the endpoint and pass to this function
        raise RuntimeError("Use extract_text_from_bytes for .pdf")

    if filename.endswith((".doc", ".docx")):
        raise RuntimeError("Use extract_text_from_bytes for .doc and .docx")

    raise HTTPException(status_code=400, detail="Only .txt, .pdf, .doc, and .docx are supported.")

def extract_text_from_bytes(filename: str, content_bytes: bytes) -> str:
    filename_l = filename.lower()

    if filename_l.endswith(".txt"):
        return clean_extracted_text(content_bytes.decode("utf-8", errors="ignore"))

    if filename_l.endswith(".pdf"):
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
            pages_text = []
            for page_number, page in enumerate(pdf.pages, start=1):
                t = page.extract_text() or ""
                if t.strip():
                    pages_text.append(f"[PAGE {page_number}]\n{t.strip()}")
            return clean_extracted_text("\n\n".join(pages_text))

    if filename_l.endswith((".doc", ".docx")):
        return clean_extracted_text(_extract_office_document_text(filename, content_bytes))

    raise HTTPException(
        status_code=400,
        detail=f"Only {', '.join(SUPPORTED_EXTENSIONS)} are supported.",
    )
