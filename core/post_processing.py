"""Cấu hình và chạy hậu xử lý dùng chung cho UI và GenerationPipeline.

Module này không import Streamlit hoặc tải model khi được import.
Các cờ ``apply_*`` là tên chuẩn; tên cũ vẫn được nhận để tương thích.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_core.documents import Document


def post_processing_options(config: dict) -> dict:
    """Đổi cấu hình của một bước thành kwargs cho PostRetrievalPipeline.

    Cấu hình rỗng hoặc chỉ có ``reranker='none'`` giữ nguyên tài liệu.
    Khi bật reranker, semantic dedup mặc định bật như trước. Với các bước
    độc lập (lọc, nén, sắp xếp), chỉ bật semantic dedup khi được yêu cầu.
    """
    reranker = config.get("reranker") or "none"
    return {
        "reranker": reranker,
        "top_n": config.get("top_n", 5),
        "apply_mmr": config.get("apply_mmr", config.get("mmr_diversity", False)),
        "mmr_lambda": config.get("mmr_lambda", 0.5),
        "apply_compression": config.get("apply_compression", config.get("compress_context", False)),
        "compression_mode": config.get("compression_mode", "extract"),
        "apply_llm_filter": config.get("apply_llm_filter", False),
        "apply_redundancy": config.get("apply_redundancy", config.get("semantic_dedup", reranker != "none")),
        "redundancy_threshold": config.get("redundancy_threshold", 0.92),
        "context_ordering": config.get("context_ordering", "sandwich"),
        "metadata_conditions": config.get("metadata_conditions"),
        "cross_encoder_model": config.get("cross_encoder_model", "BAAI/bge-reranker-v2-m3"),
        "cohere_rerank_model": config.get("cohere_rerank_model", "rerank-v3.5"),
        "llm_provider": config.get("llm_provider", "openai"),
        "llm_model": config.get("llm_model", "gpt-4.1-mini"),
        "language": config.get("language", "both"),
    }


def post_processing_enabled(config: dict) -> bool:
    """Kiểm tra mọi bộ xử lý, kể cả khi không bật reranker."""
    options = post_processing_options(config)
    return options["reranker"] != "none" or any(
        options[key]
        for key in (
            "apply_redundancy", "apply_mmr", "apply_compression",
            "apply_llm_filter", "metadata_conditions",
        )
    ) or config.get("context_ordering", "original") != "original"


def run_post_processing(
    query: str, docs: list[Document], config: dict,
) -> list[Document]:
    """Chạy các bước đã bật; để caller xử lý và hiển thị lỗi."""
    if not post_processing_enabled(config):
        return docs

    from post_retrieval import build_pipeline

    pipeline = build_pipeline(**post_processing_options(config))
    return pipeline.process(query=query, docs=docs)
