<p align="center">
  <h1 align="center">🔬 RAG-Pipeline</h1>
</p>

<p align="center">
  <b>RAG-Pipeline</b> là ứng dụng giúp bạn xây dựng, cấu hình và <b>trực quan hóa từng bước</b> trong pipeline RAG (Retrieval-Augmented Generation) - từ bước load tài liệu PDF đến bước sinh câu trả lời từ LLM.
</p>

---

<p align="center">
  <a href="https://www.youtube.com/watch?v=YPcXqbcZqaE">
    <img src="https://img.youtube.com/vi/YPcXqbcZqaE/maxresdefault.jpg" width=800>
  </a><br/>
  <i>▶️ Indexing Pipeline — Load · Chunk · Embed · Store</i>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=2THKb3pnFIk">
    <img src="https://img.youtube.com/vi/2THKb3pnFIk/maxresdefault.jpg" width=800>
  </a><br/>
  <i>▶️ Generation Pipeline — Retrieve · Rerank · Prompt · Generate</i>
</p>

> **Mục tiêu:** hiểu RAG bằng cách **nhìn tận mắt** kết quả của từng bước, và thấy
> mỗi lựa chọn cấu hình (chunking, embedding, retrieval…) thay đổi câu trả lời ra sao.

---

## RAG trong 30 giây

LLM không biết gì về tài liệu của bạn. RAG (Retrieval-Augmented Generation) giải
quyết bằng cách **tìm vài đoạn liên quan nhất trong tài liệu rồi đưa kèm vào prompt**.

```text
INDEXING (một lần):    PDF → ① Loader → ② Chunking → ③ Embedding → ④ Vector DB
GENERATION (mỗi câu):  Câu hỏi → ⑤ Pre-retrieval → ⑥ Retrieval → ⑦ Post-retrieval → ⑧ Prompt → ⑨ LLM
```

Bước ⑤ và ⑦ là tuỳ chọn. Khi câu trả lời sai, lỗi hầu như luôn thuộc một trong hai
nhóm: **tìm sai** (đoạn chứa đáp án không được lấy về) hoặc **đọc sai** (LLM có đoạn
đúng nhưng hiểu sai). App hiện kết quả từng bước để bạn biết lỗi nằm ở nhóm nào.

## Bắt đầu: làm theo thứ tự này

