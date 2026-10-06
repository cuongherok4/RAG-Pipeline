# Bài 4 — Embedding: text → vector

## Vấn đề

Máy tính không so sánh được "nghĩa" của hai câu. Tìm theo từ khoá thì hỏi
"xe hơi" sẽ không ra đoạn viết "ô tô".

## Ý tưởng

Model embedding biến mỗi đoạn text thành một vector (ví dụ 384 số). Model được
huấn luyện sao cho **hai đoạn cùng nghĩa có vector gần nhau**, bất kể dùng từ nào.

Độ "gần" thường đo bằng **cosine similarity**: từ -1 đến 1, càng gần 1 càng giống.
Khi vector đã được chuẩn hoá về độ dài 1, cosine chính là tích vô hướng
(`a @ b`) — đúng như hàm `embed()` và `search()` trong script tối giản.

## Quy tắc vàng

**Câu hỏi và chunk phải được embed bằng cùng một model.** Vector của hai model
khác nhau không so sánh được với nhau, giống đo bằng hai thước khác đơn vị.
Đổi model embedding = phải index lại từ đầu.

## Thử trong app

1. Chọn `fastembed`, giữ model mặc định (`paraphrase-multilingual-MiniLM-L12-v2`, cùng model
   với script tối giản), chạy indexing, mở tab **🧮 Embedding**.
2. Xem **heatmap cosine similarity**: các chunk cạnh nhau (cùng chủ đề) có sáng hơn không?
3. Tìm hai chunk có điểm cao nhất trên heatmap (ngoài đường chéo), đọc chúng —
   chúng có thực sự nói cùng chuyện?

## Chọn model

- Tiếng Việt: chọn model **multilingual** (`bge-m3`, `multilingual-e5`,
  OpenAI `text-embedding-3-*`). Model chỉ tiếng Anh (`bge-small-en`) cho kết quả tệ.
- Model to hơn thường tốt hơn nhưng chậm hơn. Bắt đầu nhỏ, chỉ đổi khi retrieval kém.

## Đọc code

- `embedding/fastembed_embedder.py` — ngắn, dễ đọc
- `embedding/base.py` — giao diện chung của mọi provider
