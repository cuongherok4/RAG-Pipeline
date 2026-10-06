# Tham khảo: các lựa chọn ở từng bước

Tra cứu khi đã nắm RAG cơ bản ([lộ trình học](learn/README.md)) và muốn biết mỗi
lựa chọn trong app khác nhau thế nào. Không cần đọc hết; tìm đúng bước đang xem.

Ký hiệu ⭐ là lựa chọn nên thử đầu tiên khi đã quen pipeline cơ bản.

```text
INDEXING (trang 1–4):    PDF → ① Loader → ② Chunking → ③ Embedding → ④ Vector DB
GENERATION (trang 5–9):  Câu hỏi → ⑤ Pre-retrieval → ⑥ Retrieval → ⑦ Post-retrieval → ⑧ Prompt → ⑨ LLM
```

Bước ⑤ và ⑦ là tuỳ chọn; mọi bước còn lại bắt buộc.

---

## ① Loader — PDF → text

| Strategy | Tốc độ | Bảng | Công thức | OCR | Khi nào dùng |
|----------|--------|------|-----------|-----|--------------|
| `pypdf` | Rất nhanh | ❌ | ❌ | ❌ | PDF text thuần, học và prototype |
| `pymupdf` | Rất nhanh | Cơ bản | ❌ | ❌ | PDF layout đơn giản |
| `pdfplumber` | Nhanh | Tốt | ❌ | ❌ | PDF nhiều bảng có lớp chữ |
| `marker` ⭐ | Chậm | Rất tốt | LaTeX | Surya | PDF phức tạp: bảng, công thức, hình |
| `docling` | Chậm | Rất tốt | ✅ | RapidOCR | Tài liệu học thuật, báo cáo |
| `unstructured` | Chậm | Rất tốt | ✅ | Tesseract | PDF scan |
| `opendataloader` | Nhanh | Rất tốt | ✅ | Ở mode `hybrid` | Cần Java 11+ |

- `pypdf`, `pymupdf`, `pdfplumber` trả **mỗi trang một document** nên giữ được số trang để
  trích dẫn. `marker`, `docling`, `opendataloader` trả **cả file thành một document Markdown**:
  giữ được heading và bảng, nhưng câu trả lời chỉ trích dẫn được tên file, không có số trang.
- PDF **không có lớp chữ** (ảnh scan, chữ bị outline hoá): ba loader đầu trả về
  **0 ký tự mà không báo lỗi**. Phải dùng loader có OCR.
- `opendataloader` có mode `fast` (mặc định, chỉ cần Java) và `hybrid` (chính xác hơn,
  cần chạy server `opendataloader-pdf-hybrid --port 5002`; app có nút bật server).
- **Trích xuất bảng** đổi bảng thành Markdown table. **Mô tả hình bằng VLM** gọi một
  vision model để mô tả biểu đồ thành text.

Kết quả ở tab **📄 Loader**: số document, tổng ký tự, preview từng trang.

## ② Chunking — cắt text thành đoạn

| Strategy | Cơ chế | Khi nào dùng |
|----------|--------|--------------|
| `recursive` | Cắt theo đoạn → dòng → câu → ký tự | Mặc định an toàn, dễ hiểu nhất |
| `format_aware` ⭐ | Cắt theo heading Markdown, code block, thẻ HTML | Khi loader ra Markdown thật (`marker`, `docling`) |
| `token_based` | Đếm token (tiktoken) thay vì ký tự | Khớp chính xác giới hạn token của model |
| `sentence_aware` | Ranh giới chunk là cuối câu (NLTK) | FAQ, văn bản câu ngắn |
| `semantic` | Cắt khi độ tương đồng giữa các câu giảm mạnh | Văn bản nhiều chủ đề |
| `hierarchical` | Cặp parent (lớn) + child (nhỏ) | Đi cùng retrieval `parent_document` |
| `contextual` | LLM viết thêm một câu ngữ cảnh vào đầu mỗi chunk | Đi cùng retrieval `contextual`, tốn LLM |

- `format_aware` gặp **text thuần** (output của `pypdf`/`pymupdf`/`pdfplumber`) thì
  tự lùi về `recursive`, nên kết quả y hệt nhau.
- Mặc định `split_large_sections=False`: một section dài vẫn là **một chunk** bất kể
  chunk size. Bật lên nếu model embedding có context ngắn.
- **Chunk size** thường 500–1500 ký tự; **overlap** 10–15% chunk size.

