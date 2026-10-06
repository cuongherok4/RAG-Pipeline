# Bài 0 — RAG là gì?

## Vấn đề

LLM (ChatGPT, Claude, Qwen...) chỉ biết những gì có trong dữ liệu huấn luyện.
Hỏi nó về **tài liệu nội bộ của bạn** — hợp đồng, giáo trình, báo cáo — nó không
biết, và tệ hơn, nó thường **bịa** ra một câu trả lời nghe rất hợp lý.

Cách ngây thơ: dán cả tài liệu vào prompt. Không được vì tài liệu có thể dài
hàng nghìn trang, tốn tiền, chậm, và LLM đọc prompt quá dài thì hay bỏ sót.

## Ý tưởng của RAG

**R**etrieval-**A**ugmented **G**eneration = *tìm trước, trả lời sau*.

> Chỉ đưa cho LLM **vài đoạn liên quan nhất** tới câu hỏi, rồi yêu cầu nó
> trả lời dựa trên các đoạn đó.

Giống đi thi được mở sách: không cần thuộc cả cuốn, chỉ cần lật đúng trang.

## Hai giai đoạn

```text
INDEXING — làm một lần, khi có tài liệu mới
  PDF → [Loader] → text → [Chunking] → các đoạn nhỏ → [Embedding] → vector → [Vector DB]

GENERATION — làm mỗi khi có câu hỏi
  Câu hỏi → [Embedding] → vector → [Retrieval: tìm đoạn gần nhất trong Vector DB]
          → [Prompt: câu hỏi + các đoạn tìm được] → [LLM] → câu trả lời
```

Mấu chốt nằm ở **embedding**: một model biến text thành vector số sao cho hai
đoạn cùng nghĩa có vector gần nhau. Nhờ vậy "tìm đoạn liên quan" trở thành
"tìm vector gần nhất" — việc máy tính làm rất nhanh.

## Khi RAG trả lời sai, lỗi ở đâu?

Hầu như luôn thuộc một trong hai nhóm — nhớ điều này suốt lộ trình:

1. **Tìm sai** (retrieval): đoạn chứa đáp án không nằm trong top-K. LLM giỏi đến
   mấy cũng không trả lời được thứ nó không được đọc.
   → Kiểm tra: xem các chunk được lấy về có chứa đáp án không.
2. **Đọc sai** (generation): đoạn đúng đã có trong prompt nhưng LLM hiểu sai
   hoặc bịa thêm. → Sửa prompt, đổi model, giảm temperature.

App này hiển thị kết quả **từng bước** chính là để bạn chẩn đoán được lỗi nằm ở đâu.

## Tiếp theo

Mở [`learn/01_minimal_rag.py`](../../learn/01_minimal_rag.py), đọc từ trên xuống
(mỗi hàm là một bước ở sơ đồ trên), rồi chạy nó.
