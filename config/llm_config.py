from dataclasses import dataclass
from typing import Literal

@dataclass
class LLMConfig:
    """Configuration for LLM backend"""
    provider: Literal["ollama", "vllm"]
    model: str
    endpoint: str
    temperature: float = 0.2
    top_p: float = 0.9
    max_tokens: int = 1024
    json_mode: bool = True
    num_ctx: int = 8192  # for Ollama

    @classmethod
    def ollama_default(cls):
        """Default Ollama configuration"""
        return cls(
            provider="ollama",
            model="qwen2.5:1.5b-instruct",
            endpoint="http://localhost:11434"
        )

    @classmethod
    def vllm_default(cls, model: str):
        """Default vLLM configuration"""
        return cls(
            provider="vllm",
            model=model,
            endpoint="http://localhost:8000/v1"
        )