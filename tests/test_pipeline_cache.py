"""
Test cho chuỗi khoá cache của pipeline_cache.py; không ghi ra đĩa.

Nguyên lý: khoá mỗi bước = SHA256(khoá bước trước + cấu hình bước đó), nên đổi
một bước thì chỉ bước đó và các bước sau phải chạy lại.
"""

import unittest
from unittest.mock import patch

import pipeline_cache
from pipeline_cache import PipelineCache


class CacheKeyTests(unittest.TestCase):
    def setUp(self):
        self.cache = PipelineCache.__new__(PipelineCache)  # không tạo thư mục
        self.loader = self.cache.make_step_key("input", {"pdf_strategy": "pypdf"})

    def chunk_key(self, loader_key, size=800):
        return self.cache.make_step_key(loader_key, {"strategy": "recursive", "chunk_size": size})

    def test_same_config_gives_same_key(self):
        self.assertEqual(self.chunk_key(self.loader), self.chunk_key(self.loader))

    def test_changing_a_step_changes_its_key(self):
        self.assertNotEqual(self.chunk_key(self.loader, 800), self.chunk_key(self.loader, 300))

    def test_changing_an_earlier_step_changes_every_later_key(self):
        other_loader = self.cache.make_step_key("input", {"pdf_strategy": "pymupdf"})
        self.assertNotEqual(self.chunk_key(self.loader), self.chunk_key(other_loader))

    def test_dict_order_does_not_matter(self):
        a = self.cache.make_step_key("x", {"a": 1, "b": 2})
        b = self.cache.make_step_key("x", {"b": 2, "a": 1})
        self.assertEqual(a, b)

    def test_bumping_cache_version_invalidates_old_results(self):
        # Sửa code làm đổi output của một bước thì phải tăng CACHE_VERSION,
        # nếu không kết quả cũ (sai) vẫn được dùng lại.
        old = self.chunk_key(self.loader)
        with patch.object(pipeline_cache, "CACHE_VERSION", pipeline_cache.CACHE_VERSION + 1):
            self.assertNotEqual(old, self.chunk_key(self.loader))


if __name__ == "__main__":
    unittest.main()
