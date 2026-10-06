# Bài 3 — Chunking: cắt text thành đoạn

## Vấn đề

Không embed nguyên cả trang hay cả tài liệu được, vì:

- Model embedding chỉ đọc được vài trăm token; phần thừa bị **cắt bỏ âm thầm**.
- Một vector cho cả trang chứa nhiều ý → "trung bình" hết các ý → tìm kiếm kém chính xác.
- Chunk càng to, prompt càng dài và tốn tiền.

Nhưng chunk quá nhỏ thì mất ngữ cảnh ("Nó tăng 20%" — *nó* là gì?).

## Hai tham số quan trọng nhất

- **chunk size**: độ dài tối đa mỗi chunk. Thường 500–1500 ký tự.
- **overlap**: phần chồng lấp giữa hai chunk liền nhau, thường 10–15% chunk size,
  để một câu nằm vắt qua ranh giới vẫn còn nguyên trong ít nhất một chunk.

## Trong script tối giản

`split_into_chunks()` cắt theo số ký tự cố định — cách đơn giản nhất, có thể
cắt ngang giữa câu. Chạy thử:

```bash
uv run python learn/01_minimal_rag.py --chunk-size 300 --overlap 0 --question "..."
uv run python learn/01_minimal_rag.py --chunk-size 1500 --overlap 200 --question "..."
```

So sánh số chunk ở bước **② CHUNK** và các chunk tìm được ở bước **⑥ RETRIEVE**.

## Thử trong app

1. Chọn `recursive`, size 800, overlap 100. Xem histogram ở tab **✂️ Chunking**.
2. Đổi size thành 200 rồi 2000. Số chunk thay đổi thế nào? Đọc vài chunk — chunk
   nào còn đọc hiểu được khi đứng một mình?
3. `recursive` khác script tối giản ở chỗ nó ưu tiên cắt ở ranh giới đoạn → dòng
   → câu trước khi buộc phải cắt giữa chữ. Tìm một chunk để thấy điều đó.

## Đọc code

- `chunking/recursive.py` — nên đọc đầu tiên
- `chunking/factory.py` — danh sách mọi chiến lược và tham số

Các chiến lược khác (`semantic`, `hierarchical`, `contextual`...) là **nâng cao** —
để sau bài 8.
