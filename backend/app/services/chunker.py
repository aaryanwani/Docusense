PAGE_BREAK_MARKERS = ("[PAGE ", "\f")


def _find_last_boundary(text: str, start: int, end: int, minimum_end: int) -> int:
    for marker in PAGE_BREAK_MARKERS:
        boundary = text.rfind(marker, start, end)
        if boundary >= minimum_end:
            return boundary

    safe_end = text.rfind("\n\n", start, end)
    if safe_end >= minimum_end:
        return safe_end

    safe_end = text.rfind("\n", start, end)
    if safe_end >= minimum_end:
        return safe_end

    safe_end = text.rfind(". ", start, end)
    if safe_end >= minimum_end:
        return safe_end + 1

    safe_end = text.rfind(" ", start, end)
    if safe_end > start:
        return safe_end

    return end


def _find_next_start(text: str, next_start: int, safe_end: int) -> int:
    if next_start <= 0:
        return 0

    for marker in PAGE_BREAK_MARKERS:
        marker_pos = text.find(marker, next_start, safe_end)
        if marker_pos != -1:
            return marker_pos

    safe_start = text.find("\n\n", next_start, safe_end)
    if safe_start != -1:
        return safe_start + 2

    safe_start = text.find("\n", next_start, safe_end)
    if safe_start != -1:
        return safe_start + 1

    safe_start = text.find(". ", next_start, safe_end)
    if safe_start != -1:
        return safe_start + 2

    safe_start = text.find(" ", next_start, safe_end)
    if safe_start != -1:
        return safe_start + 1

    return next_start


def chunk_text(text: str, chunk_size: int = 4000, overlap: int = 200) -> list[str]:
    """
    Intelligently chunks text by looking for safe boundaries (newlines, sentences, spaces) 
    to prevent cutting context or words in half, while maintaining overlap for the map-reduce LLM step.
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    i = 0
    text_length = len(text)
    
    while i < text_length:
        end = min(i + chunk_size, text_length)
        
        # If this is the last chunk, take the remaining text
        if end == text_length:
            chunk = text[i:end].strip()
            if chunk:
                chunks.append(chunk)
            break
            
        minimum_end = i + (chunk_size // 2)
        safe_end = _find_last_boundary(text, i, end, minimum_end)

        chunk = text[i:safe_end].strip()
        if chunk:
            chunks.append(chunk)
        
        # 2. Calculate the next start position based on overlap
        next_start = safe_end - overlap
        
        # Try to find a safe boundary for the start of the next chunk so we don't start mid-word
        if next_start > i:
            i = min(_find_next_start(text, next_start, safe_end), safe_end)
        else:
            # Prevent infinite loops if overlap happens to be bigger than the advance delta
            i = safe_end
            
    return chunks
