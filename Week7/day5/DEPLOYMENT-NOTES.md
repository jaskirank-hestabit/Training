# DEPLOYMENT NOTES — Day 5 Capstone
## Advanced RAG + Memory + Evaluation

---

## 1. System Overview

This a production-ready GenAI system that combines three retrieval modes under a single Streamlit interface. It is built on top of the RAG pipeline developed across Days 1–4 and extended in Day 5 with conversational memory, self-refinement, hallucination detection, faithfulness scoring, and structured logging.

| Component | Technology |
|-----------|-----------|
| LLM Provider | Groq (llama-3.1-8b-instant) + llama-4-scout (vision) |
| Embeddings | all-MiniLM-L6-v2 (sentence-transformers) |
| Image Embeddings | CLIP (openai/clip-vit-base-patch32) |
| Vector Store | FAISS (IndexFlatIP) |
| OCR | Tesseract + OpenCV |
| Image Captioning | BLIP (Salesforce/blip-image-captioning-large) |
| Web Image Search | ddgs + Pixabay API + Unsplash API |
| SQL Database | SQLite |
| Memory Storage | Local JSON file (src/logs/chat_logs.json) |
| UI | Streamlit |

---

## 2. Folder Structure

```
src/
├── config/
│   └── model.yaml              # provider, model, chunking, retrieval settings
├── data/
│   └── raw/
│       ├── images/             # source images for image RAG
│       ├── sample.db           # SQLite factory database
│       └── (documents)         # PDFs, TXTs, MDs, DOCXs, CSVs
├── embeddings/
│   ├── clip_embedder.py        # CLIP image + text embeddings
│   └── embedder.py             # sentence-transformers text embeddings
├── evaluation/
│   └── rag_eval.py             # faithfulness scoring + hallucination detection
├── generator/
│   ├── llm_client.py           # multi-provider LLM + vision interface
│   └── sql_generator.py        # NL → SQL + result summarisation
├── logs/
│   └── chat_logs.json          # persisted conversation memory
├── memory/
│   └── memory_store.py         # turn-based memory with disk persistence
├── pipelines/
│   ├── context_builder.py      # chunk ranking + context window assembly
│   ├── image_ingest.py         # OCR + CLIP + BLIP ingestion pipeline
│   ├── ingest.py               # text document ingestion pipeline
│   ├── ingest_single.py        # single-file in-memory ingestion (upload flow)
│   ├── rag_pipeline.py         # full text RAG pipeline with memory injection
│   └── sql_pipeline.py         # SQL generation + validation + execution
├── retriever/
│   ├── hybrid_retriever.py     # BM25 + semantic + MMR hybrid retrieval
│   ├── image_search.py         # FAISS image search + web image search
│   ├── query_engine.py         # query interface for text retrieval
│   ├── reranker.py             # cosine + BM25 blended reranking
│   └── web_image_search.py     # DDG + Pixabay + Unsplash fallback chain
├── utils/
│   ├── chunker.py              # token-aware chunking with overlap
│   ├── init_db.py              # factory SQLite database initialisation
│   ├── loader.py               # multi-format file loader
│   └── schema_loader.py        # SQLite schema extraction
└── vectorstore/
    ├── faiss_store.py          # FAISS index wrapper (save/load/search)
    ├── index.faiss             # text document vector index
    ├── index_texts.pkl         # text chunks + metadata
    ├── image_index.faiss       # image vector index (CLIP 512-dim)
    └── image_index_texts.pkl   # image captions + OCR + metadata

deployment/
└── app.py                      # Streamlit UI (4 tabs)
```

---

## 3. Setup & Run Order

### 3.1 Install Dependencies

```bash
pip install streamlit faiss-cpu sentence-transformers transformers
pip install groq openai anthropic
pip install pypdf python-docx pandas rank-bm25
pip install opencv-python pytesseract pillow
pip install ddgs requests python-dotenv
```

### 3.2 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_key_here

