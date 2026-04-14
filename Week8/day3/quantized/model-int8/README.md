# INT8 Quantized Model

Base: TinyLlama/TinyLlama-1.1B-Chat-v1.0
VRAM: ~1.24 GB (In-memory)
Disk Size: ~1.24 GB (Weights saved mostly as FP16 with quantization config)
Speed: 4.7 tok/s

## Load code:
```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
bnb = BitsAndBytesConfig(load_in_8bit=True, llm_int8_threshold=6.0)
model = AutoModelForCausalLM.from_pretrained("/content/quantized/model-int8", quantization_config=bnb)
```