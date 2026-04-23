import os
import autogen
from dotenv import load_dotenv

from memory.session_memory import get_session_memory
from memory.vector_store   import get_vector_store
from memory.long_term      import (
    init_long_term_db,
    save_conversation_turn,
    save_fact,
    get_conversation_history,
    get_facts,
    count_conversations,
    count_facts,
)

load_dotenv()


def _llm_config() -> dict:
    return {
        "config_list": [{
            "model":    os.getenv("MODEL_NAME", "phi3"),
            "base_url": os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1"),
            "api_key":  os.getenv("OPENAI_API_KEY",  "ollama"),
        }],
        "temperature": 0.3,
        "max_tokens":  768,
    }


def get_memory_agent(user_query: str, session: str = "default") -> autogen.AssistantAgent:
    """
    Build a memory-enriched AutoGen AssistantAgent.
    System prompt built fresh for every call using all 3 memory layers.
    """
    init_long_term_db()
    stm = get_session_memory(session)
    vs  = get_vector_store()

    # 1. Short-term window (RAM)
    short_ctx = stm.get_context_string()

    # 2. SQLite episodic history
    history = get_conversation_history(session, limit=6)
    if history:
        episodic_lines = "\n".join(
            f"  [{h['ts'][:19]}] {h['agent']}: {h['content'][:200]}"
            for h in history
        )
    else:
        episodic_lines = "  (no prior conversation turns for this session)"

    # 3. SQLite facts
    facts = get_facts(session=session, limit=5)
    if facts:
        fact_lines = "\n".join(f"  • {f['fact'][:200]}" for f in facts)
    else:
        fact_lines = "  (no facts stored yet for this session)"

    # 4. FAISS vector recall — search with ACTUAL user query
    similar = vs.search(user_query, top_k=5, session=session)
    if not similar:
        # fallback: global search across all sessions
        similar = vs.search(user_query, top_k=3)

    if similar:
        vector_lines = "\n".join(
            f"  • [{m['type']} | {m['ts'][:10]}] {m['text'][:200]}"
            for m in similar
        )
    else:
        vector_lines = "  (no similar past entries found)"

    # Build system prompt
    system_prompt = f"""You are a Memory-Aware Conversational Agent.

CRITICAL INSTRUCTIONS — READ BEFORE ANSWERING:
1. You have real memory from previous interactions shown below. USE IT.
2. If the user asks "what did we discuss?" or "what did we talk about?" —
   read the EPISODIC MEMORY section and summarize what you see there.
3. NEVER say "I don't have access to past conversations" — the memory IS here.
4. NEVER say "I cannot recall" — look at the memory sections below.
5. Always end your response with: [MEMORY AGENT COMPLETE]

════════════════════════════════════════
SHORT-TERM MEMORY (current RAM window)
════════════════════════════════════════
{short_ctx}

════════════════════════════════════════
EPISODIC MEMORY (SQLite conversation turns for session: {session})
════════════════════════════════════════
{episodic_lines}

════════════════════════════════════════
SEMANTIC MEMORY (distilled facts — SQLite)
════════════════════════════════════════
{fact_lines}

════════════════════════════════════════
VECTOR RECALL (FAISS similarity search results)
════════════════════════════════════════
{vector_lines}
════════════════════════════════════════

Now answer the user's query using the memory above.
Cite memory when used (e.g. "Based on our earlier discussion about X...").
Be concise and direct.
"""

    return autogen.AssistantAgent(
        name="MemoryAgent",
        system_message=system_prompt,
        llm_config=_llm_config(),
        max_consecutive_auto_reply=5,
        human_input_mode="NEVER",
    )


def run_memory_agent(user_query: str, session: str = "default") -> dict:
    """
    Run one query through the memory-aware agent.
    Persists query + answer to all three memory layers.
    Returns: {"query": str, "answer": str, "session": str}
    """
    init_long_term_db()
    stm = get_session_memory(session)
    vs  = get_vector_store()

    # Persist incoming query
    stm.add(role="user", content=user_query, agent="User")
    save_conversation_turn(session=session, role="user",
                           agent="User", content=user_query)
    vs.add(text=user_query, mem_type="query", session=session)

    # Build and run agent — pass user_query so FAISS searches correctly
    agent = get_memory_agent(user_query=user_query, session=session)
    proxy = autogen.UserProxyAgent(
        name="MemoryProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )
    chat = proxy.initiate_chat(
        recipient=agent,
        message=user_query,
        max_turns=1,
    )

    answer = ""
    for msg in chat.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "MemoryAgent":
            answer = msg.get("content", "")

    # Persist answer
    stm.add(role="assistant", content=answer, agent="MemoryAgent")
    save_conversation_turn(session=session, role="assistant",
                           agent="MemoryAgent", content=answer)
    vs.add(text=answer, mem_type="answer", session=session)

    # Save first meaningful line as a distilled fact
    first_line = next(
        (line.strip() for line in answer.split("\n")
         if line.strip() and not line.strip().startswith("[")),
        answer[:200]
    )
    save_fact(session=session, fact=first_line[:300], source="MemoryAgent")

    print(
        f"[MemoryAgent] session='{session}' | "
        f"STM={len(stm)} | "
        f"FAISS={vs.count()} | "
        f"SQLite turns={count_conversations()} facts={count_facts()}"
    )
    return {"query": user_query, "answer": answer, "session": session}