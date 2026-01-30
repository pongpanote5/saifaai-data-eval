from utils.chunking import chunk_text


def test_chunk_text_sanity():
    text = "Paragraph one. " * 50
    chunks = chunk_text(text)
    assert chunks
    assert all(chunk.strip() for chunk in chunks)
    if len(chunks) >= 2:
        assert chunks[1][:10]
