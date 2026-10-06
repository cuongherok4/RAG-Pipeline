# Lộ trình học RAG

Dành cho người **chưa từng làm RAG**. Đi theo thứ tự, mỗi bài 10–20 phút.

| # | Bài | Bạn sẽ hiểu |
|---|-----|-------------|
| 0 | [RAG là gì?](00-what-is-rag.md) | Vì sao LLM cần RAG, hai giai đoạn indexing / generation |
| 1 | [Chạy RAG tối giản](../../learn/01_minimal_rag.py) | Đọc và chạy một file ~200 dòng chứa đủ mọi bước |
| 2 | [Loader](02-loader.md) | Đưa PDF thành text — và vì sao có lúc ra 0 ký tự |
| 3 | [Chunking](03-chunking.md) | Cắt text thế nào, chunk size / overlap ảnh hưởng gì |
| 4 | [Embedding](04-embedding.md) | Text → vector, "gần nhau về nghĩa" nghĩa là gì |
| 5 | [Vector DB](05-vector-db.md) | Lưu và tìm vector nhanh |
| 6 | [Retrieval](06-retrieval.md) | Dense, sparse (BM25), hybrid |
| 7 | [Prompt & Generation](07-prompt-generation.md) | Nhét context vào prompt, giảm bịa, trích dẫn nguồn |
| 8 | [Kỹ thuật nâng cao](08-advanced.md) | Pre-retrieval, reranking, và khi nào mới cần |

## Cách học hiệu quả

1. **Đọc bài 0, rồi chạy script tối giản** trước khi mở app:
   ```bash
   uv run python learn/01_minimal_rag.py --question "Tài liệu này nói về gì?"
   ```
   Không cần API key. Có [Ollama](https://ollama.com) thì có câu trả lời thật;
   không có thì script in ra prompt — vẫn đủ để hiểu.
2. **Mỗi bài từ 2 → 7**: đọc phần giải thích, tìm hàm tương ứng trong script
   tối giản, rồi làm phần *Thử trong app* — đổi **một** tham số và quan sát.
3. **Chỉ học bài 8 khi đã thấy RAG cơ bản trả lời sai** ở đâu. Kỹ thuật nâng
   cao là để sửa một lỗi cụ thể, không phải để bật hết cho "xịn".

## Cấu hình "cơ bản" để bắt đầu trong app

Chạy app bằng `uv run streamlit run app.py` (cài đặt: [SETUP.md](../../SETUP.md)),
rồi chọn đúng các giá trị dưới đây. Mọi thứ khác để mặc định hoặc tắt.

| Bước | Chọn | Vì sao |
|------|------|--------|
| Loader | `pypdf` | Nhanh, không cần cài thêm |
| Chunking | `recursive`, size `800`, overlap `100` | Dễ hiểu nhất |
| Embedding | `fastembed` (model mặc định) | Chạy CPU, miễn phí, không cần key; cùng model với script tối giản |
| Vector DB | `faiss` | Local, không cần server |
| Pre-retrieval | tắt | — |
| Retrieval | `dense`, Top-K `4` | Giống hệt script tối giản |
| Post-retrieval | tắt | — |
| Prompt | `citation` | Thấy câu trả lời lấy từ chunk nào |
| Generation | `ollama` (local) hoặc provider bạn có key | — |
