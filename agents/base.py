from abc import ABC, abstractmethod
from typing import Dict, Any
from core.llm import LLM


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, llm: LLM):
        self.llm = llm
    
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process state and return updates"""
        pass
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return system prompt for this agent"""
        pass