"""
Test cho learn/01_minimal_rag.py; không tải model, không cần API key.

Mỗi test kiểm một nguyên lý của RAG. Đọc tên test như đọc ghi chú bài học,
rồi đối chiếu với hàm tương ứng trong script.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

_SCRIPT = Path(__file__).resolve().parent.parent / "learn" / "01_minimal_rag.py"
_spec = importlib.util.spec_from_file_location("minimal_rag", _SCRIPT)
rag = importlib.util.module_from_spec(_spec)
sys.modules["minimal_rag"] = rag  # @dataclass cần module đã đăng ký
_spec.loader.exec_module(rag)


class ChunkingTests(unittest.TestCase):
    def test_no_chunk_is_longer_than_chunk_size(self):
        pages = [(1, "x" * 1000)]
        chunks = rag.split_into_chunks(pages, size=300, overlap=50)
        self.assertTrue(all(len(c.text) <= 300 for c in chunks))

    def test_overlap_repeats_the_tail_of_previous_chunk(self):
        # Một ý nằm vắt qua ranh giới vẫn còn nguyên trong chunk sau.
        text = "".join(chr(ord("a") + i % 26) for i in range(100))
        chunks = rag.split_into_chunks([(1, text)], size=40, overlap=10)
        self.assertEqual(chunks[0].text[-10:], chunks[1].text[:10])

    def test_smaller_chunks_mean_more_chunks(self):
        pages = [(1, "x" * 2000)]
        small = rag.split_into_chunks(pages, size=200, overlap=0)
        large = rag.split_into_chunks(pages, size=1000, overlap=0)
        self.assertEqual((len(small), len(large)), (10, 2))

    def test_chunks_keep_page_number_for_citation(self):
        chunks = rag.split_into_chunks([(3, "a" * 50), (7, "b" * 50)], size=100, overlap=0)
        self.assertEqual([c.page for c in chunks], [3, 7])


class RetrievalTests(unittest.TestCase):
    def test_search_ranks_by_cosine_similarity(self):
        # Vector đã chuẩn hoá về độ dài 1 nên tích vô hướng chính là cosine.
        index = np.array([[1.0, 0.0], [0.6, 0.8], [0.0, 1.0]], dtype=np.float32)
        query = np.array([0.0, 1.0], dtype=np.float32)
        hits = rag.search(query, index, k=2)
        self.assertEqual([i for i, _ in hits], [2, 1])
        self.assertAlmostEqual(hits[0][1], 1.0)
        self.assertAlmostEqual(hits[1][1], 0.8)

    def test_top_k_limits_number_of_results(self):
        index = np.eye(5, dtype=np.float32)
        self.assertEqual(len(rag.search(index[0], index, k=3)), 3)


class PromptTests(unittest.TestCase):
    def setUp(self):
        chunks = [rag.Chunk("Đoạn A", page=2), rag.Chunk("Đoạn B", page=5)]
        self.prompt = rag.build_prompt("Câu hỏi?", chunks)

    def test_each_chunk_is_numbered_with_its_page(self):
        self.assertIn("[NGUỒN 1 — trang 2]\nĐoạn A", self.prompt)
        self.assertIn("[NGUỒN 2 — trang 5]\nĐoạn B", self.prompt)

    def test_prompt_tells_llm_to_admit_when_it_does_not_know(self):
        # Thiếu câu này, LLM sẽ dùng kiến thức sẵn có để bịa khi context thiếu.
        self.assertIn("không biết", self.prompt)

    def test_question_comes_after_context(self):
        self.assertLess(self.prompt.index("Đoạn B"), self.prompt.index("Câu hỏi: Câu hỏi?"))


if __name__ == "__main__":
    unittest.main()
