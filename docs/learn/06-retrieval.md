# Bài 6 — Retrieval: tìm đúng chunk

Đây là bước **quyết định chất lượng RAG nhiều nhất**. Nếu chunk chứa đáp án
không được lấy về, không LLM nào cứu được.

## Ba kiểu tìm cơ bản

| Kiểu | Cách hoạt động | Giỏi | Dở |
|------|----------------|------|-----|
| `dense` | So vector embedding (bài 4) | Hiểu đồng nghĩa, diễn đạt khác | Tên riêng, mã số, từ hiếm |
| `sparse` (BM25) | Đếm từ khoá trùng, từ hiếm được điểm cao | Tên riêng, mã sản phẩm, số liệu | Không hiểu đồng nghĩa |
| `hybrid` | Trộn điểm của cả hai | Cân bằng — thường là lựa chọn tốt nhất thực tế | Thêm một tham số cần chỉnh |

## Top-K

Số chunk lấy về. K nhỏ → dễ sót đáp án. K lớn → nhiều nhiễu, prompt dài.
Bắt đầu với 4–5.

## Ví dụ thật từ script tối giản

Chạy `learn/01_minimal_rag.py` với `data/test.pdf` (một bài báo **tiếng Anh** về
Faster R-CNN), so sánh điểm cosine của chunk top-1:

| Câu hỏi | cosine top-1 | Chunk top-1 có đáp án? |
|---------|-------------|------------------------|
| "Tài liệu này nói về gì?" | 0.40 | Không — câu hỏi quá chung, mọi chunk đều "hơi giống" |
| "Mô hình được đánh giá trên tập dữ liệu nào?" | 0.62 | Có — trang 6: *"I evaluate my model on the PASCAL VOC 2012 dataset"* |

Bài học:

- **Câu hỏi cụ thể tìm tốt hơn câu hỏi chung chung.** Câu "tài liệu nói về gì" là
  câu hỏi *tóm tắt*, không phải câu hỏi *tra cứu* — retrieval top-K vốn không hợp với nó.
- Model multilingual nối được câu hỏi tiếng Việt với tài liệu tiếng Anh, nhưng
  điểm tuyệt đối không cao. **Đừng đặt ngưỡng cosine cố định** — hãy nhìn thứ hạng.

## Thử trong app

1. Retrieval `dense`, Top-K 4. Hỏi một câu **diễn đạt khác** với chữ trong tài liệu.
   Xem các chunk được lấy về và điểm của chúng.
2. Hỏi một câu chứa **tên riêng / con số chính xác** có trong tài liệu. So sánh
   `dense` với `hybrid` (cần bật sparse embedding lúc indexing).
3. Tập thói quen: **luôn đọc các chunk được retrieve trước khi đọc câu trả lời.**

## Đọc code

- `retrieval/dense.py`, `retrieval/sparse.py`, `retrieval/hybrid.py`
- Trong script tối giản: hàm `search()` chính là dense retrieval.
