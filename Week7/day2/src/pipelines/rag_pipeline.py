from src.retriever.hybrid_retriever import HybridRetriever
from src.pipelines.context_builder import build_context
from src.generator.llm_client import generate_answer
import yaml

CONFIG_PATH = "src/config/model.yaml"

with open(CONFIG_PATH) as f:
    _cfg = yaml.safe_load(f)

TOP_K          = _cfg.get("retrieval", {}).get("top_k", 5)
MIN_SCORE      = _cfg.get("retrieval", {}).get("min_rerank_score", 0.45)

PROMPT_TEMPLATE = """\
You are an enterprise document assistant.
Read the numbered context passages below. Answer ONLY using information explicitly \
stated in those passages.
Do NOT use any outside knowledge. Do NOT make up information.
If the answer cannot be found in the passages, respond with exactly:
"This topic is not covered in the provided documents."

Context:
{context}

Question: {query}

Instructions:
- Summarize the answer in your own words using only the context above
- Use bullet points for any lists or factors mentioned  
- Do NOT copy sentences directly — rephrase them
- If context does not answer the question, say: "Not found in documents."

Answer (cite passage numbers like [1] or [2] where relevant):"""


def run_rag(query, filters=None):
    retriever = HybridRetriever()
    results   = retriever.retrieve(query=query, k=TOP_K, filters=filters)

    # Relevance gate
    # If the best chunk doesn't score above the threshold, the document
    # simply doesn't contain this topic. Don't call the LLM at all.
    if not results or results[0].get("rerank_score", 0) < MIN_SCORE:
        best = results[0].get("rerank_score", 0) if results else 0
        print(f"\n[Relevance gate] Best score {best:.4f} < threshold {MIN_SCORE}")
        print("[Relevance gate] Skipping LLM — topic not in documents.\n")
        return {
            "answer":  "This topic is not covered in the provided documents.",
            "sources": [],
            "context": "",
            "results": results,
        }

    context, sources = build_context(results)

    prompt = PROMPT_TEMPLATE.format(context=context, query=query)

    print("\n=== CONTEXT SENT TO LLM ===")
    print(context)
    print(f"\n[Best rerank score: {results[0].get('rerank_score', 0):.4f}]")
    print("===========================\n")

    answer = generate_answer(prompt)

    return {
        "answer":  answer,
        "sources": sources,
        "context": context,
        "results": results,
    }


if __name__ == "__main__":
    print("RAG Pipeline \n")

    user_input = input("Enter your query: ").strip()
    if not user_input:
        user_input = "Explain how credit underwriting works"

    output = run_rag(user_input)

    print("\n================ ANSWER ================\n")
    print(output["answer"])

    print("\n================ SOURCES (traceable) ================\n")
    if output["sources"]:
        for i, s in enumerate(output["sources"], 1):
            print(f"[{i}] {s['source']}  |  page {s['page']}  |  {s['type']}"
                  f"  |  via {s['search_type']}  |  score {s['rerank_score']}")
    else:
        print("No sources — topic not found in documents.")