Kết quả ở tab **✂️ Chunking**: histogram độ dài chunk, preview từng chunk kèm metadata.

## ③ Embedding — text → vector

| Provider | Model ví dụ | Tiếng Việt | Cần gì |
|----------|-------------|------------|--------|
| `fastembed` ⭐ | `paraphrase-multilingual-MiniLM-L12-v2` (mặc định) | Khá | Không gì cả, chạy CPU. Hai model `bge-*-en` chỉ hiểu tiếng Anh |
| `huggingface` | `BAAI/bge-m3` | Tốt | Nên có GPU |
| `ollama` | `bge-m3` | Tốt | Ollama đang chạy |
| `openai` | `text-embedding-3-small` | Tốt | `OPENAI_API_KEY` |
| `cohere` | `embed-multilingual-v3.0` | Tốt | `COHERE_API_KEY` |

- **Sparse embedding** (BM25 hoặc SPLADE): bật lúc indexing để dùng được retrieval
  `sparse` và `hybrid` ở bước ⑥. BM25 không cần GPU; SPLADE cần `transformers` + `torch`.
- **MRL**: một số model (OpenAI `text-embedding-3-*`…) cho phép cắt ngắn vector
  (1536 → 512 chiều) mà mất ít chất lượng, đổi lại tốn ít bộ nhớ hơn.
- Đổi model embedding thì **phải index lại**: vector của hai model khác nhau không so sánh được.

Kết quả ở tab **🧮 Embedding**: kích thước ma trận, heatmap cosine similarity giữa các chunk.

## ④ Vector DB — lưu và tìm vector

| Provider | Chạy ở đâu | Khi nào dùng |
|----------|-----------|--------------|
| `faiss` ⭐ | Local, trong process | Học, prototype |
| `chroma` | Local | Học, demo nhỏ |
| `lancedb` | Local / cloud | Dữ liệu dạng cột, lớn hơn |
| `qdrant` | Server (Docker) / cloud | Production, lọc metadata phức tạp |
| `weaviate` | Server / cloud | Hybrid search tích hợp sẵn |
| `pgvector` | PostgreSQL | Đã có hạ tầng Postgres |
| `pinecone` | Cloud | Không muốn tự vận hành |

Bốn provider cuối cần server hoặc tài khoản; URL và key đặt trong `.env`
(xem `.env.example`). Khi học, chọn `faiss` hoặc `chroma`.

---

## ⑤ Pre-retrieval — biến đổi câu hỏi *(tuỳ chọn)*

| Strategy | Cơ chế | Khi nào dùng |
|----------|--------|--------------|
| `none` ⭐ | Giữ nguyên câu hỏi | Câu hỏi đã rõ |
| `rewrite` | LLM viết lại cho rõ, sửa chính tả | Câu hỏi ngắn, thiếu ngữ cảnh |
| `expand` | Thêm từ đồng nghĩa, thuật ngữ liên quan | Tài liệu dùng nhiều cách gọi khác nhau |
| `hyde` | LLM viết một câu trả lời giả định rồi tìm bằng câu trả lời đó | Câu hỏi và tài liệu diễn đạt rất khác nhau |
| `step_back` | Tổng quát hoá câu hỏi để lấy kiến thức nền | Câu hỏi quá hẹp |
| `multi_query` | Sinh N biến thể câu hỏi, gộp kết quả | Câu hỏi nhiều cách hiểu |
| `decompose` | Tách thành các câu hỏi con | Câu hỏi nhiều ý |
| `self_query` | Rút điều kiện lọc metadata từ câu hỏi | Tài liệu có metadata phong phú |
| `route` | Phân loại câu hỏi rồi chọn strategy | Kho tài liệu nhiều chủ đề |

Mọi strategy trừ `none` đều gọi LLM, nên chậm hơn và tốn thêm chi phí.

## ⑥ Retrieval — tìm chunk liên quan

| Strategy | Cơ chế | Khi nào dùng |
|----------|--------|--------------|
| `dense` ⭐ | Cosine similarity giữa vector câu hỏi và chunk | Bắt đầu ở đây |
| `sparse` | BM25 / SPLADE, khớp từ khoá | Tên riêng, mã số, số liệu |
| `hybrid` | Trộn dense + sparse (RRF / weighted / DBSF) | Thường tốt nhất thực tế; cần bật sparse ở ③ |
| `multi_query` | N biến thể câu hỏi, gộp bằng RRF | Câu hỏi mơ hồ |
| `parent_document` | Tìm trên child chunk, trả về parent | Đi cùng chunking `hierarchical` |
| `sentence_window` | Mở rộng ±N câu quanh câu khớp | Văn xuôi liên tục |
| `multi_hop` | Tìm → LLM đặt câu hỏi tiếp → tìm tiếp | Câu hỏi cần suy luận nhiều bước |
| `contextual` | Tìm trên chunk đã có câu ngữ cảnh | Đi cùng chunking `contextual` |

