import re

PAGE_MARKER_RE = re.compile(r"^\[PAGE \d+\]$")
PLACEHOLDER_TOKEN_RE = re.compile(r"(?:_{3,}|\.{4,}|={3,}|(?:-\s*){3,}|(?:\*\s*){3,}|(?:x\s*){4,})")
LEADING_BULLET_RE = re.compile(r"^\s*(?:[-*•▪●◦‣–—]+\s*)+")
LEADING_NUMBER_RE = re.compile(r"^\s*\d+[.)]\s+")
SIGNATURE_LINE_RE = re.compile(
    r"^(?:signature|signed by|authorized signature|printed name|name|date|title|witness|initials?)\s*[:\-]?\s*(?:[_\-.=xX ]{2,})?$",
    re.IGNORECASE,
)
PLACEHOLDER_LINE_RE = re.compile(
    r"^(?:[_\-.=]{3,}|(?:-\s*){3,}|(?:\.\s*){3,}|(?:x\s*){4,}|(?:\*\s*){3,})$",
    re.IGNORECASE,
)
SIGNATURE_PLACEHOLDER_RE = re.compile(
    r"(?:signature|signed by|authorized signature|printed name|name|date|title|witness|initials?)\s*[:\-]?\s*(?:_{2,}|\.{3,}|={3,}|-{3,})",
    re.IGNORECASE,
)
UPPERCASE_HEADING_PREFIX_RE = re.compile(r"^(?:\[PAGE \d+\]\s*)?(?:[A-Z][A-Z\s/&]{3,}:?\s+)+")


def _normalize_whitespace(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    value = re.sub(r"[ \t]+", " ", value)
    return value


def _is_low_signal_line(line: str) -> bool:
    if not line:
        return False
    if PAGE_MARKER_RE.match(line):
        return False
    if PLACEHOLDER_LINE_RE.match(line):
        return True
    if SIGNATURE_LINE_RE.match(line):
        return True
    if SIGNATURE_PLACEHOLDER_RE.search(line):
        return True

    compact = re.sub(r"\s+", "", line)
    if not compact:
        return False

    punctuation_count = sum(1 for char in compact if not char.isalnum())
    if punctuation_count / max(len(compact), 1) >= 0.7 and not any(char.isalnum() for char in compact):
        return True

    return False


def _clean_line(line: str) -> str:
    line = _normalize_whitespace(line).strip()
    if not line:
        return ""
    if _is_low_signal_line(line):
        return ""

    line = PLACEHOLDER_TOKEN_RE.sub(" ", line)
    line = line.replace("**", " ").replace("`", "")
    line = re.sub(r"\s+", " ", line).strip(" -_*•▪●◦‣–—")

    if _is_low_signal_line(line):
        return ""

    return line.strip()


def clean_extracted_text(text: str) -> str:
    text = _normalize_whitespace(text)
    cleaned_lines = []
    blank_pending = False

    for raw_line in text.split("\n"):
        line = _clean_line(raw_line)
        if not line:
            if cleaned_lines and not blank_pending:
                cleaned_lines.append("")
                blank_pending = True
            continue

        cleaned_lines.append(line)
        blank_pending = False

    cleaned = "\n".join(cleaned_lines).strip()
    return re.sub(r"\n{3,}", "\n\n", cleaned)


def clean_obligation_text(text: str) -> str:
    text = _clean_line(text)
    if not text:
        return ""

    text = PAGE_MARKER_RE.sub("", text)
    text = LEADING_NUMBER_RE.sub("", text)
    text = LEADING_BULLET_RE.sub("", text)
    text = UPPERCASE_HEADING_PREFIX_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip(" -_*•▪●◦‣–—")

    if len(text) < 20 or _is_low_signal_line(text):
        return ""

    return text


def clean_generated_output(text: str) -> str:
    text = _normalize_whitespace(text).replace("*", "").replace("`", "")
    cleaned_lines = []

    for raw_line in text.split("\n"):
        line = _clean_line(raw_line)
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        line = LEADING_BULLET_RE.sub("", line)
        line = re.sub(r"^\s*[-–—]+\s*", "", line)
        line = re.sub(r"\s+", " ", line).strip()

        if line:
            cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines).strip()
    return re.sub(r"\n{3,}", "\n\n", cleaned)
