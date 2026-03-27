import os
import cv2
import numpy as np
from tqdm import tqdm
from PIL import Image, ImageEnhance

import pytesseract
from transformers import BlipProcessor, BlipForConditionalGeneration

from src.embeddings.clip_embedder import get_image_embedding
from src.vectorstore.faiss_store import FAISSStore

IMAGE_PATH = "src/data/raw/images"
SAVE_PATH  = "src/vectorstore/image_index.faiss"
SUPPORTED  = (".png", ".jpg", ".jpeg")


# ---------- LOAD BLIP ----------
print("Loading BLIP caption model...")
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
blip_model     = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")


# ---------- OCR (multi-pass for charts) ----------
def extract_ocr(image_path):
    """
    Multi-pass OCR:
      Pass 1 — standard upscaled image  (catches horizontal text: title, y-axis, legend)
      Pass 2 — rotated 90° CCW          (catches labels rotated ~90°)
      Pass 3 — rotated 45° CCW          (catches labels rotated ~45°)
    Results are merged and deduplicated.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return ""

        # Upscale for better OCR accuracy
        scale  = 2
        h, w   = img.shape[:2]
        img_up = cv2.resize(img, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

        # Convert to grayscale + sharpen
        gray    = cv2.cvtColor(img_up, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (0, 0), 1)
        sharp   = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)

        cfg = "--oem 3 --psm 11"   # sparse text — best for charts

        # Pass 1: upright
        text1 = pytesseract.image_to_string(sharp, config=cfg)

        # Pass 2: rotate 90° CCW
        rot90 = cv2.rotate(sharp, cv2.ROTATE_90_COUNTERCLOCKWISE)
        text2 = pytesseract.image_to_string(rot90, config=cfg)

        # Pass 3: rotate 45° CCW (common for grouped bar chart x-labels)
        center   = (sharp.shape[1] // 2, sharp.shape[0] // 2)
        M        = cv2.getRotationMatrix2D(center, 45, 1.0)
        rot45    = cv2.warpAffine(sharp, M, (sharp.shape[1], sharp.shape[0]),
                                  flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)
        text3    = pytesseract.image_to_string(rot45, config=cfg)

        # Merge: deduplicate lines across passes
        seen, merged = set(), []
        for line in (text1 + "\n" + text2 + "\n" + text3).splitlines():
            clean = line.strip()
            if len(clean) > 2 and clean not in seen:
                seen.add(clean)
                merged.append(clean)

        return "\n".join(merged)

    except Exception as e:
        print(f"  OCR error: {e}")
        return ""


# ---------- CAPTION ----------
def generate_caption(image_path):
    raw_image = Image.open(image_path).convert("RGB")
    inputs    = blip_processor(raw_image, return_tensors="pt")
    out       = blip_model.generate(**inputs, max_new_tokens=60)
    return blip_processor.decode(out[0], skip_special_tokens=True)


# ---------- INGEST ----------
def run_image_ingestion():
    files = [
        os.path.join(IMAGE_PATH, f)
        for f in os.listdir(IMAGE_PATH)
        if f.lower().endswith(SUPPORTED)
    ]

    if not files:
        print("No images found.")
        return

    print(f"Found {len(files)} images\n")

    embeddings, metadata = [], []

    for path in tqdm(files):
        print(f"\nProcessing: {path}")

        ocr_text = extract_ocr(path)
        caption  = generate_caption(path)
        emb      = get_image_embedding(path)

        embeddings.append(emb)
        metadata.append({
            "image_path": path,
            "ocr_text":   ocr_text,
            "caption":    caption,
            "type":       "image"
        })

        print(f"Caption : {caption}")
        print(f"OCR     : {ocr_text[:200]}")

    emb_array = np.array(embeddings)
    print(f"\nEmbedding array shape: {emb_array.shape}")

    dim   = emb_array.shape[1]
    store = FAISSStore(dim)
    store.add(embeddings, [
        {"text": m["caption"] + " " + m["ocr_text"], "metadata": m}
        for m in metadata
    ])
    store.save(SAVE_PATH)
    print("\nImage ingestion complete!")


if __name__ == "__main__":
    run_image_ingestion()