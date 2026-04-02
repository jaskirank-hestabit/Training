````markdown
# DATASET ANALYSIS — DAY 1
**Week 8 — LLM Fine-Tuning, Quantization & Optimized Inference**  
**Task:** Day 1 — LLM Architecture + Data Preparation for Fine-Tuning  
**Domain Chosen:** Coding  

---

## 1. Objective

The objective of Day 1 is to prepare a high-quality instruction tuning dataset that can later be used for fine-tuning a Large Language Model (LLM) using LoRA / QLoRA.

The dataset is prepared in **JSONL format** and contains multiple types of instruction-response samples.

This dataset is designed for **instruction tuning** in the coding domain.

---

## 2. Dataset Format

The dataset follows the required JSONL structure:

```json
{"instruction":"...", "input":"...", "output":"..."}
````

Each line represents one training sample.

### Fields

* **instruction** → task or prompt given to the model
* **input** → optional supporting context
* **output** → expected response from the model

---

## 3. Dataset Categories

The dataset includes the 3 mandatory sample types required for Day 1:

### 1. QA (Question Answering)

Examples:

* What is Python?
* What is a list?
* What is a dictionary?

Purpose:
To help the model learn direct factual question-answering.

---

### 2. Reasoning

Examples:

* Why use functions?
* Why use classes?
* Why is binary search faster?

Purpose:
To improve logical explanation and reasoning capability.

---

### 3. Extraction

Examples:

* Extract variable name from code
* Extract function name from code

Purpose:
To train structured information extraction from code snippets.

---

## 4. Dataset Size

### Total Samples Generated

* **Training samples:** 900
* **Validation samples:** 100
* **Total samples:** 1000

### Split Ratio

* **Train:** 90%
* **Validation:** 10%

This split is suitable for fine-tuning workflows.

---

## 5. Data Cleaning Performed

The following preprocessing steps were implemented.

### 1. Empty Sample Removal

Rows with missing `instruction` or `output` values are removed.

---

### 2. Duplicate Removal

Duplicate rows are identified using:

* instruction
* input
* output

Duplicate samples are removed to improve training diversity.

---

### 3. Outlier Removal

Token-length based outlier filtering was implemented.

### Threshold Used

```text
512 tokens
```

Samples exceeding 512 tokens are removed.

### Current Observation

No outliers were found in the current dataset.

---

## 6. Token Length Analysis

Tokenization was performed using the Phi-2 tokenizer.

### Final Statistics

```text
Min Token Length: 8
Average Token Length: 11.19
Max Token Length: 12
```

---

## 7. Distribution Analysis

A token distribution histogram was generated and saved at:

```text
analysis/token_distribution.png
```

This graph helps visualize the spread of token lengths across the training dataset.

---

## 8. Observations

### Positive Observations

* Dataset structure is correct
* Train/validation split is valid
* Data cleaning pipeline is implemented
* Token distribution graph generated successfully
* Outlier filtering logic added

---

### Improvement Areas

The current average token length is low.

```text
Average ≈ 11 tokens
```

This indicates that many samples are short and simple.

For better fine-tuning quality, future improvements should aim for:

```text
Average token length: 50–150
```

This will provide richer context and improve instruction tuning performance.
