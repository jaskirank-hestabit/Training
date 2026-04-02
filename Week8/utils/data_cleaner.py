import json
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2")


def load_jsonl(path):
    data = []
    with open(path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def remove_empty_samples(data):
    cleaned = []
    for row in data:
        if row["instruction"].strip() and row["output"].strip():
            cleaned.append(row)
    return cleaned


def remove_duplicates(data):
    seen = set()
    unique = []

    for row in data:
        key = (
            row["instruction"],
            row["input"],
            row["output"]
        )

        if key not in seen:
            seen.add(key)
            unique.append(row)

    return unique


def remove_token_outliers(data, max_tokens=512):
    filtered = []

    for row in data:
        text = (
            row["instruction"]
            + " "
            + row["input"]
            + " "
            + row["output"]
        )

        token_count = len(tokenizer.encode(text))

        if token_count <= max_tokens:
            filtered.append(row)

    return filtered