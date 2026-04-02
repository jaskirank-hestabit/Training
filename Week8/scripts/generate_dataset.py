import json
import random

qa_samples = []
reasoning_samples = []
extraction_samples = []

qa_templates = [
    (
        "Explain Python programming language",
        "Python is a high-level interpreted language used in web development, machine learning, automation, and data analysis."
    ),
    (
        "What is a list in Python?",
        "A list is an ordered and mutable data structure that can store multiple items of different data types."
    ),
    (
        "What is a dictionary?",
        "A dictionary stores data in key-value pairs and allows fast lookup using keys."
    ),
]

reasoning_templates = [
    (
        "Why use functions in code?",
        "Functions improve modularity, readability, reusability, and reduce duplication in large codebases."
    ),
    (
        "Why is binary search faster than linear search?",
        "Binary search reduces the search space by half on every step, making its time complexity O(log n)."
    ),
]

extraction_templates = [
    (
        "Extract variable name from code",
        "user_age = 25",
        "user_age"
    ),
    (
        "Extract function name from code",
        "def calculate_total(price, tax): return price + tax",
        "calculate_total"
    ),
]

data = []

for _ in range(400):
    q, a = random.choice(qa_templates)
    data.append({
        "instruction": q,
        "input": "",
        "output": a
    })

for _ in range(300):
    q, a = random.choice(reasoning_templates)
    data.append({
        "instruction": q,
        "input": "",
        "output": a
    })

for _ in range(300):
    ins, inp, out = random.choice(extraction_templates)
    data.append({
        "instruction": ins,
        "input": inp,
        "output": out
    })

random.shuffle(data)

with open("data/train.jsonl", "w") as f:
    for row in data[:900]:
        f.write(json.dumps(row) + "\n")

with open("data/val.jsonl", "w") as f:
    for row in data[900:]:
        f.write(json.dumps(row) + "\n")