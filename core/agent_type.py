from enum import Enum

class AgentType(Enum):
    """Types of specialized agents"""
    RESEARCH_COORDINATOR = "research_coordinator"
    SEARCH_SPECIALIST = "search_specialist"
    ANALYST = "analyst"
    VALIDATOR = "validator"
    SYNTHESIZER = "synthesizer"
    CRITIC = "critic"
    WRITER = "writer"