# Optional — for web image search fallbacks
PIXABAY_API_KEY=your_pixabay_key_here
UNSPLASH_ACCESS_KEY=your_unsplash_key_here
```

### 3.3 Run Order

```bash
# Step 1 — Initialise the SQL database
python -m src.utils.init_db

# Step 2 — Ingest text documents into FAISS
python -m src.pipelines.ingest

# Step 3 — Ingest images into CLIP FAISS index
python -m src.pipelines.image_ingest

# Step 4 — Launch the Streamlit app
streamlit run deployment/app.py
```

---

## 4. Endpoints (Streamlit Tabs)

The system exposes three functional endpoints through the Streamlit UI, corresponding to the three RAG modes defined in the Day 5 exercise.

### `/ask` — Text RAG Tab

Accepts a natural language question and retrieves answers from ingested documents.

**Flow:**
```
User Query
    → HybridRetriever (BM25 + FAISS semantic + MMR)
    → Reranker (cosine 60% + BM25 40%)
    → Context Builder (relevance gate + word limit)
    → Memory Injection (last 5 turns, text RAG only)
    → LLM (Groq / OpenAI / Anthropic / Local)
    → Optional Self-Refinement Loop
    → Evaluation (faithfulness + hallucination detection)
    → Answer + Sources + Metrics
```

**Supported input formats:** PDF, TXT, MD, DOCX, CSV

**Options available:**
- Upload a file to query it directly (in-memory index, session-scoped)
- Use the pre-ingested main index
- Filter by document type
- Toggle memory injection
- Toggle self-refinement loop

---

### `/ask-image` — Image RAG Tab

Handles image-based queries with four search modes.

**Flow — Text → Image:**
```
Text Description
    → Web Search (DDG → Pixabay → Unsplash fallback chain)
    → Image grid results
```

**Flow — Image → Image (Local):**
```
Uploaded / Selected Image
    → CLIP embedding (512-dim)
    → FAISS similarity search on local index
    → Ranked image results with captions + scores
```

**Flow — Image → Image (Web):**
```
Uploaded Image
    → Vision LLM (llama-4-scout) → short search query (4–6 words)
    → Web Search (DDG → Pixabay → Unsplash)
    → Image grid results from the web
```

**Flow — Image → Text Answer:**
```
Uploaded / Selected Image + Optional Question
    → Vision LLM (llama-4-scout) base64 image call
    → Natural language answer
    → Logged to conversation memory
```

---

### `/ask-sql` — SQL RAG Tab

Converts natural language to SQL, executes it safely, and summarises the result.

**Flow:**
```
Natural Language Question
    → Schema Loader (auto-reads all tables + columns)
    → SQL Generator LLM (schema-aware prompt)
    → SQL Validator (blocks DROP / DELETE / INSERT / UPDATE / ALTER)
    → SQLite Executor
    → Result Summariser LLM
    → Table display + optional bar chart + LLM summary
```

**Database:** `src/data/raw/sample.db`
**Table:** `factory_employees` (12 records, 12 columns covering employee, department, line, production, and defect data)

---

## 5. Memory System

### Design

Memory is implemented as a sliding window of the last 5 conversation turns (10 messages — 1 user + 1 assistant per turn). It is scoped by RAG type so that Text RAG history is not injected into SQL queries and vice versa.

### Storage

- **In-session:** `st.session_state.memory` (MemoryStore instance)
- **On-disk:** `src/logs/chat_logs.json` — written after every turn, survives page refreshes and server restarts

### Log Entry Format

```json
{
  "role": "user",
  "content": "What is the efficiency of Line-C?",
  "rag_type": "sql",
  "timestamp": "2026-04-01T14:10:22.123456",
  "query": "What is the efficiency of Line-C?"
}
```

```json
{
  "role": "assistant",
  "content": "Line-C has an average efficiency of 0.947 across Q1 2024.",
  "rag_type": "sql",
  "timestamp": "2026-04-01T14:10:23.456789",
  "answer": "Line-C has an average efficiency of 0.947 across Q1 2024.",
  "sql": "SELECT AVG(efficiency) FROM factory_employees WHERE line_name = 'Line-C'"
}
```

### Prompt Injection

For Text RAG, the last 5 turns of text-type history are prepended to the LLM prompt:

```
Conversation history (use only for context resolution, not as facts):
User: What are the main operating segments?
Assistant: The document describes three operating segments...

