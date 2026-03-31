# src/evaluation/rag_eval.py
import re
from typing import List, Dict

_STOP = {"the","a","an","is","are","was","were","be","been","have","has","had",
         "do","does","did","will","would","could","should","may","might","of",
         "in","on","at","to","for","with","by","from","this","that","it","not",
         "and","or","but","i","we","they","he","she","its","their","our"}

def compute_faithfulness(answer: str, context: str) -> float:
    """Word-overlap faithfulness: fraction of answer keywords found in context."""
    if not answer or not context:
        return 0.0
    a_words = set(re.findall(r'\b\w+\b', answer.lower())) - _STOP
    c_words = set(re.findall(r'\b\w+\b', context.lower()))
    if not a_words:
        return 0.0
    return round(len(a_words & c_words) / len(a_words), 4)


def detect_hallucination(answer: str, context: str, threshold: float = 0.35) -> Dict:
    score = compute_faithfulness(answer, context)
    disclaimers = ["not covered","not found","no information","cannot find",
                   "i don't know","outside knowledge","not mentioned"]
    has_disclaimer = any(p in answer.lower() for p in disclaimers)
    return {
        "faithfulness_score":       score,
        "is_potential_hallucination": score < threshold and not has_disclaimer,
        "confidence":               "HIGH" if score >= 0.6 else "MEDIUM" if score >= 0.35 else "LOW",
        "has_disclaimer":           has_disclaimer,
    }


def evaluate_rag_response(answer: str, context: str, sources: List[Dict]) -> Dict:
    result = detect_hallucination(answer, context)
    if sources:
        avg = sum(s.get("rerank_score", 0) for s in sources) / len(sources)
        result["avg_source_score"] = round(avg, 4)
        result["num_sources"]      = len(sources)
    else:
        result["avg_source_score"] = 0.0
        result["num_sources"]      = 0
    return result