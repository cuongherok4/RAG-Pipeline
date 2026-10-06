"""
generation/google_generator.py
================================
Google Gemini generator — gọi qua endpoint tương thích OpenAI của Gemini, nên
chỉ cần gói ``openai`` (đã có sẵn), không cần SDK riêng của Google.

Models được khuyến nghị (đều có free tier, không cần thẻ):
  gemini-3.5-flash-lite  ← mặc định: nhanh, hạn mức free cao
  gemini-3.8-flash       Chất lượng cao nhất trong nhóm Flash

Env var: GOOGLE_API_KEY — lấy miễn phí tại https://aistudio.google.com/apikey
"""

from __future__ import annotations

from generation.openai_generator import OpenAIGenerator
from utils.llm import GEMINI_REASONING_EFFORT, GEMINI_THINKING_HEADROOM, gemini_client


class GoogleGenerator(OpenAIGenerator):
    """
    Tham số
    -------
    model_name  : Google Gemini model identifier.
    temperature : Sampling temperature.
    max_tokens  : Max output tokens.
    streaming   : Stream tokens.
    """

    def __init__(
        self,
        model_name:  str   = "gemini-3.5-flash-lite",
        temperature: float = 0.0,
        max_tokens:  int   = 2048,
        streaming:   bool  = False,
    ):
        super().__init__(model_name, temperature, max_tokens, streaming)

    def _client(self):
        return gemini_client()

    def _build_kwargs(self) -> dict:
        # Gemini 3.x không tắt được thinking → giữ ở mức "low" và chừa dư địa
        # token để câu trả lời không bị cắt.
        return {
            "model":            self.model_name,
            "messages":         [],
            "max_tokens":       self.max_tokens + GEMINI_THINKING_HEADROOM,
            "temperature":      self.temperature,
            "reasoning_effort": GEMINI_REASONING_EFFORT,
        }