**Top-K**: số chunk lấy về. Không có reranker thì 4–5; có reranker thì 10–20 rồi
để reranker lọc còn Top-N.

## ⑦ Post-retrieval — chấm lại, lọc, sắp xếp *(tuỳ chọn)*

**Reranker** đọc từng cặp (câu hỏi, chunk) và chấm lại điểm:

| Reranker | Ghi chú |
|----------|---------|
| `none` | Giữ thứ hạng của retrieval |
| `cross_encoder` ⭐ | `BAAI/bge-reranker-v2-m3`, đa ngôn ngữ, chạy local |
| `cohere` | API, cần `COHERE_API_KEY` |
| `llm` | Dùng LLM sắp hạng, không cần model riêng |

**Bộ lọc** (chạy độc lập với reranker):

| Bộ lọc | Tác dụng |
|--------|----------|
| Metadata filter | Lọc cứng theo nguồn, trang… trước mọi bước khác |
| Redundancy filter | Bỏ chunk gần trùng nhau |
| MMR | Cân bằng giữa liên quan và đa dạng |
| LLM filter | LLM trả lời YES/NO cho từng chunk |
| Compression | LLM chỉ giữ phần liên quan trong mỗi chunk |

**Thứ tự context**: `sandwich` đặt chunk tốt nhất ở đầu và cuối để giảm hiện tượng
*lost in the middle*; `relevance` giảm dần theo điểm; `original` giữ thứ tự retrieval.

**Top-N**: số chunk giữ lại để đưa vào prompt, thường 3–8.

## ⑧ Prompt

| Template | Output | Khi nào dùng |
|----------|--------|--------------|
| `citation` ⭐ | Câu trả lời kèm `[NGUỒN n]` | Muốn kiểm tra từng ý lấy từ đâu |
| `basic` | Text thuần | Đơn giản nhất |
| `conversational` | Kèm lịch sử hội thoại | Hỏi tiếp nối |
| `structured` | JSON: answer, claims, sources, confidence | Code phía sau cần parse |

Tuỳ chọn: ngôn ngữ prompt (`vi` / `en` / `both`), giới hạn số ký tự context,
thêm quy tắc riêng vào system prompt.

## ⑨ Generation

| Provider | Cần gì | Ghi chú |
|----------|--------|---------|
| `ollama` | Ollama đang chạy | Miễn phí, offline. Máy yếu: `qwen2.5:3b`; RAM ≥ 16 GB: `qwen2.5:7b` |
| `openai` | `OPENAI_API_KEY` | `gpt-4.1-mini` là lựa chọn cân bằng |
| `anthropic` | `ANTHROPIC_API_KEY` | |
| `google` | `GOOGLE_API_KEY` | Có free tier |
| `cohere` | `COHERE_API_KEY` | |

**Temperature** để `0` cho RAG: muốn câu trả lời bám sát nguồn, không cần sáng tạo.

---

## Ví dụ cấu hình cho PDF phức tạp

Khi đã chạy thành thạo cấu hình cơ bản và muốn xử lý PDF có bảng, công thức:

| Bước | Chọn | Lý do |
|------|------|-------|
| ① | `marker` | Ra Markdown giữ bảng và công thức |
| ② | `format_aware`, size 1000, overlap 150 | Cắt theo heading của Markdown |
| ③ | `openai` `text-embedding-3-small` + BM25 | Bật sparse để dùng hybrid |
| ④ | `faiss` hoặc `chroma` | Không cần server |
| ⑤ | `rewrite` | Làm rõ câu hỏi, tốn ít |
| ⑥ | `hybrid`, Top-K 15 | Dense + từ khoá |
| ⑦ | `cross_encoder`, Top-N 5, redundancy filter, `sandwich` | Lấy rộng rồi lọc kỹ |
| ⑧ | `citation` | Kiểm tra được nguồn |
| ⑨ | `gpt-4.1-mini`, temperature 0 | |

Đổi **từng thứ một** và so sánh kết quả, như [bài 8](learn/08-advanced.md) hướng dẫn.
