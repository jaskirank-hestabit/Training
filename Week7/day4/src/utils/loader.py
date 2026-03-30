import pandas as pd


def load_txt(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def load_md(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def load_pdf(path):
    try:
        import pypdf
        reader = pypdf.PdfReader(path)
        pages = []
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:                              # skip blank/image-only pages
                pages.append((page_num, text))
        return pages                              # list of tuples, NOT a string
    except ImportError:
        print("pypdf not installed. Run: pip install pypdf")
        return []


def load_docx(path):
    try:
        from docx import Document
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except ImportError:
        print("python-docx not installed.")
        return ""


def load_csv(path):
    try:
        df = pd.read_csv(path)
        df = df.fillna("")
        lines = []
        for _, row in df.iterrows():
            parts = [f"{col}: {val}" for col, val in row.items() if str(val).strip()]
            lines.append("  |  ".join(parts))
        return "\n".join(lines)
    except Exception as e:
        print(f"CSV load error: {e}")
        return ""


def load_file(path):
    if path.endswith(".txt"):
        return load_txt(path)
    elif path.endswith(".md"):
        return load_md(path)
    elif path.endswith(".pdf"):
        return load_pdf(path)
    elif path.endswith(".docx"):
        return load_docx(path)
    elif path.endswith(".csv"):
        return load_csv(path)
    else:
        return ""
