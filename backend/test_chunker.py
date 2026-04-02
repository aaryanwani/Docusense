from app.services.chunker import chunk_text

text = "This is a short sentence. " * 500  # Should be easily divisible by sentences
chunks = chunk_text(text, chunk_size=400, overlap=50)
print(f"Chunks: {len(chunks)}")
for i, c in enumerate(chunks[:2]):
    print(f"[{i}]: {len(c)} chars - {c[:30]}...{c[-30:]}")

# Test edge case: huge block of text with no spaces
text2 = "A" * 10000
chunks2 = chunk_text(text2, chunk_size=400, overlap=50)
print(f"Chunks2: {len(chunks2)} (expected {10000 / 350}ish)")
