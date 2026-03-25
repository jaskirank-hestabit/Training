import os
from tqdm import tqdm

from src.utils.loader import load_file
from src.utils.chunker import chunk_text
from src.embeddings.embedder import get_embeddings
from src.vectorstore.faiss_store import FAISSStore

DATA_PATH = "src/data/raw"

# SAFETY LIMITS
MAX_FILE_SIZE_CHARS = 400_000      # skip very large files
MAX_CHUNKS_PER_FILE = 50           # limit chunks per file
MAX_TOTAL_CHUNKS = 200             # global cap


# Recursively get all files
def get_all_files(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths


def run_ingestion():
    all_chunks = []

    files = get_all_files(DATA_PATH)

    if len(files) == 0:
        print("No files found in data/raw/")
        return

    print(f"Found {len(files)} files\n")

    # Load + Chunk
    for path in files:
        print(f"Processing: {path}")

        text = load_file(path)

        if not text or not text.strip():
            print("Skipping empty file\n")
            continue

        # Skip large files
        if len(text) > MAX_FILE_SIZE_CHARS:
            print(f"Skipping large file ({len(text)} chars)\n")
            continue

        print(f"Text length: {len(text)}")

        chunks = chunk_text(text)

        # Limit chunks per file
        if len(chunks) > MAX_CHUNKS_PER_FILE:
            print(f"Limiting chunks from {len(chunks)} → {MAX_CHUNKS_PER_FILE}")
            chunks = chunks[:MAX_CHUNKS_PER_FILE]

        print(f"Chunks used: {len(chunks)}\n")

        all_chunks.extend(chunks)

        # Global chunk limit
        if len(all_chunks) >= MAX_TOTAL_CHUNKS:
            print(f"Reached max total chunks ({MAX_TOTAL_CHUNKS})")
            break

    print(f"\n Total chunks: {len(all_chunks)}\n")

    if len(all_chunks) == 0:
        print("No chunks created. Check your data.")
        return

    # Generate embeddings
    embeddings = []
    batch_size = 20

    print(" Generating embeddings...\n")

    for i in tqdm(range(0, len(all_chunks), batch_size)):
        batch = all_chunks[i:i + batch_size]

        emb = get_embeddings(batch)

        if not emb:
            print("Empty embedding batch, skipping")
            continue

        embeddings.extend(emb)

    if len(embeddings) == 0:
        print("No embeddings generated.")
        return

    # Create FAISS index
    dim = len(embeddings[0])
    store = FAISSStore(dim)

    store.add(embeddings, all_chunks)

    os.makedirs("src/vectorstore", exist_ok=True)
    store.save("src/vectorstore/index.faiss")

    print("\n Ingestion complete!")
    print(f" Stored {len(all_chunks)} chunks in FAISS")


if __name__ == "__main__":
    run_ingestion()