# Multimodal RAG — Day 3

## Overview
Image RAG pipeline that ingests images, generates CLIP embeddings,
OCR text, and BLIP captions - then supports text→image, image→image,
and image→answer retrieval.

## Pipeline Flow

### Ingestion (image_ingest.py)
```
Raw Images (JPG/PNG)
        │
        ├─────────────────────┐──────────────────────┐
        ▼                     ▼                      ▼
   OCR (Tesseract)     CLIP Embedding          BLIP Caption
   Extracts text       512-dim vector          Natural language
   from image          image representation    description
        │                     │                      │
        └─────────────────────┴──────────────────────┘
                              │
                              ▼
                    FAISS image_index.faiss
                    (stores 512-dim vectors)
```

### Query (image_search.py + test1.py)
```
Text Query ------> CLIP text encoder -> 512-dim -> FAISS search -> Images
Image Query -----> CLIP image encoder -> 512-dim -> FAISS search -> Images
Image → Answer --> Groq Vision LLM (llama-4-scout) reads image directly
```

## Models Used
| Model | Purpose | Dimension |
|-------|---------|-----------|
| CLIP (clip-vit-base-patch32) | Image + text embeddings | 512-dim |
| BLIP-large | Image captioning | - |
| Tesseract | OCR text extraction | - |
| Groq llama-4-scout (vision) | Chart/diagram interpretation | - |

## Why CLIP?
CLIP maps both images and text into the same 512-dimensional vector space.
This means a text query like "bar chart" can directly find similar images
without needing image-specific training.

## Query Modes
1. **Text → Image**: Embed query text with CLIP -> find similar images
2. **Image → Image**: Embed query image with CLIP -> find visually similar images  
3. **Image → Answer**: Send image directly to vision LLM -> accurate interpretation

## OCR Role
OCR extracts horizontal text (title, legend, axis numbers) at ingest time.
This text is stored in FAISS metadata and used for keyword-based image retrieval.
For visual chart interpretation, we use the vision LLM directly (OCR alone
cannot read rotated axis labels reliably).