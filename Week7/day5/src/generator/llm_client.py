# src/generator/llm_client.py
import os, base64, yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = "src/config/model.yaml"
with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

provider       = config["llm"]["provider"]
model_name     = config["llm"]["model_name"]
MAX_NEW_TOKENS = config["llm"].get("max_new_tokens", 300)

# ── Provider setup ──────────────────────────────────────────────────────
if provider == "local":
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    print(f"Loading LOCAL LLM: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype=torch.float32, device_map="auto")

elif provider == "groq":
    from groq import Groq
    print(f"Using Groq LLM: {model_name}")
    _groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

elif provider == "openai":
    from openai import OpenAI
    print(f"Using OpenAI LLM: {model_name}")
    _openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

elif provider == "anthropic":
    import anthropic
    print(f"Using Anthropic LLM: {model_name}")
    _anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

else:
    raise ValueError(f"Unsupported provider: {provider}")


# ── Public text interface ───────────────────────────────────────────────
def generate_answer(prompt: str) -> str:
    if provider == "local":    return _local_generate(prompt)
    if provider == "groq":     return _groq_generate(prompt)
    if provider == "openai":   return _openai_generate(prompt)
    if provider == "anthropic":return _anthropic_generate(prompt)


# ── Provider implementations ────────────────────────────────────────────
def _local_generate(prompt: str) -> str:
    import torch
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1400)
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id, repetition_penalty=1.1)
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

def _groq_generate(prompt: str) -> str:
    response = _groq_client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system",
             "content": "You are an enterprise document and image analysis assistant. "
                        "Answer strictly from the provided context. "
                        "Do not use outside knowledge."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=MAX_NEW_TOKENS, temperature=0.2)
    return response.choices[0].message.content.strip()

def _openai_generate(prompt: str) -> str:
    response = _openai_client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system",
             "content": "You are an enterprise document and image analysis assistant. "
                        "Answer strictly from the provided context."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=MAX_NEW_TOKENS, temperature=0.2)
    return response.choices[0].message.content.strip()

def _anthropic_generate(prompt: str) -> str:
    response = _anthropic_client.messages.create(
        model=model_name, max_tokens=MAX_NEW_TOKENS,
        system="You are an enterprise document and image analysis assistant. "
               "Answer strictly from the provided context.",
        messages=[{"role": "user", "content": prompt}])
    return response.content[0].text.strip()


# ── Vision interface ────────────────────────────────────────────────────
def generate_vision_answer(image_path: str, question: str) -> str:
    """
    Send an image + question to a vision-capable model and return the answer.
    Currently supported: groq (llama-4-scout vision).
    Falls back to OCR-based answer for other providers.
    """
    if provider == "groq":
        return _groq_vision(image_path, question)
    else:
        # Fallback: use CLIP retrieval + text LLM
        return _vision_fallback(image_path, question)


def _groq_vision(image_path: str, question: str) -> str:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    ext        = os.path.splitext(image_path)[1].lower().lstrip(".")
    media_type = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

    response = _groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url",
                 "image_url": {"url": f"data:{media_type};base64,{b64}"}},
                {"type": "text", "text": question}
            ]
        }],
        max_tokens=500, temperature=0.1)
    return response.choices[0].message.content.strip()


def _vision_fallback(image_path: str, question: str) -> str:
    """OCR the image and use the text LLM to answer."""
    try:
        import cv2, pytesseract
        img   = cv2.imread(image_path)
        gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text  = pytesseract.image_to_string(gray, config="--oem 3 --psm 11")
        prompt = f"Image OCR text:\n{text}\n\nQuestion: {question}\nAnswer:"
        return generate_answer(prompt)
    except Exception as e:
        return f"Vision answer unavailable for provider '{provider}': {e}"