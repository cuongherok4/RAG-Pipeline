"""Trang Bắt đầu — bản đồ 9 bước của RAG cho người mới học."""

import streamlit as st

# (số, tên, thuật ngữ, bước này làm gì, bạn sẽ thấy gì, tuỳ chọn?)
_INDEXING_STEPS = [
    (1, "Đọc tài liệu", "Loader",
     "Mở file PDF và lấy chữ ra khỏi nó.",
     "Số trang, số ký tự, xem trước nội dung từng trang.", False),
    (2, "Cắt nhỏ", "Chunking",
     "Chia văn bản dài thành các đoạn ngắn, mỗi đoạn một ý.",
     "Biểu đồ độ dài các đoạn và nội dung từng đoạn.", False),
    (3, "Biến chữ thành số", "Embedding",
     "Mỗi đoạn thành một vector; đoạn cùng nghĩa có vector gần nhau.",
     "Kích thước ma trận vector và heatmap độ giống nhau.", False),
    (4, "Lưu để tra cứu", "Vector DB",
     "Cất các vector vào kho để tìm lại thật nhanh.",
     "Index đã lưu, sẵn sàng cho phần hỏi đáp.", False),
]

_GENERATION_STEPS = [
    (5, "Làm rõ câu hỏi", "Pre-retrieval",
     "Viết lại hoặc tách câu hỏi để dễ tìm hơn.",
     "Câu hỏi gốc và các câu hỏi đã biến đổi.", True),
    (6, "Tìm đoạn liên quan", "Retrieval",
     "Lấy K đoạn có vector gần câu hỏi nhất.",
     "Các đoạn tìm được kèm điểm số.", False),
    (7, "Lọc & xếp hạng lại", "Post-retrieval",
     "Chấm lại độ liên quan, bỏ đoạn trùng hoặc lạc đề.",
     "Thứ hạng trước và sau khi lọc.", True),
    (8, "Soạn prompt", "Prompt",
     "Ghép câu hỏi với các đoạn tìm được thành lời nhắn cho LLM.",
     "Toàn văn prompt gửi cho LLM.", False),
    (9, "Trả lời", "Generation",
     "LLM đọc prompt và viết câu trả lời có trích nguồn.",
     "Câu trả lời, nguồn trích dẫn, số token.", False),
]

_LIGHT = {"s1": "#0f766e", "s1_bg": "rgba(15,118,110,.07)",
          "s2": "#c2410c", "s2_bg": "rgba(194,65,12,.06)",
          "card": "#ffffff", "border": "#d9e3df", "muted": "#5b6b67"}
_DARK = {"s1": "#2dd4bf", "s1_bg": "rgba(45,212,191,.08)",
         "s2": "#fb923c", "s2_bg": "rgba(251,146,60,.08)",
         "card": "#172321", "border": "#2a3a37", "muted": "#9fb2ad"}


def _palette() -> dict:
    theme = getattr(st.context, "theme", None)
    return _DARK if getattr(theme, "type", "light") == "dark" else _LIGHT


def _css(p: dict) -> str:
    return f"""
<style>
.rp-hero {{ padding: 1.6rem 0 1.2rem; }}
.rp-badge {{ display:inline-block; padding:.25rem .75rem; border-radius:999px;
  background:{p['s1_bg']}; color:{p['s1']}; font-weight:600; font-size:.9rem; }}
.rp-title {{ font-size:2.6rem; font-weight:700; margin:.6rem 0 .3rem; line-height:1.15; }}
.rp-lead {{ font-size:1.15rem; color:{p['muted']}; max-width:720px; line-height:1.6; margin:0; }}
.rp-flow {{ display:flex; flex-wrap:wrap; align-items:center; gap:.4rem; margin-top:1.1rem; }}
.rp-flow span {{ padding:.3rem .7rem; border-radius:8px; border:1px solid {p['border']};
  background:{p['card']}; font-weight:500; }}
.rp-flow b {{ color:{p['muted']}; font-weight:400; }}
.rp-stage {{ margin:1.8rem 0 .8rem; display:flex; align-items:baseline; gap:.7rem; flex-wrap:wrap; }}
.rp-stage h3 {{ margin:0; font-size:1.35rem; }}
.rp-stage small {{ color:{p['muted']}; font-size:.95rem; }}
.rp-wrap {{ container-type:inline-size; }}
.rp-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:.8rem; }}
@container (min-width: 860px) {{
  .rp-grid.n4 {{ grid-template-columns:repeat(4,minmax(0,1fr)); }}
  .rp-grid.n5 {{ grid-template-columns:repeat(5,minmax(0,1fr)); }}
}}
.rp-card {{ background:{p['card']}; border:1px solid {p['border']}; border-radius:12px;
  padding:.9rem 1rem; display:flex; flex-direction:column; gap:.45rem; }}
.rp-top {{ display:flex; align-items:center; justify-content:space-between; }}
.rp-num {{ flex:none; width:30px; height:30px; border-radius:50%; display:inline-flex;
  align-items:center; justify-content:center; font-weight:700; color:#fff; }}
.rp-name {{ font-weight:700; font-size:1.05rem; line-height:1.25; }}
.rp-term {{ font-size:.82rem; color:{p['muted']}; font-family:'JetBrains Mono',monospace; }}
.rp-what {{ margin:0; line-height:1.5; }}
.rp-see {{ margin:0; font-size:.9rem; color:{p['muted']}; line-height:1.45; }}
.rp-opt {{ font-size:.72rem; padding:.05rem .5rem; border-radius:999px;
  border:1px dashed {p['muted']}; color:{p['muted']}; white-space:nowrap;
  font-family:inherit; }}
.rp-start {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:.9rem; }}
.rp-start div {{ border-radius:12px; padding:1rem 1.1rem; line-height:1.55; }}
.rp-start b.rp-k {{ display:block; font-size:.8rem; letter-spacing:.08em; text-transform:uppercase;
  margin-bottom:.35rem; }}
</style>"""


