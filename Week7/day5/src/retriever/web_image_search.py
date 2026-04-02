# src/retriever/web_image_search.py
from __future__ import annotations
import os, time, random

# ── Query builder ─────────────────────────────────────────────────────────────

def _describe_via_vision_llm(image_path: str) -> str:
    try:
        from src.generator.llm_client import generate_vision_answer
        prompt = (
            "Look at this image carefully. "
            "Write a short image search query (4–6 words) to find visually similar images. "
            "Focus only on the main subject. "
            "Return ONLY the query — no explanation, no punctuation."
        )
        q = generate_vision_answer(image_path, prompt).strip().strip(".,!")
        words = q.split()
        return " ".join(words[:6]) if len(words) > 6 else q
    except Exception as e:
        print(f"  [web_image_search] vision LLM failed: {e}")
        return ""


def _describe_via_blip(image_path: str) -> str:
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        from PIL import Image as PILImage
        proc = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        mdl  = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-large")
        img    = PILImage.open(image_path).convert("RGB")
        inputs = proc(img, return_tensors="pt")
        out    = mdl.generate(**inputs, max_new_tokens=20)
        caption = proc.decode(out[0], skip_special_tokens=True).strip()
        return " ".join(caption.split()[:5])
    except Exception as e:
        print(f"  [web_image_search] BLIP failed: {e}")
        return ""


def build_search_query(image_path: str, user_hint: str = "") -> str:
    if user_hint.strip():
        return " ".join(user_hint.strip().split()[:6])
    if not image_path or not os.path.exists(image_path):
        return "nature photography"
    q = _describe_via_vision_llm(image_path)
    if q:
        return q
    q = _describe_via_blip(image_path)
    if q:
        return q
    return " ".join(
        os.path.splitext(os.path.basename(image_path))[0]
        .replace("_", " ").replace("-", " ").split()[:5]
    )


# ── Backend 1: DuckDuckGo (with exponential backoff) ─────────────────────────

def _try_ddg(query: str, k: int, timeout: int) -> list[dict] | None:
    """
    Try DDG image search with 3 attempts and exponential backoff.
    Returns list of result dicts on success, None on complete failure.
    """
    try:
        from ddgs import DDGS
    except ImportError:
        print("  [DDG] ddgs not installed — skipping")
        return None

    # Try progressively shorter queries if DDG blocks long ones
    query_variants = [
        query,
        " ".join(query.split()[:4]),
        " ".join(query.split()[:3]),
    ]

    for attempt, q in enumerate(query_variants):
        q = q.strip()
        if not q:
            continue

        wait = 2 ** attempt + random.uniform(0, 1)   # 1s, 2s, 4s with jitter
        if attempt > 0:
            print(f"  [DDG] waiting {wait:.1f}s before retry…")
            time.sleep(wait)

        print(f"  [DDG] attempt {attempt+1}: '{q}'")
        try:
            with DDGS(timeout=timeout) as ddgs:
                hits = list(ddgs.images(
                    q,
                    max_results=k + 4,
                    safesearch="off",
                ))
            if hits:
                print(f"  [DDG] got {len(hits)} results")
                results = []
                for h in hits[:k]:
                    url = h.get("image", "")
                    if url:
                        results.append({
                            "url":    url,
                            "thumb":  h.get("thumbnail") or url,
                            "title":  h.get("title", ""),
                            "source": h.get("source", ""),
                            "width":  h.get("width", 0),
                            "height": h.get("height", 0),
                        })
                if results:
                    return results
        except Exception as e:
            print(f"  [DDG] attempt {attempt+1} failed: {e}")

    print("  [DDG] all attempts exhausted")
    return None


# ── Backend 2: Pixabay (free API key from pixabay.com/api/docs) ──────────────

