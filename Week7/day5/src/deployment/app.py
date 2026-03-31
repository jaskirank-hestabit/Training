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
if "memory" not in st.session_state:
    from src.memory.memory_store import MemoryStore
    st.session_state.memory = MemoryStore(max_turns=5)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []          # [{query, answer, timestamp}]

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
    st.title("🧠 Enterprise KIS")
    st.caption("Knowledge Intelligence System — Day 5 Capstone")
    st.divider()

    st.subheader("📊 System Status")
    st.write("Text Index  :", "✅ Ready"   if _index_ok()   else "❌  Run `pipelines/ingest.py`")
    st.write("Image Index :", "✅ Ready"   if _img_idx_ok() else "❌  Run `pipelines/image_ingest.py`")
    st.write("SQL Database:", "✅ Ready"   if _db_ok()      else "❌  Run `utils/init_db.py`")

    st.divider()
    st.subheader("💭 Memory")
    st.caption(f"Turns stored: {len(st.session_state.chat_history)}/5")

    if st.button("🗑️ Clear Conversation Memory"):
        st.session_state.memory.clear()
        st.session_state.chat_history = []
        st.success("Memory cleared!")

    if st.session_state.temp_store:
        if st.button("🔄 Drop Uploaded File (use main index)"):
            st.session_state.temp_store = None
            st.success("Switched back to main index.")

    st.divider()
    st.caption("**Run order:**\n1. `init_db.py`\n2. `ingest.py`\n3. `image_ingest.py`\n4. `streamlit run deployment/app.py`")


# ── Tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📄  Text RAG", "🖼️  Image RAG", "🗄️  SQL RAG"])


