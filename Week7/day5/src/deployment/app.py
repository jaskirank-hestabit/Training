# deployment/app.py
import sys, os

# ── Make all src.* imports and relative paths work ──────────────────────
# ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import tempfile, json, sqlite3, base64
from datetime import datetime

import streamlit as st
import pandas as pd
from PIL import Image

# ── Page config ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Enterprise Knowledge Intelligence System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Minimal CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
.metric-card {background:#f0f2f6;border-radius:8px;padding:12px 16px;margin:4px 0;}
.badge-high   {background:#d4edda;color:#155724;border-radius:4px;padding:2px 8px;font-size:0.8em;}
.badge-medium {background:#fff3cd;color:#856404;border-radius:4px;padding:2px 8px;font-size:0.8em;}
.badge-low    {background:#f8d7da;color:#721c24;border-radius:4px;padding:2px 8px;font-size:0.8em;}
</style>
""", unsafe_allow_html=True)

# ── Session-state init ───────────────────────────────────────────────────
# Always reload memory from disk so it survives page refreshes
from src.memory.memory_store import MemoryStore
if "memory" not in st.session_state:
    st.session_state.memory = MemoryStore(max_turns=5, log_path="src/logs/chat_logs.json")
else:
    st.session_state.memory._load_existing()

if "chat_history" not in st.session_state:
    # Rebuild chat_history display list from persisted memory
    st.session_state.chat_history = []
    msgs = st.session_state.memory.get_messages()
    # Pair up user+assistant turns
    for i in range(0, len(msgs) - 1, 2):
        u = msgs[i]
        a = msgs[i + 1] if i + 1 < len(msgs) else {"content": ""}
        if u["role"] == "user":
            st.session_state.chat_history.append({
                "query":     u["content"],
                "answer":    a["content"],
                "timestamp": u.get("timestamp", "")[:19].replace("T", " "),
            })

if "temp_store" not in st.session_state:
    st.session_state.temp_store = None          # in-memory FAISSStore for uploads

if "temp_img_path" not in st.session_state:
    st.session_state.temp_img_path = None


# ── Helpers ──────────────────────────────────────────────────────────────
def _index_ok():  return os.path.exists("src/vectorstore/index.faiss")
def _img_idx_ok():return os.path.exists("src/vectorstore/image_index.faiss")
def _db_ok():     return os.path.exists("src/data/raw/sample.db")


# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("CAPSTONE")
    st.caption("Day 5 - Advanced RAG")
    st.divider()

    st.subheader("📊 System Status")
    st.write("Text Index  :", "✅ Ready"   if _index_ok()   else "❌  Run `pipelines/ingest.py`")
    st.write("Image Index :", "✅ Ready"   if _img_idx_ok() else "❌  Run `pipelines/image_ingest.py`")
    st.write("SQL Database:", "✅ Ready"   if _db_ok()      else "❌  Run `utils/init_db.py`")

    st.divider()
    st.subheader("💭 Memory")
    st.caption(f"Turns stored: {len(st.session_state.chat_history)}/5")
    st.caption("→ See **Memory** tab for full history")

    if st.button("🗑️ Clear Memory"):
        st.session_state.memory.clear()
        st.session_state.chat_history = []
        st.success("Memory cleared!")
        st.rerun()

    if st.session_state.temp_store:
        if st.button("🔄 Drop Uploaded File (use main index)"):
            st.session_state.temp_store = None
            st.success("Switched back to main index.")

    st.divider()


# ── Tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📄  Text RAG", "🖼️  Image RAG", "🗄️  SQL RAG", "💭  Memory"])


# ═══════════════════════════════════════════════════════════════════════
#  TAB 1  ——  TEXT RAG
# ═══════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Document Question Answering")
    st.caption("Ask questions from internal documents — upload a file or use the pre-ingested index.")

    left, right = st.columns([1, 1.6], gap="large")

    with left:
        # ── File upload ──
        st.subheader("Document Source")
        uploaded_file = st.file_uploader(
            "Upload (optional — overrides main index for this session)",
            type=["pdf", "txt", "md", "docx", "csv"],
        )

        if uploaded_file:
            st.info(f"📎 **{uploaded_file.name}** loaded")
            if st.button("⚙️ Ingest This File", key="ingest_btn"):
                with st.spinner(f"Ingesting {uploaded_file.name} …"):
                    try:
                        from src.pipelines.ingest_single import ingest_single_file
                        suffix = os.path.splitext(uploaded_file.name)[1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        store = ingest_single_file(tmp_path, source_name=uploaded_file.name)
                        st.session_state.temp_store = store
                        os.unlink(tmp_path)
                        st.success(f"✅ Ingested **{uploaded_file.name}** — "
                                   f"{len(store.texts)} chunks indexed in memory.")
                    except Exception as e:
                        st.error(f"Ingestion failed: {e}")
        else:
            if not _index_ok():
                st.warning("⚠️ No main index found. Upload a file or run `ingest.py`.")
            else:
                source_label = ("Using **uploaded file** (in-memory)"
                                if st.session_state.temp_store
                                else "Using **main document index**")
                st.success(source_label)

        st.divider()

        # ── Query ──
        st.subheader("Ask a Question")
        user_query = st.text_area("Your question:", height=120,
                                  placeholder="e.g. What is the process for credit underwriting?")

        with st.expander("Advanced Options"):
            use_memory    = st.checkbox("Include conversation memory in prompt", value=True)
            use_refine    = st.checkbox("Self-refinement loop (slower but more accurate)", value=False)
            filter_choice = st.selectbox("Filter by doc type", ["— none —","pdf","txt","md","docx","csv"])

        ask_btn = st.button("Ask", type="primary", use_container_width=True)

    with right:
        st.subheader("Answer")

        if ask_btn:
            if not user_query.strip():
                st.warning("Please enter a question.")
            elif not _index_ok() and not st.session_state.temp_store:
                st.error("No index available. Upload a file or run `ingest.py`.")
            else:
                filters = ({"doc_type": filter_choice}
                           if filter_choice != "— none —" else None)

                with st.spinner("Retrieving & generating …"):
                    try:
                        from src.pipelines.rag_pipeline import run_rag
                        from src.evaluation.rag_eval import evaluate_rag_response
                        from src.generator.llm_client import generate_answer

                        mem_ctx = (st.session_state.memory.get_history_text(rag_type="text")
                                   if use_memory else "")

                        result = run_rag(
                            user_query,
                            filters=filters,
                            memory_context=mem_ctx,
                            temp_store=st.session_state.temp_store,
                        )
                        answer = result["answer"]

                        # ── Optional refinement loop ──
                        if use_refine and result["context"]:
                            refine_prompt = (
                                "Review this answer for accuracy against the context.\n\n"
                                f"Context (excerpt): {result['context'][:600]}\n\n"
                                f"Original Answer: {answer}\n\n"
                                "Refined Answer (improve only if genuinely needed; "
                                "stay faithful to context):"
                            )
                            refined = generate_answer(refine_prompt)
                            if len(refined.strip()) > 20:
                                answer = refined
                                st.caption("✨ Self-refinement loop applied")

                        # ── Evaluation ──
                        eval_r = evaluate_rag_response(answer, result["context"], result["sources"])

                        # ── Update memory ──
                        if use_memory:
                            st.session_state.memory.add(
                                "user", user_query, rag_type="text",
                                extra={"query": user_query}
                            )
                            st.session_state.memory.add(
                                "assistant", answer, rag_type="text",
                                extra={"answer": answer}
                            )
                            st.session_state.chat_history.append({
                                "query":     user_query,
                                "answer":    answer,
                                "timestamp": datetime.now().strftime("%H:%M:%S"),
                                "rag_type":  "text",
                            })

                        # ── Display ──
                        st.markdown(answer)
                        st.divider()

                        # metrics row
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Faithfulness Score", f"{eval_r['faithfulness_score']:.2f}")
                        c2.metric("Confidence",         eval_r["confidence"])
                        c3.metric("Avg Source Score",   f"{eval_r['avg_source_score']:.2f}")

                        # Hallucination detection banner
                        if eval_r["is_potential_hallucination"]:
                            st.error(
                                "**Hallucination Detected** — "
                                f"Faithfulness score `{eval_r['faithfulness_score']:.2f}` "
                                "is below threshold `0.35`. "
                                "The answer may contain information not grounded in the "
                                "retrieved documents. Please verify manually."
                            )
                        elif eval_r["has_disclaimer"]:
                            st.info(
                                "**No Hallucination** — "
                                "The model explicitly stated it could not find the answer "
                                "in the provided documents."
                            )
                        else:
                            st.success(
                                f"**No Hallucination Detected** — "
                                f"Answer is grounded in context "
                                f"(faithfulness: `{eval_r['faithfulness_score']:.2f}`)."
                            )

                        # sources
                        if result["sources"]:
                            with st.expander("📎 Traceable Sources", expanded=True):
                                for i, s in enumerate(result["sources"], 1):
                                    st.markdown(
                                        f"**[{i}]** `{s['source']}` &nbsp;|&nbsp; "
                                        f"page {s['page']} &nbsp;|&nbsp; "
                                        f"type `{s['type']}` &nbsp;|&nbsp; "
                                        f"via `{s['search_type']}` &nbsp;|&nbsp; "
                                        f"score **{s['rerank_score']}**"
                                    )
                        else:
                            st.info("No sources — topic not found in documents.")

                        with st.expander("🔍 Raw Context Sent to LLM"):
                            st.text(result["context"][:3000] or "(empty)")

                    except Exception as e:
                        st.error(f"Pipeline error: {e}")
                        import traceback; st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════
#  TAB 2  ——  IMAGE RAG
# ═══════════════════════════════════════════════════════════════════════
with tab2:
    st.header("Image Retrieval & Analysis")
    st.caption("CLIP-powered image search · OCR · Vision LLM answers")

    left2, right2 = st.columns([1, 1.6], gap="large")

    with left2:
        st.subheader("Image Input")
        uploaded_img = st.file_uploader(
            "Upload an image (optional)",
            type=["png", "jpg", "jpeg"],
            key="img_uploader",
        )

        query_img_path = None

        if uploaded_img:
            img_pil = Image.open(uploaded_img)
            st.image(img_pil, caption=f"Uploaded: {uploaded_img.name}",
                     use_container_width=True)
            # Persist to temp file (stable across reruns)
            if (st.session_state.temp_img_path is None or
                    not os.path.exists(st.session_state.temp_img_path)):
                suffix = os.path.splitext(uploaded_img.name)[1]
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tmp.write(uploaded_img.getvalue())
                tmp.close()
                st.session_state.temp_img_path = tmp.name
            query_img_path = st.session_state.temp_img_path
        else:
            st.session_state.temp_img_path = None
            img_dir = "src/data/raw/images"
            if os.path.exists(img_dir):
                imgs = [f for f in os.listdir(img_dir)
                        if f.lower().endswith((".png", ".jpg", ".jpeg"))]
                if imgs:
                    sel = st.selectbox("Or select a local image:", imgs)
                    query_img_path = os.path.join(img_dir, sel)
                    st.image(query_img_path, caption=sel, use_container_width=True)
                else:
                    st.info("No images found in `src/data/raw/images/`")
            else:
                st.info("Image folder `src/data/raw/images/` not found.")

        st.divider()

        mode = st.radio("Search Mode:", [
            "Text → Image ",
            "Image → Image — Local Index ",
            "Image → Image — Web Search ",
            "Image → Text Answer",
        ])

        text_q_img = ""
        if "Text → Image" in mode:
            text_q_img = st.text_input(
                "Text description to search:",
                placeholder="e.g. bar chart showing gender distribution",
            )
        elif "Web Search" in mode:
            text_q_img = st.text_input(
                "Optional search hint (leave blank to auto-describe image):",
                placeholder="e.g. orange tabby cat sitting on a sofa",
            )
        elif "→ Text Answer" in mode:
            text_q_img = st.text_input(
                "Question about the image:",
                placeholder="e.g. What does this chart show?",
            )

        k_img = st.slider("Top-k results:", 1, 8, 3)
        img_btn = st.button("🔍 Search / Analyse", type="primary",
                            use_container_width=True, key="img_btn")

    with right2:
        st.subheader("Results")

        if img_btn:
            if not _img_idx_ok() and "→ Text" not in mode:
                st.error("❌ Image index not found. Run `python -m src.pipelines.image_ingest`.")
            else:
                with st.spinner("Processing …"):
                    try:
                        # ── TEXT → IMAGE (web search) ────────────────────────────
                        if "Text → Image" in mode:
                            if not text_q_img.strip():
                                st.warning("Enter a text description to search.")
                            else:
                                cache_key = f"web_hits__text__{text_q_img}__{k_img}"
                                if cache_key not in st.session_state:
                                    with st.spinner("Searching the web for matching images …"):
                                        from src.retriever.web_image_search import (
                                            search_similar_images_web,
                                        )
                                        web_hits, query_used = search_similar_images_web(
                                            image_path="",        # no image — query is text
                                            user_hint=text_q_img, # use exactly what user typed
                                            k=k_img,
                                        )
                                        st.session_state[cache_key] = (web_hits, query_used)
                                else:
                                    web_hits, query_used = st.session_state[cache_key]

                                st.info(f"🔍 Search query used: **{query_used}**")

                                if not web_hits or not web_hits[0]["url"]:
                                    first_title = web_hits[0]["title"] if web_hits else "Unknown error"
                                    st.error(
                                        f"**No images returned.**\n\n"
                                        f"Reason: `{first_title}`\n\n"
                                        f"Things to try:\n"
                                        f"- Make sure `ddgs` is installed: `pip install ddgs`\n"
                                        f"- Try a shorter / simpler description\n"
                                        f"- Check your internet connection"
                                    )
                                else:
                                    st.markdown(f"**{len(web_hits)} image(s) found on the web:**")
                                    rows = [web_hits[i:i+3] for i in range(0, len(web_hits), 3)]
                                    for row in rows:
                                        cols = st.columns(len(row))
                                        for col, hit in zip(cols, row):
                                            with col:
                                                try:
                                                    st.image(
                                                        hit["thumb"] or hit["url"],
                                                        use_container_width=True,
                                                    )
                                                except Exception:
                                                    st.caption("(image failed to load)")
                                                st.caption(
                                                    f"**{hit['title'][:50]}**\n"
                                                    f"*{hit['source']}*"
                                                )
                                                if hit["url"]:
                                                    st.markdown(
                                                        f"[Open full image ↗]({hit['url']})"
                                                    )

                        # ── IMAGE → IMAGE (local FAISS index) ───────────────────
                        elif "Local Index" in mode:
                            if not query_img_path:
                                st.warning("Upload or select an image first.")
                            else:
                                from src.retriever.image_search import ImageSearcher
                                searcher = ImageSearcher()
                                hits = searcher.search_by_image(query_img_path, k=k_img)
                                st.markdown(f"**{len(hits)} visually similar image(s) from local index:**")
                                cols = st.columns(min(len(hits), 3))
                                for i, r in enumerate(hits):
                                    p = r["metadata"]["image_path"]
                                    with cols[i % 3]:
                                        if os.path.exists(p):
                                            st.image(p, use_container_width=True)
                                        st.caption(
                                            f"Score: {r['score']:.4f}\n"
                                            f"{r['metadata']['caption'][:60]}"
                                        )

                        # ── IMAGE → IMAGE (web search — works for ANY image) ─────
                        elif "Web Search" in mode:
                            if not query_img_path:
                                st.warning("Upload or select an image first.")
                            else:
                                # Cache key: path + hint + k so we don't re-search on rerun
                                cache_key = f"web_hits__{query_img_path}__{text_q_img}__{k_img}"
                                if cache_key not in st.session_state:
                                    with st.spinner("Describing image and searching the web (up to 15s) …"):
                                        from src.retriever.image_search import ImageSearcher
                                        searcher  = ImageSearcher()
                                        web_hits, query_used = searcher.search_similar_web(
                                            query_img_path,
                                            user_hint=text_q_img,
                                            k=k_img,
                                        )
                                        st.session_state[cache_key] = (web_hits, query_used)
                                else:
                                    web_hits, query_used = st.session_state[cache_key]

                                st.info(f"🔍 Search query used: **{query_used}**")

                                if not web_hits or not web_hits[0]["url"]:
                                    st.warning(
                                        "No web results. Make sure "
                                        "`duckduckgo-search` is installed:\n"
                                        "```\npip install duckduckgo-search\n```"
                                    )
                                else:
                                    st.markdown(
                                        f"**{len(web_hits)} similar image(s) found on the web:**"
                                    )
                                    # Show in a responsive grid of 3
                                    rows = [web_hits[i:i+3] for i in range(0, len(web_hits), 3)]
                                    for row in rows:
                                        cols = st.columns(len(row))
                                        for col, hit in zip(cols, row):
                                            with col:
                                                try:
                                                    st.image(
                                                        hit["thumb"] or hit["url"],
                                                        use_container_width=True,
                                                    )
                                                except Exception:
                                                    st.caption("(image failed to load)")
                                                st.caption(
                                                    f"**{hit['title'][:50]}**\n"
                                                    f"*{hit['source']}*"
                                                )
                                                if hit["url"]:
                                                    st.markdown(
                                                        f"[Open full image ↗]({hit['url']})"
                                                    )

                        # ── IMAGE → TEXT ANSWER (vision LLM) ────────────────────
                        elif "→ Text Answer" in mode:
                            if not query_img_path:
                                st.warning("Upload or select an image first.")
                            else:
                                question = (text_q_img.strip() if text_q_img.strip() else
                                            "Analyse this image completely.\n"
                                            "1. What type of visual is it?\n"
                                            "2. What data or content does it show?\n"
                                            "3. List all visible text, labels, and values.\n"
                                            "4. Summarise the key insight in 2 sentences.")

                                from src.generator.llm_client import generate_vision_answer
                                answer = generate_vision_answer(query_img_path, question)

                                st.markdown("**Vision LLM Answer:**")
                                st.markdown(answer)

                                # ── Log to memory ──
                                img_label = os.path.basename(query_img_path) if query_img_path else "image"
                                st.session_state.memory.add(
                                    "user",
                                    f"[Image: {img_label}] {question}",
                                    rag_type="image",
                                    extra={"query": question, "image": img_label}
                                )
                                st.session_state.memory.add(
                                    "assistant",
                                    answer,
                                    rag_type="image",
                                    extra={"answer": answer}
                                )
                                st.session_state.chat_history.append({
                                    "query":     f"[Image RAG] {img_label}: {question[:60]}",
                                    "answer":    answer,
                                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                                    "rag_type":  "image",
                                })

                    except Exception as e:
                        st.error(f"Error: {e}")
                        import traceback; st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════
#  TAB 3  ——  SQL RAG
# ═══════════════════════════════════════════════════════════════════════
with tab3:
    st.header("Natural Language → SQL → Answer")
    st.caption("Write questions in plain English; the system generates SQL, executes it, and summarises the result.")

    if not _db_ok():
        st.error("❌ Database not found at `src/data/raw/sample.db`. "
                 "Run `python -m src.utils.init_db` first.")
    else:
        left3, right3 = st.columns([1, 1.6], gap="large")

        with left3:
            # ── Schema ──
            st.subheader("Database Schema")
            try:
                from src.utils.schema_loader import load_schema
                schema_text = load_schema("src/data/raw/sample.db")
                st.code(schema_text, language="sql")
            except Exception as e:
                st.error(f"Schema error: {e}")

            # ── Sample data ──
            st.subheader("Sample Data (first 10 rows)")
            try:
                conn   = sqlite3.connect("src/data/raw/sample.db")
                tables = pd.read_sql(
                    "SELECT name FROM sqlite_master WHERE type='table'", conn)
                for tbl in tables["name"]:
                    with st.expander(f"Table: **{tbl}**", expanded=True):
                        df_preview = pd.read_sql(
                            f"SELECT * FROM [{tbl}] LIMIT 10", conn)
                        st.dataframe(df_preview, use_container_width=True)
                conn.close()
            except Exception as e:
                st.error(f"Preview error: {e}")

            st.divider()

            # ── Query input ──
            st.subheader("Ask in Natural Language")
            sql_q = st.text_area(
                "Your question:",
                height=120,
                placeholder=(
                    "e.g. Show all employees on Line-A\n"
                    "e.g. Who has the most defects on their line?\n"
                    "e.g. Show average salary by department\n"
                    "e.g. Which line has the highest efficiency?\n"
                    "e.g. List all night shift employees and their product\n"
                    "e.g. Who joined before 2018?"
                ),
            )
            sql_btn = st.button("⚡ Generate & Execute SQL",
                                type="primary", use_container_width=True)

        with right3:
            st.subheader("Results")

            if sql_btn:
                if not sql_q.strip():
                    st.warning("Enter a question first.")
                else:
                    with st.spinner("Generating SQL and executing …"):
                        try:
                            from src.pipelines.sql_pipeline import run_sql_pipeline
                            out = run_sql_pipeline(sql_q)

                            if "error" in out:
                                st.error(f"❌ {out['error']}")
                                if out.get("sql"):
                                    st.subheader("Generated SQL (failed)")
                                    st.code(out["sql"], language="sql")
                            else:
                                # ── SQL ──
                                st.subheader("Generated SQL")
                                st.code(out["sql"], language="sql")

                                # ── Results table ──
                                st.subheader("Query Results")
                                if out["result"]:
                                    df_res = pd.DataFrame(out["result"])
                                    st.dataframe(df_res, use_container_width=True)
                                    st.caption(f"Rows returned: **{len(df_res)}**")
                                else:
                                    st.info("Query returned no rows.")

                                # ── LLM summary ──
                                st.subheader("LLM Summary")
                                sql_answer = out.get("answer", "_No summary._")
                                st.markdown(sql_answer)

                                # ── Log to memory ──
                                st.session_state.memory.add(
                                    "user",
                                    sql_q,
                                    rag_type="sql",
                                    extra={"query": sql_q}
                                )
                                st.session_state.memory.add(
                                    "assistant",
                                    sql_answer,
                                    rag_type="sql",
                                    extra={"answer": sql_answer, "sql": out["sql"]}
                                )
                                st.session_state.chat_history.append({
                                    "query":     f"[SQL RAG] {sql_q[:80]}",
                                    "answer":    sql_answer,
                                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                                    "rag_type":  "sql",
                                })

                        except Exception as e:
                            st.error(f"Pipeline error: {e}")
                            import traceback; st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════
#  TAB 4  ——  CONVERSATION MEMORY
# ═══════════════════════════════════════════════════════════════════════
with tab4:
    st.header("Conversation Memory")
    st.caption("Last 5 turns are stored on disk and survive page refreshes.")

    # ── Stats row ───────────────────────────────────────────────────────
    total_turns = len(st.session_state.chat_history)
    log_path    = "src/logs/chat_logs.json"
    log_exists  = os.path.exists(log_path)

    text_turns  = sum(1 for m in st.session_state.chat_history if m.get("rag_type","text") == "text")
    image_turns = sum(1 for m in st.session_state.chat_history if m.get("rag_type") == "image")
    sql_turns   = sum(1 for m in st.session_state.chat_history if m.get("rag_type") == "sql")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total turns",      total_turns)
    c2.metric("📄 Text RAG",      text_turns)
    c3.metric("🖼️ Image RAG",    image_turns)
    c4.metric("🗄️ SQL RAG",      sql_turns)
    c5.metric("Log file",         "exists" if log_exists else "❌ not yet")

    st.divider()

    # ── Controls ────────────────────────────────────────────────────────
    col_a, col_b = st.columns([1, 3])

    with col_a:
        if st.button("Clear All Memory", type="primary", use_container_width=True):
            st.session_state.memory.clear()
            st.session_state.chat_history = []
            st.success("Memory cleared!")
            st.rerun()

    # with col_b:
    #     if log_exists:
    #         with open(log_path) as f:
    #             raw_logs = f.read()
    #         st.download_button(
    #             label="⬇️ Download CHAT-LOGS.json",
    #             data=raw_logs,
    #             file_name="CHAT-LOGS.json",
    #             mime="application/json",
    #             use_container_width=True,
    #         )

    st.divider()

    # ── Conversation display ─────────────────────────────────────────────
    if not st.session_state.chat_history:
        st.info(
            "No conversation history yet. "
            "Ask a question in the **Text RAG** tab to start building memory."
        )
    else:
        st.subheader(f"Stored Turns ({total_turns})")

        # Show most recent first
        _TYPE_ICON = {"text": "📄", "image": "🖼️", "sql": "🗄️"}

        for idx, msg in enumerate(reversed(st.session_state.chat_history)):
            turn_num  = total_turns - idx
            ts        = msg.get("timestamp", "")
            rtype     = msg.get("rag_type", "text")
            icon      = _TYPE_ICON.get(rtype, "📄")

            with st.expander(
                f"Turn {turn_num}  •  {icon} {rtype.upper()}  •  🕐 {ts}  —  {msg['query'][:70]}…",
                expanded=(idx == 0),
            ):
                st.markdown("**Question:**")
                st.info(msg["query"])

                st.markdown("**Answer:**")
                st.success(msg["answer"])

        st.divider()

        # ── Raw JSON viewer ──────────────────────────────────────────────
        with st.expander("🔍 View raw memory (what gets injected into the LLM prompt)"):
            raw_history = st.session_state.memory.get_messages()
            if raw_history:
                import json
                st.code(json.dumps(raw_history, indent=2), language="json")
            else:
                st.caption("Empty.")