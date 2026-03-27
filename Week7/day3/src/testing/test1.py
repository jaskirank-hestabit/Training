import base64
import os
from src.retriever.image_search import ImageSearcher
from src.generator.llm_client import generate_answer, _groq_client

print("Initializing Image Searcher...")
searcher = ImageSearcher()

# -----------------------------
# Test 1: TEXT → IMAGE
# -----------------------------
print("\n===== TEXT → IMAGE =====")
results = searcher.search_by_text("bar chart gender distribution")
for r in results:
    print("\nImage  :", r["metadata"]["image_path"])
    print("Score  :", round(r["score"], 4))
    print("Caption:", r["metadata"]["caption"])
    print("OCR    :", r["metadata"]["ocr_text"][:80])


# -----------------------------
# Test 2: IMAGE → IMAGE
# -----------------------------
print("\n===== IMAGE → IMAGE =====")
image_path = "src/data/raw/images/bar_chart.jpg"
results = searcher.search_by_image(image_path)
for r in results:
    print(f"Similar: {r['metadata']['image_path']}  (score: {round(r['score'], 4)})")


# -----------------------------
# Test 3: IMAGE → ANSWER via Vision LLM
# -----------------------------
print("\n===== IMAGE → ANSWER (Vision LLM) =====")

def analyze_image_with_vision(image_path: str, question: str) -> str:
    """Send image directly to Groq vision model — no OCR needed."""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    media_type = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

    response = _groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",  # Groq vision model
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": question
                    }
                ]
            }
        ],
        max_tokens=500,
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()


question = """Analyze this chart completely and provide:
1. Chart type and exact title
2. All X-axis category labels (read every label carefully)
3. What the Y-axis measures and its value range
4. The legend — what groups/series are being compared
5. Key observations: which category has the highest and lowest values, and how do the groups differ
6. Overall insight: what story does this chart tell in 1-2 sentences"""

print(f"\nAnalyzing: {image_path}")
print("Sending image directly to vision LLM...\n")

answer = analyze_image_with_vision(image_path, question)
print("Answer:\n", answer)

# Also test with diagram
print("\n\n===== DIAGRAM → ANSWER (Vision LLM) =====")
diagram_path = "src/data/raw/images/diagram1.jpg"
if os.path.exists(diagram_path):
    answer2 = analyze_image_with_vision(
        diagram_path,
        "Describe this diagram completely. What is it showing, what are the main components, and what relationships or connections does it illustrate?"
    )
    print("Answer:\n", answer2)