# ═══════════════════════════════════════════════════════════════════════
#  TAB 1  ——  TEXT RAG
# ═══════════════════════════════════════════════════════════════════════
with tab1:
    st.header("📄 Document Question Answering")
    st.caption("Ask questions from internal documents — upload a file or use the pre-ingested index.")

    left, right = st.columns([1, 1.6], gap="large")

    with left:
        # ── File upload ──
        st.subheader("📁 Document Source")
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
                source_label = ("📂 Using **uploaded file** (in-memory)"
                                if st.session_state.temp_store
                                else "📚 Using **main document index**")
                st.success(source_label)

        st.divider()

        # ── Query ──
        st.subheader("🔍 Ask a Question")
        user_query = st.text_area("Your question:", height=120,
                                  placeholder="e.g. What is the process for credit underwriting?")

        with st.expander("⚙️ Advanced Options"):
            use_memory    = st.checkbox("Include conversation memory in prompt", value=True)
            use_refine    = st.checkbox("Self-refinement loop (slower but more accurate)", value=False)
            filter_choice = st.selectbox("Filter by doc type", ["— none —","pdf","txt","md","docx","csv"])

        ask_btn = st.button("🔎 Ask", type="primary", use_container_width=True)

    with right:
        st.subheader("💬 Answer")

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

                        mem_ctx = (st.session_state.memory.get_history_text()
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
                            st.session_state.memory.add("user", user_query)
                            st.session_state.memory.add("assistant", answer)
                            st.session_state.chat_history.append({
                                "query":     user_query,
                                "answer":    answer,
                                "timestamp": datetime.now().strftime("%H:%M:%S"),
                            })

                        # ── Display ──
                        st.markdown(answer)
                        st.divider()

                        # metrics row
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Faithfulness",  f"{eval_r['faithfulness_score']:.2f}")
                        c2.metric("Confidence",    eval_r["confidence"])
                        c3.metric("Sources used",  eval_r["num_sources"])
                        c4.metric("Avg src score", f"{eval_r['avg_source_score']:.2f}")

                        if eval_r["is_potential_hallucination"]:
                            st.warning("⚠️ Low faithfulness score — answer may not be fully "
                                       "grounded in the retrieved context. Verify manually.")

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

        # ── Memory panel ──
        if st.session_state.chat_history:
            st.divider()
            st.subheader(f"💭 Conversation Memory ({len(st.session_state.chat_history)} turns)")
            for msg in reversed(st.session_state.chat_history[-5:]):
                with st.expander(f"🕐 {msg['timestamp']}  —  {msg['query'][:70]}…"):
                    st.markdown(f"**Q:** {msg['query']}")
                    st.markdown(f"**A:** {msg['answer'][:400]}…" if len(msg['answer']) > 400 else f"**A:** {msg['answer']}")


# ═══════════════════════════════════════════════════════════════════════
#  TAB 2  ——  IMAGE RAG
# ═══════════════════════════════════════════════════════════════════════
with tab2:
    st.header("🖼️ Image Retrieval & Analysis")
    st.caption("CLIP-powered image search · OCR · Vision LLM answers")

    left2, right2 = st.columns([1, 1.6], gap="large")

    with left2:
        st.subheader("🖼️ Image Input")
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

        mode = st.radio("🔀 Search Mode:", [
            "Text → Image  (find images by text description)",
            "Image → Image (find visually similar images)",
            "Image → Text Answer  (vision LLM analyses image)",
        ])

        text_q_img = ""
        if "Text →" in mode or "→ Text" in mode:
            text_q_img = st.text_input("Text query / question:",
                                       placeholder="e.g. bar chart showing gender distribution")

        k_img = st.slider("Top-k results:", 1, 8, 3)
        img_btn = st.button("🔍 Search / Analyse", type="primary",
                            use_container_width=True, key="img_btn")

    with right2:
        st.subheader("📊 Results")

        if img_btn:
            if not _img_idx_ok() and "→ Text" not in mode:
                st.error("❌ Image index not found. Run `python -m src.pipelines.image_ingest`.")
            else:
                with st.spinner("Processing …"):
                    try:
                        if "Text → Image" in mode:
                            if not text_q_img.strip():
                                st.warning("Enter a text description to search.")
                            else:
                                from src.retriever.image_search import ImageSearcher
                                searcher = ImageSearcher()
                                hits = searcher.search_by_text(text_q_img, k=k_img)
                                st.markdown(f"**{len(hits)} matching image(s):**")
                                for r in hits:
                                    p = r["metadata"]["image_path"]
                                    c1, c2 = st.columns([1, 2])
                                    with c1:
                                        if os.path.exists(p):
                                            st.image(p, use_container_width=True)
                                        else:
                                            st.caption(f"(file not found: {p})")
                                    with c2:
                                        st.markdown(f"**Score:** {r['score']:.4f}")
                                        st.markdown(f"**Caption:** {r['metadata']['caption']}")
                                        st.markdown(f"**OCR:** {r['metadata']['ocr_text'][:120]}")
                                    st.divider()

                        elif "Image → Image" in mode:
                            if not query_img_path:
                                st.warning("Upload or select an image first.")
                            else:
                                from src.retriever.image_search import ImageSearcher
                                searcher = ImageSearcher()
                                hits = searcher.search_by_image(query_img_path, k=k_img)
                                st.markdown(f"**{len(hits)} visually similar image(s):**")
                                cols = st.columns(min(len(hits), 3))
                                for i, r in enumerate(hits):
                                    p = r["metadata"]["image_path"]
                                    with cols[i % 3]:
                                        if os.path.exists(p):
                                            st.image(p, use_container_width=True)
                                        st.caption(f"Score: {r['score']:.4f}\n{r['metadata']['caption'][:60]}")

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

                                # Show CLIP-similar images as supporting evidence
                                if _img_idx_ok():
                                    st.divider()
                                    st.markdown("**Related images from index (CLIP similarity):**")
                                    from src.retriever.image_search import ImageSearcher
                                    searcher = ImageSearcher()
                                    hits = searcher.search_by_image(query_img_path, k=3)
                                    cols = st.columns(min(len(hits), 3))
                                    for i, r in enumerate(hits):
                                        p = r["metadata"]["image_path"]
                                        with cols[i % 3]:
                                            if os.path.exists(p):
                                                st.image(p, use_container_width=True)
                                            st.caption(f"{r['score']:.4f}")

                    except Exception as e:
                        st.error(f"Error: {e}")
                        import traceback; st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════
#  TAB 3  ——  SQL RAG
# ═══════════════════════════════════════════════════════════════════════
with tab3:
    st.header("🗄️ Natural Language → SQL → Answer")
    st.caption("Write questions in plain English; the system generates SQL, executes it, and summarises the result.")

    if not _db_ok():
        st.error("❌ Database not found at `src/data/raw/sample.db`. "
                 "Run `python -m src.utils.init_db` first.")
    else:
        left3, right3 = st.columns([1, 1.6], gap="large")

        with left3:
            # ── Schema ──
            st.subheader("📐 Database Schema")
            try:
                from src.utils.schema_loader import load_schema
                schema_text = load_schema("src/data/raw/sample.db")
                st.code(schema_text, language="sql")
            except Exception as e:
                st.error(f"Schema error: {e}")

            # ── Sample data ──
            st.subheader("👁️ Sample Data (first 10 rows)")
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
            st.subheader("❓ Ask in Natural Language")
            sql_q = st.text_area(
                "Your question:",
                height=120,
                placeholder="e.g. Show total sales by artist for 2023\n"
                            "e.g. Which artist had the highest sales?\n"
                            "e.g. How many records are in the sales table?",
            )
            sql_btn = st.button("⚡ Generate & Execute SQL",
                                type="primary", use_container_width=True)

        with right3:
            st.subheader("📊 Results")

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
                                st.subheader("🔧 Generated SQL")
                                st.code(out["sql"], language="sql")

                                # ── Results table ──
                                st.subheader("📋 Query Results")
                                if out["result"]:
                                    df_res = pd.DataFrame(out["result"])
                                    st.dataframe(df_res, use_container_width=True)
                                    st.caption(f"Rows returned: **{len(df_res)}**")

                                    # Optional bar chart if there's a numeric column
                                    num_cols = df_res.select_dtypes("number").columns.tolist()
                                    cat_cols = df_res.select_dtypes(
                                        exclude="number").columns.tolist()
                                    if num_cols and cat_cols:
                                        with st.expander("📈 Quick Chart"):
                                            x_col = st.selectbox("X axis:", cat_cols, key="x_col")
                                            y_col = st.selectbox("Y axis:", num_cols, key="y_col")
                                            st.bar_chart(
                                                df_res.set_index(x_col)[y_col])
                                else:
                                    st.info("Query returned no rows.")

                                # ── LLM summary ──
                                st.subheader("💬 LLM Summary")
                                st.markdown(out.get("answer", "_No summary._"))

                        except Exception as e:
                            st.error(f"Pipeline error: {e}")
                            import traceback; st.code(traceback.format_exc())