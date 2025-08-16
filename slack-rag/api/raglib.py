import os, re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import httpx
import chromadb
import fitz  # PyMuPDF
from pathlib import Path
try:
    import yaml
except Exception:
    yaml = None

# ---------- Config (env-aware, good defaults for non-Docker) ----------
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
GEN_MODEL   = os.getenv("GEN_MODEL",   "llama3:instruct")      # you have this
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text:latest")    # pick a real embedding model
DATA_DIR    = Path(os.getenv("DATA_DIR", Path(__file__).resolve().parents[1] / "data"))
CHROMA_DIR  = os.getenv("CHROMA_DIR", str(Path(__file__).resolve().parents[1] / "chroma_local"))
CHUNK_SIZE = 1400
CHUNK_OVERLAP = 200
SUPPORTED_EXTS = {".txt", ".md", ".pdf"}

# Optional: silence Chroma telemetry noise
os.environ.setdefault("CHROMA_TELEMETRY_IMPLEMENTATION", "none")

client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(name="docs", metadata={"hnsw:space": "cosine"})

# Load product aliases from data/shared/product_aliases.yaml (optional)
PRODUCT_ALIASES_PATH = DATA_DIR / "shared" / "product_aliases.yaml"
try:
    if yaml and PRODUCT_ALIASES_PATH.exists():
        with PRODUCT_ALIASES_PATH.open("r", encoding="utf-8") as f:
            _raw = yaml.safe_load(f) or {}
            PRODUCT_ALIASES = {k.lower(): [a.lower() for a in v] for k, v in _raw.items()}
    else:
        PRODUCT_ALIASES = {}
except Exception:
    PRODUCT_ALIASES = {}

def canonicalize_product(name: str | None) -> str | None:
    """Return canonical product name (lowercase) if found in aliases, else normalized input or None."""
    if not name:
        return None
    n = name.strip().lower()
    if not PRODUCT_ALIASES:
        return n
    if n in PRODUCT_ALIASES:
        return n
    for canon, aliases in PRODUCT_ALIASES.items():
        if n == canon or n in aliases:
            return canon
    return n

# ---------- Utilities ----------
def _clean_text(s: str) -> str:
    s = s.replace("\x00", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def _read_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if ext == ".pdf":
        doc = fitz.open(path)
        pages = [p.get_text("text") or "" for p in doc]
        doc.close()
        return "\n".join(pages)
    return ""

def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP) -> List[str]:
    text = _clean_text(text)
    if not text: return []
    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        if end == len(text): break
        start = end - overlap
    return chunks

# ---------- Ollama client ----------
class Ollama:
    def __init__(self, base=OLLAMA_HOST):
        self.base = base

    async def embed(self, text: str) -> list[float]:
        txt = (text or "").strip()
        if not txt:
            return []

        payloads = [
            # Newer API shapes
            #{"model": EMBED_MODEL, "input": txt},
            #{"model": EMBED_MODEL, "input": [txt]},
            # Legacy API shape (your server accepts this)
            {"model": EMBED_MODEL, "prompt": txt},
        ]

        async with httpx.AsyncClient(timeout=120.0) as c:
            last_err = None
            for pl in payloads:
                try:
                    r = await c.post(f"{self.base}/api/embeddings", json=pl)
                    r.raise_for_status()
                    js = r.json()
                    # Accept common response shapes
                    if isinstance(js, dict):
                        if "embedding" in js and js["embedding"]:
                            return js["embedding"]
                        if "embeddings" in js and js["embeddings"]:  # some older builds
                            # could be list-of-vectors; return the first
                            first = js["embeddings"][0] if isinstance(js["embeddings"], list) else js["embeddings"]
                            if first: return first
                        if "data" in js and js["data"]:
                            emb = js["data"][0].get("embedding") or []
                            if emb: return emb
                except Exception as e:
                    last_err = e
            raise RuntimeError(f"Ollama embeddings returned empty/unknown payload. Last error: {last_err}")

    async def generate(self, prompt: str, temperature=0.2, max_tokens=512) -> str:
        payload = {
            "model": GEN_MODEL,
            "prompt": prompt,
            "options": {"temperature": temperature, "num_predict": max_tokens},
            "stream": False
        }
        async with httpx.AsyncClient(timeout=None) as c:
            r = await c.post(f"{self.base}/api/generate", json=payload)
            r.raise_for_status()
            js = r.json()
            return js.get("response", "")

