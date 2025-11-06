import requests
from typing import Optional, List, Dict, Any
from config.llm_config import LLMConfig


class LLM:
    """Unified LLM interface for Ollama and vLLM"""
    
    def __init__(self, cfg: LLMConfig, domain: Optional[str] = None):
        self.cfg = cfg
        self.domain = domain
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict]] = None, 
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """Send chat request to LLM backend"""
        
        if self.cfg.provider == "ollama":
            return self._chat_ollama(messages, tools)
        elif self.cfg.provider == "vllm":
            return self._chat_vllm(messages, tools, tool_choice)
        else:
            raise ValueError(f"Unknown provider: {self.cfg.provider}")
    
    def _chat_ollama(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Ollama-specific chat implementation"""
        payload = {
            "model": self.cfg.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.cfg.temperature,
                "num_ctx": self.cfg.num_ctx
            },
            "format": "json" if self.cfg.json_mode else None
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            response = requests.post(
                f"{self.cfg.endpoint}/api/chat",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()["message"]
        except Exception as e:
            print(f"ERROR - Ollama request failed: {e}")
            return {"role": "assistant", "content": "{}"}
    
    def _chat_vllm(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """vLLM-specific chat implementation"""
        payload = {
            "model": self.cfg.model,
            "messages": messages,
            "temperature": self.cfg.temperature,
            "top_p": self.cfg.top_p,
            "max_tokens": self.cfg.max_tokens,
            "tools": tools or [],
            "tool_choice": tool_choice,
            "response_format": {
                "type": "json_object" if self.cfg.json_mode else "text"
            }
        }
        
        try:
            response = requests.post(
                f"{self.cfg.endpoint}/chat/completions",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]
        except Exception as e:
            print(f"ERROR - vLLM request failed: {e}")
            return {"role": "assistant", "content": "{}"}