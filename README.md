# DocuSense

DocuSense is a private, local-first document intelligence tool for firms that need to read large contracts, agreements, policies, and internal documents without sending sensitive files to third-party LLM platforms.

The core reason this exists is straightforward: firms should be able to simplify and analyze their own documents internally. Contracts, HR records, agreements, policies, and internal operational material often contain confidential business terms, legal obligations, financial details, employee information, and client-sensitive data. DocuSense keeps that workflow inside your environment.

## Why DocuSense

Most AI document tools depend on external APIs. That creates a privacy and governance problem for firms that cannot allow employees to upload documents to third-party LLMs or AI agents.

DocuSense is designed for:

- internal contract review
- agreement summarization
- policy and compliance review
- extracting obligations and key dates
- quick legal and operational understanding of long documents
- reducing the time required to read large or repetitive contracts

## What It Does

DocuSense accepts firm documents and produces a structured analysis locally.

It:

- extracts readable text from `.txt`, `.pdf`, `.doc`, and `.docx`
- identifies the document type
- extracts entities such as organizations, dates, and monetary values
- detects obligation-heavy clauses
- generates a structured summary using a local Ollama model
- removes signature blanks, repeated underscores, dotted lines, repeated dashes, and other low-signal filler
- avoids bullet-style `*` output and noisy formatting in the final response

## Privacy Model

DocuSense is built around a local processing model.

- the frontend runs locally
- the backend runs locally
- Ollama runs locally
- the language model is hosted locally
- uploaded files stay inside the local environment

That means employees do not need to send contracts or internal documents to external LLM providers just to get a summary or extract obligations.

## Supported Document Types

- `.txt`
- `.pdf`
- `.doc`
- `.docx`

`.doc` and `.docx` extraction currently uses macOS `textutil`, so that path is macOS-friendly as currently implemented.

## Main Features

- local-first document analysis
- local Ollama integration with `qwen2`
- legal and business-focused summaries
- detected obligations section
- extracted key entities
- cleaned output that removes signature placeholders and filler symbols
- faster handling for larger documents through chunked map-reduce summarization

## How It Works

### Frontend

The React frontend lets users drag and drop or browse for documents, submit them to the backend, and view:

- document type
- document stats
- key entities
- detected obligations
- AI-generated summary

### Backend

The FastAPI backend:

1. validates the uploaded file type
2. extracts text from the file
3. cleans low-signal content such as signature lines and blank placeholders
4. classifies the document
5. extracts entities
6. extracts obligations
7. generates a structured summary with Ollama

### LLM Layer

The LLM pipeline uses Ollama locally and is tuned for enterprise-style document analysis. For larger files, it uses chunking plus map-reduce summarization to reduce latency and avoid sending the entire document through one long prompt.

## Performance Approach

Large contracts can take time to process. DocuSense includes a few optimizations to improve that:

- larger dynamic chunk sizes for large documents
- reduced overlap between chunks
- parallel chunk processing for the map stage
- direct summarization for smaller documents
- parallel execution of entity extraction, obligation extraction, and summary generation

This keeps response time lower than a naive full-document prompt flow, especially on longer PDFs and agreements.

## Output Cleanup

DocuSense intentionally removes common legal-document noise before and after analysis:

- signature blanks
- date blanks
- repeated underscores
- repeated dashes
- dotted placeholder lines
- decorative symbols
- stray `*` and bullet-like output

This makes the response cleaner for business users and easier to review quickly.

## Project Structure

```text
docusense/
  backend/
    app/
      main.py
      services/
  frontend/
    src/
```

## Local Requirements

- Python 3.12+
- Node.js / npm
- Ollama
- local Ollama model: `qwen2`
- macOS if you need `.doc` / `.docx` support with the current extractor implementation

## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

## Ollama Setup

Install and run Ollama locally, then ensure the `qwen2` model is available.

```bash
ollama pull qwen2
ollama serve
```

The backend currently expects Ollama at:

```text
http://localhost:11434/api/generate
```

## Local URLs

- frontend: `http://127.0.0.1:5173/`
- backend: `http://127.0.0.1:8000/`
- docs: `http://127.0.0.1:8000/docs`
- Ollama: `http://127.0.0.1:11434/`

## API

### `POST /analyze`

Uploads a document and returns:

- filename
- document type
- document statistics
- preview text
- entities
- obligations
- summary

### `GET /health`

Simple health endpoint for the backend.

## Intended Use In Firms

DocuSense is meant to be an internal document reader that helps teams quickly understand long or repetitive firm documents without exposing them to third-party AI systems.

Good use cases include:

- vendor agreements
- service contracts
- employment agreements
- HR policies
- internal compliance documents
- NDAs
- payment terms and commercial clauses
- onboarding or operational documentation

## Current Limitations

- `.doc` and `.docx` support currently relies on macOS `textutil`
- summary quality depends on the local Ollama model
- very large PDFs will still take time because local inference is the slowest stage
- there is not yet a background job queue or streaming progress system

## Next Improvements

- streaming status updates during long analysis
- background job queue for very large documents
- cached summaries for repeat uploads
- configurable model selection
- stronger contract-specific clause extraction
- side-by-side clause risk highlighting
- exportable report output

## License