def _card(step: tuple, color: str) -> str:
    num, name, term, what, see, optional = step
    opt = '<span class="rp-opt">tuỳ chọn</span>' if optional else ""
    return (
        f'<div class="rp-card">'
        f'<div class="rp-top"><span class="rp-num" style="background:{color}">{num}</span>{opt}</div>'
        f'<div><div class="rp-name">{name}</div><div class="rp-term">{term}</div></div>'
        f'<p class="rp-what">{what}</p>'
        f'<p class="rp-see">👀 {see}</p>'
        f'</div>'
    )


def _stage(title: str, note: str, steps: list, color: str) -> str:
    cards = "".join(_card(s, color) for s in steps)
    return (f'<div class="rp-stage"><h3 style="color:{color}">{title}</h3><small>{note}</small></div>'
            f'<div class="rp-wrap"><div class="rp-grid n{len(steps)}">{cards}</div></div>')


def _page_welcome():
    """Trang Bắt đầu — giới thiệu RAG qua 9 bước đánh số liên tục."""
    p = _palette()

    st.html(_css(p) + """
<div class="rp-hero">
  <span class="rp-badge">🎓 Học RAG từng bước</span>
  <div class="rp-title">RAG-Pipeline</div>
  <p class="rp-lead">
    Giúp LLM trả lời câu hỏi về <b>tài liệu của bạn</b>: tìm vài đoạn liên quan nhất
    rồi đưa kèm vào prompt. Mỗi bước bên dưới đều hiện kết quả trung gian để bạn
    thấy tận mắt dữ liệu biến đổi ra sao.
  </p>
  <div class="rp-flow">
    <span>📄 Tài liệu</span><b>→</b><span>✂️ Chia nhỏ</span><b>→</b><span>🔢 Vector</span>
    <b>→</b><span>🔎 Tìm kiếm</span><b>→</b><span>💬 Trả lời</span>
  </div>
</div>
""" + _stage("Giai đoạn 1 · Chuẩn bị tài liệu", "làm một lần cho mỗi bộ tài liệu",
             _INDEXING_STEPS, p["s1"])
        + _stage("Giai đoạn 2 · Hỏi đáp", "chạy lại cho mỗi câu hỏi",
                 _GENERATION_STEPS, p["s2"])
        + f"""
<div class="rp-stage"><h3>Bắt đầu thế nào?</h3></div>
<div class="rp-start">
  <div style="background:{p['s1_bg']}"><b class="rp-k" style="color:{p['s1']}">Bước A</b>
    Mở <b>🗃️ 1–4 · Chuẩn bị tài liệu</b> ở thanh bên trái → tải PDF lên →
    chọn cấu hình → bấm <b>▶️ Process</b>.</div>
  <div style="background:{p['s2_bg']}"><b class="rp-k" style="color:{p['s2']}">Bước B</b>
    Mở <b>💬 5–9 · Hỏi đáp</b> → chọn LLM → nhập câu hỏi →
    đọc các đoạn tìm được <i>trước</i> khi đọc câu trả lời.</div>
  <div style="border:1px solid {p['border']}"><b class="rp-k" style="color:{p['muted']}">Muốn hiểu sâu</b>
    Chạy <code>learn/01_minimal_rag.py</code> — cả pipeline trong một file —
    rồi theo lộ trình trong <code>docs/learn/</code>.</div>
</div>
""")

    with st.expander("⚙️ Cấu hình cơ bản cho lần chạy đầu tiên", expanded=False):
        st.markdown("""
Chọn đúng các giá trị dưới đây, mọi thứ khác để mặc định hoặc tắt. Chạy được trên CPU,
chỉ bước 9 cần LLM (Ollama local hoặc một API key).

| Bước | Chọn | Vì sao |
|------|------|--------|
| 1 · Loader | `pypdf` | Nhanh, không cần cài thêm |
| 2 · Chunking | `recursive`, size `800`, overlap `100` | Dễ hiểu nhất |
| 3 · Embedding | `fastembed` | Chạy CPU, miễn phí, không cần key |
| 4 · Vector DB | `faiss` | Local, không cần server |
| 5 · Pre-retrieval | tắt | Thêm sau khi đã thấy lỗi cần sửa |
| 6 · Retrieval | `dense`, Top-K `4` | Giống script tối giản |
| 7 · Post-retrieval | tắt | Thêm sau khi đã thấy lỗi cần sửa |
| 8 · Prompt | `citation` | Thấy câu trả lời lấy từ đoạn nào |
| 9 · Generation | `ollama` hoặc provider bạn có key, temperature `0` | Bám sát nguồn |
""")

    st.caption(
        "RAG-Pipeline · Streamlit + LangChain · "
        "Phát triển bởi [cuongherok4](https://github.com/cuongherok4) · "
        "[GitHub](https://github.com/cuongherok4/RAG-Pipeline)"
    )