Context:
[1] ...retrieved chunk...

Question: Can you elaborate on the second one?
```

---

## 6. Evaluation System

### Faithfulness Scoring

Measures the fraction of non-stop-word tokens in the answer that also appear in the retrieved context. Range: 0.0 to 1.0.

```
faithfulness = |answer_keywords ∩ context_keywords| / |answer_keywords|
```

### Confidence Levels

| Score | Confidence |
|-------|-----------|
| ≥ 0.60 | HIGH |
| ≥ 0.35 | MEDIUM |
| < 0.35 | LOW |

### Hallucination Detection

A response is flagged as a potential hallucination when:
- Faithfulness score is below `0.35`, AND
- The answer does not contain a disclaimer phrase (e.g. "not covered", "not found", "cannot find")

If the model correctly disclaims, the answer is marked as "No Hallucination — model stated it could not find the answer."

### Metrics Displayed in UI

| Metric | Description |
|--------|-------------|
| Faithfulness Score | Word-overlap ratio (0.0 – 1.0) |
| Confidence | HIGH / MEDIUM / LOW |
| Avg Source Score | Mean rerank score of retrieved chunks |
| Hallucination Banner | ✅ Clean / ℹ️ Disclaimed / 🚨 Detected |

---

## 7. Self-Refinement Loop

When enabled in Advanced Options, after the initial answer is generated a second LLM call is made:

```
Review this answer for accuracy against the context.

Context (excerpt): {first 600 chars of context}
Original Answer: {initial answer}

Refined Answer (improve only if genuinely needed; stay faithful to context):
```

The refined answer replaces the original only if it is longer than 20 characters. A label `✨ Self-refinement loop applied` is shown in the UI when this occurs.

---

## 8. Retrieval Architecture

### Hybrid Retrieval (Text RAG)

```
Query
  ├── Semantic Search   → FAISS (all-MiniLM-L6-v2, 384-dim, IndexFlatIP)
  └── Keyword Search    → BM25Okapi

Combined results
  → Metadata Filter (optional: doc_type, source, page)
  → Reranker (60% cosine + 40% normalised BM25)
  → Deduplication
  → MMR (Max Marginal Relevance, λ=0.5)
  → Top-K results
```

### Relevance Gate

If the top-ranked chunk scores below `min_rerank_score: 0.35` (set in `model.yaml`), the LLM is not called and the system returns: *"This topic is not covered in the provided documents."*

### Image Retrieval

Local index uses CLIP 512-dimensional embeddings with FAISS IndexFlatIP (inner product = cosine similarity for normalised vectors). Web search uses a 3-backend fallback chain with automatic retry and exponential backoff.

---

## 9. Configuration Reference

All tuneable parameters live in `src/config/model.yaml`:

```yaml
embedding:
  model_name: all-MiniLM-L6-v2
  device: cpu

llm:
  provider: groq                     # groq | openai | anthropic | local
  model_name: llama-3.1-8b-instant
  max_new_tokens: 300

chunking:
  chunk_size: 500                    # words per chunk
  overlap: 100                       # word overlap between chunks

limits:
  max_file_size_chars: 400000
  max_chunks_per_file: 200
  max_total_chunks: 1000

retrieval:
  top_k: 5
  min_rerank_score: 0.35

sql:
  db_path: src/data/raw/sample.db
```

To switch LLM provider, change `provider` and set the corresponding API key in `.env`. No other code changes are needed — the pipeline is provider-agnostic.