ollama = Ollama()

# ---------- Ingestion & Retrieval ----------
async def add_documents(paths: list[Path]) -> dict:
    added = 0
    for path in paths:
        # skip unsupported file types quickly
        if path.suffix.lower() not in SUPPORTED_EXTS:
            continue

        text = _read_text(path)
        chunks = chunk_text(text)
        if not chunks:
            continue

        product = _infer_product_from_path(path)  # << detect once per file
        product = canonicalize_product(product)

        ids, docs, metas, embs = [], [], [], []
        for i, ch in enumerate(chunks):
            emb = await ollama.embed(ch)
            ids.append(f"{path.as_posix()}::chunk_{i}")
            docs.append(ch)
            metas.append({
                "source": path.as_posix(),
                "chunk": i,
                "n_chunks": len(chunks),
                "chars": len(ch),
                "product": product,  # << IMPORTANT
            })
            embs.append(emb)

        collection.add(ids=ids, documents=docs, metadatas=metas, embeddings=embs)
        added += len(ids)
    return {"chunks_added": added, "collection_count": collection.count()}


async def query(q: str, k=5, product: str | None = None) -> dict:
    q_emb = await ollama.embed(q)
    # allow alias/canonical product names
    product = canonicalize_product(product)
    where = {"product": product} if product else None
    # pass metadata filter to narrow the search and speed it up
    if where:
        res = collection.query(query_embeddings=[q_emb], n_results=k, where=where)
    else:
        res = collection.query(query_embeddings=[q_emb], n_results=k)
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    ids   = res.get("ids", [[]])[0]
    dists = res.get("distances", [[]])[0]
    hits = []
    for i, doc in enumerate(docs):
        hits.append({
            "id": ids[i],
            "document": doc,
            "metadata": metas[i],
            "score": (1 - dists[i]) if dists and dists[i] is not None else None
        })
    return {"hits": hits}

def build_prompt(question: str, hits: list[dict], product: str | None = None):
    lines, sources = [], []
    for idx, h in enumerate(hits, start=1):
        src = h["metadata"].get("source", "")
        snippet = _clean_text(h["document"])[:800]
        lines.append(f"[{idx}] Source: {src}\n{snippet}\n")
        sources.append({"n": idx, "source": src, "score": h.get("score"), "product": h["metadata"].get("product")})
    context = "\n\n".join(lines) if lines else "(no matching docs)"

    product_rule = f"Only answer about the product '{product}'. Ignore other products.\n" if product else ""
    system = (
        "You are a helpful internal assistant. Use ONLY the provided context. "
        "If the user is not asking a question, say that you only answer product-related queries"
        "Do not cite the selected sources. If the answer isn't in contect, say you don't know."
        "Do not mention documents without relevant information."        
    
        + product_rule
    )

    prompt = f"""{system}

Question:
{question}

Context:
{context}

Answer (with citations):"""
    return prompt, sources

old_prompt = "Cite sources as [n]. If the answer isn't in context, say you don't know.\n"



def _infer_product_from_path(path: Path) -> str | None:
    """
    Returns the immediate product folder name under DATA_DIR, e.g.
    data/hermes/doc.pdf -> 'hermes'
    data/Zeus/guide.md  -> 'zeus'
    """
    try:
        # Find the index of DATA_DIR in path parts, then take the next part
        parts = list(path.resolve().parts)
        data_parts = list(Path(DATA_DIR).resolve().parts)
        for i in range(len(parts) - len(data_parts) + 1):
            if parts[i:i+len(data_parts)] == data_parts:
                if i + len(data_parts) < len(parts):
                    return parts[i + len(data_parts)].lower()
                break
    except Exception:
        pass
    return None
