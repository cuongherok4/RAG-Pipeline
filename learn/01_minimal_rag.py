"""
learn/01_minimal_rag.py — Toàn bộ RAG trong một file, không framework.

Đọc file này TRƯỚC khi đọc phần còn lại của repo. Mỗi hàm bên dưới là một
bước của pipeline; app Streamlit chỉ là phiên bản nhiều lựa chọn hơn của
chính các bước này.

    INDEXING  (làm một lần):  ① load PDF → ② chunk → ③ embed → ④ lưu vào "index"
    GENERATION (mỗi câu hỏi): câu hỏi → ⑥ tìm chunk gần nhất → ⑧ prompt → ⑨ LLM

Số ①–⑨ trùng với số bước trong app và README. Bước ⑤ (pre-retrieval) và
⑦ (post-retrieval) là tuỳ chọn nên script này bỏ qua.

Chạy:
    uv run python learn/01_minimal_rag.py
    uv run python learn/01_minimal_rag.py --question "Mô hình được đánh giá trên tập dữ liệu nào?"
    uv run python learn/01_minimal_rag.py --pdf file_cua_ban.pdf --llm qwen2.5:3b

Chỉ cần pypdf, fastembed, numpy (đã có trong requirements.txt).
Model embedding (~220MB) tự tải ở lần chạy đầu. Không cần API key.

LLM là tuỳ chọn: nếu Ollama đang chạy (https://ollama.com, rồi
`ollama pull qwen2.5:7b`; dùng model khác thì truyền `--llm <tên>`), script gọi
nó để sinh câu trả lời. Nếu không, script in ra prompt cuối cùng — bạn vẫn
thấy được RAG đưa gì cho LLM.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent

# Model đa ngôn ngữ, đọc được tiếng Việt, 384 chiều, chạy tốt trên CPU.
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@dataclass
class Chunk:
    text: str
    page: int  # giữ số trang để câu trả lời trích dẫn được nguồn


# ─── INDEXING ────────────────────────────────────────────────────────────────

def load_pdf(path: Path) -> list[tuple[int, str]]:
    """Bước ① — Loader: PDF → danh sách (số trang, text của trang)."""
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError

    try:
        reader = PdfReader(path)
        reader.pages[0]  # pypdf đọc cấu trúc file lười biếng — ép đọc để lỗi hiện ngay
    except (PdfReadError, OSError, IndexError) as exc:
        raise SystemExit(f"Không đọc được PDF {path}: {exc}\n"
                         "File hỏng, rỗng, hoặc không phải PDF. Thử mở nó bằng trình xem PDF.")

    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append((i, text))
    return pages


def split_into_chunks(pages: list[tuple[int, str]], size: int, overlap: int) -> list[Chunk]:
    """
    Bước ② — Chunking: cắt text thành các đoạn dài tối đa `size` ký tự.

    Vì sao phải cắt? Model embedding chỉ đọc được vài trăm token, và một
    vector cho cả trang sẽ "loãng" ý. Đoạn nhỏ → vector sắc nét hơn.

    Vì sao overlap? Một ý nằm vắt qua ranh giới hai chunk vẫn còn nguyên
    trong ít nhất một chunk.
    """
    step = size - overlap
    chunks = []
    for page, text in pages:
        for start in range(0, len(text), step):
            piece = text[start:start + size].strip()
            if piece:
                chunks.append(Chunk(piece, page))
            if start + size >= len(text):
                break
    return chunks


@lru_cache(maxsize=1)
def embedding_model():
    from fastembed import TextEmbedding

    return TextEmbedding(EMBED_MODEL)


def embed(texts: list[str]) -> np.ndarray:
    """
    Bước ③ — Embedding: mỗi đoạn text → một vector số.

    Hai đoạn có nghĩa gần nhau sẽ có vector gần nhau. Vector được chuẩn hoá
    về độ dài 1 để tích vô hướng (dot product) chính là cosine similarity.
    """
    vectors = np.array(list(embedding_model().embed(texts)), dtype=np.float32)
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


# Bước ④ — Vector DB: ở đây "index" chỉ là ma trận numpy (số chunk × số chiều).
# FAISS, Chroma, Qdrant... làm đúng việc này nhưng nhanh hơn với hàng triệu
# vector, lưu được xuống đĩa và lọc được theo metadata.


# ─── GENERATION ──────────────────────────────────────────────────────────────

def search(query_vec: np.ndarray, index: np.ndarray, k: int) -> list[tuple[int, float]]:
    """Bước ⑥ — Retrieval: lấy k chunk có cosine similarity cao nhất với câu hỏi."""
    scores = index @ query_vec
    top = np.argsort(-scores)[:k]
    return [(int(i), float(scores[i])) for i in top]


def build_prompt(question: str, chunks: list[Chunk]) -> str:
    """Bước ⑧ — Prompt: nhét các chunk tìm được vào prompt làm ngữ cảnh."""
    context = "\n\n".join(
        f"[NGUỒN {n} — trang {c.page}]\n{c.text}" for n, c in enumerate(chunks, start=1)
    )
    return (
        "Trả lời câu hỏi CHỈ dựa trên các nguồn dưới đây. "
        "Ghi [NGUỒN n] sau mỗi ý. Nếu nguồn không có thông tin, nói rõ là không biết.\n\n"
        f"{context}\n\nCâu hỏi: {question}\nTrả lời:"
    )


def generate(prompt: str, model: str) -> str | None:
    """Bước ⑨ — Generation: gửi prompt tới LLM (Ollama). Trả về None nếu không gọi được."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0}}).encode()
    request = urllib.request.Request(f"{base_url}/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.load(response)["response"]
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            print(f"  (Ollama chưa có model '{model}'. Chạy `ollama list` xem model đã tải,\n"
                  f"   rồi truyền tên đó: --llm <tên>, hoặc tải: `ollama pull {model}`)")
        else:
            print(f"  (Ollama báo lỗi: {exc})")
        return None
    except (urllib.error.URLError, OSError) as exc:
        print(f"  (Không gọi được Ollama tại {base_url}: {exc})")
        return None


# ─── CHẠY ────────────────────────────────────────────────────────────────────

def header(title: str) -> None:
    print(f"\n{'─' * 70}\n{title}\n{'─' * 70}")


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG tối giản để học.")
    parser.add_argument("--pdf", type=Path, default=ROOT / "data" / "test.pdf")
    parser.add_argument("--question", help="Câu hỏi. Bỏ trống để nhập khi chạy.")
    parser.add_argument("--chunk-size", type=int, default=800)
    parser.add_argument("--overlap", type=int, default=100)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--llm", default="qwen2.5:7b", help="Tên model Ollama.")
    args = parser.parse_args()
    if not 0 <= args.overlap < args.chunk_size:
        parser.error("--overlap phải >= 0 và nhỏ hơn --chunk-size")

    header(f"① LOAD  {args.pdf}")
    pages = load_pdf(args.pdf)
    if not pages:
        raise SystemExit("PDF không có text layer (ảnh scan?). Hãy dùng loader có OCR trong app.")
    print(f"{len(pages)} trang có chữ, {sum(len(t) for _, t in pages):,} ký tự")

    header(f"② CHUNK  size={args.chunk_size}, overlap={args.overlap}")
    chunks = split_into_chunks(pages, args.chunk_size, args.overlap)
    print(f"{len(chunks)} chunk. Chunk đầu tiên:\n  {chunks[0].text[:200]!r}...")

    header(f"③ EMBED + ④ INDEX  {EMBED_MODEL}")
    index = embed([c.text for c in chunks])
    print(f"Ma trận index: {index.shape}  (số chunk × số chiều vector)")
    print(f"Vector của chunk đầu, 5 số đầu: {np.round(index[0][:5], 3)}")

    question = args.question or input("\nNhập câu hỏi: ").strip()

    header(f"⑥ RETRIEVE  top-{args.top_k} cho: {question!r}")
    hits = search(embed([question])[0], index, args.top_k)
    for rank, (i, score) in enumerate(hits, start=1):
        print(f"  #{rank}  cosine={score:.3f}  trang {chunks[i].page}: {chunks[i].text[:90]!r}")

    header("⑧ PROMPT gửi cho LLM")
    prompt = build_prompt(question, [chunks[i] for i, _ in hits])
    print(prompt)

    header(f"⑨ GENERATE  ollama/{args.llm}")
    answer = generate(prompt, args.llm)
    print(answer if answer else "  Chưa có LLM — prompt ở trên chính là thứ RAG đưa cho LLM.")


if __name__ == "__main__":
    main()
