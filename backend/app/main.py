from concurrent.futures import ThreadPoolExecutor
import re

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.analyze import AnalyzeResponse
from app.services.ner import extract_entities
from app.services.classifier import classify_document
from app.services.obligations import extract_obligations
from app.services.llm import generate_summary
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


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)):
    filename = file.filename or ""

    # Validate file type
    if not filename.lower().endswith((".txt", ".pdf", ".doc", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only .txt, .pdf, .doc, and .docx files are supported."
        )

    # Read file asynchronously
    content_bytes = await file.read()

    # Extract text from the uploaded document
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

    # Run the heavier analysis steps in parallel for better large-document latency.
    with ThreadPoolExecutor(max_workers=3) as executor:
        entities_future = executor.submit(extract_entities, text)
        obligations_future = executor.submit(extract_obligations, text)
        summary_future = executor.submit(generate_summary, text)

        entities = entities_future.result()
        obligations = obligations_future.result()
        summary = summary_future.result()

    # Return structured response
    return AnalyzeResponse(
        filename=filename,
        document_type=document_type,
        char_count=char_count,
        word_count=word_count,
        sentence_count=sentence_count,
        paragraph_count=paragraph_count,
        preview=preview,
        entities=entities,
        obligations=obligations,
        summary=summary
    )
