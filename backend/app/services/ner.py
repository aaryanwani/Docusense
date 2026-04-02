import spacy
from datetime import datetime
import re
from app.services.chunker import chunk_text

# Load model once
nlp = spacy.load("en_core_web_sm", exclude=["parser", "lemmatizer"])

# Only keep important entity types
ALLOWED_LABELS = {"PERSON", "ORG", "DATE", "MONEY", "GPE"}


def normalize_money(text: str):
    # Remove commas and dollar signs
    clean = text.replace("$", "").replace(",", "")
    match = re.search(r"\d+(\.\d+)?", clean)
    return float(match.group()) if match else None


def normalize_date(text: str):
    try:
        parsed = datetime.strptime(text, "%B %d, %Y")
        return parsed.date().isoformat()
    except:
        return text  # fallback


def extract_entities(text: str, chunk_size: int = 8000):

    entities = []
    seen = set()

    chunks = chunk_text(text, chunk_size=chunk_size, overlap=150)

    for doc in nlp.pipe(chunks, batch_size=4):

        for ent in doc.ents:
            if ent.label_ not in ALLOWED_LABELS:
                continue

            key = (ent.text.strip(), ent.label_)
            if key in seen:
                continue
            seen.add(key)

            normalized_value = ent.text

            if ent.label_ == "MONEY":
                normalized = normalize_money(ent.text)
                if normalized is not None:
                    normalized_value = normalized

            elif ent.label_ == "DATE":
                normalized_value = normalize_date(ent.text)

            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "normalized": normalized_value
            })

    return entities
