# Bài 5 — Vector DB: lưu và tìm vector

## Vấn đề

Script tối giản lưu vector trong một ma trận numpy và so câu hỏi với **từng**
chunk. Với vài trăm chunk thì tốt. Với 10 triệu chunk thì chậm, không lưu được
xuống đĩa, không lọc được theo metadata ("chỉ tìm trong tài liệu năm 2024").

## Vector DB giải quyết gì

- **Tìm gần đúng nhanh** (ANN — Approximate Nearest Neighbor): dùng cấu trúc
  index (HNSW, IVF...) để không phải so với mọi vector. Đổi một chút độ chính
  xác lấy tốc độ gấp hàng trăm lần.
- **Lưu bền** xuống đĩa / server.
- **Lọc metadata** kết hợp với tìm vector.

## Chọn cái nào khi học?

| Nhu cầu | Chọn |
|---------|------|
| Học, thử nghiệm | `faiss` hoặc `chroma` — chạy local, không cần server |
| Production nhỏ, đã có PostgreSQL | `pgvector` |
| Production lớn | `qdrant`, `weaviate`, `pinecone` |

Với người mới: **vector DB là phần ít ảnh hưởng tới chất lượng câu trả lời nhất.**
Loader, chunking, embedding quan trọng hơn nhiều. Đừng tốn thời gian so sánh DB lúc này.

## Đọc code

- `vector_db/faiss_store.py` — đơn giản nhất
- `vector_db/base.py` — giao diện chung: thêm tài liệu, tìm kiếm, lưu/tải
