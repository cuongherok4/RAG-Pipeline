# Hướng dẫn chạy RAG-Pipeline

Làm lần lượt từ trên xuống. Lần đầu mất khoảng 15–30 phút, phần lớn là thời gian tải thư viện.

| Bước | Việc | Bắt buộc? |
|------|------|-----------|
| 1 | [Cài môi trường](#1-cài-môi-trường) | ✅ |
| 2 | [Kiểm tra môi trường](#2-kiểm-tra-môi-trường) | ✅ |
| 3 | [Chọn LLM để sinh câu trả lời](#3-chọn-llm) | Chỉ cần cho bước ⑨ |
| 4 | [Chạy script học tối giản](#4-chạy-script-học-tối-giản) | Nên làm |
| 5 | [Chạy app](#5-chạy-app) | ✅ |
| 6 | [Dùng app lần đầu](#6-dùng-app-lần-đầu) | — |
| — | [Gặp lỗi?](#gặp-lỗi) | — |
| — | [Phụ lục: GPU, thư viện tuỳ chọn, provider khác](#phụ-lục) | Khi cần |

**Yêu cầu:** Windows 10+, macOS hoặc Linux; khoảng 10 GB ổ trống; có Internet lúc cài.
Không cần cài Python trước, `uv` sẽ tự tải Python 3.11. GPU không bắt buộc.

---

## 1. Cài môi trường

Mở terminal **tại thư mục project** (thư mục chứa `app.py`).

### Windows (PowerShell)

Chạy một lệnh là xong:

```powershell
.\scripts\setup.ps1
```

Nếu PowerShell báo *running scripts is disabled*, chạy lệnh này trước rồi thử lại:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### macOS / Linux

```bash
# 1. Cài uv (một lần cho cả máy). Mở terminal mới sau khi cài.
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Tạo .venv với Python 3.11 (uv tự tải Python nếu chưa có)
uv venv --python 3.11

# 3. Cài thư viện theo lockfile (bước lâu nhất: 5–20 phút)
uv pip install -r requirements.lock.txt

# 4. (Tuỳ chọn) Cài torch đúng với GPU của máy
.venv/bin/python scripts/install_torch.py --apply
```

> Bạn không cần activate `.venv`. Mọi lệnh trong file này đều chạy qua `uv run`,
> lệnh này tự dùng đúng `.venv` của project.

---

## 2. Kiểm tra môi trường

```bash
uv run python --version                            # → Python 3.11.x
uv pip check                                       # → All installed packages are compatible
uv run python -m unittest discover -s tests -v     # → OK (vài giây, không tải model)
uv run python scripts/smoke_test.py --pdf data/test.pdf --mode single --offline
```

Unit test kiểm tra logic, không cần model hay API key. Smoke test chạy thật bước ①–④
trên `data/test.pdf`; bảng **TỔNG KẾT** cuối cùng có `FAIL 0` là đạt.

> ⏱️ Smoke test mất **1–3 phút**. Lần đầu, hoặc khi đã cài thư viện tuỳ chọn (docling,
> marker…), lệnh có thể chạy **5–10 phút** vì phải tải model và import thư viện nặng.
> Terminal vẫn đang in log là lệnh vẫn đang chạy, không phải bị treo. Cách đọc `SKIP` và
các dòng log xen giữa: xem [README → Kiểm thử](README.md#kiểm-thử).

---

## 3. Chọn LLM

Với cấu hình cơ bản ở mục 6, chỉ bước ⑨ (LLM viết câu trả lời) cần LLM; các bước
khác chạy trên máy, không cần API key. (Một số lựa chọn nâng cao như pre-retrieval,
LLM reranker, embedding OpenAI cũng gọi LLM hoặc cần key.) Chọn **một** trong hai cách:

### Cách A: OpenAI (chất lượng tốt, trả phí theo lượt dùng)

1. Tạo key tại https://platform.openai.com/api-keys và **nạp credit** tại
   https://platform.openai.com/settings/organization/billing. Có key mà tài khoản
   hết tiền thì vẫn không gọi được.
2. Tạo file `.env` từ file mẫu:
   ```bash
   cp .env.example .env            # Windows: copy .env.example .env
   ```
3. Mở `.env` và dán key vào, **không thêm dấu cách hay dấu ngoặc**:
   ```
   OPENAI_API_KEY=sk-proj-...
   ```
   Key OpenAI luôn bắt đầu bằng `sk-`.

Kiểm tra key đúng chưa (lệnh này miễn phí):

```bash
uv run python -c "from openai import OpenAI; from dotenv import load_dotenv; load_dotenv('.env'); OpenAI().models.list(); print('Key OK')"
```

### Cách B: Ollama (miễn phí, chạy trên máy bạn)

1. Cài Ollama: https://ollama.com/download
2. Tải một model. Chọn theo bộ nhớ của máy:
   ```bash
   ollama pull qwen2.5:3b     # máy yếu / GPU ≤ 4 GB — nhẹ, tiếng Việt tạm ổn
   ollama pull qwen2.5:7b     # RAM ≥ 16 GB — trả lời tốt hơn
   ```
3. Ollama tự chạy nền sau khi cài. Kiểm tra: mở http://localhost:11434, trang
   phải hiện *Ollama is running*.

---

## 4. Chạy script học tối giản

Toàn bộ RAG nằm trong một file, không cần API key. Nên chạy script này trước khi mở app
để hiểu từng bước:

```bash
uv run python learn/01_minimal_rag.py --question "Mô hình được đánh giá trên tập dữ liệu nào?"
```

Script in ra kết quả từng bước (đánh số ①–⑨ giống app): text đọc được, các chunk,
vector, các đoạn tìm được kèm điểm, và prompt gửi cho LLM. Nếu Ollama đang chạy, cuối
cùng sẽ có câu trả lời thật. Script mặc định gọi `qwen2.5:7b`; nếu bạn tải model khác
ở mục 3, thêm `--llm qwen2.5:3b` (hoặc tên model của bạn).
Dùng PDF của bạn: thêm `--pdf đường/dẫn/file.pdf`. Lần đầu script tải model embedding
(khoảng 220 MB).

Sau đó đọc tiếp [lộ trình học](docs/learn/README.md).

---

## 5. Chạy app

```bash
uv run streamlit run app.py
```

Trình duyệt tự mở **http://localhost:8501**. Để tắt app, bấm `Ctrl+C` trong terminal.

> Sửa code trong `ui/`, `core/`… thì phải **tắt app và chạy lại** mới thấy thay đổi.
> Riêng thay đổi trong `app.py` chỉ cần tải lại trang.

---

## 6. Dùng app lần đầu

App có 3 trang ở thanh bên trái: **Bắt đầu**, **1–4 · Chuẩn bị tài liệu** và **5–9 · Hỏi đáp**.

### Tài liệu mẫu

Bạn có thể dùng `data/test.pdf` có sẵn (bài báo Faster R-CNN, 10 trang), hoặc tải bài báo gốc
về RAG. Dùng bài này để học RAG là hợp nhất, vì hỏi đáp xong là hiểu luôn RAG:

```bash
curl -L -o data/rag_paper.pdf https://arxiv.org/pdf/2005.11401
```

Câu hỏi thử với `rag_paper.pdf`:

| Câu hỏi | Điều quan sát được |
|---------|--------------------|
| *Retriever trong RAG dùng mô hình gì?* | Top-2 chứa đáp án (DPR). Hỏi tiếng Việt vẫn tìm được trong tài liệu tiếng Anh |
| *What is the difference between RAG-Sequence and RAG-Token?* | Hỏi cùng ngôn ngữ với tài liệu cho điểm cosine cao hơn hẳn (~0.77 so với ~0.6) |
| *Bộ dữ liệu Natural Questions đạt kết quả bao nhiêu?* | Dense tìm **kém** với câu hỏi về số liệu. Thử lại với retrieval `hybrid` để thấy khác biệt |

**Trang 1–4 · Chuẩn bị tài liệu**

1. Upload một file PDF có chữ chọn được (không phải ảnh scan), ví dụ `data/rag_paper.pdf`.
2. Chọn cấu hình cơ bản:

   | Bước | Chọn |
   |------|------|
   | ① Loader | `pypdf` |
   | ② Chunking | `recursive`, size `800`, overlap `100` |
   | ③ Embedding | `fastembed`, giữ model mặc định |
   | ④ Vector DB | `faiss` |

3. Bấm **▶️ Process**, rồi xem kết quả ở 4 tab ngay bên dưới.

**Trang 5–9 · Hỏi đáp**

1. Tắt ⑤ Pre-retrieval và ⑦ Post-retrieval.
2. ⑥ Retrieval: `dense`, Top-K `4`. ⑧ Prompt: `citation`.
3. ⑨ Generation: `openai` / `gpt-4.1-mini` hoặc `ollama` / `qwen2.5:3b`, temperature `0`.
4. Nhập một câu hỏi **cụ thể** về tài liệu và chạy. Đọc các đoạn tìm được ở bước ⑥
   *trước khi* đọc câu trả lời.

---

## Gặp lỗi?

| Triệu chứng | Nguyên nhân | Cách sửa |
|-------------|-------------|----------|
| `uv: command not found` | Terminal chưa nhận PATH mới | Mở terminal mới, hoặc gọi thẳng `~/.local/bin/uv` |
| `.venv/bin/python: No such file` dù đã có `.venv` | Python gốc của venv đã bị xoá (ví dụ nằm trong `/tmp`) | `uv venv --python 3.11 --clear` rồi cài lại bước 1 |
| `No solution found … pywin32` | Lockfile cũ sinh trên Windows | Kéo code mới nhất (lockfile đã có marker `sys_platform == "win32"`) |
| `401 Unauthorized` / `invalid_api_key` | Key sai: gõ thừa hoặc thiếu ký tự, có dấu cách | Mở `.env`, kiểm tra key bắt đầu bằng `sk-`, rồi chạy lại lệnh kiểm tra ở mục 3 |
| `429 insufficient_quota` / `no credits remaining` | Key đúng nhưng tài khoản hết tiền | Nạp credit, hoặc chuyển sang Ollama |
| `Cannot find Root object in pdf` | File PDF hỏng (thường do bị lưu như file text) | Lấy lại file gốc; với file trong repo: `git checkout data/test.pdf` |
| Loader trả về **0 ký tự** | PDF là ảnh scan, không có lớp chữ | Dùng loader có OCR: `marker`, `docling`, `unstructured` |
| `CUDA out of memory` | GPU không đủ VRAM cho marker/docling | Dùng `pypdf`, hoặc chạy trên CPU |
| `Port 8501 is already in use` | App cũ vẫn đang chạy | Tắt terminal cũ, hoặc `uv run streamlit run app.py --server.port 8502` |
| Sửa code nhưng giao diện không đổi | Streamlit chưa nạp lại module | Tắt app (`Ctrl+C`) rồi chạy lại |
| `Failed to send telemetry event` | Cảnh báo của Chroma | Vô hại, bỏ qua |
| Lỗi import lạ, `TypeError` khó hiểu | Đang chạy nhầm môi trường (conda, Python 3.13…) | Luôn chạy qua `uv run`; kiểm tra `uv run python --version` ra 3.11 |

---

## Phụ lục

Chỉ đọc khi cần dùng một option ngoài cấu hình cơ bản.

### Phiên bản Python

Dùng **3.11** (hỗ trợ 3.10–3.12). **Không dùng 3.13**: `chromadb`, `faiss-cpu`, `numpy`
bản đang khoá chưa có wheel cho 3.13 nên cài sẽ hỏng giữa chừng. `uv venv --python 3.11`
ở mục 1 đã tự lo việc này.

### Thư viện tuỳ chọn

`requirements-extra.txt` chia theo nhóm: loader nâng cao (`marker-pdf`, `docling`,
`unstructured`, `opendataloader-pdf`), provider khác, vector DB cần server
(`qdrant-client`, `lancedb`, `weaviate-client`, `psycopg`, `pinecone`), tiếng Việt và
SPLADE. Hiện file **đang bật sẵn** nhóm loader nâng cao và `underthesea` (tải nhiều GB);
các nhóm còn lại đang bị comment. Trước khi chạy `uv pip install -r requirements-extra.txt`,
comment những dòng không dùng và bỏ comment những dòng cần. Option thiếu thư viện sẽ hiện
`SKIP` trong smoke test và bị khoá trong app.

### Phụ thuộc hệ thống (pip không cài được)

| Cần | Cho option | Kiểm tra |
|-----|-----------|----------|
| Java 11+ | loader `opendataloader` | `java -version` |
| poppler + tesseract | loader `unstructured` | `tesseract --version` |
| Ollama | embedding / generation local | `ollama list` |
| NLTK `punkt_tab` | chunking `sentence_aware` | tự lùi về cách khác nếu thiếu |

### GPU

Không bắt buộc. GPU NVIDIA chỉ làm nhanh embedding HuggingFace, cross-encoder reranker,
`marker` và SPLADE. Script dưới đây đọc `nvidia-smi` rồi cài đúng bản `torch`:

```bash
uv run python scripts/install_torch.py --check              # xem đang cài bản nào
uv run python scripts/install_torch.py --apply              # tự dò và cài
uv run python scripts/install_torch.py --apply --force-cpu  # ép bản CPU (nhẹ hơn ~2 GB)
```

### API key của provider khác

Mọi key đều đặt trong `.env`; danh sách đầy đủ có trong `.env.example`. Ngoài OpenAI:
`ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `COHERE_API_KEY`, `HF_TOKEN` (model HuggingFace
cần xin quyền), và URL/key của các vector DB chạy server. Không bao giờ commit file `.env`
(đã có trong `.gitignore`).
