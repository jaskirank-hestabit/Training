import json
import logging
import time
import uuid
from typing import AsyncGenerator, List, Optional

import config
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from model_loader import get_model
from pydantic import BaseModel, Field

# Logging 
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("llm_api")

# App 
app = FastAPI(
    title="Local LLM API",
    description="Production-ready inference server for GGUF models",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Schemas 
class GenerateRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = "You are a helpful assistant."
    max_tokens: int = Field(config.DEFAULT_MAX_TOKENS, ge=1, le=4096)
    temperature: float = Field(config.DEFAULT_TEMPERATURE, ge=0.0, le=2.0)
    top_p: float = Field(config.DEFAULT_TOP_P, ge=0.0, le=1.0)
    top_k: int = Field(config.DEFAULT_TOP_K, ge=1, le=200)
    repeat_penalty: float = Field(config.DEFAULT_REPEAT_PENALTY, ge=1.0, le=2.0)
    stream: bool = False


class Message(BaseModel):
    role: str       # "system" | "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    max_tokens: int = Field(config.DEFAULT_MAX_TOKENS, ge=1, le=4096)
    temperature: float = Field(config.DEFAULT_TEMPERATURE, ge=0.0, le=2.0)
    top_p: float = Field(config.DEFAULT_TOP_P, ge=0.0, le=1.0)
    top_k: int = Field(config.DEFAULT_TOP_K, ge=1, le=200)
    repeat_penalty: float = Field(config.DEFAULT_REPEAT_PENALTY, ge=1.0, le=2.0)
    stream: bool = False


# Middleware: request-id + timing 
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = round(time.perf_counter() - start, 3)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(elapsed)
    logger.info(f"[{request_id}] {request.method} {request.url.path} → {response.status_code} ({elapsed}s)")
    return response


# Health 
@app.get("/health")
def health():
    return {"status": "ok", "model_path": config.MODEL_PATH}


# /generate 
@app.post("/generate")
async def generate(req: GenerateRequest, request: Request):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
    model = get_model()

    # Build a simple prompt with optional system context
    full_prompt = (
        f"<|system|>\n{req.system_prompt}\n"
        f"<|user|>\n{req.prompt}\n"
        f"<|assistant|>\n"
    )

    common_kwargs = dict(
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        top_k=req.top_k,
        repeat_penalty=req.repeat_penalty,
        stop=["<|user|>", "<|system|>", "</s>"],
    )

    if req.stream:
        async def token_stream() -> AsyncGenerator[str, None]:
            output_tokens = 0
            for chunk in model(full_prompt, stream=True, **common_kwargs):
                token = chunk["choices"][0]["text"]
                output_tokens += 1
                payload = json.dumps({"token": token, "request_id": request_id})
                yield f"data: {payload}\n\n"
            yield f"data: {json.dumps({'done': True, 'tokens_generated': output_tokens, 'request_id': request_id})}\n\n"

        return StreamingResponse(token_stream(), media_type="text/event-stream")

    # Non-streaming
    t0 = time.perf_counter()
    output = model(full_prompt, **common_kwargs)
    elapsed = round(time.perf_counter() - t0, 3)
    text = output["choices"][0]["text"].strip()
    tokens_used = output["usage"]["completion_tokens"]

    logger.info(f"[{request_id}] /generate → {tokens_used} tokens in {elapsed}s")
    return {
        "request_id": request_id,
        "response": text,
        "tokens_generated": tokens_used,
        "elapsed_sec": elapsed,
    }


# /chat 
@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
    model = get_model()

    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    common_kwargs = dict(
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        top_k=req.top_k,
        repeat_penalty=req.repeat_penalty,
    )

    if req.stream:
        async def chat_stream() -> AsyncGenerator[str, None]:
            output_tokens = 0
            for chunk in model.create_chat_completion(messages=messages, stream=True, **common_kwargs):
                delta = chunk["choices"][0].get("delta", {})
                token = delta.get("content", "")
                if token:
                    output_tokens += 1
                    payload = json.dumps({"token": token, "request_id": request_id})
                    yield f"data: {payload}\n\n"
            yield f"data: {json.dumps({'done': True, 'tokens_generated': output_tokens, 'request_id': request_id})}\n\n"

        return StreamingResponse(chat_stream(), media_type="text/event-stream")

    t0 = time.perf_counter()
    output = model.create_chat_completion(messages=messages, **common_kwargs)
    elapsed = round(time.perf_counter() - t0, 3)
    reply = output["choices"][0]["message"]["content"].strip()
    tokens_used = output["usage"]["completion_tokens"]

    logger.info(f"[{request_id}] /chat ({len(messages)} msgs) → {tokens_used} tokens in {elapsed}s")
    return {
        "request_id": request_id,
        "response": reply,
        "tokens_generated": tokens_used,
        "elapsed_sec": elapsed,
        "total_messages": len(messages),
    }


# Run 
if __name__ == "__main__":
    logger.info(f" Starting LLM API on {config.API_HOST}:{config.API_PORT}")
    get_model()   # pre-load model on startup
    uvicorn.run(
        "app:app",
        host=config.API_HOST,
        port=config.API_PORT,
        log_level=config.LOG_LEVEL.lower(),
        reload=False,
    )