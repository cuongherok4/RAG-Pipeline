# Kiến trúc và cách sửa dự án

Ứng dụng giúp thử các cấu hình RAG trên PDF và xem kết quả từng bước.

## Hai luồng dữ liệu

```text
Indexing:   PDF → Loader → Chunks → Embeddings → Vector DB
Generation: Query → Pre-retrieval → Retrieval → Post-retrieval → Prompt → LLM
```

Tài liệu giữa các bước dùng `Document` của LangChain, gồm `page_content`
và `metadata`. Metadata lưu thông tin nguồn và các thông tin bổ sung do
loader, chunker hoặc retriever tạo ra.

## Tìm code ở đâu?

| Nhu cầu | Nơi bắt đầu |
| --- | --- |
| Điều hướng ứng dụng | `app.py` |
| Trang nạp tài liệu và hỏi đáp | `ui/pages/` |
| Tham số sidebar của indexing | `ui/settings/` |
| Chạy và hiển thị kết quả hỏi đáp trên UI | `ui/results/vdb_results.py` |
| Chạy pipeline bằng Python hoặc CLI | `pipeline/` |
| Hàm chạy các bước indexing | `core/pipeline_runners.py` |
| Cấu hình và thực thi hậu xử lý dùng chung | `core/post_processing.py` |
| Kỹ thuật cụ thể | `loader/`, `chunking/`, `embedding/`, `retrieval/`, các module cùng tên bước |
| Cache từng bước và danh sách index | `pipeline_cache.py`, `core/cache_helpers.py` |

## Cấu hình

UI lấy cấu hình từ widget và `st.session_state`, **không đọc `config.yaml`**.
Sửa YAML không đổi gì trên giao diện. `config.yaml` chỉ dùng cho đường chạy bằng
code/CLI, đọc qua `utils.config.load_config()` (hỗ trợ `${VAR}` và `${VAR:-mặc_định}`):

```bash
uv run python -m pipeline.indexing_pipeline --source data/test.pdf --config config.yaml
```

UI và các lớp trong `pipeline/` vẫn có phần điều phối riêng. Khi sửa một bước,
kiểm tra cả hai đường gọi. Hậu xử lý đã được gom về `core/post_processing.py`:

- `post_processing_options()` chuẩn hóa tham số.
- `post_processing_enabled()` kiểm tra tất cả bộ xử lý được bật.
- `run_post_processing()` thực thi, không phụ thuộc Streamlit.

Cờ chuẩn là `apply_redundancy`, `apply_mmr`, `apply_compression` và
`apply_llm_filter`. Các tên cũ `semantic_dedup`, `mmr_diversity`,
`compress_context` vẫn được nhận; tên chuẩn ưu tiên nếu xuất hiện cả hai.

Cấu hình rỗng hoặc chỉ `reranker: none` giữ nguyên tài liệu, kể cả số lượng.
Các bộ lọc, nén, lọc metadata và sắp xếp context có thể chạy độc lập với
reranker. Khi hậu xử lý chạy, pipeline hiện có vẫn loại trùng chính xác và
giới hạn kết quả theo `top_n`. Khi bật reranker, semantic dedup mặc định bật;
các bước độc lập chỉ bật semantic dedup nếu được yêu cầu để tránh tải model
ngoài dự kiến. Đặt `context_ordering: original` để giữ thứ tự truy xuất.

## Cache

Khóa mỗi bước phụ thuộc khóa bước trước và cấu hình của bước đó:

```text
input_hash  = SHA256(nội dung file)
loader_key  = SHA256(input_hash + cấu hình loader)
chunk_key   = SHA256(loader_key + cấu hình chunking)
embed_key   = SHA256(chunk_key  + cấu hình embedding)
vdb_key     = SHA256(embed_key  + cấu hình vector DB)
```

Hệ quả:

- Đổi cấu hình bước nào thì chạy lại từ bước đó trở đi; các bước trước dùng lại cache.
- Đổi bất kỳ thứ gì ở trang Hỏi đáp (bước 5–9) không chạy lại indexing.
- Cùng file, cùng cấu hình thì dùng lại 100%, không tốn API call.

Khoá **không** phụ thuộc code. Mọi khoá được trộn thêm `CACHE_VERSION` trong
`pipeline_cache.py`: khi sửa code làm đổi output của một bước (ví dụ sửa bug loader),
hãy tăng số này, nếu không cache cũ (sai) vẫn được dùng lại và bug trông như chưa sửa.

Cache nằm trong `processed_data/<input_hash>/{loader,chunking,embedding,vector_db}/`;
dữ liệu vector lưu theo backend và `persist_dir` (mặc định `storage/`). Cả hai thư mục
đều có thể xoá an toàn, và có thể quản lý trong expander **🗄️ Pipeline Cache** của app.

## Kiểm tra thay đổi

Unit test (không cần model hay API key): `tests/test_minimal_rag.py` cho các nguyên
lý trong script tối giản, `tests/test_pipeline_cache.py` cho chuỗi khoá cache, và
`tests/test_post_processing.py` cho cấu hình và điều phối hậu xử lý:

```bash
uv run python -m unittest discover -s tests -v
```

Test hậu xử lý thay điểm gọi backend bằng mock; chúng không xác nhận chất
lượng reranker hoặc kết nối tới nhà cung cấp. Sau khi cài môi trường dự án,
có thể kiểm tra tích hợp indexing bằng script hiện có:

```bash
uv run python scripts/smoke_test.py --pdf data/test.pdf --mode single --offline
```

Kiểm tra cả trạng thái `SKIP` trong báo cáo: option thiếu thư viện không được
coi là đã kiểm thử thành công.
