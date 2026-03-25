# RAG Architecture

## Flow

1. Load documents (PDF, TXT, CSV, DOCX)
2. Clean & extract text
3. Chunk text (500–800 tokens)
4. Generate embeddings (OpenAI)
5. Store in FAISS vector DB
6. Query → embedding → similarity search

## Components

- Loader
- Chunker
- Embedder
- Vector Store (FAISS)
- Retriever

## Notes

- Chunk overlap improves context continuity
- Smaller chunks → better retrieval
- Larger chunks → better context but less precision