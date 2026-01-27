from dataclasses import dataclass, field
from typing import List, Any
from core.agent_type import AgentType

@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    agent_type: AgentType
    llm_model: str = "liquid/lfm-2.5-1.2b-instruct:free"
    temperature: float = 0.3
    max_tokens: int = 2000
    tools: List[Any] = field(default_factory=list)
    system_prompt: str = ""
    is_async: bool = False