# Bài 7 — Prompt & Generation

## Prompt RAG gồm ba phần

1. **Chỉ dẫn**: "Chỉ trả lời dựa trên các nguồn dưới đây. Nếu không có thông tin, nói không biết."
2. **Context**: các chunk tìm được, mỗi chunk đánh số nguồn.
3. **Câu hỏi**.

Xem prompt thật ở bước **⑧ PROMPT** khi chạy `learn/01_minimal_rag.py`.

## Vì sao chỉ dẫn quan trọng

Không có câu "nói không biết nếu không có thông tin", LLM sẽ dùng kiến thức sẵn
có để **bịa** khi context thiếu — đúng điều RAG muốn tránh.

Yêu cầu **trích dẫn** (`[NGUỒN 2]`) giúp người dùng kiểm tra lại, và giúp bạn
thấy LLM dựa vào chunk nào.

## Tham số generation

- **temperature**: 0 cho RAG — muốn câu trả lời bám sát nguồn, không cần sáng tạo.
- **model**: model lớn hơn đọc context tốt hơn, nhưng lỗi retrieval thì model lớn cũng không cứu.

## Thử trong app

1. So sánh template `basic` và `citation` với cùng câu hỏi.
2. Hỏi một câu **tài liệu không hề nhắc tới**. Model có thừa nhận không biết không?
3. Tăng temperature lên 1.0, hỏi lại vài lần — câu trả lời có ổn định không?

## Đọc code

- `prompt/basic.py`, `prompt/citation.py`
- `generation/ollama_generator.py` — chạy local
- Trong script tối giản: `build_prompt()` và `generate()`.
