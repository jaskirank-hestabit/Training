import json
from utils.data_cleaner import (
    load_jsonl,
    remove_empty_samples,
    remove_duplicates,
    remove_token_outliers
)

data = load_jsonl("data/train.jsonl")

data = remove_empty_samples(data)
data = remove_duplicates(data)
data = remove_token_outliers(data, max_tokens=512)

with open("data/train_cleaned.jsonl", "w") as f:
    for row in data:
        f.write(json.dumps(row) + "\n")

print(f"Cleaned samples: {len(data)}")