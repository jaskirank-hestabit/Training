import os

# Model 
MODEL_PATH        = os.getenv("MODEL_PATH", "../../day3/quantized/model.gguf")
N_CTX             = int(os.getenv("N_CTX", "4096"))
N_THREADS         = int(os.getenv("N_THREADS", "4"))
N_GPU_LAYERS      = int(os.getenv("N_GPU_LAYERS", "0"))   # 0 = CPU only; >0 = offload layers to GPU

# Generation Defaults 
DEFAULT_MAX_TOKENS     = int(os.getenv("DEFAULT_MAX_TOKENS", "512"))
DEFAULT_TEMPERATURE    = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_TOP_P          = float(os.getenv("DEFAULT_TOP_P", "0.9"))
DEFAULT_TOP_K          = int(os.getenv("DEFAULT_TOP_K", "40"))
DEFAULT_REPEAT_PENALTY = float(os.getenv("DEFAULT_REPEAT_PENALTY", "1.1"))

# API 
API_HOST  = os.getenv("API_HOST", "0.0.0.0")
API_PORT  = int(os.getenv("API_PORT", "8000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Streamlit 
STREAMLIT_API_URL = os.getenv("STREAMLIT_API_URL", "http://localhost:8000")