# TRAINING REPORT — DAY 2
## Parameter-Efficient Fine-Tuning with LoRA / QLoRA

---

## 1. Objective

Fine-tune a large language model on a custom coding instruction dataset using QLoRA (Quantized Low-Rank Adaptation) on a Colab GPU (Tesla T4). The goal was to train only ~1% of model parameters while preserving full model quality through 4-bit quantization.

---

## 2. Model & Hardware

| Parameter | Value |
|---|---|
| Base Model | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` |
| Total Parameters | 1,102,301,184 |
| GPU | Tesla T4 (15 GB VRAM) |
| Framework | `transformers` + `peft` + `trl` |

---

## 3. Dataset

| Split | Samples |
|---|---|
| Train | `train_cleaned.jsonl` |
| Validation | `val.jsonl` |
| Domain | Coding (Python QA, Reasoning, Extraction) |
| Format | JSONL — `instruction`, `input`, `output` fields |

Dataset was cleaned using `day1/utils/data_cleaner.py`:
- Removed empty samples
- Removed duplicate entries
- Removed token outliers (> 512 tokens)

---

## 4. Quantization — BitsAndBytes (4-bit)

```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)
```

| Setting | Value | Purpose |
|---|---|---|
| `load_in_4bit` | `True` | Load weights in 4-bit precision |
| `bnb_4bit_quant_type` | `nf4` | NormalFloat4 — best quality for LLMs |
| `bnb_4bit_compute_dtype` | `float16` | Upcast to fp16 during forward pass |
| `bnb_4bit_use_double_quant` | `True` | Quantize the quantization constants (extra memory saving) |

Memory saving: ~4x compared to full fp32 loading.

---

## 5. LoRA Configuration

```python
LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
```

| Hyperparameter | Value | Meaning |
|---|---|---|
| `r` (rank) | 16 | Size of the low-rank decomposition matrices |
| `lora_alpha` | 32 | Scaling factor (effective scale = alpha/r = 2.0) |
| `lora_dropout` | 0.05 | Dropout on LoRA layers to prevent overfitting |
| `bias` | `none` | Do not train bias terms |
| `task_type` | `CAUSAL_LM` | Causal language modelling task |

### Trainable Parameters

```
trainable params: 2,252,800
all params:       1,102,301,184
trainable %:      0.2044%
```

Only ~0.2% of parameters trained — well within the < 1% target.

---

## 6. Training Configuration

```python
SFTConfig(
    per_device_train_batch_size=4,
    gradient_accumulation_steps=2,      # effective batch size = 8
    num_train_epochs=3,
    learning_rate=2e-4,
    optim="paged_adamw_8bit",
    fp16=False,
    bf16=False,
    max_grad_norm=0.3,
    warmup_steps=10,
    lr_scheduler_type="cosine",
    max_length=512
)
```

| Setting | Value | Reason |
|---|---|---|
| Batch size | 4 | Max that fits in T4 VRAM |
| Gradient accumulation | 2 steps | Effective batch = 8 without extra memory |
| Epochs | 3 | Sufficient for adapter convergence |
| Learning rate | 2e-4 | Standard for QLoRA fine-tuning |
| Optimizer | `paged_adamw_8bit` | Paged memory — avoids OOM on optimizer states |
| fp16 / bf16 | Both `False` | T4 does not support bf16; AMP disabled to avoid grad scaler crash |
| Max grad norm | 0.3 | Conservative clipping — standard for QLoRA |
| LR scheduler | cosine | Smooth decay over training |
| Max sequence length | 512 | Prevents OOM on long samples |

---

## 7. Memory Strategy Summary

| Technique | Saving |
|---|---|
| 4-bit NF4 quantization | ~4x base model memory reduction |
| Double quantization | Additional ~0.4 bits/param saving |
| Paged AdamW 8-bit | Optimizer states offloaded to CPU when needed |
| Gradient accumulation | Larger effective batch without extra VRAM |
| Only training LoRA adapters | 99.8% of weights frozen |
| Max sequence length = 512 | Caps activation memory per batch |

---

## 8. Output Artifacts

| File | Description |
|---|---|
| `adapters/adapter_model.safetensors` | Trained LoRA adapter weights (equivalent to `adapter_model.bin`) |
| `adapters/adapter_config.json` | LoRA configuration (r, alpha, target modules) |
| `adapters/tokenizer.json` | Tokenizer vocabulary |
| `adapters/tokenizer_config.json` | Tokenizer settings |
| `adapters/chat_template.jinja` | Chat prompt template |
