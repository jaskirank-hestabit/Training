import logging
import config
from llama_cpp import Llama

logger = logging.getLogger("model_loader")

_model: Llama | None = None


def get_model() -> Llama:
    """Singleton loader — loads the GGUF model once and caches it."""
    global _model
    if _model is None:
        logger.info(f"Loading model from: {config.MODEL_PATH}")
        _model = Llama(
            model_path=config.MODEL_PATH,
            n_ctx=config.N_CTX,
            n_threads=config.N_THREADS,
            n_gpu_layers=config.N_GPU_LAYERS,
            verbose=False,
            chat_format="chatml",   # works for Phi-3, Mistral, Qwen, TinyLlama
        )
        logger.info("Model loaded and ready.")
    return _model