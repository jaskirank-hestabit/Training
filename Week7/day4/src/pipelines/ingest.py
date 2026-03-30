import os
import yaml
from tqdm import tqdm

from src.utils.loader import load_file
from src.utils.chunker import chunk_text, chunk_pdf_pages
from src.embeddings.embedder import get_embeddings
from src.vectorstore.faiss_store import FAISSStore

DATA_PATH = "src/data/raw"
CONFIG_PATH = "src/config/model.yaml"

with open(CONFIG_PATH) as f:
    _cfg = yaml.safe_load(f)

_limits = _cfg.get("limits", {})
MAX_FILE_SIZE_CHARS = _limits.get("max_file_size_chars", 400_000)
MAX_CHUNKS_PER_FILE = _limits.get("max_chunks_per_file", 50)
MAX_TOTAL_CHUNKS    = _limits.get("max_total_chunks", 500)

_chunk_cfg = _cfg.get("chunking", {})
CHUNK_SIZE = _chunk_cfg.get("chunk_size", 500)
OVERLAP    = _chunk_cfg.get("overlap", 100)

SUPPORTED = {".txt", ".md", ".pdf", ".docx", ".csv"}


def get_doc_type(path):
    ext = os.path.splitext(path)[1].lower()
    return {".txt": "txt", ".md": "md", ".pdf": "pdf",
            ".docx": "docx", ".csv": "csv"}.get(ext, "unknown")


def get_all_files(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in SUPPORTED:
                file_paths.append(os.path.join(root, file))
    return file_paths


def run_ingestion():
    all_chunks = []
    files = get_all_files(DATA_PATH)

    if not files:
        print("No files found in src/data/raw/")
        return

    print(f"Found {len(files)} files\n")

    for path in files:
        print(f"Processing: {path}")

        content = load_file(path)
        source   = os.path.basename(path)
        doc_type = get_doc_type(path)

        # PDF: load_file returns [(page_num, text), ...]
        if doc_type == "pdf":
            if not content:                      # empty list = unreadable PDF
                print("  Skipping empty PDF\n")
                continue

            total_chars = sum(len(t) for _, t in content)
            print(f"  Pages: {len(content)} | Total chars: {total_chars:,}")

            if total_chars > MAX_FILE_SIZE_CHARS:
                print(f"  Skipping — too large\n")
                continue

            # chunk_pdf_pages uses REAL page numbers from each tuple
            chunks = chunk_pdf_pages(content, source=source,
                                     chunk_size=CHUNK_SIZE, overlap=OVERLAP)

        # Everything else: load_file returns a plain string
        else:
            if not content or not content.strip():
                print("  Skipping empty file\n")
                continue

            if len(content) > MAX_FILE_SIZE_CHARS:
                print(f"  Skipping — too large\n")
                continue

            print(f"  Text length: {len(content):,} chars")

            # chunk_text estimates page numbers - fine for non-PDF
            chunks = chunk_text(content, source=source, doc_type=doc_type,
                                chunk_size=CHUNK_SIZE, overlap=OVERLAP)

        if len(chunks) > MAX_CHUNKS_PER_FILE:
            print(f"  Limiting: {len(chunks)} → {MAX_CHUNKS_PER_FILE} chunks")
            chunks = chunks[:MAX_CHUNKS_PER_FILE]

        print(f"  Chunks: {len(chunks)}\n")
        all_chunks.extend(chunks)

        if len(all_chunks) >= MAX_TOTAL_CHUNKS:
            print(f"Reached global limit ({MAX_TOTAL_CHUNKS}), stopping.")
            break

    print(f"Total chunks: {len(all_chunks)}\n")

    if not all_chunks:
        print("No chunks created.")
        return

    # Embed
    print("Generating embeddings (local)...\n")
    embeddings = []
    texts = [c["text"] for c in all_chunks]

    for i in tqdm(range(0, len(texts), 20)):
        emb = get_embeddings(texts[i: i + 20])
        if emb:
            embeddings.extend(emb)

    if not embeddings:
        print("No embeddings generated.")
        return

    # Save
    dim = len(embeddings[0])
    store = FAISSStore(dim)
    store.add(embeddings, all_chunks)
    store.save("src/vectorstore/index.faiss")

    print(f"\nIngestion complete! Stored {len(all_chunks)} chunks.")

    # Verify: print a sample PDF chunk to confirm page numbers
    pdf_samples = [c for c in all_chunks if c["metadata"]["doc_type"] == "pdf"]
    if pdf_samples:
        s = pdf_samples[0]
        print(f"\nSample PDF chunk — page number should be real now:")
        print(f"  Page   : {s['metadata']['page_number']}")
        print(f"  Source : {s['metadata']['source']}")
        print(f"  Text   : {s['text'][:120]}...")


if __name__ == "__main__":
    run_ingestion()
