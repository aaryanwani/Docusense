from app.services.text_cleanup import clean_extracted_text, clean_generated_output, clean_obligation_text


raw_document = """
SERVICE AGREEMENT

Signature: ______________________
Date: ---------------------------

Acme Corp shall pay Beta LLC $5000 by April 15, 2026.
The receiving party must keep confidential information secret.
"""

cleaned_document = clean_extracted_text(raw_document)
assert "Signature:" not in cleaned_document
assert "Date:" not in cleaned_document
assert "Acme Corp shall pay Beta LLC $5000 by April 15, 2026." in cleaned_document

generated_output = """
KEY OBLIGATIONS:
* Acme Corp shall pay Beta LLC by April 15, 2026.
- The receiving party must keep confidential information secret.
Date: ______________________
"""

cleaned_output = clean_generated_output(generated_output)
assert "*" not in cleaned_output
assert "\n-" not in cleaned_output
assert "Date:" not in cleaned_output

obligation = "1. SERVICE AGREEMENT Acme Corp shall pay Beta LLC by April 15, 2026."
cleaned_obligation = clean_obligation_text(obligation)
assert cleaned_obligation == "Acme Corp shall pay Beta LLC by April 15, 2026."

print("text cleanup checks passed")
