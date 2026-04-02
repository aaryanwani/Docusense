import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.chunker import chunk_text
from app.services.text_cleanup import clean_generated_output

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2"
REQUEST_TIMEOUT_SECONDS = 120
SMALL_DOCUMENT_THRESHOLD = 9000
MAP_CHUNK_SIZE = 10000
MAP_OVERLAP = 120
MAX_MAP_WORKERS = 4


def ask_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"LLM error: {str(e)}"


def _choose_chunk_settings(text_length: int) -> tuple[int, int]:
    if text_length >= 120000:
        return 14000, 80
    if text_length >= 60000:
        return 12000, 100
    return MAP_CHUNK_SIZE, MAP_OVERLAP


def _build_chunk_prompt(chunk: str, chunk_number: int, total_chunks: int) -> str:
    return f"""
Extract only the important facts, dates, obligations, risks, clause headings, and financial details from this document portion.
Ignore signature blocks, blank sign/date fields, repeated underscores, repeated dashes, dotted blanks, and decorative symbols.
Keep the output short and dense.

OUTPUT RULES:
Use plain text only
Do not use markdown
Do not use asterisks
Do not use bullet symbols
Do not start lines with hyphens
Do not include empty sign/date placeholders

Text chunk ({chunk_number}/{total_chunks}):
{chunk}
    """


def _map_chunk(index_and_chunk: tuple[int, str], total_chunks: int) -> tuple[int, str]:
    index, chunk = index_and_chunk
    return index, ask_ollama(_build_chunk_prompt(chunk, index + 1, total_chunks))


def _map_reduce_summary(text: str) -> str:
    chunk_size, overlap = _choose_chunk_settings(len(text))
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    if not chunks:
        return "No summary generated."

    chunk_summaries = [None] * len(chunks)
    max_workers = min(MAX_MAP_WORKERS, len(chunks))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_map_chunk, item, len(chunks))
            for item in enumerate(chunks)
        ]
        for future in as_completed(futures):
            index, response = future.result()
            if not response.startswith("LLM error:"):
                chunk_summaries[index] = clean_generated_output(response)

    valid_summaries = [summary for summary in chunk_summaries if summary]
    if not valid_summaries:
        return clean_generated_output(ask_ollama("Respond with: Failed to process document chunks."))

    combined_notes = "\n\n".join(valid_summaries)
    return clean_generated_output(ask_ollama(_build_reduce_prompt(combined_notes)))


def _build_reduce_prompt(combined_notes: str) -> str:
    return f"""
You are a senior enterprise document analyst specializing in legal contracts, HR policies, pay notices, compliance documents, office rules, and internal business policies.

Your task is to analyze extracted notes from a large enterprise document and produce a final structured output that is accurate, concise, readable, and useful for both new employees and senior leadership.

Your output must help a reader quickly understand:
- what the document is about
- what actions, responsibilities, and obligations exist
- what dates, deadlines, payments, penalties, or risks matter
- what operational or compliance impact the document may have

STRICT OUTPUT RULES:
- Do NOT use asterisks or markdown
- Do NOT use headings with # symbols
- Use plain text only
- Use section titles in uppercase followed by a colon
- Do NOT use bullet symbols or list markers
- Do NOT start lines with hyphens, stars, dots, or numbering
- Ignore signature blocks, blank sign/date lines, underscores, repeated dashes, and filler symbols
- Keep the language professional, direct, and crisp
- Do not invent facts
- If something is not clearly stated in the extracted notes, say "Not clearly specified in the provided notes"
- Avoid repeating the same point in different words
- Keep each obligation or deadline on its own clean line

REQUIRED OUTPUT FORMAT:

DOCUMENT OVERVIEW:
Write 2-4 crisp sentences explaining the main purpose of the document and what it governs.

KEY OBLIGATIONS:
Write each obligation on its own line in plain sentences
Mention the responsible party when possible

IMPORTANT DATES AND DEADLINES:
Write each important date or notice period on its own line
If none are found, say "Not clearly specified in the provided notes"

FINANCIAL IMPACT:
Summarize payment terms, penalties, fees, compensation clauses, reimbursement terms, or financial obligations in short sentences
If a financial topic appears, use labels like PAYMENT:, PENALTY:, FEES:, or COMPENSATION:

RISKS AND COMPLIANCE CONCERNS:
Write each risk on its own line
Mention consequences of non-compliance if present
If risks are not clearly present, say "No major risks explicitly stated in the provided notes"

KEY CLAUSES:
If relevant, list important clauses using uppercase labels followed by a colon and short plain text descriptions
Examples: CONFIDENTIALITY:, TERMINATION:, LIABILITY:, PAYMENT:, COMPLIANCE:, DATA PROTECTION:, NOTICE PERIOD:

EXECUTIVE SUMMARY:
Write a short final summary in 3-5 lines for leadership or a new employee who wants the most important takeaways quickly.

Now analyze the following extracted notes carefully and produce the final structured output.

Extracted Notes:
{combined_notes}
    """


def generate_summary(text: str):
    # If text is small enough, do a direct summary
    if len(text) < SMALL_DOCUMENT_THRESHOLD:
        prompt = f"""
You are a senior enterprise document analyst specializing in legal contracts, HR policies, pay notices, compliance documents, office rules, and internal business policies.

Your task is to analyze an enterprise document and produce a final structured output that is accurate, concise, readable, and useful for both new employees and senior leadership.

Your output must help a reader quickly understand:
- what the document is about
- what actions, responsibilities, and obligations exist
- what dates, deadlines, payments, penalties, or risks matter
- what operational or compliance impact the document may have

STRICT OUTPUT RULES:
- Do NOT use asterisks or markdown
- Do NOT use headings with # symbols
- Use plain text only
- Use section titles in uppercase followed by a colon
- Do NOT use bullet symbols or list markers
- Do NOT start lines with hyphens, stars, dots, or numbering
- Ignore signature blocks, blank sign/date lines, underscores, repeated dashes, and filler symbols
- Keep the language professional, direct, and crisp
- Do not invent facts
- If something is not clearly stated, say "Not clearly specified"
- Avoid repeating the same point in different words
- Keep each obligation or deadline on its own clean line

REQUIRED OUTPUT FORMAT:

DOCUMENT OVERVIEW:
Write 2-4 crisp sentences explaining the main purpose of the document and what it governs.

KEY OBLIGATIONS:
Write each obligation on its own line in plain sentences
Mention the responsible party when possible

IMPORTANT DATES AND DEADLINES:
Write each important date or notice period on its own line
If none are found, say "Not clearly specified"

FINANCIAL IMPACT:
Summarize payment terms, penalties, fees, compensation clauses, reimbursement terms, or financial obligations in short sentences
If a financial topic appears, use labels like PAYMENT:, PENALTY:, FEES:, or COMPENSATION:

RISKS AND COMPLIANCE CONCERNS:
Write each risk on its own line
Mention consequences of non-compliance if present
If risks are not clearly present, say "No major risks explicitly stated"

KEY CLAUSES:
If relevant, list important clauses using uppercase labels followed by a colon and short plain text descriptions
Examples: CONFIDENTIALITY:, TERMINATION:, LIABILITY:, PAYMENT:, COMPLIANCE:, DATA PROTECTION:, NOTICE PERIOD:

EXECUTIVE SUMMARY:
Write a short final summary in 3-5 lines for leadership or a new employee who wants the most important takeaways quickly.

Document:
{text}
        """
        return clean_generated_output(ask_ollama(prompt))

    return _map_reduce_summary(text)
