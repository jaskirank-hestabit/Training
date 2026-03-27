from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

MODEL_NAME = "openai/clip-vit-base-patch32"

print(f"Loading CLIP model: {MODEL_NAME}")

device = "cpu"

model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
processor = CLIPProcessor.from_pretrained(MODEL_NAME)


def _to_tensor(output):
    """Extract plain tensor regardless of transformers version."""
    if isinstance(output, torch.Tensor):
        return output
    # BaseModelOutputWithPooling / similar dataclass
    if hasattr(output, "pooler_output") and output.pooler_output is not None:
        return output.pooler_output
    if hasattr(output, "last_hidden_state"):
        return output.last_hidden_state[:, 0, :]   # CLS token
    raise ValueError(f"Cannot extract tensor from: {type(output)}")


# ---------- IMAGE EMBEDDING ----------
def get_image_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        raw = model.get_image_features(**inputs)

    image_features = _to_tensor(raw)                                  # (1, 512)
    image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
    return image_features[0].cpu().tolist()                           # (512,)


# ---------- TEXT EMBEDDING ----------
def get_text_embedding(text):
    inputs = processor(text=[text], return_tensors="pt", padding=True).to(device)

    with torch.no_grad():
        raw = model.get_text_features(**inputs)

    text_features = _to_tensor(raw)                                   # (1, 512)
    text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
    return text_features[0].cpu().tolist()                            # (512,)