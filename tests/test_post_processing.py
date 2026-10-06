"""Regression tests cho cấu hình hậu xử lý; không gọi API hoặc tải model."""

import sys
import unittest
from types import ModuleType
from unittest.mock import Mock, patch

from core.post_processing import (
    post_processing_enabled,
    post_processing_options,
    run_post_processing,
)


class PostProcessingTests(unittest.TestCase):
    def test_disabled_returns_original_documents_without_loading_pipeline(self):
        docs = [object() for _ in range(10)]
        with patch.dict(sys.modules, {"post_retrieval": None}):
            for config in ({}, {"reranker": "none", "top_n": 5},
                           {"reranker": "none", "context_ordering": "original"}):
                with self.subTest(config=config):
                    self.assertFalse(post_processing_enabled(config))
                    self.assertIs(run_post_processing("query", docs, config), docs)

    def test_each_processor_can_run_without_a_reranker(self):
        for key, value in (
            ("apply_redundancy", True), ("apply_mmr", True),
            ("apply_compression", True), ("apply_llm_filter", True),
            ("metadata_conditions", [{"field": "language", "operator": "eq", "value": "vi"}]),
            ("context_ordering", "reverse"),
        ):
            with self.subTest(processor=key):
                config = {"reranker": "none", key: value}
                self.assertTrue(post_processing_enabled(config))
                module = ModuleType("post_retrieval")
                module.build_pipeline = Mock()
                pipeline = module.build_pipeline.return_value
                docs, expected = [object()], [object()]
                pipeline.process.return_value = expected
                with patch.dict(sys.modules, {"post_retrieval": module}):
                    self.assertIs(run_post_processing("question", docs, config), expected)
                pipeline.process.assert_called_once_with(query="question", docs=docs)
                self.assertEqual(module.build_pipeline.call_args.kwargs[key], value)

    def test_legacy_flags_are_supported(self):
        for old, new in (("semantic_dedup", "apply_redundancy"),
                         ("mmr_diversity", "apply_mmr"),
                         ("compress_context", "apply_compression")):
            with self.subTest(flag=old):
                config = {old: True}
                self.assertTrue(post_processing_enabled(config))
                self.assertTrue(post_processing_options(config)[new])
                config[new] = False
                self.assertFalse(post_processing_enabled(config))
                self.assertFalse(post_processing_options(config)[new])

    def test_reranker_keeps_its_dedup_default_but_independent_steps_do_not(self):
        self.assertTrue(post_processing_options({"reranker": "cohere"})["apply_redundancy"])
        self.assertFalse(post_processing_options({"apply_compression": True})["apply_redundancy"])
        self.assertFalse(post_processing_options({
            "reranker": "cohere", "apply_redundancy": False,
        })["apply_redundancy"])

    def test_custom_parameters_are_preserved_without_mutating_input(self):
        config = {
            "reranker": "llm", "top_n": 3, "apply_mmr": True,
            "mmr_lambda": 0.2, "apply_compression": True,
            "compression_mode": "summarise", "apply_llm_filter": True,
            "apply_redundancy": False, "redundancy_threshold": 0.8,
            "context_ordering": "original", "metadata_conditions": None,
            "cross_encoder_model": "custom-cross-encoder",
            "cohere_rerank_model": "custom-cohere", "llm_provider": "ollama",
            "llm_model": "local-model", "language": "vi",
        }
        original = dict(config)
        self.assertEqual(post_processing_options(config), original)
        self.assertEqual(config, original)

    def test_processor_errors_reach_the_caller(self):
        module = ModuleType("post_retrieval")
        module.build_pipeline = Mock()
        module.build_pipeline.return_value.process.side_effect = RuntimeError("provider unavailable")
        with patch.dict(sys.modules, {"post_retrieval": module}):
            with self.assertRaisesRegex(RuntimeError, "provider unavailable"):
                run_post_processing("query", [], {"apply_llm_filter": True})


if __name__ == "__main__":
    unittest.main()
