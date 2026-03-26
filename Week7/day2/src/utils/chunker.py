MIN_WORDS = 40   # anything smaller is likely a PDF artifact


def chunk_text(text, source="unknown", doc_type="unknown",
               chunk_size=500, overlap=100):
    words = text.split()
    chunks = []
    chunk_index = 0

    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i: i + chunk_size]
        chunk_str = " ".join(chunk_words)

        if len(chunk_words) < MIN_WORDS:   # skip tiny fragments
            continue

        estimated_page = (i // 300) + 1

        chunks.append({
            "text": chunk_str,
            "metadata": {
                "source": source,
                "doc_type": doc_type,
                "chunk_index": chunk_index,
                "page_number": estimated_page,
                "word_count": len(chunk_words),
                "tags": [doc_type, source.replace(".", "_")],
            }
        })
        chunk_index += 1

    return chunks


def chunk_pdf_pages(pages, source="unknown", chunk_size=500, overlap=100):
    all_chunks = []
    chunk_index = 0

    for page_num, page_text in pages:
        words = page_text.split()

        if len(words) < MIN_WORDS:         # skip near-empty pages
            continue

        if len(words) <= chunk_size:
            all_chunks.append({
                "text": " ".join(words),
                "metadata": {
                    "source": source,
                    "doc_type": "pdf",
                    "chunk_index": chunk_index,
                    "page_number": page_num,
                    "word_count": len(words),
                    "tags": ["pdf", source.replace(".", "_")],
                }
            })
            chunk_index += 1
            continue

        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i: i + chunk_size]
            chunk_str = " ".join(chunk_words)

            if len(chunk_words) < MIN_WORDS:   # skip trailing tiny fragments
                continue

            all_chunks.append({
                "text": chunk_str,
                "metadata": {
                    "source": source,
                    "doc_type": "pdf",
                    "chunk_index": chunk_index,
                    "page_number": page_num,
                    "word_count": len(chunk_words),
                    "tags": ["pdf", source.replace(".", "_")],
                }
            })
            chunk_index += 1

    return all_chunks