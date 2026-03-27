# local llm client 
# import yaml
# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch

# CONFIG_PATH = "src/config/model.yaml"

# with open(CONFIG_PATH) as f:
#     config = yaml.safe_load(f)

# provider   = config["llm"]["provider"]
# model_name = config["llm"]["model_name"]
# MAX_NEW_TOKENS = config["llm"].get("max_new_tokens", 80)

# if provider == "local":
#     print(f"Loading LOCAL LLM: {model_name}")

#     tokenizer = AutoTokenizer.from_pretrained(model_name)

#     model = AutoModelForCausalLM.from_pretrained(
#         model_name,
#         dtype=torch.float32,
#         device_map="auto"
#     )


# def generate_answer(prompt):
#     if provider == "local":
#         return _local_generate(prompt)
#     else:
#         raise ValueError(f"Unsupported provider: {provider}")


# def _local_generate(prompt):
#     inputs = tokenizer(
#         prompt,
#         return_tensors="pt",
#         truncation=True,
#         max_length=1400     # leave headroom for new tokens
#     )

#     with torch.no_grad():
#         outputs = model.generate(
#             **inputs,
#             max_new_tokens=MAX_NEW_TOKENS,
#             do_sample=False,               # greedy - faster + more deterministic
#             pad_token_id=tokenizer.eos_token_id,
#             eos_token_id=tokenizer.eos_token_id,
#             repetition_penalty=1.1,        # reduces looping
#         )

#     # decode only the newly generated tokens (skip the prompt)
#     new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
#     return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()





# groq llm 
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = "src/config/model.yaml"

with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

provider       = config["llm"]["provider"]
model_name     = config["llm"]["model_name"]
MAX_NEW_TOKENS = config["llm"].get("max_new_tokens", 300)

# ---------- Provider setup ----------

if provider == "local":
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    print(f"Loading LOCAL LLM: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.float32,
        device_map="auto"
    )

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


# ---------- Public interface ----------

def generate_answer(prompt: str) -> str:
    if provider == "local":
        return _local_generate(prompt)
    elif provider == "groq":
        return _groq_generate(prompt)
    elif provider == "openai":
        return _openai_generate(prompt)
    elif provider == "anthropic":
        return _anthropic_generate(prompt)


# ---------- Provider implementations ----------

def _local_generate(prompt: str) -> str:
    import torch
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1400
    )
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1,
        )
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def _groq_generate(prompt: str) -> str:
    response = _groq_client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are an enterprise document and image analysis assistant. "
                           "Answer strictly from the provided context. "
                           "Do not use outside knowledge."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=MAX_NEW_TOKENS,
        temperature=0.2,       # low = more factual, less creative
    )
    return response.choices[0].message.content.strip()


def _openai_generate(prompt: str) -> str:
    response = _openai_client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are an enterprise document and image analysis assistant. "
                           "Answer strictly from the provided context."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=MAX_NEW_TOKENS,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def _anthropic_generate(prompt: str) -> str:
    response = _anthropic_client.messages.create(
        model=model_name,
        max_tokens=MAX_NEW_TOKENS,
        system="You are an enterprise document and image analysis assistant. "
               "Answer strictly from the provided context.",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()