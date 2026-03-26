import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

CONFIG_PATH = "src/config/model.yaml"

with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

provider   = config["llm"]["provider"]
model_name = config["llm"]["model_name"]
MAX_NEW_TOKENS = config["llm"].get("max_new_tokens", 80)

if provider == "local":
    print(f"Loading LOCAL LLM: {model_name}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.float32,
        device_map="auto"
    )


def generate_answer(prompt):
    if provider == "local":
        return _local_generate(prompt)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _local_generate(prompt):
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1400     # leave headroom for new tokens
    )

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,               # greedy - faster + more deterministic
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1,        # reduces looping
        )

    # decode only the newly generated tokens (skip the prompt)
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()