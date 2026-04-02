from pydantic import BaseModel
from typing import List, Dict


class AnalyzeResponse(BaseModel):
    filename: str
    document_type: str
    char_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    preview: str
    entities: List[Dict]
    obligations: List[str]
    summary: str