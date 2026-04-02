import re
import spacy
from app.services.chunker import chunk_text
from app.services.text_cleanup import clean_obligation_text

nlp = spacy.blank("en")
nlp.add_pipe("sentencizer")

OBLIGATION_PATTERNS = (
    "shall",
    "must",
    "required to",
    "agree to",
    "agrees to",
)


def _normalize_obligation(sentence_text: str) -> str:
    sentence_text = re.sub(r"\s+", " ", sentence_text).strip()
    return clean_obligation_text(sentence_text)

def extract_obligations(text: str):
    obligations = []
    seen = set()

    chunks = chunk_text(text, chunk_size=10000, overlap=250)

    for doc in nlp.pipe(chunks, batch_size=8):
        for sent in doc.sents:
            sentence_text = _normalize_obligation(sent.text)
            if not sentence_text:
                continue

            if len(sentence_text) < 20:
                continue

            lowered = sentence_text.lower()
            if any(pattern in lowered for pattern in OBLIGATION_PATTERNS):
                dedupe_key = sentence_text.lower()
                if dedupe_key not in seen:
                    obligations.append(sentence_text)
                    seen.add(dedupe_key)

    return obligations
