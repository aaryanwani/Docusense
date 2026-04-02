def classify_document(text: str) -> str:
    text_lower = text.lower()

    # Legal indicators
    if any(keyword in text_lower for keyword in [
        "agreement", "party", "hereby", "termination", "liability", "indemnify"
    ]):
        return "LEGAL_CONTRACT"

    # HR / Pay Notice
    if any(keyword in text_lower for keyword in [
        "salary", "compensation", "leave policy", "overtime", "benefits", "notice period"
    ]):
        return "HR_POLICY"

    # Compliance
    if any(keyword in text_lower for keyword in [
        "compliance", "regulation", "iso", "audit", "policy requirement"
    ]):
        return "COMPLIANCE_RULE"

    # Office rules
    if any(keyword in text_lower for keyword in [
        "office hours", "code of conduct", "security badge", "workplace policy"
    ]):
        return "OFFICE_GUIDELINE"

    return "GENERAL_DOCUMENT"