def _try_pixabay(query: str, k: int) -> list[dict] | None:
    """
    Try Pixabay image search.
    Requires PIXABAY_API_KEY in environment / .env
    Free tier: 100 requests/minute, 20 results max per request.
    """
    import requests
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.environ.get("PIXABAY_API_KEY", "")
    if not api_key:
        print("  [Pixabay] PIXABAY_API_KEY not set — skipping")
        return None

    print(f"  [Pixabay] searching: '{query}'")
    try:
        resp = requests.get(
            "https://pixabay.com/api/",
            params={
                "key":        api_key,
                "q":          query,
                "image_type": "photo",
                "per_page":   min(k + 4, 20),
                "safesearch": "true",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        hits = data.get("hits", [])
        if not hits:
            print("  [Pixabay] no results")
            return None

        results = []
        for h in hits[:k]:
            url = h.get("largeImageURL") or h.get("webformatURL", "")
            if url:
                results.append({
                    "url":    url,
                    "thumb":  h.get("previewURL") or url,
                    "title":  h.get("tags", ""),
                    "source": "pixabay.com",
                    "width":  h.get("imageWidth", 0),
                    "height": h.get("imageHeight", 0),
                })

        print(f"  [Pixabay] got {len(results)} results")
        return results if results else None

    except Exception as e:
        print(f"  [Pixabay] failed: {e}")
        return None


# ── Backend 3: Unsplash (free API key from unsplash.com/developers) ──────────

def _try_unsplash(query: str, k: int) -> list[dict] | None:
    """
    Try Unsplash image search.
    Requires UNSPLASH_ACCESS_KEY in environment / .env
    Free tier: 50 requests/hour.
    """
    import requests
    from dotenv import load_dotenv
    load_dotenv()

    access_key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    if not access_key:
        print("  [Unsplash] UNSPLASH_ACCESS_KEY not set — skipping")
        return None

    print(f"  [Unsplash] searching: '{query}'")
    try:
        resp = requests.get(
            "https://api.unsplash.com/search/photos",
            headers={"Authorization": f"Client-ID {access_key}"},
            params={"query": query, "per_page": min(k, 10)},
            timeout=10,
        )
        resp.raise_for_status()
        items = resp.json().get("results", [])
        if not items:
            print("  [Unsplash] no results")
            return None

        results = []
        for item in items[:k]:
            url   = item["urls"].get("regular", "")
            thumb = item["urls"].get("small", url)
            if url:
                results.append({
                    "url":    url,
                    "thumb":  thumb,
                    "title":  item.get("alt_description") or item.get("description") or query,
                    "source": "unsplash.com",
                    "width":  item.get("width", 0),
                    "height": item.get("height", 0),
                })

        print(f"  [Unsplash] got {len(results)} results")
        return results if results else None

    except Exception as e:
        print(f"  [Unsplash] failed: {e}")
        return None


# ── Public API ────────────────────────────────────────────────────────────────

def search_similar_images_web(
    image_path: str,
    user_hint:  str = "",
    k:          int = 6,
    timeout:    int = 20,
) -> tuple[list[dict], str]:
    """
    Find visually similar images on the web.

    Tries backends in order: DDG → Pixabay → Unsplash
    First backend to return results wins.

    Returns:
        (results, query_used)
    """
    query = build_search_query(image_path, user_hint)
    print(f"  [web_image_search] final query: '{query}'")

    # ── Try DDG first ────────────────────────────────────────────────────
    results = _try_ddg(query, k, timeout)
    if results:
        return results, query

    # ── Fallback 1: Pixabay ──────────────────────────────────────────────
    results = _try_pixabay(query, k)
    if results:
        return results, query

    # ── Fallback 2: Unsplash ─────────────────────────────────────────────
    results = _try_unsplash(query, k)
    if results:
        return results, query

    # ── All backends failed ──────────────────────────────────────────────
    print("  [web_image_search] all backends failed")
    return [{
        "url": "", "thumb": "",
        "title": (
            "All image sources unavailable right now. "
            "DDG is rate-limited. "
            "Add PIXABAY_API_KEY or UNSPLASH_ACCESS_KEY to .env for reliable results."
        ),
        "source": "", "width": 0, "height": 0,
    }], query