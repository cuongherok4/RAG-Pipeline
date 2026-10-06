# Bài 8 — Kỹ thuật nâng cao: khi nào mới cần

**Nguyên tắc:** chỉ thêm một kỹ thuật khi bạn **thấy được lỗi cụ thể** nó sửa.
Bật tất cả cùng lúc làm pipeline chậm, tốn tiền, và bạn không biết cái nào có tác dụng.

Hãy chuẩn bị 5–10 câu hỏi mà bạn biết đáp án nằm ở trang nào. Sau mỗi thay đổi,
chạy lại cả bộ và so sánh. Đó là "evaluation" đơn giản nhất.

## Chẩn đoán → kỹ thuật

| Triệu chứng | Nguyên nhân | Thử |
|-------------|-------------|-----|
| Câu hỏi ngắn / mơ hồ / sai chính tả tìm ra chunk lạc đề | Query khác xa cách viết trong tài liệu | Pre-retrieval: `rewrite`, `hyde`, `multi_query` |
| Câu hỏi gồm nhiều ý ("so sánh A và B") | Một lần tìm không phủ hết | Pre-retrieval `decompose`, retrieval `multi_hop` |
| Đáp án có trong top-20 nhưng không lọt top-5 | Thứ hạng dense chưa chuẩn | Post-retrieval: reranker `cross_encoder` |
| Top-K toàn chunk gần giống nhau | Trùng lặp | Bật "MMR diversity" hoặc redundancy filter |
| Tên riêng / mã số tìm không ra | Dense yếu với từ hiếm | `hybrid` retrieval (bài 6) |
| Chunk đúng nhưng thiếu ngữ cảnh xung quanh | Chunk quá nhỏ | `parent_document`, `sentence_window` |
| PDF có bảng, công thức bị vỡ | Loader | `marker`, `docling` (bài 2) |

## Reranking — kỹ thuật đáng học nhất

Retrieval lấy về nhiều ứng viên (ví dụ 20) thật nhanh bằng vector. Reranker là
một model chậm hơn nhưng chính xác hơn, đọc **từng cặp (câu hỏi, chunk)** và
chấm lại điểm, rồi giữ top 5. Đây thường là cải tiến có hiệu quả cao nhất sau
khi pipeline cơ bản đã chạy.

## Đọc code

- `pre_retrieval/` — biến đổi câu hỏi trước khi tìm
- `post_retrieval/` — rerank, lọc, nén, sắp xếp context
- [Tham khảo từng bước](../options-reference.md) — bảng so sánh mọi lựa chọn trong app
- [`docs/architecture.md`](../architecture.md) — cách các module nối với nhau, cho người muốn sửa code
