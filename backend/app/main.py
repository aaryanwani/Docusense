from concurrent.futures import ThreadPoolExecutor
import json
import re

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.schemas.analyze import AnalyzeResponse
from app.services.ner import extract_entities
from app.services.classifier import classify_document
from app.services.obligations import extract_obligations
from app.services.llm import generate_summary, stream_summary_events
from app.services.text_extractor import extract_text_from_bytes

app = FastAPI(
    title="DocuSense - Document Intelligence API",
    version="0.1.0"
)

# Add CORS Middleware to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "DocuSense API is running. Visit /docs for Swagger UI."
    }


@app.get("/health")
def health():
    return {"status": "ok"}


def _validate_filename(filename: str) -> None:
    if not filename.lower().endswith((".txt", ".pdf", ".doc", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only .txt, .pdf, .doc, and .docx files are supported."
        )


def _prepare_document_analysis(filename: str, content_bytes: bytes) -> tuple[str, dict]:
    _validate_filename(filename)

    text = extract_text_from_bytes(filename, content_bytes).strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No readable text could be extracted from the uploaded file."
        )

    # Basic metadata analytics
    char_count = len(text)
    word_count = len(text.split())
    sentence_count = len(re.findall(r"[.!?]+", text))
    paragraph_count = text.count("\n\n")

    # Create preview (first 300 characters)
    preview = text[:300].replace("\n", " ").strip()

    # 🔥 AI STEP 1 — Classify Document
    document_type = classify_document(text)

    metadata = {
        "filename": filename,
        "document_type": document_type,
        "char_count": char_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "preview": preview,
    }

    return text, metadata


def _build_result_payload(metadata: dict, entities: list, obligations: list, summary: str) -> dict:
    return {
        **metadata,
        "entities": entities,
        "obligations": obligations,
        "summary": summary,
    }


def _serialize_event(event_type: str, **payload) -> str:
    return json.dumps({"type": event_type, **payload}) + "\n"


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)):
    filename = file.filename or ""
    content_bytes = await file.read()
    text, metadata = _prepare_document_analysis(filename, content_bytes)

    with ThreadPoolExecutor(max_workers=3) as executor:
        entities_future = executor.submit(extract_entities, text)
        obligations_future = executor.submit(extract_obligations, text)
        summary_future = executor.submit(generate_summary, text)

        entities = entities_future.result()
        obligations = obligations_future.result()
        summary = summary_future.result()

    return AnalyzeResponse(**_build_result_payload(metadata, entities, obligations, summary))


@app.post("/analyze/stream")
async def analyze_stream(file: UploadFile = File(...)):
    filename = file.filename or ""
    content_bytes = await file.read()

    def event_stream():
        try:
            yield _serialize_event("status", message="Parsing document")
            text, metadata = _prepare_document_analysis(filename, content_bytes)

            yield _serialize_event(
                "metadata",
                data=_build_result_payload(metadata, [], [], "")
            )
            yield _serialize_event("status", message="Extracting entities and obligations")

            with ThreadPoolExecutor(max_workers=2) as executor:
                entities_future = executor.submit(extract_entities, text)
                obligations_future = executor.submit(extract_obligations, text)

                summary = ""
                for event in stream_summary_events(text):
                    if event["type"] == "summary_complete":
                        summary = event["summary"]
                    yield _serialize_event(event["type"], **{k: v for k, v in event.items() if k != "type"})

                yield _serialize_event("status", message="Finalizing result")
                entities = entities_future.result()
                obligations = obligations_future.result()

            yield _serialize_event(
                "result",
                data=_build_result_payload(metadata, entities, obligations, summary)
            )
        except HTTPException as exc:
            yield _serialize_event("error", message=exc.detail, status_code=exc.status_code)
        except Exception as exc:
            yield _serialize_event("error", message=str(exc), status_code=500)

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
