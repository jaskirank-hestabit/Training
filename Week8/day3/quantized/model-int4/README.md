# INT4 (NF4) Quantized Model

Base: TinyLlama/TinyLlama-1.1B-Chat-v1.0
VRAM: ~0.77 GB (In-memory)
Disk Size: ~0.77 GB (Weights saved mostly as FP16 with quantization config)
Speed: 17.7 tok/s

## Load code:
```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                         bnb_4bit_compute_dtype=torch.float16)
model = AutoModelForCausalLM.from_pretrained("/content/quantized/model-int4", quantization_config=bnb)
```