| # | Việc | Ở đâu | Thời gian |
|---|------|-------|-----------|
| 1 | Cài môi trường | [SETUP.md](SETUP.md) mục 1–2 | 15–30 phút |
| 2 | Chạy test để chắc môi trường đúng | [Kiểm thử](#kiểm-thử) bên dưới | 2–5 phút |
| 3 | Hiểu RAG là gì | [Bài 0](docs/learn/00-what-is-rag.md) | 10 phút |
| 4 | Đọc rồi chạy RAG tối giản trong một file | [`learn/01_minimal_rag.py`](learn/01_minimal_rag.py) | 20 phút |
| 5 | Học từng bước, mỗi bài có bài tập làm trong app | [Lộ trình học](docs/learn/README.md) | 10–20 phút/bài |
| 6 | Tra cứu các lựa chọn khi cần | [Tham khảo từng bước](docs/options-reference.md) | — |

Việc 4 là quan trọng nhất. Script dài khoảng 200 dòng, không framework, không cần
API key, và in ra kết quả của mọi bước:

```bash
uv run python learn/01_minimal_rag.py --question "Mô hình được đánh giá trên tập dữ liệu nào?"
```

App Streamlit chỉ là phiên bản **nhiều lựa chọn hơn** của chính các hàm trong script đó.
Đừng mở app trước khi chạy script: app có hàng chục lựa chọn mỗi bước và rất dễ ngợp.

```bash
uv run streamlit run app.py      # mở http://localhost:8501
```

## Kiểm thử

Có ba mức, từ nhanh đến đầy đủ:

```bash
# 1. Unit test: vài giây, không tải model, không cần API key.
#    Đọc tên test như ghi chú bài học: test_minimal_rag.py (chunking, retrieval, prompt),
#    test_pipeline_cache.py (vì sao đổi một bước chỉ chạy lại các bước sau).
uv run python -m unittest discover -s tests -v

# 2. Smoke test: chạy thật bước ①–④ với data/test.pdf, chỉ dùng option offline.
uv run python scripts/smoke_test.py --pdf data/test.pdf --mode single --offline

# 3. End-to-end: chạy script tối giản (tải model embedding ~220 MB ở lần đầu).
uv run python learn/01_minimal_rag.py --question "Mô hình được đánh giá trên tập dữ liệu nào?"
```

Cách đọc kết quả smoke test:

- Chỉ cần nhìn bảng **TỔNG KẾT** ở cuối: `FAIL 0` là đạt. Bảng đầy đủ được ghi vào
  `smoke_report.md`.
- `SKIP` nghĩa là thiếu thư viện tuỳ chọn, API key hoặc công cụ hệ thống; option đó
  **chưa được kiểm thử**, không phải đã chạy đúng.
- Log `INFO`/`WARNING` xen giữa (ví dụ của loader `opendataloader` chạy bằng Java) là
  log của thư viện, không phải lỗi.
- Lần đầu chạy lâu hơn (5 phút trở lên) vì phải tải model; các lần sau khoảng 1 phút.

Thêm `--mode pairs` để test cặp bước liền kề.

## Code nằm ở đâu

Mỗi bước của pipeline là một thư mục. Trong mỗi thư mục, `base.py` là giao diện
chung, `factory.py` liệt kê mọi lựa chọn, còn mỗi file khác là một kỹ thuật.

| Bước | Thư mục | Nên đọc trước |
|------|---------|---------------|
| ① Loader | `loader/` | `pdf_loader.py` |
| ② Chunking | `chunking/` | `recursive.py` |
| ③ Embedding | `embedding/` | `fastembed_embedder.py` |
| ④ Vector DB | `vector_db/` | `faiss_store.py` |
| ⑤ Pre-retrieval | `pre_retrieval/` | `query_rewriter.py` |
| ⑥ Retrieval | `retrieval/` | `dense.py`, `hybrid.py` |
| ⑦ Post-retrieval | `post_retrieval/` | `cross_encoder_reranker.py` |
| ⑧ Prompt | `prompt/` | `citation.py` |
| ⑨ Generation | `generation/` | `ollama_generator.py` |

Phần còn lại: `app.py` và `ui/` là giao diện; `pipeline/` chạy cả pipeline bằng code
(không cần UI); `core/` và `pipeline_cache.py` lo điều phối và cache. Cách các phần
nối với nhau, cache hoạt động thế nào, `config.yaml` dùng khi nào:
[docs/architecture.md](docs/architecture.md).

## Bảo mật API key

Key thật chỉ để trong file `.env` ở máy bạn (tạo bằng `cp .env.example .env`); file này đã
nằm trong `.gitignore` nên không bị đẩy lên GitHub. Repo có sẵn hook chặn lộ key — cài một
lần sau khi clone:

```bash
pip install pre-commit && pre-commit install
```

Từ đó mỗi lần `git commit`, [gitleaks](https://github.com/gitleaks/gitleaks) sẽ quét và
chặn commit nếu phát hiện key, private key hoặc file `.env`. Hook `ruff` cũng chặn
lỗi Python chắc chắn sai (gọi tên chưa định nghĩa, import thừa).

## Tác giả

**cuongherok4** — [github.com/cuongherok4](https://github.com/cuongherok4)

## Giấy phép

[MIT](LICENSE): ai cũng được xem, tải về, dùng, sửa và chia sẻ lại, kể cả cho mục đích
thương mại, miễn là giữ lại thông tin bản quyền trong file `LICENSE`.
