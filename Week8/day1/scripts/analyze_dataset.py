import os
import json
import matplotlib.pyplot as plt
from transformers import AutoTokenizer

# Create output folder
os.makedirs("analysis", exist_ok=True)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2")

lengths = []

# Read dataset
with open("data/train.jsonl", "r") as f:
    for line in f:
        row = json.loads(line)

        text = (
            row["instruction"]
            + " "
            + row["input"]
            + " "
            + row["output"]
        )

        tokens = tokenizer.encode(text)
        lengths.append(len(tokens))

# Stats
print("Max:", max(lengths))
print("Avg:", sum(lengths) / len(lengths))
print("Min:", min(lengths))

# Plot
plt.figure(figsize=(8, 5))
plt.hist(lengths, bins=30)
plt.xlabel("Token Length")
plt.ylabel("Frequency")
plt.title("Token Distribution")

# Save graph
plt.savefig("analysis/token_distribution.png")

print("Graph saved at: analysis/token_distribution.png")