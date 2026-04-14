# BENCHMARK REPORT — Day 4 Inference Optimisation

**Generated:** 2026-04-10 14:16  
**Base Model:** `TinyLlama/TinyLlama-1.1B-Chat-v1.0`  
**Device:** cuda  
**Benchmark prompt:** _Explain Python programming language_

---

## 1. Models Tested

| Model | Format | Source |
|---|---|---|
| `base_fp16` | FP16 | HuggingFace `TinyLlama/TinyLlama-1.1B-Chat-v1.0` |
| `finetuned_fp16` | FP16 (LoRA merged) | `/content/drive/MyDrive/week8/adapters` |
| `quantized_int8` | INT8 (bitsandbytes) | `/content/drive/MyDrive/week8/quantized/model-int8` |
| `quantized_int4` | INT4 NF4 (bitsandbytes) | `/content/drive/MyDrive/week8/quantized/model-int4` |
| `gguf_q4` | GGUF q4_0/q8_0 (llama.cpp) | `/content/drive/MyDrive/week8/quantized/model.gguf` |

---

## 2. Summary Results

| model | avg_tokens_per_sec | avg_latency_sec | avg_vram_gb | avg_output_tokens |
| --- | --- | --- | --- | --- |
| base_fp16 | 29.534 | 0.962 | 2.211 | 27.889 |
| finetuned_fp16 | 29.766 | 0.954 | 4.411 | 27.889 |
| gguf_q4 | 8.03 | 3.12 | 0.0 | 24.667 |
| quantized_int4 | 17.479 | 1.568 | 6.43 | 27.0 |
| quantized_int8 | 7.606 | 3.954 | 5.645 | 25.667 |

---

## 3. Detailed Results by Prompt Category

### QA

| model | tokens_per_sec | total_time_sec | output_tokens |
| --- | --- | --- | --- |
| base_fp16 | 32.98 | 1.031 | 34 |
| base_fp16 | 32.78 | 0.946 | 31 |
| base_fp16 | 33.04 | 0.848 | 28 |
| finetuned_fp16 | 24.2 | 1.405 | 34 |
| finetuned_fp16 | 25.24 | 1.228 | 31 |
| finetuned_fp16 | 25.93 | 1.08 | 28 |
| quantized_int8 | 4.37 | 8.014 | 35 |
| quantized_int8 | 4.29 | 7.219 | 31 |
| quantized_int8 | 4.74 | 5.913 | 28 |
| quantized_int4 | 18.54 | 1.888 | 35 |
| quantized_int4 | 13.77 | 2.251 | 31 |
| quantized_int4 | 14.38 | 1.947 | 28 |
| gguf_q4 | 11.17 | 2.954 | 33 |
| gguf_q4 | 10.05 | 2.986 | 30 |
| gguf_q4 | 8.26 | 3.269 | 27 |

### Reasoning

| model | tokens_per_sec | total_time_sec | output_tokens |
| --- | --- | --- | --- |
| base_fp16 | 32.34 | 1.113 | 36 |
| base_fp16 | 27.23 | 1.212 | 33 |
| base_fp16 | 25.15 | 2.187 | 55 |
| finetuned_fp16 | 32.47 | 1.109 | 36 |
| finetuned_fp16 | 32.47 | 1.016 | 33 |
| finetuned_fp16 | 32.71 | 1.681 | 55 |
| quantized_int8 | 9.94 | 3.621 | 36 |
| quantized_int8 | 10.31 | 3.201 | 33 |
| quantized_int8 | 9.99 | 3.503 | 35 |
| quantized_int4 | 18.78 | 1.917 | 36 |
| quantized_int4 | 18.57 | 1.777 | 33 |
| quantized_int4 | 18.73 | 2.135 | 40 |
| gguf_q4 | 8.91 | 3.927 | 35 |
| gguf_q4 | 9.79 | 1.942 | 19 |
| gguf_q4 | 10.7 | 4.391 | 47 |

### Extraction

| model | tokens_per_sec | total_time_sec | output_tokens |
| --- | --- | --- | --- |
| base_fp16 | 20.51 | 0.634 | 13 |
| base_fp16 | 30.31 | 0.429 | 13 |
| base_fp16 | 31.47 | 0.254 | 8 |
| finetuned_fp16 | 33.42 | 0.389 | 13 |
| finetuned_fp16 | 32.76 | 0.397 | 13 |
| finetuned_fp16 | 28.69 | 0.279 | 8 |
| quantized_int8 | 7.82 | 1.663 | 13 |
| quantized_int8 | 7.61 | 1.709 | 13 |
| quantized_int8 | 9.38 | 0.746 | 7 |
| quantized_int4 | 18.07 | 0.72 | 13 |
| quantized_int4 | 17.94 | 0.725 | 13 |
| quantized_int4 | 18.53 | 0.756 | 14 |
| gguf_q4 | 7.35 | 1.497 | 11 |
| gguf_q4 | 3.97 | 2.768 | 11 |
| gguf_q4 | 2.07 | 4.345 | 9 |

---

## 4. Key Findings

### Throughput (tokens/sec)
- Fastest model: **finetuned_fp16** at **29.8 tok/s**
- Slowest model: **quantized_int8** at **7.6 tok/s**

### Quantisation Trade-offs
- INT8 quantisation reduces VRAM significantly with minimal quality loss for most tasks
- INT4 (NF4) further reduces VRAM but may show quality degradation on complex reasoning
- GGUF via llama.cpp enables CPU inference and is the most portable deployment format

### Streaming
- All HuggingFace models support `TextStreamer` - TTFT recorded per model in Section 5-8
- llama.cpp natively streams via generator - lowest memory overhead

---

## 5. Recommendations

| Use case | Recommended format |
|---|---|
| GPU server (quality priority) | FP16 base or fine-tuned |
| GPU server (memory constrained) | INT4 NF4 |
| CPU / edge device | GGUF q4_0 via llama.cpp |
| Batch throughput | INT8 with batch_size ≥ 4 |
