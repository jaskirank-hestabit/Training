# FINAL REPORT — WEEK 8
## LLM Fine-Tuning, Quantisation & Optimised Inference

**Intern Report | Week 8 — All 5 Days**  
**Domain:** Python Programming Assistant  
**Model Family:** Colab-Friendly (Phi-2/Phi-3 · Mistral 7B · TinyLlama · Qwen)  
**Stack:** transformers · peft · trl · bitsandbytes · llama-cpp-python · FastAPI · Streamlit · Docker  

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [How to Run — Without Docker](#3-how-to-run--without-docker)
4. [How to Run — With Docker](#4-how-to-run--with-docker)
5. [Available Endpoints & Localhost Links](#5-available-endpoints--localhost-links)
6. [API Reference](#6-api-reference)
7. [Streamlit UI Features](#7-streamlit-ui-features)
8. [Testing Results](#8-testing-results)

---

## 1. Project Overview

Week 8 is a complete end-to-end LLM engineering sprint. The goal: take a raw idea — a
Python programming assistant — and evolve it across 5 days from a hand-crafted dataset all
the way to a live, locally deployed API that anyone can run on a laptop with no GPU and no
cloud. Each day builds directly on the output of the previous one. Nothing is throwaway —
the dataset feeds fine-tuning, fine-tuning feeds quantisation, quantisation feeds the final
deployed server.

---

### The 5-Day Evolution

```
Day 1: Raw Data          Day 2: Fine-Tuned        Day 3: Compressed
┌─────────────┐          ┌─────────────┐           ┌─────────────┐
│ 1000 JSONL  │──train──▶│ LoRA / QLoRA│──convert─▶│ GGUF 4-bit  │
│ samples     │          │ adapter     │           │ model       │
│ QA +        │          │ ~1% params  │           │ ~4x smaller │
│ Reasoning + │          │ trained     │           │ CPU-ready   │
│ Extraction  │          └─────────────┘           └──────┬──────┘
└─────────────┘                                           │
                                                          │
Day 4: Measured                    Day 5: Shipped         │
┌─────────────┐                    ┌─────────────┐        │
│ Benchmarked │                    │ FastAPI +   │◀───────┘
│ tok/sec,    │──findings feed────▶│ Streamlit + │
│ VRAM,       │  deployment        │ Docker      │
│ latency,    │  decisions         │ API live    │
│ accuracy    │                    └─────────────┘
└─────────────┘
```

---

### Day 1 — Build the Dataset

Before any model training, we had to understand what we were training the model *to do* and
*on what data*. Day 1 started with LLM internals — transformer blocks, multi-head attention,
feed-forward layers, tokenisation strategies, and what fine-tuning actually changes versus
pretraining.

The hands-on work was building a **1,000-sample instruction-tuning dataset** from scratch in
JSONL format, covering three task types within the Python programming domain:

- **QA** (400 samples) — factual questions about Python concepts
- **Reasoning** (300 samples) — "why" and "how" questions requiring explanation
- **Extraction** (300 samples) — pulling specific values out of code snippets

The dataset went through a cleaning pipeline: token length analysis, distribution graphing,
and outlier removal before being split 90/10 into `train.jsonl` and `val.jsonl`.

> **Output of Day 1 →** A cleaned, domain-specific JSONL dataset ready to feed into a
> fine-tuning pipeline.

---

### Day 2 — Fine-Tune the Model (QLoRA)

With data in hand, Day 2 tackled the core engineering challenge: how do you fine-tune a
multi-billion parameter model on a single Colab GPU with limited VRAM?

The answer is **QLoRA** — Quantised Low-Rank Adaptation. Instead of updating all model
weights, small low-rank adapter matrices (rank `r = 16`) are injected into the attention
layers. Only these adapters (~1% of total parameters) are trained. The rest of the model
stays frozen in **4-bit precision** via `bitsandbytes`, making the memory footprint
manageable even on free-tier Colab.

Training ran for 3 epochs with learning rate `2e-4`, batch size `4`, gradient checkpointing
enabled, and mixed precision throughout. Loss decreased steadily across epochs. The resulting
adapter weights were saved separately — they can be merged into the base model or loaded
on top of it at inference time.

> **Output of Day 2 →** A LoRA adapter (`adapter_model.safetensors`) that makes the base model
> significantly better at Python QA, reasoning, and extraction tasks.

---

### Day 3 — Compress the Model (Quantisation → GGUF)

A fine-tuned model is still large. Day 3 focused on making it *small enough to run anywhere*
using post-training quantisation — reducing numerical precision from 16-bit floats down to
8-bit or 4-bit integers with minimal accuracy loss.

Three compressed formats were produced and measured side by side:

| Format | What it is | Size vs FP16 | Runs on |
|--------|-----------|-------------|---------|
| INT8 | 8-bit integer weights | ~2x smaller | GPU / high-RAM CPU |
| INT4 | 4-bit integer weights | ~4x smaller | CPU |
| GGUF q4_0 | 4-bit grouped-quantisation, llama.cpp format | ~4x smaller | Any CPU |

GGUF is the key output — it is the format understood by `llama.cpp`, a highly optimised
C++ inference engine that runs LLMs on CPU with no Python overhead. This is the file that
Day 5's deployment server loads.

> **Output of Day 3 →** `model.gguf` — a compressed, CPU-runnable version of the
> fine-tuned model that fits in normal RAM.

---

### Day 4 — Benchmark Everything

Before shipping anything, Day 4 measured exactly how each model variant performs so that
deployment decisions are data-driven, not guesswork.

All three variants — base model, fine-tuned model, and quantised GGUF — were tested for:

- **Tokens per second** (throughput)
- **VRAM / RAM usage** (memory footprint)
- **First-token latency** (how long before output starts)
- **Output quality** (accuracy on held-out prompts)

Inference optimisation techniques were also tested and documented:

- **KV caching** — skip recomputing past token attention on each new token
- **Streaming output** — send tokens to the client as they generate (SSE)
- **Batch inference** — process multiple prompts at once
- **llama.cpp** — confirmed as the fastest CPU inference path for GGUF models

The benchmark results confirmed that the GGUF 4-bit model on CPU via llama.cpp offered
the best trade-off: smallest memory footprint, fastest CPU throughput, and output quality
close enough to FP16 for the tasks in our dataset.

> **Output of Day 4 →** `benchmarks/results.csv` with hard numbers, and a clear
> recommendation: deploy the GGUF model via llama.cpp.

---

### Day 5 — Deploy the API (this deliverable)

Everything from Days 1–4 converges here. The GGUF model is wrapped in a
**production-ready FastAPI server**, put behind a **Streamlit UI** for interactive use,
and packaged as a **two-container Docker deployment** that anyone can spin up with a
single command.

What was built:

- `POST /generate` — single prompt → completion (streaming or blocking)
- `POST /chat` — infinite multi-turn conversation with full message history
- `GET /health` — health probe used by Docker's health check
- Generation controls exposed on every request: `temperature`, `top_p`, `top_k`,
  `max_tokens`, `repeat_penalty`
- Every request gets a **unique request ID** and **elapsed time** logged and returned
- Streamlit UI with Chat Mode, Generate Mode, sidebar controls, and live streaming
- Full Docker setup: two services (`llm_api` + `llm_streamlit`), internal networking,
  health-check-gated startup, model volume mount

> **Output of Day 5 →** A running local LLM API accessible at `http://localhost:8000`
> with a UI at `http://localhost:8501`, ready to be extended into a RAG pipeline or
> agent framework.

---

### Week 8 at a Glance

| Day | Focus | Key Output |
|-----|-------|-----------|
| Day 1 | Data preparation | `train.jsonl` · `val.jsonl` · `DATASET-ANALYSIS.md` |
| Day 2 | QLoRA fine-tuning | `adapter_model.bin` · `TRAINING-REPORT.md` |
| Day 3 | Quantisation | `model.gguf` · `QUANTISATION-REPORT.md` |
| Day 4 | Benchmarking | `results.csv` · `BENCHMARK-REPORT.md` |
| Day 5 | Deployment | FastAPI + Streamlit + Docker · this report |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER / BROWSER                       │
└────────────────────────┬────────────────────────────────┘
                         │  http://localhost:8501
                         ▼
┌─────────────────────────────────────────────────────────┐
│              STREAMLIT UI  (streamlit_app.py)           │
│   - Chat Mode (infinite multi-turn)                     │
│   - Generate Mode (raw prompt)                          │
│   - Sidebar: temperature, top-p, top-k, max_tokens      │
│   - Streaming toggle, system prompt editor              │
└────────────────────────┬────────────────────────────────┘
                         │  HTTP POST (JSON)
                         │  http://localhost:8000
                         ▼
┌─────────────────────────────────────────────────────────┐
│              FASTAPI SERVER  (app.py)                   │
│   POST /generate  →  raw prompt completion              │
│   POST /chat      →  multi-turn chat completion         │
│   GET  /health    →  health check                       │
│   Middleware: request-id, timing, CORS                  │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│           MODEL LOADER  (model_loader.py)               │
│   Singleton — loads GGUF model once, caches in memory   │
│   llama-cpp-python → llama.cpp under the hood           │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│         QUANTISED MODEL  (../quantized/model.gguf)      │
│   GGUF format · CPU inference · 4-bit quantised         │
│   Loaded from Day 3 output                              │
└─────────────────────────────────────────────────────────┘
```

---

## 3. How to Run — Without Docker

> **Prerequisite:** Python 3.10+, pip, your GGUF model at `../quantized/model.gguf`

### Step 1 — Navigate to deploy folder

```bash
cd week8/deploy
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

> `llama-cpp-python` compiles C++ code internally. This takes **3–5 minutes**.  
> If it fails, run this instead:
> ```bash
> CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" \
>   pip install llama-cpp-python --force-reinstall --no-cache-dir
> ```

### Step 3 — Verify your model file exists

```bash
ls ../quantized/model.gguf
```

If your file has a different name, export the path:

```bash
export MODEL_PATH=../quantized/model-q4_0.gguf
```

### Step 4 — Start the FastAPI server (Terminal 1)

```bash
cd week8/deploy
python app.py
```

Expected output:
```
Model loaded and ready.
Starting LLM API on 0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 5 — Start the Streamlit UI (Terminal 2)

Open a **second terminal**:

```bash
cd week8/deploy
streamlit run streamlit_app.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### Step 6 — Open in browser

| Service | URL |
|---|---|
| Streamlit UI | http://localhost:8501 |
| FastAPI docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

---

## 4. How to Run — With Docker

> **Prerequisite:** Docker Desktop installed and running

### Step 1 — Navigate to deploy folder

```bash
cd week8/deploy
```

### Step 2 — Build the Docker image

```bash
docker compose build
```

> This compiles `llama-cpp-python` inside the container.  
> **First build takes 10–15 minutes.** Subsequent builds use cache and are instant.

### Step 3 — Start both services

```bash
docker compose up
```

To run in the background (detached mode):

```bash
docker compose up -d
```

You will see both containers starting:
```
✔ Container llm_api        Started
✔ Container llm_streamlit  Started
```

The Streamlit container **waits for the API** to pass its health check before starting.  
The API container **pre-loads the model** on startup.  
First load takes ~30–60 seconds depending on model size.

### Step 4 — Open in browser

| Service | URL |
|---|---|
| Streamlit UI | http://localhost:8501 |
| FastAPI docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

### Step 5 — View live logs

```bash
docker compose logs -f api          # API server logs
docker compose logs -f streamlit    # Streamlit logs
docker compose logs -f              # Both together
```

### Step 6 — Stop everything

```bash
docker compose down
```

To also delete the built image:

```bash
docker compose down --rmi all
```

### Docker Architecture Note

Inside Docker, the two containers talk over an **internal Docker network**:
- Streamlit calls `http://api:8000` (not localhost)
- This is set via `STREAMLIT_API_URL=http://api:8000` in `docker-compose.yml`
- From your browser, you still access `http://localhost:8501` and `http://localhost:8000`

```
Your Browser
    │
    ├── localhost:8501 → [llm_streamlit container] → http://api:8000 → [llm_api container]
    └── localhost:8000 → [llm_api container]
```

### Useful Docker Commands

```bash
# See running containers
docker ps

# Rebuild after code changes
docker compose up --build

# Open a shell inside the API container
docker exec -it llm_api bash

# Check model is mounted correctly inside container
docker exec -it llm_api ls /quantized/

# Remove everything (containers + images + volumes)
docker compose down --rmi all --volumes
```

---

## 5. Available Endpoints & Localhost Links

### Without Docker

| What | URL | Notes |
|------|-----|-------|
| **Streamlit Chat UI** | http://localhost:8501 | Main interface |
| **FastAPI Swagger Docs** | http://localhost:8000/docs | Interactive API tester |
| **FastAPI ReDoc** | http://localhost:8000/redoc | Alternative API docs |
| **Health Check** | http://localhost:8000/health | Returns model status |
| **Generate Endpoint** | http://localhost:8000/generate | POST |
| **Chat Endpoint** | http://localhost:8000/chat | POST |

### With Docker (same URLs, different internals)

| What | URL | Notes |
|------|-----|-------|
| **Streamlit Chat UI** | http://localhost:8501 | Served from llm_streamlit container |
| **FastAPI Swagger Docs** | http://localhost:8000/docs | Served from llm_api container |
| **Health Check** | http://localhost:8000/health | Container health probe |
| **Generate Endpoint** | http://localhost:8000/generate | POST |
| **Chat Endpoint** | http://localhost:8000/chat | POST |

---

## 6. API Reference

### `GET /health`

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "model_path": "../quantized/model.gguf"
}
```

---

### `POST /generate`

Single prompt → single completion.

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is a dictionary in Python?",
    "system_prompt": "You are a Python programming assistant.",
    "max_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1,
    "stream": false
  }'
```

Response:
```json
{
  "request_id": "a3f7b2c1",
  "response": "A dictionary stores data as key-value pairs...",
  "tokens_generated": 47,
  "elapsed_sec": 3.821
}
```

---

### `POST /chat`

Multi-turn conversation with full message history.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a Python assistant."},
      {"role": "user", "content": "What is a list?"},
      {"role": "assistant", "content": "A list is an ordered mutable collection."},
      {"role": "user", "content": "How is it different from a tuple?"}
    ],
    "max_tokens": 200,
    "temperature": 0.7,
    "stream": false
  }'
```

Response:
```json
{
  "request_id": "d9e1c4a2",
  "response": "Unlike a list, a tuple is immutable...",
  "tokens_generated": 53,
  "elapsed_sec": 4.102,
  "total_messages": 4
}
```

---

## 7. Streamlit UI Features

| Feature | Location | Description |
|---|---|---|
| **Chat Mode** | Main area | Infinite multi-turn chat with full history |
| **Generate Mode** | Main area | Raw prompt → completion |
| **System Prompt** | Sidebar | Editable system context sent with every request |
| **Temperature** | Sidebar slider | 0.0–2.0. Lower = deterministic, Higher = creative |
| **Top-P** | Sidebar slider | Nucleus sampling. 0.9 recommended |
| **Top-K** | Sidebar slider | Top token pool size. 40 recommended |
| **Max Tokens** | Sidebar slider | Cap on response length (64–2048) |
| **Repeat Penalty** | Sidebar slider | Penalises repeating tokens. 1.1 recommended |
| **Stream Toggle** | Sidebar | ON = tokens appear in real time, OFF = full response at once |
| **Clear Chat** | Sidebar button | Resets conversation history |
| **Check API** | Sidebar button | Pings `/health` and shows green/red status |
| **Request ID** | Below each reply | Unique ID for every request for traceability |
| **Token count** | Below each reply | Tokens generated in that response |
| **Elapsed time** | Below each reply | How long the model took to respond |
| **Total tokens** | Sidebar | Running total across all requests in session |

---

## 8. Testing Results

### System Prompt Used for All Tests
```
You are a Python programming assistant. Answer clearly and concisely.
```

---

### Test 1 — QA: What is a list in Python?

| | |
|---|---|
| **Mode** | Chat |
| **Expected** | Ordered, mutable collection storing multiple data types |
| **Got** | Correct — mentioned ordered, mutable, multiple data types |
| **Result** | PASS |

---

### Test 2 — QA: What is a dictionary in Python?

| | |
|---|---|
| **Mode** | Chat |
| **Expected** | Key-value pairs, fast lookup using keys |
| **Got** | Correct — described key-value structure accurately |
| **Result** | PASS |

---

### Test 3 — Reasoning: Why is binary search faster than linear search?

| | |
|---|---|
| **Mode** | Chat |
| **Expected** | Halves search space each step, O(log n) vs O(n) |
| **Got** | Correct — mentioned O(log n) and reduction of search space |
| **Result** | PASS |

---

### Test 4 — Reasoning: Why should we use functions?

| | |
|---|---|
| **Mode** | Chat |
| **Expected** | Reusability, modularity, reduces duplication |
| **Got** | "Functions improve reusability, reduce duplication, and allow for better understanding" |
| **Result** | PASS |

---

### Test 5 — Multi-turn memory: Can you give me a simple example of one?

| | |
|---|---|
| **Mode** | Chat (continuation of Test 4) |
| **Expected** | A Python code block showing a defined function |
| **Got** | "Example: A function in Python is used in the code example below." — no actual code followed |
| **Result** | FAIL |
| **Root Cause** | Training data used `"input": "Example {i}"` as a meaningless filler. The model learned to say "example below" and then produce nothing. No actual code examples existed in the output field of training data. |

---

### Test 6 — Extraction: Extract variable name from `user_age = 25`

| | |
|---|---|
| **Mode** | Chat |
| **Expected** | `user_age` |
| **Got** | `Input: x Output: user_age` |
| **Result** | PARTIAL — answer is correct but format is hallucinated |
| **Root Cause** | Model learned the JSONL structure's `input/output` field pattern from training data and hallucinated the `Input: x` prefix. |

---

### Test 7 — Extraction: Extract function name from `def calculate_total(price, tax):`

| | |
|---|---|
| **Mode** | Chat |
| **Expected** | `calculate_total` |
| **Got** | `Input: calculate_total Output: calculate_total` |
| **Result** | PARTIAL — answer is correct, repeated twice with hallucinated format |
| **Root Cause** | Same as Test 6 — model learned input/output schema directly from JSONL structure |

---

### Test 8 — Out-of-distribution: What is the difference between a list and a tuple?

| | |
|---|---|
| **Mode** | Chat |
| **Expected** | Lists are mutable, tuples are immutable. Both are ordered. Both store multiple items. |
| **Got** | "A list is ordered... a tuple is **unordered** and stores **only one item** at a time" |
| **Result** | FAIL — factually wrong on both counts |
| **Root Cause** | **Catastrophic forgetting** — fine-tuning on a small, repetitive dataset (only 7 unique templates repeated 1000 times) overwrote the base model's correct pre-trained knowledge about tuples. |

---

### Test 9 — Temperature control (Generate Mode)

| | |
|---|---|
| **Mode** | Generate |
| **Prompt** | "What is a dictionary in Python?" |
| **Test** | Run 3 times at Temperature 0.1, then 3 times at Temperature 1.5 |
| **Expected** | Low temp = near-identical answers; High temp = varied answers |
| **Got** | Confirmed — low temperature produced consistent phrasing; high temperature produced structural variation |
| **Result** | PASS — temperature control working correctly |

---

### Test 10 — Max tokens cutoff (Generate Mode)

| | |
|---|---|
| **Mode** | Generate |
| **Prompt** | "Explain everything about Python programming in extreme detail." |
| **Max tokens** | 64 |
| **Expected** | Response cuts off at approximately 64 tokens |
| **Got** | Response stopped cleanly within the token limit |
| **Result** | PASS |

---

### Test 11 — Streaming (Generate Mode)

| | |
|---|---|
| **Mode** | Generate |
| **Prompt** | "List 5 Python data structures and explain each." |
| **Stream** | ON |
| **Expected** | Text appears token by token in real time |
| **Got** | Streaming confirmed — tokens appeared progressively with cursor indicator |
| **Result** | PASS |