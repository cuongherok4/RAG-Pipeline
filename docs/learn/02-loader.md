# Bài 2 — Loader: PDF → text

## Vấn đề

PDF được thiết kế để **in**, không phải để đọc bằng máy. Bên trong nó là các
lệnh "vẽ chữ X tại toạ độ (x, y)", không có khái niệm đoạn văn, bảng hay cột.
Loader phải đoán lại cấu trúc đó. Loader dở → text lộn xộn → mọi bước sau đều hỏng
(*garbage in, garbage out*).

## Trong script tối giản

Hàm `load_pdf()` dùng `pypdf` đọc lớp text của từng trang và giữ số trang để
trích dẫn sau này.

## Thử trong app

1. Upload một PDF, chọn loader `pypdf`, xem tab **📄 Loader**.
2. Đổi sang `pymupdf` rồi `pdfplumber` với **cùng file**. So sánh preview: bảng
   biểu hiển thị khác nhau thế nào? Text hai cột có bị trộn dòng không?
3. Nếu có PDF scan (ảnh chụp), thử `pypdf` — bạn sẽ được **0 ký tự** mà không có
   lỗi nào. Đó là lý do cần loader có OCR (`marker`, `docling`, `unstructured`).

## Đọc code

- `loader/pdf_loader.py` — mọi chiến lược parse PDF
- `loader/base.py` — giao diện chung; mọi loader trả về `list[Document]`

## Bẫy thường gặp

- Không kiểm tra output của loader. **Luôn đọc thử vài trang text** trước khi làm tiếp.
- Dùng loader nặng (`marker`) cho PDF text thuần: chậm hơn hàng chục lần mà không được gì thêm.
- Không để ý số document: `pypdf` ra 10 document cho PDF 10 trang (giữ số trang để trích dẫn),
  còn `marker`/`docling` ra 1 document Markdown cho cả file (giữ cấu trúc, mất số trang).
  Chọn loader là chọn đánh đổi này.
